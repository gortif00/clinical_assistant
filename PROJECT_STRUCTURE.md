# 📁 Project Structure

Professional, production-ready organization for the Clinical Mental Health Assistant.

```
clinical_assistant/
│
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 ATTRIBUTIONS.md             # Model and dataset credits
├── 📄 CITATIONS.bib               # BibTeX citations for academic use
├── 📄 CONTRIBUTING.md             # Contribution guidelines
├── 📄 Makefile                     # Build automation and task runner
├── 📄 .gitignore                   # Git exclusions
├── 📄 .env.example                 # Environment variables template
│
├── 📁 backend/                     # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Application entry point
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── analyze.py     # Core analysis endpoint
│   │   │       └── health.py      # Health checks
│   │   ├── core/
│   │   │   ├── config.py          # Configuration management
│   │   │   └── logging_config.py  # Logging setup
│   │   ├── middleware/
│   │   │   ├── auth.py            # JWT authentication
│   │   │   ├── metrics.py         # Prometheus metrics
│   │   │   └── rate_limiter.py    # Rate limiting
│   │   ├── ml/
│   │   │   ├── models_loader.py   # Singleton model manager
│   │   │   └── pipeline.py        # ML inference pipeline
│   │   └── utils/
│   │       └── text_cleaning.py   # Text preprocessing
│   │
│   ├── models/                    # Trained models (excluded from git)
│   │   ├── classifier/            # BERT classification model
│   │   │   ├── config.json
│   │   │   ├── model.safetensors
│   │   │   ├── label_map.json
│   │   │   └── training_metadata.json
│   │   ├── t5_summarizer/         # T5 summarization model
│   │   │   ├── config.json
│   │   │   └── model.safetensors
│   │   └── llama_peft/            # Llama LoRA adapter
│   │       ├── adapter_config.json
│   │       └── adapter_model.safetensors
│   │
│   ├── logs/                      # Application logs (auto-generated)
│   ├── requirements.txt           # Production dependencies
│   └── requirements-dev.txt       # Development dependencies
│
├── 📁 frontend/                   # Web interface
│   ├── index.html                 # Main UI
│   ├── images/                    # Assets (favicon, etc.)
│   ├── css/
│   │   └── styles.css             # Styling (dark mode support)
│   └── js/
│       └── app.js                 # Client-side logic (ChatGPT-style UI)
│
├── 📁 tests/                      # Test suite (pytest)
│   ├── conftest.py                # Pytest configuration & fixtures
│   ├── unit/                      # Unit tests
│   │   ├── test_auth.py           # Authentication tests
│   │   └── test_rate_limiter.py   # Rate limiting tests
│   └── integration/               # Integration tests
│       └── test_api_endpoints.py  # API endpoint tests
│
├── 📁 scripts/                    # Utility scripts
│   ├── setup.sh                   # Initial development setup
│   ├── start.sh                   # Quick start server
│   ├── test.sh                    # Run test suite
│   ├── lint.sh                    # Code quality checks
│   ├── docker-build.sh            # Build Docker image
│   └── k8s-deploy.sh              # Kubernetes deployment
│
├── 📁 deployment/                 # Deployment configurations
│   ├── Dockerfile                 # Multi-stage Docker build
│   ├── .dockerignore              # Docker build exclusions
│   ├── docker-compose.yml         # Local Docker deployment
│   └── k8s/                       # Kubernetes manifests
│       ├── deployment.yaml        # Application deployment
│       ├── configmap.yaml         # Configuration
│       ├── secrets.yaml.example   # Secrets template
│       ├── ingress.yaml           # Load balancer
│       ├── redis-deployment.yaml  # Redis for rate limiting
│       ├── prometheus-config.yaml # Monitoring
│       └── grafana-dashboard.json # Dashboards
│
├── 📁 config/                     # Configuration files
│   └── pytest.ini                 # Pytest configuration
│
├── 📁 .github/                    # GitHub-specific files
│   └── workflows/                 # CI/CD pipelines
│       └── (future: ci-cd.yml)    # GitHub Actions workflow
│
└── 📁 docs/                       # Documentation
    ├── CITATIONS.md               # Academic citation guide
    ├── DEPLOYMENT.md              # Production deployment guide
    └── BUG_FIX_P0.md             # Known issues and fixes
```

