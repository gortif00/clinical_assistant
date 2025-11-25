#!/bin/bash

################################################################################
# Clinical Mental Health Assistant - Backend Startup Script
#
# This script handles:
#   - Virtual environment setup and activation
#   - Dependency installation
#   - Model directory verification
#   - HuggingFace token validation
#   - FastAPI server launch
#
# Usage:
#   ./start_backend.sh
#
# Requirements:
#   - Python 3.8+
#   - Models in backend/models/ directory
#   - HF_TOKEN environment variable (for Llama downloads)
#
# The backend will start on http://localhost:8000
# API documentation available at http://localhost:8000/docs
################################################################################

echo "🧠 Clinical Mental Health Assistant - Backend Startup"
echo "=============================================="
echo ""

# Check if we're in the right directory (must be run from project root)
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Example: cd /path/to/clinical_assistant && ./start_backend.sh"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# ============================================
# VIRTUAL ENVIRONMENT SETUP
# ============================================
# Check if virtual environment exists, create if missing
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    echo "   This is a one-time setup (may take 1-2 minutes)"
    cd backend
    python3 -m venv venv
    cd ..
    echo "✅ Virtual environment created"
fi

# Activate virtual environment (isolates project dependencies)
echo "🔄 Activating virtual environment..."
source backend/venv/bin/activate

# ============================================
# DEPENDENCY INSTALLATION
# ============================================
# Check if FastAPI is installed as a proxy for all dependencies
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies from requirements.txt..."
    echo "   This includes: transformers, torch, peft, fastapi, etc."
    echo "   First install may take 5-10 minutes depending on your connection"
    pip install -r backend/requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# ============================================
# MODEL DIRECTORY VALIDATION
# ============================================
# Verify that all required model directories exist
# These should contain your trained models from Google Drive/Colab
echo ""
echo "🔍 Checking model directories..."
MODELS_MISSING=false

# 1. Classification Model (5-class mental health classifier)
if [ ! -d "backend/models/classifier" ]; then
    echo "⚠️  Classification model not found at: backend/models/classifier"
    echo "   Required files: config.json, pytorch_model.bin, tokenizer files"
    MODELS_MISSING=true
fi

# 2. T5 Summarizer (clinical text summarization)
if [ ! -d "backend/models/t5_summarizer" ]; then
    echo "⚠️  T5 summarizer not found at: backend/models/t5_summarizer"
    echo "   Required files: config.json, pytorch_model.bin, spiece.model"
    MODELS_MISSING=true
fi

# 3. Llama LoRA Adapter (treatment recommendation generation)
if [ ! -d "backend/models/llama_peft" ]; then
    echo "⚠️  Llama PEFT adapter not found at: backend/models/llama_peft"
    echo "   Required files: adapter_config.json, adapter_model.bin"
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

# ============================================
# HUGGINGFACE AUTHENTICATION
# ============================================
# Check if HuggingFace token is set (required for Llama base model download)
if [ -z "$HF_TOKEN" ]; then
    echo ""
    echo "⚠️  HF_TOKEN environment variable not set"
    echo "   You need this to download Llama 3.2 base model from Hugging Face"
    echo "   Get your token at: https://huggingface.co/settings/tokens"
    echo "   Set it with: export HF_TOKEN='hf_your_token_here'"
    echo "   Or run: huggingface-cli login"
fi

echo ""
echo "🚀 Starting backend server..."
echo "=============================================="
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/api/v1/health"
echo ""
echo "Model loading may take 2-5 minutes on first run..."
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI backend server
# --reload: Auto-reload on code changes (development mode)
# --host 0.0.0.0: Listen on all network interfaces
# --port 8000: Server port
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
