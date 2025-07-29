#!/usr/bin/env python3
"""
Banner Maker Web App
Flask application for creating AI-powered marketing banners
"""

import os
import uuid
import asyncio
import logging
import time
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename
import threading
from typing import Dict, Optional
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import banner maker modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.lp_scrape import scrape_landing_page, get_page_title_and_description
from src.llm_scraper import scrape_page_with_llm
from src.gpt_image import generate_unified_creative
from src.copy_gen import generate_copy_and_visual_prompts, select_best_copy_for_banner
from src.canva_oauth import init_canva_oauth, get_authenticated_api, require_canva_auth
from src.explanation_gen import generate_creative_explanation
import requests
from urllib.parse import urljoin, urlparse
import re
from PIL import Image
import io
import base64
import glob
import atexit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'banner-maker-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create temp folder for cropping images
app.config['TEMP_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Store generation results temporarily
generation_results = {}

# Cache for scraping results (persists until page refresh)
scraping_cache = {}

# Get Google API key for LLM scraping
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_temp_files():
    """Clean up old temporary files"""
    try:
        temp_pattern = os.path.join(app.config['TEMP_FOLDER'], 'temp_*.jpg')
        temp_files = glob.glob(temp_pattern)
        
        current_time = time.time()
        cleaned_count = 0
        
        for temp_file in temp_files:
            try:
                # Remove files older than 1 hour
                if current_time - os.path.getmtime(temp_file) > 3600:
                    os.remove(temp_file)
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old temporary files")
            
    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}")


# Register cleanup function to run on app shutdown
atexit.register(cleanup_temp_files)

# Run initial cleanup
cleanup_temp_files()

# Initialize Canva OAuth
init_canva_oauth(app)


def get_cached_scraping_data(url):
    """Get cached scraping data for a URL with validation"""
    try:
        cached_data = scraping_cache.get(url)
        
        if not cached_data:
            print(f"🔍 CACHE CHECK for {url}: No cached data found")
            return None
        
        # Validate cached data structure
        if 'lp_data' in cached_data and 'page_meta' in cached_data:
            # Check if the cached data is complete
            lp_data = cached_data['lp_data']
            page_meta = cached_data['page_meta']
            
            # Validate lp_data structure
            if not isinstance(lp_data, dict) or 'text_content' not in lp_data:
                print(f"⚠️ CACHE INVALID for {url}: lp_data is incomplete, will re-scrape")
                logger.warning(f"Cached lp_data for {url} is incomplete, will re-scrape")
                return None
                
            # Validate page_meta structure
            if not isinstance(page_meta, dict) or 'title' not in page_meta or 'description' not in page_meta:
                print(f"⚠️ CACHE INVALID for {url}: page_meta is incomplete, will re-scrape")
                logger.warning(f"Cached page_meta for {url} is incomplete, will re-scrape")
                return None
            
            print(f"✅ CACHE HIT for {url}: Valid data found")
            logger.info(f"Retrieved valid cached data for: {url}")
            return cached_data
        else:
            print(f"⚠️ CACHE INCOMPLETE for {url}: Missing lp_data or page_meta keys")
            logger.warning(f"Cached data for {url} is missing lp_data or page_meta")
            return None
            
    except Exception as e:
        print(f"❌ CACHE EXCEPTION for {url}: {e}")
        logger.error(f"Error retrieving cached data for {url}: {e}")
        return None


def cache_scraping_data(url, lp_data, page_meta):
    """Cache scraping data for a URL with validation"""
    try:
        # Validate input data
        if not url:
            print("❌ CACHE ERROR: URL is empty")
            logger.error("Cannot cache data: URL is empty")
            return
        
        if not lp_data or not page_meta:
            print(f"❌ CACHE ERROR for {url}: Missing lp_data or page_meta")
            logger.error(f"Cannot cache data for {url}: Missing lp_data or page_meta")
            return
        
        # Ensure we have the required fields in lp_data
        if not isinstance(lp_data, dict) or 'text_content' not in lp_data:
            print(f"❌ CACHE ERROR for {url}: Invalid lp_data structure")
            logger.error(f"Cannot cache data for {url}: Invalid lp_data structure")
            return
            
        # Ensure we have the required fields in page_meta
        if not isinstance(page_meta, dict) or 'title' not in page_meta or 'description' not in page_meta:
            print(f"❌ CACHE ERROR for {url}: Invalid page_meta structure")
            logger.error(f"Cannot cache data for {url}: Invalid page_meta structure")
            return
        
        # Initialize cache entry if it doesn't exist
        if url not in scraping_cache:
            scraping_cache[url] = {}
        
        # Cache the complete scraping data
        scraping_cache[url].update({
            'lp_data': lp_data,
            'page_meta': page_meta,
            'timestamp': time.time()
        })
        
        print(f"💾 CACHE SAVED for {url}: Complete scraping data stored")
        logger.info(f"Successfully cached complete scraping data for: {url}")
        
        # Keep cache size manageable (max 50 URLs)
        if len(scraping_cache) > 50:
            # Remove oldest entry
            oldest_url = min(scraping_cache.keys(), key=lambda k: scraping_cache[k].get('timestamp', 0))
            del scraping_cache[oldest_url]
            print(f"🗑️ CACHE CLEANUP: Removed oldest entry: {oldest_url}")
            logger.info(f"Removed oldest cache entry: {oldest_url}")
            
    except Exception as e:
        print(f"❌ CACHE EXCEPTION for {url}: {e}")
        logger.error(f"Error caching scraping data for {url}: {e}")
        # Don't raise exception, just log the error


