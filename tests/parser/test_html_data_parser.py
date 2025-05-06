"""
Unit tests for the enhanced HTML/Data Parser Module.

These tests verify that the enhanced parser module correctly extracts
structured data from HTML content based on supplier-specific configurations.
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest
from bs4 import BeautifulSoup
import lxml.html

try:
    from src.parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url,
        extract_structured_data, extract_with_xpath,
        extract_structured_data_with_xpath
    )
    from src.parser.parser import Parser
except ImportError:
    from parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url,
        extract_structured_data, extract_with_xpath,
        extract_structured_data_with_xpath
    )
    from parser.parser import Parser


class TestHtmlDataParser(unittest.TestCase):
    """Test cases for the enhanced HTML/Data Parser Module."""

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
        self.xpath_selectors = {
            "product_name": "//h1[@class='product-title']",
            "sku": "//span[@class='product-sku']",
            "description": "//div[@class='product-description']",
            "supplier_name": "//span[@class='supplier']",
            "cost": "//span[@class='cost']",
            "price": "//span[@class='price']",
            "colorways": "//ul[@class='colors']/li",
            "image_url": "//img[@class='product-image']"
        }
        
        # Create parser instances for testing
        self.css_parser = Parser(base_url=self.base_url, selectors=self.selectors)
        self.xpath_parser = Parser(base_url=self.base_url, xpath_selectors=self.xpath_selectors)
        self.combined_parser = Parser(
            base_url=self.base_url, 
            selectors=self.selectors,
            xpath_selectors=self.xpath_selectors
        )
        
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
        
        # Sample HTML with international formats
        self.international_html = """
        <html>
            <head><title>International Product</title></head>
            <body>
                <h1 class="product-title">International Product</h1>
                <span class="product-sku">INT-SKU-123</span>
                <div class="product-description">International product description.</div>
                <span class="supplier">International Supplier</span>
                <span class="cost">€45,99</span>
                <span class="price">€89,99</span>
                <ul class="colors">
                    <li>Rouge</li>
                    <li>Bleu</li>
                </ul>
                <img class="product-image" src="/images/international.jpg" alt="International Product">
            </body>
        </html>
        """

    def test_extract_text_with_css_selector(self):
        """Test extracting text using CSS selectors."""
        # Test with string input
        text = extract_text(self.sample_html, "h1.product-title")
        self.assertEqual(text, "Test Product")
        
        # Test with BeautifulSoup input
        soup = create_soup(self.sample_html)
        text = extract_text(soup, "h1.product-title")
        self.assertEqual(text, "Test Product")
        
        # Test with Tag input
        tag = soup.select_one("body")
        text = extract_text(tag, "h1.product-title")
        self.assertEqual(text, "Test Product")
        
        # Test with non-existent selector
        text = extract_text(self.sample_html, "h1.non-existent")
        self.assertEqual(text, "")

    def test_extract_with_xpath(self):
        """Test extracting data using XPath expressions."""
        # Test simple text extraction
        text = extract_with_xpath(self.sample_html, "//h1[@class='product-title']")
        self.assertEqual(text, "Test Product")
        
        # Test attribute extraction
        src = extract_with_xpath(self.sample_html, "//img[@class='product-image']", attribute="src")
        self.assertEqual(src, "/images/test.jpg")
        
        # Test list extraction
        colors = extract_with_xpath(self.sample_html, "//ul[@class='colors']/li", is_list=True)
        self.assertEqual(colors, ["Red", "Blue", "Green"])
        
        # Test with non-existent XPath
        text = extract_with_xpath(self.sample_html, "//h1[@class='non-existent']")
        self.assertEqual(text, "")

    def test_structured_data_extraction_css(self):
        """Test extracting structured data using CSS selectors."""
        data = extract_structured_data(
            self.sample_html,
            self.selectors,
            {"image_url": "src"},
            self.base_url
        )
        
        self.assertEqual(data["product_name"], "Test Product")
        self.assertEqual(data["sku"], "SKU123")
        self.assertEqual(data["description"], "This is a test product description.")
        self.assertEqual(data["supplier_name"], "Test Supplier")
        self.assertEqual(data["cost"], "$50.00")
        self.assertEqual(data["price"], "$99.99")
        self.assertEqual(data["image_url"], "https://example.com/images/test.jpg")

    def test_structured_data_extraction_xpath(self):
        """Test extracting structured data using XPath expressions."""
        data = extract_structured_data_with_xpath(
            self.sample_html,
            self.xpath_selectors,
            {"image_url": "src"},
            ["colorways"],
            self.base_url
        )
        
        self.assertEqual(data["product_name"], "Test Product")
        self.assertEqual(data["sku"], "SKU123")
        self.assertEqual(data["description"], "This is a test product description.")
        self.assertEqual(data["supplier_name"], "Test Supplier")
        self.assertEqual(data["cost"], "$50.00")
        self.assertEqual(data["price"], "$99.99")
        self.assertEqual(data["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(data["image_url"], "https://example.com/images/test.jpg")

    def test_parser_with_css_selectors(self):
        """Test parsing with CSS selectors."""
        result = self.css_parser.parse(self.sample_html)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["description"], "This is a test product description.")
        self.assertEqual(result["supplier_name"], "Test Supplier")
        self.assertEqual(result["cost"], 50.0)
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(result["image_url"], "https://example.com/images/test.jpg")

    def test_parser_with_xpath_selectors(self):
        """Test parsing with XPath selectors."""
        result = self.xpath_parser.parse(self.sample_html)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["description"], "This is a test product description.")
        self.assertEqual(result["supplier_name"], "Test Supplier")
        self.assertEqual(result["cost"], 50.0)
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(result["image_url"], "https://example.com/images/test.jpg")

    def test_parser_with_combined_selectors(self):
        """Test parsing with both CSS and XPath selectors."""
        # Create a parser with mixed selectors (some CSS, some XPath)
        mixed_parser = Parser(
            base_url=self.base_url,
            selectors={
                "product_name": "h1.product-title",
                "sku": "span.product-sku",
                "image_url": "img.product-image"
            },
            xpath_selectors={
                "description": "//div[@class='product-description']",
                "supplier_name": "//span[@class='supplier']",
                "cost": "//span[@class='cost']",
                "price": "//span[@class='price']",
                "colorways": "//ul[@class='colors']/li"
            }
        )
        
        result = mixed_parser.parse(self.sample_html)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["description"], "This is a test product description.")
        self.assertEqual(result["supplier_name"], "Test Supplier")
        self.assertEqual(result["cost"], 50.0)
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(result["image_url"], "https://example.com/images/test.jpg")

    def test_parse_multiple_products(self):
        """Test parsing multiple products."""
        results = self.css_parser.parse_multiple(self.multi_product_html, ".product-container")
        
        self.assertEqual(len(results), 2)
        
        # Check first product
        self.assertEqual(results[0]["product_name"], "Product 1")
        self.assertEqual(results[0]["sku"], "SKU001")
        self.assertEqual(results[0]["supplier_name"], "Supplier A")
        self.assertEqual(results[0]["price"], 79.99)
        self.assertEqual(results[0]["colorways"], ["Red", "Blue"])
        
        # Check second product
        self.assertEqual(results[1]["product_name"], "Product 2")
        self.assertEqual(results[1]["sku"], "SKU002")
        self.assertEqual(results[1]["supplier_name"], "Supplier B")
        self.assertEqual(results[1]["price"], 119.99)
        self.assertEqual(results[1]["colorways"], ["Green", "Yellow"])

    def test_international_number_formats(self):
        """Test parsing with international number formats."""
        result = self.css_parser.parse(self.international_html)
        
        # Check that European price format (€45,99) is correctly converted to float
        self.assertEqual(result["cost"], 45.99)
        self.assertEqual(result["price"], 89.99)

    def test_error_handling(self):
        """Test error handling with malformed HTML."""
        # Test with empty HTML
        result = self.css_parser.parse("")
        self.assertIn("error", result)
        self.assertEqual(result["product_name"], "")
        
        # Test with malformed HTML
        result = self.css_parser.parse("<html><unclosed_tag>")
        self.assertIn("error", result)
        self.assertEqual(result["product_name"], "")
        
        # Test with valid HTML but non-existent selectors
        empty_parser = Parser(base_url=self.base_url)
        result = empty_parser.parse(self.sample_html)
        self.assertEqual(result["product_name"], "")
        self.assertEqual(result["sku"], "")

    def test_extract_with_config(self):
        """Test extracting data with a configuration dictionary."""
        config = {
            "selectors": {
                "product_name": "h1.product-title",
                "price": "span.price"
            },
            "xpath_selectors": {
                "sku": "//span[@class='product-sku']",
                "colorways": "//ul[@class='colors']/li"
            }
        }
        
        result = self.css_parser.extract_with_config(self.sample_html, config)
        
        self.assertEqual(result["product_name"], "Test Product")
        self.assertEqual(result["sku"], "SKU123")
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["colorways"], ["Red", "Blue", "Green"])


if __name__ == '__main__':
    unittest.main()
