# Setup Instructions

After cleaning up redundant files, here's the simplified setup process:

## Quick Setup

1. **Run the main installation script:**
   ```bash
   cd banner_maker
   sudo ./install_all_deps.sh
   ```

2. **Set up your environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Start the application:**
   ```bash
   ./start_web_app.sh
   ```

4. **Open your browser to:**
   ```
   http://127.0.0.1:5000
   ```

## What We Cleaned Up

### Removed Redundant Files:
- ❌ `canva_test_env/` - Broken virtual environment
- ❌ `install_deps.sh` - Basic installer
- ❌ `get-pip.py` - Pip installer  
- ❌ `setup.sh` - Conflicting setup script
- ❌ `test_scraping.py` - Temporary test file
- ❌ `test_copy_generation.py` - Temporary test file

### Current Clean Structure:
- ✅ `venv/` - Working virtual environment (project root)
- ✅ `install_all_deps.sh` - Complete installation script
- ✅ `start_web_app.sh` - Application launcher
- ✅ `requirements.txt` - Dependencies specification
- ✅ `.env` - Environment configuration

## Dependencies Included

The installation script now properly installs:
- All system browser dependencies for Playwright
- Python virtual environment with all packages
- Chromium browser for web scraping
- Proper environment setup

No more manual dependency issues! 🎉
