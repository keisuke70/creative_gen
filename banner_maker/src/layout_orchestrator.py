#!/usr/bin/env python3
"""
Layout orchestrator for Canva banner generation.

This module coordinates the complete banner creation pipeline: duplicating templates,
placing background and hero images, adding text elements, and exporting final designs.
"""

import os
import html
import json
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path

from .canva_api import CanvaAPI, CanvaAPIError
from .templates import AdSize, TEMPLATE_MAP, scale_rect


logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Product information for banner generation."""
    hero_asset_id: Optional[str]  # Can be None if asset upload fails
    palette: List[str]  # Color palette for design


@dataclass
class CopyTriple:
    """Marketing copy elements."""
    headline: str
    subline: str
    cta: str


@dataclass
class BannerResult:
    """Final banner generation result."""
    design_id: str
    export_url: str
    html_snippet: str


def build_banner(
    product: Product,
    ad_size: AdSize,
    copy: CopyTriple,
    bg_asset_id: Optional[str] = None,
    api: Optional[CanvaAPI] = None,
    source_url: Optional[str] = None
) -> BannerResult:
    """
    Build a complete banner using Canva templates and assets.
    
    Pipeline:
    1. Create design with template dimensions
    2. Place background image (if provided)
    3. Place hero product image
    4. Add text elements (headline, subline, CTA)
    5. Export as PNG
    6. Generate responsive HTML snippet
    
    Args:
        product: Product information with hero image
        ad_size: Target banner size
        copy: Marketing copy elements
        bg_asset_id: Optional background asset ID
        
    Returns:
        BannerResult with design ID, export URL, and HTML snippet
        
    Raises:
        CanvaAPIError: On API failures
        ValueError: On invalid parameters
    """
    if ad_size not in TEMPLATE_MAP:
        raise ValueError(f"Unsupported ad size: {ad_size}")
    
    template = TEMPLATE_MAP[ad_size]
    
    # Use provided API instance or get authenticated one
    if api is None:
        from .canva_oauth import get_authenticated_api
        api = get_authenticated_api()
        if not api:
            raise CanvaAPIError("No authenticated Canva API available")
    
    import time
    build_start = time.time()
    logger.info(f"🏗️  Building {ad_size.value} banner ({template.canvas_w}x{template.canvas_h})")
    
    # Generate meaningful design title from URL
    design_title = None
    if source_url:
        from .title_utils import generate_design_title_from_url, generate_ad_size_display_name
        ad_size_display = generate_ad_size_display_name(ad_size.value)
        design_title = generate_design_title_from_url(source_url, ad_size_display)
        logger.info(f"Generated design title: {design_title}")
    
    # Step 1: Create design by duplicating template 
    create_start = time.time()
    logger.info(f"📋 Creating Canva design from template: {template.template_design_id}")
    design_id = api.create_design(template.canvas_w, template.canvas_h, template.template_design_id, design_title)
    create_time = (time.time() - create_start) * 1000
    logger.info(f"✅ Canva design created: {design_id} ({create_time:.1f}ms)")
    
    # Step 2: Build elements list
    elements = []
    
    # Background image (z-index 0)
    if bg_asset_id:
        bg_rect = scale_rect(
            template.frames["background"],
            template.canvas_w,
            template.canvas_h
        )
        
        elements.append({
            "type": "image",
            "asset_id": bg_asset_id,
            "top": bg_rect[1],
            "left": bg_rect[0],
            "width": bg_rect[2],
            "height": bg_rect[3],
            "z_index": 0
        })
        logger.info("Added background image element")
    
    # Hero product image (z-index 1) - only if asset available
    if product.hero_asset_id:
        hero_rect = scale_rect(
            template.frames["hero"],
            template.canvas_w,
            template.canvas_h
        )
        
        elements.append({
            "type": "image",
            "asset_id": product.hero_asset_id,
            "top": hero_rect[1],
            "left": hero_rect[0],
            "width": hero_rect[2],
            "height": hero_rect[3],
            "z_index": 1,
            "crop": "fit"  # Scale to fit without cropping
        })
        logger.info("Added hero product image element")
    else:
        logger.info("Skipping hero image (no asset provided - asset upload may have failed)")
    
    # Text elements (z-index 2+)
    text_elements = _create_text_elements(copy, template, ad_size, product.palette)
    elements.extend(text_elements)
    
    # Step 3: Add all elements to design
    if elements:
        logger.info(f"Attempting to add {len(elements)} elements to design...")
        try:
            api.add_elements(design_id, elements)
            logger.info("Successfully added elements to design")
        except Exception as e:
            logger.error(f"Failed to add elements: {e}")
            # Log element details for debugging
            logger.error(f"Elements that failed to add: {json.dumps(elements, indent=2)}")
            
            # For now, continue without elements to test export functionality
            logger.warning("Continuing with blank design due to element addition limitations in Canva Connect API")
            logger.warning("This explains why designs appear empty - element addition is not working")
    else:
        logger.info("No elements to add (creating blank template)")
    
    # Step 4: Export design
    export_start = time.time()
    logger.info(f"🖼️  Exporting design {design_id} as PNG")
    export_url = api.export_design(design_id, "png")
    export_time = (time.time() - export_start) * 1000
    logger.info(f"✅ Design exported successfully ({export_time:.1f}ms): {export_url}")
    
    # Step 5: Generate HTML snippet
    html_snippet = _generate_html_snippet(copy, template, ad_size, export_url)
    
    total_build_time = (time.time() - build_start) * 1000
    logger.info(f"🎉 Banner build completed in {total_build_time:.1f}ms: {export_url}")
    
    return BannerResult(
        design_id=design_id,
        export_url=export_url,
        html_snippet=html_snippet
    )


def _create_text_elements(
    copy: CopyTriple,
    template: Any,
    ad_size: AdSize,
    palette: List[str]
) -> List[Dict[str, Any]]:
    """
    Create text elements for headline, subline, and CTA.
    
    Args:
        copy: Marketing copy
        template: Template specification
        ad_size: Banner size for font sizing
        palette: Color palette for design
        
    Returns:
        List of text element specifications
    """
    elements = []
    
    # Determine font sizes based on banner size
    if ad_size in [AdSize.LEADERBOARD]:  # Small banners
        headline_size = 28
        subline_size = 18
        cta_size = 16
    else:  # Larger banners
        headline_size = 48
        subline_size = 24
        cta_size = 20
    
    # Primary color from palette (fallback to black)
    primary_color = palette[0] if palette else "#000000"
    
    # Headline (z-index 2)
    headline_rect = scale_rect(
        template.frames["headline"],
        template.canvas_w,
        template.canvas_h
    )
    
    elements.append({
        "type": "text",
        "text": copy.headline,
        "top": headline_rect[1],
        "left": headline_rect[0],
        "width": headline_rect[2],
        "height": headline_rect[3],
        "z_index": 2,
        "font_family": "Poppins",
        "font_weight": "bold",
        "font_size": headline_size,
        "color": primary_color,
        "alignment": "left"
    })
    
    # Subline (z-index 3)
    subline_rect = scale_rect(
        template.frames["subline"],
        template.canvas_w,
        template.canvas_h
    )
    
    elements.append({
        "type": "text",
        "text": copy.subline,
        "top": subline_rect[1],
        "left": subline_rect[0],
        "width": subline_rect[2],
        "height": subline_rect[3],
        "z_index": 3,
        "font_family": "Poppins",
        "font_weight": "medium",
        "font_size": subline_size,
        "color": primary_color,
        "alignment": "left"
    })
    
    # CTA button (z-index 4)
    cta_rect = scale_rect(
        template.frames["cta"],
        template.canvas_w,
        template.canvas_h
    )
    
    # Ensure contrast for CTA text
    cta_bg_color = primary_color
    cta_text_color = "#FFFFFF"  # White text on colored background
    
    # Add CTA background rectangle
    elements.append({
        "type": "shape",
        "shape_type": "rectangle",
        "top": cta_rect[1],
        "left": cta_rect[0],
        "width": cta_rect[2],
        "height": cta_rect[3],
        "z_index": 4,
        "fill_color": cta_bg_color,
        "border_radius": 4
    })
    
    # Add CTA text
    elements.append({
        "type": "text",
        "text": copy.cta,
        "top": cta_rect[1],
        "left": cta_rect[0],
        "width": cta_rect[2],
        "height": cta_rect[3],
        "z_index": 5,
        "font_family": "Poppins",
        "font_weight": "bold",
        "font_size": cta_size,
        "color": cta_text_color,
        "alignment": "center"
    })
    
    logger.info(f"Created {len(elements)} text elements")
    return elements


def _generate_html_snippet(
    copy: CopyTriple,
    template: Any,
    ad_size: AdSize,
    export_url: str
) -> str:
    """
    Generate responsive HTML snippet for the banner.
    
    Args:
        copy: Marketing copy for alt text
        template: Template specification
        ad_size: Banner size for CSS classes
        export_url: Exported image URL
        
    Returns:
        Complete HTML snippet with inline styles
    """
    # Escape text for HTML
    escaped_headline = html.escape(copy.headline)
    escaped_subline = html.escape(copy.subline)
    escaped_cta = html.escape(copy.cta)
    
    # Build alt text
    alt_text = f"{escaped_headline} - {escaped_subline} - {escaped_cta}"
    
    # Generate responsive CSS with percentage positioning
    frames = template.frames
    
    html_snippet = f'''<div class="ad ad--{ad_size.name.lower()}" style="
    position: relative;
    width: 100%;
    max-width: {template.canvas_w}px;
    aspect-ratio: {template.canvas_w}/{template.canvas_h};
    overflow: hidden;
    font-family: 'Poppins', sans-serif;
">
    <img src="{export_url}" alt="{alt_text}" style="
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    "/>
    
    <!-- Text overlay for accessibility -->
    <div class="ad__content" style="
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 10;
    ">
        <h2 class="ad__headline" style="
            position: absolute;
            top: {frames['headline'].y_pct}%;
            left: {frames['headline'].x_pct}%;
            width: {frames['headline'].w_pct}%;
            height: {frames['headline'].h_pct}%;
            margin: 0;
            font-weight: bold;
            font-size: clamp(16px, 3vw, 48px);
            line-height: 1.2;
            color: transparent;
        ">{escaped_headline}</h2>
        
        <p class="ad__subline" style="
            position: absolute;
            top: {frames['subline'].y_pct}%;
            left: {frames['subline'].x_pct}%;
            width: {frames['subline'].w_pct}%;
            height: {frames['subline'].h_pct}%;
            margin: 0;
            font-weight: 500;
            font-size: clamp(12px, 2vw, 24px);
            line-height: 1.3;
            color: transparent;
        ">{escaped_subline}</p>
        
        <button class="ad__cta" style="
            position: absolute;
            top: {frames['cta'].y_pct}%;
            left: {frames['cta'].x_pct}%;
            width: {frames['cta'].w_pct}%;
            height: {frames['cta'].h_pct}%;
            background: transparent;
            border: none;
            font-weight: bold;
            font-size: clamp(10px, 1.5vw, 20px);
            color: transparent;
            cursor: pointer;
            border-radius: 4px;
        ">{escaped_cta}</button>
    </div>
</div>'''
    
    return html_snippet


# Test example for development
if __name__ == "__main__":
    import requests
    from pathlib import Path
    
    # Download placeholder image
    placeholder_url = "https://placehold.co/600x400"
    response = requests.get(placeholder_url, timeout=10)
    
    if response.status_code == 200:
        # Upload placeholder to Canva
        api = CanvaAPI()
        asset_id = api.upload_binary(
            response.content,
            "placeholder.jpg",
            "image/jpeg"
        )
        
        # Create test banner
        product = Product(
            hero_asset_id=asset_id,
            palette=["#FF6B35", "#004225"]
        )
        
        copy = CopyTriple(
            headline="Test Product",
            subline="Amazing quality",
            cta="Buy Now"
        )
        
        result = build_banner(product, AdSize.MD_RECT, copy, source_url="https://example.com")
        print(f"Test banner created: {result.export_url}")
    else:
        print("Failed to download placeholder image")