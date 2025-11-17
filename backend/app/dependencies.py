"""
FastAPI dependency injection functions.

Provides reusable dependencies for:
- Authentication (JWT token validation)
- Database access
- Current user extraction
- Rate limiting
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

from app.config import get_settings
from app.database import get_database, Database
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_db() -> Database:
    """
    Get database instance.

    FastAPI dependency for database access.

    Returns:
        Database: Database instance

    Example:
        @app.get("/users")
        async def get_users(db: Database = Depends(get_db)):
            return await db.execute_query("users", "select")
    """
    return get_database()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Verify JWT token and extract payload.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        Token payload dict with user_id, email, etc.

    Raises:
        HTTPException: If token is invalid or expired

    Example:
        @app.get("/protected")
        async def protected_route(token_data: dict = Depends(verify_token)):
            user_id = token_data["user_id"]
            return {"user_id": user_id}
    """
    token = credentials.credentials

    try:
        # Decode and verify token
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("Token expired", extra={"user_id": payload.get("user_id")})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(
            "Token verified successfully", extra={"user_id": payload.get("user_id")}
        )

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid token", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Token verification failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_data: Dict[str, Any] = Depends(verify_token), db: Database = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current authenticated user from database.

    Args:
        token_data: Verified token payload
        db: Database instance

    Returns:
        User dict with all user data

    Raises:
        HTTPException: If user not found or inactive

    Example:
        @app.get("/me")
        async def get_me(user: dict = Depends(get_current_user)):
            return {"email": user["email"], "store_name": user["store_name"]}
    """
    user_id = token_data.get("user_id")
    if not user_id:
        logger.error("No user_id in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    # Get user from database
    user = await db.get_user_by_id(user_id)

    if not user:
        logger.warning("User not found", extra={"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.get("is_active", True):
        logger.warning("User inactive", extra={"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    logger.debug(
        "Current user retrieved", extra={"user_id": user_id, "email": user.get("email")}
    )

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None), db: Database = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise None.

    Useful for optional authentication endpoints where
    behavior changes based on whether user is logged in.

    Args:
        authorization: Authorization header (optional)
        db: Database instance

    Returns:
        User dict if authenticated, None otherwise

    Example:
        @app.get("/products")
        async def get_products(user: dict = Depends(get_optional_user)):
            if user:
                # Return user's products
                return await get_user_products(user["id"])
            else:
                # Return public products
                return await get_public_products()
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user = await db.get_user_by_id(user_id)
        return user if user and user.get("is_active", True) else None

    except Exception as e:
        logger.debug("Optional auth failed", extra={"error": str(e)})
        return None


class RateLimiter:
    """
    Simple in-memory rate limiter.

    For production, use Redis-based rate limiting.
    """

    def __init__(self):
        self.requests: Dict[str, list] = {}

    def is_allowed(
        self, identifier: str, max_requests: int, window_seconds: int
    ) -> bool:
        """
        Check if request is allowed based on rate limit.

        Args:
            identifier: Unique identifier (IP address, user_id, etc.)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.utcnow().timestamp()

        if identifier not in self.requests:
            self.requests[identifier] = []

        # Remove old requests outside window
        self.requests[identifier] = [
            timestamp
            for timestamp in self.requests[identifier]
            if now - timestamp < window_seconds
        ]

        # Check if under limit
        if len(self.requests[identifier]) < max_requests:
            self.requests[identifier].append(now)
            return True

        return False


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def check_rate_limit(
    request_id: str, max_requests: int = 60, window_seconds: int = 60
):
    """
    Check rate limit for request.

    Args:
        request_id: Unique request identifier
        max_requests: Max requests in window
        window_seconds: Window size in seconds

    Raises:
        HTTPException: If rate limit exceeded

    Example:
        @app.get("/api")
        async def api_endpoint(_: None = Depends(check_rate_limit)):
            return {"message": "success"}
    """
    if not settings.rate_limit_enabled:
        return

    if not _rate_limiter.is_allowed(request_id, max_requests, window_seconds):
        logger.warning("Rate limit exceeded", extra={"identifier": request_id})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds.",
        )


# Export for easy imports
__all__ = [
    "get_db",
    "verify_token",
    "get_current_user",
    "get_optional_user",
    "check_rate_limit",
]
