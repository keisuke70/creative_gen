# AI Banner Maker Web App Starter (PowerShell)
Write-Host "🌐 Starting AI Banner Maker Web App..." -ForegroundColor Green

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "📄 Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim("'`""), "Process")
        }
    }
} elseif (Test-Path "../.env") {
    Write-Host "📄 Loading environment variables from parent .env file..." -ForegroundColor Yellow
    Get-Content "../.env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim("'`""), "Process")
        }
    }
}

# Check if virtual environment exists
if (-not (Test-Path "banner_maker_env")) {
    Write-Host "❌ Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

# Check environment variables
if (-not $env:OPENAI_API_KEY) {
    Write-Host "❌ OPENAI_API_KEY environment variable not set" -ForegroundColor Red
    Write-Host "Please set it in the .env file" -ForegroundColor Red
    exit 1
}

# Activate virtual environment (Windows)
Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
& "banner_maker_env\Scripts\Activate.ps1"

# Start web app
Write-Host "🚀 Starting web application..." -ForegroundColor Green
Write-Host "📱 Web interface will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "web_app"
python run.py
