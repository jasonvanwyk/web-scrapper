"""
Unit tests for the HTML Parser module.
"""

import pytest
from bs4 import BeautifulSoup

from src.parser.html_parser import (
    create_soup,
    extract_text,
    extract_attribute,
    extract_multiple_texts,
    extract_multiple_attributes,
    extract_image_url,
    extract_structured_data
)


# Sample HTML content for testing
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1 class="title">Product Title</h1>
    <p class="description">This is a product description.</p>
    <div class="product-info">
        <span class="sku">SKU123456</span>
        <span class="price">$99.99</span>
        <span class="cost">€75.50</span>
    </div>
    <div class="colors">
        <span class="color">Red</span>
        <span class="color">Blue</span>
        <span class="color">Green</span>
    </div>
    <div class="images">
        <img src="/images/product1.jpg" alt="Product Image" class="main-image">
        <img src="/images/product2.jpg" alt="Product Image 2" class="thumbnail">
        <img data-src="/images/product3.jpg" alt="Product Image 3" class="lazy-image">
    </div>
    <div class="missing-info"></div>
</body>
</html>
"""


class TestHtmlParser:
    """Test cases for the HTML Parser module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.html = SAMPLE_HTML
        self.soup = create_soup(self.html)
    
    def test_create_soup(self):
        """Test creating a BeautifulSoup object from HTML content."""
        soup = create_soup(self.html)
        assert isinstance(soup, BeautifulSoup)
        assert soup.title.text == "Test Page"
    
    def test_extract_text(self):
        """Test extracting text from an HTML element."""
        # Test with string HTML
        assert extract_text(self.html, "h1.title") == "Product Title"
        assert extract_text(self.html, "p.description") == "This is a product description."
        
        # Test with BeautifulSoup object
        assert extract_text(self.soup, "h1.title") == "Product Title"
        assert extract_text(self.soup, "p.description") == "This is a product description."
        
        # Test with non-existent selector
        assert extract_text(self.html, "h2.nonexistent") == ""
        assert extract_text(self.html, "h2.nonexistent", default="Not Found") == "Not Found"
        
        # Test with empty element
        assert extract_text(self.html, "div.missing-info") == ""
    
    def test_extract_attribute(self):
        """Test extracting an attribute from an HTML element."""
        # Test with string HTML
        assert extract_attribute(self.html, "img.main-image", "src") == "/images/product1.jpg"
        assert extract_attribute(self.html, "img.main-image", "alt") == "Product Image"
        
        # Test with BeautifulSoup object
        assert extract_attribute(self.soup, "img.main-image", "src") == "/images/product1.jpg"
        assert extract_attribute(self.soup, "img.main-image", "alt") == "Product Image"
        
        # Test with non-existent selector
        assert extract_attribute(self.html, "img.nonexistent", "src") == ""
        assert extract_attribute(self.html, "img.nonexistent", "src", default="no-image.jpg") == "no-image.jpg"
        
        # Test with non-existent attribute
        assert extract_attribute(self.html, "img.main-image", "nonexistent") == ""
    
    def test_extract_multiple_texts(self):
        """Test extracting text from multiple HTML elements."""
        # Test with string HTML
        colors = extract_multiple_texts(self.html, "span.color")
        assert len(colors) == 3
        assert "Red" in colors
        assert "Blue" in colors
        assert "Green" in colors
        
        # Test with BeautifulSoup object
        colors = extract_multiple_texts(self.soup, "span.color")
        assert len(colors) == 3
        assert "Red" in colors
        assert "Blue" in colors
        assert "Green" in colors
        
        # Test with non-existent selector
        assert extract_multiple_texts(self.html, "span.nonexistent") == []
    
    def test_extract_multiple_attributes(self):
        """Test extracting attributes from multiple HTML elements."""
        # Test with string HTML
        image_srcs = extract_multiple_attributes(self.html, "img", "src")
        assert len(image_srcs) == 2  # Only 2 have src, one has data-src
        assert "/images/product1.jpg" in image_srcs
        assert "/images/product2.jpg" in image_srcs
        
        # Test with BeautifulSoup object
        image_alts = extract_multiple_attributes(self.soup, "img", "alt")
        assert len(image_alts) == 3
        assert "Product Image" in image_alts
        assert "Product Image 2" in image_alts
        assert "Product Image 3" in image_alts
        
        # Test with non-existent selector
        assert extract_multiple_attributes(self.html, "img.nonexistent", "src") == []
        
        # Test with non-existent attribute
        assert extract_multiple_attributes(self.html, "img", "nonexistent") == []
    
    def test_extract_image_url(self):
        """Test extracting an image URL."""
        # Test with string HTML
        assert extract_image_url(self.html, "img.main-image") == "/images/product1.jpg"
        
        # Test with BeautifulSoup object
        assert extract_image_url(self.soup, "img.main-image") == "/images/product1.jpg"
        
        # Test with data-src attribute
        assert extract_image_url(self.html, "img.lazy-image", attribute="data-src") == "/images/product3.jpg"
        
        # Test with non-existent selector
        assert extract_image_url(self.html, "img.nonexistent") == ""
        assert extract_image_url(self.html, "img.nonexistent", default="no-image.jpg") == "no-image.jpg"
    
    def test_extract_structured_data(self):
        """Test extracting structured data from HTML."""
        # Define selectors
        selectors = {
            "title": "h1.title",
            "description": "p.description",
            "sku": "span.sku",
            "price": "span.price",
            "image": "img.main-image"
        }
        
        # Define attribute map
        attribute_map = {
            "image": "src"
        }
        
        # Test with string HTML
        data = extract_structured_data(self.html, selectors, attribute_map)
        assert data["title"] == "Product Title"
        assert data["description"] == "This is a product description."
        assert data["sku"] == "SKU123456"
        assert data["price"] == "$99.99"
        assert data["image"] == "/images/product1.jpg"
        
        # Test with BeautifulSoup object
        data = extract_structured_data(self.soup, selectors, attribute_map)
        assert data["title"] == "Product Title"
        assert data["description"] == "This is a product description."
        assert data["sku"] == "SKU123456"
        assert data["price"] == "$99.99"
        assert data["image"] == "/images/product1.jpg"
        
        # Test with missing selectors
        selectors_with_missing = selectors.copy()
        selectors_with_missing["nonexistent"] = "div.nonexistent"
        data = extract_structured_data(self.html, selectors_with_missing, attribute_map)
        assert data["nonexistent"] == ""
        
        # Test without attribute map
        data = extract_structured_data(self.html, {"image": "img.main-image"})
        assert data["image"] == ""  # Gets text content, which is empty for img tag
