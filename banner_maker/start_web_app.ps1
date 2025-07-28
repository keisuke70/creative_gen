# AI Banner Maker Web App Starter (PowerShell)
Write-Host "🌐 Starting AI Banner Maker Web App..." -ForegroundColor Green

# Find creative_gen root directory
function Find-CreativeGenRoot {
    $currentDir = Get-Location
    while ($currentDir.Path -ne $currentDir.Root.Path) {
        if ((Test-Path (Join-Path $currentDir "banner_maker")) -and (Test-Path (Join-Path $currentDir "venv"))) {
            return $currentDir.Path
        }
        $currentDir = $currentDir.Parent
    }
    return $null
}

# Get creative_gen root directory
$CreativeGenRoot = Find-CreativeGenRoot
if (-not $CreativeGenRoot) {
    Write-Host "❌ Could not find creative_gen root directory (should contain both banner_maker/ and venv/)" -ForegroundColor Red
    Write-Host "Please run this script from within the creative_gen project directory" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Found creative_gen root at: $CreativeGenRoot" -ForegroundColor Green
Set-Location $CreativeGenRoot

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "📄 Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim("'`""), "Process")
        }
    }
} elseif (Test-Path "banner_maker\.env") {
    Write-Host "📄 Loading environment variables from banner_maker\.env file..." -ForegroundColor Yellow
    Get-Content "banner_maker\.env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim("'`""), "Process")
        }
    }
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found at $CreativeGenRoot\venv" -ForegroundColor Red
    Write-Host "Please create one first:" -ForegroundColor Red
    Write-Host "python -m venv venv && venv\Scripts\Activate.ps1 && pip install -r banner_maker\requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check environment variables
if (-not $env:GOOGLE_API_KEY) {
    Write-Host "❌ GOOGLE_API_KEY environment variable not set" -ForegroundColor Red
    Write-Host "Please set it in the .env file" -ForegroundColor Red
    exit 1
}

# Activate virtual environment (Windows)
Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
& "venv\Scripts\Activate.ps1"

# Start web app
Write-Host "🚀 Starting web application..." -ForegroundColor Green
Write-Host "📱 Web interface will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "banner_maker\web_app"
python run.py
