"""
User model representing store owner accounts.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


class StoreColors(BaseModel):
    """Store brand colors configuration"""

    primary: str = Field(default="#00a86b", description="Primary brand color (hex)")
    accent: str = Field(default="#f97316", description="Accent color (hex)")
    supporting: str = Field(default="#a78bfa", description="Supporting color (hex)")

    @validator("primary", "accent", "supporting")
    def validate_hex_color(cls, v):
        """Validate hex color format"""
        if not v.startswith("#") or len(v) not in [4, 7]:
            raise ValueError("Invalid hex color format")
        return v.lower()


class User(BaseModel):
    """
    User model representing a store owner.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique)
        password_hash: Bcrypt hashed password
        store_name: Display name for the store
        store_colors: Brand colors configuration
        ai_tone: AI personality tone
        is_active: Account active status
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last successful login timestamp
    """

    id: Optional[str] = Field(None, description="User UUID")
    email: EmailStr = Field(..., description="User email address")
    password_hash: Optional[str] = Field(None, description="Bcrypt hashed password")
    store_name: Optional[str] = Field(None, max_length=255, description="Store name")
    store_colors: StoreColors = Field(
        default_factory=StoreColors, description="Store brand colors"
    )
    ai_tone: str = Field(default="friendly", description="AI personality tone")
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="Email verified status")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    @validator("ai_tone")
    def validate_ai_tone(cls, v):
        """Validate AI tone is one of allowed values"""
        allowed_tones = ["friendly", "professional", "casual", "energetic"]
        if v not in allowed_tones:
            raise ValueError(f'AI tone must be one of: {", ".join(allowed_tones)}')
        return v

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "store@example.com",
                "store_name": "My Awesome Store",
                "store_colors": {
                    "primary": "#00a86b",
                    "accent": "#f97316",
                    "supporting": "#a78bfa",
                },
                "ai_tone": "friendly",
                "is_active": True,
                "is_verified": True,
            }
        }

    def to_dict(self, exclude_password: bool = True) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Args:
            exclude_password: Whether to exclude password_hash

        Returns:
            Dictionary representation
        """
        data = self.model_dump()
        if exclude_password and "password_hash" in data:
            del data["password_hash"]
        return data

    def to_public_dict(self) -> Dict[str, Any]:
        """
        Convert to public-safe dictionary (no sensitive data).

        Returns:
            Public dictionary with safe fields only
        """
        return {
            "id": self.id,
            "email": self.email,
            "store_name": self.store_name,
            "store_colors": self.store_colors.model_dump(),
            "ai_tone": self.ai_tone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserInDB(User):
    """User model with password hash (for internal use only)"""

    password_hash: str = Field(..., description="Bcrypt hashed password")


__all__ = ["User", "UserInDB", "StoreColors"]
