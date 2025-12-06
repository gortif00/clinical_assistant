# tests/unit/test_rate_limiter.py
"""
Tests para rate limiter
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import Request
from backend.app.middleware.rate_limiter import AdvancedRateLimiter


@pytest.fixture
def rate_limiter():
    """Fixture para rate limiter sin Redis"""
    return AdvancedRateLimiter(use_redis=False)


@pytest.mark.asyncio
async def test_rate_limit_anonymous_user(rate_limiter):
    """Test que usuarios anónimos tienen límite de 10 req/min"""
    request = Mock(spec=Request)
    request.client.host = "127.0.0.1"
    
    # Primeros 10 requests deben pasar
    for _ in range(10):
        result = await rate_limiter.check_rate_limit(request, "anonymous")
        assert result is True
    
    # Request 11 debe fallar
    result = await rate_limiter.check_rate_limit(request, "anonymous")
    assert result is False


@pytest.mark.asyncio
async def test_rate_limit_authenticated_user(rate_limiter):
    """Test que usuarios autenticados tienen límite de 100 req/min"""
    request = Mock(spec=Request)
    request.client.host = "127.0.0.1"
    
    # Primeros 100 requests deben pasar
    for _ in range(100):
        result = await rate_limiter.check_rate_limit(request, "authenticated")
        assert result is True
    
    # Request 101 debe fallar
    result = await rate_limiter.check_rate_limit(request, "authenticated")
    assert result is False


@pytest.mark.asyncio
async def test_rate_limit_different_ips():
    """Test que diferentes IPs tienen límites independientes"""
    limiter = AdvancedRateLimiter(use_redis=False)
    
    request1 = Mock(spec=Request)
    request1.client.host = "127.0.0.1"
    
    request2 = Mock(spec=Request)
    request2.client.host = "192.168.1.1"
    
    # Llenar límite de IP 1
    for _ in range(10):
        await limiter.check_rate_limit(request1, "anonymous")
    
    # IP 1 bloqueada
    assert await limiter.check_rate_limit(request1, "anonymous") is False
    
    # IP 2 todavía puede hacer requests
    assert await limiter.check_rate_limit(request2, "anonymous") is True


@pytest.mark.asyncio
async def test_rate_limit_with_redis():
    """Test rate limiter con Redis (mockeado)"""
    with patch('backend.app.middleware.rate_limiter.redis.Redis') as mock_redis:
        # Mock Redis responses
        mock_redis_instance = Mock()
        mock_redis_instance.get.return_value = None
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        limiter = AdvancedRateLimiter(
            use_redis=True,
            redis_url="redis://localhost:6379"
        )
        
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        
        result = await limiter.check_rate_limit(request, "anonymous")
        assert result is True
        
        # Verificar que se llamó a Redis
        mock_redis_instance.get.assert_called()
