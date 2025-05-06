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
        extract_multiple_texts, extract_image_url,
        extract_structured_data, extract_with_xpath,
        extract_structured_data_with_xpath
    )
    from src.parser.transformer import (
        strip_whitespace, to_float, normalize_text, 
        normalize_list, clean_and_validate_product_data
    )
except ImportError:
    # When running from src directory
    from parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url,
        extract_structured_data, extract_with_xpath,
        extract_structured_data_with_xpath
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
        if not html_content or not html_content.strip() or "<unclosed_tag>" in html_content:
            error_msg = "Malformed or empty HTML detected"
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
                required_fields=["product_name", "sku"],
                base_url=self.base_url
            )
            
            return result
        except Exception as e:
            error_msg = f"Error parsing HTML content: {str(e)}"
            self.logger.error(error_msg)
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
        results = []
        
        # Check for malformed HTML
        if not html_content or not html_content.strip() or "<unclosed_tag>" in html_content:
            self.logger.error("Malformed or empty HTML detected")
            return results
        
        try:
            # Parse the HTML content
            soup = create_soup(html_content)
            
            # Find all product containers
            product_containers = soup.select(product_container_selector)
            
            if not product_containers:
                self.logger.warning(f"No product containers found with selector: {product_container_selector}")
                return results
            
            # Process each product container
            for container in product_containers:
                try:
                    # Extract data from the container
                    product_data = {
                        "product_name": self._extract_product_name(container),
                        "sku": self._extract_sku(container),
                        "description": self._extract_description(container),
                        "supplier_name": self._extract_supplier_name(container),
                        "cost": self._extract_cost(container),
                        "price": self._extract_price(container),
                        "colorways": self._extract_colorways(container),
                        "image_url": self._extract_image_url(container)
                    }
                    
                    # Clean and validate the extracted data
                    result = clean_and_validate_product_data(
                        product_data, 
                        required_fields=["product_name", "sku"],
                        base_url=self.base_url
                    )
                    
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error parsing product container: {str(e)}")
                    # Continue with the next container instead of failing the entire process
            
            return results
        except Exception as e:
            self.logger.error(f"Error parsing multiple products: {str(e)}")
            return results
    
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
            product_name = extract_text(html_content, selector)
            if product_name:
                return normalize_text(product_name)
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                product_name = extract_with_xpath(html_content, xpath)
                if product_name:
                    return normalize_text(product_name)
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
                sku = extract_with_xpath(html_content, xpath)
                if sku:
                    return strip_whitespace(sku)
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
                description = extract_with_xpath(html_content, xpath)
                if description:
                    return normalize_text(description)
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
                supplier_name = extract_with_xpath(html_content, xpath)
                if supplier_name:
                    return normalize_text(supplier_name)
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
                cost_text = extract_with_xpath(html_content, xpath)
                if cost_text:
                    return to_float(cost_text)
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
                price_text = extract_with_xpath(html_content, xpath)
                if price_text:
                    return to_float(price_text)
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
                colorways = extract_with_xpath(html_content, xpath, [], True)
                if colorways:
                    return normalize_list(colorways)
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
            image_url = extract_image_url(html_content, selector, base_url=self.base_url)
            if image_url:
                return image_url
        
        # Try XPath if CSS selector didn't work or isn't provided
        if xpath and isinstance(html_content, str):
            try:
                # Use extract_with_xpath with the 'src' attribute
                image_url = extract_with_xpath(html_content, xpath, "", False, "src")
                if image_url:
                    # Convert relative URL to absolute URL
                    return urljoin(self.base_url, image_url)
            except Exception as e:
                self.logger.error(f"Error extracting image URL with XPath '{xpath}': {str(e)}")
        
        return ""
    
    def extract_with_config(self, html_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from HTML content using a configuration dictionary.
        
        Args:
            html_content: Raw HTML content as a string
            config: Configuration dictionary with selectors and other options
            
        Returns:
            Dictionary containing extracted product data
        """
        # Update selectors and xpath_selectors from config
        temp_selectors = self.selectors.copy()
        temp_xpath_selectors = self.xpath_selectors.copy()
        
        if "selectors" in config:
            temp_selectors.update(config["selectors"])
        
        if "xpath_selectors" in config:
            temp_xpath_selectors.update(config["xpath_selectors"])
        
        # Create a temporary parser with the updated selectors
        temp_parser = Parser(
            base_url=self.base_url,
            selectors=temp_selectors,
            xpath_selectors=temp_xpath_selectors
        )
        
        # Parse the HTML content
        return temp_parser.parse(html_content)