def cache_copy_data(url, copy_variants, best_copy):
    """Cache copy generation data for a URL"""
    if url not in scraping_cache:
        scraping_cache[url] = {}
    
    scraping_cache[url].update({
        'copy_variants': copy_variants,
        'best_copy': best_copy,
        'copy_timestamp': time.time()
    })


def get_cached_copy_data(url):
    """Get cached copy data for a URL"""
    cached_data = scraping_cache.get(url)
    if cached_data and 'copy_variants' in cached_data:
        return {
            'copy_variants': cached_data['copy_variants'],
            'best_copy': cached_data['best_copy']
        }
    return None


async def scrape_with_llm_fallback(url: str, use_llm: bool = True) -> tuple:
    """
    Enhanced scraping function that uses LLM by default with fallback to traditional scraping
    
    Args:
        url: URL to scrape
        use_llm: Whether to attempt LLM scraping first
        
    Returns:
        tuple: (lp_data, page_meta, used_llm_flag)
    """
    logger.info(f"Starting scraping for {url} with LLM={'enabled' if use_llm else 'disabled'}")
    
    if use_llm and GOOGLE_API_KEY:
        try:
            # Attempt LLM-enhanced scraping
            logger.info(f"Attempting LLM-enhanced scraping for {url}")
            llm_result = await scrape_page_with_llm(url, GOOGLE_API_KEY)
            
            # Check if LLM extraction was successful
            if (llm_result.get('llm_extraction', {}).get('extraction_confidence', 0) > 0.5 and
                llm_result.get('text_content')):
                
                # LLM scraping successful - format for compatibility
                lp_data = {
                    'text_content': llm_result['text_content'],
                    'images': llm_result.get('images', []),
                    'has_viable_image': llm_result.get('has_viable_image', False),
                    'hero_image_data': llm_result.get('hero_image_data'),
                    'llm_extraction': llm_result.get('llm_extraction'),
                    'extraction_method': 'llm'
                }
                
                page_meta = llm_result.get('metadata', {})
                # Ensure required fields exist
                if 'title' not in page_meta:
                    page_meta['title'] = llm_result.get('llm_extraction', {}).get('llm_extracted_data', {}).get('product_name', 'Page')
                if 'description' not in page_meta:
                    page_meta['description'] = llm_result.get('llm_extraction', {}).get('llm_extracted_data', {}).get('product_description', '')
                
                logger.info(f"LLM scraping successful for {url} with confidence {llm_result.get('llm_extraction', {}).get('extraction_confidence', 0):.2f}")
                return lp_data, page_meta, True
                
            else:
                logger.warning(f"LLM scraping returned low confidence results for {url}, falling back to traditional scraping")
                
        except Exception as e:
            logger.error(f"LLM scraping failed for {url}: {e}")
            logger.info("Falling back to traditional scraping...")
    
    # Fallback to traditional scraping
    try:
        logger.info(f"Using traditional scraping for {url}")
        lp_data = await scrape_landing_page(url)
        page_meta = await get_page_title_and_description(url)
        
        # Add extraction method marker
        if isinstance(lp_data, dict):
            lp_data['extraction_method'] = 'traditional'
        
        logger.info(f"Traditional scraping successful for {url}")
        return lp_data, page_meta, False
        
    except Exception as e:
        logger.error(f"Traditional scraping also failed for {url}: {e}")
        raise e


