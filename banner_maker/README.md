# AI Banner Maker

Generate stunning marketing banners from landing page URLs using a streamlined AI-powered approach. Simply provide a URL and get professional banners with perfect text positioning and optimized copy.

## 🎯 What It Does

Input: Landing page URL → Output: Professional marketing banner with optimized copy and visuals

**Example**: `https://shopify-store.com/product/widget` → Beautiful banner with smart text positioning, perfect dimensions, and marketing copy

## ✨ Features

- **Unified AI Generation**: Single AI call creates complete banners with text, layout, and styling
- **Smart Web Scraping**: Extracts content and context from any landing page
- **Intelligent Text Positioning**: Dimension-aware prompts prevent text overflow on all banner sizes
- **Smart Copy Generation**: GPT-4.1 creates 5 copy variants optimized for different marketing goals
- **Multiple Banner Sizes**: Square (1024×1024), Landscape (1536×1024), Portrait (1024×1536)
- **Product Image Support**: Upload your own product images for enhanced results
- **Web App Interface**: Easy-to-use browser interface with real-time progress
- **Multiple Export Formats**: PNG banners + responsive HTML/CSS

## 🚀 Quick Start

### 1. System Requirements

- **Operating System**: Ubuntu/Debian Linux (WSL2 supported)
- **Python**: 3.8 or higher
- **Node.js**: Not required (Playwright handles browser downloads)

### 2. Get API Keys

**OpenAI API Key** (Required):
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new key → Copy the `sk-proj-...` key

### 3. Installation

#### Option A: Automatic Setup (Recommended)
```bash
git clone <repository-url>
cd banner_maker

# Make setup script executable
chmod +x setup.sh

# Run automatic setup (will ask for sudo password)
./setup.sh
```

#### Option B: Manual Setup
```bash
# 1. Create Python virtual environment
python3 -m venv banner_maker_env
source banner_maker_env/bin/activate

# 2. Upgrade pip and install Python packages
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Install Playwright browser (INSIDE virtual environment)
playwright install chromium

# 4. Install system dependencies (OUTSIDE virtual environment, requires sudo)
sudo apt-get update
sudo apt-get install -y libvips-dev libgbm1 libasound2 \
    libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 \
    libxcomposite1 libxdamage1 libxrandr2 libxss1
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# In the banner_maker directory, create .env file
cat > .env << 'EOF'
OPENAI_API_KEY='sk-proj-your-openai-key-here'
EOF
```

### 5. Start the Web App

```bash
# Quick start (loads .env automatically)
./start_web_app.sh
```

Access at: **http://localhost:5000**

## 💻 Usage

### Web Interface (Recommended)

1. Open http://localhost:5000
2. Enter landing page URL
3. Optional: Upload product image for enhanced results
4. Choose banner size (Square/Landscape/Portrait) and copy style
5. Click "Generate AI Banner"
6. Download results (PNG + HTML/CSS)

### Command Line Interface

```bash
# Activate virtual environment first
source banner_maker_env/bin/activate

# Basic usage
python3 -m src.main https://example.com/landing-page

# Advanced options
python3 -m src.main https://example.com/lp \
  --banner-size 1200x628 \
  --output-dir ./output \
  --verbose
```

## 🏗️ System Architecture

### How It Works

**Streamlined AI-First Pipeline**:
1. **Web Scraping** → Playwright extracts content and context from landing page
2. **Copy Generation** → GPT-4.1 creates marketing copy variants optimized for banners
3. **Unified AI Generation** → GPT Image 1 creates complete banner with text, layout, and styling in one call
4. **Dimension Optimization** → Smart prompts ensure perfect text positioning for each banner size
5. **Export** → Generates PNG + responsive HTML/CSS

### Technology Stack
- **Playwright**: Headless browser for web scraping
- **OpenAI GPT-4.1**: Marketing copy generation and optimization
- **OpenAI GPT Image 1**: Advanced image generation with text integration
- **Flask**: Web application framework
- **PIL/Pillow**: Image processing and optimization

