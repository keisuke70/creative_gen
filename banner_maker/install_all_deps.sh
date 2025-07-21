#!/bin/bash

echo "🚀 Installing ALL Banner Maker Dependencies..."
echo "=============================================="

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Some dependencies require sudo access."
    echo "   Please run: sudo ./install_all_deps.sh"
    echo ""
    echo "   Or run individual commands manually:"
    echo "   1. sudo apt-get install browser dependencies"
    echo "   2. Install Python packages"
    echo "   3. Install Playwright browsers"
    echo ""
    read -p "Continue with user-level installation only? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please run with sudo for full installation."
        exit 1
    fi
fi

# System packages (requires sudo)
if [ "$EUID" -eq 0 ]; then
    echo "📦 Installing system dependencies..."
    apt-get update
    apt-get install -y \
        curl \
        python3 \
        python3-pip \
        python3-venv \
        libnspr4 \
        libnss3 \
        libasound2t64 \
        libxrandr2 \
        libxcomposite1 \
        libxdamage1 \
        libxss1 \
        libxtst6 \
        libxext6 \
        libxfixes3 \
        libgtk-3-0 \
        libgconf-2-4 \
        libatk-bridge2.0-0 \
        libdrm2 \
        libxkbcommon0 \
        libatspi2.0-0
    echo "✅ System dependencies installed"
else
    echo "⚠️  Skipping system dependencies (requires sudo)"
fi

# Python packages (use virtual environment)
echo ""
echo "🐍 Setting up Python virtual environment and packages..."

# Navigate to parent directory to create venv at project root
cd ..

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install from requirements.txt
echo "Installing from requirements.txt..."
python3 -m pip install -r banner_maker/requirements.txt

echo "✅ Python packages installed in virtual environment"

# Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

# Install Playwright system dependencies if we have sudo
if [ "$EUID" -eq 0 ]; then
    echo "📦 Installing Playwright system dependencies..."
    python3 -m playwright install chromium --with-deps
    echo "✅ Playwright system dependencies installed"
else
    echo "⚠️  Run 'sudo python3 -m playwright install-deps' for browser dependencies"
fi

# Deactivate virtual environment
deactivate

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Next Steps:"
echo "1. Set up your .env file with API keys:"
echo "   cp .env.example .env"
echo "   # Edit .env with your actual API keys"
echo ""
echo "2. Start the application:"
echo "   cd banner_maker && ./start_web_app.sh"
echo ""
echo "3. Open: http://127.0.0.1:5000"
echo ""
echo "🚀 Your AI Banner Maker is ready!"

# Make the script executable
chmod +x "$0"