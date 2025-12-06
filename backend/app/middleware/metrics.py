# backend/app/middleware/metrics.py
"""
Prometheus metrics para monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
from typing import Callable

# Métricas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Active HTTP requests'
)

# Métricas específicas de ML
MODEL_INFERENCE_DURATION = Histogram(
    'model_inference_duration_seconds',
    'Model inference duration in seconds',
    ['model_name']
)

MODEL_LOAD_DURATION = Histogram(
    'model_load_duration_seconds',
    'Model loading duration in seconds',
    ['model_name']
)

MODEL_MEMORY_USAGE = Gauge(
    'model_memory_usage_bytes',
    'Model memory usage in bytes',
    ['model_name']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)


class MetricsMiddleware:
    """Middleware para recolectar métricas de requests"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Incrementar requests activos
        ACTIVE_REQUESTS.inc()
        
        # Timer para duración
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Registrar métricas
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                endpoint=request.url.path
            ).inc()
            raise
            
        finally:
            ACTIVE_REQUESTS.dec()


async def metrics_endpoint(request: Request):
    """Endpoint para exponer métricas a Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
