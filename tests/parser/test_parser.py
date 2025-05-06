"""
Unit tests for the Parser class.
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from bs4 import BeautifulSoup

try:
    from src.parser.parser import Parser
except ImportError:
    from parser.parser import Parser


class TestParser(unittest.TestCase):
    """Test cases for the Parser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://example.com"
        self.selectors = {
            "product_name": "h1.product-title",
            "sku": "span.product-sku",
            "description": "div.product-description",
            "supplier_name": "span.supplier",
            "cost": "span.cost",
            "price": "span.price",
            "colorways": "ul.colors li",
            "image_url": "img.product-image"
        }
        self.parser = Parser(base_url=self.base_url, selectors=self.selectors)
        
        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head><title>Test Product</title></head>
            <body>
                <h1 class="product-title">Test Product</h1>
                <span class="product-sku">SKU123</span>
                <div class="product-description">This is a test product description.</div>
                <span class="supplier">Test Supplier</span>
                <span class="cost">$50.00</span>
                <span class="price">$99.99</span>
                <ul class="colors">
                    <li>Red</li>
                    <li>Blue</li>
                    <li>Green</li>
                </ul>
                <img class="product-image" src="/images/test.jpg" alt="Test Product">
            </body>
        </html>
        """
        
        # Sample HTML with multiple products
        self.multi_product_html = """
        <html>
            <head><title>Product List</title></head>
            <body>
                <div class="product-container">
                    <h1 class="product-title">Product 1</h1>
                    <span class="product-sku">SKU001</span>
                    <div class="product-description">Description 1</div>
                    <span class="supplier">Supplier A</span>
                    <span class="cost">$40.00</span>
                    <span class="price">$79.99</span>
                    <ul class="colors">
                        <li>Red</li>
                        <li>Blue</li>
                    </ul>
                    <img class="product-image" src="/images/product1.jpg" alt="Product 1">
                </div>
                <div class="product-container">
                    <h1 class="product-title">Product 2</h1>
                    <span class="product-sku">SKU002</span>
                    <div class="product-description">Description 2</div>
                    <span class="supplier">Supplier B</span>
                    <span class="cost">$60.00</span>
                    <span class="price">$119.99</span>
                    <ul class="colors">
                        <li>Green</li>
                        <li>Yellow</li>
                    </ul>
                    <img class="product-image" src="/images/product2.jpg" alt="Product 2">
                </div>
            </body>
        </html>
        """
        
        # Sample HTML with missing elements
        self.incomplete_html = """
        <html>
            <head><title>Incomplete Product</title></head>
            <body>
                <h1 class="product-title">Incomplete Product</h1>
                <!-- No SKU -->
                <div class="product-description">This product has missing data.</div>
                <!-- No supplier -->
                <!-- No cost -->
                <span class="price">$59.99</span>
                <!-- No colorways -->
                <!-- No image -->
            </body>
        </html>
        """
        
        # Sample HTML with malformed data
        self.malformed_html = """
        <html>
            <head><title>Malformed Product</title></head>
            <body>
                <h1 class="product-title">Malformed Product</h1>
                <span class="product-sku">SK</span> <!-- Too short -->
                <div class="product-description">Description.</div>
                <span class="supplier">Supplier C</span>
                <span class="cost">Not a price</span> <!-- Invalid price -->
                <span class="price">€ 89,99</span> <!-- European format -->
                <ul class="colors">
                    <li></li> <!-- Empty color -->
                </ul>
                <img class="product-image" src="" alt="No image"> <!-- Empty src -->
            </body>
        </html>
        """

    def test_parser_initialization(self):
        """Test that the Parser initializes correctly."""
        self.assertEqual(self.parser.base_url, self.base_url)
        self.assertEqual(self.parser.selectors, self.selectors)
        self.assertEqual(self.parser.xpath_selectors, {})
        
        # Test with XPath selectors
        xpath_selectors = {"product_name": "//h1[@class='product-title']"}
        parser = Parser(base_url=self.base_url, xpath_selectors=xpath_selectors)
        self.assertEqual(parser.xpath_selectors, xpath_selectors)

    def test_parse_complete_product(self):
        """Test parsing a complete product with all fields present."""
        result = self.parser.parse(self.sample_html)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["description"], "This is a test product description.")
        self.assertEqual(result["supplier_name"], "Test Supplier")
        self.assertEqual(result["cost"], 50.0)
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(result["image_url"], "https://example.com/images/test.jpg")

    def test_parse_multiple_products(self):
        """Test parsing multiple products from a single HTML document."""
        results = self.parser.parse_multiple(self.multi_product_html, ".product-container")
        
        self.assertEqual(len(results), 2)
        
        # Check first product
        self.assertEqual(results[0]["product_name"], "Product 1")
        self.assertEqual(results[0]["sku"], "SKU001")
        self.assertEqual(results[0]["colorways"], ["Red", "Blue"])
        
        # Check second product
        self.assertEqual(results[1]["product_name"], "Product 2")
        self.assertEqual(results[1]["sku"], "SKU002")
        self.assertEqual(results[1]["colorways"], ["Green", "Yellow"])

    def test_parse_incomplete_product(self):
        """Test parsing a product with missing fields."""
        result = self.parser.parse(self.incomplete_html)
        
        self.assertEqual(result["product_name"], "Incomplete Product")
        self.assertEqual(result["sku"], "")  # Missing
        self.assertEqual(result["description"], "This product has missing data.")
        self.assertEqual(result["supplier_name"], "")  # Missing
        self.assertEqual(result["cost"], 0.0)  # Missing
        self.assertEqual(result["price"], 59.99)
        self.assertEqual(result["colorways"], [])  # Missing
        self.assertEqual(result["image_url"], "")  # Missing

    def test_parse_malformed_product(self):
        """Test parsing a product with malformed data."""
        result = self.parser.parse(self.malformed_html)
        
        self.assertEqual(result["product_name"], "Malformed Product")
        self.assertEqual(result["sku"], "SK")  # Too short but still extracted
        self.assertEqual(result["description"], "Description.")
        self.assertEqual(result["supplier_name"], "Supplier C")
        self.assertEqual(result["cost"], 0.0)  # Invalid price defaults to 0
        self.assertEqual(result["price"], 89.99)  # European format handled correctly
        self.assertEqual(result["colorways"], [])  # Empty color filtered out
        self.assertEqual(result["image_url"], "")  # Empty src

    def test_parse_with_xpath(self):
        """Test parsing using XPath selectors."""
        xpath_parser = Parser(
            base_url=self.base_url,
            xpath_selectors={
                "product_name": "//h1[@class='product-title']",
                "sku": "//span[@class='product-sku']",
                "price": "//span[@class='price']"
            }
        )
        
        result = xpath_parser.parse(self.sample_html)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["price"], 99.99)

    def test_parse_with_error(self):
        """Test parsing with an error in the HTML content."""
        # Invalid HTML that will cause a parsing error
        invalid_html = "<html><unclosed_tag>"
        
        # The parser should handle the error gracefully
        result = self.parser.parse(invalid_html)
        
        # Check that default values are returned
        self.assertEqual(result["product_name"], "")
        self.assertEqual(result["sku"], "")
        self.assertEqual(result["price"], 0.0)
        self.assertTrue("error" in result)  # Error message should be included

    def test_parse_multiple_with_error(self):
        """Test parsing multiple products with an error in one product."""
        with patch('bs4.BeautifulSoup.select') as mock_select:
            # Mock the select method to raise an exception for the second call
            mock_select.side_effect = [
                [MagicMock()],  # First call returns a list with one mock
                Exception("Test error")  # Second call raises an exception
            ]
            
            # The parser should handle the error gracefully
            results = self.parser.parse_multiple(self.multi_product_html, ".product-container")
            
            # Should still return results from the first successful parse
            self.assertEqual(len(results), 1)

    def test_absolute_url_conversion(self):
        """Test that relative URLs are converted to absolute URLs."""
        # Create a parser with a different base URL
        parser = Parser(base_url="https://shop.example.org/")
        
        # Create a simple HTML with a relative image URL
        html = '<html><body><img class="product-image" src="products/image.jpg"></body></html>'
        
        # Add the selector for the image
        parser.selectors = {"image_url": "img.product-image"}
        
        # Parse the HTML
        result = parser.parse(html)
        
        # Check that the relative URL was converted to an absolute URL
        self.assertEqual(result["image_url"], "https://shop.example.org/products/image.jpg")

    def test_empty_selectors(self):
        """Test parsing with empty selectors."""
        parser = Parser(base_url=self.base_url)
        result = parser.parse(self.sample_html)
        
        # All fields should have default values
        self.assertEqual(result["product_name"], "")
        self.assertEqual(result["sku"], "")
        self.assertEqual(result["description"], "")
        self.assertEqual(result["supplier_name"], "")
        self.assertEqual(result["cost"], 0.0)
        self.assertEqual(result["price"], 0.0)
        self.assertEqual(result["colorways"], [])
        self.assertEqual(result["image_url"], "")

    def test_extract_methods_individually(self):
        """Test each _extract_* method individually."""
        soup = BeautifulSoup(self.sample_html, 'lxml')
        
        self.assertEqual(self.parser._extract_product_name(soup), "Test Product")
        self.assertEqual(self.parser._extract_sku(soup), "SKU123")
        self.assertEqual(self.parser._extract_description(soup), "This is a test product description.")
        self.assertEqual(self.parser._extract_supplier_name(soup), "Test Supplier")
        self.assertEqual(self.parser._extract_cost(soup), 50.0)
        self.assertEqual(self.parser._extract_price(soup), 99.99)
        self.assertEqual(self.parser._extract_colorways(soup), ["Red", "Blue", "Green"])
        self.assertEqual(self.parser._extract_image_url(soup), "https://example.com/images/test.jpg")


if __name__ == '__main__':
    unittest.main()
