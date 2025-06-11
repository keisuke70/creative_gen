# AI Banner Maker Web App

Professional web application for creating AI-powered marketing banners with streamlined AI generation.

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

## 🏗️ Architecture

### **Simplified AI-First Flow**
```
LP URL → Extract Content & Context → Generate 3 Copy Variants → 
Auto-Select or Manual Choice → Single AI Generation (Complete Creative) → Output
```

## 📦 Installation

> **⚠️ IMPORTANT**: The web app requires a Python virtual environment. You **MUST** activate the venv before running the web server or you'll get "module not found" errors.

### **Prerequisites**
- Python 3.8 or higher
- OpenAI API key with GPT Image 1 access

### **Step 1: Virtual Environment Setup**
```bash
# Navigate to banner_maker directory (parent of web_app)
cd banner_maker

# Create virtual environment
python3 -m venv banner_maker_env

# Activate virtual environment (Linux/Mac)
source banner_maker_env/bin/activate

# Or on Windows
# banner_maker_env\Scripts\activate
```

### **Step 2: Install Dependencies**
```bash
# Upgrade pip and install Python packages
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browser (IMPORTANT: do this inside venv)
playwright install chromium
```

### **Step 3: Environment Variables**
```bash
# Create .env file in banner_maker directory
cat > .env << 'EOF'
OPENAI_API_KEY='sk-proj-your-openai-key-here'
EOF
```

## 🔧 Configuration

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

## 🚀 Running the App

### **Development Mode**
```bash
# IMPORTANT: Make sure virtual environment is activated
source banner_maker_env/bin/activate  # Linux/Mac
# or: banner_maker_env\Scripts\activate  # Windows

# Navigate to web app directory
cd web_app

# Start the web server
python run.py
```
Access at: http://localhost:5000

### **Quick Start Script**
```bash
# Use the provided start script (auto-activates venv)
./start_web_app.sh
```

### **Production Mode**
```bash
# IMPORTANT: Make sure virtual environment is activated first
source banner_maker_env/bin/activate  # Linux/Mac

export FLASK_ENV=production
cd web_app
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### **Docker Deployment**
```bash
# Build container
docker build -t banner-maker-web .

# Run container
docker run -p 5000:5000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  banner-maker-web
```

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

## 🛠️ Development

### **File Structure**
```
web_app/
├── app.py              # Flask application
├── run.py              # Development server
├── templates/
│   └── index.html      # Main interface
├── static/
│   ├── css/           # Stylesheets
│   └── js/
│       └── app.js     # Frontend logic
└── uploads/           # Temporary file storage
```

### **Adding New Features**
1. **Backend**: Add routes to `app.py`
2. **Frontend**: Update `templates/index.html` and `static/js/app.js`
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

## 🐛 Troubleshooting

### **Common Issues**

**"Missing environment variables"**
- Ensure `OPENAI_API_KEY` is set

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
- Ensure virtual environment is activated: `source banner_maker_env/bin/activate`
- Verify you're in the correct directory (banner_maker)
- Reinstall dependencies: `pip install -r requirements.txt`

**"Playwright browser not found"**
- Activate venv first, then run: `playwright install chromium`
- Browser must be installed inside the virtual environment

### **Debug Mode**
```bash
export FLASK_DEBUG=1
python run.py
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

## 📄 License

Professional marketing banner generation tool built with GPT Image 1 and GPT-4.1 for streamlined, high-quality banner creation.