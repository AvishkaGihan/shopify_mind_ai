"""
Tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    def test_signup_success(self):
        """Test successful user signup"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "testuser@example.com",
                "password": "SecurePass123",
                "store_name": "Test Store",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "token" in data["data"]
        assert data["data"]["email"] == "testuser@example.com"

    def test_signup_invalid_email(self):
        """Test signup with invalid email"""
        response = client.post(
            "/auth/signup", json={"email": "invalid-email", "password": "SecurePass123"}
        )

        assert response.status_code == 422  # Validation error

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        response = client.post(
            "/auth/signup", json={"email": "user@example.com", "password": "weak"}
        )

        assert response.status_code == 422  # Validation error

    def test_login_success(self):
        """Test successful login"""
        # First signup
        client.post(
            "/auth/signup",
            json={"email": "logintest@example.com", "password": "SecurePass123"},
        )

        # Then login
        response = client.post(
            "/auth/login",
            json={"email": "logintest@example.com", "password": "SecurePass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data["data"]

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/auth/login",
            json={"email": "logintest@example.com", "password": "WrongPassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "SomePassword123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_get_current_user(self):
        """Test getting current user profile"""
        # First login
        login_response = client.post(
            "/auth/login",
            json={"email": "logintest@example.com", "password": "SecurePass123"},
        )

        token = login_response.json()["data"]["token"]

        # Get profile
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "logintest@example.com"

    def test_get_current_user_no_token(self):
        """Test getting profile without token"""
        response = client.get("/auth/me")

        assert response.status_code == 403  # Forbidden

    def test_get_current_user_invalid_token(self):
        """Test getting profile with invalid token"""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401  # Unauthorized

    def test_logout(self):
        """Test logout endpoint"""
        # First login
        login_response = client.post(
            "/auth/login",
            json={"email": "logintest@example.com", "password": "SecurePass123"},
        )

        token = login_response.json()["data"]["token"]

        # Logout
        response = client.post(
            "/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_password_reset_request(self):
        """Test password reset request"""
        response = client.post(
            "/auth/reset-password", json={"email": "logintest@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # For MVP, token is returned in response
        assert "reset_token" in data["data"]


class TestAuthService:
    """Test suite for AuthService methods"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from app.services.auth_service import AuthService
        from app.database import get_database

        db = get_database()
        auth_service = AuthService(db)

        password = "TestPassword123"
        hashed = auth_service.hash_password(password)

        # Hash should be different from original
        assert hashed != password

        # Verification should work
        assert auth_service.verify_password(password, hashed) is True

        # Wrong password should fail
        assert auth_service.verify_password("WrongPassword", hashed) is False

    def test_jwt_token_generation(self):
        """Test JWT token generation and decoding"""
        from app.services.auth_service import AuthService
        from app.database import get_database

        db = get_database()
        auth_service = AuthService(db)

        user_id = "test-uuid-123"
        email = "test@example.com"

        # Generate token
        token = auth_service.generate_jwt_token(user_id, email)

        assert token is not None
        assert isinstance(token, str)

        # Decode token
        payload = auth_service.decode_jwt_token(token)

        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
