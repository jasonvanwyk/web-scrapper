"""
Integration tests for the BrowserHandler and DynamicScraper.

These tests verify that the browser automation components work correctly
with actual browser instances. They require Playwright system dependencies
to be installed.
"""

import os
import unittest
import pytest
from pathlib import Path

# Try both import paths to handle different execution contexts
try:
    from src.browser_automation.browser_handler import BrowserHandler
    from src.scrapers.dynamic_scraper import DynamicScraper
except ModuleNotFoundError:
    from browser_automation.browser_handler import BrowserHandler
    from scrapers.dynamic_scraper import DynamicScraper


# Skip these tests if the SKIP_INTEGRATION_TESTS environment variable is set
skip_integration_tests = os.environ.get("SKIP_INTEGRATION_TESTS", "false").lower() in ("true", "1", "t")
skip_reason = "Integration tests are skipped. Set SKIP_INTEGRATION_TESTS=false to run them."


@pytest.mark.skipif(skip_integration_tests, reason=skip_reason)
class TestBrowserIntegration(unittest.TestCase):
    """Integration tests for browser automation components."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test output directory if it doesn't exist
        self.test_output_dir = Path(__file__).parent / "test_output"
        self.test_output_dir.mkdir(exist_ok=True)
        
        # Initialize the BrowserHandler with headless mode
        self.browser_handler = BrowserHandler(
            browser_type="chromium",
            headless=True,
            timeout=30000,
            stealth_mode=True
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        if hasattr(self, 'browser_handler') and self.browser_handler:
            self.browser_handler.close()
    
    def test_browser_navigation(self):
        """Test basic browser navigation."""
        # Navigate to a test website
        self.browser_handler.goto("https://example.com")
        
        # Wait for the h1 element to be visible
        h1_element = self.browser_handler.wait_for_selector("h1")
        
        # Get the page content
        content = self.browser_handler.get_content()
        
        # Verify that the page contains the expected content
        self.assertIn("<h1>Example Domain</h1>", content)
        self.assertIsNotNone(h1_element)
    
    def test_screenshot_capture(self):
        """Test screenshot capture functionality."""
        # Navigate to a test website
        self.browser_handler.goto("https://example.com")
        
        # Take a screenshot
        screenshot_path = str(self.test_output_dir / "example_screenshot.png")
        screenshot = self.browser_handler.screenshot(path=screenshot_path)
        
        # Verify that the screenshot was taken
        self.assertTrue(os.path.exists(screenshot_path))
        self.assertIsInstance(screenshot, bytes)
        self.assertGreater(len(screenshot), 0)
    
    def test_javascript_execution(self):
        """Test JavaScript execution in the browser."""
        # Navigate to a test website
        self.browser_handler.goto("https://example.com")
        
        # Execute JavaScript to modify the page
        self.browser_handler.evaluate("""
            document.querySelector('h1').textContent = 'Modified Example';
        """)
        
        # Get the modified content
        content = self.browser_handler.get_content()
        
        # Verify that the JavaScript execution worked
        self.assertIn("<h1>Modified Example</h1>", content)


@pytest.mark.skipif(skip_integration_tests, reason=skip_reason)
class TestDynamicScraperIntegration(unittest.TestCase):
    """Integration tests for the DynamicScraper."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a DynamicScraper instance for a test website
        self.scraper = DynamicScraper(
            name="Example Website",
            base_url="https://example.com",
            headless=True,
            stealth_mode=True,
            selectors={
                "product_name": "h1",
                "description": "p",
            }
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        if hasattr(self, 'scraper') and self.scraper:
            self.scraper.close()
    
    def test_extract_data(self):
        """Test extracting data from a website."""
        # Extract data from the example.com website
        data = self.scraper.extract_data("https://example.com")
        
        # Verify that the data was extracted correctly
        self.assertEqual(data["product_name"], "Example Domain")
        self.assertIn("illustrative examples", data["description"])
        self.assertEqual(data["supplier_name"], "Example Website")


if __name__ == "__main__":
    unittest.main()