@app.route('/')
def index():
    """Main banner creation interface"""
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/debug/routes')
def debug_routes():
    """Debug route to show all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'route': rule.rule,
            'methods': list(rule.methods),
            'endpoint': rule.endpoint
        })
    return jsonify({'routes': routes})


@app.route('/api/generate', methods=['POST'])
@require_canva_auth
def generate_banner():
    """Generate banner using Canva pipeline"""
    import time
    start_time = time.time()
    logger.info("🚀 Starting Canva banner generation")
    
    try:
        from src.layout_orchestrator import build_banner, AdSize, Product, CopyTriple
        
        data = request.get_json()
        product_id = data.get('product_id')  # For database lookup
        url = data.get('url')  # Fallback for direct URL processing
        size_key = data.get('size', 'MD_RECT')
        variant_idx = data.get('variant_idx', 0)
        product_image_paths = data.get('product_image_paths', [])
        
        # Backward compatibility for single image
        if not product_image_paths and data.get('product_image_path'):
            product_image_paths = [data.get('product_image_path')]
        
        # Validate ad size
        if size_key not in AdSize.__members__:
            return jsonify({'error': f'Invalid size: {size_key}'}), 400
        
        ad_size = AdSize[size_key]
        
        # For now, use direct parameters instead of database
        # TODO: Implement proper database integration
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get cached data (existing functionality)
        cached_data = get_cached_scraping_data(url)
        if not cached_data or 'selected_copy' not in cached_data:
            return jsonify({'error': 'No copy has been selected. Please generate and select copy first.'}), 400
        
        selected_copy = cached_data['selected_copy']
        
        # Create copy triple from selected copy
        copy = CopyTriple(
            headline=selected_copy.get('text', '').split('\n')[0][:50],  # First line as headline
            subline=selected_copy.get('text', '').split('\n')[1] if '\n' in selected_copy.get('text', '') else 'Quality you can trust',
            cta='Learn More'
        )
        
        # Create design title from selected copy
        design_title = f"Marketing Banner - {selected_copy.get('type', 'banner').title()}"
        
        # Get authenticated Canva API instance
        auth_time = time.time()
        api = get_authenticated_api()
        if not api:
            return jsonify({'error': 'Canva authentication required'}), 401
        logger.info(f"⚡ Auth check: {(time.time() - auth_time)*1000:.1f}ms")
        
        # Upload product images to Canva if provided
        hero_asset_ids = []
        if product_image_paths:
            upload_start = time.time()
            logger.info(f"📤 Starting upload of {len(product_image_paths)} product image(s)")
            
            for i, product_image_path in enumerate(product_image_paths):
                if os.path.exists(product_image_path):
                    try:
                        with open(product_image_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Determine MIME type
                        import mimetypes
                        mime_type, _ = mimetypes.guess_type(product_image_path)
                        if not mime_type or not mime_type.startswith('image/'):
                            mime_type = 'image/jpeg'
                        
                        logger.info(f"📤 Uploading product image {i+1}/{len(product_image_paths)} ({len(image_data)} bytes)")
                        asset_id = api.upload_binary(
                            image_data,
                            os.path.basename(product_image_path),
                            mime_type
                        )
                        hero_asset_ids.append(asset_id)
                        logger.info(f"✅ Product image {i+1} uploaded: {asset_id}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to upload product image {i+1}: {str(e)}")
                        # Continue with other images
                        continue
                else:
                    logger.warning(f"⚠️ Product image {i+1} not found: {product_image_path}")
            
            upload_time = (time.time() - upload_start) * 1000
            logger.info(f"✅ Uploaded {len(hero_asset_ids)}/{len(product_image_paths)} product images ({upload_time:.1f}ms)")
        
        # Use first uploaded image as primary hero asset for compatibility
        hero_asset_id = hero_asset_ids[0] if hero_asset_ids else None
        
        # Note: We no longer require the product image - can create text-only banners
        
        # Create product object
        product = Product(
            hero_asset_id=hero_asset_id,
            palette=['#FF6B35', '#004225']  # Default palette
        )
        
        # Use pre-generated background if provided
        bg_asset_id = data.get('background_asset_id')
        if not bg_asset_id:
            logger.warning("No background asset ID provided, proceeding without background")
        else:
            logger.info(f"🎨 Using pre-generated background: {bg_asset_id}")
        
        # Use simplified upload instead of complex banner building
        # This avoids the failing element addition and export timeout issues
        from src.simple_canva_upload import simple_canva_upload
        
        build_start = time.time()
        logger.info(f"🏗️  Using simplified Canva upload (bg_asset: {bg_asset_id}, hero_asset: {hero_asset_id})")
        
        simple_result = simple_canva_upload(
            product_image_paths=product_image_paths,
            hero_asset_ids=hero_asset_ids,
            background_asset_id=bg_asset_id,
            api=api,
            design_title=design_title or f"Marketing Banner {ad_size.value}"
        )
        
        build_time = (time.time() - build_start) * 1000
        logger.info(f"✅ Simplified upload completed ({build_time:.1f}ms): design_id={simple_result.design_id}")
        
        # Convert to compatible result format
        from src.layout_orchestrator import BannerResult
        result = BannerResult(
            design_id=simple_result.design_id,
            export_url=simple_result.design_url,  # Use edit URL instead of export
            html_snippet=f'<p>Assets uploaded to Canva. <a href="{simple_result.design_url}" target="_blank">Open in Canva</a> to arrange them.</p>'
        )
        
        # Import template map for dimensions
        from src.templates import TEMPLATE_MAP
        
        # Store result for download (reuse existing session storage)
        session_id = str(uuid.uuid4())
        generation_results[session_id] = {
            'status': 'completed',
            'design_id': result.design_id,
            'export_url': result.export_url,
            'html_snippet': result.html_snippet,
            'banner_url': result.export_url,
            'generation_mode': 'canva',
            'dimensions': f"{TEMPLATE_MAP[ad_size].canvas_w}x{TEMPLATE_MAP[ad_size].canvas_h}"
        }
        
        # Log total time
        total_time = (time.time() - start_time) * 1000
        logger.info(f"🎉 Total Canva generation time: {total_time:.1f}ms")
        
        # Return completed result immediately (no polling needed)
        # Frontend will handle this directly instead of polling for status
        return jsonify({
            'session_id': session_id,
            'design_id': result.design_id,
            'export_url': result.export_url,
            'html': result.html_snippet,
            'status': 'completed',
            'generation_time_ms': round(total_time, 1)
        })
        
    except Exception as e:
        # Handle rate limiting
        if '429' in str(e):
            return jsonify({'error': 'Rate limited by Canva API. Please try again later.'}), 503
        
        logger.error(f"Banner generation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_product_image():
    """Upload product image for banner generation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filepath': unique_filename,
                'filename': unique_filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-cropped', methods=['POST'])
