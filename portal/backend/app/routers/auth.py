"""
Authentication router with JWT token endpoints
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_jwt_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
    RefreshTokenRequest,
    User,
    TokenData,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Mock user database for development (Phase 2 will use real database)
MOCK_USERS = {
    "admin": {
        "id": "user-001",
        "username": "admin",
        "email": "admin@portal.local",
        "password_hash": hash_password("admin123"),  # Plain password for development only
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(),
    },
    "editor": {
        "id": "user-002",
        "username": "editor",
        "email": "editor@portal.local",
        "password_hash": hash_password("editor123"),
        "role": "editor",
        "is_active": True,
        "created_at": datetime.now(),
    },
    "viewer": {
        "id": "user-003",
        "username": "viewer",
        "email": "viewer@portal.local",
        "password_hash": hash_password("viewer123"),
        "role": "viewer",
        "is_active": True,
        "created_at": datetime.now(),
    },
}


@router.post(
    "/token",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def login(credentials: LoginRequest) -> LoginResponse:
    """
    Authenticate user and return access token.

    **Phase 2 Implementation Note:** Currently uses mock user database for development.
    Will be updated to query real user database from auth service.

    Args:
        credentials: Username and password

    Returns:
        LoginResponse with access token, refresh token, and user info

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Validate inputs
    if not credentials.username or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )

    # Find user (Phase 2: will query database)
    user_data = MOCK_USERS.get(credentials.username)
    if not user_data:
        logger.warning(f"Login attempt with unknown username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Verify password
    if not verify_password(credentials.password, user_data["password_hash"]):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Check if user is active
    if not user_data.get("is_active"):
        logger.warning(f"Login attempt with inactive user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    # Create tokens
    token_data = {
        "sub": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Log successful login
    logger.info(f"Successful login: {credentials.username} (ID: {user_data['id']})")

    # Build response
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"],
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=1800,  # 30 minutes in seconds
        user=user,
    )


@router.post(
    "/verify",
    response_model=TokenVerifyResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"},
    },
)
async def verify_token(request: TokenVerifyRequest) -> TokenVerifyResponse:
    """
    Verify JWT token validity.

    Args:
        request: TokenVerifyRequest with token to verify

    Returns:
        TokenVerifyResponse with validity status and payload

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = verify_jwt_token(request.token)

        token_data = TokenData(
            sub=payload.get("sub"),
            role=payload.get("role", "viewer"),
            service=payload.get("service", "portal-master"),
            iat=payload.get("iat"),
            exp=payload.get("exp"),
        )

        return TokenVerifyResponse(
            valid=True,
            payload=token_data,
            message="Token is valid",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh_access_token(
    request: RefreshTokenRequest,
) -> TokenResponse:
    """
    Refresh expired access token using refresh token.

    **Phase 2 Implementation Note:** Will validate refresh token against
    refresh token database to prevent reuse after rotation.

    Args:
        request: RefreshTokenRequest with refresh token

    Returns:
        TokenResponse with new access token and refresh token

    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    try:
        payload = verify_jwt_token(request.refresh_token)

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Create new tokens
        token_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role", "viewer"),
        }
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        logger.info(f"Token refreshed for user: {payload.get('sub')}")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",
            expires_in=1800,  # 30 minutes in seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.get(
    "/me",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user information.

    Args:
        current_user: Current user from JWT token

    Returns:
        User information

    Raises:
        HTTPException: 401 if not authenticated
    """
    # Phase 2: Fetch full user details from database
    user_id = current_user.get("sub")

    # For now, return mock user data
    for user_data in MOCK_USERS.values():
        if user_data["id"] == user_id:
            return User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                created_at=user_data["created_at"],
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )
