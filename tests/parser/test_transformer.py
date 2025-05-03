"""
Unit tests for the transformer module.

This module tests the data sanitization, normalization, and validation
functions in the transformer module.
"""

import sys
import os
import unittest
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path to allow imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import the transformer module
try:
    from src.parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, validate_sku_format, validate_required_field,
        sanitize_html_content, normalize_url, validate_url,
        clean_and_validate_product_data, ProductData
    )
except ImportError:
    from parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, validate_sku_format, validate_required_field,
        sanitize_html_content, normalize_url, validate_url,
        clean_and_validate_product_data, ProductData
    )


class TestTransformerBasicFunctions(unittest.TestCase):
    """Test basic sanitization and normalization functions."""

    def test_strip_whitespace(self):
        """Test stripping whitespace from text."""
        # Test with normal text
        self.assertEqual(strip_whitespace("  Hello  World  "), "Hello World")
        
        # Test with tabs and newlines
        self.assertEqual(strip_whitespace("Hello\tWorld\n"), "Hello World")
        
        # Test with None
        self.assertEqual(strip_whitespace(None), "")
        
        # Test with empty string
        self.assertEqual(strip_whitespace(""), "")

    def test_to_float(self):
        """Test converting text to float."""
        # Test with simple number
        self.assertAlmostEqual(to_float("123.45"), 123.45)
        
        # Test with currency symbol
        self.assertAlmostEqual(to_float("$123.45"), 123.45)
        
        # Test with European format (comma as decimal)
        self.assertAlmostEqual(to_float("123,45"), 123.45)
        
        # Test with European format (period as thousands separator)
        self.assertAlmostEqual(to_float("1.234,56"), 1234.56)
        
        # Test with US format (comma as thousands separator)
        self.assertAlmostEqual(to_float("1,234.56"), 1234.56)
        
        # Test with None
        self.assertAlmostEqual(to_float(None), 0.0)
        
        # Test with empty string
        self.assertAlmostEqual(to_float(""), 0.0)
        
        # Test with non-numeric text
        self.assertAlmostEqual(to_float("abc"), 0.0)
        
        # Test with custom default
        self.assertAlmostEqual(to_float("abc", default=1.0), 1.0)
        
        # Test with different currency symbols
        self.assertAlmostEqual(to_float("€123.45"), 123.45)
        self.assertAlmostEqual(to_float("£123.45"), 123.45)
        self.assertAlmostEqual(to_float("¥123.45"), 123.45)

    def test_normalize_text(self):
        """Test normalizing text by removing extra whitespace, newlines, and tabs."""
        # Test with normal text
        self.assertEqual(normalize_text("Hello World"), "Hello World")
        
        # Test with extra whitespace
        self.assertEqual(normalize_text("  Hello  World  "), "Hello World")
        
        # Test with newlines and tabs
        self.assertEqual(normalize_text("Hello\nWorld\tTest"), "Hello World Test")
        
        # Test with None
        self.assertEqual(normalize_text(None), "")
        
        # Test with empty string
        self.assertEqual(normalize_text(""), "")

    def test_normalize_list(self):
        """Test normalizing a list of items."""
        # Test with list of strings
        self.assertEqual(normalize_list(["Red", "Green", "Blue"]), ["Red", "Green", "Blue"])
        
        # Test with list containing whitespace
        self.assertEqual(normalize_list(["  Red  ", " Green ", "Blue  "]), ["Red", "Green", "Blue"])
        
        # Test with comma-separated string
        self.assertEqual(normalize_list("Red, Green, Blue"), ["Red", "Green", "Blue"])
        
        # Test with empty items in list
        self.assertEqual(normalize_list(["Red", "", "Blue"]), ["Red", "Blue"])
        
        # Test with None
        self.assertEqual(normalize_list(None), [])
        
        # Test with empty string
        self.assertEqual(normalize_list(""), [])
        
        # Test with custom delimiter
        self.assertEqual(normalize_list("Red|Green|Blue", delimiter="|"), ["Red", "Green", "Blue"])

    def test_normalize_currency(self):
        """Test normalizing currency values and extracting currency symbol."""
        # Test with USD
        result = normalize_currency("$123.45")
        self.assertAlmostEqual(result["value"], 123.45)
        self.assertEqual(result["currency"], "$")
        
        # Test with EUR
        result = normalize_currency("€123.45")
        self.assertAlmostEqual(result["value"], 123.45)
        self.assertEqual(result["currency"], "€")
        
        # Test with currency code
        result = normalize_currency("USD 123.45")
        self.assertAlmostEqual(result["value"], 123.45)
        self.assertEqual(result["currency"], "USD")
        
        # Test with no currency symbol
        result = normalize_currency("123.45")
        self.assertAlmostEqual(result["value"], 123.45)
        self.assertEqual(result["currency"], "")
        
        # Test with custom currency symbol
        result = normalize_currency("123.45", currency_symbol="$")
        self.assertAlmostEqual(result["value"], 123.45)
        self.assertEqual(result["currency"], "$")
        
        # Test with None
        result = normalize_currency(None)
        self.assertAlmostEqual(result["value"], 0.0)
        self.assertEqual(result["currency"], "")


