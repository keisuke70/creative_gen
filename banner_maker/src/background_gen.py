#!/usr/bin/env python3
"""
Background generator utility for Canva banners.

Creates AI-generated background images with user-specified prompts and banner sizes.
"""

import os
import tempfile
import logging
from typing import Optional, List
from PIL import Image, ImageDraw
from dotenv import load_dotenv
from google import genai
from google.genai import types

from .canva_api import CanvaAPI

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

logger = logging.getLogger(__name__)


def get_aspect_ratio_for_banner_size(banner_size: str) -> str:
    """
    Map banner size to closest Gemini-supported aspect ratio.
    
    Gemini supports: "1:1", "3:4", "4:3", "9:16", and "16:9"
    
    Args:
        banner_size: Banner size identifier from UI
        
    Returns:
        Aspect ratio string supported by Gemini
    """
    # Banner size to dimensions mapping
    size_dimensions = {
        "MD_RECT": (300, 250),      # 1.2:1 -> closest to 4:3
        "LG_RECT": (336, 280),      # 1.2:1 -> closest to 4:3  
        "LEADERBOARD": (728, 90),   # 8.1:1 -> closest to 16:9
        "HALF_PAGE": (300, 600),    # 1:2 -> closest to 9:16
        "WIDE_SKYSCRAPER": (160, 600), # 1:3.75 -> closest to 9:16
        "FB_RECT_1": (1200, 628),   # 1.91:1 -> closest to 16:9
        "FB_SQUARE": (1200, 1200)   # 1:1 -> exact match 1:1
    }
    
    if banner_size not in size_dimensions:
        logger.warning(f"Unknown banner size: {banner_size}, defaulting to 1:1")
        return "1:1"
    
    width, height = size_dimensions[banner_size]
    ratio = width / height
    
    # Map to closest supported aspect ratio
    if ratio >= 1.6:  # Wide formats
        return "16:9"
    elif ratio >= 1.25:  # Medium wide
        return "4:3"
    elif ratio >= 0.9:  # Square-ish
        return "1:1"
    elif ratio >= 0.7:  # Portrait
        return "3:4"
    else:  # Tall portrait
        return "9:16"


def translate_prompt_to_english(japanese_prompt: str, client) -> str:
    """
    Translate Japanese prompt to English using Gemini.
    
    Args:
        japanese_prompt: Japanese prompt to translate
        client: Gemini client instance
        
    Returns:
        English translation of the prompt
    """
    try:
        translation_prompt = f"""Translate the following Japanese text to English for use in an AI image generation prompt. Keep it concise and descriptive for image generation:

{japanese_prompt}

English translation:"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=translation_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500
            )
        )
        
        english_prompt = response.text.strip()
        return english_prompt
        
    except Exception as e:
        logger.warning(f"Translation failed: {e}, using original prompt")
        return japanese_prompt


def generate_ai_background(prompt: str, banner_size: str = "FB_SQUARE") -> Optional[List[bytes]]:
    """
    Generate 3 AI background images using Gemini Imagen.
    Translates Japanese prompts to English for better image generation results.
    
    Args:
        prompt: User-provided prompt for background generation (Japanese or English)
        banner_size: Banner size identifier for aspect ratio determination
        
    Returns:
        List of PNG image data as bytes, or None if generation fails
    """
    try:
        # Set up Gemini client
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No GOOGLE_API_KEY found for AI background generation")
            return None
        
        client = genai.Client(api_key=api_key)
        
        # Translate Japanese prompt to English for better image generation
        english_prompt = translate_prompt_to_english(prompt, client)
        
        # Get aspect ratio based on banner size
        aspect_ratio = get_aspect_ratio_for_banner_size(banner_size)
        
        
        
        # Generate image with Gemini's Imagen model
        try:
            logger.info("Attempting background generation with imagen-4.0-generate-preview-06-06")
            response = client.models.generate_images(
                model="imagen-4.0-generate-preview-06-06",
                prompt=english_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=3,
                    output_mime_type="image/png",
                    aspect_ratio=aspect_ratio
                )
            )
            
            # Extract all image data from response
            images_data = []
            for i, generated_image in enumerate(response.generated_images):
                img_bytes = generated_image.image.image_bytes
                
                # Validate image data
                if not img_bytes or len(img_bytes) == 0:
                    logger.warning(f"Generated image {i+1} data is empty, skipping")
                    continue
                    
                images_data.append(img_bytes)
            
            if not images_data:
                raise RuntimeError("No valid image data generated")
            
            logger.info(f"Successfully generated {len(images_data)} AI background images using imagen-4.0-generate-preview-06-06")
            return images_data
            
        except Exception as imagen_error:
            logger.error(f"Imagen generation failed: {imagen_error}")
            return None
            
    except Exception as e:
        logger.warning(f"AI background generation failed: {e}")
        return None


def maybe_generate_background(prompt: str, banner_size: str, api: Optional[CanvaAPI] = None, palette: Optional[List[str]] = None) -> Optional[List[str]]:
    """
    Generate 3 AI background images or gradient fallback and upload to Canva.
    
    Args:
        prompt: User-provided prompt for background generation
        banner_size: Banner size identifier for aspect ratio determination
        api: Authenticated Canva API instance
        palette: Fallback color palette for gradient generation
        
    Returns:
        List of Canva asset IDs if successful, None if failure
    """
    # Get authenticated API
    if api is None:
        from .canva_oauth import get_authenticated_api
        api = get_authenticated_api()
        if not api:
            logger.warning("No authenticated Canva API available for background generation")
            return None
    
    try:
        # Try AI background generation first
        if prompt and prompt.strip():
            logger.info("Attempting AI background generation based on user prompt")
            ai_background_images = generate_ai_background(prompt.strip(), banner_size)
            
            if ai_background_images:
                asset_ids = []
                for i, ai_background_data in enumerate(ai_background_images):
                    asset_id = api.upload_binary(
                        ai_background_data,
                        f"ai_background_{i+1}.png",
                        "image/png"
                    )
                    asset_ids.append(asset_id)
                    logger.info(f"Generated AI background {i+1}: {asset_id}")
                
                logger.info(f"Generated {len(asset_ids)} AI backgrounds total")
                return asset_ids
            else:
                logger.warning("AI background generation failed, falling back to gradient")
        
        # Fallback to gradient if AI generation failed or no prompt
        if palette:
            logger.info("Generating gradient background as fallback")
            gradient_data = create_gradient_image(palette)
            
            asset_id = api.upload_binary(
                gradient_data,
                "gradient_background.png",
                "image/png"
            )
            
            logger.info(f"Generated gradient background: {asset_id}")
            return [asset_id]  # Return as list for consistency
        else:
            logger.info("No color palette available, skipping background generation")
            return None
        
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