# AI Banner Maker - Creative Asset Management Platform

Professional web application for creating marketing assets with AI-powered content analysis, image extraction, copy generation, and Canva integration.

## 🎯 What It Does

**Input**: Landing page URL → **Output**: Organized creative assets ready for use in Canva

**Example**: `https://www.yodobashi.com/product/12345/` → Extracted images, AI-generated marketing copy, creative insights, and blank Canva design with proper dimensions

## 🚀 Key Features

### **🔍 Advanced Web Analysis**
- **Enhanced Scraping** - 2-10x more content extraction with platform-specific selectors
- **Anti-Bot Protection** - Hybrid Playwright + Requests fallback system bypasses detection
- **Platform Optimization** - Special support for Yodobashi, Amazon, Rakuten, Shopify, WordPress
- **Dynamic Content** - Handles JavaScript, infinite scroll, and lazy loading

### **🖼️ Intelligent Image Management**
- **Smart Image Extraction** - Automatically finds and filters high-quality images from web pages
- **Multi-Format Support** - PNG, JPG, JPEG, GIF, WebP up to 16MB
- **Drag & Drop Interface** - Extract images from web pages or upload your own
- **Automatic Cleanup** - Manages temporary files and storage efficiently

### **✍️ AI-Powered Copy Generation**
- **Multiple Variants** - Generates 5 copy styles: Benefit, Urgency, Promo, Neutral, Playful
- **Smart Selection** - Manual selection with live preview and editing
- **Background Prompts** - Each copy includes AI background generation prompts
- **Caching System** - Avoids duplicate processing for efficiency

### **💡 Creative Insights & Explanation**
- **Comprehensive Analysis** - AI-generated marketing insights and creative direction
- **Target Audience** - Detailed audience analysis and motivations  
- **Selling Points** - Key benefits and emotional triggers identification
- **Creative Direction** - Visual style, color, and typography recommendations
- **Messaging Strategy** - Headline approaches and tone guidance
- **CTA Suggestions** - Multiple call-to-action variations

### **🎨 Optional AI Background Generation**
- **Context-Aware** - Generates backgrounds that match your selected copy and brand
- **Text-Free Designs** - Pure abstract backgrounds perfect for overlay text
- **Professional Quality** - Marketing-ready backgrounds with proper mood and style

### **🔗 Seamless Canva Integration**
- **OAuth Authentication** - Secure connection to your Canva account
- **Smart Uploads** - Automatically uploads all assets to your Canva library
- **Proper Organization** - Creates blank designs with correct dimensions and project names
- **Multiple Formats** - Supports all standard banner sizes and social media formats

## 🏗️ Complete Workflow

```
Landing Page URL → 
  ↓
Web Scraping (Enhanced with Anti-Bot) →
  ↓
Image Extraction + Copy Generation + Creative Insights →
  ↓
Optional: AI Background Generation →
  ↓
Asset Upload to Canva + Blank Design Creation
```

### **Step-by-Step Process**

1. **📱 Enter URL**: Input any landing page URL
2. **🔄 Auto-Analysis**: AI scrapes content with platform-specific optimization  
3. **🖼️ Extract Images**: High-quality images automatically extracted and displayed
4. **✍️ Generate Copy**: 5 marketing copy variants with background prompts
5. **💡 Get Insights**: Comprehensive creative strategy and recommendations
6. **🎨 Optional Background**: Generate AI backgrounds that match your copy
7. **📤 Send to Canva**: All assets uploaded, blank design created with proper dimensions
8. **🎯 Create in Canva**: Use provided assets to build your final creative

## 💻 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- OpenAI API key (GPT-4.1 and DALL-E access)
- Canva Developer Account (for OAuth integration)

### **Step 1: Environment Setup**

#### **Linux/Mac/WSL:**
```bash
# Navigate to banner_maker directory
cd banner_maker

# Create and activate virtual environment
python3 -m venv banner_maker_env
source banner_maker_env/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

#### **Windows PowerShell:**
```powershell
# Navigate to banner_maker directory
cd banner_maker

# Create and activate virtual environment
python -m venv banner_maker_env
banner_maker_env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### **Step 2: Environment Configuration**

Create `.env` file in the `banner_maker` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY='sk-proj-your-openai-key-here'

# Canva OAuth Configuration (Optional - for Canva integration)
CANVA_CLIENT_ID='your-canva-client-id'
CANVA_CLIENT_SECRET='your-canva-client-secret'
CANVA_REDIRECT_URI='http://localhost:5000/auth/canva/callback'

# Application Configuration
FLASK_ENV=development
PORT=5000
```

### **Step 3: Start the Application**

#### **Quick Start (Recommended):**
```bash
# Linux/Mac/WSL
./start_web_app.sh

# Windows PowerShell
.\start_web_app.ps1
```

#### **Manual Start:**
```bash
# Activate environment
source banner_maker_env/bin/activate  # Linux/Mac/WSL
# banner_maker_env\Scripts\Activate.ps1  # Windows

