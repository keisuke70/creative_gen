#!/usr/bin/env python3
"""
Banner Maker Web App Runner
Development and production server launcher
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Check environment variables
    required_env_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the app.")
        sys.exit(1)
    
    # Development vs Production
    if os.getenv('FLASK_ENV') == 'production':
        print("🚀 Starting Banner Maker in production mode...")
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
    else:
        print("🔧 Starting Banner Maker in development mode...")
        print("📱 Web interface: http://127.0.0.1:5000")
        print("🛠️  API endpoint: http://127.0.0.1:5000/api")
        app.run(host='127.0.0.1', port=5000, debug=True)