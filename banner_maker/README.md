# AI Banner Maker Web App

Professional web application for creating AI-powered marketing banners with streamlined AI generation.

## 🎯 What It Does

Input: Landing page URL → Output: Professional marketing banner with optimized copy and visuals

**Example**: `https://shopify-store.com/product/widget` → Beautiful banner with smart text positioning, perfect dimensions, and marketing copy

## 🚀 Features

### **Streamlined AI Generation**
- **Unified Creative Generation** - Complete banners with text, fonts, and layout in one step
- **Perfect Text Positioning** - Dimension-aware prompts prevent text overflow on all banner sizes

### **Core Capabilities**
- **Smart Landing Page Analysis** - Extracts content and context automatically
- **Optional Product Upload** - Manual image upload for enhanced results
- **Multiple Banner Sizes** - Square (1024×1024), Landscape (1536×1024), Portrait (1024×1536)
- **Smart Copy Selection** - Generates 3 copy styles (benefit, urgency, promotional) with auto-selection or manual choice
- **Real-time Progress** - Live generation status with detailed progress tracking
- **Instant Downloads** - PNG, HTML, and CSS files ready for use
- **Web App Interface**: Easy-to-use browser interface with real-time progress
- **Multiple Export Formats**: PNG banners + responsive HTML/CSS

## 🎨 Banner Generation Features

| Feature | Capability |
|---------|-----------|
| **Speed** | Fast (15-30s) |
| **Text Positioning** | ✅ Perfect dimension-aware positioning |
| **Background Quality** | ✅ AI Generated with product integration |
| **Text Integration** | ✅ Native text rendering |
| **Multiple Sizes** | ✅ Square, Landscape, Portrait |
| **Product Support** | ✅ Optional product image upload |
| **Best For** | All marketing banners and ads |

## 🎯 Use Cases

### **E-commerce**
- Product-focused banners with perfect text positioning
- Promotional campaigns with urgency-driven copy
- Social media ads with consistent branding

### **SaaS/Digital Products**
- Benefit-focused banners highlighting features
- Professional layouts with dimension-aware typography
- Landing page hero sections

### **Content Marketing**
- Blog post promotional banners
- Event announcements
- Newsletter headers

## 📊 Performance & Costs

### **Generation Times**
- Banner Generation: 15-30 seconds
- File Processing: 5-10 seconds
- Total Time: 20-40 seconds

### **API Costs (per banner)**
- GPT Image 1: ~$0.05-0.10 (varies by size)
- GPT-4.1 Copy: ~$0.01-0.03
- Total: ~$0.06-0.13 per banner

## 🔒 Security Features

- **File Upload Validation** - Type and size restrictions
- **Session Management** - Temporary file cleanup
- **API Rate Limiting** - Prevents abuse
- **Input Sanitization** - XSS protection
- **Environment Variables** - Secure credential storage

## 🏗️ Architecture

### **Simplified AI-First Flow**
```
LP URL → Extract Content & Context → Generate 3 Copy Variants → 
Auto-Select or Manual Choice → Single AI Generation (Complete Creative) → Output
```

**Streamlined AI-First Pipeline**:
1. **Web Scraping** → Playwright extracts content and context from landing page
2. **Copy Generation** → GPT-4.1 creates 3 marketing copy variants with auto-selection or manual choice
3. **Unified AI Generation** → GPT Image 1 creates complete banner with text, layout, and styling in one call
4. **Dimension Optimization** → Smart prompts ensure perfect text positioning for each banner size
5. **Export** → Generates PNG + responsive HTML/CSS

## � Installation

> **⚠️ IMPORTANT**: The web app requires a Python virtual environment. You **MUST** activate the venv before running the web server or you'll get "module not found" errors.

### **Prerequisites**
- Python 3.8 or higher
- OpenAI API key with GPT Image 1 access

### **Step 1: Virtual Environment Setup**

