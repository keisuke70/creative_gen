#!/usr/bin/env python3
"""
Background generator utility for Canva banners.

Creates deterministic CSS gradients based on product color palettes,
renders them as images, and uploads to Canva for use as backgrounds.
"""

import os
import tempfile
import logging
from typing import Optional, List
from PIL import Image, ImageDraw
from dotenv import load_dotenv

from .canva_api import CanvaAPI, CanvaAPIError

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


logger = logging.getLogger(__name__)


def maybe_generate_background(product, api: Optional[CanvaAPI] = None) -> Optional[str]:
    """
    Generate a gradient background asset from product palette.
    
    Args:
        product: Product object with palette attribute
        
    Returns:
        Canva asset ID if successful, None if no palette or failure
    """
    if not hasattr(product, 'palette') or not product.palette:
        logger.info("No color palette available, skipping background generation")
        return None
    
    try:
        # Generate gradient image
        gradient_data = create_gradient_image(product.palette)
        
        # Upload to Canva using provided or authenticated API
        if api is None:
            from .canva_oauth import get_authenticated_api
            api = get_authenticated_api()
            if not api:
                logger.warning("No authenticated Canva API available for background generation")
                return None
        
        asset_id = api.upload_binary(
            gradient_data,
            "gradient_background.png",
            "image/png"
        )
        
        logger.info(f"Generated gradient background: {asset_id}")
        return asset_id
        
    except Exception as e:
        logger.warning(f"Background generation failed: {e}")
        return None


def create_gradient_image(
    colors: List[str],
    size: tuple = (1080, 1080),
    direction: str = "diagonal"
) -> bytes:
    """
    Create a gradient image from color palette.
    
    Args:
        colors: List of hex color codes
        size: Image dimensions (width, height)
        direction: Gradient direction ('horizontal', 'vertical', 'diagonal')
        
    Returns:
        PNG image data as bytes
    """
    width, height = size
    
    # Create image
    image = Image.new('RGB', size)
    draw = ImageDraw.Draw(image)
    
    if len(colors) == 1:
        # Solid color
        image = Image.new('RGB', size, colors[0])
    elif len(colors) == 2:
        # Two-color gradient
        image = _create_two_color_gradient(colors[0], colors[1], size, direction)
    else:
        # Multi-color gradient (use first two colors)
        image = _create_two_color_gradient(colors[0], colors[1], size, direction)
    
    # Save to bytes
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        image.save(tmp_file.name, 'PNG')
        
        with open(tmp_file.name, 'rb') as f:
            image_data = f.read()
        
        # Clean up temp file
        os.unlink(tmp_file.name)
        
    return image_data


def _create_two_color_gradient(
    color1: str,
    color2: str,
    size: tuple,
    direction: str
) -> Image.Image:
    """
    Create a two-color gradient.
    
    Args:
        color1: Start color (hex)
        color2: End color (hex)
        size: Image dimensions
        direction: Gradient direction
        
    Returns:
        PIL Image with gradient
    """
    width, height = size
    image = Image.new('RGB', size)
    
    # Convert hex colors to RGB
    rgb1 = _hex_to_rgb(color1)
    rgb2 = _hex_to_rgb(color2)
    
    # Generate gradient pixels
    for y in range(height):
        for x in range(width):
            # Calculate blend ratio based on direction
            if direction == "horizontal":
                ratio = x / width
            elif direction == "vertical":
                ratio = y / height
            elif direction == "diagonal":
                ratio = (x + y) / (width + height)
            else:
                ratio = x / width  # Default to horizontal
            
            # Blend colors
            r = int(rgb1[0] * (1 - ratio) + rgb2[0] * ratio)
            g = int(rgb1[1] * (1 - ratio) + rgb2[1] * ratio)
            b = int(rgb1[2] * (1 - ratio) + rgb2[2] * ratio)
            
            image.putpixel((x, y), (r, g, b))
    
    return image


def _hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000')
        
    Returns:
        RGB tuple (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        # Short format: #RGB -> #RRGGBB
        hex_color = ''.join(c * 2 for c in hex_color)
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        # Fallback to black for invalid colors
        logger.warning(f"Invalid hex color: {hex_color}, using black")
        return (0, 0, 0)