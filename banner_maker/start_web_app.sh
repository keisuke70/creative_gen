#!/bin/bash

# AI Banner Maker Web App Starter
echo "🌐 Starting AI Banner Maker Web App..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f "../.env" ]; then
    echo "📄 Loading environment variables from parent .env file..."
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set"
    echo "Please set it with: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source ../venv/bin/activate

# Start web app
echo "🚀 Starting web application..."
echo "📱 Web interface will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

cd web_app
python3 run.py