def upload_cropped_image():
    """Upload cropped image data from canvas"""
    try:
        data = request.get_json()
        image_data = data.get('image_data')
        original_filename = data.get('filename', 'cropped_image.png')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Remove data URL prefix
        if image_data.startswith('data:image/'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image data
        try:
            img_bytes = base64.b64decode(image_data)
        except Exception:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Validate it's a valid image
        try:
            with Image.open(io.BytesIO(img_bytes)) as img:
                # Convert to RGB if necessary (for PNG with alpha)
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                
                # Generate unique filename
                unique_filename = f"{uuid.uuid4()}_cropped.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save as JPEG
                img.save(filepath, 'JPEG', quality=90)
                
                return jsonify({
                    'success': True,
                    'filepath': filepath,
                    'filename': unique_filename
                })
                
        except Exception as e:
            return jsonify({'error': f'Invalid image format: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/proxy-image', methods=['POST'])
def proxy_image():
    """Proxy image download to handle CORS issues for final use"""
    try:
        data = request.get_json()
        image_url = data.get('url')
        filename = data.get('filename', 'downloaded_image')
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Validate it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return jsonify({'error': 'URL does not point to a valid image'}), 400
        
        # Convert to PIL Image and save
        try:
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{secure_filename(filename)}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save as JPEG
            img.save(filepath, 'JPEG', quality=90)
            
            return jsonify({
                'success': True,
                'filepath': unique_filename,
                'filename': unique_filename,
                'is_extracted_image': True  # Mark as extracted image for cleanup
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/proxy-image-temp', methods=['POST'])
def proxy_image_temp():
    """Proxy image download for temporary cropping use only"""
    try:
        data = request.get_json()
        image_url = data.get('url')
        filename = data.get('filename', 'temp_crop_image')
        
        if not image_url:
            return jsonify({'error': 'No image URL provided'}), 400
        
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Validate it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return jsonify({'error': 'URL does not point to a valid image'}), 400
        
        # Convert to PIL Image and save temporarily
        try:
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
            
            # Generate unique temp filename
            unique_filename = f"temp_{uuid.uuid4()}_{secure_filename(filename)}.jpg"
            filepath = os.path.join(app.config['TEMP_FOLDER'], unique_filename)
            
            # Save as JPEG in temp folder
            img.save(filepath, 'JPEG', quality=90)
            
            return jsonify({
                'success': True,
                'temp_filename': unique_filename,
                'is_temp': True
            })
            
        except Exception as e:
            return jsonify({'error': f'Failed to process image: {str(e)}'}), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-temp/<filename>')
def download_temp_image(filename):
    """Serve temporary proxied images for cropping"""
    try:
        # Security check - only allow files in temp folder
        safe_filename = secure_filename(filename)
        filepath = os.path.join(app.config['TEMP_FOLDER'], safe_filename)
        
        if os.path.exists(filepath) and os.path.commonpath([filepath, app.config['TEMP_FOLDER']]) == app.config['TEMP_FOLDER']:
            return send_file(filepath)
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleanup-temp', methods=['POST'])
def cleanup_temp_image():
    """Clean up temporary image file"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
            
        safe_filename = secure_filename(filename)
        filepath = os.path.join(app.config['TEMP_FOLDER'], safe_filename)
        
        if os.path.exists(filepath) and os.path.commonpath([filepath, app.config['TEMP_FOLDER']]) == app.config['TEMP_FOLDER']:
            try:
                os.remove(filepath)
                logger.info(f"Cleaned up temp image: {filepath}")
                return jsonify({'success': True, 'message': 'Temp image cleaned up successfully'})
            except Exception as e:
                logger.warning(f"Failed to clean up temp image {filepath}: {e}")
                return jsonify({'error': f'Failed to clean up temp image: {str(e)}'}), 500
        else:
            return jsonify({'success': True, 'message': 'Temp image already cleaned up'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<session_id>')
def check_status(session_id):
    """Check generation status"""
    if session_id in generation_results:
        result = generation_results[session_id]
        if result.get('status') == 'completed':
            # Clean up old results (keep only last 10)
            if len(generation_results) > 10:
                oldest_key = min(generation_results.keys())
                del generation_results[oldest_key]
        return jsonify(result)
    else:
        return jsonify({'status': 'not_found'}), 404


@app.route('/api/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """Download generated files"""
    if session_id not in generation_results:
        return jsonify({'error': 'Session not found'}), 404
    
    result = generation_results[session_id]
    if result.get('status') != 'completed':
        return jsonify({'error': 'Generation not completed'}), 400
    
    file_path = None
    if file_type == 'banner':
        file_path = result.get('banner_path')
    elif file_type == 'html':
        file_path = result.get('html_path')
    elif file_type == 'css':
        file_path = result.get('css_path')
    
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/cache/<path:url>')
def check_cache_status(url):
    """Check if URL data is cached"""
    cached_data = get_cached_scraping_data(url)
    if cached_data:
        has_copy_cache = 'copy_variants' in cached_data
        return jsonify({
            'cached': True,
            'timestamp': cached_data['timestamp'],
            'age_seconds': time.time() - cached_data['timestamp'],
            'has_copy_cache': has_copy_cache,
            'copy_age_seconds': time.time() - cached_data.get('copy_timestamp', cached_data['timestamp']) if has_copy_cache else None
        })
    else:
        return jsonify({'cached': False, 'has_copy_cache': False})


@app.route('/api/copy-variants', methods=['POST'])
def get_copy_variants():
    """Generate copy variants for manual selection (Legacy endpoint - redirects to new workflow)"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check cache first for existing copy variants
        cached_copy_data = get_cached_copy_data(url)
        if cached_copy_data:
            return jsonify({
                'variants': cached_copy_data['copy_variants'],
                'cached': True
            })
        
        # Redirect to new workflow: require intelligent scraping first
        cached_page_data = get_cached_scraping_data(url)
        if not cached_page_data or 'lp_data' not in cached_page_data or 'page_meta' not in cached_page_data:
            return jsonify({
                'error': 'Please use "Intelligent Scraping" first, then "Generate Copy".',
                'require_scraping': True
            }), 400
        
        # Use cached data from intelligent scraping
        lp_data = cached_page_data['lp_data']
        page_meta = cached_page_data['page_meta']
        logger.info(f"Using cached data for copy variants: {url}")
        
        # Generate copy variants
        copy_variants = generate_copy_and_visual_prompts(
            text_content=lp_data['text_content'],
            title=page_meta['title'],
            description=page_meta['description']
        )
        
        # Cache the results
        best_copy = select_best_copy_for_banner(copy_variants, max_chars=60)
        cache_copy_data(url, copy_variants, best_copy)
        
        return jsonify({
            'variants': copy_variants,
            'cached': False,
            'source': 'intelligent_scraping'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-copy', methods=['POST'])
def generate_copy_variants():
    """Generate 5 editable copy variants using saved scraping results"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get saved scraping data from the intelligent scraping step
        cached_page_data = get_cached_scraping_data(url)
        
        if not cached_page_data or 'lp_data' not in cached_page_data or 'page_meta' not in cached_page_data:
            return jsonify({
                'error': 'No scraping data found. Please run "Intelligent Scraping" first.',
                'require_scraping': True
            }), 400
        
        lp_data = cached_page_data['lp_data']
        page_meta = cached_page_data['page_meta']
        llm_extracted_data = cached_page_data.get('llm_extracted_data', {})
        
        logger.info(f"Generating copy variants using cached data for {url}")
        
        # Generate 5 copy variants from scraped data using rich LLM extracted information
        copy_variants = generate_copy_and_visual_prompts(
            text_content=lp_data.get('text_content', ''),
            title=page_meta.get('title', ''),
            description=page_meta.get('description', ''),
            llm_extracted_data=llm_extracted_data
        )
        
        # Don't cache automatically - let user select first
        return jsonify({
            'success': True,
            'variants': copy_variants,
            'page_title': page_meta['title'],
            'page_description': page_meta['description'],
            'source': 'intelligent_scraping'
        })
        
    except Exception as e:
        logger.error(f"Copy generation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-selected-copy', methods=['POST'])
def save_selected_copy():
    """Save the user's selected and potentially edited copy"""
    try:
        data = request.get_json()
        url = data.get('url')
        selected_copy = data.get('selected_copy')
        
        if not url or not selected_copy:
            return jsonify({'error': 'URL and selected copy are required'}),
        # Cache the selected copy for this URL
        if url not in scraping_cache:
            scraping_cache[url] = {}
        
        scraping_cache[url].update({
            'selected_copy': selected_copy,
            'copy_selected_timestamp': time.time()
        })
        
        return jsonify({
            'success': True,
            'message': 'Selected copy saved successfully.'
        })
        
    except Exception as e:
        logger.error(f"Error saving selected copy: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-background', methods=['POST'])
@require_canva_auth
def generate_background():
    """Generate AI background image using user prompt"""
    try:
        from src.background_gen import generate_ai_background
        
        data = request.get_json()
        custom_background_prompt = data.get('custom_background_prompt')  # User-edited prompt from UI
        banner_size = data.get('banner_size', 'FB_SQUARE')  # Default to square
        
        if not custom_background_prompt or not custom_background_prompt.strip():
            return jsonify({'error': 'Background prompt is required'}), 400
        
        # Get authenticated Canva API instance
        api = get_authenticated_api()
        if not api:
            return jsonify({'error': 'Canva authentication required'}), 401
        
        logger.info(f"🎨 Using background prompt: {custom_background_prompt[:100]}...")
        
        # Generate AI background using the user prompt
        bg_gen_start = time.time()
        logger.info(f"🎨 Generating AI backgrounds using user prompt (banner size: {banner_size})")
        ai_background_images = generate_ai_background(custom_background_prompt.strip(), banner_size)
        bg_gen_time = (time.time() - bg_gen_start) * 1000
        logger.info(f"✅ AI backgrounds generated ({bg_gen_time:.1f}ms)")
        
        if ai_background_images:
            # Upload all images to Canva
            bg_upload_start = time.time()
            asset_ids = []
            background_urls = []
            
            for i, ai_background_data in enumerate(ai_background_images):
                logger.info(f"📤 Starting background {i+1} upload to Canva ({len(ai_background_data)} bytes)")
                asset_id = api.upload_binary(
                    ai_background_data,
                    f"ai_background_{i+1}.png",
                    "image/png"
                )
                asset_ids.append(asset_id)
                
                # Create preview URL with base64 data
                background_url = "data:image/png;base64," + __import__('base64').b64encode(ai_background_data).decode()
                background_urls.append(background_url)
                
                logger.info(f"✅ Background {i+1} uploaded to Canva: {asset_id}")
            
            bg_upload_time = (time.time() - bg_upload_start) * 1000
            logger.info(f"✅ All {len(asset_ids)} backgrounds uploaded to Canva ({bg_upload_time:.1f}ms)")
            
            return jsonify({
                'success': True,
                'background_asset_ids': asset_ids,
                'background_urls': background_urls,
                'generation_time_ms': bg_gen_time,
                'upload_time_ms': bg_upload_time,
                'count': len(asset_ids),
                'message': f'{len(asset_ids)} AI backgrounds generated successfully'
            })
        else:
            return jsonify({'error': 'Failed to generate AI backgrounds'}), 500
        
    except Exception as e:
        logger.error(f"Background generation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-explanation', methods=['POST'])
def generate_explanation():
    """Generate creative explanation and insights using saved scraping results"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get saved scraping data from the intelligent scraping step
        cached_page_data = get_cached_scraping_data(url)
        
        if not cached_page_data or 'lp_data' not in cached_page_data or 'page_meta' not in cached_page_data:
            return jsonify({
                'error': 'No scraping data found. Please run "Intelligent Scraping" first.',
                'require_scraping': True
            }), 400
        
        lp_data = cached_page_data['lp_data']
        page_meta = cached_page_data['page_meta']
        llm_extracted_data = cached_page_data.get('llm_extracted_data', {})
        
        logger.info(f"Generating explanation using cached data for {url}")
        
        # Generate creative explanation using the enhanced scraping data
        explanation = generate_creative_explanation(
            text_content=lp_data['text_content'],
            title=page_meta['title'],
            description=page_meta['description'],
            url=url,
            llm_extracted_data=llm_extracted_data
        )
        
        # Cache the explanation
        if url not in scraping_cache:
            scraping_cache[url] = {}
        
        scraping_cache[url].update({
            'explanation': explanation,
            'explanation_timestamp': time.time()
        })
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'page_title': page_meta['title'],
            'page_description': page_meta['description'],
            'source': 'intelligent_scraping'
        })
        
    except Exception as e:
        logger.error(f"Explanation generation error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract-images', methods=['POST'])
def extract_images():
    """Extract images from a URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract images from the URL
        images = extract_images_from_url(url)
        
        return jsonify({
            'success': True,
            'images': images,
            'count': len(images)
        })
        
    except Exception as e:
        logger.error(f"Image extraction error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def extract_images_from_url(url: str) -> list:
    """Extract images from a webpage URL using enhanced scraper with dynamic content support"""
    try:
        # Use enhanced scraper for dynamic content support
        import asyncio
        
        async def scrape_images_async():
            from enhanced_scraper import EnhancedWebScraper
            scraper = EnhancedWebScraper()
            # Use minimal scroll attempts for speed - just 1 attempt
            result = await scraper.scrape_page_comprehensive(url, include_images=True, max_scroll_attempts=1)
            return result.get('images', [])
        
        # Run async scraper with proper event loop handling
        # Try to use existing loop first
        try:
            loop = asyncio.get_running_loop()
            # If there's already a running loop, create a new thread for this
            import concurrent.futures
            import threading
            
            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(scrape_images_async())
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                raw_images = future.result(timeout=120)  # 2 minute timeout
                
        except RuntimeError:
            # No running loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                raw_images = loop.run_until_complete(scrape_images_async())
            finally:
                loop.close()
        
        # Convert to web UI format
        images = []
        for img in raw_images:
            image_info = {
                'src': img.get('src', ''),
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('naturalWidth', 0),
                'height': img.get('naturalHeight', 0),
                'size': None,  # Enhanced scraper doesn't provide file size
                'type': 'image/unknown',  # Enhanced scraper doesn't provide content type
                'displayWidth': img.get('displayWidth', 0),
                'displayHeight': img.get('displayHeight', 0),
                'area': img.get('area', 0),
                'isVisible': img.get('isVisible', True)
            }
            images.append(image_info)
        
        # Images from enhanced scraper are already sorted by area (largest first)
        # Limit to first 30 images to show more results while keeping reasonable performance
        logger.info(f"Enhanced scraper found {len(images)} images for {url}")
        return images[:30]
            
    except Exception as e:
        logger.error(f"Enhanced scraper failed for {url}: {e}", exc_info=True)
        logger.info("Falling back to basic requests-based image extraction...")
        
        # Fallback to basic approach
        return extract_images_from_url_fallback(url)


def extract_images_from_url_fallback(url: str) -> list:
    """Fallback image extraction using basic requests/HTML parsing"""
    try:
        # Send request to get the HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        from selectolax.parser import HTMLParser
        html = HTMLParser(response.text)
        
        # Find all image elements
        img_elements = html.css('img')
        images = []
        
        for img in img_elements:
            # Get image source
            src = img.attributes.get('src')
            if not src:
                continue
                
            # Convert relative URLs to absolute URLs
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(url, src)
            elif not src.startswith('http'):
                src = urljoin(url, src)
            
            # Get image metadata
            alt = img.attributes.get('alt', '')
            title = img.attributes.get('title', '')
            width = img.attributes.get('width')
            height = img.attributes.get('height')
            
            # Skip very small images without validation (faster fallback)
            if width and height:
                try:
                    w, h = int(width), int(height)
                    if w < 100 or h < 100:
                        continue
                except (ValueError, TypeError):
                    pass
            
            image_info = {
                'src': src,
                'alt': alt,
                'title': title,
                'width': width or 0,
                'height': height or 0,
                'size': None,
                'type': 'image/unknown'
            }
            
            images.append(image_info)
        
        # Basic sorting by width*height if available
        images_with_size = []
        images_without_size = []
        
        for img in images:
            if img['width'] and img['height']:
                try:
                    area = int(img['width']) * int(img['height'])
                    images_with_size.append((img, area))
                except (ValueError, TypeError):
                    images_without_size.append(img)
            else:
                images_without_size.append(img)
        
        # Sort by area (largest first)
        images_with_size.sort(key=lambda x: x[1], reverse=True)
        sorted_images = [img for img, _ in images_with_size] + images_without_size
        
        logger.info(f"Fallback scraper found {len(sorted_images)} images for {url}")
        return sorted_images[:20]
        
    except Exception as e:
        logger.error(f"Fallback image extraction also failed for {url}: {e}", exc_info=True)
        return []


def run_generation_async(session_id: str, url: str, mode: str, banner_size: str, product_image_path: Optional[str] = None):
    """Run banner generation asynchronously"""
    try:
        # Update status
        generation_results[session_id] = {
            'status': 'running',
            'progress': 0,
            'message': 'Starting generation...'
        }
        
        # Run the actual generation
        asyncio.set_event_loop(asyncio.new_event_loop())
        result = asyncio.run(
            generate_banner_async(session_id, url, mode, banner_size, product_image_path)
        )
        
        # Store final result
        generation_results[session_id] = result
        
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        generation_results[session_id] = {
            'status': 'error',
            'error': str(e),
            'progress': 0
        }


async def generate_banner_async(session_id: str, url: str, mode: str, banner_size: str, product_image_path: Optional[str] = None) -> Dict:
    """Async banner generation with progress updates"""
    try:
        # Parse dimensions
        if 'x' in banner_size:
            width, height = map(int, banner_size.split('x'))
        else:
            width = height = 1024
        
        # Update progress: Starting
        generation_results[session_id].update({
            'progress': 5,
            'message': 'Analyzing landing page...'
        })
        
        # Check cache first for scraping data
        cached_scraping_data = get_cached_scraping_data(url)
        
        if cached_scraping_data:
            lp_data = cached_scraping_data['lp_data']
            page_meta = cached_scraping_data['page_meta']
            logger.info(f"Using cached scraping data for {url}")
        else:
            # Scrape landing page
            logger.info(f"Scraping landing page: {url}")
            lp_data = await scrape_landing_page(url)
            page_meta = await get_page_title_and_description(url)
            
            # Cache the scraping results
            cache_scraping_data(url, lp_data, page_meta)
            logger.info(f"Cached scraping data for {url}")
        
        # Update progress: Page scraped
        generation_results[session_id].update({
            'progress': 15,
            'message': 'Using selected copy...'
        })
        
        # Use pre-selected copy from the separate copy generation step
        cached_data = get_cached_scraping_data(url)
        if not cached_data or 'selected_copy' not in cached_data:
            raise Exception("No copy has been selected. Please generate and select copy first.")
        
        best_copy = cached_data['selected_copy']
        logger.info(f"Using pre-selected copy: {best_copy['type']}")
        
        # Update progress: Copy loaded
        generation_results[session_id].update({
            'progress': 25,
            'message': 'Creating banner design...'
        })
        
        # Generate banner path
        session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_folder, exist_ok=True)
        banner_path = os.path.join(session_folder, 'banner.png')
        
        # Update progress: Starting banner generation
        generation_results[session_id].update({
            'progress': 50,
            'message': 'Generating banner with AI...'
        })
        
        # Generate banner
        banner_result = await generate_unified_creative(
            copy_text=best_copy['text'],
            copy_type=best_copy['type'],
            background_prompt=lp_data.get('visual_elements', ''),
            brand_context=f"{page_meta['title']} - {page_meta['description']}",
            product_context=lp_data.get('text_content', '')[:500],
            dimensions=(width, height),
            output_path=banner_path,
            product_image_path=product_image_path
        )
        
        if not banner_result.get('success'):
            raise Exception(f"Banner generation failed: {banner_result.get('error', 'Unknown error')}")
        
        # Update progress: Banner generated
        generation_results[session_id].update({
            'progress': 85,
            'message': 'Finalizing banner...'
        })
        
        # Determine image source
        image_source = "Product image + AI background" if product_image_path else "AI generated"
        
        # Update progress: Completed
        generation_results[session_id].update({
            'progress': 100,
            'message': 'Banner completed!'
        })
        
        # Prepare final result
        try:
            result = {
                'status': 'completed',
                'progress': 100,
                'message': 'Banner generated successfully!',
                'banner_path': banner_path,
                'html_path': None,  # HTML generation not implemented in unified mode
                'css_path': None,   # CSS generation not implemented in unified mode
                'image_source': image_source,
                'copy_used': best_copy,
                'banner_url': f'/api/download/{session_id}/banner',  # Direct URL instead of url_for
                'generation_mode': mode,
                'dimensions': f"{width}x{height}"
            }
            
            # Keep uploaded product image for potential reuse
            # Note: Image will be cleaned up when user uploads a new one or session ends
            if product_image_path and os.path.exists(product_image_path):
                logger.info(f"Keeping uploaded product image for reuse: {product_image_path}")
            
            logger.info(f"Generation completed successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Error finalizing result: {e}", exc_info=True)
            raise e
        
    except Exception as e:
        # Keep uploaded product image for potential reuse on failure
        # Note: Image will be cleaned up when user uploads a new one or session ends
        if product_image_path and os.path.exists(product_image_path):
            logger.info(f"Keeping uploaded product image after error for potential reuse: {product_image_path}")
        
        return {
            'status': 'error',
            'error': str(e),
            'progress': 0
        }


@app.route('/api/cleanup-image', methods=['POST'])
def cleanup_uploaded_image():
    """Clean up uploaded product image"""
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        
        if not image_path:
            return jsonify({'error': 'No image path provided'}), 400
            
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"Cleaned up uploaded product image: {image_path}")
                return jsonify({'success': True, 'message': 'Image cleaned up successfully'})
            except Exception as e:
                logger.warning(f"Failed to clean up image {image_path}: {e}")
                return jsonify({'error': f'Failed to clean up image: {str(e)}'}), 500
        else:
            return jsonify({'success': True, 'message': 'Image already cleaned up'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-background-to-design', methods=['POST'])
@require_canva_auth
def add_background_to_design():
    """Add background image to existing Canva design"""
    try:
        data = request.get_json()
        design_id = data.get('design_id')
        background_asset_id = data.get('background_asset_id')
        
        if not design_id:
            return jsonify({'error': 'Design ID is required'}), 400
            
        if not background_asset_id:
            return jsonify({'error': 'Background asset ID is required'}), 400
        
        # Get authenticated Canva API instance
        api = get_authenticated_api()
        if not api:
            return jsonify({'error': 'Canva authentication required'}), 401
        
        logger.info(f"Adding background {background_asset_id} to existing design {design_id}")
        
        # Import Canva client for element creation
        from src.simple_canva_upload import add_background_to_existing_design
        
        # Add background to the existing design
        result = add_background_to_existing_design(
            design_id=design_id,
            background_asset_id=background_asset_id,
            api=api
        )
        
        if result.success:
            logger.info(f"✅ Background added to design {design_id} successfully")
            return jsonify({
                'success': True,
                'design_id': design_id,
                'design_url': result.design_url,
                'message': 'Background added to design successfully'
            })
        else:
            logger.error(f"❌ Failed to add background to design: {result.error}")
            return jsonify({'error': result.error}), 500
            
    except Exception as e:
        logger.error(f"Error adding background to design: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/intelligent-scraping', methods=['POST'])
def intelligent_scraping():
    """Unified intelligent scraping endpoint using the new LLM scraper system"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check cache first
        cached_data = get_cached_scraping_data(url)
        if cached_data:
            logger.info(f"Returning cached intelligent scraping data for {url}")
            return jsonify({
                'success': True,
                'cached': True,
                'url': url,
                'extraction_method': cached_data.get('extraction_method', 'cached'),
                'confidence': cached_data.get('confidence', 1.0),
                'timestamp': cached_data.get('timestamp'),
                'llm_extracted_data': cached_data.get('llm_extracted_data', {}),
                'preprocessed_data_file': cached_data.get('preprocessed_data_file'),
                'page_title': cached_data.get('page_meta', {}).get('title', ''),
                'page_description': cached_data.get('page_meta', {}).get('description', '')
            })
        
        # Use the new LLM scraper
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            logger.info(f"Starting intelligent scraping for {url}")
            
            # Import and use the new scraper
            from src.llm_scraper import scrape_page_with_llm
            
            if not GOOGLE_API_KEY:
                return jsonify({'error': 'Google API key not configured'}), 500
            
            # Use the new LLM scraper
            result = loop.run_until_complete(
                scrape_page_with_llm(url, GOOGLE_API_KEY, save_preprocessed=True)
            )
            
            # Extract the clean results from the new format
            llm_extracted_data = result.get('llm_extracted_data', {})
            extraction_method = result.get('extraction_method', 'unknown')
            confidence = result.get('confidence', 0.0)
            preprocessed_data_file = result.get('preprocessed_data_file')
            
            # Create compatible format for existing system
            # Use LLM extracted data to create page_meta
            page_meta = {
                'title': llm_extracted_data.get('product_name', 'Page Title'),
                'description': llm_extracted_data.get('product_description', '')
            }
            
            # Create enhanced text content from LLM data for backward compatibility
            enhanced_content_parts = []
            if llm_extracted_data.get('product_name'):
                enhanced_content_parts.append(f"Product: {llm_extracted_data['product_name']}")
            if llm_extracted_data.get('product_description'):
                enhanced_content_parts.append(f"Description: {llm_extracted_data['product_description']}")
            if llm_extracted_data.get('key_features'):
                if isinstance(llm_extracted_data['key_features'], list):
                    enhanced_content_parts.append(f"Features: {', '.join(llm_extracted_data['key_features'])}")
                else:
                    enhanced_content_parts.append(f"Features: {llm_extracted_data['key_features']}")
            if llm_extracted_data.get('unique_selling_points'):
                enhanced_content_parts.append(f"Benefits: {llm_extracted_data['unique_selling_points']}")
            
            enhanced_text_content = " | ".join(enhanced_content_parts)
            
            # Create lp_data in compatible format
            lp_data = {
                'text_content': enhanced_text_content,
                'images': [],  # Not using images from LLM scraper for now
                'has_viable_image': False,
                'hero_image_data': None,
                'extraction_method': extraction_method,
                'llm_extracted_data': llm_extracted_data,
                'confidence': confidence
            }
            
            # Store all results in cache for later use
            cache_data = {
                'lp_data': lp_data,
                'page_meta': page_meta,
                'timestamp': result.get('timestamp', time.time()),
                'extraction_method': extraction_method,
                'confidence': confidence,
                'llm_extracted_data': llm_extracted_data,
                'preprocessed_data_file': preprocessed_data_file
            }
            
            # Cache using URL as key
            scraping_cache[url] = cache_data
            
            logger.info(f"Intelligent scraping completed for {url} with method: {extraction_method}, confidence: {confidence}")
            
            return jsonify({
                'success': True,
                'cached': False,
                'url': url,
                'extraction_method': extraction_method,
                'confidence': confidence,
                'timestamp': result.get('timestamp'),
                'llm_extracted_data': llm_extracted_data,
                'preprocessed_data_file': preprocessed_data_file,
                'page_title': page_meta['title'],
                'page_description': page_meta['description'],
                'model_used': result.get('model_used', 'gemini-2.5-flash-lite')
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Intelligent scraping error for {url}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape-llm', methods=['POST'])
def scrape_with_llm_endpoint():
    """Legacy API endpoint for LLM-enhanced web scraping (deprecated)"""
    try:
        data = request.get_json()
        url = data.get('url')
        use_llm = data.get('use_llm', True)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check cache first
        cached_data = get_cached_scraping_data(url)
        if cached_data:
            logger.info(f"Returning cached data for {url}")
            return jsonify({
                'cached': True,
                'lp_data': cached_data['lp_data'],
                'page_meta': cached_data['page_meta'],
                'extraction_method': cached_data['lp_data'].get('extraction_method', 'unknown')
            })
        
        # Perform scraping
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            lp_data, page_meta, used_llm = loop.run_until_complete(
                scrape_with_llm_fallback(url, use_llm)
            )
            
            # Cache the results
            cache_scraping_data(url, lp_data, page_meta)
            
            return jsonify({
                'cached': False,
                'lp_data': lp_data,
                'page_meta': page_meta,
                'extraction_method': lp_data.get('extraction_method', 'unknown'),
                'used_llm': used_llm,
                'llm_extraction': lp_data.get('llm_extraction') if used_llm else None
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"LLM scraping endpoint error: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)