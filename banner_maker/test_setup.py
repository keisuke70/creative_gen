#!/usr/bin/env python3
"""
Test script to verify Banner Maker setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright imported successfully")
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test if required environment variables are set"""
    print("\n🔑 Testing environment variables...")
    
    required_vars = ['OPENAI_API_KEY']
    all_set = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            all_set = False
    
    return all_set

def test_banner_maker_modules():
    """Test if banner maker modules can be imported"""
    print("\n📦 Testing Banner Maker modules...")
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    modules = [
        'lp_scrape',
        'gpt_image', 
        'copy_gen',
        'compose',
        'vision_crop',
        'export_html'
    ]
    
    all_imported = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            all_imported = False
    
    return all_imported

def main():
    print("🚀 Banner Maker Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Environment Test", test_environment),
        ("Banner Maker Modules", test_banner_maker_modules)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Banner Maker is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Start web app: ./start_web_app.sh")
        print("  2. Or use CLI: python3 -m banner_maker.main https://example.com")
    else:
        print("❌ Some tests failed. Please check the setup.")
        print("\n🔧 Troubleshooting:")
        print("  1. Run: ./setup.sh")
        print("  2. Set environment variables:")
        print("     export OPENAI_API_KEY='your-key'")
        print("     export GOOGLE_APPLICATION_CREDENTIALS='/path/to/creds.json'")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())