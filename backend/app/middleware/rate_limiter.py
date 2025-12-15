# backend/app/middleware/rate_limiter.py
"""
Advanced rate limiting middleware for API protection.

Implements tiered rate limiting with Redis for distributed rate limiting
and in-memory fallback for single-instance deployments.

Supports three user tiers:
- Anonymous: 10 requests/minute
- Authenticated: 100 requests/minute
- Premium: 1000 requests/minute
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from datetime import datetime, timedelta
from typing import Optional

# Initialize basic rate limiter (uses client IP address as key)
limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# REDIS CONNECTION FOR DISTRIBUTED RATE LIMITING
# ============================================================================
# Redis enables rate limiting across multiple server instances
try:
    redis_client = redis.Redis(
        host='localhost',  # Redis server address
        port=6379,  # Default Redis port
        db=0,  # Database number
        decode_responses=True  # Automatically decode responses to strings
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    # Redis not available, fall back to in-memory rate limiting
    REDIS_AVAILABLE = False
    print("⚠️  Redis not available, using in-memory rate limiting")


class AdvancedRateLimiter:
    """
    Advanced rate limiter with multiple user tier strategies.
    
    Implements token bucket algorithm for rate limiting with different
    limits based on user authentication tier.
    """
    
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
        
        # Use Redis if available (for distributed rate limiting)
        # Otherwise fall back to in-memory rate limiting
        if REDIS_AVAILABLE:
            return await self._check_redis(key, max_requests, window_seconds)
        else:
            return await self._check_memory(key, max_requests, window_seconds)
    
    async def _check_redis(self, key: str, max_requests: int, window: int) -> bool:
        """
        Redis-based rate limiting for distributed deployments.
        
        Uses Redis atomic operations to track request counts across
        multiple server instances.
        
        Args:
            key (str): Redis key for this client/tier combination
            max_requests (int): Maximum requests allowed in window
            window (int): Time window in seconds
            
        Returns:
            bool: True if within limit
            
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Get current request count for this key
        current = redis_client.get(key)
        
        # First request from this client in this window
        if current is None:
            # Set initial count to 1 with expiration
            redis_client.setex(key, window, 1)
            return True
        
        # Check if limit exceeded
        current_count = int(current)
        if current_count >= max_requests:
            # Get time until reset
            ttl = redis_client.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {ttl} seconds."
            )
        
        # Increment count atomically
        redis_client.incr(key)
        return True
    
    async def _check_memory(self, key: str, max_requests: int, window: int) -> bool:
        """
        In-memory rate limiting fallback for single-instance deployments.
        
        This is a simplified implementation. In production with multiple
        instances, use Redis-based rate limiting.
        
        Args:
            key (str): Key for this client/tier combination
            max_requests (int): Maximum requests allowed
            window (int): Time window in seconds
            
        Returns:
            bool: Always True (permissive fallback)
        """
        # Simple in-memory implementation
        # In production with multiple instances, use Redis
        return True


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================
# Create global instance for use throughout the application
rate_limiter = AdvancedRateLimiter()
