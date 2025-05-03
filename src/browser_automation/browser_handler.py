"""
Browser handler module.

This module provides a BrowserHandler class that manages Playwright browser instances
and provides methods for browser interactions with stealth configurations.
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext, Playwright

# Define PlaywrightError as a generic Exception to avoid import issues
PlaywrightError = Exception

# Try both import paths to handle different execution contexts
try:
    from src.config import config
except ModuleNotFoundError:
    from config import config


class BrowserHandler:
    """
    Handler for browser automation using Playwright.
    
    This class manages Playwright browser instances and provides methods for
    browser interactions with stealth configurations to minimize bot detection.
    
    Attributes:
        playwright: The Playwright instance.
        browser: The browser instance.
        context: The browser context.
        page: The current page.
        browser_type: The type of browser to use (chromium, firefox, webkit).
        headless: Whether to run the browser in headless mode.
        timeout: Timeout for browser operations in milliseconds.
        stealth_mode: Whether to use stealth mode to minimize bot detection.
        logger: A logger instance for the handler.
    """
    
    # Default user agents for stealth mode
    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
    ]
    
    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        timeout: Optional[int] = None,
        stealth_mode: bool = True,
        user_agents: Optional[List[str]] = None,
        proxy: Optional[Dict[str, str]] = None,
        delay: Optional[float] = None,
        download_path: Optional[str] = None
    ):
        """
        Initialize the browser handler.
        
        Args:
            browser_type: The type of browser to use (chromium, firefox, webkit).
            headless: Whether to run the browser in headless mode.
            timeout: Timeout for browser operations in milliseconds.
                    If None, uses config.scraping.browser_timeout.
            stealth_mode: Whether to use stealth mode to minimize bot detection.
            user_agents: List of User-Agent strings to rotate through.
                        If None, uses DEFAULT_USER_AGENTS.
            proxy: Optional proxy configuration.
            delay: Delay between browser actions in seconds.
                  If None, uses config.scraping.browser_delay.
            download_path: Path to download directory.
        """
        self.browser_type = browser_type
        self.headless = headless
        self.timeout = timeout or config.scraping.browser_timeout
        self.stealth_mode = stealth_mode
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        self.proxy = proxy
        self.delay = delay or config.scraping.browser_delay
        self.download_path = download_path
        
        # Initialize attributes that will be set later
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize Playwright
        self._initialize_playwright()
    
    def _initialize_playwright(self) -> None:
        """
        Initialize Playwright and create a browser instance.
        """
        try:
            self.playwright = sync_playwright().start()
            
            # Get the browser instance based on the specified type
            if self.browser_type == "chromium":
                browser_instance = self.playwright.chromium
            elif self.browser_type == "firefox":
                browser_instance = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_instance = self.playwright.webkit
            else:
                self.logger.warning(f"Unsupported browser type: {self.browser_type}. Using chromium.")
                browser_instance = self.playwright.chromium
            
            # Launch the browser
            self.browser = browser_instance.launch(headless=self.headless)
            
            # Create a new browser context with stealth mode if enabled
            self._create_context()
            
            self.logger.info(f"Initialized {self.browser_type} browser")
        except Exception as e:
            self.logger.error(f"Error initializing Playwright: {e}")
            self.close()
            raise
    
    def _create_context(self) -> None:
        """
        Create a new browser context with stealth mode if enabled.
        """
        # Select a random user agent
        user_agent = random.choice(self.user_agents)
        
        # Context options
        context_options = {
            "user_agent": user_agent,
            "viewport": {"width": 1920, "height": 1080},
            "screen": {"width": 1920, "height": 1080},
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "permissions": []
        }
        
        # Add proxy if specified
        if self.proxy:
            context_options["proxy"] = self.proxy
        
        # Add download path if specified
        if self.download_path:
            download_dir = Path(self.download_path)
            download_dir.mkdir(parents=True, exist_ok=True)
            context_options["accept_downloads"] = True
            context_options["downloads_path"] = str(download_dir)
        
        # Create the context
        self.context = self.browser.new_context(**context_options)
        
        # Apply stealth mode if enabled
        if self.stealth_mode:
            self._apply_stealth_mode()
        
        # Create a new page
        self.page = self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(self.timeout)
    
    def _apply_stealth_mode(self) -> None:
        """
        Apply stealth mode to minimize bot detection.
        """
        # Add JavaScript to modify navigator properties
        self.context.add_init_script("""
        () => {
            // Override properties to prevent detection
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // Override plugins and languages
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                        description: "Native Client Executable",
                        filename: "internal-nacl-plugin",
                        length: 1,
                        name: "Native Client"
                    }
                ]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            // Override platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Override connection
            if (navigator.connection) {
                Object.defineProperty(navigator.connection, 'rtt', {
                    get: () => 100
                });
            }
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters.name === 'notifications') {
                    return Promise.resolve({state: Notification.permission});
                }
                return originalQuery(parameters);
            };
        }
        """)
        
        self.logger.debug("Applied stealth mode configurations")
    
    def _add_delay(self) -> None:
        """
        Add a delay between browser actions to be more human-like.
        """
        # Add a random delay within a range
        delay_time = self.delay + random.uniform(-0.5, 0.5) * self.delay
        delay_time = max(0.1, delay_time)  # Ensure minimum delay
        time.sleep(delay_time)
    
    def new_page(self) -> Page:
        """
        Create a new page in the current context.
        
        Returns:
            Page: The new page.
        """
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        return self.page
    
    def goto(self, url: str, wait_until: str = "load", timeout: Optional[int] = None) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to.
            wait_until: When to consider navigation succeeded.
                       Options: 'load', 'domcontentloaded', 'networkidle', 'commit'.
            timeout: Timeout for navigation in milliseconds.
                    If None, uses the default timeout.
        """
        try:
            self._add_delay()
            self.logger.debug(f"Navigating to {url}")
            self.page.goto(url, wait_until=wait_until, timeout=timeout or self.timeout)
        except PlaywrightError as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            raise
    
    def wait_for_selector(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> Any:
        """
        Wait for an element matching the selector.
        
        Args:
            selector: A selector to search for.
            state: State to wait for: 'attached', 'detached', 'visible', or 'hidden'.
            timeout: Maximum time to wait in milliseconds.
                    If None, uses the default timeout.
                    
        Returns:
            The element handle.
        """
        try:
            return self.page.wait_for_selector(
                selector,
                state=state,
                timeout=timeout or self.timeout
            )
        except PlaywrightError as e:
            self.logger.error(f"Error waiting for selector '{selector}': {e}")
            raise
    
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Click on an element matching the selector.
        
        Args:
            selector: A selector to search for.
            timeout: Maximum time to wait in milliseconds.
                    If None, uses the default timeout.
        """
        try:
            self._add_delay()
            self.page.click(selector, timeout=timeout or self.timeout)
        except PlaywrightError as e:
            self.logger.error(f"Error clicking on selector '{selector}': {e}")
            raise
    
    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """
        Fill an input field with the given value.
        
        Args:
            selector: A selector to search for.
            value: Value to fill.
            timeout: Maximum time to wait in milliseconds.
                    If None, uses the default timeout.
        """
        try:
            self._add_delay()
            self.page.fill(selector, value, timeout=timeout or self.timeout)
        except PlaywrightError as e:
            self.logger.error(f"Error filling selector '{selector}' with value '{value}': {e}")
            raise
    
    def select_option(self, selector: str, value: Optional[str] = None, label: Optional[str] = None, timeout: Optional[int] = None) -> List[str]:
        """
        Select an option from a <select> element.
        
        Args:
            selector: A selector to search for.
            value: Option value to select.
            label: Option label to select.
            timeout: Maximum time to wait in milliseconds.
                    If None, uses the default timeout.
                    
        Returns:
            List of selected values.
        """
        try:
            self._add_delay()
            options = {}
            if value is not None:
                options["value"] = value
            if label is not None:
                options["label"] = label
            
            return self.page.select_option(selector, **options, timeout=timeout or self.timeout)
        except PlaywrightError as e:
            self.logger.error(f"Error selecting option from selector '{selector}': {e}")
            raise
    
    def get_content(self) -> str:
        """
        Get the HTML content of the current page.
        
        Returns:
            str: The HTML content.
        """
        try:
            return self.page.content()
        except PlaywrightError as e:
            self.logger.error(f"Error getting page content: {e}")
            raise
    
    def screenshot(self, path: Optional[str] = None, full_page: bool = True) -> bytes:
        """
        Take a screenshot of the current page.
        
        Args:
            path: Path to save the screenshot.
            full_page: Whether to take a screenshot of the full page.
            
        Returns:
            bytes: The screenshot as bytes.
        """
        try:
            return self.page.screenshot(path=path, full_page=full_page)
        except PlaywrightError as e:
            self.logger.error(f"Error taking screenshot: {e}")
            raise
    
    def evaluate(self, expression: str) -> Any:
        """
        Evaluate JavaScript expression in the context of the current page.
        
        Args:
            expression: JavaScript expression to evaluate.
            
        Returns:
            The result of the expression.
        """
        try:
            return self.page.evaluate(expression)
        except PlaywrightError as e:
            self.logger.error(f"Error evaluating expression: {e}")
            raise
    
    def wait_for_load_state(self, state: str = "load", timeout: Optional[int] = None) -> None:
        """
        Wait for the page to reach a specific load state.
        
        Args:
            state: Load state to wait for: 'load', 'domcontentloaded', 'networkidle'.
            timeout: Maximum time to wait in milliseconds.
                    If None, uses the default timeout.
        """
        try:
            self.page.wait_for_load_state(state, timeout=timeout or self.timeout)
        except PlaywrightError as e:
            self.logger.error(f"Error waiting for load state '{state}': {e}")
            raise
    
    def close_page(self) -> None:
        """
        Close the current page.
        """
        if self.page:
            try:
                self.page.close()
                self.page = None
            except PlaywrightError as e:
                self.logger.error(f"Error closing page: {e}")
    
    def close(self) -> None:
        """
        Close the browser and Playwright instance.
        """
        if self.page:
            try:
                self.page.close()
                self.page = None
            except Exception as e:
                self.logger.error(f"Error closing page: {e}")
        
        if self.context:
            try:
                self.context.close()
                self.context = None
            except Exception as e:
                self.logger.error(f"Error closing context: {e}")
        
        if self.browser:
            try:
                self.browser.close()
                self.browser = None
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
        
        if self.playwright:
            try:
                self.playwright.stop()
                self.playwright = None
            except Exception as e:
                self.logger.error(f"Error stopping Playwright: {e}")
    
    def __enter__(self) -> "BrowserHandler":
        """
        Enter the context manager.
        
        Returns:
            BrowserHandler: The browser handler instance.
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        
        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.
        """
        self.close()
