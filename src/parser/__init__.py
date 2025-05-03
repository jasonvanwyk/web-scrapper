"""
Parser module for the Automated Product Data Scraper.

This module contains components for parsing HTML content and transforming
extracted data into standardized formats.
"""

from .html_parser import (
    create_soup, extract_text, extract_attribute, 
    extract_multiple_texts, extract_multiple_attributes,
    extract_image_url, extract_structured_data
)
from .transformer import (
    strip_whitespace, to_float, normalize_currency, normalize_text,
    normalize_list, validate_sku_format, validate_required_field,
    clean_and_validate_product_data
)
from .parser import Parser

__all__ = [
    'create_soup', 'extract_text', 'extract_attribute', 
    'extract_multiple_texts', 'extract_multiple_attributes',
    'extract_image_url', 'extract_structured_data',
    'strip_whitespace', 'to_float', 'normalize_currency', 'normalize_text',
    'normalize_list', 'validate_sku_format', 'validate_required_field',
    'clean_and_validate_product_data',
    'Parser'
]