class TestTransformerValidationFunctions(unittest.TestCase):
    """Test validation functions."""

    def test_validate_sku_format(self):
        """Test validating SKU format."""
        # Test with valid SKU
        self.assertTrue(validate_sku_format("ABC123"))
        
        # Test with valid SKU containing dash and underscore
        self.assertTrue(validate_sku_format("ABC-123_XYZ"))
        
        # Test with too short SKU
        self.assertFalse(validate_sku_format("AB"))
        
        # Test with invalid characters
        self.assertFalse(validate_sku_format("ABC 123"))
        self.assertFalse(validate_sku_format("ABC@123"))
        
        # Test with None
        self.assertFalse(validate_sku_format(None))
        
        # Test with empty string
        self.assertFalse(validate_sku_format(""))

    def test_validate_required_field(self):
        """Test validating if a required field has a value."""
        # Test with string
        self.assertTrue(validate_required_field("Hello"))
        
        # Test with empty string
        self.assertFalse(validate_required_field(""))
        
        # Test with whitespace-only string
        self.assertFalse(validate_required_field("   "))
        
        # Test with None
        self.assertFalse(validate_required_field(None))
        
        # Test with number
        self.assertTrue(validate_required_field(123))
        
        # Test with zero
        self.assertTrue(validate_required_field(0))
        
        # Test with list
        self.assertTrue(validate_required_field([1, 2, 3]))
        
        # Test with empty list
        self.assertTrue(validate_required_field([]))

    def test_validate_url(self):
        """Test validating URL format."""
        # Test with valid HTTP URL
        self.assertTrue(validate_url("http://example.com"))
        
        # Test with valid HTTPS URL
        self.assertTrue(validate_url("https://example.com"))
        
        # Test with valid URL with path
        self.assertTrue(validate_url("https://example.com/path/to/resource"))
        
        # Test with valid URL with query parameters
        self.assertTrue(validate_url("https://example.com/search?q=test"))
        
        # Test with invalid URL (no protocol)
        self.assertFalse(validate_url("example.com"))
        
        # Test with invalid URL (invalid characters)
        self.assertFalse(validate_url("https://example com"))
        
        # Test with empty string
        self.assertFalse(validate_url(""))
        
        # Test with None (should be handled by the function)
        with self.assertRaises(TypeError):
            validate_url(None)


class TestTransformerEnhancedFunctions(unittest.TestCase):
    """Test enhanced sanitization and normalization functions."""

    def test_sanitize_html_content(self):
        """Test removing HTML tags and decoding HTML entities."""
        # Test with HTML tags
        self.assertEqual(sanitize_html_content("<p>Hello World</p>"), "Hello World")
        
        # Test with nested HTML tags
        self.assertEqual(
            sanitize_html_content("<div><p>Hello <strong>World</strong></p></div>"), 
            "Hello World"
        )
        
        # Test with HTML entities
        self.assertEqual(sanitize_html_content("Hello &amp; World"), "Hello & World")
        
        # Test with mixed HTML tags and entities
        self.assertEqual(
            sanitize_html_content("<p>Hello &amp; <strong>World</strong></p>"), 
            "Hello & World"
        )
        
        # Test with None
        self.assertEqual(sanitize_html_content(None), "")
        
        # Test with empty string
        self.assertEqual(sanitize_html_content(""), "")

    def test_normalize_url(self):
        """Test normalizing URL by converting relative URLs to absolute URLs."""
        # Test with absolute URL
        self.assertEqual(
            normalize_url("https://example.com/image.jpg"), 
            "https://example.com/image.jpg"
        )
        
        # Test with relative URL and base URL
        self.assertEqual(
            normalize_url("/image.jpg", "https://example.com"), 
            "https://example.com/image.jpg"
        )
        
        # Test with relative URL (no leading slash) and base URL
        self.assertEqual(
            normalize_url("image.jpg", "https://example.com"), 
            "https://example.com/image.jpg"
        )
        
        # Test with relative URL and base URL with path
        self.assertEqual(
            normalize_url("image.jpg", "https://example.com/products/"), 
            "https://example.com/products/image.jpg"
        )
        
        # Test with None
        self.assertEqual(normalize_url(None), "")
        
        # Test with empty string
        self.assertEqual(normalize_url(""), "")
        
        # Test with None base URL
        self.assertEqual(normalize_url("/image.jpg", None), "/image.jpg")


