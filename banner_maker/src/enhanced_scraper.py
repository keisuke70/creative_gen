"""
Enhanced Web Scraper
Robust Playwright-based scraper with comprehensive text extraction
"""

import asyncio
import re
import time
import requests
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page, Browser
from selectolax.parser import HTMLParser
import logging

try:
    from .scraper_config import ScraperConfig
except ImportError:
    from scraper_config import ScraperConfig

logger = logging.getLogger(__name__)

class EnhancedWebScraper:
    """Enhanced web scraper with comprehensive text extraction capabilities"""
    
    def __init__(self, config: ScraperConfig = None):
        self.config = config or ScraperConfig()
        self.seen_texts: Set[str] = set()
    
    async def scrape_page_comprehensive(self, url: str, 
                                      include_images: bool = True,
                                      max_scroll_attempts: int = 3,
                                      use_fallback: bool = True) -> Dict:
        """
        Comprehensive page scraping with enhanced text extraction
        
        Args:
            url: Target URL to scrape
            include_images: Whether to extract and download images
            max_scroll_attempts: Max attempts to handle infinite scroll
            use_fallback: Whether to use requests fallback if Playwright fails
            
        Returns:
            Dict with extracted content including text, images, metadata
        """
        # First try Playwright approach
        try:
            return await self._scrape_with_playwright(url, include_images, max_scroll_attempts)
        except Exception as playwright_error:
            logger.warning(f"Playwright approach failed: {playwright_error}")
            
            if use_fallback:
                logger.info("Attempting fallback with requests...")
                return await self._scrape_with_requests_fallback(url)
            else:
                raise playwright_error
    
    async def _scrape_with_playwright(self, url: str, include_images: bool, max_scroll_attempts: int) -> Dict:
        """Original Playwright-based scraping approach"""
        async with async_playwright() as p:
            # Launch browser with stealth options to bypass anti-bot measures
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Create context with realistic browser fingerprint
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='ja-JP',
                timezone_id='Asia/Tokyo',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Add stealth scripts to avoid detection
            await page.add_init_script("""
                // Override the navigator.webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                // Mock chrome object
                window.chrome = {
                    runtime: {}
                };
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Util.getPermissionState('granted') }) :
                        originalQuery(parameters)
                );
                
                // Hide automation indicators
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ja-JP', 'ja', 'en-US', 'en'],
                });
                
                // Mock screen properties
                Object.defineProperty(screen, 'width', { get: () => 1920 });
                Object.defineProperty(screen, 'height', { get: () => 1080 });
            """)
            
            try:
                # Phase 1: Load page and inject noise-hiding CSS
                await self._load_page_with_dynamic_content(page, url, max_scroll_attempts)
                
                # Phase 2: Extract comprehensive text content
                text_content = await self._extract_comprehensive_text(page, url)
                
                # Phase 3: Extract images if requested
                images = []
                hero_image_data = None
                if include_images:
                    images, hero_image_data = await self._extract_images_enhanced(page, url)
                
                # Phase 4: Extract metadata
                metadata = await self._extract_page_metadata(page)
                
                # Phase 5: Post-process and filter content
                filtered_content = self._post_filter_content(text_content)
                
                return {
                    'url': url,
                    'text_content': filtered_content,
                    'raw_text_content': text_content,
                    'images': images,
                    'hero_image_data': hero_image_data,
                    'has_viable_image': len(images) > 0,
                    'metadata': metadata,
                    'content_stats': {
                        'character_count': len(filtered_content),
                        'word_count': len(filtered_content.split()),
                        'image_count': len(images),
                        'extraction_timestamp': time.time()
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in Playwright scraping {url}: {e}")
                # Re-raise the exception to trigger fallback
                raise e
            finally:
                await browser.close()
                
    async def _scrape_with_requests_fallback(self, url: str) -> Dict:
        """Fallback scraping method using requests and selectolax"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            session = requests.Session()
            session.headers.update(headers)
            
            logger.info(f"Fetching URL with requests: {url}")
            response = session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            parser = HTMLParser(response.text)
            
            # Extract text using platform-specific selectors
            text_content = self._extract_text_from_html(parser, url)
            
            # Extract basic metadata
            metadata = self._extract_metadata_from_html(parser)
            
            logger.info(f"Requests fallback successful. Extracted {len(text_content)} characters")
            
            return {
                'url': url,
                'text_content': text_content,
                'raw_text_content': text_content,
                'images': [],  # No image extraction in fallback mode
                'hero_image_data': None,
                'has_viable_image': False,
                'metadata': metadata,
                'content_stats': {
                    'character_count': len(text_content),
                    'word_count': len(text_content.split()),
                    'image_count': 0,
                    'extraction_timestamp': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Requests fallback failed: {e}")
            return {
                'url': url,
                'text_content': '',
                'raw_text_content': '',
                'images': [],
                'hero_image_data': None,
                'has_viable_image': False,
                'metadata': {},
                'error': f"Both Playwright and requests fallback failed: {str(e)}"
            }
    
    def _extract_text_from_html(self, parser: HTMLParser, url: str) -> str:
        """Extract text from HTML using platform-specific selectors"""
        # Check for platform-specific selectors first
        platform_selectors = self.config.get_platform_selectors(url)
        if platform_selectors:
            all_texts = []
            for selector in platform_selectors:
                try:
                    elements = parser.css(selector)
                    for element in elements:
                        text = element.text(strip=True)
                        if text and text.strip():
                            all_texts.append(text.strip())
                except Exception as e:
                    logger.warning(f"Error with platform selector '{selector}' on {url}: {e}")
            
            if all_texts:
                logger.info(f"Used {len(platform_selectors)} platform-specific selectors for {url}")
                return "\n\n".join(all_texts)

        # Fallback to generic extraction
        logger.info(f"No platform-specific selectors found for {url}, using generic extraction.")
        
        # Remove noise elements for cleaner extraction
        for noise_selector in self.config.NOISE_SELECTORS:
            for element in parser.css(noise_selector):
                element.decompose()

        text_blocks = []
        seen_texts = set()
        
        for selector in self.config.get_all_content_selectors():
            for element in parser.css(selector):
                text = element.text(strip=True)
                
                # Basic filtering and deduplication
                if text and len(text) >= self.config.MIN_TEXT_LENGTH:
                    normalized_text = re.sub(r'\s+', ' ', text).lower()
                    if normalized_text not in seen_texts:
                        # Filter spam patterns
                        if not any(re.search(p, normalized_text, re.I) for p in self.config.SPAM_PATTERNS):
                            text_blocks.append(text)
                            seen_texts.add(normalized_text)
        
        return "\n\n".join(text_blocks)
    
    def _extract_metadata_from_html(self, parser: HTMLParser) -> Dict[str, str]:
        """Extract basic metadata from HTML"""
        metadata = {}
        
        # Title
        title_tag = parser.css_first('title')
        if title_tag:
            metadata['title'] = title_tag.text(strip=True)
        
        # Meta tags
        meta_tags = parser.css('meta')
        for meta in meta_tags:
            name = meta.attributes.get('name', '').lower()
            property_attr = meta.attributes.get('property', '').lower()
            content = meta.attributes.get('content', '')
            
            if name == 'description' and content:
                metadata['description'] = content
            elif name == 'keywords' and content:
                metadata['keywords'] = content
            elif property_attr == 'og:title' and content:
                metadata['og_title'] = content
            elif property_attr == 'og:description' and content:
                metadata['og_description'] = content
        
        # H1 tags
        h1_tags = parser.css('h1')
        if h1_tags:
            metadata['h1_text'] = ' | '.join([h1.text(strip=True) for h1 in h1_tags if h1.text(strip=True)])
        
        return metadata
    
    async def _load_page_with_dynamic_content(self, page: Page, url: str, 
                                            max_scroll_attempts: int) -> None:
        """Load page and handle dynamic content with anti-bot evasion"""
        
        # Retry logic for loading the page
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Loading page attempt {attempt + 1}/{max_retries}: {url}")
                
                # Minimal delay for speed optimization
                if attempt > 0:  # Only delay on retry attempts
                    await page.wait_for_timeout(500)
                
                # Fast loading strategy - prioritize speed over perfection
                if attempt == 0:
                    # First attempt: Just wait for DOM content loaded (fast)
                    await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                elif attempt == 1:
                    # Second attempt: Even more minimal wait
                    await page.goto(url, wait_until="commit", timeout=8000)
                else:
                    # Final attempt: Just navigate
                    await page.goto(url, timeout=5000)
                
                # Check if page loaded successfully
                page_title = await page.title()
                if page_title and not "error" in page_title.lower():
                    logger.info(f"Page loaded successfully: {page_title}")
                    break
                else:
                    logger.warning(f"Potential error page detected: {page_title}")
                    if attempt < max_retries - 1:
                        await page.wait_for_timeout(2000)
                        continue
                        
            except Exception as e:
                logger.warning(f"Page load attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                await page.wait_for_timeout(3000)
                continue
        
        # Mimic human interaction
        await page.mouse.move(100, 100)
        await page.wait_for_timeout(500)
        await page.mouse.move(200, 200)
        
        # Inject CSS to hide noise elements before content extraction
        try:
            await page.add_style_tag(content=self.config.get_noise_hiding_css())
        except Exception as e:
            logger.warning(f"Failed to inject CSS: {e}")
        
        # Handle infinite scroll and lazy loading
        await self._handle_dynamic_content_loading(page, max_scroll_attempts)
        
        # Final wait for any remaining dynamic content
        await page.wait_for_timeout(2000)

    async def _handle_dynamic_content_loading(self, page: Page, max_attempts: int) -> None:
        """Handle infinite scroll and lazy-loaded content - fast version"""
        
        # Minimal wait for initial content to load
        await page.wait_for_timeout(1000)
        
        # Quick scroll to trigger any lazy loading - limit attempts for speed
        scroll_attempts = min(max_attempts, 2)  # Max 2 attempts
        for attempt in range(scroll_attempts):
            # Get initial page height
            prev_height = await page.evaluate("document.body.scrollHeight")
            
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Quick wait for new content - much shorter timeout
            await page.wait_for_timeout(1000)
            
            # Check if new content loaded
            new_height = await page.evaluate("document.body.scrollHeight")
            
            if new_height == prev_height:
                break  # No new content loaded
                
        # Scroll back to top for consistent extraction
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)

    async def _wait_for_network_idle(self, page: Page, timeout: int = 10000) -> None:
        """Wait for network to be idle using generic Playwright mechanisms"""
        try:
            # Wait for network to be mostly idle (no more than 2 requests in 500ms)
            await page.wait_for_load_state('networkidle', timeout=timeout)
            logger.info("Network idle state achieved")
        except Exception as e:
            logger.warning(f"Network idle timeout ({timeout}ms): {e}")
            # Fallback: wait for DOM ready state
            try:
                await page.wait_for_function(
                    "document.readyState === 'complete'", 
                    timeout=min(timeout // 2, 5000)
                )
                logger.info("Document ready state achieved")
            except Exception as e2:
                logger.warning(f"Document ready state timeout: {e2}")
                # Final fallback: brief fixed wait
                await page.wait_for_timeout(2000)

    async def _wait_for_images_to_load(self, page: Page) -> None:
        """Fast image loading strategy - optimized for speed"""
        try:
            # Quick check for already loaded images
            await page.wait_for_function("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images.length === 0 || images.filter(img => 
                        img.complete && img.naturalWidth > 0
                    ).length >= Math.max(5, images.length * 0.6);  // Accept 60% loaded
                }
            """, timeout=3000)  # Much shorter timeout
            logger.info("Initial images loaded")
            
        except Exception:
            logger.info("Quick image check timeout - doing fast lazy loading")
            
            # Very fast lazy loading check
            try:
                # Quick scroll to bottom and back
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(800)   # Even shorter
                await page.evaluate("window.scrollTo(0, 0)")
                await page.wait_for_timeout(300)   # Brief stabilization
                
                logger.info("Fast lazy loading completed")
                    
            except Exception as e:
                logger.info(f"Fast lazy loading completed: {e}")

    async def _extract_comprehensive_text(self, page: Page, url: str) -> str:
        """
        Extracts text from a page, prioritizing platform-specific selectors.
        If platform-specific selectors are defined for the URL's domain,
        only those are used. Otherwise, it falls back to a general-purpose
        extraction using a broad set of content selectors.
        """
        # Check for platform-specific selectors first
        platform_selectors = self.config.get_platform_selectors(url)
        if platform_selectors:
            all_texts = []
            for selector in platform_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if text and text.strip():
                            all_texts.append(text.strip())
                except Exception as e:
                    logger.warning(f"Error with platform selector '{selector}' on {url}: {e}")
            
            if all_texts:
                logger.info(f"Used {len(platform_selectors)} platform-specific selectors for {url}")
                return "\n\n".join(all_texts)

        # Fallback to generic extraction if no platform selectors are found or they yield no text
        logger.info(f"No platform-specific selectors found for {url}, using generic extraction.")
        
        # Get platform-specific selectors for fallback approach
        platform_selectors = self.config.get_platform_selectors(url)
        
        # Extract text with prioritized approach
        text_content = await page.evaluate(f"""
            () => {{
                const primarySelectors = {self.config.PRIMARY_CONTENT_SELECTORS};
                const secondarySelectors = {self.config.SECONDARY_CONTENT_SELECTORS};
                const platformSelectors = {platform_selectors};
                
                const allTexts = [];
                const seenTexts = new Set();
                
                // Helper function to clean and validate text
                const cleanText = (text) => {{
                    if (!text) return '';
                    return text.trim().replace(/\\s+/g, ' ');
                }};
                
                const isValidText = (text) => {{
                    if (!text || text.length < {self.config.MIN_TEXT_LENGTH}) return false;
                    if (text.length > {self.config.MAX_TEXT_LENGTH}) return false;
                    if (seenTexts.has(text)) return false;
                    
                    // Filter obvious noise
                    const lowerText = text.toLowerCase();
                    const noisePatterns = ['cookie', 'privacy policy', 'terms of service', 
                                         'all rights reserved', '©', 'follow us', 'subscribe'];
                    return !noisePatterns.some(pattern => lowerText.includes(pattern));
                }};
                
                // Phase 1: Platform-specific selectors (highest priority for known sites)
                for (const selector of platformSelectors) {{
                    try {{
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {{
                            const text = cleanText(el.textContent);
                            if (isValidText(text)) {{
                                allTexts.push({{ text, priority: 'highest', selector }});
                                seenTexts.add(text);
                            }}
                        }}
                    }} catch (e) {{
                        console.warn('Error with platform selector', selector, e);
                    }}
                }}
                
                // Phase 2: Primary content
                for (const selector of primarySelectors) {{
                    try {{
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {{
                            const text = cleanText(el.textContent);
                            if (isValidText(text)) {{
                                allTexts.push({{ text, priority: 'high', selector }});
                                seenTexts.add(text);
                            }}
                        }}
                    }} catch (e) {{
                        console.warn('Error with selector', selector, e);
                    }}
                }}
                
                // Phase 3: Secondary content (if we need more)
                if (allTexts.join(' ').length < {self.config.MIN_TOTAL_LENGTH}) {{
                    for (const selector of secondarySelectors) {{
                        try {{
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {{
                                const text = cleanText(el.textContent);
                                if (isValidText(text)) {{
                                    allTexts.push({{ text, priority: 'medium', selector }});
                                    seenTexts.add(text);
                                }}
                            }}
                        }} catch (e) {{
                            console.warn('Error with secondary selector', selector, e);
                        }}
                    }}
                }}
                
                // Sort by priority and combine
                const priorityOrder = {{ 'highest': 4, 'high': 3, 'medium': 2, 'low': 1 }};
                allTexts.sort((a, b) => priorityOrder[b.priority] - priorityOrder[a.priority]);
                
                return allTexts.map(item => item.text).join(' ').slice(0, {self.config.MAX_TOTAL_LENGTH});
            }}
        """)
        
        return text_content or ""
    
    async def _extract_images_enhanced(self, page: Page, url: str) -> Tuple[List[Dict], Optional[bytes]]:
        """Enhanced image extraction with dynamic content waiting"""
        
        # Wait for images to load using generic strategies
        await self._wait_for_images_to_load(page)
        
        # Debug: Get detailed image information for troubleshooting
        debug_info = await page.evaluate("""
            () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                const totalImages = imgs.length;
                
                const imageDetails = imgs.map(img => {
                    const rect = img.getBoundingClientRect();
                    return {
                        src: img.src,
                        alt: img.alt || '',
                        title: img.title || '',
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight,
                        displayWidth: rect.width,
                        displayHeight: rect.height,
                        area: img.naturalWidth * img.naturalHeight,
                        isVisible: rect.width > 0 && rect.height > 0,
                        loading: img.loading || 'eager',
                        className: img.className || '',
                        complete: img.complete
                    };
                });
                
                const validImages = imageDetails.filter(img => {
                    // More lenient filtering for cross-platform compatibility
                    const hasValidSize = img.area >= 10000; // Minimum 100x100
                    const notDataUri = !img.src.includes('data:image');
                    const notIcon = !img.className.includes('icon');
                    const notLogo = !img.className.includes('logo');
                    const hasValidSrc = img.src && img.src.startsWith('http');
                    
                    // More flexible visibility check - accept if either display or natural dimensions are valid
                    const isVisuallyValid = img.isVisible || (img.naturalWidth > 0 && img.naturalHeight > 0);
                    
                    return hasValidSize && notDataUri && notIcon && notLogo && hasValidSrc && isVisuallyValid;
                });
                
                return {
                    totalFound: totalImages,
                    afterFiltering: validImages.length,
                    validImages: validImages.sort((a, b) => b.area - a.area),
                    sampleInvalid: imageDetails.filter(img => {
                        const hasValidSize = img.area >= 10000;
                        const notDataUri = !img.src.includes('data:image');
                        const notIcon = !img.className.includes('icon');
                        const notLogo = !img.className.includes('logo');
                        const hasValidSrc = img.src && img.src.startsWith('http');
                        const isVisuallyValid = img.isVisible || (img.naturalWidth > 0 && img.naturalHeight > 0);
                        
                        return !(hasValidSize && notDataUri && notIcon && notLogo && hasValidSrc && isVisuallyValid);
                    }).slice(0, 5) // First 5 invalid images for debugging
                };
            }
        """)
        
        logger.info(f"Image extraction debug for {url}:")
        logger.info(f"  Total images found: {debug_info['totalFound']}")
        logger.info(f"  After filtering: {debug_info['afterFiltering']}")
        if debug_info['afterFiltering'] == 0 and debug_info['totalFound'] > 0:
            logger.warning(f"  All {debug_info['totalFound']} images were filtered out!")
            for i, invalid in enumerate(debug_info['sampleInvalid'][:5]):
                src_display = invalid['src'][:60] + '...' if len(invalid['src']) > 60 else invalid['src']
                logger.warning(f"    Sample filtered image {i+1}: {src_display}")
                logger.warning(f"      Size: {invalid['naturalWidth']}x{invalid['naturalHeight']} (area: {invalid['area']})")
                logger.warning(f"      Display: {invalid['displayWidth']}x{invalid['displayHeight']}")
                logger.warning(f"      Visible: {invalid['isVisible']}, Complete: {invalid['complete']}")
                logger.warning(f"      Class: {invalid['className']}, Loading: {invalid['loading']}")
        elif debug_info['afterFiltering'] > 0:
            logger.info(f"  Successfully found {debug_info['afterFiltering']} valid images")
            for i, valid in enumerate(debug_info['validImages'][:3]):
                src_display = valid['src'][:60] + '...' if len(valid['src']) > 60 else valid['src']
                logger.info(f"    Valid image {i+1}: {src_display} ({valid['naturalWidth']}x{valid['naturalHeight']})")
        
        images = debug_info['validImages']
        
        # Download the largest viable image
        hero_image_data = None
        if images and len(images) > 0:
            try:
                largest_img = images[0]
                response = await page.goto(largest_img['src'])
                if response and response.status == 200:
                    hero_image_data = await response.body()
                    # Navigate back to the original page
                    await page.goto(url)
            except Exception as e:
                logger.warning(f"Failed to download hero image: {e}")
        
        return images, hero_image_data
    
    async def _extract_page_metadata(self, page: Page) -> Dict[str, str]:
        """Extract comprehensive page metadata"""
        
        metadata = await page.evaluate("""
            () => {
                const getMetaContent = (name) => {
                    const meta = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                    return meta ? meta.content : '';
                };
                
                return {
                    title: document.title || '',
                    description: getMetaContent('description'),
                    keywords: getMetaContent('keywords'),
                    author: getMetaContent('author'),
                    
                    // Open Graph
                    og_title: getMetaContent('og:title'),
                    og_description: getMetaContent('og:description'),
                    og_type: getMetaContent('og:type'),
                    og_image: getMetaContent('og:image'),
                    
                    // Twitter Card
                    twitter_title: getMetaContent('twitter:title'),
                    twitter_description: getMetaContent('twitter:description'),
                    twitter_image: getMetaContent('twitter:image'),
                    
                    // Schema.org
                    canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                    lang: document.documentElement.lang || '',
                    
                    // Additional context
                    h1_text: Array.from(document.querySelectorAll('h1'))
                            .map(h => h.textContent?.trim())
                            .filter(t => t)
                            .join(' | '),
                };
            }
        """)
        
        return metadata
    
    def _post_filter_content(self, text_content: str) -> str:
        """Post-process and filter extracted content for quality"""
        
        if not text_content:
            return ""
        
        # Remove spam patterns
        for pattern in self.config.SPAM_PATTERNS:
            text_content = re.sub(pattern, '', text_content, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Remove very short sentences that are likely noise
        sentences = [s.strip() for s in text_content.split('.') if len(s.strip()) > 15]
        
        # Rejoin and limit length
        filtered_content = '. '.join(sentences)
        
        return filtered_content[:self.config.MAX_TOTAL_LENGTH]

# Convenience function for backward compatibility
async def scrape_landing_page_enhanced(url: str) -> Dict:
    """Enhanced version of the original scrape_landing_page function"""
    scraper = EnhancedWebScraper()
    return await scraper.scrape_page_comprehensive(url)