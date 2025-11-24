# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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

# Include routers
app.include_router(analyze_router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Clinical Mental Health Assistant API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }