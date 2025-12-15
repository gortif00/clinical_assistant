# 📁 Project Structure

Clean, production-ready organization for the Clinical Mental Health Assistant.

```
clinical_assistant/
│
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 ATTRIBUTIONS.md             # Model and dataset credits
├── 📄 CITATIONS.bib               # BibTeX citations for academic use
├── 📄 CONTRIBUTING.md             # Contribution guidelines
│
├── 🐳 docker-compose.yml          # Docker orchestration (recommended deployment)
├── 🐳 Dockerfile                  # Container definition
├── 📄 .dockerignore               # Docker build exclusions
├── 📄 .gitignore                  # Git exclusions
├── 📄 .env.example                # Environment variables template
├── 📄 start.sh                    # Quick start script
│
├── 📁 backend/                    # FastAPI application
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
│   ├── models/                    # Trained models (not in git - see .gitignore)
│   │   ├── classifier/
│   │   │   ├── config.json
│   │   │   ├── label_map.json
│   │   │   └── training_metadata.json
│   │   ├── t5_summarizer/
│   │   │   └── config.json
│   │   └── llama_peft/
│   │       └── adapter_config.json
│   │
│   ├── requirements.txt           # Production dependencies
│   └── requirements-dev.txt       # Development dependencies
│
├── 📁 frontend/                   # Web interface
│   ├── index.html                 # Main UI
│   ├── css/
│   │   └── styles.css             # Styling (dark mode support)
│   └── js/
│       └── app.js                 # Client-side logic
│
├── 📁 tests/                      # Test suite
│   ├── conftest.py                # Pytest configuration
│   ├── unit/
│   │   ├── test_auth.py
│   │   └── test_rate_limiter.py
│   └── integration/
│       └── test_api_endpoints.py
│
├── 📁 k8s/                        # Kubernetes deployment
│   ├── deployment.yaml            # K8s deployment spec
│   ├── configmap.yaml             # Configuration
│   ├── secrets.yaml.example       # Secrets template
│   ├── ingress.yaml               # Load balancer
│   ├── redis-deployment.yaml      # Redis for rate limiting
│   ├── prometheus-config.yaml     # Monitoring
│   └── grafana-dashboard.json     # Dashboards
│
└── 📁 docs/                       # Documentation
    ├── CITATIONS.md               # Academic citation guide
    └── DEPLOYMENT.md              # Production deployment guide
```

---

## 📊 File Size Overview

| Component | Size | Description |
|-----------|------|-------------|
| **Backend Code** | ~500 KB | Python application |
| **Frontend** | ~100 KB | HTML/CSS/JS |
| **Models** | ~3.0 GB | AI models (excluded from git) |
| **Documentation** | ~200 KB | Markdown files |
| **Tests** | ~50 KB | Test suite |
| **K8s Configs** | ~50 KB | Deployment manifests |

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
