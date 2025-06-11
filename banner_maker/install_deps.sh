#!/bin/bash

echo "🚀 Installing Banner Maker Dependencies via apt..."

# Try to install Python packages via apt
echo "📦 Installing Python packages..."

# Install pip first
echo "Installing pip..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

# Add user bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Install basic packages
echo "Installing basic packages..."
python3 -m pip install --user flask werkzeug

# Install AI packages
echo "Installing AI packages..."
python3 -m pip install --user openai

# Install image processing
echo "Installing image processing..."
python3 -m pip install --user Pillow

# Install other packages
echo "Installing other packages..."
python3 -m pip install --user click aiohttp selectolax

echo ""
echo "✅ Basic installation complete!"
echo ""
echo "📋 Manual steps needed:"
echo "2. Install Playwright: python3 -m pip install --user playwright && python3 -m playwright install chromium"
echo ""
echo "🔑 Set your API keys:"
echo "export OPENAI_API_KEY='your-openai-key'"
echo ""
echo "🚀 Then start with: python3 simple_start.py"