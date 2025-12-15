# backend/app/middleware/auth.py
"""
JWT-based authentication and authorization middleware.

Implements:
- JWT token generation and validation
- Password hashing with bcrypt
- User authentication and authorization
- Access token (30 min) and refresh token (7 days) management
- User tier-based access control

Security:
- Uses HS256 algorithm for JWT signing
- Bcrypt for password hashing
- Bearer token authentication
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

# ============================================================================
# JWT CONFIGURATION
# ============================================================================
# Secret key for signing JWT tokens (MUST be changed in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"  # HMAC with SHA-256
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token validity: 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token validity: 7 days

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Bearer token security scheme for FastAPI
security = HTTPBearer()


class User:
    """
    User model for authentication.
    
    Represents an authenticated user with username, email, and tier.
    Used for authorization and rate limiting.
    """
    def __init__(self, username: str, email: str, tier: str = "authenticated"):
        self.username = username
        self.email = email
        self.tier = tier  # User tier: 'anonymous', 'authenticated', or 'premium'


class AuthManager:
    """
    Authentication and authorization manager.
    
    Provides static methods for:
    - Password hashing and verification
    - JWT token creation (access and refresh)
    - Token validation and decoding
    """
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hashed version.
        
        Args:
            plain_password (str): Plain text password to verify
            hashed_password (str): Bcrypt hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        
        Args:
            password (str): Plain text password to hash
            
        Returns:
            str: Bcrypt hashed password for storage
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create a JWT access token.
        
        Args:
            data (dict): Data to encode in token (typically {'sub': username})
            expires_delta (Optional[timedelta]): Custom expiration time
            
        Returns:
            str: Encoded JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        \"""
        Create a JWT refresh token with longer expiration.
        
        Args:
            data (dict): Data to encode in token
            
        Returns:
            str: Encoded JWT refresh token
        \"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate a JWT token.
        
        Args:
            token (str): JWT token string
            
        Returns:
            dict: Decoded token payload
            
        Raises:
            HTTPException: 401 if token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )


# ============================================================================
# FASTAPI DEPENDENCIES FOR ROUTE PROTECTION
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Extract and validate user from JWT token (FastAPI dependency).
    
    Use this dependency to protect routes that require authentication.
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if token is invalid or missing
    """
    token = credentials.credentials
    
    try:
        payload = AuthManager.decode_token(token)
        username: str = payload.get("sub")
        email: str = payload.get("email")
        tier: str = payload.get("tier", "authenticated")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return User(username=username, email=email, tier=tier)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============================================================================
# OPTIONAL AUTHENTICATION DEPENDENCY
# ============================================================================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    \"""
    Extract user from JWT token if present, allow anonymous access otherwise.
    
    Use this dependency for routes that work for both authenticated and
    anonymous users, with different behavior based on authentication status.
    
    Args:
        credentials: Optional bearer token from request header
        
    Returns:
        Optional[User]: User object if authenticated, None if anonymous
    \"""
    # No credentials provided - anonymous user
    if credentials is None:
        return None
    
    # Credentials provided - validate and return user
    return await get_current_user(credentials)
