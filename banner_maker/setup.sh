#!/bin/bash

# AI Banner Maker Setup Script
echo "🚀 Setting up AI Banner Maker..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Make sure you're in the banner_maker directory."
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv banner_maker_env

# Activate virtual environment
echo "✅ Activating virtual environment..."
source banner_maker_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Install Playwright browser
echo "🌐 Installing Playwright browser..."
python3 -m playwright install chromium

# Install system dependencies
echo "🔧 Installing system dependencies..."
echo "Note: This requires sudo password for system package installation"
sudo apt-get update
sudo apt-get install -y \
    libgbm1 \
    libasound2 \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Create .env file with your API key:"
echo "   cat > .env << 'EOF'"
echo "   OPENAI_API_KEY='sk-proj-your-key-here'"
echo "   EOF"
echo ""
echo "2. Start the web app:"
echo "   ./start_web_app.sh"
echo ""
echo "3. Access the web interface at:"
echo "   http://localhost:5000"
echo ""
echo "🎯 Or run CLI version (activate environment first):"
echo "   source banner_maker_env/bin/activate"
echo "   python3 -m src.main https://example.com/landing-page --verbose"
echo ""
echo "📚 For detailed setup help, see README.md"