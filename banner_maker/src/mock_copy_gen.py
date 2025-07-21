#!/usr/bin/env python3
"""
Mock copy generation service - provides AI-generated copy without web scraping.

This bypasses the browser dependency issue by generating copy directly from URLs
without scraping, using OpenAI to generate contextual marketing copy.
"""

import re
from typing import List, Dict
from .copy_gen import generate_copy_and_visual_prompts

def extract_product_info_from_url(url: str) -> Dict[str, str]:
    """
    Extract basic product information from URL structure.
    
    Args:
        url: Product URL
        
    Returns:
        Dictionary with extracted info
    """
    # Extract domain
    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    domain = domain_match.group(1) if domain_match else "unknown"
    
    # Extract product keywords from URL path
    path_parts = url.split('/')
    product_keywords = []
    
    for part in path_parts:
        # Look for product identifiers
        if any(keyword in part.lower() for keyword in ['product', 'item', 'dp', 'p']):
            continue
        # Extract meaningful words (not IDs)
        words = re.findall(r'[a-zA-Z]+', part)
        product_keywords.extend([w for w in words if len(w) > 2])
    
    # Clean and deduplicate
    product_keywords = list(set([w.lower() for w in product_keywords if len(w) > 2]))[:5]
    
    return {
        'domain': domain,
        'product_keywords': product_keywords,
        'title': ' '.join(product_keywords[:3]).title() if product_keywords else 'Quality Product',
        'category': 'product'
    }

def generate_mock_copy_variants(url: str) -> List[Dict[str, str]]:
    """
    Generate copy variants from URL without web scraping.
    
    Args:
        url: Product URL
        
    Returns:
        List of copy variants
    """
    # Extract basic info from URL
    product_info = extract_product_info_from_url(url)
    
    # Create context for AI copy generation
    context = f"""
    Product URL: {url}
    Domain: {product_info['domain']}
    Product: {product_info['title']}
    Keywords: {', '.join(product_info['product_keywords'])}
    
    Generate marketing copy for this product based on the URL and keywords.
    """
    
    try:
        # Use existing copy generation function
        copy_variants = generate_copy_and_visual_prompts(
            text_content=context,
            title=product_info['title'],
            description=f"Product from {product_info['domain']}"
        )
        
        # Format variants properly
        formatted_variants = []
        for i, variant in enumerate(copy_variants):
            # Handle both string and dict variants
            text = variant if isinstance(variant, str) else str(variant.get('text', variant))
            
            formatted_variants.append({
                'type': ['benefit', 'urgency', 'promo', 'neutral', 'playful'][i % 5],
                'text': text,
                'score': 85 + (i * 2),  # Mock confidence score
                'source': 'ai_generated'
            })
        
        return formatted_variants
        
    except Exception as e:
        # Fallback to template-based copy
        print(f"AI copy generation failed: {e}")
        return generate_fallback_copy(product_info)

def generate_fallback_copy(product_info: Dict[str, str]) -> List[Dict[str, str]]:
    """Generate fallback copy when AI generation fails."""
    
    product_name = product_info.get('title', 'Premium Product')
    domain = product_info.get('domain', 'store')
    
    # Template-based copy variants
    templates = [
        {
            'type': 'benefit',
            'text': f"{product_name}\nQuality you can trust\nShop now and save!",
            'score': 80
        },
        {
            'type': 'urgency', 
            'text': f"Limited Time: {product_name}\nDon't miss out!\nOrder today",
            'score': 85
        },
        {
            'type': 'promo',
            'text': f"Special Offer: {product_name}\nBest price guaranteed\nBuy now",
            'score': 78
        },
        {
            'type': 'neutral',
            'text': f"{product_name}\nAvailable at {domain}\nLearn more",
            'score': 75
        },
        {
            'type': 'playful',
            'text': f"Get your {product_name}!\nYou'll love it\nTry it now",
            'score': 82
        }
    ]
    
    for template in templates:
        template['source'] = 'template'
    
    return templates