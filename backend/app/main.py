# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
import time
import uuid

from app.api.v1.analyze import router as analyze_router
from app.api.v1.health import router as health_router
from app.ml.models_loader import load_all_models
from app.middleware.rate_limiter import AdvancedRateLimiter
from app.middleware.metrics import MetricsMiddleware, metrics_endpoint
from app.core.logging_config import setup_logging, RequestLogger
from app.core import config


# Setup logging
setup_logging(
    log_level=config.LOG_LEVEL,
    log_dir="logs",
    enable_json=True
)
logger = RequestLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, cleanup on shutdown"""
    print("\n🚀 Starting Clinical Mental Health Assistant API...")
    print(f"📊 Logging level: {config.LOG_LEVEL}")
    print(f"🔒 Rate limiting: {'Redis' if config.USE_REDIS_RATE_LIMITING else 'In-Memory'}")
    load_all_models()
    yield
    print("\n👋 Shutting down...")


app = FastAPI(
    title="Clinical Mental Health Assistant API",
    description="AI-Powered Diagnostic Support Tool for Mental Health Professionals",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
rate_limiter = AdvancedRateLimiter()
app.state.rate_limiter = rate_limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics middleware
app.middleware("http")(MetricsMiddleware())

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    response_time = time.time() - start_time
    logger.log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        ip_address=request.client.host if request.client else "unknown",
        status_code=response.status_code,
        response_time=response_time
    )
    
    return response

# Include API routers
app.include_router(analyze_router, prefix="/api/v1", tags=["analyze"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])

# Metrics endpoint for Prometheus
app.add_route("/metrics", metrics_endpoint)

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