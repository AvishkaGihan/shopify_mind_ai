"""
Data models for ShopifyMind AI.

These models represent database entities and are used for:
- Type hints
- Data validation
- ORM-style interactions with Supabase
"""

from .user import User
from .product import Product
from .conversation import Conversation
from .order import Order, OrderItem
from .analytics_event import AnalyticsEvent

__all__ = [
    "User",
    "Product",
    "Conversation",
    "Order",
    "OrderItem",
    "AnalyticsEvent",
]
