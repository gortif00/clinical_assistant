#!/bin/bash

# Clinical Mental Health Assistant - Frontend Startup Script

echo "🎨 Clinical Mental Health Assistant - Frontend"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    exit 1
fi

cd frontend

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "🚀 Starting frontend server on http://localhost:3000"
    echo "Press Ctrl+C to stop"
    echo ""
    python3 -m http.server 3000
elif command -v python &> /dev/null; then
    echo "🚀 Starting frontend server on http://localhost:3000"
    echo "Press Ctrl+C to stop"
    echo ""
    python -m http.server 3000
else
    echo "❌ Python not found. Please install Python to run the frontend."
    exit 1
fi
