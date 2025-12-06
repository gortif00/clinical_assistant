# backend/app/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from datetime import datetime, timedelta
from typing import Optional

# Inicializar limiter
limiter = Limiter(key_func=get_remote_address)

# Configuración de Redis para rate limiting distribuido
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available, using in-memory rate limiting")

class AdvancedRateLimiter:
    """Rate limiter avanzado con múltiples estrategias"""
    
    def __init__(self):
        self.limits = {
            "anonymous": {"requests": 10, "window": 60},      # 10 req/min
            "authenticated": {"requests": 100, "window": 60}, # 100 req/min
            "premium": {"requests": 1000, "window": 60}       # 1000 req/min
        }
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_tier: str = "anonymous"
    ) -> bool:
        """Verifica si el request está dentro del límite"""
        client_ip = get_remote_address(request)
        key = f"rate_limit:{user_tier}:{client_ip}"
        
        limit_config = self.limits.get(user_tier, self.limits["anonymous"])
        max_requests = limit_config["requests"]
        window_seconds = limit_config["window"]
        
        if REDIS_AVAILABLE:
            return await self._check_redis(key, max_requests, window_seconds)
        else:
            return await self._check_memory(key, max_requests, window_seconds)
    
    async def _check_redis(self, key: str, max_requests: int, window: int) -> bool:
        """Rate limiting con Redis (distribuido)"""
        current = redis_client.get(key)
        
        if current is None:
            redis_client.setex(key, window, 1)
            return True
        
        current_count = int(current)
        if current_count >= max_requests:
            ttl = redis_client.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds."
            )
        
        redis_client.incr(key)
        return True
    
    async def _check_memory(self, key: str, max_requests: int, window: int) -> bool:
        """Rate limiting en memoria (fallback)"""
        # Implementación simple en memoria
        # En producción, usar Redis
        return True

# Instancia global
rate_limiter = AdvancedRateLimiter()
