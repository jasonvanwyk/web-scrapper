"""
Static scraper module.

This module provides a concrete implementation of the BaseScraper for static HTML websites.
It uses the RequestHandler to make HTTP requests and BeautifulSoup for HTML parsing.
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.base_scraper import BaseScraper
    from src.http_client.request_handler import RequestHandler
    from src.parser.html_parser import extract_text, extract_attribute, extract_image_url, extract_multiple_texts
    from src.parser.transformer import strip_whitespace, to_float, normalize_list, clean_and_validate_product_data
except ModuleNotFoundError:
    from scrapers.base_scraper import BaseScraper
    from http_client.request_handler import RequestHandler
    from parser.html_parser import extract_text, extract_attribute, extract_image_url, extract_multiple_texts
    from parser.transformer import strip_whitespace, to_float, normalize_list, clean_and_validate_product_data


class StaticScraper(BaseScraper):
    """
    Concrete implementation of BaseScraper for static HTML websites.
    
    This class uses the RequestHandler to make HTTP requests and BeautifulSoup
    for parsing HTML content.
    
    Attributes:
        request_handler: The RequestHandler instance for making HTTP requests.
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
        **kwargs
    ):
        """
        Initialize the static scraper.
        
        Args:
            name: The name of the supplier.
            base_url: The base URL of the supplier website.
            requires_login: Whether login is required.
            username: The username for authentication.
            password: The password for authentication.
            selectors: CSS selectors for data extraction.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(name, base_url, **kwargs)
        self.requires_login = requires_login
        self.username = username
        self.password = password
        self.selectors = selectors or {}
        
        # Initialize the request handler
        self.request_handler = kwargs.get('request_handler', RequestHandler())
        
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
            # Get the login page to retrieve any CSRF token if needed
            response = self.request_handler.get(login_url)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for CSRF token if specified in selectors
            csrf_token = None
            if 'csrf_token' in self.selectors:
                csrf_selector = self.selectors['csrf_token']
                csrf_element = soup.select_one(csrf_selector)
                if csrf_element and csrf_element.has_attr('value'):
                    csrf_token = csrf_element['value']
                    self.logger.debug(f"Found CSRF token: {csrf_token}")
            
            # Prepare login data
            login_data = {
                self.selectors.get('username_field', 'username'): username,
                self.selectors.get('password_field', 'password'): password
            }
            
            # Add CSRF token if found
            if csrf_token:
                login_data[self.selectors.get('csrf_field', 'csrf_token')] = csrf_token
            
            # Submit the login form
            login_submit_url = self.selectors.get('login_submit_url', login_url)
            login_submit_url = self.build_absolute_url(login_submit_url)
            
            response = self.request_handler.post(
                login_submit_url,
                data=login_data,
                allow_redirects=True
            )
            
            # Check if login was successful
            # This is a simple check based on status code and URL
            # In a real implementation, we would check for specific elements or redirects
            if response.status_code == 200:
                # Check for success indicator if specified in selectors
                if 'login_success_indicator' in self.selectors:
                    success_indicator = self.selectors['login_success_indicator']
                    soup = BeautifulSoup(response.text, 'lxml')
                    if soup.select_one(success_indicator):
                        self.logger.info(f"Login successful for {self.name}")
                        return True
                    else:
                        self.logger.warning(f"Login failed for {self.name}: success indicator not found")
                        return False
                else:
                    # If no specific success indicator, assume login was successful
                    self.logger.info(f"Login successful for {self.name}")
                    return True
            else:
                self.logger.warning(f"Login failed for {self.name}: status code {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed for {self.name}: {e}")
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
        self.logger.info(f"Getting product URLs for {self.name}")
        
        # Use the provided category URL or the default from selectors
        if category_url is None:
            category_url = self.selectors.get('category_url', '')
            category_url = self.build_absolute_url(category_url)
        
        product_urls = []
        current_page = 1
        max_pages = int(self.selectors.get('max_pages', '1'))
        
        try:
            while current_page <= max_pages:
                # Get the page URL for the current page
                page_url = self.handle_pagination(category_url, current_page)
                
                # Fetch the page
                response = self.request_handler.get(page_url)
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract product URLs using the product link selector
                product_link_selector = self.selectors.get('product_link', 'a.product')
                product_links = soup.select(product_link_selector)
                
                # Extract and normalize URLs
                for link in product_links:
                    if link.has_attr('href'):
                        product_url = self.build_absolute_url(link['href'])
                        if product_url not in product_urls:
                            product_urls.append(product_url)
                
                self.logger.debug(f"Found {len(product_links)} product links on page {current_page}")
                
                # Check if there's a next page
                next_page_selector = self.selectors.get('next_page', '')
                if next_page_selector:
                    next_page = soup.select_one(next_page_selector)
                    if not next_page:
                        self.logger.debug(f"No next page found, stopping at page {current_page}")
                        break
                
                current_page += 1
            
            self.logger.info(f"Found {len(product_urls)} unique product URLs for {self.name}")
            return product_urls
            
        except Exception as e:
            self.logger.error(f"Error getting product URLs for {self.name}: {e}")
            return []
    
    def handle_pagination(self, url: str, page: int = 1) -> str:
        """
        Handle pagination for multi-page results.
        
        Args:
            url: The base URL for the page.
            page: The page number to navigate to.
            
        Returns:
            str: The URL for the specified page.
        """
        if page == 1:
            return url
        
        # Check if there's a pagination format in selectors
        pagination_format = self.selectors.get('pagination_format', '')
        if pagination_format:
            # Replace {page} with the actual page number
            page_url = pagination_format.replace('{page}', str(page))
            return self.build_absolute_url(page_url)
        
        # Default pagination handling: add ?page=N or &page=N
        parsed_url = urlparse(url)
        
        # If the URL already has query parameters, preserve them
        if parsed_url.query:
            from urllib.parse import parse_qs, urlencode
            
            # Parse the query string into a dictionary
            query_params = parse_qs(parsed_url.query)
            
            # Add or update the page parameter
            query_params['page'] = [str(page)]
            
            # Convert the dictionary back to a query string
            new_query = urlencode(query_params, doseq=True)
            
            # Reconstruct the URL with the new query string
            return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
        else:
            return f"{url}?page={page}"
    
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
            # Fetch the product page
            response = self.request_handler.get(product_url)
            html_content = response.text
            
            # Extract data using selectors and our parser/transformer modules
            raw_data = {
                "product_name": extract_text(html_content, self.selectors.get('product_name', '')),
                "sku": extract_text(html_content, self.selectors.get('sku', '')),
                "description": extract_text(html_content, self.selectors.get('description', '')),
                "supplier_name": self.name,
                "cost": to_float(extract_text(html_content, self.selectors.get('cost', ''))),
                "price": to_float(extract_text(html_content, self.selectors.get('price', ''))),
                "colorways": normalize_list(extract_multiple_texts(html_content, self.selectors.get('colorways', ''))),
                "image_url": self.build_absolute_url(extract_image_url(html_content, self.selectors.get('image_url', ''))),
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
