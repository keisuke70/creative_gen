"""
LLM-Enhanced Web Scraper
Intelligent content extraction using Gemini 2.5 Flash Lite with structured output
"""

import asyncio
import re
import json
import time
import logging
import random
import hashlib
import os
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse
from google import genai
from playwright.async_api import Page
from selectolax.parser import HTMLParser
import markdown
import html2text
from pydantic import BaseModel, Field

from enhanced_scraper import EnhancedWebScraper

logger = logging.getLogger(__name__)

class ExtractedContent(BaseModel):
    """Pydantic model for structured content extraction"""
    product_name: Optional[str] = Field(default=None, description="Main product or service name")
    product_description: Optional[str] = Field(default=None, description="Detailed description of the product/service")
    key_features: Optional[List[str]] = Field(default=None, description="List of main features or benefits")
    price_info: Optional[str] = Field(default=None, description="Price, cost, or pricing information")
    brand_name: Optional[str] = Field(default=None, description="Brand or company name")
    category: Optional[str] = Field(default=None, description="Product category or type")
    target_audience: Optional[str] = Field(default=None, description="Who this product/service is for")
    unique_selling_points: Optional[str] = Field(default=None, description="What makes this special or different")
    call_to_action: Optional[str] = Field(default=None, description="Main action the page wants users to take")
    availability: Optional[str] = Field(default=None, description="Stock status, availability information")
    specifications: Optional[Dict[str, str]] = Field(default=None, description="Technical specs or detailed attributes")
    reviews_sentiment: Optional[str] = Field(default=None, description="General sentiment from reviews if present")