#### **Linux/Mac/WSL:**
```bash
# Navigate to banner_maker directory (parent of web_app)
cd banner_maker

# Create virtual environment
python3 -m venv banner_maker_env

# Activate virtual environment
source banner_maker_env/bin/activate
```

#### **Windows PowerShell:**
```powershell
# Navigate to banner_maker directory (parent of web_app)
cd banner_maker

# Create virtual environment
python -m venv banner_maker_env

# Activate virtual environment
banner_maker_env\Scripts\Activate.ps1
```

#### **Windows Command Prompt:**
```cmd
# Navigate to banner_maker directory (parent of web_app)
cd banner_maker

# Create virtual environment
python -m venv banner_maker_env

# Activate virtual environment
banner_maker_env\Scripts\activate.bat
```

### **Step 2: Install Dependencies**

#### **Linux/Mac/WSL:**
```bash
# Upgrade pip and install Python packages
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser (IMPORTANT: do this inside venv)
playwright install chromium
```

#### **Windows:**
```powershell
# Upgrade pip and install Python packages
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser (IMPORTANT: do this inside venv)
playwright install chromium
```

### **Step 3: Environment Variables**

> **⚠️ IMPORTANT**: The `.env` file must be created in the `banner_maker` directory (the same directory where `start_web_app.sh` and `requirements.txt` are located), NOT in the `web_app` subdirectory.

**File Location**: `/path/to/banner_maker/.env` (same level as `start_web_app.sh`)

#### **Linux/Mac/WSL:**
```bash
# Make sure you're in the banner_maker directory
cd banner_maker

# Verify you're in the correct location (should show start_web_app.sh, requirements.txt, etc.)
ls -la

# Create .env file in the current directory (banner_maker)
cat > .env << 'EOF'
OPENAI_API_KEY='sk-proj-your-openai-key-here'
EOF

# Verify the file was created
ls -la .env
```

#### **Windows PowerShell:**
```powershell
# Make sure you're in the banner_maker directory
cd banner_maker

# Verify you're in the correct location (should show start_web_app.ps1, requirements.txt, etc.)
Get-ChildItem

# Create .env file in the current directory (banner_maker)
@"
OPENAI_API_KEY='sk-proj-your-openai-key-here'
"@ | Out-File -FilePath ".env" -Encoding UTF8

# Verify the file was created
Get-ChildItem .env
```

#### **Windows Command Prompt:**
```cmd
# Make sure you're in the banner_maker directory
cd banner_maker

# Verify you're in the correct location (should show start_web_app.ps1, requirements.txt, etc.)
dir

# Create .env file in the current directory (banner_maker)
echo OPENAI_API_KEY='sk-proj-your-openai-key-here' > .env

# Verify the file was created
dir .env
```

**Expected file structure after creating .env:**
```
banner_maker/
├── .env                ← Your environment file should be here
├── start_web_app.sh    ← Same level as these files
├── start_web_app.ps1
├── requirements.txt
├── web_app/
│   ├── app.py
│   └── run.py
└── src/
    └── main.py
```

##  Configuration

### **Required Environment Variables**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### **Optional Environment Variables**
```bash
FLASK_ENV=development  # or production
PORT=5000              # server port
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
```

## 🚀 Running the Web App

### **Development Mode**

#### **Linux/Mac/WSL:**
```bash
# IMPORTANT: Make sure virtual environment is activated
source banner_maker_env/bin/activate

# Navigate to web app directory
cd web_app

# Start the web server
python run.py
```

#### **Windows PowerShell:**
```powershell
# IMPORTANT: Make sure virtual environment is activated
banner_maker_env\Scripts\Activate.ps1

# Navigate to web app directory
cd web_app

# Start the web server
python run.py
```

#### **Windows Command Prompt:**
```cmd
# IMPORTANT: Make sure virtual environment is activated
banner_maker_env\Scripts\activate.bat

# Navigate to web app directory
cd web_app

# Start the web server
python run.py
```

**Access at: http://localhost:5000**

