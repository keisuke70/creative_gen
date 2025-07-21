#!/usr/bin/env python3
"""
Simple Canva integration test that bypasses web scraping.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables explicitly
load_dotenv('/home/kei/creative_gen/.env')

# Add banner_maker to path
sys.path.append(str(Path(__file__).parent / 'banner_maker'))

def test_basic_oauth():
    """Test OAuth setup and configuration."""
    print("🔐 Testing OAuth Configuration...")
    
    # Check environment variables
    client_id = os.getenv("CANVA_CLIENT_ID")
    client_secret = os.getenv("CANVA_CLIENT_SECRET")
    redirect_uri = os.getenv("CANVA_REDIRECT_URI")
    
    if not client_id or not client_secret:
        print("❌ Missing CANVA_CLIENT_ID or CANVA_CLIENT_SECRET in .env")
        return False
    
    print(f"✅ Client ID: {client_id}")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Test API initialization
    try:
        from src.canva_api import CanvaAPI
        api = CanvaAPI()  # Without token, should not fail
        print("✅ CanvaAPI initialized successfully")
        
        # Test authorization URL generation
        auth_url = api.get_authorization_url(state="test-state")
        print(f"✅ Authorization URL: {auth_url[:80]}...")
        
        return True
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        return False


def test_image_processing():
    """Test image loading and processing."""
    print("\n📷 Testing Image Processing...")
    
    image_path = "/home/kei/creative_gen/box_front.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    try:
        from PIL import Image
        
        # Load and verify image
        with Image.open(image_path) as img:
            print(f"✅ Image loaded: {img.size} pixels, mode: {img.mode}")
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print("✅ Converted to RGB mode")
            
            # Simulate upload preparation
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = buffer.getvalue()
            
            print(f"✅ Image prepared for upload: {len(image_data)} bytes")
            return True
            
    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        return False


def test_template_system():
    """Test template and layout system."""
    print("\n🎨 Testing Template System...")
    
    try:
        from src.templates import AdSize, TEMPLATE_MAP, scale_rect, Rect
        
        # Test enum
        print(f"✅ Available ad sizes: {[size.name for size in AdSize]}")
        
        # Test template mapping
        for ad_size in [AdSize.MD_RECT, AdSize.FB_RECT_1]:
            template = TEMPLATE_MAP[ad_size]
            print(f"✅ {ad_size.name}: {template.canvas_w}x{template.canvas_h}")
            
            # Test frame scaling
            hero_frame = template.frames["hero"]
            scaled = scale_rect(hero_frame, template.canvas_w, template.canvas_h)
            print(f"   Hero frame: {scaled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Template system failed: {e}")
        return False


def test_copy_generation():
    """Test copy and content structures."""
    print("\n✍️  Testing Copy Generation...")
    
    try:
        from src.layout_orchestrator import CopyTriple, Product
        
        # Test copy structure
        copy = CopyTriple(
            headline="Premium Quality Product",
            subline="Experience the difference today",
            cta="Shop Now"
        )
        print(f"✅ Copy created: {copy.headline}")
        
        # Test product structure
        product = Product(
            hero_asset_id="test-asset-123",
            palette=["#FF6B35", "#004225", "#F7931E"]
        )
        print(f"✅ Product created with {len(product.palette)} colors")
        
        return True
        
    except Exception as e:
        print(f"❌ Copy generation failed: {e}")
        return False


def test_background_generation():
    """Test background generation system."""
    print("\n🌈 Testing Background Generation...")
    
    try:
        from src.background_gen import create_gradient_image
        
        # Test gradient creation
        colors = ["#FF6B35", "#004225"]
        gradient_data = create_gradient_image(colors, size=(400, 300))
        
        print(f"✅ Gradient generated: {len(gradient_data)} bytes")
        
        # Save test gradient
        with open("test_gradient.png", "wb") as f:
            f.write(gradient_data)
        print("✅ Test gradient saved as test_gradient.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Background generation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Simple Canva Integration Test")
    print("=" * 50)
    
    tests = [
        ("OAuth Configuration", test_basic_oauth),
        ("Image Processing", test_image_processing),
        ("Template System", test_template_system),
        ("Copy Generation", test_copy_generation),
        ("Background Generation", test_background_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔹 {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for OAuth flow.")
        print("\n🚀 Next Steps:")
        print("1. Start server: export PATH=\"$HOME/.local/bin:$PATH\" && python3 run_test_server.py")
        print("2. Visit: http://localhost:5000/auth/canva/authorize")
        print("3. Complete Canva authorization")
        print("4. Test banner generation via the web interface")
    else:
        print("⚠️  Some tests failed. Fix issues before proceeding.")


if __name__ == "__main__":
    main()