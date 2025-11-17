"""
Products router handling CSV upload, product listing, and management.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from typing import Optional
from datetime import datetime

from app.database import Database, get_database
from app.dependencies import get_current_user
from app.services.csv_service import CSVService
from app.schemas.product import (
    ProductUploadResponse,
    ProductListResponse,
    ProductResponse,
    ProductDeleteResponse,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={
        401: {"description": "Unauthorized"},
        400: {"description": "Bad Request"},
    },
)


@router.post(
    "/upload",
    response_model=ProductUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload product CSV",
    description="Upload CSV file with product data. Validates and imports products into database.",
)
async def upload_products(
    file: UploadFile = File(..., description="CSV file with product data"),
    replace_existing: bool = Query(
        False, description="If true, delete existing products before import"
    ),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Upload and import products from CSV file.

    **CSV Format:**
    - Required columns: name, price
    - Optional columns: description, category, sku, image_url

    **Validation:**
    - File size: Max 10MB
    - Max products: 1000 per upload
    - Price must be > 0
    - Image URLs must be valid

    Returns summary with total rows, inserted count, and any errors.
    """
    csv_service = CSVService(db)

    result = await csv_service.upload_and_import(
        user_id=current_user["id"], file=file, replace_existing=replace_existing
    )

    message = "Upload completed successfully"
    if result["failed"] > 0:
        message = f"Upload completed with {result['failed']} errors"

    return ProductUploadResponse(
        success=True,
        data=result,
        message=message,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List products",
    description="Get paginated list of products for the authenticated store.",
)
async def list_products(
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    List products for authenticated store.

    **Query Parameters:**
    - limit: Number of results (1-100, default 20)
    - offset: Pagination offset (default 0)
    - category: Filter by category (optional)

    Returns paginated list of products with total count.
    """
    # Get products from database
    products = await db.get_products(
        user_id=current_user["id"], limit=limit, offset=offset
    )

    # Get total count
    count_result = (
        db.client.table("products").select("*").eq("user_id", current_user["id"])
    )

    if category:
        count_result = count_result.eq("category", category)

    count_response = count_result.execute()
    total_count = len(count_response.data) if count_response.data else 0

    # Filter by category if specified
    if category and products:
        products = [p for p in products if p.get("category") == category]

    has_more = (offset + len(products)) < total_count

    return ProductListResponse(
        success=True,
        data={
            "products": products,
            "total_count": total_count,
            "page": (offset // limit) + 1,
            "page_size": limit,
            "has_more": has_more,
        },
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product details",
    description="Get detailed information for a specific product.",
)
async def get_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Get product details by ID.

    Returns complete product information including:
    - Name, description, price
    - Category, SKU
    - Image URL
    - Stock quantity
    """
    result = await db.execute_query(
        table="products",
        operation="select",
        filters={"id": product_id, "user_id": current_user["id"]},
    )

    if not result:
        from app.utils.error_handler import NotFoundException

        raise NotFoundException(
            "Product not found", resource_type="product", resource_id=product_id
        )

    return ProductResponse(
        success=True,
        data=result[0],
        message=None,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    summary="Delete a product",
    description="Delete a specific product by ID.",
)
async def delete_product(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database),
):
    """
    Delete a product by ID.

    Permanently removes the product from the database.
    """
    await db.execute_query(
        table="products",
        operation="delete",
        filters={"id": product_id, "user_id": current_user["id"]},
    )

    logger.info(
        "Product deleted",
        extra={"user_id": current_user["id"], "product_id": product_id},
    )

    return ProductDeleteResponse(
        success=True,
        data={"deleted_count": 1},
        message="Product deleted successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.delete(
    "",
    response_model=ProductDeleteResponse,
    summary="Delete all products",
    description="Delete all products for the authenticated store.",
)
async def delete_all_products(
    current_user: dict = Depends(get_current_user), db: Database = Depends(get_database)
):
    """
    Delete all products for authenticated store.

    **Warning:** This action cannot be undone!
    """
    success = await db.delete_all_products(current_user["id"])

    if not success:
        from app.utils.error_handler import DatabaseException

        raise DatabaseException("Failed to delete products")

    logger.info("All products deleted", extra={"user_id": current_user["id"]})

    return ProductDeleteResponse(
        success=True,
        data={"deleted_count": "all"},
        message="All products deleted successfully",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/template/download",
    summary="Download CSV template",
    description="Get CSV template with example product data.",
)
async def download_csv_template(db: Database = Depends(get_database)):
    """
    Download CSV template for product upload.

    Returns a CSV file with headers and one example row.
    """
    from fastapi.responses import Response

    csv_service = CSVService(db)
    template = csv_service.generate_csv_template()

    return Response(
        content=template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=product_template.csv"},
    )


__all__ = ["router"]
