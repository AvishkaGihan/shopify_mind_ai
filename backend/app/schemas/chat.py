"""
Chat-related request/response schemas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message"""

    message: str = Field(
        ..., min_length=1, max_length=2000, description="Customer message"
    )
    customer_identifier: Optional[str] = Field(
        None,
        max_length=255,
        description="Customer identifier (email, session ID, etc.)",
    )
    session_id: Optional[str] = Field(
        None, max_length=255, description="Session identifier for grouping messages"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Do you have wireless headphones?",
                "customer_identifier": "customer@example.com",
                "session_id": "sess_abc123",
            }
        }


class ProductCard(BaseModel):
    """Schema for product card in chat response"""

    id: str = Field(..., description="Product UUID")
    name: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., description="Product price")
    category: Optional[str] = Field(None, description="Product category")
    image_url: Optional[str] = Field(None, description="Product image URL")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 129.99,
                "category": "Electronics",
                "image_url": "https://example.com/image.jpg",
            }
        }


class ChatMessageResponse(BaseModel):
    """Response schema for chat message"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "customer_message": "Do you have wireless headphones?",
                    "ai_response": "Yes! We have several wireless headphones available...",
                    "products": [
                        {
                            "id": "prod_123",
                            "name": "Wireless Headphones",
                            "price": 129.99,
                            "image_url": "https://example.com/image.jpg",
                        }
                    ],
                    "intent_detected": "product_inquiry",
                    "response_time_ms": 1523,
                },
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "conversations": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "message": "Do you have wireless headphones?",
                            "response": "Yes! We have several options...",
                            "timestamp": "2025-11-15T10:30:00Z",
                        }
                    ],
                    "total_count": 47,
                    "page": 1,
                    "page_size": 20,
                    "has_more": True,
                },
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class ChatHistoryRequest(BaseModel):
    """Request schema for chat history"""

    customer_identifier: Optional[str] = Field(
        None, max_length=255, description="Filter by customer"
    )
    limit: int = Field(default=20, ge=1, le=100, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_identifier": "customer@example.com",
                "limit": 20,
                "offset": 0,
            }
        }


class OrderLookupRequest(BaseModel):
    """Request schema for order lookup via chat"""

    query: str = Field(
        ..., min_length=3, max_length=255, description="Order ID or customer email"
    )

    class Config:
        json_schema_extra = {"example": {"query": "ORD-12345"}}


class OrderStatusCard(BaseModel):
    """Schema for order status card in chat"""

    order_id: str = Field(..., description="Order number")
    customer_email: str = Field(..., description="Customer email")
    items: List[Dict[str, Any]] = Field(..., description="Order items")
    total: float = Field(..., description="Total amount")
    status: str = Field(..., description="Order status")
    status_color: str = Field(..., description="Status badge color")
    estimated_delivery: Optional[str] = Field(
        None, description="Estimated delivery date"
    )
    tracking_number: Optional[str] = Field(None, description="Tracking number")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORD-12345",
                "customer_email": "customer@example.com",
                "items": [
                    {"name": "Wireless Headphones", "quantity": 2, "price": 129.99}
                ],
                "total": 293.38,
                "status": "shipped",
                "status_color": "#2196F3",
                "estimated_delivery": "2025-11-20T17:00:00Z",
                "tracking_number": "TRK1234567890",
            }
        }


__all__ = [
    "ChatMessageRequest",
    "ProductCard",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "ChatHistoryRequest",
    "OrderLookupRequest",
    "OrderStatusCard",
]
