import os
import logging
import base64
from typing import Dict, Optional
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client variable - will be initialized when first needed
client = None

def get_openai_client():
    """Get or create OpenAI client with lazy initialization"""
    global client
    if client is None:
        client = setup_openai_client()
    return client

def setup_openai_client() -> OpenAI:
    """
    Initialize OpenAI client (reads OPENAI_API_KEY from env or argument).
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable not set")

    logger.info(f"Setting up OpenAI client with API key: {api_key[:10]}...")

    # modern SDK no longer needs extra kwargs; pass only api_key
    client = OpenAI(api_key=api_key)   # no deprecated 'proxies' kw
    logger.info("OpenAI client created successfully")
    return client


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

async def generate_unified_creative(
    copy_text: str,
    copy_type: str,
    background_prompt: str = "",
    brand_context: str = "",
    product_context: str = "",
    dimensions: tuple = (1200, 628),
    output_path: str = "unified_banner.png",
    product_image_path: Optional[str] = None
) -> Dict:
    """
    Generate complete creative with text, layout, and styling in a single AI generation
    This is the new unified approach that creates everything at once
    """
    try:
        logger.info(f"Starting unified creative generation")
        logger.info(f"Copy text: {copy_text}")
        logger.info(f"Copy type: {copy_type}")
        logger.info(f"Dimensions: {dimensions}")
        logger.info(f"Output path: {output_path}")
        logger.info(f"Product image path: {product_image_path}")
        
        client = setup_openai_client()
        
        # Build comprehensive prompt for unified generation
        width, height = dimensions
        api_size = f"{width}x{height}"  # Convert dimensions to API format
        logger.info(f"Using API size parameter: {api_size}")
        
        # Font and style mapping based on copy type with dimension-aware layouts
        min_margin = max(60, width//20)
        max_text_width = int(width * 0.55)
        max_text_height = int(height * 0.20)
        suggested_font_size = max(24, min(width, height)//25)
        
        style_config = {
            'benefit': {
                'font': 'Inter Bold, clean sans-serif',
                'text_color': 'white with dark shadow',
                'atmosphere': 'professional and trustworthy',
                'layout': f'text bottom-left with {min_margin}px margins, max {max_text_width}px width, max {max_text_height}px height, {suggested_font_size}px font size'
            },
            'urgency': {
                'font': 'Impact or bold sans-serif',
                'text_color': 'bright yellow or orange with dark outline',
                'atmosphere': 'dynamic and energetic',
                'layout': f'text bottom-left with {min_margin}px margins, max {max_text_width}px width, max {max_text_height}px height, attention-grabbing but contained within {suggested_font_size}px font size'
            },
            'promo': {
                'font': 'Montserrat Bold',
                'text_color': 'bright contrasting color with shadow',
                'atmosphere': 'celebratory and exciting',
                'layout': f'text bottom-left with {min_margin}px margins, max {max_text_width}px width, max {max_text_height}px height, promotional feel with {suggested_font_size}px font size'
            },
            'neutral': {
                'font': 'Source Sans Pro',
                'text_color': 'dark gray or white with subtle shadow',
                'atmosphere': 'clean and minimalist',
                'layout': f'text bottom-left with {min_margin}px margins, max {max_text_width}px width, max {max_text_height}px height, elegant spacing with {suggested_font_size}px font size'
            },
            'playful': {
                'font': 'Nunito Bold or rounded sans-serif',
                'text_color': 'vibrant, fun colors with outline',
                'atmosphere': 'colorful and engaging',
                'layout': f'text bottom-left with {min_margin}px margins, max {max_text_width}px width, max {max_text_height}px height, creatively styled with {suggested_font_size}px font size'
            }
        }
        
        config = style_config.get(copy_type, style_config['benefit'])
        
        # Product integration strategy
        product_instruction = ""
        text_instruction = ""
        
        if product_image_path and os.path.exists(product_image_path):
            product_instruction = """PRESERVE the provided product image EXACTLY AS-IS without ANY modifications, alterations, or changes. Use the uploaded image in its original form, colors, lighting, and composition. DO NOT modify, enhance, recolor, resize, or alter the product image in any way. Place this unchanged product image prominently in the banner and create ONLY the background around it. The product image is perfect as provided and must remain completely unmodified."""
            text_instruction = f"""
