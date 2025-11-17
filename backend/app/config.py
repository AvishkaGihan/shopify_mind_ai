"""
Configuration management for ShopifyMind AI backend.

Handles environment variables and application settings using Pydantic.
All sensitive data loaded from .env file (never committed to git).
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses pydantic-settings to validate and parse .env file.
    All values have defaults except sensitive credentials.
    """

    # ==========================================
    # Application Configuration
    # ==========================================
    app_name: str = "ShopifyMind AI"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_version: str = Field(default="v1", description="API version prefix")

    # ==========================================
    # Supabase Configuration
    # ==========================================
    supabase_url: Optional[str] = Field(
        default=None, description="Supabase project URL"
    )
    supabase_key: Optional[str] = Field(
        default=None, description="Supabase service role key"
    )
    supabase_anon_key: Optional[str] = Field(
        default=None, description="Supabase anon public key"
    )

    # ==========================================
    # JWT Authentication
    # ==========================================
    jwt_secret: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="JWT signing secret",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_days: int = Field(default=7, description="JWT expiration in days")

    # ==========================================
    # Google Gemini API
    # ==========================================
    gemini_api_key: Optional[str] = Field(
        default=None, description="Google Gemini API key"
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash", description="Gemini model to use"
    )
    gemini_temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Gemini temperature (0-1)"
    )
    gemini_max_tokens: int = Field(
        default=1000, ge=100, le=8000, description="Maximum tokens for Gemini response"
    )

    # ==========================================
    # CORS Configuration
    # ==========================================
    cors_origins: List[str] = Field(
        default=["*"], description="Allowed CORS origins (comma-separated in .env)"
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins from .env"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ==========================================
    # File Upload Configuration
    # ==========================================
    max_upload_size_mb: int = Field(
        default=10, description="Maximum CSV upload size in MB"
    )
    max_products_per_upload: int = Field(
        default=1000, description="Maximum products per CSV upload"
    )

    # ==========================================
    # Rate Limiting (optional)
    # ==========================================
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(
        default=60, description="Requests per minute per IP"
    )

    # ==========================================
    # Logging Configuration
    # ==========================================
    log_level: str = Field(
        default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    log_format: str = Field(default="json", description="Log format (json or text)")

    # ==========================================
    # Email Configuration (optional)
    # ==========================================
    smtp_host: Optional[str] = Field(default=None, description="SMTP server host")
    smtp_port: Optional[int] = Field(default=587, description="SMTP server port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_from: Optional[str] = Field(default=None, description="From email address")

    # ==========================================
    # Sentry (optional)
    # ==========================================
    sentry_dsn: Optional[str] = Field(
        default=None, description="Sentry DSN for error tracking"
    )
    sentry_environment: str = Field(
        default="development", description="Sentry environment name"
    )

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_max_upload_size_bytes(self) -> int:
        """Convert max upload size from MB to bytes"""
        return self.max_upload_size_mb * 1024 * 1024

    def get_jwt_expiration_seconds(self) -> int:
        """Convert JWT expiration from days to seconds"""
        return self.jwt_expiration_days * 24 * 60 * 60


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    This prevents reading .env file on every request.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience function for importing
settings = get_settings()


# Export for easy imports
__all__ = ["Settings", "get_settings", "settings"]
