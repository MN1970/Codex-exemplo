"""
Security and application configuration
"""

from pydantic_settings import BaseSettings
from datetime import timedelta
from typing import List


class SecuritySettings(BaseSettings):
    """Security configuration settings"""

    # JWT Configuration
    JWT_SECRET: str = "change-me-in-production-use-secrets-token-urlsafe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Public endpoints (no authentication required)
    EXCLUDED_PATHS: List[str] = [
        "/api/health",
        "/api/config",
        "/openapi.json",
        "/docs",
        "/redoc",
    ]

    # Service identification
    SERVICE_NAME: str = "portal-master"
    SERVICE_VERSION: str = "0.1.0-portal-adk5"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_security_settings() -> SecuritySettings:
    """Get security settings singleton"""
    return SecuritySettings()


# Computed values
def get_access_token_expire_delta() -> timedelta:
    """Get access token expiration delta"""
    settings = get_security_settings()
    return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def get_refresh_token_expire_delta() -> timedelta:
    """Get refresh token expiration delta"""
    settings = get_security_settings()
    return timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
