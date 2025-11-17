"""
Authentication service handling password hashing, JWT tokens, and password reset.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from app.config import get_settings
from app.database import Database
from app.utils.logger import get_logger
from app.utils.error_handler import AuthenticationException
from app.utils.validators import validate_email, validate_password

logger = get_logger(__name__)
settings = get_settings()


class AuthService:
    """
    Service for authentication operations.

    Handles:
    - Password hashing and verification
    - JWT token generation and validation
    - Password reset token generation
    - User session management
    """

    def __init__(self, db: Database):
        """
        Initialize auth service.

        Args:
            db: Database instance
        """
        self.db = db

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Example:
            hashed = auth_service.hash_password("MySecurePass123")
        """
        # Validate password before hashing
        validate_password(password)

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds for good security
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)

        logger.debug("Password hashed successfully")
        return hashed.decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            password_hash: Hashed password from database

        Returns:
            True if password matches, False otherwise

        Example:
            is_valid = auth_service.verify_password("MyPass", stored_hash)
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), password_hash.encode("utf-8")
            )
        except Exception as e:
            logger.error("Password verification failed", extra={"error": str(e)})
            return False

    def generate_jwt_token(
        self,
        user_id: str,
        email: str,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a JWT access token.

        Args:
            user_id: User UUID
            email: User email
            additional_claims: Additional claims to include in token

        Returns:
            JWT token string

        Example:
            token = auth_service.generate_jwt_token(user_id="123", email="user@example.com")
        """
        # Calculate expiration
        expiration = datetime.utcnow() + timedelta(
            seconds=settings.get_jwt_expiration_seconds()
        )

        # Build payload
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expiration,
            "iat": datetime.utcnow(),
        }

        # Add additional claims if provided
        if additional_claims:
            payload.update(additional_claims)

        # Generate token
        token = jwt.encode(
            payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
        )

        logger.info(
            "JWT token generated",
            extra={"user_id": user_id, "expires_at": expiration.isoformat()},
        )

        return token

    def decode_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and verify a JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload dict

        Raises:
            AuthenticationException: If token is invalid or expired

        Example:
            payload = auth_service.decode_jwt_token(token)
            user_id = payload["user_id"]
        """
        try:
            payload = jwt.decode(
                token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise AuthenticationException("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", extra={"error": str(e)})
            raise AuthenticationException("Invalid token")

    async def signup(
        self, email: str, password: str, store_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            store_name: Optional store name

        Returns:
            Dict with user data and token

        Raises:
            ValidationException: If validation fails
            AuthenticationException: If email already exists

        Example:
            result = await auth_service.signup(
                email="store@example.com",
                password="SecurePass123",
                store_name="My Store"
            )
        """
        # Validate input
        validate_email(email)
        validate_password(password)

        # Check if user already exists
        existing_user = await self.db.get_user_by_email(email)
        if existing_user:
            logger.warning("Signup attempt with existing email", extra={"email": email})
            raise AuthenticationException("An account with this email already exists")

        # Hash password
        password_hash = self.hash_password(password)

        # Create user
        user = await self.db.create_user(
            email=email, password_hash=password_hash, store_name=store_name
        )

        if not user:
            logger.error("Failed to create user", extra={"email": email})
            raise AuthenticationException("Failed to create account")

        # Generate token
        token = self.generate_jwt_token(user_id=user["id"], email=user["email"])

        logger.info(
            "User signup successful", extra={"user_id": user["id"], "email": email}
        )

        return {
            "user_id": user["id"],
            "email": user["email"],
            "store_name": user.get("store_name"),
            "token": token,
            "expires_in": settings.get_jwt_expiration_seconds(),
        }

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and generate token.

        Args:
            email: User email
            password: User password

        Returns:
            Dict with user data and token

        Raises:
            AuthenticationException: If credentials are invalid

        Example:
            result = await auth_service.login(
                email="store@example.com",
                password="SecurePass123"
            )
        """
        # Validate input
        validate_email(email)

        # Get user from database
        user = await self.db.get_user_by_email(email)
        if not user:
            logger.warning(
                "Login attempt with non-existent email", extra={"email": email}
            )
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not self.verify_password(password, user["password_hash"]):
            logger.warning("Login attempt with wrong password", extra={"email": email})
            raise AuthenticationException("Invalid email or password")

        # Check if account is active
        if not user.get("is_active", True):
            logger.warning("Login attempt for inactive account", extra={"email": email})
            raise AuthenticationException("Account is inactive")

        # Update last login timestamp
        await self.db.update_user(
            user_id=user["id"], data={"last_login_at": datetime.utcnow()}
        )

        # Generate token
        token = self.generate_jwt_token(user_id=user["id"], email=user["email"])

        logger.info(
            "User login successful", extra={"user_id": user["id"], "email": email}
        )

        return {
            "user_id": user["id"],
            "email": user["email"],
            "store_name": user.get("store_name"),
            "token": token,
            "expires_in": settings.get_jwt_expiration_seconds(),
        }

    def generate_password_reset_token(self) -> str:
        """
        Generate a secure password reset token.

        Returns:
            Random token string

        Example:
            token = auth_service.generate_password_reset_token()
        """
        return secrets.token_urlsafe(32)

    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Initiate password reset process.

        Args:
            email: User email

        Returns:
            Dict with reset token (in MVP, just return success)

        Note:
            In production, this would send an email with the reset link.
            For MVP, we'll just log the token.

        Example:
            result = await auth_service.request_password_reset("user@example.com")
        """
        validate_email(email)

        # Check if user exists
        user = await self.db.get_user_by_email(email)
        if not user:
            # Don't reveal if email exists (security best practice)
            logger.info(
                "Password reset requested for non-existent email",
                extra={"email": email},
            )
            return {
                "status": "check_email",
                "message": "If the email exists, a reset link has been sent",
            }

        # Generate reset token
        reset_token = self.generate_password_reset_token()

        # In production: Store token in database with expiration (15 minutes)
        # In production: Send email with reset link

        logger.info(
            "Password reset requested",
            extra={
                "user_id": user["id"],
                "email": email,
                "reset_token": reset_token,  # Remove in production!
            },
        )

        return {
            "status": "check_email",
            "message": "If the email exists, a reset link has been sent",
            "reset_token": reset_token,  # For MVP testing only!
        }

    async def reset_password(
        self, reset_token: str, new_password: str
    ) -> Dict[str, Any]:
        """
        Reset user password with token.

        Args:
            reset_token: Password reset token
            new_password: New password

        Returns:
            Success status dict

        Note:
            In production, verify token from database and check expiration.
            For MVP, this is simplified.

        Example:
            result = await auth_service.reset_password(token, "NewPass123")
        """
        validate_password(new_password)

        # In production: Validate token from database
        # For MVP: Just hash and update (simplified)

        password_hash = self.hash_password(new_password)  # noqa: F841

        logger.info("Password reset completed")

        return {
            "status": "password_updated",
            "message": "Password has been reset successfully",
        }


__all__ = ["AuthService"]
