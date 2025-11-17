"""
User-related request/response schemas.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from app.models.user import StoreColors


class UserSignupRequest(BaseModel):
    """Request schema for user signup"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    store_name: Optional[str] = Field(
        None, max_length=255, description="Store name (optional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "store@example.com",
                "password": "SecurePass123",
                "store_name": "My Awesome Store",
            }
        }


class UserLoginRequest(BaseModel):
    """Request schema for user login"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {"email": "store@example.com", "password": "SecurePass123"}
        }


class TokenResponse(BaseModel):
    """Response schema for authentication with JWT token"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "store@example.com",
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "expires_in": 604800,
                },
                "message": "Login successful",
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class UserResponse(BaseModel):
    """Response schema for user data"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "store@example.com",
                    "store_name": "My Awesome Store",
                    "store_colors": {
                        "primary": "#00a86b",
                        "accent": "#f97316",
                        "supporting": "#a78bfa",
                    },
                    "ai_tone": "friendly",
                },
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class PasswordResetRequest(BaseModel):
    """Request schema for password reset"""

    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {"example": {"email": "store@example.com"}}


class PasswordResetConfirm(BaseModel):
    """Request schema for password reset confirmation"""

    reset_token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reset_token": "abc123def456",
                "new_password": "NewSecurePass123",
            }
        }


class UpdateStoreSettingsRequest(BaseModel):
    """Request schema for updating store settings"""

    store_name: Optional[str] = Field(None, max_length=255)
    store_colors: Optional[StoreColors] = None
    ai_tone: Optional[str] = Field(None, max_length=50)

    @validator("ai_tone")
    def validate_ai_tone(cls, v):
        """Validate AI tone is one of allowed values"""
        if v is not None:
            allowed_tones = ["friendly", "professional", "casual", "energetic"]
            if v not in allowed_tones:
                raise ValueError(f'AI tone must be one of: {", ".join(allowed_tones)}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "store_name": "Updated Store Name",
                "store_colors": {
                    "primary": "#00a86b",
                    "accent": "#f97316",
                    "supporting": "#a78bfa",
                },
                "ai_tone": "professional",
            }
        }


class StandardResponse(BaseModel):
    """Standard success response format"""

    success: bool = Field(default=True)
    data: Optional[Dict[str, Any]] = Field(default=None)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)


class ErrorResponse(BaseModel):
    """Standard error response format"""

    success: bool = Field(default=False)
    error: str = Field(...)
    code: str = Field(...)
    details: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid email or password",
                "code": "AUTH_INVALID_CREDENTIALS",
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


__all__ = [
    "UserSignupRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "UpdateStoreSettingsRequest",
    "StandardResponse",
    "ErrorResponse",
]
