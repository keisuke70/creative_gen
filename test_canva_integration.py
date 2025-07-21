#!/usr/bin/env python3
"""
Test script for Canva banner generation functionality.

This script tests the complete pipeline:
1. OAuth authentication status check
2. Image upload to Canva
3. Banner generation with random copy
4. Export and download
"""

import os
import sys
import json
import time
from pathlib import Path

# Add banner_maker to path
sys.path.append(str(Path(__file__).parent / 'banner_maker'))

from src.canva_api import CanvaAPI, CanvaAPIError, CanvaOAuthError
from src.canva_oauth import get_stored_token, get_authenticated_api
from src.layout_orchestrator import build_banner, Product, CopyTriple, AdSize
from src.background_gen import maybe_generate_background


def test_oauth_status():
    """Test OAuth authentication status."""
    print("🔐 Testing OAuth Status...")
    
    # Check for stored token
    token = get_stored_token("default")
    if token:
        print(f"✅ Found stored access token: {token[:20]}...")
        return True
    
    # Check environment token
    env_token = os.getenv("CANVA_ACCESS_TOKEN")
    if env_token:
        print(f"✅ Found environment access token: {env_token[:20]}...")
        return True
    
    print("❌ No access token found. OAuth flow required.")
    return False


def test_api_connection(api):
    """Test basic API connectivity."""
    print("🌐 Testing API Connection...")
    
    try:
        # Try to make a simple request to test authentication
        # Note: We'll use design creation as a test since there's no simple "ping" endpoint
        print("   Creating test design to verify authentication...")
        design_id = api.create_design(100, 100)
        print(f"✅ API connection successful! Test design: {design_id}")
        return True
    except CanvaAPIError as e:
        print(f"❌ API connection failed: {e}")
        return False


def test_image_upload(api, image_path):
    """Test uploading the box_front.png image."""
    print(f"📤 Testing Image Upload: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        print(f"   Image size: {len(image_data)} bytes")
        
        asset_id = api.upload_binary(
            image_data,
            "box_front.png",
            "image/png"
        )
        
        print(f"✅ Image uploaded successfully! Asset ID: {asset_id}")
        return asset_id
        
    except Exception as e:
        print(f"❌ Image upload failed: {e}")
        return None


def test_banner_generation(api, hero_asset_id):
    """Test complete banner generation pipeline."""
    print("🎨 Testing Banner Generation...")
    
    # Create test copy
    copy = CopyTriple(
        headline="Premium Quality Product",
        subline="Experience the difference",
        cta="Shop Now"
    )
    
    # Create product
    product = Product(
        hero_asset_id=hero_asset_id,
        palette=["#FF6B35", "#004225", "#F7931E"]
    )
    
    # Test different banner sizes
    test_sizes = [AdSize.MD_RECT, AdSize.FB_RECT_1]
    
    results = []
    
    for ad_size in test_sizes:
        print(f"   Testing {ad_size.value} ({ad_size.name})...")
        
        try:
            # Generate background
            bg_asset_id = maybe_generate_background(product)
            if bg_asset_id:
                print(f"     Generated background: {bg_asset_id}")
            
            # Build banner
            result = build_banner(product, ad_size, copy, bg_asset_id)
            
            print(f"     ✅ Banner created!")
            print(f"     Design ID: {result.design_id}")
            print(f"     Export URL: {result.export_url}")
            
            results.append({
                'size': ad_size.name,
                'design_id': result.design_id,
                'export_url': result.export_url,
                'html_snippet': result.html_snippet[:100] + "..." if len(result.html_snippet) > 100 else result.html_snippet
            })
            
        except Exception as e:
            print(f"     ❌ Failed: {e}")
            results.append({
                'size': ad_size.name,
                'error': str(e)
            })
    
    return results


def main():
    """Run complete test suite."""
    print("🚀 Starting Canva Integration Test")
    print("=" * 50)
    
    # Step 1: Check OAuth status
    if not test_oauth_status():
        print("\n🔗 OAuth Flow Required:")
        print("1. Start the Flask app: python banner_maker/web_app/app.py")
        print("2. Visit: http://localhost:5000/auth/canva/authorize")
        print("3. Complete Canva authorization")
        print("4. Check status: http://localhost:5000/auth/canva/status")
        print("5. Run this test again")
        return
    
    # Step 2: Get authenticated API
    print("\n🔧 Initializing API...")
    api = get_authenticated_api("default")
    if not api:
        # Fallback to environment token
        env_token = os.getenv("CANVA_ACCESS_TOKEN")
        if env_token:
            api = CanvaAPI(access_token=env_token)
        else:
            print("❌ Could not get authenticated API instance")
            return
    
    # Step 3: Test API connection
    if not test_api_connection(api):
        return
    
    # Step 4: Test image upload
    image_path = "/home/kei/creative_gen/box_front.png"
    hero_asset_id = test_image_upload(api, image_path)
    if not hero_asset_id:
        return
    
    # Step 5: Test banner generation
    print("\n" + "=" * 50)
    results = test_banner_generation(api, hero_asset_id)
    
    # Step 6: Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['size']}: {result['error']}")
        else:
            print(f"✅ {result['size']}: {result['design_id']}")
            print(f"   Export: {result['export_url']}")
    
    print("\n🎉 Test completed!")
    
    # Save results to file
    with open("canva_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("📄 Results saved to: canva_test_results.json")


if __name__ == "__main__":
    main()