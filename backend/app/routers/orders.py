"""
Orders router handling order lookup and status tracking.
"""

from fastapi import APIRouter, Depends, Query, status
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.services.order_service import OrderService
from app.utils.logger import get_logger
from app.utils.error_handler import NotFoundException

logger = get_logger(__name__)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Not Found"},
    },
)


@router.get(
    "/search",
    summary="Search orders",
    description="Search orders by order ID or customer email.",
)
async def search_orders(
    query: str = Query(
        ..., min_length=3, max_length=255, description="Order ID or customer email"
    ),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Search orders by order ID or customer email.

    **Query Parameter:**
    - query: Order ID (e.g., "ORD-12345") or customer email

    Returns list of matching orders with status cards.
    """
    order_service = OrderService(db)

    orders = await order_service.search_orders(user_id=current_user["id"], query=query)

    # Format orders for chat display
    formatted_orders = [order_service.format_order_for_chat(order) for order in orders]

    return {
        "success": True,
        "data": {"orders": formatted_orders, "count": len(formatted_orders)},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/{order_id}",
    summary="Get order details",
    description="Get detailed information for a specific order.",
)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get order details by order ID.

    Returns complete order information including:
    - Order ID, customer info
    - Items list with quantities and prices
    - Status with color coding
    - Estimated delivery date
    - Tracking information
    """
    order_service = OrderService(db)

    order = await order_service.get_order_by_id(
        user_id=current_user["id"], order_id=order_id
    )

    if not order:
        raise NotFoundException(
            f"Order {order_id} not found", resource_type="order", resource_id=order_id
        )

    formatted_order = order_service.format_order_for_chat(order)

    return {
        "success": True,
        "data": formatted_order,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post(
    "/mock/generate",
    status_code=status.HTTP_201_CREATED,
    summary="Generate mock orders (MVP only)",
    description="Create mock orders for testing. Development/MVP only.",
)
async def generate_mock_orders(
    count: int = Query(10, ge=1, le=50, description="Number of orders to create"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Generate mock orders for testing.

    **Development/MVP only!**

    Creates realistic mock orders with:
    - Random products
    - Various statuses (pending, shipped, delivered, etc.)
    - Estimated delivery dates
    - Tracking numbers

    Useful for testing order lookup and status display.
    """
    order_service = OrderService(db)

    created_count = await order_service.create_mock_orders(
        user_id=current_user["id"], count=count
    )

    logger.info(
        "Mock orders generated",
        extra={"user_id": current_user["id"], "count": created_count},
    )

    return {
        "success": True,
        "data": {"created_count": created_count},
        "message": f"Created {created_count} mock orders",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.patch(
    "/{order_id}/status",
    summary="Update order status",
    description="Update order status and tracking information.",
)
async def update_order_status(
    order_id: str,
    status: str = Query(..., description="New order status"),
    tracking_number: str = Query(None, description="Tracking number (optional)"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Update order status.

    **Status values:**
    - pending
    - processing
    - shipped
    - in_transit
    - out_for_delivery
    - delivered
    - cancelled
    """
    order_service = OrderService(db)

    updated_order = await order_service.update_order_status(
        user_id=current_user["id"],
        order_id=order_id,
        new_status=status,
        tracking_number=tracking_number,
    )

    if not updated_order:
        raise NotFoundException(
            f"Order {order_id} not found or update failed",
            resource_type="order",
            resource_id=order_id,
        )

    formatted_order = order_service.format_order_for_chat(updated_order)

    return {
        "success": True,
        "data": formatted_order,
        "message": "Order status updated successfully",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["router"]
