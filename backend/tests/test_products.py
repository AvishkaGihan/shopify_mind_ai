"""
Tests for product management endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Fixture to get authentication token"""
    # Signup and login
    client.post(
        "/auth/signup",
        json={
            "email": "producttest@example.com",
            "password": "SecurePass123",
            "store_name": "Product Test Store",
        },
    )

    response = client.post(
        "/auth/login",
        json={"email": "producttest@example.com", "password": "SecurePass123"},
    )

    return response.json()["data"]["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Fixture to get authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestProductEndpoints:
    """Test suite for product management endpoints"""

    def test_upload_csv_success(self, auth_headers):
        """Test successful CSV upload"""
        # Create a simple CSV
        csv_content = b"""name,price,description,category
Wireless Headphones,129.99,High-quality headphones,Electronics
Smart Watch,249.99,Fitness tracking watch,Electronics
"""

        files = {"file": ("products.csv", BytesIO(csv_content), "text/csv")}

        response = client.post("/products/upload", headers=auth_headers, files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["inserted"] == 2
        assert data["data"]["failed"] == 0

    def test_upload_csv_invalid_file(self, auth_headers):
        """Test CSV upload with invalid file"""
        files = {"file": ("products.txt", BytesIO(b"Not a CSV"), "text/plain")}

        response = client.post("/products/upload", headers=auth_headers, files=files)

        assert response.status_code == 400

    def test_upload_csv_validation_errors(self, auth_headers):
        """Test CSV upload with validation errors"""
        # CSV with invalid price
        csv_content = b"""name,price,description
Invalid Product,-10.00,This should fail
Valid Product,29.99,This should work
"""

        files = {"file": ("products.csv", BytesIO(csv_content), "text/csv")}

        response = client.post("/products/upload", headers=auth_headers, files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["failed"] > 0
        assert len(data["data"]["errors"]) > 0

    def test_list_products(self, auth_headers):
        """Test listing products"""
        response = client.get("/products", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "products" in data["data"]
        assert "total_count" in data["data"]

    def test_list_products_pagination(self, auth_headers):
        """Test product list pagination"""
        response = client.get("/products?limit=5&offset=0", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["products"]) <= 5

    def test_get_product_by_id(self, auth_headers):
        """Test getting product by ID"""
        # First, upload a product
        csv_content = b"""name,price,description
Test Product,19.99,Test description
"""

        files = {"file": ("products.csv", BytesIO(csv_content), "text/csv")}

        client.post("/products/upload", headers=auth_headers, files=files)

        # Get list of products
        list_response = client.get("/products", headers=auth_headers)

        products = list_response.json()["data"]["products"]

        if products:
            product_id = products[0]["id"]

            # Get specific product
            response = client.get(f"/products/{product_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["id"] == product_id

    def test_delete_product(self, auth_headers):
        """Test deleting a product"""
        # First, get a product ID
        list_response = client.get("/products", headers=auth_headers)

        products = list_response.json()["data"]["products"]

        if products:
            product_id = products[0]["id"]

            # Delete product
            response = client.delete(f"/products/{product_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["deleted_count"] == 1

    def test_delete_all_products(self, auth_headers):
        """Test deleting all products"""
        response = client.delete("/products", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_download_csv_template(self):
        """Test downloading CSV template"""
        response = client.get("/products/template/download")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "product_template.csv" in response.headers["content-disposition"]


class TestCSVService:
    """Test suite for CSVService methods"""

    def test_csv_row_validation(self):
        """Test CSV row validation"""
        from app.utils.validators import validate_csv_row

        # Valid row
        valid_row = {
            "name": "Test Product",
            "price": "29.99",
            "description": "Test description",
            "category": "Electronics",
        }

        result = validate_csv_row(valid_row, required_fields=["name", "price"])
        assert result["name"] == "Test Product"
        assert result["price"] == 29.99

    def test_csv_row_validation_invalid_price(self):
        """Test CSV row validation with invalid price"""
        from app.utils.validators import validate_csv_row
        from app.utils.error_handler import ValidationException

        invalid_row = {"name": "Test Product", "price": "-10.00"}  # Negative price

        with pytest.raises(ValidationException):
            validate_csv_row(invalid_row, required_fields=["name", "price"])

    def test_csv_row_validation_missing_required(self):
        """Test CSV row validation with missing required field"""
        from app.utils.validators import validate_csv_row
        from app.utils.error_handler import ValidationException

        invalid_row = {
            "price": "29.99"
            # Missing 'name'
        }

        with pytest.raises(ValidationException):
            validate_csv_row(invalid_row, required_fields=["name", "price"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
