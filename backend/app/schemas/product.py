"""
Product-related request/response schemas.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ProductUploadError(BaseModel):
    """Schema for individual product upload error"""

    row: int = Field(..., description="Row number in CSV")
    error: str = Field(..., description="Error message")
    data: Optional[Dict[str, Any]] = Field(None, description="Row data that failed")

    class Config:
        json_schema_extra = {
            "example": {
                "row": 5,
                "error": "Price must be greater than 0",
                "data": {"name": "Product X", "price": "-10.00"},
            }
        }


class ProductUploadResponse(BaseModel):
    """Response schema for CSV product upload"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "total_rows": 342,
                    "inserted": 340,
                    "failed": 2,
                    "errors": [
                        {"row": 2, "error": "Price must be greater than 0"},
                        {"row": 5, "error": "Invalid image URL format"},
                    ],
                },
                "message": "Upload completed with 2 errors",
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class ProductResponse(BaseModel):
    """Response schema for single product"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Wireless Headphones",
                    "description": "High-quality wireless headphones",
                    "price": 129.99,
                    "category": "Electronics",
                    "image_url": "https://example.com/image.jpg",
                },
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class ProductListResponse(BaseModel):
    """Response schema for product list"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "products": [],
                    "total_count": 342,
                    "page": 1,
                    "page_size": 20,
                    "has_more": True,
                },
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


class ProductSearchRequest(BaseModel):
    """Request schema for product search"""

    query: str = Field(..., min_length=1, max_length=255, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    limit: int = Field(default=20, ge=1, le=100, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "wireless headphones",
                "category": "Electronics",
                "min_price": 50.00,
                "max_price": 200.00,
                "limit": 20,
                "offset": 0,
            }
        }


class ProductDeleteResponse(BaseModel):
    """Response schema for product deletion"""

    success: bool = Field(default=True)
    data: Dict[str, Any] = Field(...)
    message: Optional[str] = Field(None)
    timestamp: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"deleted_count": 342},
                "message": "All products deleted successfully",
                "timestamp": "2025-11-15T10:30:00Z",
            }
        }


__all__ = [
    "ProductUploadError",
    "ProductUploadResponse",
    "ProductResponse",
    "ProductListResponse",
    "ProductSearchRequest",
    "ProductDeleteResponse",
]
