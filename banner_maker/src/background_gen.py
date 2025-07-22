#!/usr/bin/env python3
"""
Background generator utility for Canva banners.

Creates AI-generated background images tailored to marketing copy content,
with gradient fallback when AI generation fails.
"""

import os
import tempfile
import logging
import requests
import base64
from typing import Optional, List, Dict, Any
from PIL import Image, ImageDraw
from dotenv import load_dotenv
import openai
from io import BytesIO

from .canva_api import CanvaAPI, CanvaAPIError

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


logger = logging.getLogger(__name__)


def _extract_image_bytes(img_obj) -> bytes:
    """
    Accepts a single item from response.data and returns raw bytes.
    
    Works for gpt-image-1 (.b64_json) and DALL-E (.url).
    """
    if getattr(img_obj, "b64_json", None):
        return base64.b64decode(img_obj.b64_json)
    if getattr(img_obj, "url", None):
        resp = requests.get(img_obj.url, timeout=30)
        resp.raise_for_status()
        return resp.content
    raise RuntimeError("No image payload in response")


def maybe_generate_background(product, copy_content: Optional[Dict[str, Any]] = None, api: Optional[CanvaAPI] = None) -> Optional[str]:
    """
    Generate an AI background image tailored to the marketing copy, with gradient fallback.
    
    Args:
        product: Product object with palette attribute
        copy_content: Dictionary with headline, subline, and cta text for AI prompt generation
        api: Authenticated Canva API instance
        
    Returns:
        Canva asset ID if successful, None if failure
    """
    # Get authenticated API
    if api is None:
        from .canva_oauth import get_authenticated_api
        api = get_authenticated_api()
        if not api:
            logger.warning("No authenticated Canva API available for background generation")
            return None
    
    try:
        # Try AI background generation first if copy content is available
        if copy_content and copy_content.get('headline'):
            logger.info("Attempting AI background generation based on copy content")
            ai_background_data = generate_ai_background(copy_content, product)
            
            if ai_background_data:
                asset_id = api.upload_binary(
                    ai_background_data,
                    "ai_background.png",
                    "image/png"
                )
                logger.info(f"Generated AI background: {asset_id}")
                return asset_id
            else:
                logger.warning("AI background generation failed, falling back to gradient")
        
        # Fallback to gradient if no copy content or AI generation failed
        if hasattr(product, 'palette') and product.palette:
            logger.info("Generating gradient background as fallback")
            gradient_data = create_gradient_image(product.palette)
            
            asset_id = api.upload_binary(
                gradient_data,
                "gradient_background.png",
                "image/png"
            )
            
            logger.info(f"Generated gradient background: {asset_id}")
            return asset_id
        else:
            logger.info("No color palette available, skipping background generation")
            return None
        
    except Exception as e:
        logger.warning(f"Background generation failed: {e}")
        return None


def generate_ai_background_with_stored_prompt(copy_content: Dict[str, Any], product) -> Optional[bytes]:
    """
    Generate AI background image using the pre-generated prompt from copy generation.
    
    Args:
        copy_content: Dictionary containing headline, background_prompt, and other copy data
        product: Product object for additional context (mainly for fallback)
        
    Returns:
        PNG image data as bytes, or None if generation fails
    """
    try:
        # Set up OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("No OpenAI API key found for AI background generation")
            return None
        
        # Extract the pre-generated background prompt
        background_prompt = copy_content.get('background_prompt', '')
        copy_type = copy_content.get('type', 'neutral')
        headline = copy_content.get('headline', copy_content.get('text', ''))
        
        if not background_prompt:
            logger.warning("No background prompt found in copy content, falling back to basic generation")
            return generate_ai_background(copy_content, product)
        
        # Enhance the stored prompt with technical requirements for DALL-E
        enhanced_prompt = f"""
        {background_prompt}
        
        TECHNICAL REQUIREMENTS:
        - Composition optimized for text overlay readability
        - Professional marketing material aesthetic
        - 1024x1024 resolution optimized
        - No text, logos, or specific branded elements
        - Colors and mood should complement the message: "{headline[:50]}"
        - Suitable for {copy_type} marketing approach
        """.strip()
        
        logger.info(f"Generating AI background using stored prompt for {copy_type} copy")
        
        # Generate image with OpenAI gpt-image-1 (preferred) with DALL-E fallback
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Try gpt-image-1 first
        try:
            logger.info("Attempting background generation with gpt-image-1")
            response = client.images.generate(
                model="gpt-image-1",
                prompt=enhanced_prompt,
                size="1024x1024",
                n=1
            )
            
            # Extract image bytes (Base64 for gpt-image-1, URL for DALL-E)
            img_bytes = _extract_image_bytes(response.data[0])
            logger.info(f"Successfully generated AI background using gpt-image-1")
            return img_bytes
            
        except Exception as gpt_image_error:
            logger.warning(f"gpt-image-1 failed: {gpt_image_error}, falling back to DALL-E-3")
            
            # Fallback to DALL-E-3
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                
                # Download the generated image (DALL-E uses URLs)
                image_url = response.data[0].url
                image_response = requests.get(image_url, timeout=30)
                
                if image_response.status_code == 200:
                    logger.info(f"Successfully generated AI background using DALL-E-3 fallback")
                    return image_response.content
                else:
                    logger.error(f"Failed to download DALL-E generated image: {image_response.status_code}")
                    return None
                    
            except Exception as dalle_error:
                logger.error(f"Both gpt-image-1 and DALL-E-3 failed: {dalle_error}")
                return None
            
    except Exception as e:
        logger.warning(f"AI background generation with stored prompt failed: {e}")

