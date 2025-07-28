#!/bin/bash

# AI Banner Maker Web App Starter
echo "🌐 Starting AI Banner Maker Web App..."

# Find creative_gen root directory
find_creative_gen_root() {
    local current_dir="$(pwd)"
    while [ "$current_dir" != "/" ]; do
        if [ -d "$current_dir/banner_maker" ] && [ -d "$current_dir/venv" ]; then
            echo "$current_dir"
            return 0
        fi
        current_dir="$(dirname "$current_dir")"
    done
    return 1
}

# Get creative_gen root directory
CREATIVE_GEN_ROOT=$(find_creative_gen_root)
if [ -z "$CREATIVE_GEN_ROOT" ]; then
    echo "❌ Could not find creative_gen root directory (should contain both banner_maker/ and venv/)"
    echo "Please run this script from within the creative_gen project directory"
    exit 1
fi

echo "📂 Found creative_gen root at: $CREATIVE_GEN_ROOT"
cd "$CREATIVE_GEN_ROOT"

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f "banner_maker/.env" ]; then
    echo "📄 Loading environment variables from banner_maker/.env file..."
    export $(cat banner_maker/.env | grep -v '^#' | xargs)
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found at $CREATIVE_GEN_ROOT/venv"
    echo "Please create one first:"
    echo "python3 -m venv venv && source venv/bin/activate && pip install -r banner_maker/requirements.txt"
    exit 1
fi

# Check environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY environment variable not set"
    echo "Please set it in the .env file or with: export GOOGLE_API_KEY='your-api-key'"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Start web app
echo "🚀 Starting web application..."
echo "📱 Web interface will be available at: http://127.0.0.1:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

cd banner_maker/web_app
python run.py