"""
Analytics router handling metrics aggregation and dashboard data.
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.services.analytics_service import AnalyticsService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={
        401: {"description": "Unauthorized"},
    },
)


@router.get(
    "/summary",
    summary="Get analytics dashboard summary",
    description="Get complete analytics summary for dashboard display.",
)
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get analytics dashboard summary.

    **Query Parameter:**
    - days: Number of days to analyze (1-90, default 7)

    **Returns:**
    - Total questions asked
    - Questions asked today
    - Top products mentioned
    - Daily volume chart data
    - Engagement metrics
    """
    analytics_service = AnalyticsService(db)

    summary = await analytics_service.get_dashboard_summary(
        user_id=current_user["id"], days=days
    )

    return {
        "success": True,
        "data": summary,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/questions-volume",
    summary="Get questions volume chart data",
    description="Get daily question volume for chart display.",
)
async def get_questions_volume(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get questions volume chart data.

    Returns daily count of questions asked, formatted for line chart.
    """
    analytics_service = AnalyticsService(db)

    chart_data = await analytics_service.get_questions_volume_chart_data(
        user_id=current_user["id"], days=days
    )

    return {
        "success": True,
        "data": {"chart_data": chart_data, "days": days},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/top-products",
    summary="Get top product mentions",
    description="Get most frequently mentioned products for pie chart.",
)
async def get_top_products(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    limit: int = Query(5, ge=1, le=20, description="Number of top products"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get top product mentions.

    Returns products most frequently mentioned in conversations,
    formatted for pie chart display.
    """
    analytics_service = AnalyticsService(db)

    chart_data = await analytics_service.get_top_products_chart_data(
        user_id=current_user["id"], days=days
    )

    # Limit to requested count
    chart_data = chart_data[:limit]

    return {
        "success": True,
        "data": {"chart_data": chart_data, "days": days},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/engagement",
    summary="Get engagement metrics",
    description="Get customer engagement metrics.",
)
async def get_engagement_metrics(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get engagement metrics.

    **Returns:**
    - Total conversations
    - Unique customers
    - Average messages per customer
    - Total events logged
    """
    analytics_service = AnalyticsService(db)

    metrics = await analytics_service.get_engagement_metrics(
        user_id=current_user["id"], days=days
    )

    return {
        "success": True,
        "data": metrics,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/events",
    summary="Get event counts",
    description="Get aggregated event counts by type.",
)
async def get_event_counts(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get event counts by type.

    Returns count of each event type:
    - question_asked
    - product_view
    - order_lookup
    - etc.
    """
    analytics_service = AnalyticsService(db)

    event_counts = await analytics_service.get_event_counts(
        user_id=current_user["id"], days=days
    )

    return {
        "success": True,
        "data": {"events": event_counts, "days": days},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get(
    "/daily-volume",
    summary="Get daily event volume",
    description="Get total events by day for trend analysis.",
)
async def get_daily_volume(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get daily event volume.

    Returns total events per day for trend visualization.
    """
    analytics_service = AnalyticsService(db)

    daily_volume = await analytics_service.get_daily_volume(
        user_id=current_user["id"], days=days
    )

    return {
        "success": True,
        "data": {"daily_volume": daily_volume, "days": days},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["router"]
