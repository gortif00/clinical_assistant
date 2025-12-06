# tests/unit/test_auth.py
"""
Tests para sistema de autenticación JWT
"""
import pytest
from datetime import timedelta
from jose import jwt, JWTError
from backend.app.middleware.auth import AuthManager
from backend.app.core.config import settings


def test_create_access_token():
    """Test creación de access token"""
    data = {"sub": "test_user"}
    token = AuthManager.create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decodificar y verificar
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == "test_user"
    assert "exp" in payload


def test_create_access_token_with_expiry():
    """Test token con expiración custom"""
    data = {"sub": "test_user"}
    expires = timedelta(minutes=5)
    token = AuthManager.create_access_token(data, expires_delta=expires)
    
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    
    assert payload["sub"] == "test_user"


def test_create_refresh_token():
    """Test creación de refresh token"""
    data = {"sub": "test_user"}
    token = AuthManager.create_refresh_token(data)
    
    assert token is not None
    payload = jwt.decode(
        token,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == "test_user"


def test_verify_password():
    """Test hash y verificación de password"""
    password = "test_password_123"
    hashed = AuthManager.get_password_hash(password)
    
    assert hashed != password
    assert AuthManager.verify_password(password, hashed) is True
    assert AuthManager.verify_password("wrong_password", hashed) is False


def test_decode_invalid_token():
    """Test decodificación de token inválido"""
    with pytest.raises(JWTError):
        jwt.decode(
            "invalid.token.here",
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )


def test_expired_token():
    """Test token expirado"""
    data = {"sub": "test_user"}
    # Token que expira inmediatamente
    token = AuthManager.create_access_token(
        data,
        expires_delta=timedelta(seconds=-1)
    )
    
    with pytest.raises(JWTError):
        jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
