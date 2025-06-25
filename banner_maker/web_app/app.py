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
from flask import Flask, render_template, request, jsonify, send_file, url_for
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

from src.lp_scrape import scrape_landing_page, get_page_title_and_description
from src.gpt_image import generate_unified_creative
from src.copy_gen import generate_copy_and_visual_prompts, select_best_copy_for_banner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'banner-maker-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store generation results temporarily
generation_results = {}

# Cache for scraping results (persists until page refresh)
scraping_cache = {}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_cached_scraping_data(url):
    """Get cached scraping data for a URL"""
    return scraping_cache.get(url)


def cache_scraping_data(url, lp_data, page_meta):
    """Cache scraping data for a URL"""
    if url not in scraping_cache:
        scraping_cache[url] = {}
    
    scraping_cache[url].update({
        'lp_data': lp_data,
        'page_meta': page_meta,
        'timestamp': time.time()
    })
    
    # Keep cache size manageable (max 50 URLs)
    if len(scraping_cache) > 50:
        # Remove oldest entry
        oldest_url = min(scraping_cache.keys(), key=lambda k: scraping_cache[k]['timestamp'])
        del scraping_cache[oldest_url]


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


@app.route('/')
def index():
    """Main banner creation interface"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_banner():
    """Generate banner from LP URL and optional product image"""
    try:
        data = request.get_json()
        url = data.get('url')
        generation_mode = 'unified'  # Only unified mode supported
        banner_size = data.get('banner_size', '1024x1024')
        copy_type = data.get('copy_type', 'auto')  # auto, benefit, urgency, promo
        copy_selection_mode = data.get('copy_selection_mode', 'auto')  # auto or manual
        selected_copy_index = data.get('selected_copy_index')  # for manual selection
        skip_copy = data.get('skip_copy', False)  # Skip copy generation if cached
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Start generation in background
        thread = threading.Thread(
            target=run_generation_async,
            args=(session_id, url, generation_mode, banner_size, copy_type, data.get('product_image_path'), skip_copy, copy_selection_mode, selected_copy_index)
        )
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'message': 'Banner generation started'
        })
        
    except Exception as e:
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
                'filepath': filepath,
                'filename': unique_filename
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
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
    """Generate copy variants for manual selection"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check cache first
        cached_copy_data = get_cached_copy_data(url)
        if cached_copy_data:
            return jsonify({
                'variants': cached_copy_data['copy_variants'],
                'cached': True
            })
        
        # Get page data - scrape if not available
        cached_page_data = get_cached_scraping_data(url)
        if not cached_page_data:
            # Auto-scrape the page
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            lp_data = loop.run_until_complete(scrape_landing_page(url))
            page_meta = loop.run_until_complete(get_page_title_and_description(url))
            
            # Cache the scraping results
            cache_scraping_data(url, lp_data, page_meta)
            
            loop.close()
        else:
            lp_data = cached_page_data['lp_data']
            page_meta = cached_page_data['page_meta']
        
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
            'cached': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_generation_async(session_id: str, url: str, mode: str, banner_size: str, copy_type: str, product_image_path: Optional[str] = None, skip_copy: bool = False, copy_selection_mode: str = 'auto', selected_copy_index: Optional[int] = None):
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
            generate_banner_async(session_id, url, mode, banner_size, copy_type, product_image_path, skip_copy, copy_selection_mode, selected_copy_index)
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


async def generate_banner_async(session_id: str, url: str, mode: str, banner_size: str, copy_type: str, product_image_path: Optional[str] = None, skip_copy: bool = False, copy_selection_mode: str = 'auto', selected_copy_index: Optional[int] = None) -> Dict:
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
            'message': 'Generating marketing copy...'
        })
        
        # Handle copy generation/selection
        if copy_selection_mode == 'manual' and selected_copy_index is not None:
            # Use manually selected copy
            cached_copy_data = get_cached_copy_data(url)
            if cached_copy_data and selected_copy_index < len(cached_copy_data['copy_variants']):
                copy_variants = cached_copy_data['copy_variants']
                best_copy = copy_variants[selected_copy_index]
                logger.info(f"Using manually selected copy variant: {selected_copy_index}")
            else:
                raise Exception("Selected copy variant not available")
        else:
            # Auto copy selection
            if skip_copy:
                # Use cached copy
                cached_copy_data = get_cached_copy_data(url)
                if cached_copy_data:
                    copy_variants = cached_copy_data['copy_variants']
                    best_copy = cached_copy_data['best_copy']
                    logger.info("Using cached copy data")
                else:
                    raise Exception("No cached copy data available for skip_copy mode")
            else:
                # Generate new copy
                copy_variants = generate_copy_and_visual_prompts(
                    text_content=lp_data['text_content'],
                    title=page_meta['title'],
                    description=page_meta['description']
                )
                
                # Select best copy for banner
                best_copy = select_best_copy_for_banner(copy_variants, max_chars=60)
                
                # Cache the copy results
                cache_copy_data(url, copy_variants, best_copy)
                logger.info("Generated and cached new copy variants")
        
        # Update progress: Copy generated
        generation_results[session_id].update({
            'progress': 35,
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)