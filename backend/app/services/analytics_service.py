"""
Analytics aggregation service.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.database import Database
from app.utils.logger import get_logger
from app.models.analytics_event import EventType

logger = get_logger(__name__)


class AnalyticsService:
    """
    Service for analytics data aggregation and reporting.

    Handles:
    - Event logging
    - Metric aggregation
    - Dashboard data generation
    """

    def __init__(self, db: Database):
        """
        Initialize analytics service.

        Args:
            db: Database instance
        """
        self.db = db

    async def log_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        customer_identifier: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """
        Log an analytics event.

        Args:
            user_id: Store owner UUID
            event_type: Type of event
            event_data: Event-specific data
            session_id: Session identifier
            customer_identifier: Customer identifier
            ip_address: IP address
            user_agent: User agent string

        Returns:
            True if successful, False otherwise

        Example:
            await analytics_service.log_event(
                user_id="123",
                event_type="question_asked",
                event_data={"message_length": 25}
            )
        """
        try:
            data = {
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data or {},
                "session_id": session_id,
                "customer_identifier": customer_identifier,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }

            await self.db.execute_query(
                table="analytics_events", operation="insert", data=data
            )

            logger.debug(
                "Analytics event logged",
                extra={"user_id": user_id, "event_type": event_type},
            )

            return True

        except Exception as e:
            # Don't fail main flow if analytics fails
            logger.warning(
                "Failed to log analytics event",
                extra={"user_id": user_id, "event_type": event_type, "error": str(e)},
            )
            return False

    async def get_event_counts(
        self, user_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get event counts by type for the last N days.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            List of event count dicts

        Example:
            counts = await analytics_service.get_event_counts(user_id, days=7)
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            result = self.db.client.rpc(
                "get_event_counts",
                {
                    "search_user_id": user_id,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                },
            ).execute()

            return result.data if isinstance(result.data, list) else []  # type: ignore

        except Exception as e:
            logger.error(
                "Failed to get event counts",
                extra={"user_id": user_id, "error": str(e)},
            )
            return []

    async def get_daily_volume(
        self, user_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get daily event volume for the last N days.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            List of daily volume dicts

        Example:
            volume = await analytics_service.get_daily_volume(user_id, days=7)
        """
        try:
            result = self.db.client.rpc(
                "get_daily_event_volume", {"search_user_id": user_id, "days_back": days}
            ).execute()

            return result.data if isinstance(result.data, list) else []  # type: ignore

        except Exception as e:
            logger.error(
                "Failed to get daily volume",
                extra={"user_id": user_id, "error": str(e)},
            )
            return []

    async def get_top_products(
        self, user_id: str, days: int = 7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top product mentions for the last N days.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back
            limit: Number of top products to return

        Returns:
            List of product mention dicts

        Example:
            products = await analytics_service.get_top_products(user_id, days=7)
        """
        try:
            result = self.db.client.rpc(
                "get_top_product_mentions",
                {"search_user_id": user_id, "days_back": days, "limit_count": limit},
            ).execute()

            return result.data if isinstance(result.data, list) else []  # type: ignore

        except Exception as e:
            logger.error(
                "Failed to get top products",
                extra={"user_id": user_id, "error": str(e)},
            )
            return []

    async def get_engagement_metrics(
        self, user_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get engagement metrics for the last N days.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            Engagement metrics dict

        Example:
            metrics = await analytics_service.get_engagement_metrics(user_id)
        """
        try:
            result = self.db.client.rpc(
                "get_engagement_metrics", {"search_user_id": user_id, "days_back": days}
            ).execute()

            if result.data:
                data = result.data[0] if isinstance(result.data, list) else result.data
                if isinstance(data, dict):
                    avg_messages = data.get("avg_messages_per_customer", 0)
                    avg_messages_float = (
                        float(avg_messages)
                        if isinstance(avg_messages, (int, float))
                        else 0.0
                    )
                    return {
                        "total_conversations": data.get("total_conversations", 0),  # type: ignore
                        "unique_customers": data.get("unique_customers", 0),  # type: ignore
                        "avg_messages_per_customer": avg_messages_float,
                        "total_events": data.get("total_events", 0),  # type: ignore
                    }

            return {
                "total_conversations": 0,
                "unique_customers": 0,
                "avg_messages_per_customer": 0.0,
                "total_events": 0,
            }

        except Exception as e:
            logger.error(
                "Failed to get engagement metrics",
                extra={"user_id": user_id, "error": str(e)},
            )
            return {
                "total_conversations": 0,
                "unique_customers": 0,
                "avg_messages_per_customer": 0.0,
                "total_events": 0,
            }

    async def get_dashboard_summary(
        self, user_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get complete analytics dashboard summary.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            Complete dashboard data dict

        Example:
            summary = await analytics_service.get_dashboard_summary(user_id)
        """
        # Get all analytics data in parallel
        event_counts = await self.get_event_counts(user_id, days)
        daily_volume = await self.get_daily_volume(user_id, days)
        top_products = await self.get_top_products(user_id, days)
        engagement = await self.get_engagement_metrics(user_id, days)

        # Calculate total questions
        total_questions = sum(
            count.get("count", 0)
            for count in event_counts
            if count.get("event_type") == EventType.QUESTION_ASKED
        )

        # Calculate questions today
        today = datetime.utcnow().date()
        questions_today = sum(
            day.get("event_count", 0)
            for day in daily_volume
            if day.get("date") == today.isoformat()
        )

        logger.info(
            "Dashboard summary generated",
            extra={"user_id": user_id, "total_questions": total_questions},
        )

        return {
            "total_questions": total_questions,
            "questions_today": questions_today,
            "top_products": top_products,
            "daily_volume": daily_volume,
            "engagement": engagement,
        }

    async def get_questions_volume_chart_data(
        self, user_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get data formatted for questions volume chart.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            Chart data list
        """
        daily_volume = await self.get_daily_volume(user_id, days)

        # Format for chart
        chart_data = [
            {"date": day.get("date"), "count": day.get("event_count", 0)}
            for day in daily_volume
        ]

        return chart_data

    async def get_top_products_chart_data(
        self, user_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get data formatted for top products pie chart.

        Args:
            user_id: Store owner UUID
            days: Number of days to look back

        Returns:
            Chart data list
        """
        top_products = await self.get_top_products(user_id, days, limit=5)

        # Format for pie chart
        chart_data = [
            {
                "name": product.get("product_name", "Unknown"),
                "value": product.get("mention_count", 0),
            }
            for product in top_products
        ]

        return chart_data


__all__ = ["AnalyticsService"]
