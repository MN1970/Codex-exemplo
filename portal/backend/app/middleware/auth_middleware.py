"""
Authentication middleware for JWT token validation
"""

import logging
import time
from typing import Callable, List
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.security import verify_jwt_token
from app.core.config import get_security_settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate JWT tokens on protected endpoints.

    Automatically validates JWT tokens from Authorization header for all endpoints
    except those in the excluded paths list. Injects user information into request state.
    """

    def __init__(
        self,
        app,
        excluded_paths: List[str] = None,
    ):
        super().__init__(app)
        settings = get_security_settings()
        self.excluded_paths = excluded_paths or settings.EXCLUDED_PATHS
        self.service_name = settings.SERVICE_NAME

    def is_excluded_path(self, path: str) -> bool:
        """Check if path is in the excluded (public) paths list."""
        # Normalize path
        normalized_path = path.rstrip("/") or "/"

        for excluded in self.excluded_paths:
            excluded_normalized = excluded.rstrip("/") or "/"
            if normalized_path == excluded_normalized:
                return True
            # Also check prefix matches for paths like /docs, /redoc, /openapi.json
            if normalized_path.startswith(excluded_normalized + "/"):
                return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> any:
        """
        Process request and validate JWT token if required.

        Args:
            request: FastAPI request object
            call_next: Callable to continue processing

        Returns:
            Response from next middleware/handler
        """
        start_time = time.time()
        path = request.url.path
        method = request.method

        # Skip authentication for excluded paths
        if self.is_excluded_path(path):
            response = await call_next(request)
            # Log request
            elapsed_time = time.time() - start_time
            logger.info(
                f"PUBLIC {method} {path} - "
                f"Status: {response.status_code} - "
                f"Time: {elapsed_time:.3f}s"
            )
            return response

        # Validate JWT token for protected endpoints
        token = None
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Parse Bearer token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication header format",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = parts[1]

            # Verify token
            payload = verify_jwt_token(token)

            # Inject user info into request state
            request.state.user = payload
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role", "viewer")

            # Log authenticated request
            response = await call_next(request)
            elapsed_time = time.time() - start_time
            logger.info(
                f"AUTH {method} {path} - "
                f"User: {request.state.user_id} - "
                f"Status: {response.status_code} - "
                f"Time: {elapsed_time:.3f}s"
            )
            return response

        except HTTPException as e:
            # Log unauthorized access attempt
            elapsed_time = time.time() - start_time
            logger.warning(
                f"UNAUTH {method} {path} - "
                f"Reason: {e.detail} - "
                f"Time: {elapsed_time:.3f}s"
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "detail": e.detail,
                    "error": "unauthorized",
                },
                headers=e.headers or {"WWW-Authenticate": "Bearer"},
            )

        except Exception as e:
            # Log unexpected errors
            elapsed_time = time.time() - start_time
            logger.error(
                f"ERROR {method} {path} - "
                f"Exception: {str(e)} - "
                f"Time: {elapsed_time:.3f}s"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error": "internal_error",
                },
            )
