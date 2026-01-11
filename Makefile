.PHONY: help setup install test lint clean run docker-build docker-run k8s-deploy

# Default target
help:
	@echo "Clinical Mental Health Assistant - Makefile Commands"
	@echo "====================================================="
	@echo ""
	@echo "Development:"
	@echo "  make setup          - Initial project setup (venv + deps)"
	@echo "  make install        - Install dependencies only"
	@echo "  make run            - Start development server"
	@echo "  make test           - Run test suite with coverage"
	@echo "  make lint           - Run code quality checks"
	@echo "  make clean          - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run with docker-compose"
	@echo "  make docker-stop    - Stop docker-compose"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy     - Deploy to Kubernetes"
	@echo "  make k8s-status     - Check deployment status"
	@echo "  make k8s-logs       - Tail application logs"
	@echo ""

# Initial setup
setup:
	@./scripts/setup.sh

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@cd backend && source venv/bin/activate && pip install -r requirements.txt -q
	@cd backend && source venv/bin/activate && pip install -r requirements-dev.txt -q
	@echo "✅ Dependencies installed"

# Run development server
run:
	@./scripts/start.sh

# Run tests
test:
	@./scripts/test.sh

# Run linting
lint:
	@./scripts/lint.sh

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf htmlcov/ .coverage coverage.xml .pytest_cache/ 2>/dev/null || true
	@echo "✅ Clean complete"

# Docker build
docker-build:
	@./scripts/docker-build.sh

# Docker run
docker-run:
	@echo "🐳 Starting with docker-compose..."
	@docker-compose -f deployment/docker-compose.yml up

docker-stop:
	@echo "🛑 Stopping docker-compose..."
	@docker-compose -f deployment/docker-compose.yml down

# Kubernetes deployment
k8s-deploy:
	@./scripts/k8s-deploy.sh

k8s-status:
	@kubectl get pods,svc,ingress -n production

k8s-logs:
	@kubectl logs -f deployment/clinical-assistant -n production

# Format code
format:
	@echo "🎨 Formatting code with Black..."
	@cd backend && source venv/bin/activate && black app/
	@echo "✅ Code formatted"

# Generate requirements.txt from current environment
freeze:
	@echo "📋 Generating requirements.txt..."
	@cd backend && source venv/bin/activate && pip freeze > requirements.txt
	@echo "✅ requirements.txt updated"
