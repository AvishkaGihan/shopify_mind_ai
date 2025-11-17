"""
Database connection and utilities for Supabase PostgreSQL.

Provides functions for database operations using Supabase client.
Handles connection pooling, error handling, and query execution.
"""

from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class Database:
    """
    Supabase database connection manager.

    Provides methods for common database operations with proper
    error handling and logging.
    """

    def __init__(self):
        """Initialize Supabase client"""
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase URL and key must be configured")
        self.client: Client = create_client(
            settings.supabase_url, settings.supabase_key
        )
        logger.info(
            "Database connection initialized",
            extra={"supabase_url": settings.supabase_url},
        )

    def get_client(self) -> Client:
        """
        Get Supabase client instance.

        Returns:
            Client: Supabase client
        """
        return self.client

    async def execute_query(
        self,
        table: str,
        operation: str = "select",
        filters: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        columns: str = "*",
    ) -> Optional[Any]:
        """
        Execute a database query with error handling.

        Args:
            table: Table name
            operation: Operation type (select, insert, update, delete)
            filters: Filter conditions as dict
            data: Data to insert/update
            columns: Columns to select (default: all)

        Returns:
            Query result or None on error

        Raises:
            Exception: On database error
        """
        try:
            query = self.client.table(table)

            if operation == "select":
                query = query.select(columns)
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)  # type: ignore
                result = query.execute()

            elif operation == "insert":
                if not data:
                    raise ValueError("Data required for insert operation")
                result = query.insert(data).execute()

            elif operation == "update":
                if not data or not filters:
                    raise ValueError("Data and filters required for update")
                query = query.update(data)
                for key, value in filters.items():
                    query = query.eq(key, value)  # type: ignore
                result = query.execute()

            elif operation == "delete":
                if not filters:
                    raise ValueError("Filters required for delete operation")
                for key, value in filters.items():
                    query = query.eq(key, value)  # type: ignore
                result = query.delete().execute()

            else:
                raise ValueError(f"Unknown operation: {operation}")

            logger.debug(
                "Query executed successfully",
                extra={"table": table, "operation": operation, "filters": filters},
            )

            return result.data

        except Exception as e:
            logger.error(
                "Database query failed",
                extra={"table": table, "operation": operation, "error": str(e)},
            )
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address.

        Args:
            email: User email

        Returns:
            User dict or None if not found
        """
        try:
            result = await self.execute_query(
                table="users", operation="select", filters={"email": email}
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(
                "Failed to get user by email", extra={"email": email, "error": str(e)}
            )
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User dict or None if not found
        """
        try:
            result = await self.execute_query(
                table="users", operation="select", filters={"id": user_id}
            )
            return result[0] if result else None
        except Exception as e:
            logger.error(
                "Failed to get user by ID", extra={"user_id": user_id, "error": str(e)}
            )
            return None

    async def create_user(
        self, email: str, password_hash: str, store_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create new user.

        Args:
            email: User email
            password_hash: Hashed password
            store_name: Optional store name

        Returns:
            Created user dict or None on error
        """
        try:
            data = {
                "email": email,
                "password_hash": password_hash,
            }
            if store_name:
                data["store_name"] = store_name

            result = await self.execute_query(
                table="users", operation="insert", data=data
            )

            logger.info(
                "User created successfully",
                extra={"email": email, "user_id": result[0]["id"] if result else None},
            )

            return result[0] if result else None

        except Exception as e:
            logger.error(
                "Failed to create user", extra={"email": email, "error": str(e)}
            )
            return None

    async def update_user(
        self, user_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user data.

        Args:
            user_id: User UUID
            data: Data to update

        Returns:
            Updated user dict or None on error
        """
        try:
            result = await self.execute_query(
                table="users", operation="update", filters={"id": user_id}, data=data
            )

            logger.info(
                "User updated successfully",
                extra={"user_id": user_id, "fields": list(data.keys())},
            )

            return result[0] if result else None

        except Exception as e:
            logger.error(
                "Failed to update user", extra={"user_id": user_id, "error": str(e)}
            )
            return None

    async def get_products(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> List[Any]:
        """
        Get products for a user.

        Args:
            user_id: User UUID
            limit: Max results to return
            offset: Pagination offset

        Returns:
            List of product dicts
        """
        try:
            result = (
                self.client.table("products")
                .select("*")
                .eq("user_id", user_id)
                .range(offset, offset + limit - 1)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logger.error(
                "Failed to get products", extra={"user_id": user_id, "error": str(e)}
            )
            return []

    async def create_product(
        self, user_id: str, product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create new product.

        Args:
            user_id: User UUID
            product_data: Product data

        Returns:
            Created product dict or None on error
        """
        try:
            data = {**product_data, "user_id": user_id}
            result = await self.execute_query(
                table="products", operation="insert", data=data
            )
            return result[0] if result else None

        except Exception as e:
            logger.error(
                "Failed to create product", extra={"user_id": user_id, "error": str(e)}
            )
            return None

    async def bulk_insert_products(
        self, user_id: str, products: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk insert products.

        Args:
            user_id: User UUID
            products: List of product dicts

        Returns:
            Number of products inserted
        """
        try:
            # Add user_id to each product
            products_with_user = [
                {**product, "user_id": user_id} for product in products
            ]

            result = self.client.table("products").insert(products_with_user).execute()

            count = len(result.data) if result.data else 0

            logger.info(
                "Bulk insert completed", extra={"user_id": user_id, "count": count}
            )

            return count

        except Exception as e:
            logger.error(
                "Bulk insert failed",
                extra={
                    "user_id": user_id,
                    "product_count": len(products),
                    "error": str(e),
                },
            )
            return 0

    async def delete_all_products(self, user_id: str) -> bool:
        """
        Delete all products for a user.

        Args:
            user_id: User UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.table("products").delete().eq("user_id", user_id).execute()

            logger.info("All products deleted", extra={"user_id": user_id})

            return True

        except Exception as e:
            logger.error(
                "Failed to delete products", extra={"user_id": user_id, "error": str(e)}
            )
            return False

    async def health_check(self) -> bool:
        """
        Check database connection health.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Simple query to test connection
            self.client.table("users").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error("Database health check failed", extra={"error": str(e)})
            return False


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """
    Get global database instance (singleton pattern).

    Returns:
        Database: Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


# Export for easy imports
__all__ = ["Database", "get_database"]