# Start web server
cd web_app
python run.py
```

**Access at: http://localhost:5000**

## 🎨 How to Use

### **Web Interface Workflow**

1. **🔗 Connect to Canva** (Optional but recommended)
   - Click "Connect to Canva" in the header
   - Authorize the application via OAuth

2. **📝 Enter Landing Page URL**
   - Input any product page, blog post, or landing page
   - System automatically detects platform (Yodobashi, Amazon, etc.)

3. **🖼️ Extract & Manage Images**
   - Click "Extract Images" to find high-quality images
   - Drag images from extraction area to upload area
   - Or upload your own images via drag & drop

4. **✍️ Generate Marketing Copy**
   - Click "Generate Copy" for 5 AI-generated variants
   - Select your preferred copy style and edit if needed
   - Each copy includes matching background generation prompts

5. **💡 Get Creative Insights** (Optional)
   - Click "Generate Explanation" for comprehensive analysis
   - Receive target audience insights, selling points, creative direction
   - Copy sections to clipboard for reference

6. **🎨 Generate AI Background** (Optional)
   - Click "Generate AI Background" to create matching backgrounds
   - Uses prompts tailored to your selected copy and brand context

7. **📤 Send to Canva**
   - Click "Send to Canva" to upload all assets
   - Creates blank design with proper dimensions
   - All images and backgrounds available in your Canva library

8. **🎯 Create in Canva**
   - Open the created design in Canva
   - Use uploaded assets to build your final creative
   - Apply generated copy and creative insights

## 🔧 Advanced Features

### **Anti-Bot Web Scraping**
- **Hybrid Approach**: Playwright → Requests fallback for maximum success rate
- **Platform Optimization**: Special selectors for major e-commerce sites
- **Stealth Mode**: Advanced techniques to bypass detection systems
- **Error Recovery**: Automatic retry and fallback mechanisms

### **Platform-Specific Support**
- **✅ Yodobashi**: Complete product page analysis
- **✅ Amazon**: Product title and features extraction  
- **✅ Rakuten**: Product details and descriptions
- **✅ Shopify**: General product page support
- **✅ WordPress**: Blog and article content

### **Intelligent Caching**
- **Content Cache**: Avoids duplicate scraping for the same URL
- **Copy Cache**: Stores generated variants for quick access
- **Session Management**: Maintains user state across interactions
- **Automatic Cleanup**: Manages storage and temporary files

### **File Management System**
- **Smart Upload**: Handles multiple formats and sizes
- **Extraction Integration**: Seamlessly processes web images
- **Temporary Handling**: Cleans up after Canva upload
- **Error Recovery**: Robust handling of upload failures

## 📡 API Reference

### **Core Endpoints**

#### **POST /api/generate-copy**
Generate marketing copy variants
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/generate-explanation** 
Generate creative insights and strategy
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/extract-images**
Extract images from webpage
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/generate-background**
Generate AI background (requires Canva auth)
```json
{
  "url": "https://example.com/product",
  "selected_copy": {...},
  "custom_background_prompt": "..."
}
```

#### **POST /api/generate**
Upload assets to Canva (requires auth)
```json
{
  "url": "https://example.com/product",
  "size": "MD_RECT",
  "variant_idx": 0,
  "product_image_paths": ["/path/to/image.jpg"],
  "background_asset_id": "optional-bg-id"
}
```

### **File Upload Endpoints**

#### **POST /api/upload**
Upload product images
```
Content-Type: multipart/form-data
file: image file (up to 16MB)
```

#### **POST /api/proxy-image**
Download and convert web images
```json
{
  "url": "https://example.com/image.jpg",
  "filename": "product-image"
}
```

## 🎯 Use Cases & Examples

### **E-commerce Product Marketing**
```
Input: https://www.yodobashi.com/product/100000001005807664/
↓
Output: 
- Product images extracted and optimized
- 5 marketing copy variants (benefit, urgency, promo, etc.)
- Target audience analysis and selling points
- AI backgrounds matching product category
- Ready-to-use Canva design with all assets
```

### **Blog Content Promotion**
```
Input: https://myblog.com/10-productivity-tips/
↓
Output:
- Article images and graphics extracted  
- Social media copy variants
- Content marketing strategy insights
- Professional backgrounds for quote cards
- Canva templates for multiple social formats
```

### **SaaS Product Campaigns**
```
Input: https://myapp.com/features/
↓
Output:
- Feature screenshots and mockups
- Benefit-focused copy highlighting value props
- B2B audience insights and messaging strategy
- Clean, professional backgrounds
- Banner templates for various ad platforms
```

## 🔒 Security & Privacy

### **Data Protection**
- **Temporary Processing**: Scraped content processed and discarded
- **Secure Upload**: Files validated and sanitized
- **Session Isolation**: User data separated by session
- **OAuth Security**: Secure Canva integration with proper scopes

### **File Security**
- **Type Validation**: Only allowed image formats accepted
- **Size Limits**: 16MB maximum per file
- **Automatic Cleanup**: Temporary files removed after processing
- **Path Sanitization**: Prevents directory traversal attacks

## 📊 Performance & Costs

### **Generation Times**
- Web Scraping: 5-15 seconds (with anti-bot measures)
- Copy Generation: 10-20 seconds (5 variants)
- Creative Insights: 15-25 seconds (comprehensive analysis)
- Background Generation: 20-30 seconds (high-quality AI)
- Canva Upload: 5-15 seconds (depends on file count)

### **API Costs (Estimated)**
- Copy Generation: ~$0.02-0.05 per request (GPT-4.1 mini)
- Creative Insights: ~$0.03-0.07 per request (GPT-4.1 mini)
- Background Generation: ~$0.04-0.08 per image (DALL-E)
- **Total per complete workflow**: ~$0.09-0.20

## 🛠️ Technical Architecture

### **Core Components**
- **Enhanced Scraper**: `src/enhanced_scraper.py` - Advanced web content extraction
- **Copy Generator**: `src/copy_gen.py` - AI-powered marketing copy creation
- **Insight Generator**: `src/explanation_gen.py` - Creative strategy analysis
- **Canva Integration**: `src/canva_oauth.py` + `src/simple_canva_upload.py`
- **Web Interface**: `web_app/` - Flask-based user interface

### **Key Technologies**
- **Backend**: Flask, OpenAI API, Playwright, Requests
- **Frontend**: HTML5, JavaScript ES6, TailwindCSS, FontAwesome
- **Storage**: Local filesystem with automatic cleanup
- **Authentication**: OAuth 2.0 for Canva integration
- **Image Processing**: PIL/Pillow for format conversion

### **Data Flow**
```
URL Input → Scraping (Playwright/Requests) → Content Analysis → 
AI Processing (Copy/Insights/Backgrounds) → Canva Upload → 
User Interface Updates → Asset Management
```

## 🔧 Troubleshooting

### **Common Issues**

**"Scraping Failed"**
- Check if URL is accessible
- Platform may be blocking requests (system will try fallback)
- Verify internet connection

**"Copy Generation Failed"**
- Check OpenAI API key and credits
- Verify API key has GPT-4.1 access
- Check for API rate limits

**"Canva Connection Issues"**
- Verify Canva OAuth credentials
- Check redirect URI configuration  
- Ensure proper scopes are requested

**"File Upload Problems"**
- Check file size (16MB limit)
- Verify file format (PNG, JPG, JPEG, GIF, WebP)
- Ensure sufficient disk space

### **Debug Mode**
```bash
# Enable detailed logging
export FLASK_DEBUG=1
export FLASK_ENV=development
python run.py
```

## 📈 Roadmap & Future Features

### **Planned Enhancements**
- **🔮 More AI Models**: Support for additional image generation models
- **📱 Mobile Optimization**: Responsive design improvements
- **🎨 Style Transfer**: Apply brand styles to generated backgrounds
- **📊 Analytics Dashboard**: Track usage and generation success rates
- **🔄 Batch Processing**: Handle multiple URLs simultaneously
- **🎯 A/B Testing**: Generate multiple creative variations for testing

### **Integration Expansion**
- **Adobe Creative Suite**: Export to Photoshop/Illustrator
- **Figma Integration**: Direct asset export to Figma
- **Social Media APIs**: Direct posting to platforms
- **CRM Integration**: Connect with marketing automation tools

## 🆘 Support & Documentation

### **Getting Help**
1. Check this README for setup and usage instructions
2. Review the troubleshooting section above
3. Check API documentation for endpoint details
4. Verify all dependencies and credentials are properly configured

### **File Structure Reference**
```
banner_maker/
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
├── start_web_app.sh         # Linux/Mac startup script
├── start_web_app.ps1        # Windows startup script
├── src/                     # Core functionality
│   ├── enhanced_scraper.py  # Advanced web scraping
│   ├── copy_gen.py          # AI copy generation
│   ├── explanation_gen.py   # Creative insights
│   ├── canva_oauth.py       # Canva authentication
│   └── simple_canva_upload.py # Asset upload
├── web_app/                 # Web interface
│   ├── app.py               # Flask application
│   ├── run.py               # Development server
│   ├── templates/index.html # Main interface
│   ├── static/js/app.js     # Frontend logic
│   └── uploads/             # Temporary file storage
└── documentation/           # Additional docs
    ├── scraper_improvements_ja.md
    └── ファイルアップロード機能.md
```

---

**Ready to create professional marketing assets?** 🚀

**Setup Time**: 5-10 minutes  
**First Creative**: Ready in 2-3 minutes  
**Perfect For**: E-commerce, SaaS, content marketing, social media campaigns

Start by running `./start_web_app.sh` (Linux/Mac) or `.\start_web_app.ps1` (Windows) and open http://localhost:5000!