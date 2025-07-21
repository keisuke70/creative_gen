#!/usr/bin/env python3
"""
Test server runner for Canva OAuth flow.
"""

import sys
from pathlib import Path

# Add banner_maker to path
sys.path.append(str(Path(__file__).parent / 'banner_maker'))

# Import and run the Flask app
from web_app.app import app

if __name__ == "__main__":
    print("🚀 Starting Canva Test Server...")
    print("📍 OAuth URLs:")
    print("   - Start OAuth: http://localhost:5000/auth/canva/authorize")
    print("   - Check Status: http://localhost:5000/auth/canva/status")
    print("   - Main App: http://localhost:5000/")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)