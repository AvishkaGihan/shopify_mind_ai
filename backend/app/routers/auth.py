"""
Authentication router handling user signup, login, and password management.
"""

from fastapi import APIRouter, Depends, status
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserSignupRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    PasswordResetRequest,
    StandardResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"},
    },
)


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new store owner",
    description="Create a new user account with email and password. Returns JWT token for authentication.",
)
async def signup(request: UserSignupRequest, db: Database = Depends(get_database)):
    """
    Register a new store owner account.

    - **email**: Valid email address (unique)
    - **password**: Minimum 8 characters
    - **store_name**: Optional store name

    Returns JWT token with 7-day expiration.
    """
    auth_service = AuthService(db)

    result = await auth_service.signup(
        email=request.email, password=request.password, store_name=request.store_name
    )

    return TokenResponse(
        success=True,
        data=result,
        message="Account created successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticate user and return JWT token.",
)
async def login(request: UserLoginRequest, db: Database = Depends(get_database)):
    """
    Login with email and password.

    - **email**: User email address
    - **password**: User password

    Returns JWT token with 7-day expiration.
    """
    auth_service = AuthService(db)

    result = await auth_service.login(email=request.email, password=request.password)

    return TokenResponse(
        success=True,
        data=result,
        message="Login successful",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.post(
    "/logout",
    response_model=StandardResponse,
    summary="Logout current user",
    description="Logout user (client should discard token).",
)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user.

    Note: Since we use stateless JWT, the client should simply discard the token.
    For additional security in production, implement token blacklisting.
    """
    logger.info("User logged out", extra={"user_id": current_user["id"]})

    return StandardResponse(
        success=True,
        message="Logged out successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information.",
)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Returns user information including:
    - User ID
    - Email
    - Store name
    - Store colors
    - AI tone
    """
    return UserResponse(
        success=True,
        data={
            "id": current_user["id"],
            "email": current_user["email"],
            "store_name": current_user.get("store_name"),
            "store_colors": current_user.get(
                "store_colors",
                {"primary": "#00a86b", "accent": "#f97316", "supporting": "#a78bfa"},
            ),
            "ai_tone": current_user.get("ai_tone", "friendly"),
            "created_at": current_user.get("created_at"),
        },
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.post(
    "/reset-password",
    response_model=StandardResponse,
    summary="Request password reset",
    description="Request a password reset email (MVP: returns token directly).",
)
async def request_password_reset(
    request: PasswordResetRequest, db: Database = Depends(get_database)
):
    """
    Request password reset.

    - **email**: User email address

    In production, this would send an email with reset link.
    For MVP, the reset token is returned in response.
    """
    auth_service = AuthService(db)

    result = await auth_service.request_password_reset(request.email)

    return StandardResponse(
        success=True,
        data=result,
        message="If the email exists, a reset link has been sent",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/health",
    response_model=StandardResponse,
    summary="Auth service health check",
    description="Check if authentication service is operational.",
)
async def auth_health_check():
    """Health check for authentication service."""
    return StandardResponse(
        success=True,
        data={"status": "healthy"},
        message="Authentication service is operational",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


__all__ = ["router"]
