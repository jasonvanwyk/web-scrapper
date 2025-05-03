"""
Tests for the StaticScraper class.
"""

import unittest
from unittest import mock
from bs4 import BeautifulSoup

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.static_scraper import StaticScraper
    from src.http_client.request_handler import RequestHandler
except ModuleNotFoundError:
    from scrapers.static_scraper import StaticScraper
    from http_client.request_handler import RequestHandler


class TestStaticScraper(unittest.TestCase):
    """Tests for the StaticScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock RequestHandler
        self.mock_request_handler = mock.MagicMock(spec=RequestHandler)
        
        # Create test selectors
        self.test_selectors = {
            "product_name": "h1.product-name",
            "sku": "span.sku",
            "description": "div.description",
            "cost": "span.cost",
            "price": "span.price",
            "colorways": "ul.colors li",
            "image_url": "img.product-image",
            "product_link": "a.product-link",
            "next_page": "a.next-page",
            "pagination_format": "/products?page={page}",
            "login_url": "/login",
            "login_submit_url": "/login",
            "username_field": "username",
            "password_field": "password",
            "csrf_token": "input[name='csrf_token']",
            "csrf_field": "csrf_token",
            "login_success_indicator": "div.welcome-message",
            "category_url": "/products",
            "max_pages": "3"
        }
        
        # Create a StaticScraper with the mock RequestHandler
        self.scraper = StaticScraper(
            name="Test Supplier",
            base_url="https://example.com",
            requires_login=False,
            selectors=self.test_selectors,
            request_handler=self.mock_request_handler
        )
    
    def test_init(self):
        """Test initialization of StaticScraper."""
        # Check that the name was set
        self.assertEqual(self.scraper.name, "Test Supplier")
        
        # Check that the base_url was set
        self.assertEqual(self.scraper.base_url, "https://example.com")
        
        # Check that requires_login was set
        self.assertEqual(self.scraper.requires_login, False)
        
        # Check that selectors were set
        self.assertEqual(self.scraper.selectors, self.test_selectors)
        
        # Check that the request_handler was set
        self.assertEqual(self.scraper.request_handler, self.mock_request_handler)
    
    def test_init_with_login(self):
        """Test initialization of StaticScraper with login."""
        # Create a StaticScraper with login required
        with mock.patch.object(StaticScraper, "login") as mock_login:
            scraper = StaticScraper(
                name="Test Supplier",
                base_url="https://example.com",
                requires_login=True,
                username="test_user",
                password="test_password",
                selectors=self.test_selectors,
                request_handler=self.mock_request_handler
            )
            
            # Check that login was called
            mock_login.assert_called_once_with("test_user", "test_password")
    
    def test_login(self):
        """Test the login method."""
        # Set up the mock RequestHandler
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="hidden" name="csrf_token" value="test_csrf_token">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <button type="submit">Login</button>
                </form>
                <div class="welcome-message">Welcome, User!</div>
            </body>
        </html>
        """
        self.mock_request_handler.get.return_value = mock_response
        self.mock_request_handler.post.return_value = mock_response
        
        # Call the login method
        result = self.scraper.login("test_user", "test_password")
        
        # Check that the result is True
        self.assertTrue(result)
        
        # Check that get was called with the login URL
        self.mock_request_handler.get.assert_called_once_with("https://example.com/login")
        
        # Check that post was called with the login data
        self.mock_request_handler.post.assert_called_once_with(
            "https://example.com/login",
            data={
                "username": "test_user",
                "password": "test_password",
                "csrf_token": "test_csrf_token"
            },
            allow_redirects=True
        )
    
    def test_login_failed(self):
        """Test the login method when login fails."""
        # Set up the mock RequestHandler for the GET request
        get_response = mock.MagicMock()
        get_response.status_code = 200
        get_response.text = """
        <html>
            <body>
                <form action="/login" method="post">
                    <input type="hidden" name="csrf_token" value="test_csrf_token">
                    <input type="text" name="username">
                    <input type="password" name="password">
                    <button type="submit">Login</button>
                </form>
            </body>
        </html>
        """
        
        # Set up the mock RequestHandler for the POST request
        post_response = mock.MagicMock()
        post_response.status_code = 401  # Unauthorized
        
        self.mock_request_handler.get.return_value = get_response
        self.mock_request_handler.post.return_value = post_response
        
        # Call the login method
        result = self.scraper.login("test_user", "test_password")
        
        # Check that the result is False
        self.assertFalse(result)
    
    def test_get_product_urls(self):
        """Test the get_product_urls method."""
        # Set up the mock RequestHandler
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <div class="products">
                    <a class="product-link" href="/product/1">Product 1</a>
                    <a class="product-link" href="/product/2">Product 2</a>
                    <a class="product-link" href="/product/3">Product 3</a>
                </div>
                <a class="next-page" href="/products?page=2">Next</a>
            </body>
        </html>
        """
        self.mock_request_handler.get.return_value = mock_response
        
        # Call the get_product_urls method
        result = self.scraper.get_product_urls()
        
        # Check that the result contains the expected URLs
        expected_urls = [
            "https://example.com/product/1",
            "https://example.com/product/2",
            "https://example.com/product/3"
        ]
        self.assertEqual(result, expected_urls)
        
        # Check that get was called with the category URL
        self.mock_request_handler.get.assert_any_call("https://example.com/products")
    
    def test_handle_pagination(self):
        """Test the handle_pagination method."""
        # Test with page 1
        result = self.scraper.handle_pagination("https://example.com/products", 1)
        self.assertEqual(result, "https://example.com/products")
        
        # Test with page 2 using default approach (no pagination_format in selectors)
        # First, temporarily remove pagination_format from selectors
        original_pagination_format = self.scraper.selectors.get('pagination_format')
        if 'pagination_format' in self.scraper.selectors:
            del self.scraper.selectors['pagination_format']
            
        result = self.scraper.handle_pagination("https://example.com/products", 2)
        self.assertEqual(result, "https://example.com/products?page=2")
        
        # Test with a URL that already has query parameters
        result = self.scraper.handle_pagination("https://example.com/products?category=shoes", 2)
        # The order of parameters might vary, so we check that both parameters are present
        self.assertIn("category=shoes", result)
        self.assertIn("page=2", result)
        
        # Restore pagination_format if it was present
        if original_pagination_format:
            self.scraper.selectors['pagination_format'] = original_pagination_format
    
    def test_extract_data(self):
        """Test the extract_data method."""
        # Set up the mock RequestHandler
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <h1 class="product-name">Test Product</h1>
                <span class="sku">SKU123</span>
                <div class="description">This is a test product.</div>
                <span class="cost">$10.00</span>
                <span class="price">$20.00</span>
                <ul class="colors">
                    <li>Red</li>
                    <li>Blue</li>
                    <li>Green</li>
                </ul>
                <img class="product-image" src="/images/test-product.jpg">
            </body>
        </html>
        """
        self.mock_request_handler.get.return_value = mock_response
        
        # Call the extract_data method
        result = self.scraper.extract_data("https://example.com/product/1")
        
        # Check that the result contains the expected data
        expected_data = {
            "product_name": "Test Product",
            "sku": "SKU123",
            "description": "This is a test product.",
            "supplier_name": "Test Supplier",
            "cost": 10.0,
            "price": 20.0,
            "colorways": ["Red", "Blue", "Green"],
            "image_url": "https://example.com/images/test-product.jpg"
        }
        self.assertEqual(result, expected_data)
        
        # Check that get was called with the product URL
        self.mock_request_handler.get.assert_called_once_with("https://example.com/product/1")
    
    def test_extract_text(self):
        """Test the _extract_text method."""
        # Create a BeautifulSoup object
        html = """
        <html>
            <body>
                <h1 class="product-name">Test Product</h1>
                <span class="sku">SKU123</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Test with a valid selector
        result = self.scraper._extract_text(soup, "product_name")
        self.assertEqual(result, "Test Product")
        
        # Test with a valid selector
        result = self.scraper._extract_text(soup, "sku")
        self.assertEqual(result, "SKU123")
        
        # Test with an invalid selector
        result = self.scraper._extract_text(soup, "invalid_selector")
        self.assertEqual(result, "")
    
    def test_extract_price(self):
        """Test the _extract_price method."""
        # Create a BeautifulSoup object
        html = """
        <html>
            <body>
                <span class="cost">$10.00</span>
                <span class="price">$20.00</span>
                <span class="invalid-price">Not a price</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Test with a valid selector
        result = self.scraper._extract_price(soup, "cost")
        self.assertEqual(result, 10.0)
        
        # Test with a valid selector
        result = self.scraper._extract_price(soup, "price")
        self.assertEqual(result, 20.0)
        
        # Test with an invalid selector
        result = self.scraper._extract_price(soup, "invalid_selector")
        self.assertEqual(result, 0.0)
    
    def test_extract_colorways(self):
        """Test the _extract_colorways method."""
        # Create a BeautifulSoup object
        html = """
        <html>
            <body>
                <ul class="colors">
                    <li>Red</li>
                    <li>Blue</li>
                    <li>Green</li>
                </ul>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Test with a valid selector
        result = self.scraper._extract_colorways(soup)
        self.assertEqual(result, ["Red", "Blue", "Green"])
        
        # Test with an invalid selector
        self.scraper.selectors["colorways"] = "invalid_selector"
        result = self.scraper._extract_colorways(soup)
        self.assertEqual(result, [])
    
    def test_extract_image_url(self):
        """Test the _extract_image_url method."""
        # Create a BeautifulSoup object
        html = """
        <html>
            <body>
                <img class="product-image" src="/images/test-product.jpg">
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Test with a valid selector
        result = self.scraper._extract_image_url(soup)
        self.assertEqual(result, "https://example.com/images/test-product.jpg")
        
        # Test with an invalid selector
        self.scraper.selectors["image_url"] = "invalid_selector"
        result = self.scraper._extract_image_url(soup)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
