"""
Pydantic schemas for request/response validation.

Schemas define the shape of data coming in (requests) and going out (responses).
They are separate from models to allow different validation rules for API vs database.
"""

from .user import (
    UserSignupRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    UpdateStoreSettingsRequest,
)
from .product import (
    ProductUploadResponse,
    ProductListResponse,
    ProductResponse,
)
from .chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
)

__all__ = [
    # User schemas
    "UserSignupRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "PasswordResetRequest",
    "UpdateStoreSettingsRequest",
    # Product schemas
    "ProductUploadResponse",
    "ProductListResponse",
    "ProductResponse",
    # Chat schemas
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
]
