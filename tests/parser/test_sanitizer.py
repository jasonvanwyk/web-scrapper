"""
Unit tests for the sanitizer module.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.parser.sanitizer import (
    sanitize_product_data, sanitize_text_field, sanitize_numeric_field,
    sanitize_list_field, sanitize_url_field
)


class TestSanitizer(unittest.TestCase):
    """Test cases for the sanitizer module."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample raw data for testing
        self.raw_data = {
            "product_name": "  Test Product  ",
            "sku": " ABC-123 ",
            "description": "<p>This is a <b>test</b> description.</p>",
            "supplier_name": " Test Supplier ",
            "cost": "$10.99",
            "price": "€20,50",
            "colorways": ["Red ", " Blue", "Green"],
            "image_url": "/images/test.jpg"
        }
        
        # Sample data with missing fields
        self.incomplete_data = {
            "product_name": "Incomplete Product",
            "sku": "INC-123"
        }
        
        # Sample data with error field
        self.error_data = {
            "product_name": "",
            "error": "Failed to extract data"
        }
        
        # Sample data with invalid values
        self.invalid_data = {
            "product_name": "Invalid Product",
            "sku": "INV-123",
            "cost": "not a price",
            "price": "invalid",
            "colorways": None,
            "image_url": 12345  # Not a string
        }

    def test_sanitize_product_data_complete(self):
        """Test sanitizing complete product data."""
        sanitized = sanitize_product_data(self.raw_data, "https://example.com")
        
        # Check if all fields are present and properly sanitized
        self.assertEqual(sanitized["product_name"], "Test Product")
        self.assertEqual(sanitized["sku"], "ABC-123")
        self.assertEqual(sanitized["description"], "This is a test description.")
        self.assertEqual(sanitized["supplier_name"], "Test Supplier")
        self.assertEqual(sanitized["cost"], 10.99)
        self.assertEqual(sanitized["price"], 20.50)
        self.assertEqual(sanitized["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(sanitized["image_url"], "https://example.com/images/test.jpg")

    def test_sanitize_product_data_incomplete(self):
        """Test sanitizing incomplete product data."""
        sanitized = sanitize_product_data(self.incomplete_data)
        
        # Check if missing fields are added with default values
        self.assertEqual(sanitized["product_name"], "Incomplete Product")
        self.assertEqual(sanitized["sku"], "INC-123")
        self.assertEqual(sanitized["description"], "")
        self.assertEqual(sanitized["supplier_name"], "")
        self.assertEqual(sanitized["cost"], 0.0)
        self.assertEqual(sanitized["price"], 0.0)
        self.assertEqual(sanitized["colorways"], [])
        self.assertEqual(sanitized["image_url"], "")

    def test_sanitize_product_data_with_error(self):
        """Test sanitizing data with error field."""
        sanitized = sanitize_product_data(self.error_data)
        
        # Check if error field is preserved
        self.assertEqual(sanitized["error"], "Failed to extract data")
        self.assertEqual(sanitized["product_name"], "")

    def test_sanitize_product_data_with_invalid_values(self):
        """Test sanitizing data with invalid values."""
        sanitized = sanitize_product_data(self.invalid_data)
        
        # Check if invalid values are properly handled
        self.assertEqual(sanitized["cost"], 0.0)
        self.assertEqual(sanitized["price"], 0.0)
        self.assertEqual(sanitized["colorways"], [])
        self.assertEqual(sanitized["image_url"], "")

    def test_sanitize_product_data_empty(self):
        """Test sanitizing empty data."""
        with self.assertLogs(level='WARNING'):
            sanitized = sanitize_product_data({})
        
        # Check if all fields are added with default values
        self.assertEqual(sanitized["product_name"], "")
        self.assertEqual(sanitized["sku"], "")
        self.assertEqual(sanitized["description"], "")
        self.assertEqual(sanitized["supplier_name"], "")
        self.assertEqual(sanitized["cost"], 0.0)
        self.assertEqual(sanitized["price"], 0.0)
        self.assertEqual(sanitized["colorways"], [])
        self.assertEqual(sanitized["image_url"], "")

    def test_sanitize_text_field(self):
        """Test sanitizing text fields."""
        # Test with normal string
        self.assertEqual(sanitize_text_field("  Test String  "), "Test String")
        
        # Test with None
        self.assertEqual(sanitize_text_field(None), "")
        
        # Test with non-string
        self.assertEqual(sanitize_text_field(123), "123")
        
        # Test with multiple spaces and newlines
        self.assertEqual(sanitize_text_field("Test  \n  String"), "Test String")

    def test_sanitize_numeric_field(self):
        """Test sanitizing numeric fields."""
        # Test with string containing currency symbol
        self.assertEqual(sanitize_numeric_field("$10.99"), 10.99)
        
        # Test with European format
        self.assertEqual(sanitize_numeric_field("€20,50"), 20.50)
        
        # Test with integer
        self.assertEqual(sanitize_numeric_field(15), 15.0)
        
        # Test with float
        self.assertEqual(sanitize_numeric_field(15.75), 15.75)
        
        # Test with None
        self.assertEqual(sanitize_numeric_field(None), 0.0)
        
        # Test with invalid string
        self.assertEqual(sanitize_numeric_field("not a price"), 0.0)
        
        # Test with custom default
        self.assertEqual(sanitize_numeric_field("invalid", 1.0), 1.0)

    def test_sanitize_list_field(self):
        """Test sanitizing list fields."""
        # Test with list of strings
        self.assertEqual(
            sanitize_list_field(["Red ", " Blue", "Green"]), 
            ["Red", "Blue", "Green"]
        )
        
        # Test with comma-separated string
        self.assertEqual(
            sanitize_list_field("Red, Blue, Green"), 
            ["Red", "Blue", "Green"]
        )
        
        # Test with custom delimiter
        self.assertEqual(
            sanitize_list_field("Red|Blue|Green", "|"), 
            ["Red", "Blue", "Green"]
        )
        
        # Test with None
        self.assertEqual(sanitize_list_field(None), [])
        
        # Test with empty list
        self.assertEqual(sanitize_list_field([]), [])
        
        # Test with empty string
        self.assertEqual(sanitize_list_field(""), [])

    def test_sanitize_url_field(self):
        """Test sanitizing URL fields."""
        # Test with relative URL and base URL
        self.assertEqual(
            sanitize_url_field("/images/test.jpg", "https://example.com"), 
            "https://example.com/images/test.jpg"
        )
        
        # Test with absolute URL
        self.assertEqual(
            sanitize_url_field("https://example.org/images/test.jpg", "https://example.com"), 
            "https://example.org/images/test.jpg"
        )
        
        # Test with None
        self.assertEqual(sanitize_url_field(None), "")
        
        # Test with empty string
        self.assertEqual(sanitize_url_field(""), "")
        
        # Test with non-string
        self.assertEqual(sanitize_url_field(12345), "")
        
        # Test with no base URL
        self.assertEqual(sanitize_url_field("/images/test.jpg"), "/images/test.jpg")


if __name__ == "__main__":
    unittest.main()
