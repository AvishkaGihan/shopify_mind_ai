"""
Store router handling store configuration and settings.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.schemas.user import UpdateStoreSettingsRequest, UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/store",
    tags=["Store"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"},
    },
)


@router.get(
    "/settings",
    response_model=UserResponse,
    summary="Get store settings",
    description="Get current store configuration and settings.",
)
async def get_store_settings(current_user: dict = Depends(get_current_user)):
    """
    Get store settings for authenticated user.

    Returns:
    - Store name
    - Brand colors (primary, accent, supporting)
    - AI personality tone
    - Creation date
    """
    return UserResponse(
        success=True,
        data={
            "id": current_user["id"],
            "email": current_user["email"],
            "store_name": current_user.get("store_name"),
            "store_colors": current_user.get(
                "store_colors",
                {"primary": "#00a86b", "accent": "#f97316", "supporting": "#a78bfa"},
            ),
            "ai_tone": current_user.get("ai_tone", "friendly"),
            "created_at": current_user.get("created_at"),
        },
        message="Store settings retrieved successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.put(
    "/settings",
    response_model=UserResponse,
    summary="Update store settings",
    description="Update store configuration and settings.",
)
async def update_store_settings(
    request: UpdateStoreSettingsRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Update store settings.

    **Updatable fields:**
    - store_name: Display name for the store
    - store_colors: Brand colors (primary, accent, supporting)
    - ai_tone: AI personality (friendly, professional, casual, energetic)

    All fields are optional. Only provided fields will be updated.
    """
    # Build update data
    update_data = {}

    if request.store_name is not None:
        update_data["store_name"] = request.store_name

    if request.store_colors is not None:
        update_data["store_colors"] = request.store_colors.model_dump()

    if request.ai_tone is not None:
        update_data["ai_tone"] = request.ai_tone

    if not update_data:
        # No fields to update
        return UserResponse(
            success=True,
            data={
                "id": current_user["id"],
                "email": current_user["email"],
                "store_name": current_user.get("store_name"),
                "store_colors": current_user.get("store_colors"),
                "ai_tone": current_user.get("ai_tone"),
            },
            message="No changes made",
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    # Update user in database
    updated_user = await db.update_user(user_id=current_user["id"], data=update_data)

    if not updated_user:
        from app.utils.error_handler import DatabaseException

        raise DatabaseException("Failed to update store settings")

    logger.info(
        "Store settings updated",
        extra={
            "user_id": current_user["id"],
            "updated_fields": list(update_data.keys()),
        },
    )

    return UserResponse(
        success=True,
        data={
            "id": updated_user["id"],
            "email": updated_user["email"],
            "store_name": updated_user.get("store_name"),
            "store_colors": updated_user.get("store_colors"),
            "ai_tone": updated_user.get("ai_tone"),
        },
        message="Store settings updated successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/stats",
    summary="Get store statistics",
    description="Get basic store statistics (products, conversations, etc.).",
)
async def get_store_stats(
    current_user: dict = Depends(get_current_user), db: Database = Depends(get_database)
):
    """
    Get store statistics.

    Returns:
    - Total products
    - Total conversations
    - Total customers (unique)
    - Account created date
    """
    # Get product count
    products_result = (
        db.client.table("products")
        .select("*")
        .eq("user_id", current_user["id"])
        .execute()
    )

    product_count = len(products_result.data) if products_result.data else 0

    # Get conversation count
    conversations_result = (
        db.client.table("conversations")
        .select("*")
        .eq("user_id", current_user["id"])
        .execute()
    )

    conversation_count = (
        len(conversations_result.data) if conversations_result.data else 0
    )

    # Get unique customers count
    customers_result = (
        db.client.table("conversations")
        .select("customer_identifier")
        .eq("user_id", current_user["id"])
        .execute()
    )

    unique_customers = len(
        set(
            item.get("customer_identifier") if isinstance(item, dict) else None
            for item in (customers_result.data or [])
            if isinstance(item, dict) and item.get("customer_identifier")
        )
    )

    return {
        "success": True,
        "data": {
            "total_products": product_count,
            "total_conversations": conversation_count,
            "unique_customers": unique_customers,
            "account_created": current_user.get("created_at"),
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["router"]