---

## 📊 Component Overview

| Component | Size | Files | Description |
|-----------|------|-------|-------------|
| **Backend Code** | ~500 KB | ~15 files | FastAPI app with ML pipeline |
| **Frontend** | ~100 KB | 3 files | Modern ChatGPT-style UI |
| **Models** | ~3.0 GB | 3 models | AI models (excluded from git) |
| **Tests** | ~50 KB | 12+ tests | Comprehensive test coverage |
| **Scripts** | ~30 KB | 6 scripts | Automation and deployment |
| **K8s Configs** | ~50 KB | 7 files | Production manifests |
| **Documentation** | ~250 KB | 6 files | Guides and references |

---

## 🎯 Key Organizational Principles

### 1. **Separation of Concerns**
- **backend/**: All Python application code
- **frontend/**: All UI code (HTML/CSS/JS)
- **deployment/**: All deployment configs (Docker, K8s)
- **scripts/**: All automation scripts
- **tests/**: All test code
- **docs/**: All documentation

### 2. **Professional Structure**
- Clear separation between source code and configuration
- Dedicated directories for scripts and deployment
- CI/CD ready with `.github/workflows/`
- Makefile for common tasks

### 3. **Deployment Ready**
- Docker configs in `deployment/`
- Kubernetes manifests organized in `deployment/k8s/`
- Environment-based configuration with `.env`
- Multiple deployment options (local, Docker, K8s)

### 4. **Developer Friendly**
- Simple `make` commands for all tasks
- Automated setup with `./scripts/setup.sh`
- Comprehensive scripts for testing, linting, deploying
- Clear documentation structure

---

## 🚀 Quick Start Commands

```bash
# Initial setup
make setup          # or ./scripts/setup.sh

# Development
make run            # Start development server
make test           # Run tests with coverage
make lint           # Check code quality

# Docker deployment
make docker-build   # Build image
make docker-run     # Run with docker-compose

# Kubernetes deployment
make k8s-deploy     # Deploy to cluster
make k8s-status     # Check status
```

---

## 🚫 Excluded from Repository

These are listed in `.gitignore`:

- ✋ **Model files** (`*.safetensors`, `*.bin`) - Too large for Git (3GB+)
- ✋ **Virtual environments** (`venv/`, `env/`) - Platform-specific
- ✋ **Cache files** (`__pycache__/`, `*.pyc`) - Generated at runtime
- ✋ **Logs** (`logs/`, `*.log`) - Runtime output
- ✋ **Environment secrets** (`.env`) - Sensitive data
- ✋ **IDE configs** (`.vscode/`, `.idea/`) - Personal preferences
- ✋ **System files** (`.DS_Store`) - OS-specific

---

## 📥 How to Get Models

Models are not in the repository. Download them with:

```bash
# Option 1: Hugging Face Hub (recommended)
huggingface-cli download mental/mental-bert-base-uncased --local-dir backend/models/classifier
huggingface-cli download t5-base --local-dir backend/models/t5_summarizer
huggingface-cli download meta-llama/Llama-3.2-1B-Instruct --local-dir backend/models/llama_peft

# Option 2: Docker automatically handles it
docker-compose up  # Models load on first request
```

---

## ✅ Key Design Decisions

1. **Unified Backend/Frontend** - Single FastAPI app serves both (simplicity)
2. **Docker-First** - Containerized for reproducible deployment
3. **Singleton Pattern** - Models loaded once, cached in memory
4. **Modular Structure** - Clear separation: API, ML, middleware, utils
5. **Production-Ready** - Auth, rate limiting, logging, metrics included

---

## 📚 Documentation Organization

- **Root**: User-facing docs (README, LICENSE, ATTRIBUTIONS)
- **docs/**: Technical deep-dives and deployment guides
- **Inline**: Code comments and docstrings

---

**Last Updated**: December 2025
