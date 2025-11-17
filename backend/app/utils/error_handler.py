"""
Error handling utilities and custom exceptions.

Provides:
- Custom exception classes
- Standardized error responses
- Exception handlers for FastAPI
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """
    Base application exception.

    All custom exceptions should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            code: Error code for client handling
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        return {
            "success": False,
            "error": self.message,
            "code": self.code,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


class ValidationException(AppException):
    """Exception for validation errors"""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationException(AppException):
    """Exception for authentication errors"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTH_ERROR",
            details=details,
        )


class AuthorizationException(AppException):
    """Exception for authorization errors"""

    def __init__(
        self,
        message: str = "You don't have permission to access this resource",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
            details=details,
        )


class NotFoundException(AppException):
    """Exception for resource not found errors"""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            details=details,
        )


class DatabaseException(AppException):
    """Exception for database errors"""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            details=details,
        )


class ExternalAPIException(AppException):
    """Exception for external API errors"""

    def __init__(
        self,
        message: str = "External API request failed",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if service:
            error_details["service"] = service

        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="EXTERNAL_API_ERROR",
            details=error_details,
        )


class RateLimitException(AppException):
    """Exception for rate limit errors"""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None,
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after

        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class FileUploadException(AppException):
    """Exception for file upload errors"""

    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="FILE_UPLOAD_ERROR",
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom AppException and subclasses.

    Args:
        request: FastAPI request
        exc: AppException instance

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Application exception: {exc.code}",
        extra={
            "code": exc.code,
            "message": exc.message,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details,
        },
    )

    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException.

    Args:
        request: FastAPI request
        exc: HTTPException instance

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        f"HTTP exception: {exc.status_code}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: RequestValidationError instance

    Returns:
        JSONResponse with validation error details
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": {"errors": errors},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Exception instance

    Returns:
        JSONResponse with generic error message
    """
    # Log full traceback for debugging
    error_traceback = traceback.format_exc()

    logger.error(
        "Unhandled exception",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "traceback": error_traceback,
        },
    )

    # Return generic error to client (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected error occurred. Please try again later.",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


def handle_exceptions(app):
    """
    Register exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        from app.utils.error_handler import handle_exceptions

        app = FastAPI()
        handle_exceptions(app)
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered")


# Export for easy imports
__all__ = [
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "DatabaseException",
    "ExternalAPIException",
    "RateLimitException",
    "FileUploadException",
    "handle_exceptions",
]
