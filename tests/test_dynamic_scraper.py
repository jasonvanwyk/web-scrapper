"""
Tests for the DynamicScraper class.

This module contains unit tests for the DynamicScraper class, which is responsible
for scraping dynamic websites that require JavaScript execution or complex interactions.
"""

import unittest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.dynamic_scraper import DynamicScraper
    from src.browser_automation.browser_handler import BrowserHandler
except ModuleNotFoundError:
    from scrapers.dynamic_scraper import DynamicScraper
    from browser_automation.browser_handler import BrowserHandler


class TestDynamicScraper(unittest.TestCase):
    """Test cases for the DynamicScraper class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock BrowserHandler
        self.mock_browser_handler = MagicMock(spec=BrowserHandler)
        
        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head><title>Test Product</title></head>
            <body>
                <h1 class="product-title">Test Product</h1>
                <div class="sku">SKU123</div>
                <div class="description">This is a test product description.</div>
                <div class="price">$99.99</div>
                <div class="cost">$49.99</div>
                <ul class="colorways">
                    <li>Red</li>
                    <li>Blue</li>
                    <li>Green</li>
                </ul>
                <img class="product-image" src="/images/test-product.jpg" />
                <a class="next" href="/page/2">Next</a>
                <div class="products">
                    <a href="/product/1" class="product">Product 1</a>
                    <a href="/product/2" class="product">Product 2</a>
                </div>
            </body>
        </html>
        """
        
        # Configure the mock BrowserHandler
        self.mock_browser_handler.get_content.return_value = self.sample_html
        
        # Patch the BrowserHandler class to avoid initialization issues
        with patch('src.scrapers.dynamic_scraper.BrowserHandler', return_value=self.mock_browser_handler):
            # Create a DynamicScraper instance with the mock BrowserHandler
            self.scraper = DynamicScraper(
                name="Test Supplier",
                base_url="https://example.com",
                selectors={
                    "product_name": ".product-title",
                    "sku": ".sku",
                    "description": ".description",
                    "price": ".price",
                    "cost": ".cost",
                    "colorways": ".colorways li",
                    "image_url": ".product-image",
                    "product_links": ".product",
                    "next_page": ".next"
                }
            )
            
            # Replace the browser_handler directly to ensure we're using our mock
            self.scraper.browser_handler = self.mock_browser_handler

    def tearDown(self):
        """Tear down test fixtures."""
        self.scraper = None
        self.mock_browser_handler = None

    def test_initialization(self):
        """Test that DynamicScraper initializes correctly."""
        self.assertEqual(self.scraper.name, "Test Supplier")
        self.assertEqual(self.scraper.base_url, "https://example.com")
        self.assertEqual(self.scraper.browser_handler, self.mock_browser_handler)

    def test_login(self):
        """Test the login method."""
        # Configure the mock BrowserHandler
        self.mock_browser_handler.wait_for_selector.return_value = True
        
        # Call the login method
        result = self.scraper.login("testuser", "testpass")
        
        # Verify that the browser handler methods were called correctly
        self.mock_browser_handler.goto.assert_called_once()
        self.mock_browser_handler.fill.assert_any_call("input[name=\"username\"], input[type=\"email\"]", "testuser")
        self.mock_browser_handler.fill.assert_any_call("input[name=\"password\"], input[type=\"password\"]", "testpass")
        self.mock_browser_handler.click.assert_called_once()
        self.mock_browser_handler.wait_for_load_state.assert_called_once_with("networkidle")
        self.mock_browser_handler.wait_for_selector.assert_any_call(".account, .dashboard, .logged-in", timeout=5000)
        
        # Verify that the method returned the expected result
        self.assertTrue(result)

    def test_get_product_urls(self):
        """Test the get_product_urls method."""
        # Configure the mock BrowserHandler
        self.mock_browser_handler.wait_for_selector.return_value = True
        self.mock_browser_handler.evaluate.return_value = False  # Next button is not disabled
        
        # Call the get_product_urls method
        urls = self.scraper.get_product_urls()
        
        # Verify that the browser handler methods were called correctly
        self.mock_browser_handler.goto.assert_called_once()
        self.mock_browser_handler.wait_for_selector.assert_any_call(".product")
        self.mock_browser_handler.get_content.assert_called_once()
        
        # Verify that the method returned the expected result
        self.assertEqual(len(urls), 2)
        self.assertIn("https://example.com/product/1", urls)
        self.assertIn("https://example.com/product/2", urls)

    def test_handle_pagination(self):
        """Test the handle_pagination method."""
        # Test with default pagination format
        url = "https://example.com/category"
        paginated_url = self.scraper.handle_pagination(url, 2)
        self.assertEqual(paginated_url, "https://example.com/category?page=2")
        
        # Test with query_param pagination format
        self.scraper.selectors["pagination_format"] = "query_param"
        self.scraper.selectors["page_param"] = "p"
        paginated_url = self.scraper.handle_pagination(url, 3)
        self.assertEqual(paginated_url, "https://example.com/category?p=3")
        
        # Test with path pagination format
        self.scraper.selectors["pagination_format"] = "path"
        self.scraper.selectors["pagination_path_template"] = "/page/{page}"
        paginated_url = self.scraper.handle_pagination(url, 4)
        self.assertEqual(paginated_url, "https://example.com/category/page/4")

    def test_extract_data(self):
        """Test the extract_data method."""
        # Call the extract_data method
        product_data = self.scraper.extract_data("https://example.com/product/1")
        
        # Verify that the browser handler methods were called correctly
        self.mock_browser_handler.goto.assert_called_once_with("https://example.com/product/1")
        self.mock_browser_handler.wait_for_selector.assert_any_call(".product-title")
        self.mock_browser_handler.wait_for_load_state.assert_called_once_with("networkidle")
        self.mock_browser_handler.get_content.assert_called_once()
        
        # Verify that the method returned the expected result
        self.assertEqual(product_data["product_name"], "Test Product")
        self.assertEqual(product_data["sku"], "SKU123")
        self.assertEqual(product_data["description"], "This is a test product description.")
        self.assertEqual(product_data["supplier_name"], "Test Supplier")
        self.assertEqual(product_data["price"], 99.99)
        self.assertEqual(product_data["cost"], 49.99)
        self.assertEqual(product_data["colorways"], ["Red", "Blue", "Green"])
        self.assertEqual(product_data["image_url"], "https://example.com/images/test-product.jpg")

    def test_extract_text(self):
        """Test the _extract_text method."""
        # Create a BeautifulSoup object from the sample HTML
        soup = BeautifulSoup(self.sample_html, "lxml")
        
        # Test with a valid selector
        text = self.scraper._extract_text(soup, "product_name")
        self.assertEqual(text, "Test Product")
        
        # Test with an invalid selector
        text = self.scraper._extract_text(soup, "invalid_selector")
        self.assertEqual(text, "")

    def test_extract_price(self):
        """Test the _extract_price method."""
        # Create a BeautifulSoup object from the sample HTML
        soup = BeautifulSoup(self.sample_html, "lxml")
        
        # Test with a valid selector
        price = self.scraper._extract_price(soup, "price")
        self.assertEqual(price, 99.99)
        
        # Test with an invalid selector
        price = self.scraper._extract_price(soup, "invalid_selector")
        self.assertEqual(price, 0.0)

    def test_extract_colorways(self):
        """Test the _extract_colorways method."""
        # Create a BeautifulSoup object from the sample HTML
        soup = BeautifulSoup(self.sample_html, "lxml")
        
        # Test with a valid selector
        colorways = self.scraper._extract_colorways(soup)
        self.assertEqual(colorways, ["Red", "Blue", "Green"])
        
        # Test with an invalid selector
        self.scraper.selectors["colorways"] = ".invalid-selector"
        colorways = self.scraper._extract_colorways(soup)
        self.assertEqual(colorways, [])

    def test_extract_image_url(self):
        """Test the _extract_image_url method."""
        # Create a BeautifulSoup object from the sample HTML
        soup = BeautifulSoup(self.sample_html, "lxml")
        
        # Test with a valid selector
        image_url = self.scraper._extract_image_url(soup)
        self.assertEqual(image_url, "https://example.com/images/test-product.jpg")
        
        # Test with an invalid selector
        self.scraper.selectors["image_url"] = ".invalid-selector"
        image_url = self.scraper._extract_image_url(soup)
        self.assertEqual(image_url, "")

    def test_close(self):
        """Test the close method."""
        self.scraper.close()
        self.mock_browser_handler.close.assert_called_once()

    def test_maps_to_products(self):
        """Test the Maps_to_products method."""
        # Configure the mock BrowserHandler
        self.mock_browser_handler.wait_for_selector.return_value = True
        self.mock_browser_handler.evaluate.return_value = False  # Next button is not disabled
        
        # Create a category map for testing
        category_map = {
            "Category 1": "/category/1",
            "Category 2": "/category/2"
        }
        
        # Mock the get_product_urls method to return different URLs for different categories
        with patch.object(self.scraper, 'get_product_urls') as mock_get_urls:
            mock_get_urls.side_effect = lambda url: [
                f"{url}/product/1",
                f"{url}/product/2"
            ] if url == "https://example.com/category/1" else [
                f"{url}/product/3",
                f"{url}/product/4"
            ]
            
            # Call the Maps_to_products method
            result = self.scraper.Maps_to_products(category_map)
            
            # Verify that get_product_urls was called for each category
            self.assertEqual(mock_get_urls.call_count, 2)
            
            # Verify the results
            self.assertEqual(len(result), 2)
            self.assertEqual(len(result["Category 1"]), 2)
            self.assertEqual(len(result["Category 2"]), 2)
            expected_urls_category1 = [
                "https://example.com/category/1/product/1",
                "https://example.com/category/1/product/2"
            ]
            expected_urls_category2 = [
                "https://example.com/category/2/product/3",
                "https://example.com/category/2/product/4"
            ]
            for url in expected_urls_category1:
                self.assertIn(url, result["Category 1"])
            for url in expected_urls_category2:
                self.assertIn(url, result["Category 2"])

    def test_maps_to_products_error_handling(self):
        """Test error handling in the Maps_to_products method."""
        # Create a category map for testing
        category_map = {
            "Category 1": "/category/1",
            "Category 2": "/category/2"
        }
        
        # Mock the get_product_urls method to raise an exception
        with patch.object(self.scraper, 'get_product_urls') as mock_get_urls:
            mock_get_urls.side_effect = Exception("Test error")
            
            # Call the Maps_to_products method
            result = self.scraper.Maps_to_products(category_map)
            
            # Verify that the method handled the error and returned empty lists
            self.assertEqual(len(result), 2)
            self.assertEqual(result["Category 1"], [])
            self.assertEqual(result["Category 2"], [])

    def test_context_manager(self):
        """Test the context manager functionality."""
        with self.scraper as scraper:
            self.assertEqual(scraper, self.scraper)
        
        # Verify that close was called when exiting the context
        self.mock_browser_handler.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
