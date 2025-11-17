"""
Order management service.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import Database
from app.utils.logger import get_logger
from app.models.order import OrderStatus

logger = get_logger(__name__)


class OrderService:
    """
    Service for order management operations.

    Handles:
    - Order search and lookup
    - Order status tracking
    - Mock order generation (for MVP)
    """

    def __init__(self, db: Database):
        """
        Initialize order service.

        Args:
            db: Database instance
        """
        self.db = db

    async def search_orders(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Search orders by order ID or customer email.

        Args:
            user_id: Store owner UUID
            query: Search query (order ID or email)

        Returns:
            List of matching orders

        Example:
            orders = await order_service.search_orders(user_id, "ORD-12345")
        """
        if len(query) < 3:  # type: ignore
            logger.warning("Search query too short", extra={"query": query})
            return []

        try:
            # Use database function to search
            result = self.db.client.rpc(
                "search_orders", {"search_user_id": user_id, "search_query": query}
            ).execute()

            orders = result.data if isinstance(result.data, list) else []  # type: ignore

            logger.info(
                "Orders searched",
                extra={"user_id": user_id, "query": query, "results": len(orders)},
            )

            return orders  # type: ignore

        except Exception as e:
            logger.error(
                "Order search failed",
                extra={"user_id": user_id, "query": query, "error": str(e)},
            )
            return []

    async def get_order_by_id(
        self, user_id: str, order_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get order details by order ID.

        Args:
            user_id: Store owner UUID
            order_id: Order number

        Returns:
            Order dict or None if not found

        Example:
            order = await order_service.get_order_by_id(user_id, "ORD-12345")
        """
        try:
            # Use database function to get order details
            result = self.db.client.rpc(
                "get_order_details",
                {"search_user_id": user_id, "search_order_id": order_id},
            ).execute()

            if not result.data:
                logger.info(
                    "Order not found", extra={"user_id": user_id, "order_id": order_id}
                )
                return None

            order = result.data[0] if isinstance(result.data, list) else result.data

            logger.info(
                "Order retrieved", extra={"user_id": user_id, "order_id": order_id}
            )

            return order  # type: ignore

        except Exception as e:
            logger.error(
                "Failed to get order",
                extra={"user_id": user_id, "order_id": order_id, "error": str(e)},
            )
            return None

    def format_order_for_chat(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format order data for chat display.

        Args:
            order: Order dict from database

        Returns:
            Formatted order dict for chat UI
        """
        return {
            "id": order.get("id"),
            "order_id": order.get("order_id"),
            "customer_email": order.get("customer_email"),
            "customer_name": order.get("customer_name"),
            "items": order.get("items", []),
            "total": float(order.get("total", 0)),
            "status": order.get("status"),
            "status_color": OrderStatus.get_color(order.get("status", "pending")),
            "estimated_delivery": order.get("estimated_delivery"),
            "tracking_number": order.get("tracking_number"),
            "tracking_url": order.get("tracking_url"),
            "created_at": order.get("created_at"),
        }

    async def create_mock_orders(self, user_id: str, count: int = 10) -> int:
        """
        Create mock orders for testing (MVP only).

        Args:
            user_id: Store owner UUID
            count: Number of mock orders to create

        Returns:
            Number of orders created

        Example:
            created = await order_service.create_mock_orders(user_id, 10)
        """
        import random

        statuses = [
            OrderStatus.PENDING,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.IN_TRANSIT,
            OrderStatus.DELIVERED,
        ]

        mock_products = [
            {"name": "Wireless Headphones", "price": 129.99},
            {"name": "Smart Watch", "price": 249.99},
            {"name": "Laptop Stand", "price": 39.99},
            {"name": "USB-C Cable", "price": 19.99},
            {"name": "Phone Case", "price": 24.99},
        ]

        orders_created = 0

        for i in range(count):
            # Generate order data
            order_num = f"ORD-{10000 + i}"
            status = random.choice(statuses)

            # Random items
            num_items = random.randint(1, 3)
            items = []
            subtotal = Decimal("0")

            for _ in range(num_items):
                product = random.choice(mock_products)
                quantity = random.randint(1, 3)
                price = Decimal(str(product["price"]))

                items.append(
                    {
                        "product_name": product["name"],
                        "quantity": quantity,
                        "price": float(price),
                    }
                )

                subtotal += price * quantity

            # Calculate totals
            tax = subtotal * Decimal("0.09")  # 9% tax
            shipping = Decimal("10.00")
            total = subtotal + tax + shipping

            # Estimated delivery (3-7 days from now)
            days_ahead = random.randint(3, 7)
            estimated_delivery = datetime.utcnow() + timedelta(days=days_ahead)

            # Create order
            order_data = {
                "user_id": user_id,
                "order_id": order_num,
                "customer_email": f"customer{i}@example.com",
                "customer_name": f"Customer {i}",
                "items": items,
                "subtotal": float(subtotal),
                "tax": float(tax),
                "shipping": float(shipping),
                "total": float(total),
                "status": status,
                "payment_status": "paid",
                "estimated_delivery": estimated_delivery.isoformat(),
                "tracking_number": (
                    f"TRK{1000000000 + i}"
                    if status
                    in [
                        OrderStatus.SHIPPED,
                        OrderStatus.IN_TRANSIT,
                        OrderStatus.DELIVERED,
                    ]
                    else None
                ),
            }

            try:
                result = await self.db.execute_query(
                    table="orders", operation="insert", data=order_data
                )

                if result:
                    orders_created += 1

            except Exception as e:
                logger.error(
                    "Failed to create mock order",
                    extra={"order_num": order_num, "error": str(e)},
                )

        logger.info(
            "Mock orders created", extra={"user_id": user_id, "count": orders_created}
        )

        return orders_created

    async def update_order_status(
        self,
        user_id: str,
        order_id: str,
        new_status: str,
        tracking_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update order status.

        Args:
            user_id: Store owner UUID
            order_id: Order number
            new_status: New status value
            tracking_number: Optional tracking number

        Returns:
            Updated order dict or None if failed
        """
        # Validate status
        if new_status not in OrderStatus.get_all():
            logger.error("Invalid order status", extra={"status": new_status})
            return None

        # Get current order
        order = await self.get_order_by_id(user_id, order_id)
        if not order:
            logger.error(
                "Order not found for update",
                extra={"user_id": user_id, "order_id": order_id},
            )
            return None

        # Build update data
        update_data = {"status": new_status, "updated_at": datetime.utcnow()}

        if tracking_number:
            update_data["tracking_number"] = tracking_number

        # Mark as delivered if status is delivered
        if new_status == OrderStatus.DELIVERED:
            update_data["actual_delivery"] = datetime.utcnow()

        try:
            # Update order
            result = await self.db.execute_query(
                table="orders",
                operation="update",
                filters={"id": order["id"]},
                data=update_data,
            )

            logger.info(
                "Order status updated",
                extra={
                    "user_id": user_id,
                    "order_id": order_id,
                    "new_status": new_status,
                },
            )

            return result[0] if result else None

        except Exception as e:
            logger.error(
                "Failed to update order status",
                extra={"user_id": user_id, "order_id": order_id, "error": str(e)},
            )
            return None


__all__ = ["OrderService"]
