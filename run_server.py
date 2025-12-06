#!/usr/bin/env python3
"""
Simple server runner script that avoids uvicorn's file watching issues.
"""
import os
import sys

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set HF token from environment
if 'HF_TOKEN' not in os.environ:
    print("⚠️  Warning: HF_TOKEN not set in environment")
    print("   Set it with: export HF_TOKEN=your_token_here")

if __name__ == "__main__":
    import uvicorn
    
    print("🧠 Clinical Mental Health Assistant")
    print("=" * 50)
    print()
    print("🚀 Starting server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print()
    print("   First request: ~30-60s (model loading)")
    print("   Subsequent: ~5-10s (cached)")
    print()
    print("=" * 50)
    print()
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run server without reload to avoid file watching issues
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid WatchFiles issues
        log_level="info"
    )
