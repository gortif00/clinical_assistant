# backend/app/middleware/metrics.py
"""
Prometheus metrics collection for system monitoring.

Exposes metrics for:
- HTTP request counts and durations
- Active request tracking
- Model inference performance
- Model memory usage
- Error tracking

Metrics are exposed at /metrics endpoint for Prometheus scraping.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
from typing import Callable

# ============================================================================
# HTTP METRICS
# ============================================================================
# Track general HTTP request metrics for monitoring API health

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']  # Labels: HTTP method, endpoint path, status code
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request processing duration in seconds',
    ['method', 'endpoint']  # Labels: HTTP method, endpoint path
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of currently active HTTP requests'
)

# ============================================================================
# ML MODEL METRICS
# ============================================================================
# Track ML-specific metrics for model performance monitoring

MODEL_INFERENCE_DURATION = Histogram(
    'model_inference_duration_seconds',
    'Model inference processing time in seconds',
    ['model_name']  # Labels: classifier, summarizer, generator
)

MODEL_LOAD_DURATION = Histogram(
    'model_load_duration_seconds',
    'Time taken to load a model into memory',
    ['model_name']  # Labels: classifier, summarizer, generator
)

MODEL_MEMORY_USAGE = Gauge(
    'model_memory_usage_bytes',
    'Current memory usage of loaded models in bytes',
    ['model_name']  # Labels: classifier, summarizer, generator
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total number of errors encountered',
    ['error_type', 'endpoint']  # Labels: exception type, endpoint path
)


# ============================================================================
# METRICS MIDDLEWARE CLASS
# ============================================================================

class MetricsMiddleware:
    \"""
    FastAPI middleware for automatic metrics collection.
    
    Tracks:
    - Active request count (incremented on request, decremented on completion)
    - Request duration (start to finish)
    - Total request count by method, endpoint, and status code
    - Error count by type and endpoint
    \"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        \"""
        Process request and collect metrics.
        
        Args:
            request (Request): Incoming FastAPI request
            call_next (Callable): Next middleware/handler in chain
            
        Returns:
            Response: HTTP response from handler
        \"""
        # Increment active requests counter
        ACTIVE_REQUESTS.inc()
        
        # Start timer for request duration
        start_time = time.time()
        
        try:
            # Process request through remaining middleware/handlers
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Record request count with labels
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            # Record request duration as histogram
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            ERROR_COUNT.labels(
                error_type=type(e).__name__,  # Exception class name
                endpoint=request.url.path
            ).inc()
            raise  # Re-raise exception after recording
            
        finally:
            # Always decrement active requests (even if error occurred)
            ACTIVE_REQUESTS.dec()


# ============================================================================
# PROMETHEUS METRICS ENDPOINT
# ============================================================================

async def metrics_endpoint(request: Request):
    \"""
    Expose metrics in Prometheus format.
    
    This endpoint should be scraped by Prometheus at regular intervals
    (e.g., every 15 seconds) to collect metrics.
    
    Returns:
        Response: Metrics in Prometheus text format
    \"""
    return Response(
        content=generate_latest(),  # Generate Prometheus format
        media_type=CONTENT_TYPE_LATEST  # text/plain; version=0.0.4
    )
