"""
Parser & Transformer Module for the Automated Product Data Scraper.

This module serves as the main entry point for parsing HTML/XML content and transforming
the extracted data into structured, clean, and validated data records.

It integrates the functionality of the HTML parser, data parser, and transformer components
to provide a comprehensive solution for data extraction and transformation.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import lxml.etree as ET
import lxml.html

# Import existing modules
try:
    from src.parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url, extract_structured_data
    )
    from src.parser.parser import Parser
    from src.parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, sanitize_html_content, normalize_url,
        validate_url, validate_sku_format, validate_required_field,
        clean_and_validate_product_data, ProductData
    )
except ImportError:
    # When running from src directory
    from parser.html_parser import (
        create_soup, extract_text, extract_attribute, 
        extract_multiple_texts, extract_image_url, extract_structured_data
    )
    from parser.parser import Parser
    from parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, sanitize_html_content, normalize_url,
        validate_url, validate_sku_format, validate_required_field,
        clean_and_validate_product_data, ProductData
    )

logger = logging.getLogger(__name__)


class ParserTransformer:
    """
    ParserTransformer class that combines HTML parsing and data transformation.
    
    This class provides a unified interface for parsing HTML content and transforming
    the extracted data into structured, clean, and validated records.
    
    Attributes:
        parser: Parser instance for extracting data from HTML
        base_url: Base URL for resolving relative URLs
    """
    
    def __init__(
        self, 
        base_url: str,
        selectors: Optional[Dict[str, str]] = None,
        xpath_selectors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the ParserTransformer.
        
        Args:
            base_url: Base URL for resolving relative URLs
            selectors: Dictionary of CSS selectors for different data fields
            xpath_selectors: Dictionary of XPath expressions for different data fields
        """
        self.parser = Parser(base_url, selectors, xpath_selectors)
        self.base_url = base_url
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def parse_and_transform(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content and transform the extracted data.
        
        Args:
            html_content: Raw HTML content as a string
            
        Returns:
            Dictionary containing parsed, transformed, and validated product data
        """
        # Parse the HTML content
        parsed_data = self.parser.parse(html_content)
        
        # Transform and validate the parsed data
        transformed_data = clean_and_validate_product_data(
            parsed_data, 
            required_fields=["product_name", "sku"],
            base_url=self.base_url
        )
        
        return transformed_data
    
    def parse_and_transform_multiple(
        self, 
        html_content: str, 
        product_container_selector: str
    ) -> List[Dict[str, Any]]:
        """
        Parse HTML content containing multiple products and transform the extracted data.
        
        Args:
            html_content: Raw HTML content as a string
            product_container_selector: CSS selector for the container of each product
            
        Returns:
            List of dictionaries containing parsed, transformed, and validated product data
        """
        # Parse multiple products from the HTML content
        parsed_data_list = self.parser.parse_multiple(html_content, product_container_selector)
        
        # Transform and validate each product's data
        transformed_data_list = []
        for parsed_data in parsed_data_list:
            transformed_data = clean_and_validate_product_data(
                parsed_data, 
                required_fields=["product_name", "sku"],
                base_url=self.base_url
            )
            transformed_data_list.append(transformed_data)
        
        return transformed_data_list
    
    def extract_and_transform_with_selectors(
        self, 
        html_content: Union[str, BeautifulSoup],
        selectors: Dict[str, str],
        attribute_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Extract data using custom selectors and transform the results.
        
        Args:
            html_content: HTML content as a string or BeautifulSoup object
            selectors: Dictionary mapping field names to CSS selectors
            attribute_map: Optional dictionary mapping field names to attribute names
                          (if not provided, text content is extracted)
            
        Returns:
            Dictionary containing extracted, transformed, and validated data
        """
        # Extract structured data using the provided selectors
        extracted_data = extract_structured_data(html_content, selectors, attribute_map)
        
        # Transform and validate the extracted data
        transformed_data = clean_and_validate_product_data(
            extracted_data, 
            base_url=self.base_url
        )
        
        return transformed_data
    
    def extract_and_transform_with_xpath(
        self, 
        html_content: str,
        xpath_expressions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract data using XPath expressions and transform the results.
        
        Args:
            html_content: HTML content as a string
            xpath_expressions: Dictionary mapping field names to XPath expressions
            
        Returns:
            Dictionary containing extracted, transformed, and validated data
        """
        extracted_data = {}
        
        try:
            # Parse HTML with lxml
            tree = lxml.html.fromstring(html_content)
            
            # Extract data using XPath expressions
            for field, xpath in xpath_expressions.items():
                try:
                    elements = tree.xpath(xpath)
                    if elements:
                        if field in ["colorways"]:
                            # For list fields, extract text from all matching elements
                            extracted_data[field] = [element.text_content().strip() for element in elements]
                        elif field in ["image_url"]:
                            # For image URLs, extract the src attribute
                            if hasattr(elements[0], "get"):
                                src = elements[0].get("src")
                                if src:
                                    extracted_data[field] = urljoin(self.base_url, src)
                                else:
                                    extracted_data[field] = ""
                            else:
                                extracted_data[field] = str(elements[0])
                        else:
                            # For other fields, extract text from the first matching element
                            extracted_data[field] = elements[0].text_content().strip()
                    else:
                        # No elements found for this field
                        if field in ["colorways"]:
                            extracted_data[field] = []
                        elif field in ["cost", "price"]:
                            extracted_data[field] = 0.0
                        else:
                            extracted_data[field] = ""
                except Exception as e:
                    self.logger.error(f"Error extracting field '{field}' with XPath '{xpath}': {str(e)}")
                    if field in ["colorways"]:
                        extracted_data[field] = []
                    elif field in ["cost", "price"]:
                        extracted_data[field] = 0.0
                    else:
                        extracted_data[field] = ""
        except Exception as e:
            self.logger.error(f"Error parsing HTML with lxml: {str(e)}")
            return {
                "product_name": "",
                "sku": "",
                "description": "",
                "supplier_name": "",
                "cost": 0.0,
                "price": 0.0,
                "colorways": [],
                "image_url": "",
                "error": f"Error parsing HTML: {str(e)}"
            }
        
        # Transform and validate the extracted data
        transformed_data = clean_and_validate_product_data(
            extracted_data, 
            base_url=self.base_url
        )
        
        return transformed_data


# Utility functions for direct use

def parse_html(
    html_content: str,
    base_url: str,
    selectors: Optional[Dict[str, str]] = None,
    xpath_selectors: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Parse HTML content and extract structured data.
    
    Args:
        html_content: Raw HTML content as a string
        base_url: Base URL for resolving relative URLs
        selectors: Dictionary of CSS selectors for different data fields
        xpath_selectors: Dictionary of XPath expressions for different data fields
        
    Returns:
        Dictionary containing parsed and validated product data
    """
    parser_transformer = ParserTransformer(base_url, selectors, xpath_selectors)
    return parser_transformer.parse_and_transform(html_content)


def parse_multiple_products(
    html_content: str,
    base_url: str,
    product_container_selector: str,
    selectors: Optional[Dict[str, str]] = None,
    xpath_selectors: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Parse HTML content containing multiple products.
    
    Args:
        html_content: Raw HTML content as a string
        base_url: Base URL for resolving relative URLs
        product_container_selector: CSS selector for the container of each product
        selectors: Dictionary of CSS selectors for different data fields
        xpath_selectors: Dictionary of XPath expressions for different data fields
        
    Returns:
        List of dictionaries containing parsed and validated product data
    """
    parser_transformer = ParserTransformer(base_url, selectors, xpath_selectors)
    return parser_transformer.parse_and_transform_multiple(html_content, product_container_selector)


def transform_data(data: Dict[str, Any], base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Transform and validate product data.
    
    Args:
        data: Dictionary of product data
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Dictionary containing transformed and validated product data
    """
    return clean_and_validate_product_data(data, base_url=base_url)
