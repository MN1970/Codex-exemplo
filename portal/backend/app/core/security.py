"""
Authentication and security utilities
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import (
    get_security_settings,
    get_access_token_expire_delta,
    get_refresh_token_expire_delta,
)

oauth2_scheme = HTTPBearer(
    description="JWT Bearer Token",
    auto_error=True
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Claims to encode (must include 'sub' for user ID)
        expires_delta: Token expiration time delta

    Returns:
        Encoded JWT token
    """
    settings = get_security_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + get_access_token_expire_delta()

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "service": settings.SERVICE_NAME,
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Claims to encode (must include 'sub' for user ID)

    Returns:
        Encoded JWT refresh token
    """
    settings = get_security_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + get_refresh_token_expire_delta()

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "service": settings.SERVICE_NAME,
        "type": "refresh",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    settings = get_security_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    Dependency to extract and validate the current user from JWT token.

    Args:
        credentials: HTTP Bearer token from request

    Returns:
        Decoded token payload with user information

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_jwt_token(token)

    # Validate required claims
    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to ensure the current user has admin role.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current user payload if they are an admin

    Raises:
        HTTPException: If user is not an admin
    """
    role = current_user.get("role", "viewer")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions: admin role required",
        )
    return current_user


async def get_current_editor_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to ensure the current user has editor or admin role.

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current user payload if they have editor or admin role

    Raises:
        HTTPException: If user does not have editor or admin role
    """
    role = current_user.get("role", "viewer")
    if role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions: editor or admin role required",
        )
    return current_user
