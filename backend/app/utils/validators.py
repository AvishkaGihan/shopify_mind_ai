"""
Data validation utilities.

Provides functions for validating:
- Email addresses
- Passwords
- CSV data
- User input sanitization
"""

# type: ignore[call-arg]  # Suppress false positive about missing 'details' parameter in ValidationException

import re
from typing import Optional, Dict, Any, List
from decimal import Decimal, InvalidOperation
from app.utils.error_handler import ValidationException


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Uses RFC 5322 compliant regex pattern.

    Args:
        email: Email address to validate

    Returns:
        True if valid, raises ValidationException if invalid

    Raises:
        ValidationException: If email format is invalid

    Example:
        validate_email("user@example.com")  # True
        validate_email("invalid.email")  # Raises ValidationException
    """
    if not email or not isinstance(email, str):
        raise ValidationException(
            message="Email is required", details={"field": "email"}
        )

    # RFC 5322 compliant email regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        raise ValidationException(
            message="Invalid email format", details={"field": "email", "value": email}
        )

    if len(email) > 255:
        raise ValidationException(
            message="Email is too long (max 255 characters)", details={"field": "email"}
        )

    return True


def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Validate password strength.

    Requirements:
    - Minimum length (default 8)
    - At least one letter (optional, can add more rules)

    Args:
        password: Password to validate
        min_length: Minimum password length

    Returns:
        True if valid, raises ValidationException if invalid

    Raises:
        ValidationException: If password doesn't meet requirements

    Example:
        validate_password("MySecurePass123")  # True
        validate_password("short")  # Raises ValidationException
    """
    if not password or not isinstance(password, str):
        raise ValidationException(
            message="Password is required", details={"field": "password"}
        )

    if len(password) < min_length:
        raise ValidationException(
            message=f"Password must be at least {min_length} characters long",
            details={"field": "password", "min_length": min_length},
        )

    if len(password) > 128:
        raise ValidationException(
            message="Password is too long (max 128 characters)",
            details={"field": "password"},
        )

    # Optional: Add more strength requirements
    # Uncomment for Pro tier with stronger requirements
    """
    if not re.search(r'[A-Z]', password):
        raise ValidationException(
            message="Password must contain at least one uppercase letter"
        )

    if not re.search(r'[a-z]', password):
        raise ValidationException(
            message="Password must contain at least one lowercase letter"
        )

    if not re.search(r'[0-9]', password):
        raise ValidationException(
            message="Password must contain at least one number"
        )
    """

    return True


def validate_csv_row(
    row: Dict[str, Any], required_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate and clean CSV row data.

    Args:
        row: CSV row as dictionary
        required_fields: List of required field names

    Returns:
        Validated and cleaned row data

    Raises:
        ValidationException: If validation fails

    Example:
        row = {"name": "Product", "price": "29.99", "category": "Electronics"}
        validated = validate_csv_row(row, required_fields=["name", "price"])
    """
    if not row or not isinstance(row, dict):
        raise ValidationException(
            message="Invalid CSV row format", details={"row": row}
        )

    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if not row.get(field)]
        if missing_fields:
            raise ValidationException(
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields, "row": row},
            )

    # Validate and clean data
    validated_row = {}

    # Name (required)
    name = row.get("name", "").strip()
    if not name:
        raise ValidationException(
            message="Product name is required", details={"row": row}
        )
    if len(name) > 255:
        raise ValidationException(
            message="Product name is too long (max 255 characters)",
            details={"name": name},
        )
    validated_row["name"] = name

    # Price (required)
    try:
        price_str = str(row.get("price", "")).strip().replace("$", "").replace(",", "")
        price = Decimal(price_str)
        if price < 0:
            raise ValidationException(
                message="Price cannot be negative", details={"price": price_str}
            )
        validated_row["price"] = float(price)
    except (InvalidOperation, ValueError):
        raise ValidationException(
            message="Invalid price format", details={"price": row.get("price")}
        )

    # Description (optional)
    description = row.get("description", "").strip()
    if description:
        if len(description) > 5000:
            description = description[:5000]  # Truncate if too long
        validated_row["description"] = description

    # Category (optional)
    category = row.get("category", "").strip()
    if category:
        if len(category) > 100:
            category = category[:100]
        validated_row["category"] = category

    # SKU (optional)
    sku = row.get("sku", "").strip()
    if sku:
        # Alphanumeric and hyphens only
        if not re.match(r"^[a-zA-Z0-9-_]+$", sku):
            raise ValidationException(
                message="SKU can only contain letters, numbers, hyphens, and underscores",
                details={"sku": sku},
            )
        if len(sku) > 100:
            sku = sku[:100]
        validated_row["sku"] = sku

    # Image URL (optional)
    image_url = row.get("image_url", "").strip()
    if image_url:
        # Basic URL validation
        if not re.match(r"^https?://", image_url):
            raise ValidationException(
                message="Image URL must start with http:// or https://",
                details={"image_url": image_url},
            )
        if len(image_url) > 500:
            raise ValidationException(
                message="Image URL is too long (max 500 characters)",
                details={"image_url": image_url},
            )
        validated_row["image_url"] = image_url

    return validated_row


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Example:
        sanitized = sanitize_input("<script>alert('xss')</script>", max_length=100)
        # Returns: "alert('xss')" (without script tags)
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace
    text = " ".join(text.split())

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def validate_order_id(order_id: str) -> bool:
    """
    Validate order ID format.

    Args:
        order_id: Order ID to validate

    Returns:
        True if valid, raises ValidationException if invalid

    Raises:
        ValidationException: If order ID format is invalid
    """
    if not order_id or not isinstance(order_id, str):
        raise ValidationException(
            message="Order ID is required", details={"field": "order_id"}
        )

    # Allow alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9-_]+$", order_id):
        raise ValidationException(
            message="Order ID can only contain letters, numbers, hyphens, and underscores",
            details={"order_id": order_id},
        )

    if len(order_id) > 50:
        raise ValidationException(
            message="Order ID is too long (max 50 characters)",
            details={"order_id": order_id},
        )

    return True


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (basic).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, raises ValidationException if invalid

    Raises:
        ValidationException: If phone format is invalid
    """
    if not phone:
        return True  # Phone is optional

    # Remove common formatting characters
    phone_cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)

    # Check if it's all digits (10-15 digits typical)
    if not re.match(r"^\d{10,15}$", phone_cleaned):
        raise ValidationException(
            message="Invalid phone number format", details={"phone": phone}
        )

    return True


def validate_json_field(data: Any, field_name: str, required: bool = False) -> bool:
    """
    Validate JSON field data.

    Args:
        data: Data to validate
        field_name: Name of the field (for error messages)
        required: Whether field is required

    Returns:
        True if valid, raises ValidationException if invalid

    Raises:
        ValidationException: If validation fails
    """
    if data is None:
        if required:
            raise ValidationException(
                message=f"{field_name} is required", details={"field": field_name}
            )
        return True

    # Check if it's a valid JSON-serializable type
    try:
        import json

        json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValidationException(
            message=f"Invalid {field_name} format",
            details={"field": field_name, "error": str(e)},
        )

    return True


# Export for easy imports
__all__ = [
    "validate_email",
    "validate_password",
    "validate_csv_row",
    "sanitize_input",
    "validate_order_id",
    "validate_phone_number",
    "validate_json_field",
]
