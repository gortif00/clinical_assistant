#!/bin/bash

# Clinical Mental Health Assistant - Run Tests Script
# Runs the complete test suite with coverage reporting

set -e

echo "🧪 Running Clinical Assistant Test Suite"
echo "=========================================="
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
source backend/venv/bin/activate

# Run tests with coverage
echo "📊 Running tests with coverage..."
pytest tests/ \
    --cov=backend/app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    -v

echo ""
echo "✅ Tests complete!"
echo ""
echo "Coverage report generated:"
echo "  - HTML: htmlcov/index.html"
echo "  - XML: coverage.xml"
echo ""
echo "Open HTML report:"
echo "  open htmlcov/index.html"
