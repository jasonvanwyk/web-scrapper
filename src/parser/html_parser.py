"""
HTML Parser module for the Automated Product Data Scraper.

This module provides functions for parsing HTML content using BeautifulSoup4
and LXML, extracting specific elements and attributes based on CSS selectors
or XPath expressions.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup, Tag
import lxml.html
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


def create_soup(html_content: str) -> BeautifulSoup:
    """
    Create a BeautifulSoup object from HTML content.
    
    Args:
        html_content: HTML content as a string
        
    Returns:
        BeautifulSoup object
    """
    return BeautifulSoup(html_content, 'lxml')


def extract_text(html_content: Union[str, BeautifulSoup, Tag], selector: str, default: str = "") -> str:
    """
    Extract text from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selector: CSS selector to find the element
        default: Default value to return if element is not found
        
    Returns:
        Text content of the element or default value if not found
    """
    try:
        # Handle different input types
        if isinstance(html_content, str):
            soup = create_soup(html_content)
        elif isinstance(html_content, (BeautifulSoup, Tag)):
            soup = html_content
        else:
            logger.error(f"Unsupported content type: {type(html_content)}")
            return default
            
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        logger.debug(f"Element not found with selector: {selector}")
        return default
    except Exception as e:
        logger.error(f"Error extracting text with selector '{selector}': {str(e)}")
        return default


def extract_attribute(
    html_content: Union[str, BeautifulSoup, Tag], 
    selector: str, 
    attribute: str,
    default: str = ""
) -> str:
    """
    Extract an attribute from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selector: CSS selector to find the element
        attribute: Name of the attribute to extract
        default: Default value to return if element or attribute is not found
        
    Returns:
        Attribute value or default value if not found
    """
    try:
        # Handle different input types
        if isinstance(html_content, str):
            soup = create_soup(html_content)
        elif isinstance(html_content, (BeautifulSoup, Tag)):
            soup = html_content
        else:
            logger.error(f"Unsupported content type: {type(html_content)}")
            return default
            
        element = soup.select_one(selector)
        if element and element.has_attr(attribute):
            return element[attribute]
        logger.debug(f"Element or attribute '{attribute}' not found with selector: {selector}")
        return default
    except Exception as e:
        logger.error(f"Error extracting attribute '{attribute}' with selector '{selector}': {str(e)}")
        return default


def extract_multiple_texts(
    html_content: Union[str, BeautifulSoup, Tag], 
    selector: str
) -> List[str]:
    """
    Extract text from multiple HTML elements identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selector: CSS selector to find the elements
        
    Returns:
        List of text content from matching elements (empty list if none found)
    """
    try:
        # Handle different input types
        if isinstance(html_content, str):
            soup = create_soup(html_content)
        elif isinstance(html_content, (BeautifulSoup, Tag)):
            soup = html_content
        else:
            logger.error(f"Unsupported content type: {type(html_content)}")
            return []
            
        elements = soup.select(selector)
        return [element.get_text(strip=True) for element in elements]
    except Exception as e:
        logger.error(f"Error extracting multiple texts with selector '{selector}': {str(e)}")
        return []


def extract_multiple_attributes(
    html_content: Union[str, BeautifulSoup, Tag], 
    selector: str, 
    attribute: str
) -> List[str]:
    """
    Extract an attribute from multiple HTML elements identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selector: CSS selector to find the elements
        attribute: Name of the attribute to extract
        
    Returns:
        List of attribute values from matching elements (empty list if none found)
    """
    try:
        # Handle different input types
        if isinstance(html_content, str):
            soup = create_soup(html_content)
        elif isinstance(html_content, (BeautifulSoup, Tag)):
            soup = html_content
        else:
            logger.error(f"Unsupported content type: {type(html_content)}")
            return []
            
        elements = soup.select(selector)
        return [element[attribute] for element in elements if element.has_attr(attribute)]
    except Exception as e:
        logger.error(f"Error extracting multiple attributes '{attribute}' with selector '{selector}': {str(e)}")
        return []


def extract_image_url(
    html_content: Union[str, BeautifulSoup, Tag], 
    selector: str,
    attribute: str = "src",
    default: str = "",
    base_url: Optional[str] = None
) -> str:
    """
    Extract an image URL from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selector: CSS selector to find the image element
        attribute: Attribute containing the URL (usually 'src' or 'data-src')
        default: Default value to return if image or attribute is not found
        base_url: Base URL to resolve relative URLs (if None, returns URL as-is)
        
    Returns:
        Image URL or default value if not found
    """
    url = extract_attribute(html_content, selector, attribute, default)
    if url and base_url:
        return urljoin(base_url, url)
    return url


def extract_structured_data(
    html_content: Union[str, BeautifulSoup, Tag],
    selectors: Dict[str, str],
    attribute_map: Optional[Dict[str, str]] = None,
    base_url: Optional[str] = None
) -> Dict[str, str]:
    """
    Extract multiple data points from HTML using a dictionary of selectors.
    
    Args:
        html_content: HTML content as a string, BeautifulSoup object, or Tag
        selectors: Dictionary mapping field names to CSS selectors
        attribute_map: Optional dictionary mapping field names to attribute names
                      (if not provided, text content is extracted)
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Dictionary of extracted data with field names as keys
    """
    result = {}
    
    # Handle different input types
    if isinstance(html_content, str):
        soup = create_soup(html_content)
    elif isinstance(html_content, (BeautifulSoup, Tag)):
        soup = html_content
    else:
        logger.error(f"Unsupported content type: {type(html_content)}")
        return {}
    
    attribute_map = attribute_map or {}
    
    for field, selector in selectors.items():
        try:
            if field in attribute_map:
                if field == "image_url" and base_url:
                    # Handle image URLs specially to resolve relative URLs
                    value = extract_attribute(soup, selector, attribute_map[field], "")
                    result[field] = urljoin(base_url, value) if value else ""
                else:
                    result[field] = extract_attribute(soup, selector, attribute_map[field], "")
            else:
                result[field] = extract_text(soup, selector, "")
        except Exception as e:
            logger.error(f"Error extracting field '{field}' with selector '{selector}': {str(e)}")
            result[field] = ""
    
    return result


def extract_with_xpath(
    html_content: str,
    xpath: str,
    default: Any = "",
    is_list: bool = False,
    attribute: Optional[str] = None
) -> Union[str, List[str], Any]:
    """
    Extract data from HTML using an XPath expression.
    
    Args:
        html_content: HTML content as a string
        xpath: XPath expression to find the element(s)
        default: Default value to return if element is not found
        is_list: Whether to return a list of results or just the first one
        attribute: Optional attribute name to extract (if None, extracts text content)
        
    Returns:
        Extracted data (string, list, or default value)
    """
    try:
        # Parse HTML with lxml
        tree = lxml.html.fromstring(html_content)
        
        # Find elements matching the XPath
        elements = tree.xpath(xpath)
        
        if not elements:
            logger.debug(f"No elements found with XPath: {xpath}")
            return default
        
        if is_list:
            # Return list of values
            if attribute:
                return [elem.get(attribute, "") for elem in elements if hasattr(elem, "get")]
            else:
                return [elem.text_content().strip() if hasattr(elem, "text_content") else str(elem) 
                        for elem in elements]
        else:
            # Return first value
            if attribute:
                return elements[0].get(attribute, "") if hasattr(elements[0], "get") else default
            else:
                return elements[0].text_content().strip() if hasattr(elements[0], "text_content") else str(elements[0])
    except Exception as e:
        logger.error(f"Error extracting data with XPath '{xpath}': {str(e)}")
        return default if not is_list else []


def extract_structured_data_with_xpath(
    html_content: str,
    xpath_expressions: Dict[str, str],
    attribute_map: Optional[Dict[str, str]] = None,
    list_fields: Optional[List[str]] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract multiple data points from HTML using a dictionary of XPath expressions.
    
    Args:
        html_content: HTML content as a string
        xpath_expressions: Dictionary mapping field names to XPath expressions
        attribute_map: Optional dictionary mapping field names to attribute names
                      (if not provided, text content is extracted)
        list_fields: Optional list of field names that should return lists
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Dictionary of extracted data with field names as keys
    """
    result = {}
    attribute_map = attribute_map or {}
    list_fields = list_fields or ["colorways"]
    
    try:
        # Parse HTML with lxml
        tree = lxml.html.fromstring(html_content)
        
        for field, xpath in xpath_expressions.items():
            try:
                is_list = field in list_fields
                attribute = attribute_map.get(field)
                
                if field == "image_url" and base_url:
                    # Handle image URLs specially
                    value = extract_with_xpath(html_content, xpath, "", False, attribute or "src")
                    result[field] = urljoin(base_url, value) if value else ""
                else:
                    result[field] = extract_with_xpath(html_content, xpath, 
                                                      [] if is_list else "", 
                                                      is_list, 
                                                      attribute)
            except Exception as e:
                logger.error(f"Error extracting field '{field}' with XPath '{xpath}': {str(e)}")
                result[field] = [] if is_list else ""
    except Exception as e:
        logger.error(f"Error parsing HTML with lxml: {str(e)}")
        return {}
    
    return result