class LLMWebScraper(EnhancedWebScraper):
    """Enhanced web scraper that uses LLM for intelligent content extraction"""
    
    def __init__(self, google_api_key: str, config=None):
        super().__init__(config)
        # Initialize Gemini client
        self.client = genai.Client(api_key=google_api_key)
        self.model_name = 'gemini-2.5-flash-lite'  # Using stable model
        
        # HTML to text converter for preprocessing
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap lines
        
    def _save_preprocessed_data(self, url: str, preprocessed_content: str) -> str:
        """Save preprocessed data to a separate file and return the filename"""
        try:
            # Create a safe filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = f"preprocessed_{url_hash}.txt"
            
            # Save to current working directory
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Preprocessed Data for: {url}\n")
                f.write(f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*60 + "\n\n")
                f.write(preprocessed_content)
            
            logger.info(f"Preprocessed data saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save preprocessed data: {e}")
            return ""
        
    async def scrape_page_with_llm(self, url: str, 
                                  include_images: bool = True,
                                  max_scroll_attempts: int = 3,
                                  use_fallback: bool = True,
                                  extraction_schema: Optional[BaseModel] = None,
                                  save_preprocessed: bool = True) -> Dict:
        """
        Enhanced scraping using LLM for content extraction
        
        Args:
            url: Target URL to scrape
            include_images: Whether to extract images (deprecated, not used in clean output)
            max_scroll_attempts: Max scroll attempts for dynamic content
            use_fallback: Whether to use traditional tag-based fallback
            extraction_schema: Custom Pydantic schema for extraction
            save_preprocessed: Whether to save preprocessed data to separate files
            
        Returns:
            Dict with structured content extracted by LLM (clean format)
        """
        try:
            # Step 1: Try to get raw HTML for LLM processing (fast) and track method used
            raw_html, extraction_method = await self._get_raw_html_with_method(url)
            
            if raw_html and len(raw_html) > 1000:
                # We got good HTML content for LLM processing
                logger.info(f"Got HTML content using {extraction_method} method ({len(raw_html)} chars)")
            else:
                # Fallback to traditional scraper (but without retries if possible)
                logger.info("LLM HTML fetch failed, using traditional scraper")
                if use_fallback:
                    raw_result = await self.scrape_page_comprehensive(
                        url, include_images, max_scroll_attempts, use_fallback=False
                    )
                    raw_html = raw_result.get('raw_html', '')
                    extraction_method = 'traditional_scraper'
                else:
                    raise Exception("Unable to fetch HTML content")
            
            # Step 2: Prepare content for LLM processing
            preprocessed_content = self._preprocess_html_for_llm(raw_html)
            
            # Step 3: Save preprocessed data if requested
            preprocessed_file = ""
            if save_preprocessed and preprocessed_content:
                preprocessed_file = self._save_preprocessed_data(url, preprocessed_content)
            
            # Step 4: Extract structured data using LLM
            llm_extracted_data = await self._extract_with_llm_structured(
                preprocessed_content, url, extraction_schema
            )
            
            # Step 5: Return clean format as requested
            clean_result = {
                'url': url,
                'llm_extracted_data': llm_extracted_data.get('llm_extracted_data', {}),
                'extraction_method': extraction_method,
                'confidence': llm_extracted_data.get('extraction_confidence', 0.0),
                'timestamp': time.time(),
                'model_used': self.model_name
            }
            
            # Add preprocessed file info if saved
            if preprocessed_file:
                clean_result['preprocessed_data_file'] = preprocessed_file
            
            return clean_result
            
        except Exception as e:
            logger.error(f"LLM scraping failed for {url}: {e}")
            
            if use_fallback:
                logger.info("Falling back to traditional tag-based scraping...")
                return await super().scrape_page_comprehensive(url, include_images, max_scroll_attempts, use_fallback)
            else:
                raise e
    
    async def _get_raw_html_with_method(self, url: str) -> tuple[str, str]:
        """Get raw HTML content and track which method was successful - returns (html, method_name)"""
        
        # Strategy 1: Try Playwright FIRST (preferred when it works) - but with quick timeout
        try:
            logger.info(f"Attempting Playwright fetch for {url} (quick attempt)")
            html_content = await self._get_html_with_playwright_quick(url)
            if html_content and len(html_content) > 1000:
                logger.info(f"Playwright approach successful ({len(html_content)} chars)")
                return html_content, "playwright"
        except Exception as e:
            logger.info(f"Playwright quick attempt failed (expected for anti-bot sites): {e}")
        
        # Strategy 2: Fallback to requests (for anti-bot sites)
        try:
            logger.info(f"Attempting requests-based fetch for {url}")
            html_content = await self._get_html_with_requests(url)
            if html_content and len(html_content) > 1000:
                logger.info(f"Requests approach successful ({len(html_content)} chars)")
                return html_content, "requests"
        except Exception as e:
            logger.warning(f"Requests approach failed: {e}")
        
        logger.error("Both Playwright and requests approaches failed")
        return "", "failed"
    
    async def _get_raw_html(self, url: str) -> str:
        """Get raw HTML content - Playwright first (when possible), quick fallback to requests"""
        html_content, _ = await self._get_raw_html_with_method(url)
        return html_content
    
    async def _get_html_with_requests(self, url: str) -> str:
        """Advanced requests-based HTML fetching with comprehensive spoofing"""
        import requests
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        session = requests.Session()
        
        # Comprehensive headers to mimic real browser
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        session.headers.update(headers)
        
        # Multiple attempts with different strategies
        for attempt in range(3):
            try:
                logger.info(f"Requests attempt {attempt + 1} for {url}")
                
                # Random delay between attempts
                if attempt > 0:
                    delay = random.uniform(2, 5)
                    await asyncio.sleep(delay)
                
                # Try different referer strategies
                if attempt == 1:
                    session.headers['Referer'] = 'https://www.google.com/'
                elif attempt == 2:
                    session.headers['Referer'] = 'https://www.yodobashi.com/'
                
                # Make request with timeout
                response = session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                # Check if we got blocked (common anti-bot responses)
                if (response.status_code == 200 and 
                    len(response.text) > 1000 and
                    'blocked' not in response.text.lower() and
                    'captcha' not in response.text.lower() and
                    'access denied' not in response.text.lower()):
                    
                    logger.info(f"Requests successful on attempt {attempt + 1}")
                    return response.text
                else:
                    logger.warning(f"Attempt {attempt + 1}: Got response but appears blocked or empty")
                    continue
                    
            except Exception as e:
                logger.warning(f"Requests attempt {attempt + 1} failed: {e}")
                continue
        
        return ""
    
    async def _get_html_with_playwright_quick(self, url: str) -> str:
        """Quick Playwright attempt - fail fast if anti-bot detected (5s max)"""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # VERY quick single attempt - fail fast if anti-bot (5s max total)
                await page.goto(url, wait_until="domcontentloaded", timeout=5000)  # 5s max
                await page.wait_for_timeout(1000)  # Brief wait for dynamic content
                
                html_content = await page.content()
                if len(html_content) > 1000:
                    logger.info(f"Quick Playwright succeeded ({len(html_content)} chars)")
                    return html_content
                    
            except Exception as e:
                logger.info(f"Quick Playwright failed in 5s (expected for anti-bot): {e}")
            finally:
                await browser.close()
        
        return ""
    
    async def _get_html_with_playwright(self, url: str) -> str:
        """Playwright approach with maximum stealth (backup method)"""
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='ja-JP',
                timezone_id='Asia/Tokyo'
            )
            
            page = await context.new_page()
            
            try:
                # Single attempt with longer timeout
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)
                
                html_content = await page.content()
                if len(html_content) > 1000:
                    return html_content
                    
            except Exception as e:
                logger.error(f"Playwright approach failed: {e}")
            finally:
                await browser.close()
        
        return ""
    
    def _preprocess_html_for_llm(self, html_content: str) -> str:
        """
        Preprocess HTML content to optimize for LLM processing
        Removes noise, converts to markdown, and reduces token count
        """
        if not html_content:
            return ""
        
        try:
            # Parse HTML
            parser = HTMLParser(html_content)
            
            # Remove noise elements
            noise_selectors = [
                'script', 'style', 'noscript', 'meta', 'link',
                'nav', 'footer', 'header', 'aside',
                '.nav', '.navigation', '.menu', '.sidebar',
                '.ads', '.advertisement', '.banner-ad',
                '.social-share', '.social-media',
                '.cookie', '.gdpr', '.popup', '.modal',
                '.breadcrumb', '.pagination'
            ]
            
            for selector in noise_selectors:
                for element in parser.css(selector):
                    element.decompose()
            
            # Get cleaned HTML
            cleaned_html = str(parser.html)
            
            # Convert to markdown for better LLM processing
            markdown_content = self.html_converter.handle(cleaned_html)
            
            # Further clean the markdown
            markdown_content = self._clean_markdown_content(markdown_content)
            
            # Limit length to optimize token usage
            max_chars = 12000  # Roughly 3000-4000 tokens
            if len(markdown_content) > max_chars:
                # Truncate intelligently at sentence boundaries
                truncated = markdown_content[:max_chars]
                last_period = truncated.rfind('.')
                if last_period > max_chars * 0.8:  # If we can find a good break point
                    markdown_content = truncated[:last_period + 1]
                else:
                    markdown_content = truncated
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error preprocessing HTML: {e}")
            # Fallback: simple text extraction
            parser = HTMLParser(html_content)
            return parser.text()[:8000]  # Emergency fallback
    
    def _clean_markdown_content(self, markdown_content: str) -> str:
        """Clean and optimize markdown content for LLM processing"""
        
        # Remove excessive whitespace
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        markdown_content = re.sub(r'[ \t]+', ' ', markdown_content)
        
        # Remove common noise patterns
        noise_patterns = [
            r'Cookie.*?policy.*?\n',
            r'Accept.*?cookies.*?\n',
            r'Privacy.*?policy.*?\n',
            r'Terms.*?service.*?\n',
            r'©.*?reserved.*?\n',
            r'All rights reserved.*?\n',
            r'Follow us.*?\n',
            r'Subscribe.*?\n'
        ]
        
        for pattern in noise_patterns:
            markdown_content = re.sub(pattern, '', markdown_content, flags=re.IGNORECASE)
        
        # Remove excessive special characters
        markdown_content = re.sub(r'[*_]{3,}', '', markdown_content)
        markdown_content = re.sub(r'-{4,}', '---', markdown_content)
        
        return markdown_content.strip()
    
    async def _extract_with_llm_structured(self, content: str, url: str, schema: Optional[BaseModel] = None) -> Dict:
        """
        Use LLM with structured output to extract data from preprocessed content
        """
        # Use default schema if none provided
        schema_class = schema or ExtractedContent
        
        # Create the prompt for structured extraction
        prompt = f"""
Analyze the following webpage content and extract relevant information.

URL: {url}

WEBPAGE CONTENT:
{content}

Extract information about the product, service, or content from this page. Be precise and factual - only extract information that is clearly stated in the content.
"""
        
        try:
            # Create a simplified JSON schema for Gemini
            json_schema = {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Main product or service name"},
                    "product_description": {"type": "string", "description": "Detailed description of the product/service"},
                    "key_features": {"type": "array", "items": {"type": "string"}, "description": "List of main features or benefits"},
                    "price_info": {"type": "string", "description": "Price, cost, or pricing information"},
                    "brand_name": {"type": "string", "description": "Brand or company name"},
                    "category": {"type": "string", "description": "Product category or type"},
                    "target_audience": {"type": "string", "description": "Who this product/service is for"},
                    "unique_selling_points": {"type": "string", "description": "What makes this special or different"},
                    "call_to_action": {"type": "string", "description": "Main action the page wants users to take"},
                    "availability": {"type": "string", "description": "Stock status, availability information"},
                    "reviews_sentiment": {"type": "string", "description": "General sentiment from reviews if present"}
                }
            }
            
            # Call Gemini API with structured output
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": json_schema,
                }
            )
            
            # Parse the structured response
            if hasattr(response, 'parsed') and response.parsed:
                extracted_data = response.parsed
            else:
                # Fallback to parsing text response as JSON
                extracted_data = json.loads(response.text)
            
            # Ensure extracted_data is a dict
            if not isinstance(extracted_data, dict):
                extracted_data = {}
            
            # Calculate confidence based on completeness
            confidence = self._calculate_confidence_structured(extracted_data)
            
            return {
                'llm_extracted_data': extracted_data,
                'extraction_confidence': confidence,
                'extraction_timestamp': time.time(),
                'model_used': self.model_name,
                'structured_output': True
            }
            
        except Exception as e:
            logger.error(f"LLM structured extraction failed: {e}")
            return {
                'llm_extracted_data': {},
                'extraction_confidence': 0.0,
                'error': str(e),
                'structured_output': False
            }
    
    def _calculate_confidence_structured(self, extracted_data: Dict) -> float:
        """Calculate confidence score based on completeness and quality of structured extraction"""
        if not extracted_data:
            return 0.0
        
        # Count non-empty fields
        non_empty_fields = 0
        total_fields = 0
        
        for key, value in extracted_data.items():
            total_fields += 1
            if value is not None and str(value).strip() not in ['', 'null', 'None']:
                non_empty_fields += 1
        
        if total_fields == 0:
            return 0.0
        
        completeness_score = non_empty_fields / total_fields
        
        # Quality indicators
        quality_score = 0.0
        quality_total = 4
        
        # Check for key fields that indicate good extraction
        if extracted_data.get('product_name'):
            quality_score += 0.25
        if extracted_data.get('product_description') and len(str(extracted_data['product_description'])) > 20:
            quality_score += 0.25
        if extracted_data.get('key_features'):
            quality_score += 0.25
        if extracted_data.get('brand_name') or extracted_data.get('category'):
            quality_score += 0.25
        
        # Combined score (weighted average)
        confidence = (completeness_score * 0.7) + (quality_score * 0.3)
        return min(1.0, confidence)
    
    def _merge_extraction_results(self, traditional_result: Dict, llm_result: Dict) -> Dict:
        """Merge traditional scraping results with LLM extraction results"""
        
        # Start with traditional results
        merged_result = traditional_result.copy()
        
        # Add LLM-specific data
        merged_result.update({
            'llm_extraction': llm_result,
            'extraction_method': 'hybrid_llm_traditional',
            'llm_confidence': llm_result.get('extraction_confidence', 0.0)
        })
        
        # Enhance traditional text_content with LLM structured data if confidence is high
        if llm_result.get('extraction_confidence', 0) > 0.7:
            llm_data = llm_result.get('llm_extracted_data', {})
            
            # Create enhanced text content from structured data
            enhanced_sections = []
            
            if llm_data.get('product_name'):
                enhanced_sections.append(f"Product: {llm_data['product_name']}")
            
            if llm_data.get('product_description'):
                enhanced_sections.append(f"Description: {llm_data['product_description']}")
            
            if llm_data.get('key_features') and isinstance(llm_data['key_features'], list):
                enhanced_sections.append(f"Features: {', '.join(llm_data['key_features'])}")
            elif llm_data.get('key_features'):
                enhanced_sections.append(f"Features: {llm_data['key_features']}")
            
            if llm_data.get('unique_selling_points'):
                enhanced_sections.append(f"Key Benefits: {llm_data['unique_selling_points']}")
            
            if llm_data.get('price_info'):
                enhanced_sections.append(f"Price: {llm_data['price_info']}")
            
            if enhanced_sections:
                enhanced_text = " | ".join(enhanced_sections)
                merged_result['enhanced_text_content'] = enhanced_text
                
                # Use enhanced content as primary if it's more comprehensive
                original_length = len(merged_result.get('text_content', ''))
                if len(enhanced_text) > max(200, original_length * 0.3):  # If enhanced content is substantial
                    merged_result['text_content'] = enhanced_text
        
        return merged_result


# Convenience function for LLM-enhanced scraping
async def scrape_page_with_llm(url: str, google_api_key: str, 
                              extraction_schema: Optional[BaseModel] = None,
                              save_preprocessed: bool = True) -> Dict:
    """
    Convenience function for LLM-enhanced page scraping with structured output
    
    Args:
        url: URL to scrape
        google_api_key: Google API key for Gemini
        extraction_schema: Optional custom Pydantic schema for extraction
        save_preprocessed: Whether to save preprocessed data to separate files
        
    Returns:
        Clean extraction results with structured LLM analysis
    """
    scraper = LLMWebScraper(google_api_key)
    return await scraper.scrape_page_with_llm(url, extraction_schema=extraction_schema, 
                                            save_preprocessed=save_preprocessed)