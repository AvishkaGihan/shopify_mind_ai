"""
Analytics event model for tracking user interactions.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EventType:
    """Analytics event type constants"""

    QUESTION_ASKED = "question_asked"
    PRODUCT_VIEW = "product_view"
    ORDER_LOOKUP = "order_lookup"
    CONVERSATION_STARTED = "conversation_started"
    CONVERSATION_ENDED = "conversation_ended"
    CSV_UPLOAD = "csv_upload"
    SETTINGS_UPDATED = "settings_updated"

    @classmethod
    def get_all(cls) -> list:
        """Get all valid event types"""
        return [
            cls.QUESTION_ASKED,
            cls.PRODUCT_VIEW,
            cls.ORDER_LOOKUP,
            cls.CONVERSATION_STARTED,
            cls.CONVERSATION_ENDED,
            cls.CSV_UPLOAD,
            cls.SETTINGS_UPDATED,
        ]


class AnalyticsEvent(BaseModel):
    """
    Analytics event model for tracking user interactions.

    Attributes:
        id: Unique event identifier (UUID)
        user_id: Store owner UUID
        event_type: Type of event
        event_data: Flexible JSON data for event-specific info
        session_id: Customer session identifier
        customer_identifier: Anonymous customer identifier
        ip_address: Customer IP address (optional)
        user_agent: Browser/app user agent string
        created_at: Event timestamp
    """

    id: Optional[str] = Field(None, description="Event UUID")
    user_id: str = Field(..., description="Store owner UUID")
    event_type: str = Field(..., description="Event type")
    event_data: Dict[str, Any] = Field(
        default_factory=dict, description="Event-specific data"
    )
    session_id: Optional[str] = Field(
        None, max_length=255, description="Session identifier"
    )
    customer_identifier: Optional[str] = Field(
        None, max_length=255, description="Customer identifier"
    )
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    created_at: Optional[datetime] = Field(None, description="Event timestamp")

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "event_type": "question_asked",
                "event_data": {
                    "message_length": 25,
                    "response_time_ms": 1523,
                    "intent_detected": "product_inquiry",
                },
                "session_id": "sess_abc123",
                "customer_identifier": "customer@example.com",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0...",
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation
        """
        return self.model_dump()


class AnalyticsEventCreate(BaseModel):
    """Schema for creating a new analytics event"""

    event_type: str = Field(...)
    event_data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(None, max_length=255)
    customer_identifier: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class EventMetrics(BaseModel):
    """Schema for aggregated event metrics"""

    event_type: str
    count: int
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None


class DailyMetrics(BaseModel):
    """Schema for daily aggregated metrics"""

    date: str  # YYYY-MM-DD format
    event_count: int
    unique_customers: Optional[int] = None

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {"date": "2025-11-15", "event_count": 47, "unique_customers": 12}
        }


class EngagementMetrics(BaseModel):
    """Schema for engagement metrics"""

    total_conversations: int = Field(default=0)
    unique_customers: int = Field(default=0)
    avg_messages_per_customer: float = Field(default=0.0)
    total_events: int = Field(default=0)

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "total_conversations": 47,
                "unique_customers": 15,
                "avg_messages_per_customer": 3.13,
                "total_events": 142,
            }
        }


class ProductMention(BaseModel):
    """Schema for product mention tracking"""

    product_id: Optional[str] = None
    product_name: str
    mention_count: int

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "product_name": "Wireless Headphones",
                "mention_count": 23,
            }
        }


class AnalyticsSummary(BaseModel):
    """Schema for analytics dashboard summary"""

    total_questions: int = Field(default=0)
    questions_today: int = Field(default=0)
    top_products: list[ProductMention] = Field(default_factory=list)
    daily_volume: list[DailyMetrics] = Field(default_factory=list)
    engagement: EngagementMetrics = Field(default_factory=EngagementMetrics)

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "total_questions": 342,
                "questions_today": 47,
                "top_products": [],
                "daily_volume": [],
                "engagement": {},
            }
        }


__all__ = [
    "AnalyticsEvent",
    "AnalyticsEventCreate",
    "EventType",
    "EventMetrics",
    "DailyMetrics",
    "EngagementMetrics",
    "ProductMention",
    "AnalyticsSummary",
]
