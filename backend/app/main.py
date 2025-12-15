# backend/app/main.py
# MAIN APPLICATION ENTRY POINT
# This file configures and starts the FastAPI server that serves both frontend and backend

# FastAPI imports for creating the web application
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  # Allow requests from other origins
from fastapi.staticfiles import StaticFiles  # Serve static files (CSS, JS)
from fastapi.responses import FileResponse  # Return HTML files
from contextlib import asynccontextmanager  # Manage app startup/shutdown
from pathlib import Path  # Handle file paths
import time  # Measure response times
import uuid  # Generate unique request IDs

# Import project modules
from app.api.v1.analyze import router as analyze_router  # Analysis endpoint routes
from app.api.v1.health import router as health_router  # Health check routes
from app.ml.models_loader import load_all_models  # Function to load ML models
from app.middleware.rate_limiter import AdvancedRateLimiter  # Rate limiting (protection against abuse)
from app.middleware.metrics import MetricsMiddleware, metrics_endpoint  # Prometheus metrics
from app.core.logging_config import setup_logging, RequestLogger  # Logging system
from app.core import config  # Global configuration


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Configure the logging system before starting the application
setup_logging(
    log_level=config.LOG_LEVEL,  # Log detail level (INFO, DEBUG, ERROR, etc.)
    log_dir="logs",  # Folder where log files are saved
    enable_json=True  # JSON format logs (easier to process)
)
logger = RequestLogger()  # Logger instance to record HTTP requests


# ============================================================================
# LIFESPAN: APPLICATION LIFECYCLE MANAGEMENT
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the complete application lifecycle:
    - STARTUP: Executed when the server starts (loads ML models)
    - SHUTDOWN: Executed when the server closes (cleanup)
    """
    # ---- STARTUP: On initialization ----
    print("\n🚀 Starting Clinical Mental Health Assistant API...")
    print(f"📊 Logging level: {config.LOG_LEVEL}")
    print(f"🔒 Rate limiting: {'Redis' if config.USE_REDIS_RATE_LIMITING else 'In-Memory'}")
    
    # Load all ML models (BERT, T5, Llama) using lazy loading
    # Models are loaded into memory once and reused across requests
    load_all_models()
    
    yield  # Application runs between startup and shutdown
    
    # ---- SHUTDOWN: On closing ----
    print("\n👋 Shutting down...")


# ============================================================================
# FASTAPI APPLICATION CREATION
# ============================================================================
app = FastAPI(
    title="Clinical Mental Health Assistant API",
    description="AI-Powered Diagnostic Support Tool for Mental Health Professionals",
    version="1.0.0",
    lifespan=lifespan,  # Link the lifecycle defined above
    docs_url="/docs",  # Interactive Swagger documentation at /docs
    redoc_url="/redoc"  # Alternative ReDoc documentation at /redoc
)

# ============================================================================
# RATE LIMITER: PROTECTION AGAINST ABUSE
# ============================================================================
# Initialize the rate limiter (limits the number of requests per minute)
# - Anonymous: 10 req/min
# - Authenticated: 100 req/min
# - Premium: 1000 req/min
rate_limiter = AdvancedRateLimiter()
app.state.rate_limiter = rate_limiter  # Store in app state

# ============================================================================
# CORS MIDDLEWARE: ALLOW REQUESTS FROM OTHER ORIGINS
# ============================================================================
# Although the frontend is served from the same port, CORS is useful for development
# and to allow access from other applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # Allowed origins (configured in .env)
    allow_credentials=True,  # Allow cookies and authentication
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# METRICS MIDDLEWARE: PROMETHEUS
# ============================================================================
# Collects metrics from HTTP requests (duration, count, errors)
# These metrics are exposed at /metrics to be scraped by Prometheus
app.middleware("http")(MetricsMiddleware())

# ============================================================================
# LOGGING MIDDLEWARE: LOG ALL REQUESTS
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware that logs information for each HTTP request:
    - Unique request ID
    - Method (GET, POST, etc.)
    - Path (/api/v1/analyze)
    - Client IP address
    - Response code (200, 404, 500, etc.)
    - Response time in seconds
    """
    request_id = str(uuid.uuid4())  # Unique ID to track the request
    start_time = time.time()  # Start time
    
    # Process the request (call next middleware or endpoint)
    response = await call_next(request)
    
    # Calculate how long it took to process
    response_time = time.time() - start_time
    
    # Log the information
    logger.log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        ip_address=request.client.host if request.client else "unknown",
        status_code=response.status_code,
        response_time=response_time
    )
    
    return response

# ============================================================================
# INCLUDE ROUTERS: API ENDPOINTS
# ============================================================================
# Add endpoints defined in other files
app.include_router(analyze_router, prefix="/api/v1", tags=["analyze"])  # POST /api/v1/analyze
app.include_router(health_router, prefix="/api/v1", tags=["health"])  # GET /api/v1/health

# ============================================================================
# METRICS ENDPOINT: EXPOSE METRICS FOR PROMETHEUS
# ============================================================================
# Prometheus can scrape /metrics to collect statistics
app.add_route("/metrics", metrics_endpoint)

# ============================================================================
# SERVE FRONTEND: HTML, CSS, JS
# ============================================================================
# Calculate the path to the frontend folder (go up two levels from backend/app/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static file folders so they're accessible from the browser
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

@app.get("/")
async def serve_frontend():
    """
    Root endpoint: serves the frontend index.html file.
    When the user opens http://localhost:8000 in the browser,
    they receive the HTML file containing the chatbot interface.
    """
    return FileResponse(str(FRONTEND_DIR / "index.html"))