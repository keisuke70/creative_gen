#!/usr/bin/env python3
"""
Test script for LLM-enhanced web scraper
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llm_scraper import scrape_page_with_llm

# Load environment variables
load_dotenv()

async def test_llm_scraper():
    """Test the LLM scraper with various URLs"""
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    # Test URLs
    test_urls = [
        "https://www.yodobashi.com/product/100000001003310299/",  # Yodobashi product
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing LLM scraper with: {url}")
        print("=" * 50)
        
        try:
            result = await scrape_page_with_llm(url, api_key)
            
            print(f"✅ Scraping successful!")
            print(f"📄 Text content length: {len(result.get('text_content', ''))}")
            print(f"🖼️  Images found: {len(result.get('images', []))}")
            print(f"🤖 Extraction method: {result.get('extraction_method', 'unknown')}")
            
            # LLM extraction details
            llm_extraction = result.get('llm_extraction', {})
            if llm_extraction:
                confidence = llm_extraction.get('extraction_confidence', 0)
                print(f"🎯 LLM confidence: {confidence:.2f}")
                
                extracted_data = llm_extraction.get('llm_extracted_data', {})
                if extracted_data:
                    print(f"📦 Product name: {extracted_data.get('product_name', 'N/A')}")
                    print(f"🏷️  Brand: {extracted_data.get('brand_name', 'N/A')}")
                    print(f"💰 Price info: {extracted_data.get('price_info', 'N/A')}")
                    print(f"📝 Description: {extracted_data.get('product_description', 'N/A')[:100]}...")
            
            # Show first 200 chars of text content
            text_preview = result.get('text_content', '')[:200]
            print(f"📃 Text preview: {text_preview}...")
            
        except Exception as e:
            print(f"❌ Error testing {url}: {e}")
        
        print("\n")


async def test_extraction_schema():
    """Test custom extraction schema"""
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return
    
    # Custom schema for e-commerce products
    custom_schema = {
        "product_title": "The main title or name of the product",
        "manufacturer": "Brand or manufacturer name",
        "model_number": "Product model or SKU",
        "current_price": "Current selling price with currency",
        "original_price": "Original or MSRP price if different from current",
        "availability_status": "In stock, out of stock, or availability information",
        "product_category": "Category or type of product",
        "main_features": "Key features or specifications (list)",
        "customer_rating": "Average customer rating if available",
        "review_count": "Number of customer reviews"
    }
    
    url = "https://example.com"  # Replace with actual product URL for testing
    print(f"🧪 Testing custom extraction schema with: {url}")
    
    try:
        from llm_scraper import LLMWebScraper
        scraper = LLMWebScraper(api_key)
        result = await scraper.scrape_page_with_llm(url, extraction_schema=custom_schema)
        
        print("✅ Custom schema extraction completed!")
        print(json.dumps(result.get('llm_extraction', {}), indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Custom schema test failed: {e}")


if __name__ == "__main__":
    print("🚀 Testing LLM-Enhanced Web Scraper")
    print("====================================")
    
    # Run basic tests
    asyncio.run(test_llm_scraper())
    
    # Run custom schema test
    print("\n" + "="*50)
    print("🧪 Testing Custom Extraction Schema")
    print("="*50)
    asyncio.run(test_extraction_schema())
    
    print("\n✅ Testing completed!")