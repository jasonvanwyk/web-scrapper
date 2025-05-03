"""
Tests for the BrowserHandler class.

This module contains unit tests for the BrowserHandler class, which is responsible
for managing Playwright browser instances and providing methods for browser interactions.
"""

import unittest
from unittest.mock import MagicMock, patch

# Try both import paths to handle different execution contexts
try:
    from src.browser_automation.browser_handler import BrowserHandler
except ModuleNotFoundError:
    from browser_automation.browser_handler import BrowserHandler


class TestBrowserHandler(unittest.TestCase):
    """Test cases for the BrowserHandler class."""

    @patch('src.browser_automation.browser_handler.sync_playwright')
    def setUp(self, mock_sync_playwright):
        """Set up test fixtures."""
        # Mock Playwright and browser components
        self.mock_playwright = MagicMock()
        self.mock_browser = MagicMock()
        self.mock_context = MagicMock()
        self.mock_page = MagicMock()
        
        # Configure mocks
        mock_sync_playwright.return_value.start.return_value = self.mock_playwright
        self.mock_playwright.chromium = MagicMock()
        self.mock_playwright.chromium.launch.return_value = self.mock_browser
        self.mock_browser.new_context.return_value = self.mock_context
        self.mock_context.new_page.return_value = self.mock_page
        
        # Create BrowserHandler instance with mocked components
        self.browser_handler = BrowserHandler(
            browser_type="chromium",
            headless=True,
            timeout=30000,
            stealth_mode=True
        )
        
        # Replace the actual browser components with mocks
        self.browser_handler.playwright = self.mock_playwright
        self.browser_handler.browser = self.mock_browser
        self.browser_handler.context = self.mock_context
        self.browser_handler.page = self.mock_page

    def tearDown(self):
        """Tear down test fixtures."""
        self.browser_handler = None

    @patch('src.browser_automation.browser_handler.sync_playwright')
    def test_initialization(self, mock_sync_playwright):
        """Test that BrowserHandler initializes correctly."""
        # Configure mocks
        mock_playwright_instance = MagicMock()
        mock_browser_instance = MagicMock()
        mock_context_instance = MagicMock()
        mock_page_instance = MagicMock()
        
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium = MagicMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser_instance
        mock_browser_instance.new_context.return_value = mock_context_instance
        mock_context_instance.new_page.return_value = mock_page_instance
        
        # Create a new BrowserHandler instance
        handler = BrowserHandler(browser_type="chromium", headless=True)
        
        # Verify initialization
        mock_sync_playwright.return_value.start.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)
        mock_browser_instance.new_context.assert_called_once()
        mock_context_instance.new_page.assert_called_once()
        
        # Clean up
        handler.close()

    def test_goto(self):
        """Test the goto method."""
        url = "https://example.com"
        self.browser_handler.goto(url)
        
        # Verify that page.goto was called with the correct URL
        self.mock_page.goto.assert_called_once()
        args, kwargs = self.mock_page.goto.call_args
        self.assertEqual(args[0], url)
        self.assertEqual(kwargs.get("wait_until"), "load")

    def test_wait_for_selector(self):
        """Test the wait_for_selector method."""
        selector = "#test-element"
        self.browser_handler.wait_for_selector(selector)
        
        # Verify that page.wait_for_selector was called with the correct selector
        self.mock_page.wait_for_selector.assert_called_once()
        args, kwargs = self.mock_page.wait_for_selector.call_args
        self.assertEqual(args[0], selector)
        self.assertEqual(kwargs.get("state"), "visible")

    def test_click(self):
        """Test the click method."""
        selector = "#test-button"
        self.browser_handler.click(selector)
        
        # Verify that page.click was called with the correct selector
        self.mock_page.click.assert_called_once_with(selector, timeout=self.browser_handler.timeout)

    def test_fill(self):
        """Test the fill method."""
        selector = "#test-input"
        value = "test value"
        self.browser_handler.fill(selector, value)
        
        # Verify that page.fill was called with the correct selector and value
        self.mock_page.fill.assert_called_once_with(selector, value, timeout=self.browser_handler.timeout)

    def test_get_content(self):
        """Test the get_content method."""
        self.mock_page.content.return_value = "<html><body>Test content</body></html>"
        content = self.browser_handler.get_content()
        
        # Verify that page.content was called and the correct content was returned
        self.mock_page.content.assert_called_once()
        self.assertEqual(content, "<html><body>Test content</body></html>")

    def test_evaluate(self):
        """Test the evaluate method."""
        expression = "document.title"
        self.mock_page.evaluate.return_value = "Test Page"
        result = self.browser_handler.evaluate(expression)
        
        # Verify that page.evaluate was called with the correct expression
        self.mock_page.evaluate.assert_called_once_with(expression)
        self.assertEqual(result, "Test Page")

    def test_close(self):
        """Test the close method."""
        self.browser_handler.close()
        
        # Verify that all components were closed
        self.mock_page.close.assert_called_once()
        self.mock_context.close.assert_called_once()
        self.mock_browser.close.assert_called_once()
        self.mock_playwright.stop.assert_called_once()

    def test_context_manager(self):
        """Test the context manager protocol."""
        with self.browser_handler as handler:
            # Verify that the context manager returns the handler
            self.assertEqual(handler, self.browser_handler)
        
        # Verify that close was called when exiting the context
        self.mock_page.close.assert_called_once()
        self.mock_context.close.assert_called_once()
        self.mock_browser.close.assert_called_once()
        self.mock_playwright.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
