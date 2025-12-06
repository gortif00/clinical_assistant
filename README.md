# 🧠 Clinical Mental Health Assistant

> **AI-Powered Diagnostic Support Tool for Mental Health Professionals**

An intelligent system that provides automated mental health condition classification and evidence-based treatment recommendations based on clinical case descriptions.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red.svg)](https://pytorch.org/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
  - [Docker Deployment](#-docker-deployment-recommended)
  - [Local Development](#-local-development)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)
- [Disclaimer](#️-important-disclaimer)

---

## 🎯 Overview

The Clinical Mental Health Assistant is a **unified full-stack application** that leverages three state-of-the-art NLP models:

| Component | Model | Purpose | Performance |
|-----------|-------|---------|-------------|
| **Classification** | BERT (110M params) | Diagnose mental health conditions | 204K training samples |
| **Summarization** | T5-base (220M params) | Extract clinical summaries | ROUGE-2: 14.72% |
| **Generation** | Llama 3.2-1B + LoRA | Generate treatment recommendations | Perplexity: 6.15 |

### ✨ Key Features

- ✅ **Unified Deployment**: Single command launch - no separate frontend/backend
- ⚡ **High Performance**: 60-80% faster inference with optimized model loading
- 🔒 **Privacy-First**: All processing runs locally, no external API calls
- 🎯 **Professional UI**: Clean, medical-grade interface
- 📊 **Real-time Status**: Device monitoring (CUDA/MPS/CPU)
- 🐳 **Docker Ready**: Production-ready containerized deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application (Port 8000)                 │
├─────────────────────────────────────────────────────────────┤
│  Frontend (/)              │  Backend API (/api/v1)          │
│  - HTML/CSS/JS             │  - /analyze (POST)              │
│  - Served by FastAPI       │  - /health (GET)                │
│                            │  - /get_status (GET)            │
├─────────────────────────────────────────────────────────────┤
│              Model Manager (Singleton Pattern)               │
│  • Lazy Loading            │  • Device Auto-detection        │
│  • Model Caching           │  • Unified Pipeline             │
└─────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Unified Stack**: Frontend and backend served from single FastAPI instance
- **Singleton Pattern**: Models loaded once and reused across requests
- **Lazy Loading**: Models load only when needed, with caching
- **Zero Config**: Automatic device detection (CUDA/MPS/CPU)

---

## 🚀 Quick Start

### 🐳 Docker Deployment (Recommended)

**Perfect for production or if you want zero setup hassle.**

```bash
# 1. Clone the repository
git clone https://github.com/gortif00/clinical_assistant.git
cd clinical_assistant

# 2. Create .env file with your HuggingFace token (required for Llama)
echo "HF_TOKEN=your_huggingface_token_here" > .env

# 3. Launch the application
docker-compose up --build

# 4. Access the application
# Open your browser at: http://localhost:8000
```

**That's it!** The application will:
- ✅ Install all dependencies automatically
- ✅ Load models on first request (takes ~30-60s)
- ✅ Serve both frontend and API from port 8000
- ✅ Cache models for fast subsequent requests

**Stopping the application:**
```bash
docker-compose down
```

---

### 💻 Local Development

**For development or if you prefer running without Docker.**

#### Prerequisites

- Python 3.11+
- pip and virtualenv
- HuggingFace account and token
- 8GB+ RAM (16GB recommended)
- GPU optional but recommended

#### Step-by-Step Setup

```bash
# 1. Clone and navigate
git clone https://github.com/gortif00/clinical_assistant.git
cd clinical_assistant

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Set HuggingFace token
export HF_TOKEN="your_huggingface_token_here"

# 5. Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Access the application
# Open your browser at: http://localhost:8000
```

**Development Tips:**
- Use `--reload` flag for auto-restart on code changes
- Check logs for model loading progress
- First request takes 30-60s (loads all models)
- Subsequent requests are 5-10s (uses cached models)

---

## 📁 Project Structure

```
clinical_assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── analyze.py          # API endpoints
│   │   ├── core/
│   │   │   └── config.py           # Configuration
│   │   ├── ml/
│   │   │   ├── models_loader.py    # Model Manager (optimized)
│   │   │   └── pipeline.py         # Legacy pipeline (deprecated)
│   │   ├── utils/
│   │   │   └── text_cleaning.py    # Text preprocessing
│   │   ├── main.py                 # FastAPI app entry point
│   │   └── __init__.py
│   ├── models/                     # Trained models (not in repo)
│   │   ├── classifier/
│   │   ├── t5_summarizer/
│   │   └── llama_peft/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/                       # Frontend files (served by FastAPI)
│   ├── index.html
│   ├── css/styles.css
│   └── js/app.js
├── docs/                           # Documentation
│   ├── REPORT_SUMMARY.md
│   ├── SYSTEM_VERIFICATION_REPORT.md
│   └── SPEED_OPTIMIZATIONS.md
├── docker-compose.yml              # Docker orchestration
├── Dockerfile                      # Docker image definition
├── start.sh                        # Quick start script
├── .env                            # Environment variables (create this)
├── .gitignore
└── README.md                       # This file
```

**Key Files:**
- `backend/app/main.py`: FastAPI app that serves both frontend and API
- `backend/app/ml/models_loader.py`: Optimized model manager with singleton pattern
- `frontend/`: Static frontend files (HTML/CSS/JS)
- `docker-compose.yml`: Single-command deployment configuration

---

## 📚 API Documentation

Once the application is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Main Endpoints

#### `POST /api/v1/analyze`

Analyze a clinical case and generate recommendations.

**Request Body:**
```json
{
  "text": "Patient clinical observations...",
  "auto_classify": true,
  "pathology": null
}
```

**Response:**
```json
{
  "classification": {
    "pathology": "Major Depressive Disorder",
    "confidence": 0.87,
    "all_probabilities": {...}
  },
  "summary": "Clinical summary...",
  "recommendation": "Treatment recommendation...",
  "metadata": {
    "processing_time": 7.32
  }
}
```

#### `GET /api/v1/get_status`

Get execution device status (CUDA/MPS/CPU).

**Response:**
```json
{
  "status": "ok",
  "device": "mps"
}
```

#### `GET /api/v1/health`

Check if models are loaded and ready.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: HuggingFace token for Llama model access
HF_TOKEN=your_token_here

# Optional: Advanced settings (defaults work fine)
# CLASSIFICATION_MODEL_PATH=backend/models/classifier
# T5_SUMMARIZATION_PATH=backend/models/t5_summarizer
# LLAMA_MODEL_CHECKPOINT=meta-llama/Llama-3.2-1B-Instruct
```

### Getting a HuggingFace Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Accept Llama model license at https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
4. Add token to `.env` file

---

## 🔧 Troubleshooting

### Common Issues

#### "Models not loaded" error
**Cause**: Models directory is empty or models failed to load.

**Solution**:
```bash
# Check if models exist
ls -lh backend/models/

# If missing, you need to train models first
# See docs/SYSTEM_VERIFICATION_REPORT.md for training instructions
```

#### First request is very slow (30-60s)
**Cause**: This is normal! Models are loading for the first time.

**Expected behavior**:
- First request: 30-60s (loads BERT + T5 + Llama)
- Second request: 5-10s (uses cached models)

#### "Frontend not showing device" or CORS errors
**Cause**: Backend might not be running or accessible.

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check logs for errors
docker-compose logs -f  # For Docker
# or check terminal output for local deployment
```

#### Docker build fails with "disk space" error
**Cause**: Docker models are large (~2GB).

**Solution**:
```bash
# Clean old images
docker system prune -a

# Use volume mounting (already configured in docker-compose.yml)
# Models will be loaded from ./backend/models instead of copied into image
```

### Performance Issues

If inference is slow even after first request:

1. **Check device**: Visit http://localhost:8000 - should show GPU if available
2. **Check logs**: Look for "⚡ Already loaded, skip" messages (should appear on 2nd+ requests)
3. **Verify RAM**: Ensure you have 8GB+ free RAM
4. **GPU drivers**: For CUDA, ensure nvidia-docker is installed

---

## 📖 Documentation

Additional documentation is available in the `docs/` directory:

- **[REPORT_SUMMARY.md](docs/REPORT_SUMMARY.md)**: Project overview and model details
- **[SYSTEM_VERIFICATION_REPORT.md](docs/SYSTEM_VERIFICATION_REPORT.md)**: Technical deep dive
- **[SPEED_OPTIMIZATIONS.md](docs/SPEED_OPTIMIZATIONS.md)**: Performance improvements explained

---

## ⚠️ Important Disclaimer

**This system is a clinical decision support tool designed for licensed mental health professionals.**

- ✅ **Intended Use**: Augment professional clinical judgment
- ❌ **Not a Replacement**: Does not replace comprehensive clinical assessment
- 🔒 **Professional Only**: For use by qualified healthcare providers
- 📋 **Final Diagnosis**: Must incorporate patient history and professional expertise

**This tool should never be used as the sole basis for diagnosis or treatment decisions.**

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Models**: BERT, T5, and Llama from HuggingFace Transformers
- **Framework**: FastAPI for unified backend/frontend serving
- **Optimization**: Inspired by efficient model management patterns

---

## 📧 Contact

For questions or issues:
- Open an issue on [GitHub](https://github.com/gortif00/clinical_assistant/issues)
- Check existing documentation in `docs/`

---

**Made with ❤️ for Mental Health Professionals**
