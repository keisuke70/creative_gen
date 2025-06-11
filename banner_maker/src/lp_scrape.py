import asyncio
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page
from selectolax.parser import HTMLParser
import base64
from io import BytesIO
from PIL import Image


async def scrape_landing_page(url: str) -> Dict:
    """
    Scrape landing page for images and text content using Playwright.
    Returns the largest viable image (≥300px²) and page text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Faster loading with domcontentloaded instead of networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(1000)  # Reduced wait time
            
            # Get page content
            content = await page.content()
            
            # Extract text content more efficiently (focus on key areas)
            text_content = await page.evaluate("""
                () => {
                    // Focus on key content areas for faster extraction
                    const selectors = [
                        'h1', 'h2', 'h3', '.hero', '.banner', '.main-content', 
                        '.product-description', '.benefits', '.features', 'p'
                    ];
                    
                    const texts = [];
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const text = el.textContent?.trim();
                            if (text && text.length > 5 && text.length < 500) {
                                texts.push(text);
                            }
                        }
                        // Stop early if we have enough content
                        if (texts.join(' ').length > 1500) break;
                    }
                    
                    return texts.join(' ').slice(0, 2000);
                }
            """)
            
            # Get all images with their dimensions
            images = await page.evaluate("""
                () => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.map(img => ({
                        src: img.src,
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight,
                        alt: img.alt || '',
                        area: img.naturalWidth * img.naturalHeight
                    })).filter(img => img.area >= 300);
                }
            """)
            
            # Sort by area (largest first)
            images.sort(key=lambda x: x['area'], reverse=True)
            
            # Download the largest image if available
            hero_image_data = None
            if images:
                largest_img = images[0]
                try:
                    response = await page.goto(largest_img['src'])
                    if response and response.status == 200:
                        hero_image_data = await response.body()
                except Exception as e:
                    print(f"Failed to download image {largest_img['src']}: {e}")
            
            return {
                'url': url,
                'text_content': text_content,
                'images': images,
                'hero_image_data': hero_image_data,
                'has_viable_image': len(images) > 0
            }
            
        finally:
            await browser.close()


def parse_html_images(html_content: str) -> List[Dict]:
    """
    Fallback HTML parsing for image extraction using selectolax
    """
    tree = HTMLParser(html_content)
    imgs = tree.css('img')
    
    image_list = []
    for img in imgs:
        src = img.attributes.get('src', '')
        alt = img.attributes.get('alt', '')
        
        if src:
            image_list.append({
                'src': src,
                'alt': alt,
                'naturalWidth': 0,  # Unknown without browser rendering
                'naturalHeight': 0,
                'area': 0
            })
    
    return image_list


async def get_page_title_and_description(url: str) -> Dict[str, str]:
    """
    Extract page title and meta description for better context
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=15000)
            
            title = await page.title()
            description = await page.evaluate("""
                () => {
                    const metaDesc = document.querySelector('meta[name="description"]');
                    return metaDesc ? metaDesc.content : '';
                }
            """)
            
            return {
                'title': title,
                'description': description
            }
            
        except Exception as e:
            return {
                'title': '',
                'description': ''
            }
        finally:
            await browser.close()