### **Quick Start Scripts (Recommended)**

#### **Linux/Mac/WSL:**
```bash
# Use the provided bash script (auto-activates venv)
./start_web_app.sh
```

#### **Windows PowerShell:**
```powershell
# Use the provided PowerShell script (auto-activates venv)
.\start_web_app.ps1
```

### **Production Mode**

#### **Linux/Mac/WSL:**
```bash
# IMPORTANT: Make sure virtual environment is activated first
source banner_maker_env/bin/activate

export FLASK_ENV=production
cd web_app
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### **Windows PowerShell:**
```powershell
# IMPORTANT: Make sure virtual environment is activated first
banner_maker_env\Scripts\Activate.ps1

$env:FLASK_ENV="production"
cd web_app
python run.py
```

## 💻 How to Use the Web App

### Web Interface (Recommended)

1. Open http://localhost:5000
2. Enter landing page URL
3. Optional: Upload product image for enhanced results
4. Choose banner size (Square/Landscape/Portrait) and copy style
5. Click "Generate AI Banner"
6. Download results (PNG + HTML/CSS)

## 📡 API Endpoints

### **POST /api/generate**
Start banner generation
```json
{
  "url": "https://example.com/landing-page",
  "banner_size": "1024x1024|1536x1024|1024x1536",
  "copy_selection_mode": "auto|manual",
  "selected_copy_index": 0,
  "product_image_path": "/path/to/uploaded/image.jpg"
}
```

### **POST /api/upload**
Upload product image
```
Content-Type: multipart/form-data
file: image file (PNG, JPG, JPEG, GIF, WebP)
```

### **GET /api/status/{session_id}**
Check generation progress
```json
{
  "status": "running|completed|error",
  "progress": 75,
  "message": "Enhancing background with AI..."
}
```

### **GET /api/download/{session_id}/{file_type}**
Download generated files
- `file_type`: `banner|html|css`

## 🏗️ System Architecture

### How It Works

**Streamlined AI-First Pipeline**:

1. **Web Scraping** → Playwright extracts content and context from landing page
2. **Copy Generation** → GPT-4.1 creates 3 marketing copy variants with auto-selection or manual choice
3. **Unified AI Generation** → GPT Image 1 creates complete banner with text, layout, and styling in one call
4. **Dimension Optimization** → Smart prompts ensure perfect text positioning for each banner size
5. **Export** → Generates PNG + responsive HTML/CSS

### Technology Stack

- **Playwright**: Headless browser for web scraping
- **OpenAI GPT-4.1**: Marketing copy generation with intelligent variant selection
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

### **Common Issues**

**"Missing environment variables"**
- Ensure `OPENAI_API_KEY` is set in `.env` file
- **Check .env file location**: Must be in `banner_maker/` directory (same level as `start_web_app.sh`), NOT in `web_app/` subdirectory
- Verify API key starts with `sk-proj-`
- Restart web app after creating `.env`

**"Generation failed"**
- Check API credentials and quotas
- Verify landing page is accessible
- Ensure uploaded images are valid

**"File upload failed"**
- Check file size (<16MB) and format (PNG, JPG, JPEG, GIF, WebP)
- Verify upload directory permissions

**"Slow generation"**
- API response times vary (15-60s is normal)
- Check network connectivity
- Monitor API usage limits

**"Module not found" errors**
- **Linux/Mac/WSL**: Ensure virtual environment is activated: `source banner_maker_env/bin/activate`
- **Windows PowerShell**: Ensure virtual environment is activated: `banner_maker_env\Scripts\Activate.ps1`
- **Windows CMD**: Ensure virtual environment is activated: `banner_maker_env\Scripts\activate.bat`
- Verify you're in the correct directory (banner_maker)
- Reinstall dependencies: `pip install -r requirements.txt`

**"Playwright browser not found"**
- Activate venv first, then run: `playwright install chromium`
- Browser must be installed inside the virtual environment

**"PowerShell execution policy" (Windows)**
- Run PowerShell as Administrator and execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use: `powershell -ExecutionPolicy Bypass -File start_web_app.ps1`

**"Port 5000 already in use"**
```bash
# Find and stop the process
sudo lsof -i :5000
sudo kill <process-id>

