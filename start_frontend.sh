#!/bin/bash

################################################################################
# Clinical Mental Health Assistant - Frontend Startup Script
#
# This script starts a simple HTTP server to serve the frontend files.
#
# The frontend is a static web application (HTML/CSS/JS) that:
#   - Provides a chat-based interface for clinical case analysis
#   - Communicates with the backend API at http://localhost:8000
#   - Displays classification results, summaries, and recommendations
#   - Offers both automatic and manual diagnosis modes
#
# Usage:
#   ./start_frontend.sh
#
# Requirements:
#   - Python 3.x (uses built-in http.server module)
#   - Backend must be running on port 8000
#
# The frontend will be available at: http://localhost:3000
################################################################################

echo "🎨 Clinical Mental Health Assistant - Frontend"
echo "=============================================="
echo ""

# ============================================
# DIRECTORY VALIDATION
# ============================================
# Verify we're in the correct directory structure
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    echo "   Please run this script from the project root directory"
    echo "   Example: cd /path/to/clinical_assistant && ./start_frontend.sh"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# ============================================
# START HTTP SERVER
# ============================================
# Use Python's built-in HTTP server to serve static files
# This is perfect for development; for production, use nginx/apache

echo "🚀 Starting frontend server..."
echo ""
echo "Frontend will be available at:"
echo "  - Main UI: http://localhost:3000"
echo ""
echo "Make sure the backend is running at:"
echo "  - Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "=============================================="
echo ""

# Try python3 first (preferred), fall back to python
if command -v python3 &> /dev/null; then
    # Python 3.x - use http.server module
    python3 -m http.server 3000
elif command -v python &> /dev/null; then
    # Legacy Python - try http.server or SimpleHTTPServer
    python -m http.server 3000 2>/dev/null || python -m SimpleHTTPServer 3000
else
    echo "❌ Python not found. Please install Python 3.x to run the frontend."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi
