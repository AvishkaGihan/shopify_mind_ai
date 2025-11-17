"""
Chat router handling customer messages and AI responses.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Any, List, Dict
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.services.gemini_service import GeminiService
from app.services.analytics_service import AnalyticsService
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from app.models.analytics_event import EventType
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"},
    },
)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send chat message",
    description="Send customer message and receive AI response with optional product cards.",
)
async def send_message(
    request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Send a customer message and get AI response.

    **Request:**
    - message: Customer message text (1-2000 chars)
    - customer_identifier: Optional customer ID (email, session, etc.)
    - session_id: Optional session ID for grouping

    **Response:**
    - AI-generated response
    - Product cards (if products mentioned)
    - Intent detection (product_inquiry, order_lookup, etc.)
    - Response time in milliseconds
    """
    gemini_service = GeminiService(db)
    analytics_service = AnalyticsService(db)

    # Get conversation history (last 5 messages)
    history_result = (
        db.client.table("conversations")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )

    conversation_history = history_result.data if history_result.data else []

    # Generate AI response
    formatted_history: Optional[List[Dict[str, Any]]] = None
    if conversation_history:
        # Type cast the conversation history to match function signature
        formatted_history = list(reversed(conversation_history))  # type: ignore

    ai_result = await gemini_service.generate_response(
        user_id=current_user["id"],
        customer_message=request.message,
        conversation_history=formatted_history,
    )

    # Store conversation
    conversation_data = {
        "user_id": current_user["id"],
        "customer_identifier": request.customer_identifier,
        "customer_message": request.message,
        "ai_response": ai_result["ai_response"],
        "message_count": len(conversation_history) + 1,
        "products_referenced": ai_result["products_referenced"],
        "intent_detected": ai_result["intent_detected"],
        "response_time_ms": ai_result["response_time_ms"],
    }

    conversation_result = await db.execute_query(
        table="conversations", operation="insert", data=conversation_data
    )

    # Log analytics event
    await analytics_service.log_event(
        user_id=current_user["id"],
        event_type=EventType.QUESTION_ASKED,
        event_data={
            "message_length": len(request.message),
            "response_time_ms": ai_result["response_time_ms"],
            "intent_detected": ai_result["intent_detected"],
        },
        session_id=request.session_id,
        customer_identifier=request.customer_identifier,
    )

    # Get product details for referenced products
    products = []
    if ai_result["products_referenced"]:
        for product_id in ai_result["products_referenced"][:3]:  # Max 3 cards
            product_result = await db.execute_query(
                table="products", operation="select", filters={"id": product_id}
            )
            if product_result:
                product = product_result[0]
                products.append(
                    {
                        "id": product["id"],
                        "name": product["name"],
                        "description": product.get("description", "")[:200],
                        "price": float(product["price"]),
                        "category": product.get("category"),
                        "image_url": product.get("image_url"),
                    }
                )

    conversation_id = conversation_result[0]["id"] if conversation_result else None

    return ChatMessageResponse(
        success=True,
        data={
            "id": conversation_id,
            "customer_message": request.message,
            "ai_response": ai_result["ai_response"],
            "products": products,
            "intent_detected": ai_result["intent_detected"],
            "response_time_ms": ai_result["response_time_ms"],
        },
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="Get paginated conversation history for the store.",
)
async def get_chat_history(
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    customer_identifier: Optional[str] = Query(None, description="Filter by customer"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get conversation history for authenticated store.

    **Query Parameters:**
    - limit: Number of results (1-100, default 20)
    - offset: Pagination offset (default 0)
    - customer_identifier: Filter by specific customer (optional)

    Returns paginated list of conversations with total count.
    """
    # Build query
    query = (
        db.client.table("conversations").select("*").eq("user_id", current_user["id"])
    )

    if customer_identifier:
        query = query.eq("customer_identifier", customer_identifier)

    # Get total count
    count_query = (
        db.client.table("conversations").select("*").eq("user_id", current_user["id"])
    )

    if customer_identifier:
        count_query = count_query.eq("customer_identifier", customer_identifier)

    count_result = count_query.execute()
    total_count = len(count_result.data) if count_result.data else 0

    # Get paginated results
    result = (
        query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    )

    conversations: List[Dict[str, Any]] = result.data if result.data else []  # type: ignore

    # Format for response
    formatted_conversations = [
        {
            "id": conv["id"],
            "message": conv["customer_message"],
            "response": conv["ai_response"],
            "timestamp": conv["created_at"],
            "customer_identifier": conv.get("customer_identifier"),
            "intent_detected": conv.get("intent_detected"),
        }
        for conv in conversations
    ]

    has_more = (offset + len(conversations)) < total_count

    return ChatHistoryResponse(
        success=True,
        data={
            "conversations": formatted_conversations,
            "total_count": total_count,
            "page": (offset // limit) + 1,
            "page_size": limit,
            "has_more": has_more,
        },
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.delete(
    "/history",
    summary="Clear chat history",
    description="Delete all conversation history for the store.",
)
async def clear_chat_history(
    current_user: dict = Depends(get_current_user), db: Database = Depends(get_database)
):
    """
    Clear all conversation history for authenticated store.

    **Warning:** This action cannot be undone!
    """
    db.client.table("conversations").delete().eq(
        "user_id", current_user["id"]
    ).execute()

    logger.info("Chat history cleared", extra={"user_id": current_user["id"]})

    return {
        "success": True,
        "message": "Chat history cleared successfully",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["router"]
