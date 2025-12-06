#!/bin/bash

# Clinical Mental Health Assistant - Quick Start Script
# This script starts the unified application (frontend + backend in one)

set -e

echo "🧠 Clinical Mental Health Assistant - Quick Start"
echo "=================================================="
echo ""

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  Warning: HF_TOKEN environment variable not set"
    echo "   Llama model may fail to load without it."
    echo ""
    echo "   To set it:"
    echo "   export HF_TOKEN='your_huggingface_token'"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies (this may take a few minutes)..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if models exist
if [ ! -d "models/classifier" ] || [ ! -d "models/t5_summarizer" ] || [ ! -d "models/llama_peft" ]; then
    echo "⚠️  Warning: Model directories not found in backend/models/"
    echo "   Expected:"
    echo "   - backend/models/classifier/"
    echo "   - backend/models/t5_summarizer/"
    echo "   - backend/models/llama_peft/"
    echo ""
    echo "   Models will need to be trained or downloaded before first use."
    echo "   See docs/SYSTEM_VERIFICATION_REPORT.md for details."
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the application
echo "🚀 Starting Clinical Mental Health Assistant..."
echo ""
echo "   Application will be available at:"
echo "   🌐 http://localhost:8000"
echo ""
echo "   API Documentation:"
echo "   📚 http://localhost:8000/docs"
echo ""
echo "   Note: First request will take 30-60s to load models"
echo "   Subsequent requests will be much faster (5-10s)"
echo ""
echo "   Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Run uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
