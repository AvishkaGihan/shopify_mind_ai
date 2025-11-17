"""
Product model representing inventory items.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class Product(BaseModel):
    """
    Product model representing a store inventory item.

    Attributes:
        id: Unique product identifier (UUID)
        user_id: Store owner UUID
        name: Product name
        description: Product description
        price: Product price
        category: Product category
        sku: Stock keeping unit
        image_url: URL to product image
        stock_quantity: Available stock quantity
        is_active: Product visibility status
        metadata: Additional product data as JSON
        created_at: Product creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[str] = Field(None, description="Product UUID")
    user_id: Optional[str] = Field(None, description="Store owner UUID")
    name: str = Field(..., max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price")
    category: Optional[str] = Field(
        None, max_length=100, description="Product category"
    )
    sku: Optional[str] = Field(None, max_length=100, description="Stock keeping unit")
    image_url: Optional[str] = Field(
        None, max_length=500, description="Product image URL"
    )
    stock_quantity: int = Field(default=0, ge=0, description="Stock quantity")
    is_active: bool = Field(default=True, description="Product active status")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional data"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator("price")
    def validate_price(cls, v):
        """Validate price is positive"""
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @validator("sku")
    def validate_sku(cls, v):
        """Validate SKU format (alphanumeric, hyphens, underscores)"""
        if v is not None and v.strip():
            import re

            if not re.match(r"^[a-zA-Z0-9-_]+$", v):
                raise ValueError(
                    "SKU can only contain letters, numbers, hyphens, and underscores"
                )
        return v

    @validator("image_url")
    def validate_image_url(cls, v):
        """Validate image URL starts with http/https"""
        if v is not None and v.strip():
            import re

            if not re.match(r"^https?://", v):
                raise ValueError("Image URL must start with http:// or https://")
        return v

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 129.99,
                "category": "Electronics",
                "sku": "WH-001",
                "image_url": "https://example.com/images/headphones.jpg",
                "stock_quantity": 50,
                "is_active": True,
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation
        """
        data = self.model_dump()
        # Convert Decimal to float for JSON serialization
        if "price" in data and isinstance(data["price"], Decimal):
            data["price"] = float(data["price"])
        return data

    def to_card_dict(self) -> Dict[str, Any]:
        """
        Convert to card format for chat display.

        Returns:
            Dictionary with card-friendly fields
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description[:200] if self.description else None,
            "price": float(self.price),
            "category": self.category,
            "image_url": self.image_url,
        }

    def get_search_text(self) -> str:
        """
        Get combined search text for full-text search.

        Returns:
            Combined name and description text
        """
        text = self.name
        if self.description:
            text += " " + self.description
        if self.category:
            text += " " + self.category
        return text


class ProductCreate(BaseModel):
    """Schema for creating a new product"""

    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    stock_quantity: int = Field(default=0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProductUpdate(BaseModel):
    """Schema for updating a product"""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


__all__ = ["Product", "ProductCreate", "ProductUpdate"]
