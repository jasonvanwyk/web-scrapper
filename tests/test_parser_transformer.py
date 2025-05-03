"""
Unit tests for the Parser & Transformer Module.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from bs4 import BeautifulSoup

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.parser.parser_transformer import (
        ParserTransformer, parse_html, parse_multiple_products, transform_data
    )
    # Define the module paths for patching based on how they're imported in parser_transformer.py
    HTML_PARSER_PATH = 'src.parser.html_parser'
    PARSER_PATH = 'src.parser.parser'
    TRANSFORMER_PATH = 'src.parser.transformer'
    PARSER_TRANSFORMER_PATH = 'src.parser.parser_transformer'
except ImportError:
    from parser.parser_transformer import (
        ParserTransformer, parse_html, parse_multiple_products, transform_data
    )
    # Define the module paths for patching based on how they're imported in parser_transformer.py
    HTML_PARSER_PATH = 'parser.html_parser'
    PARSER_PATH = 'parser.parser'
    TRANSFORMER_PATH = 'parser.transformer'
    PARSER_TRANSFORMER_PATH = 'parser.parser_transformer'


class TestParserTransformer(unittest.TestCase):
    """Test cases for the ParserTransformer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://example.com"
        self.selectors = {
            "product_name": ".product-name",
            "sku": ".product-sku",
            "description": ".product-description",
            "supplier_name": ".supplier-name",
            "cost": ".product-cost",
            "price": ".product-price",
            "colorways": ".product-colors li",
            "image_url": ".product-image img"
        }
        self.xpath_selectors = {
            "product_name": "//h1[@class='product-name']",
            "sku": "//div[@class='product-sku']",
            "description": "//div[@class='product-description']",
            "supplier_name": "//div[@class='supplier-name']",
            "cost": "//div[@class='product-cost']",
            "price": "//div[@class='product-price']",
            "colorways": "//ul[@class='product-colors']/li",
            "image_url": "//div[@class='product-image']/img"
        }
        self.parser_transformer = ParserTransformer(
            self.base_url, self.selectors, self.xpath_selectors
        )
        
        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head><title>Test Product</title></head>
            <body>
                <h1 class="product-name">Test Product</h1>
                <div class="product-sku">SKU123456</div>
                <div class="product-description">This is a test product description.</div>
                <div class="supplier-name">Test Supplier</div>
                <div class="product-cost">$10.99</div>
                <div class="product-price">$19.99</div>
                <ul class="product-colors">
                    <li>Red</li>
                    <li>Blue</li>
                    <li>Green</li>
                </ul>
                <div class="product-image">
                    <img src="/images/test-product.jpg" alt="Test Product">
                </div>
            </body>
        </html>
        """
        
        # Sample HTML content with multiple products
        self.sample_html_multiple = """
        <html>
            <head><title>Test Products</title></head>
            <body>
                <div class="product-container">
                    <h1 class="product-name">Test Product 1</h1>
                    <div class="product-sku">SKU123456</div>
                    <div class="product-description">This is test product 1.</div>
                    <div class="supplier-name">Test Supplier</div>
                    <div class="product-cost">$10.99</div>
                    <div class="product-price">$19.99</div>
                    <ul class="product-colors">
                        <li>Red</li>
                        <li>Blue</li>
                    </ul>
                    <div class="product-image">
                        <img src="/images/test-product-1.jpg" alt="Test Product 1">
                    </div>
                </div>
                <div class="product-container">
                    <h1 class="product-name">Test Product 2</h1>
                    <div class="product-sku">SKU789012</div>
                    <div class="product-description">This is test product 2.</div>
                    <div class="supplier-name">Test Supplier</div>
                    <div class="product-cost">$12.99</div>
                    <div class="product-price">$24.99</div>
                    <ul class="product-colors">
                        <li>Green</li>
                        <li>Yellow</li>
                    </ul>
                    <div class="product-image">
                        <img src="/images/test-product-2.jpg" alt="Test Product 2">
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Sample HTML with malformed content
        self.malformed_html = "<unclosed_tag>Test Product<div>Incomplete HTML"

    def test_parse_and_transform(self):
        """Test parsing and transforming HTML content."""
        # Mock the Parser.parse method to return a predefined result
        with patch(f'{PARSER_PATH}.Parser.parse') as mock_parse:
            mock_parse.return_value = {
                "product_name": "Test Product",
                "sku": "SKU123456",
                "description": "This is a test product description.",
                "supplier_name": "Test Supplier",
                "cost": "$10.99",
                "price": "$19.99",
                "colorways": ["Red", "Blue", "Green"],
                "image_url": "/images/test-product.jpg"
            }
            
            result = self.parser_transformer.parse_and_transform(self.sample_html)
            
            # Verify the result
            self.assertEqual(result["product_name"], "Test Product")
            self.assertEqual(result["sku"], "SKU123456")
            self.assertEqual(result["description"], "This is a test product description.")
            self.assertEqual(result["supplier_name"], "Test Supplier")
            self.assertEqual(result["cost"], 10.99)
            self.assertEqual(result["price"], 19.99)
            self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
            self.assertEqual(result["image_url"], "https://example.com/images/test-product.jpg")
            self.assertTrue(result["validation"]["is_valid"])
            self.assertEqual(result["validation"]["missing_required_fields"], [])

    def test_parse_and_transform_multiple(self):
        """Test parsing and transforming HTML content with multiple products."""
        # Mock the Parser.parse_multiple method to return predefined results
        with patch(f'{PARSER_PATH}.Parser.parse_multiple') as mock_parse_multiple:
            mock_parse_multiple.return_value = [
                {
                    "product_name": "Test Product 1",
                    "sku": "SKU123456",
                    "description": "This is test product 1.",
                    "supplier_name": "Test Supplier",
                    "cost": "$10.99",
                    "price": "$19.99",
                    "colorways": ["Red", "Blue"],
                    "image_url": "/images/test-product-1.jpg"
                },
                {
                    "product_name": "Test Product 2",
                    "sku": "SKU789012",
                    "description": "This is test product 2.",
                    "supplier_name": "Test Supplier",
                    "cost": "$12.99",
                    "price": "$24.99",
                    "colorways": ["Green", "Yellow"],
                    "image_url": "/images/test-product-2.jpg"
                }
            ]
            
            results = self.parser_transformer.parse_and_transform_multiple(
                self.sample_html_multiple, ".product-container"
            )
            
            # Verify the results
            self.assertEqual(len(results), 2)
            
            # Check first product
            self.assertEqual(results[0]["product_name"], "Test Product 1")
            self.assertEqual(results[0]["sku"], "SKU123456")
            self.assertEqual(results[0]["colorways"], ["Red", "Blue"])
            self.assertEqual(results[0]["image_url"], "https://example.com/images/test-product-1.jpg")
            
            # Check second product
            self.assertEqual(results[1]["product_name"], "Test Product 2")
            self.assertEqual(results[1]["sku"], "SKU789012")
            self.assertEqual(results[1]["colorways"], ["Green", "Yellow"])
            self.assertEqual(results[1]["image_url"], "https://example.com/images/test-product-2.jpg")

    def test_extract_and_transform_with_selectors(self):
        """Test extracting and transforming data using custom selectors."""
        # Create a BeautifulSoup object from the sample HTML
        soup = BeautifulSoup(self.sample_html, 'lxml')
        
        # Define custom selectors for the test
        custom_selectors = {
            "product_name": ".product-name",
            "price": ".product-price"
        }
        
        # Define attribute map for the test
        attribute_map = {
            "image_url": "src"
        }
        
        # Create a real result to return instead of mocking
        expected_result = {
            "product_name": "Test Product",
            "price": 19.99,
            "validation": {"is_valid": True, "missing_required_fields": []}
        }
        
        # Use the actual implementation instead of mocking
        result = self.parser_transformer.extract_and_transform_with_selectors(
            soup, custom_selectors, attribute_map
        )
        
        # Verify the result contains expected fields with correct types
        self.assertIn("product_name", result)
        self.assertIn("price", result)
        self.assertIn("validation", result)
        self.assertIsInstance(result["product_name"], str)
        self.assertIsInstance(result["price"], float)

    def test_extract_and_transform_with_xpath(self):
        """Test extracting and transforming data using XPath expressions."""
        # Define custom XPath expressions for the test
        custom_xpath = {
            "product_name": "//h1[@class='product-name']",
            "price": "//div[@class='product-price']",
            "colorways": "//ul[@class='product-colors']/li",
            "image_url": "//div[@class='product-image']/img"
        }
        
        result = self.parser_transformer.extract_and_transform_with_xpath(
            self.sample_html, custom_xpath
        )
        
        # Verify the result
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["price"], 19.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(result["image_url"], "https://example.com/images/test-product.jpg")

    def test_parse_html_utility(self):
        """Test the parse_html utility function."""
        with patch(f'{PARSER_TRANSFORMER_PATH}.ParserTransformer.parse_and_transform') as mock_parse:
            mock_parse.return_value = {
                "product_name": "Test Product",
                "sku": "SKU123456",
                "validation": {"is_valid": True, "missing_required_fields": []}
            }
            
            result = parse_html(
                self.sample_html, self.base_url, self.selectors, self.xpath_selectors
            )
            
            # Verify the result
            self.assertEqual(result["product_name"], "Test Product")
            self.assertEqual(result["sku"], "SKU123456")
            self.assertTrue(result["validation"]["is_valid"])

    def test_parse_multiple_products_utility(self):
        """Test the parse_multiple_products utility function."""
        with patch(f'{PARSER_TRANSFORMER_PATH}.ParserTransformer.parse_and_transform_multiple') as mock_parse:
            mock_parse.return_value = [
                {
                    "product_name": "Test Product 1",
                    "sku": "SKU123456",
                    "validation": {"is_valid": True, "missing_required_fields": []}
                },
                {
                    "product_name": "Test Product 2",
                    "sku": "SKU789012",
                    "validation": {"is_valid": True, "missing_required_fields": []}
                }
            ]
            
            results = parse_multiple_products(
                self.sample_html_multiple, self.base_url, ".product-container",
                self.selectors, self.xpath_selectors
            )
            
            # Verify the results
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["product_name"], "Test Product 1")
            self.assertEqual(results[1]["product_name"], "Test Product 2")

    def test_transform_data_utility(self):
        """Test the transform_data utility function."""
        with patch(f'{PARSER_TRANSFORMER_PATH}.clean_and_validate_product_data') as mock_transform:
            mock_transform.return_value = {
                "product_name": "Test Product",
                "sku": "SKU123456",
                "price": 19.99,
                "validation": {"is_valid": True, "missing_required_fields": []}
            }
            
            data = {
                "product_name": "Test Product",
                "sku": "SKU123456",
                "price": "$19.99"
            }
            
            result = transform_data(data, self.base_url)
            
            # Verify the result
            self.assertEqual(result["product_name"], "Test Product")
            self.assertEqual(result["sku"], "SKU123456")
            self.assertEqual(result["price"], 19.99)
            self.assertTrue(result["validation"]["is_valid"])

    def test_error_handling_malformed_html(self):
        """Test error handling for malformed HTML."""
        # Test with malformed HTML
        with patch(f'{PARSER_PATH}.Parser.parse') as mock_parse:
            mock_parse.return_value = {
                "product_name": "",
                "sku": "",
                "description": "",
                "supplier_name": "",
                "cost": 0.0,
                "price": 0.0,
                "colorways": [],
                "image_url": "",
                "error": "Malformed HTML detected"
            }
            
            result = self.parser_transformer.parse_and_transform(self.malformed_html)
            
            # Verify the result contains the error
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Malformed HTML detected")

    def test_missing_required_fields(self):
        """Test validation of missing required fields."""
        # Mock the Parser.parse method to return a result with missing required fields
        with patch(f'{PARSER_PATH}.Parser.parse') as mock_parse:
            mock_parse.return_value = {
                "product_name": "",  # Missing product_name
                "sku": "SKU123456",
                "description": "This is a test product description.",
                "supplier_name": "Test Supplier",
                "cost": "$10.99",
                "price": "$19.99",
                "colorways": ["Red", "Blue", "Green"],
                "image_url": "/images/test-product.jpg"
            }
            
            result = self.parser_transformer.parse_and_transform(self.sample_html)
            
            # Verify the validation result
            self.assertFalse(result["validation"]["is_valid"])
            self.assertIn("product_name", result["validation"]["missing_required_fields"])


if __name__ == "__main__":
    unittest.main()
