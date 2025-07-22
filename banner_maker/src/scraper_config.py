"""
Scraper Configuration
Modular selector and filter configuration for robust web scraping
"""

from typing import List, Dict, Set

class ScraperConfig:
    """Configuration class for web scraping selectors and filters"""
    
    # Primary content selectors (high priority)
    PRIMARY_CONTENT_SELECTORS = [
        # Semantic HTML5 elements
        'article', 
        'section',
        '[role="main"]',
        '[itemprop~="articleBody"]',
        'main',
        
        # Common content containers
        '.content', '.main-content', '.post-content', '.article-content',
        '.entry-content', '.post-body', '.article-body',
        
        # Landing page specific
        '.hero', '.banner', '.intro', '.summary',
        '.product-description', '.benefits', '.features',
        '.value-proposition', '.selling-points'
    ]
    
    # Secondary content selectors (medium priority)
    SECONDARY_CONTENT_SELECTORS = [
        # Text elements
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'blockquote', 'pre',
        
        # Lists and structured content
        'li', 'dd', 'dt',
        'figcaption', 'caption',
        
        # Table content
        'td', 'th',
        
        # Forms and interactive elements
        'label[for]', '.field-description', '.help-text',
        
        # Comments and user content
        '.comment', '.review', '.testimonial', '.quote'
    ]
    
    # Noise elements to hide before scraping
    NOISE_SELECTORS = [
        'nav', 'footer', 'aside', 'header',
        '.nav', '.navigation', '.menu', '.sidebar',
        '.ads', '.advertisement', '.banner-ad', '.google-ads',
        '.social-share', '.social-media', '.share-buttons',
        '[aria-label*="cookie"]', '.cookie', '.gdpr',
        '.popup', '.modal', '.overlay',
        '.breadcrumb', '.pagination',
        'script', 'style', 'noscript'
    ]
    
    # Text filtering criteria
    MIN_TEXT_LENGTH = 10
    MAX_TEXT_LENGTH = 1000
    MIN_TOTAL_LENGTH = 100
    MAX_TOTAL_LENGTH = 8000
    
    # Content quality filters
    SPAM_PATTERNS = [
        r'click here', r'buy now', r'limited time',
        r'©\s*\d{4}', r'all rights reserved',
        r'terms of service', r'privacy policy',
        r'subscribe to', r'follow us'
    ]
    
    # Site-specific selectors for common platforms
    PLATFORM_SELECTORS = {
        'yodobashi': ['h1#products_maintitle span[itemprop="name"]', 'div.pDesBody'],
        'amazon': ['#productTitle', '#feature-bullets'],
        'rakuten': ['h1.product_name', 'div.p-product_details-spec'],
        'wordpress': ['.post', '.entry', '.content'],
        'shopify': ['.product-description', '.product-details', '.product-content'],
        'squarespace': ['.sqs-block-content', '.content'],
        'wix': ['.txtNew', '[data-testid="richTextElement"]'],
        'medium': ['.postArticle-content', '.section-content'],
        'ghost': ['.post-content', '.kg-post'],
        'webflow': ['.rich-text', '.text-block']
    }

    @classmethod
    def get_noise_hiding_css(cls) -> str:
        """Generates a CSS string to hide noise elements."""
        selectors = ", ".join(cls.NOISE_SELECTORS)
        return f"{selectors} {{ display: none !important; visibility: hidden !important; }}"

    @classmethod
    def get_all_content_selectors(cls) -> List[str]:
        """Get combined list of all content selectors"""
        return cls.PRIMARY_CONTENT_SELECTORS + cls.SECONDARY_CONTENT_SELECTORS
    
    @classmethod
    def get_platform_selectors(cls, url: str) -> List[str]:
        """Get platform-specific selectors based on URL.
        
        Stops after finding the first matching platform for efficiency.
        """
        url_lower = url.lower()
        
        for platform, selectors in cls.PLATFORM_SELECTORS.items():
            if platform in url_lower:
                return selectors
        return []