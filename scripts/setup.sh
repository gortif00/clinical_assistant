#!/bin/bash

# Clinical Mental Health Assistant - Development Setup Script
# Sets up the development environment from scratch

set -e

echo "🧠 Clinical Mental Health Assistant - Development Setup"
echo "======================================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate and install dependencies
echo "📦 Installing dependencies..."
source backend/venv/bin/activate
cd backend
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
cd ..
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found"
    if [ -f ".env.example" ]; then
        echo "📋 Creating .env from template..."
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your HF_TOKEN"
        echo "   Get your token from: https://huggingface.co/settings/tokens"
    else
        echo "❌ No .env.example found"
    fi
else
    echo "✅ .env file exists"
fi
echo ""

# Check for models
echo "📊 Checking for trained models..."
if [ ! -d "backend/models/classifier" ] || [ ! -d "backend/models/t5_summarizer" ] || [ ! -d "backend/models/llama_peft" ]; then
    echo "⚠️  Model directories incomplete"
    echo "   You'll need to train models or download pre-trained ones"
    echo "   See docs/DEPLOYMENT.md for details"
else
    echo "✅ Model directories found"
fi
echo ""

echo "======================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your HF_TOKEN (if not done)"
echo "2. Run: ./scripts/start.sh"
echo "3. Open: http://localhost:8000"
echo ""
echo "For development with auto-reload:"
echo "  cd backend && source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo "======================================================"