class TestProductDataModel(unittest.TestCase):
    """Test the Pydantic model for product data validation."""

    def test_product_data_model_valid(self):
        """Test creating a ProductData instance with valid data."""
        data = {
            "product_name": "Example Product",
            "sku": "EX12345",
            "description": "This is an example product.",
            "supplier_name": "Example Supplier",
            "cost": 45.0,
            "price": 89.99,
            "colorways": ["Black", "White", "Silver"],
            "image_url": "https://example.com/image.jpg"
        }
        
        product = ProductData(**data)
        
        self.assertEqual(product.product_name, "Example Product")
        self.assertEqual(product.sku, "EX12345")
        self.assertEqual(product.description, "This is an example product.")
        self.assertEqual(product.supplier_name, "Example Supplier")
        self.assertAlmostEqual(product.cost, 45.0)
        self.assertAlmostEqual(product.price, 89.99)
        self.assertEqual(product.colorways, ["Black", "White", "Silver"])
        self.assertEqual(product.image_url, "https://example.com/image.jpg")

    def test_product_data_model_defaults(self):
        """Test creating a ProductData instance with minimal data."""
        # Create with minimal data
        product = ProductData()
        
        # Check defaults
        self.assertEqual(product.product_name, "")
        self.assertEqual(product.sku, "")
        self.assertEqual(product.description, "")
        self.assertEqual(product.supplier_name, "")
        self.assertAlmostEqual(product.cost, 0.0)
        self.assertAlmostEqual(product.price, 0.0)
        self.assertEqual(product.colorways, [])
        self.assertEqual(product.image_url, "")

    def test_product_data_model_validation(self):
        """Test validation in the ProductData model."""
        # Test with negative price (should be corrected to 0.0)
        data = {
            "product_name": "Example Product",
            "sku": "EX12345",
            "price": -10.0
        }
        
        product = ProductData(**data)
        self.assertAlmostEqual(product.price, 0.0)
        
        # Test with invalid SKU (should be accepted but logged)
        data = {
            "product_name": "Example Product",
            "sku": "A"  # Too short
        }
        
        product = ProductData(**data)
        self.assertEqual(product.sku, "A")  # Still accepted despite being invalid


class TestCleanAndValidateProductData(unittest.TestCase):
    """Test the clean_and_validate_product_data function."""

    def test_clean_and_validate_valid_data(self):
        """Test cleaning and validating valid product data."""
        data = {
            "product_name": "  Example Product  ",
            "sku": "  EX12345  ",
            "description": "<p>This is an <strong>example</strong> product.</p>",
            "supplier_name": "Example Supplier\n",
            "cost": "$45.00",
            "price": "€89,99",
            "colorways": ["  Black  ", "White", "  Silver  "],
            "image_url": "/image.jpg"
        }
        
        result = clean_and_validate_product_data(
            data, 
            required_fields=["product_name", "sku"],
            base_url="https://example.com"
        )
        
        # Check cleaned values
        self.assertEqual(result["product_name"], "Example Product")
        self.assertEqual(result["sku"], "EX12345")
        self.assertEqual(result["description"], "This is an example product.")
        self.assertEqual(result["supplier_name"], "Example Supplier")
        self.assertAlmostEqual(result["cost"], 45.0)
        self.assertAlmostEqual(result["price"], 89.99)
        self.assertEqual(result["colorways"], ["Black", "White", "Silver"])
        self.assertEqual(result["image_url"], "https://example.com/image.jpg")
        
        # Check validation result
        self.assertTrue(result["validation"]["is_valid"])
        self.assertEqual(result["validation"]["missing_required_fields"], [])

    def test_clean_and_validate_missing_required_fields(self):
        """Test cleaning and validating data with missing required fields."""
        data = {
            "product_name": "",  # Empty required field
            "sku": "EX12345",
            "description": "This is an example product."
        }
        
        result = clean_and_validate_product_data(
            data, 
            required_fields=["product_name", "sku"]
        )
        
        # Check validation result
        self.assertFalse(result["validation"]["is_valid"])
        self.assertIn("product_name", result["validation"]["missing_required_fields"])

    def test_clean_and_validate_with_error(self):
        """Test cleaning and validating data with an error field."""
        data = {
            "product_name": "Example Product",
            "sku": "EX12345",
            "error": "Failed to extract data"
        }
        
        result = clean_and_validate_product_data(data)
        
        # Check that error is preserved
        self.assertEqual(result["error"], "Failed to extract data")
        
        # Check that other fields are still present
        self.assertEqual(result["product_name"], "Example Product")
        self.assertEqual(result["sku"], "EX12345")

    def test_clean_and_validate_with_different_types(self):
        """Test cleaning and validating data with different types."""
        data = {
            "product_name": "Example Product",
            "sku": "EX12345",
            "cost": 45.0,  # Float
            "price": "89.99",  # String
            "colorways": "Black, White, Silver"  # Comma-separated string
        }
        
        result = clean_and_validate_product_data(data)
        
        # Check type conversions
        self.assertAlmostEqual(result["cost"], 45.0)
        self.assertAlmostEqual(result["price"], 89.99)
        self.assertEqual(result["colorways"], ["Black", "White", "Silver"])


if __name__ == "__main__":
    unittest.main()