def generate_ai_background(copy_content: Dict[str, Any], product) -> Optional[bytes]:
    """
    Generate AI background image using OpenAI DALL-E based on marketing copy content.
    
    Args:
        copy_content: Dictionary containing headline, subline, cta
        product: Product object for additional context
        
    Returns:
        PNG image data as bytes, or None if generation fails
    """
    try:
        # Set up OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("No OpenAI API key found for AI background generation")
            return None
        
        # Create contextual prompt for background generation
        headline = copy_content.get('headline', '')
        subline = copy_content.get('subline', '')
        cta = copy_content.get('cta', '')
        
        # Build a descriptive prompt for the background
        prompt_parts = []
        
        # Analyze copy to determine style and mood
        copy_text = f"{headline} {subline} {cta}".lower()
        
        # Determine background style based on copy content
        if any(word in copy_text for word in ['luxury', 'premium', 'elegant', 'sophisticated']):
            style = "luxury, elegant, sophisticated with gold accents and premium textures"
        elif any(word in copy_text for word in ['tech', 'digital', 'ai', 'innovation', 'modern']):
            style = "modern, tech-inspired with clean geometric patterns and digital aesthetics"
        elif any(word in copy_text for word in ['nature', 'organic', 'natural', 'eco', 'green']):
            style = "natural, organic with soft textures and earth tones"
        elif any(word in copy_text for word in ['energy', 'power', 'strong', 'dynamic', 'bold']):
            style = "dynamic, energetic with bold patterns and vibrant colors"
        elif any(word in copy_text for word in ['comfort', 'cozy', 'home', 'family', 'warm']):
            style = "warm, comfortable with soft textures and inviting tones"
        else:
            style = "clean, professional with subtle patterns and balanced composition"
        
        # Create the AI prompt
        background_prompt = f"""
        Create an abstract background image suitable for a marketing banner with the following characteristics:
        - Style: {style}
        - Mood: Professional yet engaging, suitable for the marketing message "{headline}"
        - Composition: Abstract patterns, textures, or geometric shapes that won't compete with text overlay
        - Color harmony: Balanced and sophisticated color palette
        - Focus: Background should be subtle enough to allow text to be readable when overlaid
        - No text, logos, or specific objects - purely abstract background patterns
        - High quality, professional marketing material aesthetic
        - Suitable for banner advertising format
        """.strip()
        
        logger.info(f"Generating AI background with prompt: {background_prompt[:100]}...")
        
        # Generate image with OpenAI gpt-image-1 (preferred) with DALL-E fallback
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Try gpt-image-1 first
        try:
            logger.info("Attempting background generation with gpt-image-1")
            response = client.images.generate(
                model="gpt-image-1",
                prompt=background_prompt,
                size="1024x1024",
                n=1
            )
            
            # Extract image bytes (Base64 for gpt-image-1, URL for DALL-E)
            img_bytes = _extract_image_bytes(response.data[0])
            logger.info("Successfully generated AI background image using gpt-image-1")
            return img_bytes
            
        except Exception as gpt_image_error:
            logger.warning(f"gpt-image-1 failed: {gpt_image_error}, falling back to DALL-E-3")
            
            # Fallback to DALL-E-3
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=background_prompt,
                    size="1024x1024",  # Standard size, will be resized as needed
                    quality="standard",
                    n=1
                )
                
                # Download the generated image (DALL-E uses URLs)
                image_url = response.data[0].url
                image_response = requests.get(image_url, timeout=30)
                
                if image_response.status_code == 200:
                    logger.info("Successfully generated AI background image using DALL-E-3 fallback")
                    return image_response.content
                else:
                    logger.error(f"Failed to download DALL-E generated image: {image_response.status_code}")
                    return None
                    
            except Exception as dalle_error:
                logger.error(f"Both gpt-image-1 and DALL-E-3 failed: {dalle_error}")
                return None
            
    except Exception as e:
        logger.warning(f"AI background generation failed: {e}")
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