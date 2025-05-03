"""
Dynamic scraper module.

This module provides a concrete implementation of the BaseScraper for dynamic websites
that require JavaScript execution or complex interactions. It uses Playwright via
the BrowserHandler for browser automation.
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

from bs4 import BeautifulSoup

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.base_scraper import BaseScraper
    from src.browser_automation.browser_handler import BrowserHandler
    from src.parser.html_parser import extract_text, extract_attribute, extract_image_url, extract_multiple_texts
    from src.parser.transformer import strip_whitespace, to_float, normalize_list, clean_and_validate_product_data
except ModuleNotFoundError:
    from scrapers.base_scraper import BaseScraper
    from browser_automation.browser_handler import BrowserHandler
    from parser.html_parser import extract_text, extract_attribute, extract_image_url, extract_multiple_texts
    from parser.transformer import strip_whitespace, to_float, normalize_list, clean_and_validate_product_data


class DynamicScraper(BaseScraper):
    """
    Concrete implementation of BaseScraper for dynamic websites.
    
    This class uses the BrowserHandler to automate browser interactions and
    handle websites that require JavaScript execution or complex interactions.
    
    Attributes:
        browser_handler: The BrowserHandler instance for browser automation.
        selectors: CSS selectors for data extraction.
    """
    
    def __init__(
        self,
        name: str,
        base_url: str,
        requires_login: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        headless: bool = True,
        stealth_mode: bool = True,
        **kwargs
    ):
        """
        Initialize the dynamic scraper.
        
        Args:
            name: The name of the supplier.
            base_url: The base URL of the supplier website.
            requires_login: Whether login is required.
            username: The username for authentication.
            password: The password for authentication.
            selectors: CSS selectors for data extraction.
            headless: Whether to run the browser in headless mode.
            stealth_mode: Whether to use stealth mode to minimize bot detection.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(name, base_url, **kwargs)
        self.requires_login = requires_login
        self.username = username
        self.password = password
        self.selectors = selectors or {}
        self.headless = headless
        self.stealth_mode = stealth_mode
        
        # Initialize the browser handler
        self.browser_handler = kwargs.get('browser_handler', BrowserHandler(
            headless=self.headless,
            stealth_mode=self.stealth_mode
        ))
        
        # Login if required
        if self.requires_login and self.username and self.password:
            self.login(self.username, self.password)
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the supplier website if required.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
            
        Returns:
            bool: True if login was successful, False otherwise.
        """
        self.logger.info(f"Attempting to log in to {self.name}")
        
        # Get the login page selector or use a default
        login_url = self.selectors.get('login_url', '/login')
        login_url = self.build_absolute_url(login_url)
        
        try:
            # Navigate to the login page
            self.browser_handler.goto(login_url)
            
            # Wait for the login form to be visible
            username_selector = self.selectors.get('username_field', 'input[name="username"], input[type="email"]')
            password_selector = self.selectors.get('password_field', 'input[name="password"], input[type="password"]')
            submit_selector = self.selectors.get('submit_button', 'button[type="submit"], input[type="submit"]')
            
            # Fill in the login form
            self.browser_handler.wait_for_selector(username_selector)
            self.browser_handler.fill(username_selector, username)
            self.browser_handler.fill(password_selector, password)
            
            # Click the submit button
            self.browser_handler.click(submit_selector)
            
            # Wait for navigation to complete
            self.browser_handler.wait_for_load_state("networkidle")
            
            # Check if login was successful
            # This could be checking for a specific element that only appears when logged in
            # or checking if we're redirected to a dashboard/account page
            success_indicator = self.selectors.get('login_success_indicator', '.account, .dashboard, .logged-in')
            
            try:
                self.browser_handler.wait_for_selector(success_indicator, timeout=5000)
                self.logger.info(f"Successfully logged in to {self.name}")
                return True
            except Exception:
                self.logger.warning(f"Login to {self.name} may have failed. Could not find success indicator.")
                return False
            
        except Exception as e:
            self.logger.error(f"Error during login to {self.name}: {e}")
            return False
    
    def get_product_urls(self, category_url: Optional[str] = None) -> List[str]:
        """
        Get URLs for individual product pages.
        
        Args:
            category_url: Optional URL for a specific category page.
                          If None, use the base URL or a default category page.
                          
        Returns:
            List[str]: A list of product page URLs.
        """
        self.logger.info(f"Getting product URLs from {category_url or self.base_url}")
        
        # Use the provided category URL or a default one
        url = category_url or self.selectors.get('default_category_url', self.base_url)
        url = self.build_absolute_url(url)
        
        product_urls = []
        current_page = 1
        max_pages = int(self.selectors.get('max_pages', 1))
        
        try:
            while current_page <= max_pages:
                # Navigate to the page
                page_url = self.handle_pagination(url, current_page)
                self.browser_handler.goto(page_url)
                
                # Wait for product elements to be visible
                product_selector = self.selectors.get('product_links', 'a.product, .product a, .product-item a')
                self.browser_handler.wait_for_selector(product_selector)
                
                # Get the page content and parse it with BeautifulSoup
                content = self.browser_handler.get_content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Extract product links
                product_elements = soup.select(product_selector)
                
                if not product_elements:
                    self.logger.warning(f"No product elements found on page {current_page} using selector: {product_selector}")
                    break
                
                # Extract and process URLs
                for element in product_elements:
                    if element.has_attr('href'):
                        product_url = element['href']
                        # Make the URL absolute if it's relative
                        product_url = self.build_absolute_url(product_url)
                        
                        if product_url not in product_urls:
                            product_urls.append(product_url)
                
                self.logger.debug(f"Found {len(product_elements)} products on page {current_page}")
                
                # Check if there's a next page
                next_page_selector = self.selectors.get('next_page', '.next, .pagination .next, a[rel="next"]')
                
                try:
                    next_button = self.browser_handler.wait_for_selector(next_page_selector, timeout=5000)
                    if not next_button:
                        break
                    
                    # Check if the next button is disabled or not clickable
                    is_disabled = self.browser_handler.evaluate(f"""
                        () => {{
                            const element = document.querySelector('{next_page_selector}');
                            return element && (
                                element.disabled ||
                                element.classList.contains('disabled') ||
                                element.getAttribute('aria-disabled') === 'true'
                            );
                        }}
                    """)
                    
                    if is_disabled:
                        break
                    
                    current_page += 1
                except Exception:
                    # No next page found or error occurred
                    break
            
            self.logger.info(f"Found {len(product_urls)} unique product URLs")
            return product_urls
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs: {e}")
            return product_urls
    
    def handle_pagination(self, url: str, page: int = 1) -> str:
        """
        Handle pagination for multi-page results.
        
        Args:
            url: The base URL for the page.
            page: The page number to navigate to.
            
        Returns:
            str: The URL for the specified page.
        """
        if page <= 1:
            return url
        
        # Get the pagination format from selectors or use defaults
        pagination_format = self.selectors.get('pagination_format', '')
        
        if pagination_format == 'query_param':
            # Use query parameter (e.g., ?page=2)
            page_param = self.selectors.get('page_param', 'page')
            
            # Parse the URL and update or add the page parameter
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Update the page parameter
            query_params[page_param] = [str(page)]
            
            # Reconstruct the URL with the updated query parameters
            updated_query = urlencode(query_params, doseq=True)
            
            # Replace the query part in the URL
            parts = list(parsed_url)
            parts[4] = updated_query
            
            return urljoin(self.base_url, urlparse(url).path + '?' + updated_query)
            
        elif pagination_format == 'path':
            # Use path format (e.g., /category/page/2)
            path_template = self.selectors.get('pagination_path_template', '/page/{page}')
            path_with_page = path_template.format(page=page)
            
            # Check if the URL already has a path component
            parsed_url = urlparse(url)
            base_path = parsed_url.path.rstrip('/')
            
            # Combine the base path with the pagination path
            new_path = f"{base_path}{path_with_page}"
            
            # Reconstruct the URL with the new path
            parts = list(parsed_url)
            parts[2] = new_path
            
            return urlparse(url).scheme + '://' + urlparse(url).netloc + new_path + (('?' + urlparse(url).query) if urlparse(url).query else '')
            
        else:
            # Default: append page number to URL
            separator = '?' if '?' not in url else '&'
            return f"{url}{separator}page={page}"
    
    def extract_data(self, product_url: str) -> Dict[str, Any]:
        """
        Extract product data from a product page.
        
        Args:
            product_url: The URL of the product page.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted product data.
        """
        self.logger.info(f"Extracting data from {product_url}")
        
        try:
            # Navigate to the product page
            self.browser_handler.goto(product_url)
            
            # Wait for the product details to be visible
            product_name_selector = self.selectors.get('product_name', 'h1, .product-title, .product-name')
            self.browser_handler.wait_for_selector(product_name_selector)
            
            # Wait for the page to be fully loaded
            self.browser_handler.wait_for_load_state("networkidle")
            
            # Get the page content
            html_content = self.browser_handler.get_content()
            
            # Extract data using selectors and our parser/transformer modules
            raw_data = {
                "product_name": extract_text(html_content, self.selectors.get('product_name', '')),
                "sku": extract_text(html_content, self.selectors.get('sku', '')),
                "description": extract_text(html_content, self.selectors.get('description', '')),
                "supplier_name": self.name,
                "cost": to_float(extract_text(html_content, self.selectors.get('cost', ''))),
                "price": to_float(extract_text(html_content, self.selectors.get('price', ''))),
                "colorways": normalize_list(extract_multiple_texts(html_content, self.selectors.get('colorways', ''))),
                "image_url": extract_image_url(html_content, self.selectors.get('image_url', '')),
            }
            
            # Clean and validate the extracted data
            processed_data = clean_and_validate_product_data(raw_data)
            
            self.logger.debug(f"Extracted data for product: {processed_data['data'].get('product_name', 'Unknown')}")
            
            # Return the cleaned data
            return processed_data['data']
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {product_url}: {e}")
            return {
                "product_name": "",
                "sku": "",
                "description": "",
                "supplier_name": self.name,
                "cost": 0.0,
                "price": 0.0,
                "colorways": [],
                "image_url": "",
                "error": str(e)
            }
    
    def _extract_text(self, soup: BeautifulSoup, selector_key: str) -> str:
        """
        Extract text from an element using a selector.
        
        Args:
            soup: The BeautifulSoup object.
            selector_key: The key for the selector in self.selectors.
            
        Returns:
            str: The extracted text or an empty string if not found.
        """
        selector = self.selectors.get(selector_key, '')
        if not selector:
            return ""
        
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return ""
    
    def _extract_price(self, soup: BeautifulSoup, selector_key: str) -> float:
        """
        Extract a price from an element using a selector.
        
        Args:
            soup: The BeautifulSoup object.
            selector_key: The key for the selector in self.selectors.
            
        Returns:
            float: The extracted price or 0.0 if not found or invalid.
        """
        price_text = self._extract_text(soup, selector_key)
        if not price_text:
            return 0.0
        
        # Remove currency symbols and other non-numeric characters
        price_text = ''.join(c for c in price_text if c.isdigit() or c == '.')
        
        try:
            return float(price_text)
        except ValueError:
            return 0.0
    
    def _extract_colorways(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract colorways from the product page.
        
        Args:
            soup: The BeautifulSoup object.
            
        Returns:
            List[str]: A list of available colors.
        """
        selector = self.selectors.get('colorways', '')
        if not selector:
            return []
        
        colorway_elements = soup.select(selector)
        colorways = []
        
        for element in colorway_elements:
            color = element.get_text(strip=True)
            if color and color not in colorways:
                colorways.append(color)
        
        return colorways
    
    def _extract_image_url(self, soup: BeautifulSoup) -> str:
        """
        Extract the product image URL.
        
        Args:
            soup: The BeautifulSoup object.
            
        Returns:
            str: The URL of the product image or an empty string if not found.
        """
        selector = self.selectors.get('image_url', '')
        if not selector:
            return ""
        
        image_element = soup.select_one(selector)
        if not image_element:
            return ""
        
        # Check if the image URL is in the src or data-src attribute
        image_url = image_element.get('src') or image_element.get('data-src', '')
        
        # Make the URL absolute if it's relative
        if image_url:
            return self.build_absolute_url(image_url)
        
        return ""
    
    def close(self) -> None:
        """
        Close the browser and clean up resources.
        """
        if hasattr(self, 'browser_handler') and self.browser_handler:
            self.browser_handler.close()
    
    def __del__(self) -> None:
        """
        Destructor to ensure resources are cleaned up.
        """
        self.close()
