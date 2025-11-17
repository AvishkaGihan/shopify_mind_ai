"""
Utility functions and helpers for ShopifyMind AI backend.

Includes:
- Logging utilities
- Error handling
- Data validation
- Common helper functions
"""

from .logger import get_logger, setup_logging
from .error_handler import (
    AppException,
    ValidationException,
    AuthenticationException,
    NotFoundException,
    handle_exceptions,
)
from .validators import (
    validate_email,
    validate_password,
    validate_csv_row,
    sanitize_input,
)

__all__ = [
    # Logger
    "get_logger",
    "setup_logging",
    # Error handling
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "NotFoundException",
    "handle_exceptions",
    # Validators
    "validate_email",
    "validate_password",
    "validate_csv_row",
    "sanitize_input",
]  # Utils package initialization
