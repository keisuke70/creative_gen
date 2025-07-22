#!/usr/bin/env pwsh
# Windows PowerShell script for installing ALL Banner Maker Dependencies

Write-Host "🚀 Installing ALL Banner Maker Dependencies (Windows)..." -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  Some dependencies may require Administrator access." -ForegroundColor Yellow
    Write-Host "   Consider running PowerShell as Administrator for full installation." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue with user-level installation only? (y/N)"
    if ($continue -notmatch '^[Yy]$') {
        Write-Host "Exiting. Please run as Administrator for full installation." -ForegroundColor Red
        exit 1
    }
}

# Check if Python is installed
Write-Host ""
Write-Host "🐍 Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if pip is available
try {
    $pipVersion = python -m pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip." -ForegroundColor Red
    exit 1
}

# Navigate to parent directory to create venv at project root
Write-Host ""
Write-Host "📁 Navigating to project root..." -ForegroundColor Green
Set-Location ".."

# Create virtual environment if it doesn't exist
Write-Host ""
Write-Host "🔧 Setting up Python virtual environment..." -ForegroundColor Green

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "   Try running: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  pip upgrade failed, continuing anyway..." -ForegroundColor Yellow
}

# Install from requirements.txt
Write-Host ""
Write-Host "📦 Installing Python packages from requirements.txt..." -ForegroundColor Green
python -m pip install -r "banner_maker\requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python packages" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python packages installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host ""
Write-Host "🌐 Installing Playwright browsers..." -ForegroundColor Green
python -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Playwright browsers" -ForegroundColor Red
    exit 1
}

# Install Playwright system dependencies
Write-Host ""
Write-Host "📦 Installing Playwright system dependencies..." -ForegroundColor Green
try {
    python -m playwright install-deps chromium
    Write-Host "✅ Playwright system dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some Playwright dependencies may need manual installation" -ForegroundColor Yellow
    Write-Host "   This is normal on Windows - browsers should still work" -ForegroundColor Yellow
}

# Check if Visual C++ Redistributable is needed
Write-Host ""
Write-Host "🔍 Checking system requirements..." -ForegroundColor Green
Write-Host "   If you encounter DLL errors, install Visual C++ Redistributable:" -ForegroundColor Yellow
Write-Host "   https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow

Write-Host ""
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Set up your .env file with API keys:" -ForegroundColor White
Write-Host "   Copy banner_maker\.env.example to banner_maker\.env" -ForegroundColor Yellow
Write-Host "   Edit .env with your actual API keys" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Start the application:" -ForegroundColor White
Write-Host "   cd banner_maker" -ForegroundColor Yellow
Write-Host "   .\start_web_app.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Open: http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Your AI Banner Maker is ready!" -ForegroundColor Green
Write-Host ""

# Deactivate virtual environment
Write-Host "Deactivating virtual environment..." -ForegroundColor Yellow
deactivate

Write-Host "✨ Setup complete! Enjoy your AI Banner Maker! ✨" -ForegroundColor Magenta