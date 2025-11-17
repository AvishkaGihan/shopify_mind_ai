"""
Order model representing customer orders.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr


class OrderItem(BaseModel):
    """
    Individual item in an order.

    Attributes:
        product_id: Product UUID (optional)
        product_name: Product name
        quantity: Quantity ordered
        price: Price per unit
    """

    product_id: Optional[str] = Field(None, description="Product UUID")
    product_name: str = Field(..., description="Product name")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    price: Decimal = Field(..., gt=0, description="Price per unit")

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "product_id": "123e4567-e89b-12d3-a456-426614174000",
                "product_name": "Wireless Headphones",
                "quantity": 2,
                "price": 129.99,
            }
        }

    def get_subtotal(self) -> Decimal:
        """Calculate item subtotal"""
        return self.price * self.quantity


class Address(BaseModel):
    """
    Shipping or billing address.

    Attributes:
        line1: Address line 1
        line2: Address line 2 (optional)
        city: City
        state: State/province
        postal_code: Postal/ZIP code
        country: Country code
    """

    line1: str = Field(..., description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State/province")
    postal_code: str = Field(..., description="Postal/ZIP code")
    country: str = Field(default="US", description="Country code")

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "US",
            }
        }


class OrderStatus:
    """Order status constants"""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"

    @classmethod
    def get_all(cls) -> List[str]:
        """Get all valid status values"""
        return [
            cls.PENDING,
            cls.PROCESSING,
            cls.SHIPPED,
            cls.IN_TRANSIT,
            cls.OUT_FOR_DELIVERY,
            cls.DELIVERED,
            cls.CANCELLED,
            cls.REFUNDED,
            cls.FAILED,
        ]

    @classmethod
    def get_color(cls, status: str) -> str:
        """Get color for status badge"""
        color_map = {
            cls.PENDING: "#FBC02D",  # Yellow
            cls.PROCESSING: "#FBC02D",  # Yellow
            cls.SHIPPED: "#2196F3",  # Blue
            cls.IN_TRANSIT: "#2196F3",  # Blue
            cls.OUT_FOR_DELIVERY: "#2196F3",  # Blue
            cls.DELIVERED: "#4CAF50",  # Green
            cls.CANCELLED: "#F44336",  # Red
            cls.REFUNDED: "#F44336",  # Red
            cls.FAILED: "#F44336",  # Red
        }
        return color_map.get(status, "#999999")


class Order(BaseModel):
    """
    Order model representing a customer order.

    Attributes:
        id: Unique order identifier (UUID, internal)
        user_id: Store owner UUID
        order_id: Human-readable order number
        customer_email: Customer email address
        customer_name: Customer full name
        customer_phone: Customer phone number
        items: List of order items
        subtotal: Order subtotal before tax and shipping
        tax: Tax amount
        shipping: Shipping cost
        total: Total order amount
        status: Order status
        payment_status: Payment status
        shipping_address: Shipping address
        billing_address: Billing address
        estimated_delivery: Estimated delivery date
        actual_delivery: Actual delivery date
        tracking_number: Carrier tracking number
        tracking_url: URL to carrier tracking page
        notes: Internal notes or customer comments
        created_at: Order creation timestamp
        updated_at: Last update timestamp
    """

    id: Optional[str] = Field(None, description="Order UUID (internal)")
    user_id: Optional[str] = Field(None, description="Store owner UUID")
    order_id: str = Field(..., max_length=50, description="Order number")
    customer_email: EmailStr = Field(..., description="Customer email")
    customer_name: Optional[str] = Field(
        None, max_length=255, description="Customer name"
    )
    customer_phone: Optional[str] = Field(
        None, max_length=50, description="Customer phone"
    )
    items: List[OrderItem] = Field(..., description="Order items")
    subtotal: Decimal = Field(..., ge=0, description="Subtotal")
    tax: Decimal = Field(default=Decimal("0"), ge=0, description="Tax amount")
    shipping: Decimal = Field(default=Decimal("0"), ge=0, description="Shipping cost")
    total: Decimal = Field(..., ge=0, description="Total amount")
    status: str = Field(default=OrderStatus.PENDING, description="Order status")
    payment_status: str = Field(default="pending", description="Payment status")
    shipping_address: Optional[Address] = Field(None, description="Shipping address")
    billing_address: Optional[Address] = Field(None, description="Billing address")
    estimated_delivery: Optional[datetime] = Field(
        None, description="Estimated delivery"
    )
    actual_delivery: Optional[datetime] = Field(None, description="Actual delivery")
    tracking_number: Optional[str] = Field(
        None, max_length=255, description="Tracking number"
    )
    tracking_url: Optional[str] = Field(
        None, max_length=500, description="Tracking URL"
    )
    notes: Optional[str] = Field(None, description="Notes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        """Pydantic configuration"""

        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "order_id": "ORD-12345",
                "customer_email": "customer@example.com",
                "customer_name": "John Doe",
                "items": [
                    {
                        "product_name": "Wireless Headphones",
                        "quantity": 2,
                        "price": 129.99,
                    }
                ],
                "subtotal": 259.98,
                "tax": 23.40,
                "shipping": 10.00,
                "total": 293.38,
                "status": "shipped",
                "tracking_number": "TRK1234567890",
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary representation
        """
        data = self.model_dump()
        # Convert Decimals to floats
        for key in ["subtotal", "tax", "shipping", "total"]:
            if key in data and isinstance(data[key], Decimal):
                data[key] = float(data[key])
        return data

    def to_status_card_dict(self) -> Dict[str, Any]:
        """
        Convert to status card format for chat display.

        Returns:
            Dictionary formatted for order status card
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "items": [
                {
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "price": float(item.price),
                }
                for item in self.items
            ],
            "total": float(self.total),
            "status": self.status,
            "status_color": OrderStatus.get_color(self.status),
            "estimated_delivery": (
                self.estimated_delivery.isoformat() if self.estimated_delivery else None
            ),
            "tracking_number": self.tracking_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def calculate_totals(self):
        """Recalculate order totals from items"""
        self.subtotal = Decimal(sum(item.get_subtotal() for item in self.items))
        self.total = self.subtotal + self.tax + self.shipping


class OrderCreate(BaseModel):
    """Schema for creating a new order"""

    order_id: str = Field(..., max_length=50)
    customer_email: EmailStr
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=50)
    items: List[OrderItem]
    subtotal: Decimal = Field(..., ge=0)
    tax: Decimal = Field(default=Decimal("0"), ge=0)
    shipping: Decimal = Field(default=Decimal("0"), ge=0)
    total: Decimal = Field(..., ge=0)
    status: str = Field(default=OrderStatus.PENDING)
    shipping_address: Optional[Address] = None
    estimated_delivery: Optional[datetime] = None
    tracking_number: Optional[str] = None


class OrderUpdate(BaseModel):
    """Schema for updating an order"""

    status: Optional[str] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    notes: Optional[str] = None


__all__ = [
    "Order",
    "OrderItem",
    "OrderStatus",
    "Address",
    "OrderCreate",
    "OrderUpdate",
]
