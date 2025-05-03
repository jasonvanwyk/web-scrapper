"""
HTML Parser module for the Automated Product Data Scraper.

This module provides functions for parsing HTML content using BeautifulSoup4
and extracting specific elements and attributes based on CSS selectors.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from bs4 import BeautifulSoup

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


def extract_text(html_content: Union[str, BeautifulSoup], selector: str, default: str = "") -> str:
    """
    Extract text from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selector: CSS selector to find the element
        default: Default value to return if element is not found
        
    Returns:
        Text content of the element or default value if not found
    """
    try:
        soup = html_content if isinstance(html_content, BeautifulSoup) else create_soup(html_content)
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        logger.debug(f"Element not found with selector: {selector}")
        return default
    except Exception as e:
        logger.error(f"Error extracting text with selector '{selector}': {str(e)}")
        return default


def extract_attribute(
    html_content: Union[str, BeautifulSoup], 
    selector: str, 
    attribute: str,
    default: str = ""
) -> str:
    """
    Extract an attribute from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selector: CSS selector to find the element
        attribute: Name of the attribute to extract
        default: Default value to return if element or attribute is not found
        
    Returns:
        Attribute value or default value if not found
    """
    try:
        soup = html_content if isinstance(html_content, BeautifulSoup) else create_soup(html_content)
        element = soup.select_one(selector)
        if element and element.has_attr(attribute):
            return element[attribute]
        logger.debug(f"Element or attribute '{attribute}' not found with selector: {selector}")
        return default
    except Exception as e:
        logger.error(f"Error extracting attribute '{attribute}' with selector '{selector}': {str(e)}")
        return default


def extract_multiple_texts(
    html_content: Union[str, BeautifulSoup], 
    selector: str
) -> List[str]:
    """
    Extract text from multiple HTML elements identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selector: CSS selector to find the elements
        
    Returns:
        List of text content from matching elements (empty list if none found)
    """
    try:
        soup = html_content if isinstance(html_content, BeautifulSoup) else create_soup(html_content)
        elements = soup.select(selector)
        return [element.get_text(strip=True) for element in elements]
    except Exception as e:
        logger.error(f"Error extracting multiple texts with selector '{selector}': {str(e)}")
        return []


def extract_multiple_attributes(
    html_content: Union[str, BeautifulSoup], 
    selector: str, 
    attribute: str
) -> List[str]:
    """
    Extract an attribute from multiple HTML elements identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selector: CSS selector to find the elements
        attribute: Name of the attribute to extract
        
    Returns:
        List of attribute values from matching elements (empty list if none found)
    """
    try:
        soup = html_content if isinstance(html_content, BeautifulSoup) else create_soup(html_content)
        elements = soup.select(selector)
        return [element[attribute] for element in elements if element.has_attr(attribute)]
    except Exception as e:
        logger.error(f"Error extracting multiple attributes '{attribute}' with selector '{selector}': {str(e)}")
        return []


def extract_image_url(
    html_content: Union[str, BeautifulSoup], 
    selector: str,
    attribute: str = "src",
    default: str = ""
) -> str:
    """
    Extract an image URL from an HTML element identified by a CSS selector.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selector: CSS selector to find the image element
        attribute: Attribute containing the URL (usually 'src' or 'data-src')
        default: Default value to return if image or attribute is not found
        
    Returns:
        Image URL or default value if not found
    """
    return extract_attribute(html_content, selector, attribute, default)


def extract_structured_data(
    html_content: Union[str, BeautifulSoup],
    selectors: Dict[str, str],
    attribute_map: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Extract multiple data points from HTML using a dictionary of selectors.
    
    Args:
        html_content: HTML content as a string or BeautifulSoup object
        selectors: Dictionary mapping field names to CSS selectors
        attribute_map: Optional dictionary mapping field names to attribute names
                      (if not provided, text content is extracted)
        
    Returns:
        Dictionary of extracted data with field names as keys
    """
    result = {}
    soup = html_content if isinstance(html_content, BeautifulSoup) else create_soup(html_content)
    
    attribute_map = attribute_map or {}
    
    for field, selector in selectors.items():
        try:
            if field in attribute_map:
                result[field] = extract_attribute(soup, selector, attribute_map[field], "")
            else:
                result[field] = extract_text(soup, selector, "")
        except Exception as e:
            logger.error(f"Error extracting field '{field}' with selector '{selector}': {str(e)}")
            result[field] = ""
    
    return result
