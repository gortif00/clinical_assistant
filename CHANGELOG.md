# Changelog

All notable changes to the Clinical Mental Health Assistant project.

## [2.0.0] - 2026-01-11

### 🎯 Major Reorganization - Production-Ready Structure

Complete project restructuring for professional deployment and maintainability.

### Added

#### Build & Automation
- **Makefile** with comprehensive build automation
  - `make setup` - automated environment setup
  - `make run` - start development server
  - `make test` - run test suite with coverage
  - `make lint` - code quality checks
  - `make docker-build` - build Docker images
  - `make k8s-deploy` - Kubernetes deployment
  - `make help` - show all commands

#### Scripts (`scripts/` directory)
- `setup.sh` - Complete development environment initialization
- `start.sh` - Quick server startup (moved from root)
- `test.sh` - Automated testing with coverage reporting
- `lint.sh` - Multi-tool code quality checks (Black, Flake8, MyPy)
- `docker-build.sh` - Docker build automation with registry support
- `k8s-deploy.sh` - Kubernetes deployment automation
- `README.md` - Comprehensive scripts documentation

#### Documentation
- `docs/REORGANIZATION.md` - Complete reorganization guide
- `scripts/README.md` - Scripts usage documentation
- Enhanced `PROJECT_STRUCTURE.md` with new organization
- Updated main `README.md` with Makefile commands

#### Organization
- `deployment/` directory for all deployment configs
- `config/` directory for configuration files
- `.github/workflows/` structure for CI/CD (ready for implementation)

### Changed

#### Directory Structure
- **Moved deployment files** to `deployment/`
  - `docker-compose.yml` → `deployment/docker-compose.yml`
  - `Dockerfile` → `deployment/Dockerfile`
  - `.dockerignore` → `deployment/.dockerignore`
  - `k8s/` → `deployment/k8s/`

- **Moved configuration** to `config/`
  - `pytest.ini` → `config/pytest.ini`

- **Moved scripts** to `scripts/`
  - `start.sh` → `scripts/start.sh`

- **Moved documentation** to `docs/`
  - `BUG_FIX_P0.md` → `docs/BUG_FIX_P0.md`

#### Documentation Updates
- `README.md` - Updated all paths and added Makefile commands
- `PROJECT_STRUCTURE.md` - Complete rewrite with new structure
- `.env.example` - Enhanced with comprehensive configuration options

### Improved

#### Developer Experience
- **One-command setup**: `make setup` handles everything
- **Unified interface**: All operations through `make` or `scripts/`
- **Better testing**: Automated coverage with HTML reports
- **Code quality**: Automated linting and formatting
- **Clear documentation**: README in every major directory

#### Deployment
- **Multiple deployment options**: Local, Docker, Kubernetes
- **Automated scripts**: No manual steps required
- **Professional organization**: Industry-standard structure
- **CI/CD ready**: Proper structure for GitHub Actions

#### Maintenance
- **Clear separation**: Source, deployment, scripts, config
- **Scalable structure**: Easy to add new features
- **Better navigation**: Know where everything belongs
- **Team-ready**: Professional organization for collaboration

### Migration Guide

#### For Existing Users

**Your data is safe:**
- `.env` file remains in root
- All backend code unchanged in `backend/`
- Frontend unchanged in `frontend/`
- Tests unchanged in `tests/`

**Update your commands:**

| Old Command | New Command |
|------------|-------------|
| `./start.sh` | `make run` or `./scripts/start.sh` |
| `docker-compose up` | `make docker-run` or `docker-compose -f deployment/docker-compose.yml up` |
| `kubectl apply -f k8s/` | `make k8s-deploy` or `./scripts/k8s-deploy.sh` |
| `pytest` | `make test` or `./scripts/test.sh` |

**Quick Start (New Users):**
```bash
git clone <repo>
cd clinical_assistant
make setup
make run
```

### Technical Details

#### File Locations
- Source code: `backend/app/`
- Frontend: `frontend/`
- Tests: `tests/`
- Scripts: `scripts/`
- Docker: `deployment/`
- Kubernetes: `deployment/k8s/`
- Config: `config/` + `.env`
- Docs: `docs/`

#### Benefits
✅ Professional structure
✅ Easy onboarding (`make setup`)
✅ Automated workflows
✅ Production-ready
✅ CI/CD prepared
✅ Team-friendly
✅ Industry-standard organization

---

## [1.5.0] - Previous Version

### Added
- ChatGPT-style structured output for clinical reports
- Markdown parser for formatted recommendations
- Enhanced generation prompts with titles, subtitles, and sections
- Improved model generation parameters

### Changed
- Updated Llama generation to produce comprehensive structured reports
- Enhanced frontend markdown rendering
- Increased token limits for better report quality

---

## [1.0.0] - Initial Release

### Features
- Multi-stage ML pipeline (Classification, Summarization, Generation)
- BERT classifier for mental health diagnosis
- T5 summarizer for clinical summaries
- Llama generator with LoRA for treatment recommendations
- Modern chatbot UI with dark mode
- Docker deployment support
- Kubernetes manifests
- Rate limiting and JWT authentication
- Prometheus metrics and Grafana dashboards
- Comprehensive test suite (25+ tests, 70% coverage)

---

## Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backwards-compatible)
- **PATCH** version for backwards-compatible bug fixes
