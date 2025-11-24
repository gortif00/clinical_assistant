#!/bin/bash

# Clinical Mental Health Assistant - Startup Script

echo "🧠 Clinical Mental Health Assistant - Startup"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source backend/venv/bin/activate

# Check if requirements are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r backend/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check model directories
echo ""
echo "🔍 Checking model directories..."
MODELS_MISSING=false

if [ ! -d "backend/models/classifier" ]; then
    echo "⚠️  Classification model not found at: backend/models/classifier"
    MODELS_MISSING=true
fi

if [ ! -d "backend/models/t5_summarizer" ]; then
    echo "⚠️  T5 summarizer not found at: backend/models/t5_summarizer"
    MODELS_MISSING=true
fi

if [ ! -d "backend/models/llama_peft" ]; then
    echo "⚠️  Llama PEFT adapter not found at: backend/models/llama_peft"
    MODELS_MISSING=true
fi

if [ "$MODELS_MISSING" = true ]; then
    echo ""
    echo "⚠️  WARNING: Some models are missing!"
    echo "Please copy your trained models to the backend/models/ directory:"
    echo "  - backend/models/classifier/"
    echo "  - backend/models/t5_summarizer/"
    echo "  - backend/models/llama_peft/"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ All model directories found"
fi

# Check Hugging Face token
if [ -z "$HF_TOKEN" ]; then
    echo ""
    echo "⚠️  HF_TOKEN environment variable not set"
    echo "You may need it to download Llama models from Hugging Face"
    echo "Set it with: export HF_TOKEN='your_token_here'"
fi

echo ""
echo "🚀 Starting backend server..."
echo "=============================================="
echo ""

# Start the backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
