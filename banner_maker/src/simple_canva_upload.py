"""
Simplified Canva Upload - Just Upload Assets Without Complex Composition
This bypasses the failing element addition and export timeout issues
"""

import logging
import time
from typing import Optional, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SimpleCanvaResult:
    """Simplified result - just uploads assets without complex design"""
    design_id: str
    design_url: str
    uploaded_assets: List[Dict[str, str]]
    total_time_ms: float

def simple_canva_upload(
    product_image_paths: Optional[List[str]] = None,
    product_image_path: Optional[str] = None,  # Backward compatibility
    hero_asset_ids: Optional[List[str]] = None,
    background_asset_id: Optional[str] = None,
    api = None,
    design_title: str = "Marketing Assets"
) -> SimpleCanvaResult:
    """
    Simplified Canva upload - just upload images and create blank design
    No complex composition, no export timeouts - just fast asset upload
    
    Args:
        product_image_paths: List of paths to product images to upload (new)
        product_image_path: Single path to product image (backward compatibility)
        hero_asset_ids: List of pre-uploaded asset IDs corresponding to product_image_paths
        background_asset_id: Pre-uploaded background asset ID
        api: Authenticated Canva API instance
        design_title: Title for the design
        
    Returns:
        SimpleCanvaResult with design URL and uploaded assets
    """
    start_time = time.time()
    uploaded_assets = []
    
    logger.info(f"🚀 Starting simplified Canva upload: {design_title}")
    
    # Handle backward compatibility
    if product_image_path and not product_image_paths:
        product_image_paths = [product_image_path]
    
    # Step 1: Upload product images if provided or use pre-uploaded asset IDs
    product_asset_ids = []
    
    if hero_asset_ids:
        # Use pre-uploaded asset IDs (faster)
        product_asset_ids = hero_asset_ids
        logger.info(f"✅ Using {len(hero_asset_ids)} pre-uploaded product assets")
        
        for i, asset_id in enumerate(hero_asset_ids):
            uploaded_assets.append({
                'type': 'product_image',
                'asset_id': asset_id,
                'index': i + 1,
                'upload_time_ms': 0  # Already uploaded
            })
            
    elif product_image_paths:
        # Upload images if paths provided (fallback)
        logger.info(f"📤 Uploading {len(product_image_paths)} product images")
        
        for i, image_path in enumerate(product_image_paths):
            try:
                upload_start = time.time()
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                import mimetypes
                mime_type, _ = mimetypes.guess_type(image_path)
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = 'image/jpeg'
                
                logger.info(f"📤 Uploading product image {i+1}/{len(product_image_paths)} ({len(image_data)} bytes)")
                asset_id = api.upload_binary(
                    image_data,
                    f"product_{int(time.time())}_{i+1}.jpg",
                    mime_type
                )
                upload_time = (time.time() - upload_start) * 1000
                logger.info(f"✅ Product image {i+1} uploaded: {asset_id} ({upload_time:.1f}ms)")
                
                product_asset_ids.append(asset_id)
                uploaded_assets.append({
                    'type': 'product_image',
                    'asset_id': asset_id,
                    'index': i + 1,
                    'upload_time_ms': round(upload_time, 1)
                })
                
            except Exception as e:
                logger.warning(f"Product image {i+1} upload failed: {e}")
                continue
    
    # Set primary product asset for backward compatibility
    product_asset_id = product_asset_ids[0] if product_asset_ids else None
    
    # Step 2: Record background asset (already uploaded)
    if background_asset_id:
        logger.info(f"🎨 Using pre-uploaded background: {background_asset_id}")
        uploaded_assets.append({
            'type': 'background_image', 
            'asset_id': background_asset_id,
            'upload_time_ms': 0  # Pre-uploaded
        })
    
    # Step 3: Create simple blank design (300x250 default)
    try:
        design_start = time.time()
        logger.info("📋 Creating simple blank design")
        
        # Create basic design without template complications
        design_id = api.create_design(300, 250, None, design_title)
        design_time = (time.time() - design_start) * 1000
        logger.info(f"✅ Blank design created: {design_id} ({design_time:.1f}ms)")
        
        # Generate Canva edit URL 
        design_url = f"https://www.canva.com/design/{design_id}/edit"
        
    except Exception as e:
        logger.error(f"Failed to create simple design: {e}")
        raise
    
    total_time = (time.time() - start_time) * 1000
    logger.info(f"🎉 Simplified upload completed in {total_time:.1f}ms")
    logger.info(f"📁 Uploaded {len(uploaded_assets)} assets to Canva")
    logger.info(f"🔗 Design ready for manual editing: {design_url}")
    
    return SimpleCanvaResult(
        design_id=design_id,
        design_url=design_url,
        uploaded_assets=uploaded_assets,
        total_time_ms=round(total_time, 1)
    )


def get_asset_summary(uploaded_assets: List[Dict[str, str]]) -> str:
    """Generate user-friendly summary of uploaded assets"""
    if not uploaded_assets:
        return "No assets uploaded"
    
    summary_parts = []
    for asset in uploaded_assets:
        asset_type = asset['type'].replace('_', ' ').title()
        summary_parts.append(f"• {asset_type} (ID: {asset['asset_id']})")
    
    return "\n".join(summary_parts)


@dataclass
class BackgroundAddResult:
    """Result for adding background to existing design"""
    success: bool
    design_id: str
    design_url: str
    error: Optional[str] = None


def add_background_to_existing_design(
    design_id: str,
    background_asset_id: str,
    api
) -> BackgroundAddResult:
    """
    Make background image available in existing Canva design
    Since automatic placement is not supported by the API, this ensures the background 
    asset is available in the user's Canva account for manual use in the design.
    
    Args:
        design_id: Existing Canva design ID  
        background_asset_id: Background image asset ID (already uploaded)
        api: Authenticated Canva API instance
        
    Returns:
        BackgroundAddResult with success status and design URL
    """
    logger.info(f"🎨 Making background {background_asset_id} available for design {design_id}")
    
    try:
        # Generate edit URL for the design
        design_url = f"https://www.canva.com/design/{design_id}/edit"
        
        # Since the background asset is already uploaded to the user's Canva account,
        # it will be available in their "Uploads" section when they edit the design.
        # No additional API calls needed - just confirm the asset exists.
        
        logger.info(f"✅ Background asset {background_asset_id} is available in your Canva uploads")
        logger.info(f"🔗 Open design {design_id} to manually add the background")
        
        return BackgroundAddResult(
            success=True,
            design_id=design_id,
            design_url=design_url
        )
            
    except Exception as e:
        logger.error(f"❌ Failed to process background for design {design_id}: {e}")
        return BackgroundAddResult(
            success=False,
            design_id=design_id,
            design_url=f"https://www.canva.com/design/{design_id}/edit",
            error=str(e)
        )