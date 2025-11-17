"""
Structured logging configuration for ShopifyMind AI.

Uses structlog for structured, JSON-formatted logging with:
- Timestamp
- Log level
- Module name
- Extra context
- Pretty printing in development
"""

import logging
import sys
from typing import Any, Dict, Optional
import structlog
from app.config import get_settings

settings = get_settings()


def setup_logging():
    """
    Configure structured logging for the application.

    Sets up structlog with appropriate processors for
    development (human-readable) and production (JSON).

    Call this once at application startup.
    """
    # Set log level from config
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Configure structlog processors
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate final processor based on format
    if settings.log_format == "json":
        # Production: JSON format for easy parsing
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development: Pretty console output
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        BoundLogger: Structured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("User logged in", user_id="123", email="user@example.com")
        logger.error("Database error", error=str(e), table="users")
    """
    return structlog.get_logger(name)


class RequestLogger:
    """
    Middleware for logging HTTP requests and responses.

    Use with FastAPI middleware to automatically log all API requests.
    """

    def __init__(self, logger_name: str = "api.requests"):
        self.logger = get_logger(logger_name)

    async def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
        error: Optional[str] = None,
        **extra,
    ):
        """
        Log HTTP request with context.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            user_id: Authenticated user ID (if any)
            error: Error message (if failed)
            **extra: Additional context to log
        """
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            **extra,
        }

        if user_id:
            log_data["user_id"] = user_id

        if error:
            log_data["error"] = error
            self.logger.error("Request failed", **log_data)
        elif status_code >= 400:
            self.logger.warning("Request error", **log_data)
        else:
            self.logger.info("Request completed", **log_data)


def log_database_query(
    operation: str,
    table: str,
    duration_ms: float,
    rows_affected: Optional[int] = None,
    error: Optional[str] = None,
    **extra,
):
    """
    Log database query for monitoring performance.

    Args:
        operation: SQL operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration in milliseconds
        rows_affected: Number of rows affected
        error: Error message if query failed
        **extra: Additional context

    Example:
        log_database_query(
            operation="SELECT",
            table="products",
            duration_ms=12.5,
            rows_affected=100,
            user_id="123"
        )
    """
    logger = get_logger("database")

    log_data = {
        "operation": operation,
        "table": table,
        "duration_ms": round(duration_ms, 2),
        **extra,
    }

    if rows_affected is not None:
        log_data["rows_affected"] = rows_affected

    if error:
        log_data["error"] = error
        logger.error("Database query failed", **log_data)
    elif duration_ms > 1000:  # Slow query threshold
        logger.warning("Slow database query", **log_data)
    else:
        logger.debug("Database query executed", **log_data)


def log_external_api_call(
    service: str,
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    error: Optional[str] = None,
    **extra,
):
    """
    Log external API calls (e.g., Gemini API).

    Args:
        service: Service name (e.g., "gemini", "sendgrid")
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration
        error: Error message if failed
        **extra: Additional context

    Example:
        log_external_api_call(
            service="gemini",
            endpoint="/v1/models/gemini-1.5-flash:generateContent",
            method="POST",
            status_code=200,
            duration_ms=1523.4,
            user_id="123"
        )
    """
    logger = get_logger("external_api")

    log_data = {
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **extra,
    }

    if error:
        log_data["error"] = error
        logger.error(f"{service} API call failed", **log_data)
    elif status_code >= 400:
        logger.warning(f"{service} API error", **log_data)
    elif duration_ms > 5000:  # Slow API threshold
        logger.warning(f"Slow {service} API call", **log_data)
    else:
        logger.info(f"{service} API call completed", **log_data)


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive fields in log data.

    Args:
        data: Dictionary with potentially sensitive data

    Returns:
        Dictionary with sensitive fields masked

    Example:
        data = {"email": "user@example.com", "password": "secret123"}
        masked = mask_sensitive_data(data)
        # {"email": "user@example.com", "password": "***"}
    """
    sensitive_fields = {
        "password",
        "password_hash",
        "token",
        "api_key",
        "secret",
        "credit_card",
        "ssn",
    }

    masked = data.copy()
    for key in masked:
        if any(field in key.lower() for field in sensitive_fields):
            masked[key] = "***"

    return masked


# Initialize logging on module import
setup_logging()


# Export for easy imports
__all__ = [
    "setup_logging",
    "get_logger",
    "RequestLogger",
    "log_database_query",
    "log_external_api_call",
    "mask_sensitive_data",
]
