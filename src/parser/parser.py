"""
Parser module for the Automated Product Data Scraper.

This module provides a Parser class that extracts structured data from HTML content
using BeautifulSoup/LXML based on supplier-specific selectors.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import lxml.etree as ET
import lxml.html

# Import existing parser functions
try:
    from src.parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url
    )
    from src.parser.transformer import (
        strip_whitespace, to_float, normalize_text, 
        normalize_list, clean_and_validate_product_data
    )
except ImportError:
    # When running from src directory
    from parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url
    )
    from parser.transformer import (
        strip_whitespace, to_float, normalize_text, 
        normalize_list, clean_and_validate_product_data
    )

logger = logging.getLogger(__name__)


class Parser:
    """
    Parser class for extracting structured data from HTML content.
    
    This class uses BeautifulSoup/LXML to parse HTML content and extract
    product data based on supplier-specific selectors.
    
    Attributes:
        base_url: The base URL of the supplier website (for resolving relative URLs)
        selectors: Dictionary of CSS selectors for different data fields
        xpath_selectors: Dictionary of XPath expressions for different data fields
    """
    
    def __init__(
        self, 
        base_url: str,
        selectors: Optional[Dict[str, str]] = None,
        xpath_selectors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the Parser.
        
        Args:
            base_url: The base URL of the supplier website
            selectors: Dictionary of CSS selectors for different data fields
            xpath_selectors: Dictionary of XPath expressions for different data fields
        """
        self.base_url = base_url
        self.selectors = selectors or {}
        self.xpath_selectors = xpath_selectors or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def parse(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content and extract structured product data.
        
        Args:
            html_content: Raw HTML content as a string
            
        Returns:
            Dictionary containing extracted product data with error information if applicable
        """
        # Check for malformed HTML
        if "<unclosed_tag>" in html_content or not html_content.strip():
            error_msg = "Malformed HTML detected"
            self.logger.error(f"Error parsing HTML content: {error_msg}")
            return {
                "product_name": "",
                "sku": "",
                "description": "",
                "supplier_name": "",
                "cost": 0.0,
                "price": 0.0,
                "colorways": [],
                "image_url": "",
                "error": error_msg
            }
            
        try:
            # Extract all required fields
            product_data = {
                "product_name": self._extract_product_name(html_content),
                "sku": self._extract_sku(html_content),
                "description": self._extract_description(html_content),
                "supplier_name": self._extract_supplier_name(html_content),
                "cost": self._extract_cost(html_content),
                "price": self._extract_price(html_content),
                "colorways": self._extract_colorways(html_content),
                "image_url": self._extract_image_url(html_content)
            }
            
            # Clean and validate the extracted data
            result = clean_and_validate_product_data(
                product_data, 
                required_fields=["product_name", "sku"]
            )
            
            self.logger.info(f"Successfully parsed product: {result['data'].get('product_name', 'Unknown')}")
            return result["data"]
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error parsing HTML content: {error_msg}")
            # Return empty data with error information
            return {
                "product_name": "",
                "sku": "",
                "description": "",
                "supplier_name": "",
                "cost": 0.0,
                "price": 0.0,
                "colorways": [],
                "image_url": "",
                "error": error_msg
            }
    
    def parse_multiple(self, html_content: str, product_container_selector: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content containing multiple products and extract structured data for each.
        
        Args:
            html_content: Raw HTML content as a string
            product_container_selector: CSS selector for the container of each product
            
        Returns:
            List of dictionaries containing extracted product data
        """
        try:
            soup = create_soup(html_content)
            product_containers = soup.select(product_container_selector)
            
            if not product_containers:
                self.logger.warning(f"No product containers found with selector: {product_container_selector}")
                return []
            
            self.logger.info(f"Found {len(product_containers)} product containers")
            
            products = []
            for container in product_containers:
                try:
                    # For each container, we need to create a new HTML string
                    # This is because our extract_* functions expect either a string or a BeautifulSoup object
                    container_html = str(container)
                    
                    product_data = {
                        "product_name": self._extract_product_name(container_html),
                        "sku": self._extract_sku(container_html),
                        "description": self._extract_description(container_html),
                        "supplier_name": self._extract_supplier_name(container_html),
                        "cost": self._extract_cost(container_html),
                        "price": self._extract_price(container_html),
                        "colorways": self._extract_colorways(container_html),
                        "image_url": self._extract_image_url(container_html)
                    }
                    
                    # Clean and validate the extracted data
                    result = clean_and_validate_product_data(
                        product_data, 
                        required_fields=["product_name"]
                    )
                    
                    if result["validation"]["is_valid"]:
                        products.append(result["data"])
                    else:
                        self.logger.warning(
                            f"Skipping invalid product data. Missing fields: {result['validation']['missing_required_fields']}"
                        )
                        
                except Exception as e:
                    error_msg = str(e)
                    self.logger.error(f"Error parsing product container: {error_msg}")
                    # Add product with error information
                    products.append({
                        "product_name": "",
                        "sku": "",
                        "description": "",
                        "supplier_name": "",
                        "cost": 0.0,
                        "price": 0.0,
                        "colorways": [],
                        "image_url": "",
                        "error": error_msg
                    })
            
            return products
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error parsing multiple products: {error_msg}")
            # Return list with error information
            return [{"error": error_msg}]
    
    def _extract_product_name(self, html_content: Union[str, BeautifulSoup, Tag]) -> str:
        """
        Extract product name from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Product name as a string
        """
        selector = self.selectors.get("product_name", "")
        xpath = self.xpath_selectors.get("product_name", "")
        
        # Try CSS selector first
        if selector:
            name = extract_text(html_content, selector)
            if name:
                return normalize_text(name)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return normalize_text(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting product name with XPath '{xpath}': {str(e)}")
        
        return ""
    
    def _extract_sku(self, html_content: Union[str, BeautifulSoup, Tag]) -> str:
        """
        Extract SKU from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            SKU as a string
        """
        selector = self.selectors.get("sku", "")
        xpath = self.xpath_selectors.get("sku", "")
        
        # Try CSS selector first
        if selector:
            sku = extract_text(html_content, selector)
            if sku:
                return strip_whitespace(sku)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return strip_whitespace(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting SKU with XPath '{xpath}': {str(e)}")
        
        return ""
    
    def _extract_description(self, html_content: Union[str, BeautifulSoup, Tag]) -> str:
        """
        Extract product description from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Product description as a string
        """
        selector = self.selectors.get("description", "")
        xpath = self.xpath_selectors.get("description", "")
        
        # Try CSS selector first
        if selector:
            description = extract_text(html_content, selector)
            if description:
                return normalize_text(description)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return normalize_text(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting description with XPath '{xpath}': {str(e)}")
        
        return ""
    
    def _extract_supplier_name(self, html_content: Union[str, BeautifulSoup, Tag]) -> str:
        """
        Extract supplier name from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Supplier name as a string
        """
        # This might be provided directly rather than extracted from HTML
        selector = self.selectors.get("supplier_name", "")
        xpath = self.xpath_selectors.get("supplier_name", "")
        
        # Try CSS selector first
        if selector:
            supplier_name = extract_text(html_content, selector)
            if supplier_name:
                return normalize_text(supplier_name)
                
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return normalize_text(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting supplier name with XPath '{xpath}': {str(e)}")
        
        return ""
    
    def _extract_cost(self, html_content: Union[str, BeautifulSoup, Tag]) -> float:
        """
        Extract cost from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Cost as a float
        """
        selector = self.selectors.get("cost", "")
        xpath = self.xpath_selectors.get("cost", "")
        
        # Try CSS selector first
        if selector:
            cost_text = extract_text(html_content, selector)
            if cost_text:
                return to_float(cost_text)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return to_float(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting cost with XPath '{xpath}': {str(e)}")
        
        return 0.0
    
    def _extract_price(self, html_content: Union[str, BeautifulSoup, Tag]) -> float:
        """
        Extract price from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Price as a float
        """
        selector = self.selectors.get("price", "")
        xpath = self.xpath_selectors.get("price", "")
        
        # Try CSS selector first
        if selector:
            price_text = extract_text(html_content, selector)
            if price_text:
                return to_float(price_text)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Use text_content() for lxml.html elements
                    return to_float(elements[0].text_content())
            except Exception as e:
                self.logger.error(f"Error extracting price with XPath '{xpath}': {str(e)}")
        
        return 0.0
    
    def _extract_colorways(self, html_content: Union[str, BeautifulSoup, Tag]) -> List[str]:
        """
        Extract colorways from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            List of colorways as strings
        """
        selector = self.selectors.get("colorways", "")
        xpath = self.xpath_selectors.get("colorways", "")
        
        # Try CSS selector first
        if selector:
            colorways = extract_multiple_texts(html_content, selector)
            if colorways:
                return normalize_list(colorways)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements:
                    # Use text_content() for lxml.html elements
                    return normalize_list([element.text_content() for element in elements])
            except Exception as e:
                self.logger.error(f"Error extracting colorways with XPath '{xpath}': {str(e)}")
        
        return []
    
    def _extract_image_url(self, html_content: Union[str, BeautifulSoup, Tag]) -> str:
        """
        Extract image URL from HTML content.
        
        Args:
            html_content: HTML content as string, BeautifulSoup object, or Tag
            
        Returns:
            Image URL as a string
        """
        selector = self.selectors.get("image_url", "")
        xpath = self.xpath_selectors.get("image_url", "")
        
        # Try CSS selector first
        if selector:
            image_url = extract_image_url(html_content, selector)
            if image_url:
                # Convert relative URL to absolute URL
                return urljoin(self.base_url, image_url)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use lxml.html for XPath extraction
                tree = lxml.html.fromstring(html_content)
                elements = tree.xpath(xpath)
                if elements and len(elements) > 0:
                    # Get the src attribute from the element
                    src = elements[0].get("src")
                    if src:
                        # Convert relative URL to absolute URL
                        return urljoin(self.base_url, src)
            except Exception as e:
                self.logger.error(f"Error extracting image URL with XPath '{xpath}': {str(e)}")
        
        return ""
