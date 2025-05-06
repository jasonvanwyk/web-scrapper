"""
Unit tests for the Data Transformer module.
"""

import pytest
from src.parser.transformer import (
    strip_whitespace,
    to_float,
    normalize_currency,
    normalize_text,
    normalize_list,
    validate_sku_format,
    validate_required_field,
    clean_and_validate_product_data
)


class TestTransformer:
    """Test cases for the Data Transformer module."""
    
    def test_strip_whitespace(self):
        """Test stripping whitespace from text."""
        assert strip_whitespace("  Hello  World  ") == "Hello World"
        assert strip_whitespace("\n\tHello\nWorld\t") == "Hello World"
        assert strip_whitespace("") == ""
        assert strip_whitespace(None) == ""
        assert strip_whitespace("   ") == ""
    
    def test_to_float(self):
        """Test converting text to float."""
        # Basic conversions
        assert to_float("123.45") == 123.45
        assert to_float("123") == 123.0
        
        # Currency symbols
        assert to_float("$123.45") == 123.45
        assert to_float("€123.45") == 123.45
        assert to_float("£123.45") == 123.45
        assert to_float("¥123.45") == 123.45
        
        # Thousand separators
        assert to_float("1,234.56") == 1234.56
        
        # European format (period as thousand separator, comma as decimal)
        european_value = to_float("1.234,56", default=0.0)
        assert abs(european_value - 1234.56) < 0.001  # Allow small floating-point differences
        
        # Edge cases
        assert to_float("") == 0.0
        assert to_float(None) == 0.0
        assert to_float("invalid", default=99.99) == 99.99
        
        # Custom default
        assert to_float("invalid", default=42.0) == 42.0
    
    def test_normalize_currency(self):
        """Test normalizing currency values."""
        # Basic currency detection
        result = normalize_currency("$123.45")
        assert result["value"] == 123.45
        assert result["currency"] == "$"
        
        result = normalize_currency("€123.45")
        assert result["value"] == 123.45
        assert result["currency"] == "€"
        
        # With provided currency symbol
        result = normalize_currency("123.45", currency_symbol="USD")
        assert result["value"] == 123.45
        assert result["currency"] == "USD"
        
        # Edge cases
        result = normalize_currency("")
        assert result["value"] == 0.0
        assert result["currency"] == ""
        
        result = normalize_currency(None, default=99.99, currency_symbol="EUR")
        assert result["value"] == 99.99
        assert result["currency"] == "EUR"
    
    def test_normalize_text(self):
        """Test normalizing text."""
        assert normalize_text("Hello\nWorld") == "Hello World"
        assert normalize_text("Hello\tWorld") == "Hello World"
        assert normalize_text("Hello  World") == "Hello World"
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
    
    def test_normalize_list(self):
        """Test normalizing a list of items."""
        # String input
        assert normalize_list("Red, Blue, Green") == ["Red", "Blue", "Green"]
        assert normalize_list("Red,Blue,Green") == ["Red", "Blue", "Green"]
        
        # List input
        assert normalize_list(["Red", "Blue", "Green"]) == ["Red", "Blue", "Green"]
        assert normalize_list(["Red ", " Blue", "Green"]) == ["Red", "Blue", "Green"]
        
        # Mixed input with empty items
        assert normalize_list(["Red", "", "Green"]) == ["Red", "Green"]
        assert normalize_list("Red, , Green") == ["Red", "Green"]
        
        # Edge cases
        assert normalize_list("") == []
        assert normalize_list([]) == []
        assert normalize_list(None) == []
        
        # Custom delimiter
        assert normalize_list("Red|Blue|Green", delimiter="|") == ["Red", "Blue", "Green"]
    
    def test_validate_sku_format(self):
        """Test validating SKU format."""
        # Valid SKUs
        assert validate_sku_format("ABC123") is True
        assert validate_sku_format("123-456") is True
        assert validate_sku_format("SKU_123") is True
        
        # Invalid SKUs
        assert validate_sku_format("AB") is False  # Too short
        assert validate_sku_format("") is False
        assert validate_sku_format(None) is False
        assert validate_sku_format("SKU 123") is False  # Contains space
        assert validate_sku_format("SKU#123") is False  # Contains special char
    
    def test_validate_required_field(self):
        """Test validating required fields."""
        # Valid values
        assert validate_required_field("Hello") is True
        assert validate_required_field(123) is True
        assert validate_required_field(0) is True
        assert validate_required_field([1, 2, 3]) is True
        assert validate_required_field({"key": "value"}) is True
        
        # Invalid values
        assert validate_required_field("") is False
        assert validate_required_field("   ") is False
        assert validate_required_field(None) is False
    
    def test_clean_and_validate_product_data(self):
        """Test cleaning and validating product data."""
        # Valid data
        data = {
            "product_name": "Test Product",
            "sku": "ABC123",
            "description": "This is a test product.",
            "supplier_name": "Test Supplier",
            "price": "$123.45",
            "cost": "€100.00",
            "colorways": "Red, Blue, Green"
        }
        
        result = clean_and_validate_product_data(data)
        
        assert result["validation"]["is_valid"] is True
        assert len(result["validation"]["missing_required_fields"]) == 0
        
        assert result["product_name"] == "Test Product"
        assert result["sku"] == "ABC123"
        assert result["description"] == "This is a test product."
        assert result["supplier_name"] == "Test Supplier"
        assert result["price"] == 123.45
        assert result["cost"] == 100.0
        assert result["colorways"] == ["Red", "Blue", "Green"]
        
        # Invalid data (missing required fields)
        invalid_data = {
            "description": "This is a test product.",
            "supplier_name": "Test Supplier",
            "price": "$123.45"
        }
        
        result = clean_and_validate_product_data(invalid_data)
        
        assert result["validation"]["is_valid"] is False
        assert "product_name" in result["validation"]["missing_required_fields"]
        assert "sku" in result["validation"]["missing_required_fields"]
        
        # Custom required fields
        custom_required = {
            "product_name": "Test Product",
            "price": "$123.45"
        }
        
        result = clean_and_validate_product_data(custom_required, required_fields=["product_name", "price"])
        
        assert result["validation"]["is_valid"] is True
        assert len(result["validation"]["missing_required_fields"]) == 0