## 📦 Dependencies Breakdown

### Virtual Environment (Python packages)
- `playwright==1.45.0` - Web scraping
- `openai>=1.80.0` - AI image generation and copy writing
- `flask==3.0.0` - Web interface
- `Pillow==10.2.0` - Image handling
- `click==8.1.7` - CLI interface
- `aiohttp==3.9.3` - Async HTTP support
- `selectolax==0.3.21` - Fast HTML parsing
- `werkzeug==3.0.1` - WSGI utilities
- `gunicorn==21.2.0` - Production web server

### System Dependencies (Installed with sudo)
- `libgbm1`, `libasound2` - Playwright browser support
- `libnss3`, `libnspr4`, `libatk-bridge2.0-0` - Chrome/Chromium dependencies
- `libdrm2`, `libxcomposite1`, `libxdamage1`, `libxrandr2`, `libxss1` - Display libraries

### Browsers (Playwright managed)
- Chromium browser (downloaded automatically by Playwright)

## 🔧 Troubleshooting

### Common Issues

**"OPENAI_API_KEY not set"**
- Check `.env` file exists in banner_maker directory
- Verify API key starts with `sk-proj-`
- Restart web app after creating `.env`


**Playwright browser errors**
```bash
# Install system dependencies
sudo apt-get install -y libgbm1 libasound2

# Reinstall Playwright browsers
source banner_maker_env/bin/activate
playwright install chromium
```


**Port 5000 already in use**
```bash
# Find and stop the process
sudo lsof -i :5000
sudo kill <process-id>

# Or change port in web_app/run.py
```

### Virtual Environment Commands

```bash
# Activate virtual environment (required for CLI usage)
source banner_maker_env/bin/activate

# Deactivate virtual environment
deactivate

# Check installed packages
pip list

# Update a specific package
pip install --upgrade openai
```

## 💰 API Costs (2024 Pricing)

- **GPT Image 1**: ~$0.05-0.10 per banner (varies by size and quality)
- **GPT-4.1**: ~$0.01-0.03 per copy generation

**Typical cost per banner**: $0.06-0.13

## 📁 Output Files

Each banner generation creates:
- `banner.png` - Final marketing banner with perfect text positioning
- `banner.html` - Responsive HTML template
- `banner.css` - Professional styling

## 🎨 Copy Types & Visual Styles

The system generates 5 copy variants:
- **Benefit**: Trust-focused, professional styling
- **Urgency**: Action-driven, bold colors
- **Promo**: Sale-focused, celebratory effects
- **Neutral**: Clean, minimalist approach
- **Playful**: Fun, colorful, engaging

## 🚨 Important Notes

1. **Virtual environment must be activated** for CLI usage
2. **System dependencies require sudo** - only needed once
3. **Playwright downloads browsers automatically** - internet required for first run
4. **API keys are sensitive** - never commit `.env` to version control
5. **Text positioning is dimension-aware** - prompts automatically adjust for each banner size

## 🆘 Getting Help

1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure API keys are valid and have sufficient credits
4. Check system logs for detailed error messages

## 📋 Requirements Summary

**Before Starting**:
- Ubuntu/Debian Linux (WSL2 works)
- Python 3.8+
- OpenAI API key with GPT Image 1 access
- Sudo access for system package installation

**After Setup**:
- Run `./start_web_app.sh` to start
- Access web interface at http://localhost:5000
- For CLI: activate virtual environment first

## Example Usage

```bash
# Web app (easiest)
./start_web_app.sh
# → Open http://localhost:5000

# CLI (requires virtual environment)
source banner_maker_env/bin/activate
python3 -m src.main https://shopify-store.com/product/widget --verbose
```

---

**Setup Time**: ~5-10 minutes with automatic script  
**First Banner**: Ready in 2-3 minutes  
**Perfect for**: E-commerce, SaaS, content sites, social media ads