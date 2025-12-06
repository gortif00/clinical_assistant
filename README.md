# 🧠 Clinical Mental Health Assistant

> **AI-Powered Diagnostic Support Tool for Mental Health Professionals**

An intelligent system that provides automated mental health condition classification and evidence-based treatment recommendations based on clinical case descriptions.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1-red.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-25%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-70%25-green.svg)](tests/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen.svg)](docs/DEPLOYMENT.md)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
  - [Docker Deployment](#-docker-deployment-recommended)
  - [Local Development](#-local-development)
- [Production Features](#-production-features)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
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

## 🚀 Production Features

This application is **production-ready** with enterprise-grade features:

### Security & Authentication
- ✅ **Rate Limiting**: Configurable limits per tier (anonymous/authenticated/premium)
- ✅ **JWT Authentication**: Token-based auth with access/refresh tokens
- ✅ **Password Hashing**: Secure bcrypt password storage
- ✅ **CORS Configuration**: Configurable cross-origin policies

### Monitoring & Observability
- ✅ **Prometheus Metrics**: Exposed on `/metrics` endpoint
  - HTTP request counts, duration, errors
  - Model inference time and memory usage
  - System metrics (CPU, memory, disk, GPU)
- ✅ **Structured Logging**: JSON logs with request tracking
- ✅ **Health Checks**: Multiple probe types for Kubernetes
  - `/api/v1/health` - Basic health
  - `/api/v1/health/detailed` - Full system status
  - `/api/v1/health/ready` - Readiness probe
  - `/api/v1/health/live` - Liveness probe

### Testing & Quality
- ✅ **25 Automated Tests**: Unit + Integration tests
- ✅ **70%+ Coverage**: Comprehensive test coverage
- ✅ **pytest Configuration**: Ready to run with `pytest`

### CI/CD & Deployment
- ✅ **GitHub Actions Pipeline**: 4-stage automated deployment
  - Test (linting, type checking, pytest)
  - Security (Trivy, Safety, Bandit)
  - Build (Docker multi-platform)
  - Deploy (Kubernetes rolling update)
- ✅ **Kubernetes Manifests**: Production-ready K8s configs
  - Deployment with HPA (auto-scaling 3-10 pods)
  - Ingress with TLS (cert-manager)
  - Redis for distributed rate limiting
  - Prometheus + Grafana monitoring

### Documentation
- 📚 **Comprehensive Guides**: 1200+ lines of documentation
  - [Deployment Guide](docs/DEPLOYMENT.md) - Complete deployment instructions
  - [Production README](docs/README_PRODUCTION.md) - Professional overview
  - [Implementation Summary](docs/PRODUCTION_IMPLEMENTATION.md) - Technical details
  - [Integration Complete](docs/INTEGRATION_COMPLETE.md) - Status & next steps

**Quick Links:**
- Run tests: `pytest`
- View metrics: http://localhost:8000/metrics
- Check health: http://localhost:8000/api/v1/health/detailed
- API docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
clinical_assistant/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── analyze.py          # Analysis endpoints
│   │   │   └── health.py           # Health checks ✨
│   │   ├── core/
│   │   │   ├── config.py           # Configuration
│   │   │   └── logging_config.py   # Structured logging ✨
│   │   ├── middleware/             # Production middleware ✨
│   │   │   ├── rate_limiter.py
│   │   │   ├── auth.py
│   │   │   └── metrics.py
│   │   ├── ml/
│   │   │   ├── models_loader.py    # Model Manager (optimized)
│   │   │   └── pipeline.py
│   │   ├── utils/
│   │   │   └── text_cleaning.py
│   │   ├── main.py                 # FastAPI app (production-ready)
│   │   └── __init__.py
│   ├── models/                     # Trained models
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── index.html
│   ├── images/favicon.svg          # Custom favicon ✨
│   ├── css/styles.css
│   └── js/app.js
├── tests/                          # Automated tests ✨
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── k8s/                            # Kubernetes manifests ✨
│   ├── deployment.yaml
│   ├── ingress.yaml
│   └── ...
├── .github/workflows/              # CI/CD pipeline ✨
│   └── ci-cd.yml
├── docs/                           # Documentation ✨
│   ├── DEPLOYMENT.md
│   ├── README_PRODUCTION.md
│   └── ...
├── docker-compose.yml
├── Dockerfile
├── pytest.ini                      # Test config ✨
├── test_endpoints.sh               # Test script ✨
├── run_server.py
├── .env.example                    # Environment template ✨
└── README.md

✨ = New production features
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

## 🧪 Testing

Run the automated test suite:

```bash
# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only

# Test specific endpoint
./test_endpoints.sh
```

**Test Coverage:**
- Rate limiting (6 tests)
- JWT authentication (7 tests)
- API endpoints (12 tests)
- **Total: 25 tests**

---

## 📦 Deployment

### Local Production

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your values

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Run server
python run_server.py
```

### Docker

```bash
docker-compose up --build
```

### Kubernetes

```bash
# See complete guide in docs/DEPLOYMENT.md

# Quick start:
kubectl create namespace production
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/
```

**Production Checklist:**
- [ ] Change JWT secrets (`.env`)
- [ ] Configure CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Setup Redis for rate limiting
- [ ] Configure monitoring
- [ ] Setup CI/CD secrets in GitHub

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

---

## 📊 Monitoring

### Health Checks

```bash
# Basic health
curl http://localhost:8000/api/v1/health

# Detailed system status
curl http://localhost:8000/api/v1/health/detailed

# Kubernetes probes
curl http://localhost:8000/api/v1/health/ready
curl http://localhost:8000/api/v1/health/live
```

### Metrics

Prometheus metrics exposed on `/metrics`:

```bash
# View metrics
curl http://localhost:8000/metrics

# Key metrics:
# - http_requests_total
# - http_request_duration_seconds
# - model_inference_duration_seconds
# - errors_total
```

### Grafana Dashboard

Import `k8s/grafana-dashboard.json` for:
- Request rate & latency (p95, p99)
- Error rates
- Model performance
- System resources (CPU, memory, GPU)
- Pod health

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
