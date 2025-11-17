"""
CSV parsing and product import service.
"""

import csv
import io
from typing import List, Dict, Any, Tuple
from fastapi import UploadFile

from app.config import get_settings
from app.database import Database
from app.utils.logger import get_logger
from app.utils.error_handler import ValidationException, FileUploadException
from app.utils.validators import validate_csv_row

logger = get_logger(__name__)
settings = get_settings()


class CSVService:
    """
    Service for CSV file parsing and product import.

    Handles:
    - CSV file validation
    - Product data parsing and validation
    - Bulk product insertion
    - Error reporting
    """

    def __init__(self, db: Database):
        """
        Initialize CSV service.

        Args:
            db: Database instance
        """
        self.db = db
        self.required_fields = ["name", "price"]
        self.optional_fields = ["description", "category", "sku", "image_url"]

    async def parse_csv_file(
        self, file: UploadFile
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse CSV file and validate product data.

        Args:
            file: Uploaded CSV file

        Returns:
            Tuple of (valid_products, errors)

        Raises:
            FileUploadException: If file is invalid

        Example:
            valid_products, errors = await csv_service.parse_csv_file(file)
        """
        # Validate file
        await self._validate_file(file)

        # Read file content
        content = await file.read()

        # Decode to string
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.error("CSV file encoding error")
            raise FileUploadException(
                "Invalid file encoding. Please use UTF-8 encoding."
            )

        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(text))

        # Validate headers
        if not csv_reader.fieldnames:
            raise FileUploadException("CSV file is empty or has no headers")

        self._validate_headers(list(csv_reader.fieldnames))

        # Parse rows
        valid_products = []
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (1 is header)
            try:
                # Validate and clean row
                validated_row = validate_csv_row(row, self.required_fields)
                valid_products.append(validated_row)

            except ValidationException as e:
                errors.append({"row": row_num, "error": e.message, "data": row})
            except Exception as e:
                errors.append({"row": row_num, "error": str(e), "data": row})

        # Check if we have too many products
        if len(valid_products) > settings.max_products_per_upload:
            raise FileUploadException(
                f"Too many products. Maximum {settings.max_products_per_upload} allowed.",
                details={
                    "total_products": len(valid_products),
                    "max_allowed": settings.max_products_per_upload,
                },
            )

        logger.info(
            "CSV parsed",
            extra={
                "total_rows": len(valid_products) + len(errors),
                "valid_rows": len(valid_products),
                "error_rows": len(errors),
            },
        )

        return valid_products, errors

    async def _validate_file(self, file: UploadFile):
        """
        Validate uploaded file.

        Args:
            file: Uploaded file

        Raises:
            FileUploadException: If file is invalid
        """
        # Check file exists
        if not file:
            raise FileUploadException("No file uploaded")

        # Check filename
        if not file.filename:
            raise FileUploadException("Invalid filename")

        # Check file extension
        if not file.filename.lower().endswith(".csv"):
            raise FileUploadException("Invalid file type. Please upload a CSV file.")

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        max_size = settings.get_max_upload_size_bytes()
        if file_size > max_size:
            raise FileUploadException(
                f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
                details={
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "max_size_mb": settings.max_upload_size_mb,
                },
            )

        logger.debug(
            "File validated", extra={"filename": file.filename, "size_bytes": file_size}
        )

    def _validate_headers(self, headers: List[str]):
        """
        Validate CSV headers.

        Args:
            headers: List of column headers

        Raises:
            FileUploadException: If required headers are missing
        """
        # Normalize headers (lowercase, strip whitespace)
        normalized_headers = [h.lower().strip() for h in headers]

        # Check required fields
        missing_fields = []
        for field in self.required_fields:
            if field.lower() not in normalized_headers:
                missing_fields.append(field)

        if missing_fields:
            raise FileUploadException(
                f"Missing required columns: {', '.join(missing_fields)}",
                details={
                    "missing_fields": missing_fields,
                    "required_fields": self.required_fields,
                    "found_headers": headers,
                },
            )

        logger.debug("CSV headers validated", extra={"headers": headers})

    async def import_products(
        self,
        user_id: str,
        products: List[Dict[str, Any]],
        replace_existing: bool = False,
    ) -> Dict[str, Any]:
        """
        Import products into database.

        Args:
            user_id: Store owner UUID
            products: List of validated product dicts
            replace_existing: If True, delete existing products first

        Returns:
            Dict with import results

        Example:
            result = await csv_service.import_products(user_id, products)
        """
        if not products:
            return {"total_rows": 0, "inserted": 0, "failed": 0, "errors": []}

        # Delete existing products if requested
        if replace_existing:
            logger.info("Deleting existing products", extra={"user_id": user_id})
            await self.db.delete_all_products(user_id)

        # Bulk insert products
        inserted_count = await self.db.bulk_insert_products(user_id, products)

        logger.info(
            "Products imported",
            extra={"user_id": user_id, "inserted_count": inserted_count},
        )

        return {
            "total_rows": len(products),
            "inserted": inserted_count,
            "failed": len(products) - inserted_count,
            "errors": [],
        }

    async def upload_and_import(
        self, user_id: str, file: UploadFile, replace_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Complete CSV upload and import workflow.

        Args:
            user_id: Store owner UUID
            file: Uploaded CSV file
            replace_existing: If True, delete existing products first

        Returns:
            Dict with complete import results

        Example:
            result = await csv_service.upload_and_import(user_id, file)
        """
        # Parse CSV
        valid_products, parse_errors = await self.parse_csv_file(file)

        # Import valid products
        if valid_products:
            import_result = await self.import_products(
                user_id=user_id,
                products=valid_products,
                replace_existing=replace_existing,
            )
        else:
            import_result = {"total_rows": 0, "inserted": 0, "failed": 0, "errors": []}

        # Combine results
        total_rows = len(valid_products) + len(parse_errors)

        result = {
            "total_rows": total_rows,
            "inserted": import_result["inserted"],
            "failed": len(parse_errors) + import_result["failed"],
            "errors": parse_errors,
        }

        logger.info(
            "CSV upload completed", extra={"user_id": user_id, "result": result}
        )

        return result

    def generate_csv_template(self) -> str:
        """
        Generate a CSV template with headers and example row.

        Returns:
            CSV template as string

        Example:
            template = csv_service.generate_csv_template()
        """
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=self.required_fields + self.optional_fields
        )

        # Write headers
        writer.writeheader()

        # Write example row
        writer.writerow(
            {
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": "129.99",
                "category": "Electronics",
                "sku": "WH-001",
                "image_url": "https://example.com/images/headphones.jpg",
            }
        )

        return output.getvalue()


__all__ = ["CSVService"]
