"""
Conversation model representing chat messages between customers and AI.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """
    Conversation model representing a chat message exchange.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Store owner UUID
        customer_identifier: Anonymous customer ID (email, session, etc.)
        customer_message: Customer's question or message
        ai_response: AI-generated response
        message_count: Sequential message number in conversation
        products_referenced: List of product IDs mentioned in response
        intent_detected: Detected customer intent
        sentiment_score: Customer sentiment (-1.0 to 1.0)
        response_time_ms: AI response time in milliseconds
        created_at: Message timestamp
    """

    id: Optional[str] = Field(None, description="Conversation UUID")
    user_id: str = Field(..., description="Store owner UUID")
    customer_identifier: Optional[str] = Field(
        None, max_length=255, description="Customer identifier"
    )
    customer_message: str = Field(..., description="Customer message")
    ai_response: str = Field(..., description="AI response")
    message_count: int = Field(default=1, ge=1, description="Message sequence number")
    products_referenced: List[str] = Field(
        default_factory=list, description="Product IDs mentioned"
    )
    intent_detected: Optional[str] = Field(
        None, max_length=100, description="Detected intent"
    )
    sentiment_score: Optional[float] = Field(
        None, ge=-1.0, le=1.0, description="Sentiment score"
    )
    response_time_ms: Optional[int] = Field(
        None, ge=0, description="Response time in ms"
    )
    created_at: Optional[datetime] = Field(None, description="Message timestamp")

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "customer_identifier": "customer@example.com",
                "customer_message": "Do you have wireless headphones?",
                "ai_response": "Yes! We have several wireless headphones available...",
                "message_count": 1,
                "products_referenced": ["123e4567-e89b-12d3-a456-426614174002"],
                "intent_detected": "product_inquiry",
                "sentiment_score": 0.8,
                "response_time_ms": 1523,
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation
        """
        return self.model_dump()

    def to_chat_dict(self) -> Dict[str, Any]:
        """
        Convert to chat display format.

        Returns:
            Dictionary formatted for chat UI
        """
        return {
            "id": self.id,
            "message": self.customer_message,
            "response": self.ai_response,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "products": self.products_referenced,
        }


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation message"""

    customer_identifier: Optional[str] = Field(None, max_length=255)
    customer_message: str = Field(...)
    ai_response: str = Field(...)
    message_count: int = Field(default=1, ge=1)
    products_referenced: List[str] = Field(default_factory=list)
    intent_detected: Optional[str] = Field(None, max_length=100)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    response_time_ms: Optional[int] = Field(None, ge=0)


class ConversationHistory(BaseModel):
    """Schema for conversation history response"""

    conversations: List[Conversation] = Field(default_factory=list)
    total_count: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=20)
    has_more: bool = Field(default=False)

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "conversations": [],
                "total_count": 47,
                "page": 1,
                "page_size": 20,
                "has_more": True,
            }
        }


class MessageIntent:
    """Common message intent types"""

    PRODUCT_INQUIRY = "product_inquiry"
    ORDER_LOOKUP = "order_lookup"
    GENERAL_QUESTION = "general_question"
    COMPLAINT = "complaint"
    PRAISE = "praise"
    SHIPPING_QUESTION = "shipping_question"
    RETURN_REQUEST = "return_request"
    UNKNOWN = "unknown"


__all__ = [
    "Conversation",
    "ConversationCreate",
    "ConversationHistory",
    "MessageIntent",
]
