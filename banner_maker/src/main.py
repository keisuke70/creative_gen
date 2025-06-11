#!/usr/bin/env python3
"""
Banner Maker CLI - Generate marketing banners from landing pages
Usage: python -m banner_maker.main https://example.com/lp
"""

import asyncio
import sys
import os
import click
from typing import Dict, Optional

from .lp_scrape import scrape_landing_page, get_page_title_and_description
from .vision_crop import detect_objects_and_crop, create_fallback_crop
from .gpt_image import generate_hero_image, replace_background_with_ai, generate_background_prompt
from .copy_gen import generate_copy_and_visual_prompts, select_best_copy_for_banner
from .compose import create_enhanced_banner_composition
from .export_html import generate_banner_html_css


@click.command()
@click.argument('url')
@click.option('--fallback', type=click.Choice(['none', 'generate']), default='generate',
              help='Fallback strategy when no suitable image found (default: generate)')
@click.option('--enhance-bg', is_flag=True, default=True, 
              help='Enhance backgrounds with AI even when product image exists (default: true)')
@click.option('--output-dir', '-o', default='.', help='Output directory for generated files')
@click.option('--banner-size', default='1200x628', help='Banner dimensions (default: 1200x628)')
@click.option('--font-size', default=48, help='Font size for banner text (default: 48)')
@click.option('--skip-html', is_flag=True, help='Skip HTML/CSS generation')
@click.option('--disable-effects', is_flag=True, help='Disable visual effects and enhancements')
@click.option('--copy-selection', type=click.Choice(['auto', 'manual']), default='auto', help='Copy selection mode: auto or manual (default: auto)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(url: str, fallback: str, enhance_bg: bool, output_dir: str, banner_size: str, font_size: int, skip_html: bool, disable_effects: bool, copy_selection: str, verbose: bool):
    """
    Generate marketing banner from landing page URL
    
    Example:
        python -m banner_maker.main https://example.com/landing-page
    """
    asyncio.run(process_landing_page(
        url=url,
        fallback=fallback,
        enhance_bg=enhance_bg,
        output_dir=output_dir,
        banner_size=banner_size,
        font_size=font_size,
        skip_html=skip_html,
        disable_effects=disable_effects,
        copy_selection=copy_selection,
        verbose=verbose
    ))


async def process_landing_page(
    url: str,
    fallback: str = 'generate',
    enhance_bg: bool = True,
    output_dir: str = '.',
    banner_size: str = '1200x628',
    font_size: int = 48,
    skip_html: bool = False,
    disable_effects: bool = False,
    copy_selection: str = 'auto',
    verbose: bool = False
) -> Dict:
    """
    Main orchestrator function that processes a landing page through the full pipeline
    """
    if verbose:
        click.echo(f"🚀 Processing landing page: {url}")
    
    # Parse banner dimensions
    try:
        width, height = map(int, banner_size.split('x'))
        banner_dimensions = (width, height)
    except ValueError:
        click.echo("❌ Invalid banner size format. Use WIDTHxHEIGHT (e.g., 1200x628)")
        return {'success': False, 'error': 'Invalid banner size format'}
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    image_source = "UNKNOWN"
    hero_path = os.path.join(output_dir, "hero.png")
    banner_path = os.path.join(output_dir, "banner.png")
    
    try:
        # Step 1: Scrape landing page
        if verbose:
            click.echo("📄 Scraping landing page...")
        
        lp_data = await scrape_landing_page(url)
        
        if not lp_data['text_content']:
            click.echo("⚠️  Warning: No text content found on landing page")
        
        # Get additional page metadata
        page_meta = await get_page_title_and_description(url)
        
        # Step 2: Process hero image
        hero_success = False
        
        if lp_data['has_viable_image'] and lp_data['hero_image_data']:
            if verbose:
                click.echo("🖼️  Processing hero image from landing page...")
            
            # Try Google Vision object detection and cropping
            crop_result = detect_objects_and_crop(
                lp_data['hero_image_data'], 
                output_path=hero_path
            )
            
            if crop_result['success']:
                hero_success = True
                image_source = "LP"
                if verbose:
                    click.echo(f"✅ Object detected: {crop_result['object_name']} (confidence: {crop_result['confidence']:.2f})")
            else:
                if verbose:
                    click.echo(f"⚠️  Vision API failed: {crop_result['error']}")
                
                # Fallback to center crop
                fallback_crop_result = create_fallback_crop(
                    lp_data['hero_image_data'],
                    output_path=hero_path
                )
                
                if fallback_crop_result['success']:
                    hero_success = True
                    image_source = "LP"
                    if verbose:
                        click.echo("✅ Used center crop fallback")
        
        # Step 3: Generate image if needed
        if not hero_success and fallback == 'generate':
            if verbose:
                click.echo("🎨 Generating hero image with GPT-4.1 mini...")
            
            generation_result = await generate_hero_image(
                text_content=lp_data['text_content'],
                title=page_meta['title'],
                description=page_meta['description'],
                output_path=hero_path
            )
            
            if generation_result['success']:
                hero_success = True
                image_source = "GPT"
                if verbose:
                    click.echo("✅ Hero image generated successfully")
            else:
                click.echo(f"❌ Image generation failed: {generation_result['error']}")
        
        if not hero_success:
            click.echo("❌ Failed to obtain hero image")
            return {'success': False, 'error': 'No hero image available'}
        
        # Step 4: Generate marketing copy with visual prompts
        if verbose:
            click.echo("✍️  Generating marketing copy variants with visual prompts...")
        
        copy_variants = generate_copy_and_visual_prompts(
            text_content=lp_data['text_content'],
            title=page_meta['title'],
            description=page_meta['description']
        )
        
        # Select copy for banner
        copy_selection_result = select_best_copy_for_banner(
            copy_variants, 
            max_chars=60, 
            manual_selection=(copy_selection == 'manual')
        )
        
        # Handle manual selection mode
        if copy_selection == 'manual' and copy_selection_result.get('mode') == 'manual':
            if verbose:
                click.echo("📝 Available copy variants:")
                for i, variant in enumerate(copy_selection_result['variants'], 1):
                    click.echo(f"   {i}. {variant['type'].upper()}: {variant['text']}")
            
            # Prompt user to select
            while True:
                try:
                    choice = click.prompt('Select copy variant (1-3)', type=int)
                    if 1 <= choice <= len(copy_selection_result['variants']):
                        best_copy = copy_selection_result['variants'][choice - 1]
                        break
                    else:
                        click.echo("Invalid choice. Please select 1-3.")
                except (ValueError, click.Abort):
                    click.echo("Invalid input. Please enter a number 1-3.")
        else:
            best_copy = copy_selection_result
        
        if verbose:
            click.echo(f"📝 Selected copy ({best_copy['type']}): {best_copy['text']}")
            click.echo(f"🎨 Background prompt: {best_copy.get('background_prompt', 'N/A')}")
        
        # Step 5: Enhance background if product image exists and enhancement is enabled
        enhanced_hero_path = hero_path
        if hero_success and enhance_bg and image_source == "LP":
            if verbose:
                click.echo("🎨 Enhancing background with AI...")
            
            background_prompt = best_copy.get('background_prompt', 
                generate_background_prompt(best_copy['text'], best_copy['type']))
            
            enhance_result = replace_background_with_ai(
                product_image_path=hero_path,
                background_prompt=background_prompt,
                output_path=os.path.join(output_dir, "enhanced_hero.png")
            )
            
            if enhance_result['success']:
                enhanced_hero_path = enhance_result['enhanced_path']
                image_source = "LP+GPT"  # Indicate mixed source
                if verbose:
                    click.echo("✅ Background enhanced successfully")
            else:
                if verbose:
                    click.echo(f"⚠️  Background enhancement failed: {enhance_result['error']}")
        
        # Step 6: Compose final banner with enhanced visuals
        if verbose:
            click.echo("🎭 Composing enhanced banner...")
        
        composition_result = create_enhanced_banner_composition(
            hero_image_path=enhanced_hero_path,
            copy_text=best_copy['text'],
            copy_type=best_copy['type'],
            output_path=banner_path,
            banner_size=banner_dimensions,
            font_size=font_size,
            visual_effects=not disable_effects
        )
        
        if not composition_result['success']:
            click.echo(f"❌ Banner composition failed: {composition_result['error']}")
            return {'success': False, 'error': 'Banner composition failed'}
        
        # Step 7: Generate HTML/CSS
        if not skip_html:
            if verbose:
                click.echo("🌐 Generating HTML/CSS...")
            
            html_result = generate_banner_html_css(
                banner_image_path=banner_path,
                copy_text=best_copy['text'],
                banner_size=banner_dimensions,
                font_size=font_size,
                output_dir=output_dir
            )
            
            if html_result['success'] and verbose:
                click.echo("✅ HTML/CSS generated successfully")
        
        # Step 8: Output results
        click.echo(f"▸ banner.png")
        if not skip_html:
            click.echo(f"▸ banner.html / banner.css")
        click.echo(f"image_source={image_source}")
        
        if verbose:
            click.echo("\n📊 Generation Summary:")
            click.echo(f"   URL: {url}")
            click.echo(f"   Hero Source: {image_source}")
            click.echo(f"   Copy Type: {best_copy['type']}")
            click.echo(f"   Background Enhanced: {image_source == 'LP+GPT'}")
            click.echo(f"   Visual Effects: {not disable_effects}")
            click.echo(f"   Banner Size: {banner_dimensions[0]}×{banner_dimensions[1]}")
            click.echo(f"   Output Dir: {output_dir}")
        
        return {
            'success': True,
            'image_source': image_source,
            'banner_path': banner_path,
            'enhanced_hero_path': enhanced_hero_path if 'enhanced_hero_path' in locals() else hero_path,
            'copy_used': best_copy,
            'all_copy_variants': copy_variants,
            'background_enhanced': image_source == 'LP+GPT',
            'visual_effects_applied': not disable_effects
        }
        
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}")
        if verbose:
            import traceback
            click.echo(traceback.format_exc())
        return {'success': False, 'error': str(e)}


def check_dependencies():
    """
    Check if required dependencies and API keys are available
    """
    missing_deps = []
    
    # Check environment variables
    required_env_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for image generation and copy writing',
        'GOOGLE_APPLICATION_CREDENTIALS': 'Google Cloud credentials for Vision API'
    }
    
    for env_var, description in required_env_vars.items():
        if not os.getenv(env_var):
            missing_deps.append(f"Missing {env_var} ({description})")
    
    if missing_deps:
        click.echo("⚠️  Missing required dependencies:")
        for dep in missing_deps:
            click.echo(f"   • {dep}")
        click.echo("\nPlease set the required environment variables and try again.")
        return False
    
    return True


if __name__ == '__main__':
    # Check dependencies before running
    if not check_dependencies():
        sys.exit(1)
    
    main()