# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.api.v1.analyze import router as analyze_router
from app.ml.models_loader import load_all_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, cleanup on shutdown"""
    print("\n🚀 Starting Clinical Mental Health Assistant API...")
    load_all_models()
    yield
    print("\n👋 Shutting down...")


app = FastAPI(
    title="Clinical Mental Health Assistant API",
    description="AI-Powered Diagnostic Support Tool for Mental Health Professionals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - configure origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(analyze_router, prefix="/api/v1")

# Get the project root directory (go up from backend/app/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static files (CSS, JS)
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.get("/")
async def serve_frontend():
    """Serve the main frontend HTML"""
    return FileResponse(str(FRONTEND_DIR / "index.html"))