# Or change port in web_app/run.py
```

### **Debug Mode**

#### **Linux/Mac/WSL:**
```bash
export FLASK_DEBUG=1
python run.py
```

#### **Windows PowerShell:**
```powershell
$env:FLASK_DEBUG=1
python run.py
```

#### **Windows Command Prompt:**
```cmd
set FLASK_DEBUG=1
python run.py
```

### **Virtual Environment Commands**

```bash
# Activate virtual environment (required for all usage)
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

The system generates 3 copy variants with flexible selection options:

- **Benefit**: Trust-focused, professional styling (prioritized for auto-selection)
- **Urgency**: Action-driven, bold colors (prioritized for auto-selection)
- **Promo**: Sale-focused, celebratory effects (prioritized for auto-selection)

**Selection Modes**:

- **Auto-Selection**: System automatically chooses the best variant based on length and impact
- **Manual Selection**: User reviews all 3 variants and chooses their preferred copy

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
- **Operating System**: Windows 10/11, macOS, or Linux (WSL2 recommended for Windows)
- **Python**: 3.8 or higher
- **OpenAI API key** with GPT Image 1 access
- **Administrator access** (Windows) or sudo access (Linux) for initial setup

**After Setup**:
- **Windows**: Run `.\start_web_app.ps1` to start
- **Linux/Mac/WSL**: Run `./start_web_app.sh` to start
- **Access web interface**: http://localhost:5000
- **Virtual environment**: Must be activated for all usage

## 💡 Quick Start Examples

#### **Windows PowerShell:**
```powershell
# Navigate to project
cd C:\path\to\banner_maker

# Start web app (auto-activates venv)
.\start_web_app.ps1
# → Open http://localhost:5000
```

#### **Linux/Mac/WSL:**
```bash
# Navigate to project
cd /path/to/banner_maker

# Start web app (auto-activates venv)
./start_web_app.sh
# → Open http://localhost:5000
```

---

**Setup Time**: ~5-10 minutes with automatic script  
**First Banner**: Ready in 2-3 minutes  
**Perfect for**: E-commerce, SaaS, content sites, social media ads

## 🛠️ Development

### **File Structure**
```
banner_maker/
├── src/                # Core banner generation logic
│   ├── main.py         # CLI interface
│   ├── lp_scrape.py    # Landing page scraping
│   ├── copy_gen.py     # Copy generation
│   ├── gpt_image.py    # AI image generation
│   └── compose.py      # Banner composition
├── web_app/            # Web application
│   ├── app.py          # Flask application
│   ├── run.py          # Development server
│   ├── templates/
│   │   └── index.html  # Main interface
│   ├── static/
│   │   ├── css/       # Stylesheets
│   │   └── js/
│   │       └── app.js # Frontend logic
│   └── uploads/       # Temporary file storage
├── start_web_app.sh    # Linux/Mac start script
├── start_web_app.ps1   # Windows start script
└── requirements.txt    # Python dependencies
```

### **Adding New Features**
1. **Backend**: Add routes to `web_app/app.py`
2. **Frontend**: Update `web_app/templates/index.html` and `web_app/static/js/app.js`
3. **API**: Extend generation functions in `src/` modules

### **Testing**
```bash
# Test banner generation
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "banner_size": "1024x1024"}'

# Check status
curl http://localhost:5000/api/status/{session_id}
```

## 📈 Scaling

### **Production Deployment**
- Use gunicorn with multiple workers
- Implement Redis for session storage
- Add nginx for static file serving
- Use cloud storage for uploads

### **Performance Optimization**
- Cache landing page scraping results
- Implement background job processing
- Add CDN for generated banners
- Use database for session management
