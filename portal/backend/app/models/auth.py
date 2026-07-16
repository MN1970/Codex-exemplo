"""
Pydantic models for authentication and authorization
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class User(BaseModel):
    """User representation"""
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: Optional[EmailStr] = Field(None, description="User email")
    role: Literal["admin", "editor", "viewer"] = Field(
        default="viewer",
        description="User role for access control"
    )
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """JWT token payload structure"""
    sub: str = Field(..., description="Subject (user ID)")
    role: Literal["admin", "editor", "viewer"] = Field(
        default="viewer",
        description="User role"
    )
    service: str = Field(
        default="portal-master",
        description="Service identifier"
    )
    iat: Optional[int] = Field(None, description="Issued at timestamp")
    exp: Optional[int] = Field(None, description="Expiration timestamp")


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: User = Field(..., description="Authenticated user information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str = Field(..., description="Refresh token")


class TokenVerifyRequest(BaseModel):
    """Token verification request model"""
    token: str = Field(..., description="JWT token to verify")


class TokenVerifyResponse(BaseModel):
    """Token verification response model"""
    valid: bool = Field(..., description="Whether token is valid")
    payload: Optional[TokenData] = Field(None, description="Decoded token payload")
    message: Optional[str] = Field(None, description="Verification message")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error code or type")
    detail: str = Field(..., description="Detailed error message")
    timestamp: Optional[datetime] = Field(None, description="When error occurred")
