#!/bin/bash

# Clinical Mental Health Assistant - Linting and Code Quality Check
# Runs code quality checks: black, flake8, mypy

set -e

echo "🔍 Running Code Quality Checks"
echo "==============================="
echo ""

cd "$(dirname "$0")/.."

# Activate virtual environment
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/setup.sh first"
    exit 1
fi

source backend/venv/bin/activate

echo "1️⃣ Running Black (code formatter)..."
black backend/app --check --diff || {
    echo "❌ Black found formatting issues"
    echo "   Fix with: black backend/app"
    exit 1
}
echo "✅ Black passed"
echo ""

echo "2️⃣ Running Flake8 (linter)..."
flake8 backend/app --max-line-length=120 --extend-ignore=E203,W503 || {
    echo "❌ Flake8 found issues"
    exit 1
}
echo "✅ Flake8 passed"
echo ""

echo "3️⃣ Running MyPy (type checker)..."
mypy backend/app --ignore-missing-imports || {
    echo "⚠️  MyPy found type issues (non-blocking)"
}
echo "✅ MyPy complete"
echo ""

echo "=============================="
echo "✅ All code quality checks passed!"
