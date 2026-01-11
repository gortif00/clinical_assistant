# Scripts Directory

Automation scripts for development, testing, and deployment.

## Available Scripts

### 🚀 setup.sh
**Initial development environment setup**

Creates virtual environment, installs dependencies, validates configuration.

```bash
./scripts/setup.sh
# OR
make setup
```

**What it does:**
- Checks Python version (3.11+ required)
- Creates virtual environment in `backend/venv`
- Installs production and development dependencies
- Creates `.env` from template if missing
- Validates model directories

---

### ▶️ start.sh
**Start the development server**

Activates virtual environment and starts the FastAPI server.

```bash
./scripts/start.sh
# OR
make run
```

**What it does:**
- Loads environment variables from `.env`
- Validates HF_TOKEN is set
- Checks for model directories
- Starts uvicorn server on port 8000
- Displays helpful startup information

---

### 🧪 test.sh
**Run the complete test suite**

Executes all tests with coverage reporting.

```bash
./scripts/test.sh
# OR
make test
```

**What it does:**
- Runs pytest with coverage
- Generates HTML, XML, and terminal coverage reports
- Outputs coverage statistics
- Creates `htmlcov/` directory with detailed reports

**Output:**
- `htmlcov/index.html` - Interactive coverage report
- `coverage.xml` - XML coverage for CI/CD
- Terminal output with pass/fail status

---

### 🔍 lint.sh
**Code quality and style checks**

Runs Black, Flake8, and MyPy for code quality assurance.

```bash
./scripts/lint.sh
# OR
make lint
```

**What it does:**
1. **Black**: Checks code formatting (PEP 8 compliant)
2. **Flake8**: Lints code for errors and style issues
3. **MyPy**: Type checking for better code safety

**Exit codes:**
- 0: All checks passed
- 1: Issues found (fix with suggestions)

---

### 🐳 docker-build.sh
**Build Docker image**

Builds production-ready Docker image with optional registry push.

```bash
./scripts/docker-build.sh
# OR
make docker-build
```

**Environment variables:**
- `IMAGE_NAME`: Image name (default: clinical-assistant)
- `IMAGE_TAG`: Image tag (default: latest)
- `REGISTRY`: Docker registry URL (optional)
- `PUSH`: Push to registry (default: false)

**Examples:**
```bash
# Build locally
./scripts/docker-build.sh

# Build and tag for registry
REGISTRY=ghcr.io/username IMAGE_TAG=v1.0.0 ./scripts/docker-build.sh

# Build and push
REGISTRY=ghcr.io/username PUSH=true ./scripts/docker-build.sh
```

---

### ☸️ k8s-deploy.sh
**Deploy to Kubernetes**

Automated Kubernetes deployment with all required resources.

```bash
./scripts/k8s-deploy.sh
# OR
make k8s-deploy
```

**Environment variables:**
- `NAMESPACE`: Kubernetes namespace (default: production)
- `KUBECTL`: kubectl command path (default: kubectl)

**What it does:**
1. Creates namespace (if needed)
2. Applies secrets (if secrets.yaml exists)
3. Deploys ConfigMap
4. Deploys Redis
5. Deploys application
6. Sets up Ingress
7. Waits for deployment to be ready
8. Shows status and logs commands

**Prerequisites:**
- kubectl installed and configured
- Access to Kubernetes cluster
- `deployment/k8s/secrets.yaml` created from template

---

## Usage Examples

### Development Workflow
```bash
# 1. Initial setup (once)
make setup

# 2. Start development
make run

# 3. Make changes, then test
make test

# 4. Check code quality
make lint

# 5. Format code if needed
make format
```

### CI/CD Workflow
```bash
# Run all quality checks
./scripts/lint.sh && ./scripts/test.sh

# Build Docker image
./scripts/docker-build.sh

# Deploy to Kubernetes
./scripts/k8s-deploy.sh
```

### Production Deployment
```bash
# Option 1: Docker
make docker-build
make docker-run

# Option 2: Kubernetes
make k8s-deploy
make k8s-status
```

---

## Script Requirements

All scripts require:
- **Bash** shell (compatible with sh/zsh)
- **Python 3.11+** (for Python scripts)
- **Virtual environment** in `backend/venv` (created by setup.sh)

Additional requirements for specific scripts:
- **docker-build.sh**: Docker installed
- **k8s-deploy.sh**: kubectl installed and configured

---

## Troubleshooting

### "Permission denied" error
Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### Virtual environment not found
Run setup first:
```bash
make setup
```

### Tests failing
Ensure dependencies are installed:
```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Docker build fails
Check Docker is running:
```bash
docker info
```

---

## Making Changes

When adding new scripts:
1. Follow existing naming convention (`verb.sh`)
2. Add shebang: `#!/bin/bash`
3. Set exit on error: `set -e`
4. Include helpful echo messages
5. Make executable: `chmod +x scripts/newscript.sh`
6. Update this README
7. Add to Makefile if appropriate
