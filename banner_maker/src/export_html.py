from typing import Dict, Tuple
import os


def generate_banner_html_css(
    banner_image_path: str,
    copy_text: str,
    banner_size: Tuple[int, int] = (1200, 628),
    font_size: int = 48,
    output_dir: str = "."
) -> Dict:
    """
    Generate responsive HTML/CSS that recreates the banner layout using Flexbox
    """
    try:
        width, height = banner_size
        
        # Generate HTML content
        html_content = generate_html_template(
            banner_image_path, 
            copy_text, 
            width, 
            height
        )
        
        # Generate CSS content
        css_content = generate_css_template(
            banner_image_path,
            copy_text,
            width,
            height, 
            font_size
        )
        
        # Write files
        html_path = os.path.join(output_dir, "banner.html")
        css_path = os.path.join(output_dir, "banner.css")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        return {
            'success': True,
            'html_path': html_path,
            'css_path': css_path,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'html_path': None,
            'css_path': None
        }


def generate_html_template(
    image_path: str, 
    copy_text: str, 
    width: int, 
    height: int
) -> str:
    """
    Generate HTML template with semantic structure
    """
    image_filename = os.path.basename(image_path)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Banner</title>
    <link rel="stylesheet" href="banner.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="banner-container">
        <div class="banner-hero" role="img" aria-label="Hero banner image">
            <div class="banner-content">
                <h1 class="banner-text">{copy_text}</h1>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_template


def generate_css_template(
    image_path: str,
    copy_text: str, 
    width: int,
    height: int,
    font_size: int
) -> str:
    """
    Generate responsive CSS using Flexbox with mobile-first approach
    """
    image_filename = os.path.basename(image_path)
    aspect_ratio = (height / width) * 100  # For responsive aspect ratio
    
    css_template = f"""/* Banner Maker - Generated CSS */
/* Mobile-first responsive design */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.4;
}}

.banner-container {{
    width: 100%;
    max-width: {width}px;
    margin: 0 auto;
    position: relative;
}}

.banner-hero {{
    width: 100%;
    height: 0;
    padding-bottom: {aspect_ratio:.2f}%; /* Maintain aspect ratio */
    background-image: url('./{image_filename}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: flex-start;
    overflow: hidden;
}}

.banner-content {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20px;
    background: linear-gradient(
        transparent 0%,
        rgba(0, 0, 0, 0.1) 50%,
        rgba(0, 0, 0, 0.4) 100%
    );
    display: flex;
    align-items: flex-end;
}}

.banner-text {{
    color: #ffffff;
    font-weight: 800;
    font-size: clamp(18px, 4vw, {font_size}px);
    text-shadow: 
        2px 2px 4px rgba(0, 0, 0, 0.8),
        1px 1px 2px rgba(0, 0, 0, 0.5);
    line-height: 1.2;
    max-width: 70%;
    margin: 0;
}}

/* Mobile optimizations */
@media (max-width: 768px) {{
    .banner-content {{
        padding: 15px;
    }}
    
    .banner-text {{
        font-size: clamp(16px, 5vw, 32px);
        max-width: 85%;
    }}
}}

/* Large desktop optimization */
@media (min-width: 1400px) {{
    .banner-container {{
        max-width: 1400px;
    }}
    
    .banner-text {{
        font-size: {min(font_size + 8, 64)}px;
    }}
}}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {{
    .banner-hero {{
        background-image: url('./{image_filename}');
    }}
}}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {{
    .banner-hero {{
        background-attachment: scroll;
    }}
}}

/* Print styles */
@media print {{
    .banner-container {{
        max-width: none;
        width: 100%;
    }}
    
    .banner-text {{
        color: #000000;
        text-shadow: none;
    }}
    
    .banner-content {{
        background: rgba(255, 255, 255, 0.9);
    }}
}}

/* Focus states for accessibility */
.banner-hero:focus {{
    outline: 3px solid #007acc;
    outline-offset: 2px;
}}"""

    return css_template


def generate_react_component(
    image_path: str,
    copy_text: str,
    component_name: str = "MarketingBanner"
) -> str:
    """
    Generate React component version of the banner
    """
    image_filename = os.path.basename(image_path)
    
    react_component = f"""import React from 'react';
import './banner.css';

interface {component_name}Props {{
    imageUrl?: string;
    text?: string;
    className?: string;
}}

const {component_name}: React.FC<{component_name}Props> = ({{
    imageUrl = './{image_filename}',
    text = '{copy_text}',
    className = ''
}}) => {{
    return (
        <div className={{`banner-container ${{className}}`}}>
            <div 
                className="banner-hero"
                style={{{{ backgroundImage: `url(${{imageUrl}})` }}}}
                role="img"
                aria-label="Hero banner image"
            >
                <div className="banner-content">
                    <h1 className="banner-text">{{text}}</h1>
                </div>
            </div>
        </div>
    );
}};

export default {component_name};"""

    return react_component


def generate_vue_component(
    image_path: str,
    copy_text: str,
    component_name: str = "MarketingBanner"
) -> str:
    """
    Generate Vue component version of the banner
    """
    image_filename = os.path.basename(image_path)
    
    vue_component = f"""<template>
  <div class="banner-container" :class="className">
    <div 
      class="banner-hero"
      :style="{{ backgroundImage: `url(${{imageUrl}})` }}"
      role="img"
      aria-label="Hero banner image"
    >
      <div class="banner-content">
        <h1 class="banner-text">{{{{ text }}}}</h1>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {{
  imageUrl?: string;
  text?: string;
  className?: string;
}}

withDefaults(defineProps<Props>(), {{
  imageUrl: './{image_filename}',
  text: '{copy_text}',
  className: ''
}});
</script>

<style scoped>
@import './banner.css';
</style>"""

    return vue_component