TEXT INTEGRATION WITH PRODUCT IMAGE:
- Place the marketing text "{copy_text}" OUTSIDE the product image area
- Position text on the background area, not overlapping the product
- Text must stay within {int(width * 0.55)}px width and {int(height * 0.20)}px height limits
- Leave minimum {max(60, width//20)}px margins from all canvas edges
- Ensure the product image remains clean and unobstructed by text
- Text should complement the product, not compete with it
- Use the background space effectively for text placement"""
        else:
            product_instruction = f"Create or incorporate visual elements representing: {product_context[:200] if product_context else 'the business/service described'}"
            text_instruction = f"""
TEXT AS MAIN ELEMENT:
- The marketing text "{copy_text}" should be prominently featured
- Text must stay within {int(width * 0.55)}px width and {int(height * 0.20)}px height limits  
- Leave minimum {max(60, width//20)}px margins from all canvas edges
- Integrate text naturally with the visual design
- Text can be more prominent since there's no product image to compete with"""
        
        # Build unified prompt
        unified_prompt = f"""Create a complete marketing banner creative with the following specifications:

DIMENSIONS: {width} x {height} pixels (aspect ratio: {width/height:.2f})

MARKETING TEXT: "{copy_text}"
- Font: {config['font']} (must be bold and highly readable)
- Color: {config['text_color']} (ensure maximum contrast)
- Layout: {config['layout']}
- Style: {copy_type} marketing approach

{text_instruction}

VISUAL STYLE:
- Atmosphere: {config['atmosphere']}
- Background: {background_prompt or 'complementary professional background'}
- Brand context: {brand_context or 'modern business'}

CRITICAL PRODUCT IMAGE REQUIREMENTS:
{product_instruction}

TECHNICAL REQUIREMENTS:
- High resolution, print-ready quality
- Text must be clearly readable and properly positioned
- Professional marketing banner layout
- Colors should be vibrant but not overwhelming
- Maintain proper contrast for text readability
- Include subtle gradients or effects for premium feel

LAYOUT SPECIFICATIONS:
- Text placement: {config['layout']}
- Ensure text doesn't overlap important visual elements
- Leave appropriate margins and spacing
- Balance visual hierarchy between text and imagery

TEXT REQUIREMENTS FOR {width}x{height} CANVAS:
- Text: "{copy_text}"
- Position: Bottom-left with {min_margin}px margins from edges
- Fit within: {max_text_width}x{max_text_height}px text box
- Font: ~{suggested_font_size}px, high contrast with shadow/outline
- Split long text across 2-3 lines, reduce font if needed
- NEVER extend beyond canvas boundaries

FINAL REMINDER: If a product image was provided, use it EXACTLY as uploaded without any modifications whatsoever. The product image must remain in its original, unaltered state.

Create a complete, ready-to-use marketing banner that combines all these elements seamlessly with the text clearly visible and properly contained within the specified dimensions."""
        
        logger.info(f"Final unified prompt: {unified_prompt}")
        
        # Generate unified creative
        if product_image_path and os.path.exists(product_image_path):
            logger.info(f"Using product image for editing: {product_image_path}")
            # Use image editing API with the product image as base
            with open(product_image_path, 'rb') as image_file:
                logger.info("Calling OpenAI images.edit API...")
                response = get_openai_client().images.edit(
                    model="gpt-image-1",
                    image=image_file,
                    prompt=unified_prompt,
                    size=api_size,  # Use actual requested dimensions
                    n=1
                )
                logger.info("OpenAI edit API call successful")
        else:
            logger.info("Generating creative from scratch")
            # Generate from scratch
            logger.info("Calling OpenAI images.generate API...")
            response = get_openai_client().images.generate(
                model="gpt-image-1",
                prompt=unified_prompt,
                size=api_size,  # Use actual requested dimensions
                n=1
            )
            logger.info("OpenAI generate API call successful")
        
        # Extract image from response (Base64 for gpt-image-1, URL for DALL-E)
        logger.info("Processing generated creative image...")
        img_bytes = _extract_image_bytes(response.data[0])
        image = Image.open(BytesIO(img_bytes))
        logger.info(f"Original image size: {image.size}")
        
        # Verify dimensions match request (should not need resizing now)
        if image.size != dimensions:
            logger.warning(f"API returned {image.size} but requested {dimensions}, resizing...")
            image = image.resize(dimensions, Image.Resampling.LANCZOS)
        else:
            logger.info(f"Image generated at correct size: {image.size}")
        
        logger.info(f"Saving creative to: {output_path}")
        image.save(output_path, 'PNG', optimize=True, quality=95)
        logger.info("Creative saved successfully")
            
        return {
            'success': True,
            'output_path': output_path,
            'prompt_used': unified_prompt,
            'dimensions': dimensions,
            'copy_text': copy_text,
            'copy_type': copy_type,
            'generation_mode': 'unified',
            'product_integrated': product_image_path is not None,
            'error': None
        }
            
    except Exception as e:
        error_msg = f"Unified creative generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            'success': False,
            'error': error_msg,
            'output_path': None
        }