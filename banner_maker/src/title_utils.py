#!/usr/bin/env python3
"""
Utility functions for generating meaningful design titles from URLs.
"""

import re
from urllib.parse import urlparse
from typing import Optional


def generate_design_title_from_url(url: str, ad_size_name: str = "Banner") -> str:
    """
    Generate a meaningful design title based on URL domain and context.
    
    Args:
        url: The landing page URL
        ad_size_name: The banner size/type for context
        
    Returns:
        A meaningful title for the Canva design
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extract the main domain name without TLD
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            # Get the main domain (e.g., 'shopify' from 'shopify.com')
            main_domain = domain_parts[0]
        else:
            main_domain = domain
        
        # Capitalize and clean up the domain name
        brand_name = main_domain.replace('-', ' ').replace('_', ' ').title()
        
        # Handle common patterns and improvements
        brand_name = _improve_brand_name(brand_name)
        
        # Create the title
        title = f"{brand_name} {ad_size_name}"
        
        # Add path context if it provides meaningful information
        path_context = _extract_path_context(parsed.path)
        if path_context:
            title = f"{brand_name} {path_context} {ad_size_name}"
        
        # Ensure title is within Canva's limits (1-255 characters)
        if len(title) > 255:
            title = title[:252] + "..."
        
        return title
        
    except Exception:
        # Fallback to a generic title if URL parsing fails
        return f"Marketing {ad_size_name}"


def _improve_brand_name(name: str) -> str:
    """Improve brand name recognition and formatting."""
    
    # Common brand name mappings
    improvements = {
        'Amazon': 'Amazon',
        'Google': 'Google', 
        'Microsoft': 'Microsoft',
        'Apple': 'Apple',
        'Facebook': 'Facebook',
        'Instagram': 'Instagram',
        'Twitter': 'Twitter',
        'Linkedin': 'LinkedIn',
        'Youtube': 'YouTube',
        'Shopify': 'Shopify',
        'Wordpress': 'WordPress',
        'Github': 'GitHub',
        'Mailchimp': 'Mailchimp',
        'Hubspot': 'HubSpot',
        'Salesforce': 'Salesforce'
    }
    
    # Check for exact matches first
    for key, value in improvements.items():
        if name.lower() == key.lower():
            return value
    
    # Check for partial matches
    for key, value in improvements.items():
        if key.lower() in name.lower():
            return value
    
    return name


def _extract_path_context(path: str) -> Optional[str]:
    """Extract meaningful context from URL path."""
    
    if not path or path == '/':
        return None
    
    # Remove leading/trailing slashes and split
    path_parts = path.strip('/').split('/')
    
    # Look for meaningful path segments
    context_keywords = {
        'product': 'Product',
        'products': 'Product',
        'service': 'Service', 
        'services': 'Service',
        'blog': 'Blog',
        'news': 'News',
        'about': 'About',
        'contact': 'Contact',
        'pricing': 'Pricing',
        'features': 'Features',
        'solutions': 'Solutions',
        'case-study': 'Case Study',
        'case-studies': 'Case Study',
        'testimonial': 'Testimonial',
        'testimonials': 'Testimonial',
        'demo': 'Demo',
        'trial': 'Trial',
        'signup': 'Signup',
        'register': 'Register',
        'login': 'Login',
        'download': 'Download',
        'shop': 'Shop',
        'store': 'Store',
        'catalog': 'Catalog',
        'category': 'Category',
        'landing': 'Landing',
        'campaign': 'Campaign',
        'promo': 'Promo',
        'offer': 'Offer',
        'deal': 'Deal',
        'special': 'Special'
    }
    
    # Find the first meaningful context in the path
    for part in path_parts:
        # Clean up the part
        clean_part = part.lower().replace('-', '').replace('_', '')
        
        # Check for exact matches
        if clean_part in context_keywords:
            return context_keywords[clean_part]
        
        # Check for partial matches
        for keyword, display in context_keywords.items():
            if keyword in clean_part or clean_part in keyword:
                return display
    
    return None


def generate_ad_size_display_name(ad_size_value: str) -> str:
    """Convert AdSize enum value to a human-readable display name."""
    
    size_mappings = {
        'MD_RECT': 'Medium Rectangle Banner',
        'LG_RECT': 'Large Rectangle Banner', 
        'LEADERBOARD': 'Leaderboard Banner',
        'HALF_PAGE': 'Half Page Banner',
        'WIDE_SKYSCRAPER': 'Skyscraper Banner',
        'FB_RECT_1': 'Facebook Banner',
        'FB_SQUARE': 'Facebook Square Banner'
    }
    
    return size_mappings.get(ad_size_value, 'Marketing Banner')
