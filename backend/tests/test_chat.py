"""
Tests for chat and AI response endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    # Signup and login
    client.post(
        "/auth/signup",
        json={
            "email": "chattest@example.com",
            "password": "SecurePass123",
            "store_name": "Chat Test Store",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "chattest@example.com", "password": "SecurePass123"},
    )

    return response.json()["data"]["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Fixture to get authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestChatEndpoints:
    """Test suite for chat endpoints"""

    @patch("app.services.gemini_service.GeminiService.generate_response")
    def test_send_message_success(self, mock_generate, auth_headers):
        """Test sending a chat message successfully"""
        # Mock AI response
        mock_generate.return_value = {
            "ai_response": "Yes, we have wireless headphones available!",
            "intent_detected": "product_inquiry",
            "products_referenced": [],
            "response_time_ms": 1500,
        }

        response = client.post(
            "/chat/message",
            headers=auth_headers,
            json={
                "message": "Do you have wireless headphones?",
                "customer_identifier": "test@example.com",
                "session_id": "session_123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "ai_response" in data["data"]
        assert "intent_detected" in data["data"]

    def test_send_message_empty(self, auth_headers):
        """Test sending empty message"""
        response = client.post(
            "/chat/message", headers=auth_headers, json={"message": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_send_message_too_long(self, auth_headers):
        """Test sending message that's too long"""
        long_message = "x" * 2001  # Over 2000 char limit

        response = client.post(
            "/chat/message", headers=auth_headers, json={"message": long_message}
        )

        assert response.status_code == 422  # Validation error

    def test_get_chat_history(self, auth_headers):
        """Test getting chat history"""
        response = client.get("/chat/history", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "conversations" in data["data"]
        assert "total_count" in data["data"]

    def test_get_chat_history_pagination(self, auth_headers):
        """Test chat history pagination"""
        response = client.get("/chat/history?limit=10&offset=0", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["conversations"]) <= 10

    def test_get_chat_history_filter_by_customer(self, auth_headers):
        """Test filtering chat history by customer"""
        response = client.get(
            "/chat/history?customer_identifier=test@example.com", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_clear_chat_history(self, auth_headers):
        """Test clearing chat history"""
        response = client.delete("/chat/history", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_send_message_no_auth(self):
        """Test sending message without authentication"""
        response = client.post("/chat/message", json={"message": "Hello"})

        assert response.status_code == 403  # Forbidden


class TestGeminiService:
    """Test suite for GeminiService methods"""

    def test_intent_detection_product_inquiry(self):
        """Test intent detection for product inquiry"""
        from app.services.gemini_service import GeminiService
        from app.database import get_database

        db = get_database()
        gemini_service = GeminiService(db)

        intent = gemini_service._detect_intent(
            "Do you have wireless headphones?", "Yes, we have several models..."
        )

        assert intent == "product_inquiry"

    def test_intent_detection_order_lookup(self):
        """Test intent detection for order lookup"""
        from app.services.gemini_service import GeminiService
        from app.database import get_database

        db = get_database()
        gemini_service = GeminiService(db)

        intent = gemini_service._detect_intent(
            "Where is my order ORD-12345?", "Let me look that up..."
        )

        assert intent == "order_lookup"

    def test_product_reference_extraction(self):
        """Test extracting product references from AI response"""
        from app.services.gemini_service import GeminiService
        from app.database import get_database

        db = get_database()
        gemini_service = GeminiService(db)

        products = [
            {"id": "123", "name": "Wireless Headphones"},
            {"id": "456", "name": "Smart Watch"},
        ]

        ai_response = "We have Wireless Headphones available for $129.99"

        referenced_ids = gemini_service._extract_product_references(
            ai_response, products
        )

        assert "123" in referenced_ids
        assert "456" not in referenced_ids

    @patch("httpx.AsyncClient.post")
    async def test_gemini_api_call(self, mock_post):
        """Test calling Gemini API"""
        from app.services.gemini_service import GeminiService
        from app.database import get_database

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "This is a test response"}]}}
            ]
        }
        mock_post.return_value = mock_response

        db = get_database()
        gemini_service = GeminiService(db)

        result = await gemini_service._call_gemini_api("Test prompt")

        assert result is not None
        assert "candidates" in result


class TestAnalyticsIntegration:
    """Test suite for analytics integration with chat"""

    @patch("app.services.gemini_service.GeminiService.generate_response")
    def test_analytics_event_logged(self, mock_generate, auth_headers):
        """Test that analytics events are logged for chat messages"""
        # Mock AI response
        mock_generate.return_value = {
            "ai_response": "Test response",
            "intent_detected": "product_inquiry",
            "products_referenced": [],
            "response_time_ms": 1500,
        }

        # Send message
        response = client.post(
            "/chat/message",
            headers=auth_headers,
            json={"message": "Test message", "session_id": "test_session"},
        )

        assert response.status_code == 201

        # Check that analytics can be retrieved
        analytics_response = client.get(
            "/analytics/summary?days=1", headers=auth_headers
        )

        assert analytics_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
