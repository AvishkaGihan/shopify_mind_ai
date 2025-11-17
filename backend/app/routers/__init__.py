"""
API route handlers for ShopifyMind AI.

Routers organize endpoints by domain:
- auth: Authentication and user management
- products: Product management and CSV upload
- chat: Customer chat and AI responses
- orders: Order lookup and tracking
- store: Store configuration and settings
- analytics: Analytics and metrics
"""

from .auth import router as auth_router
from .products import router as products_router
from .chat import router as chat_router
from .orders import router as orders_router
from .store import router as store_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "products_router",
    "chat_router",
    "orders_router",
    "store_router",
    "analytics_router",
]
