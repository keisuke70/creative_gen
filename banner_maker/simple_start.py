#!/usr/bin/env python3
"""
Simple Banner Maker Web App - Minimal Dependencies Version
"""

import os
import sys
import json
import uuid
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Simple HTTP handler
class BannerMakerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path.startswith('/static/'):
            self.serve_static()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/generate':
            self.handle_generate()
        else:
            self.send_error(404)
    
    def serve_html(self):
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Banner Maker - Simple Version</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .form-group { 
            margin: 20px 0; 
        }
        label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: bold;
        }
        input, select, button { 
            width: 100%; 
            padding: 12px; 
            border: none; 
            border-radius: 8px; 
            font-size: 16px;
        }
        button { 
            background: #4CAF50; 
            color: white; 
            cursor: pointer; 
            margin-top: 20px;
        }
        button:hover { 
            background: #45a049; 
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            display: none;
        }
        .error {
            background: rgba(255,0,0,0.3);
        }
        .success {
            background: rgba(0,255,0,0.3);
        }
        h1 { 
            text-align: center; 
            margin-bottom: 30px;
        }
        .note {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI Banner Maker</h1>
        
        <div class="note">
            <strong>📋 Setup Required:</strong><br>
            This is a simplified version. For full functionality, please install Flask and other dependencies:<br>
            <code>pip install flask openai playwright</code>
        </div>
        
        <form id="bannerForm">
            <div class="form-group">
                <label for="url">🔗 Landing Page URL:</label>
                <input type="url" id="url" name="url" required 
                       placeholder="https://example.com/your-landing-page">
            </div>
            
            <div class="form-group">
                <label for="mode">🎨 Generation Mode:</label>
                <select id="mode" name="mode">
                    <option value="unified">Unified AI Mode (Fast)</option>
                    <option value="enhanced">Enhanced Mode (Detailed)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="size">📏 Banner Size:</label>
                <select id="size" name="size">
                    <option value="1200x628">Social Media (1200×628)</option>
                    <option value="1920x1080">Desktop Banner (1920×1080)</option>
                    <option value="728x90">Leaderboard (728×90)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="copyType">✍️ Copy Style:</label>
                <select id="copyType" name="copyType">
                    <option value="auto">Auto-Select Best</option>
                    <option value="benefit">Benefit-Focused</option>
                    <option value="urgency">Urgency-Driven</option>
                    <option value="promo">Promotional</option>
                    <option value="neutral">Professional</option>
                    <option value="playful">Playful</option>
                </select>
            </div>
            
            <button type="submit">🎯 Generate Banner</button>
        </form>
        
        <div id="status" class="status">
            <div id="statusMessage">Ready to generate your banner!</div>
        </div>
        
        <div class="note">
            <strong>🔑 Required Environment Variables:</strong><br>
            • OPENAI_API_KEY: Your OpenAI API key<br>
            • GOOGLE_APPLICATION_CREDENTIALS: Path to Google Cloud credentials JSON
        </div>
    </div>
    
    <script>
        document.getElementById('bannerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const status = document.getElementById('status');
            const message = document.getElementById('statusMessage');
            
            status.style.display = 'block';
            status.className = 'status';
            message.textContent = 'This is a demo interface. Please install full dependencies for functionality.';
            
            // Show environment check
            const hasOpenAI = prompt('Enter your OpenAI API key (or cancel to skip):');
            const hasGoogle = prompt('Enter path to Google credentials (or cancel to skip):');
            
            if (hasOpenAI && hasGoogle) {
                message.textContent = 'API keys provided! Install full dependencies to proceed with generation.';
                status.className = 'status success';
            } else {
                message.textContent = 'API keys required. Please set environment variables and install dependencies.';
                status.className = 'status error';
            }
        });
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def handle_generate(self):
        response = {
            'error': 'Full dependencies not installed. Please run: pip install flask openai playwright'
        }
        
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def main():
    print("🚀 Starting Simple Banner Maker Web Interface...")
    print("📋 Note: This is a minimal version for testing.")
    print("   For full functionality, install: pip install flask openai playwright")
    print("")
    
    # Check environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not set")
    else:
        print("✅ OPENAI_API_KEY found")
    
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
    else:
        print("✅ GOOGLE_APPLICATION_CREDENTIALS found")
    
    print("")
    
    # Start server
    server = HTTPServer(('localhost', 5000), BannerMakerHandler)
    print("🌐 Simple web interface available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    
    # Open browser
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == '__main__':
    main()