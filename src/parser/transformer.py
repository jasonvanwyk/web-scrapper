"""
Data Transformer module for the Automated Product Data Scraper.

This module provides functions for cleaning, normalizing, and validating
data extracted from HTML content.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def strip_whitespace(text: Optional[str]) -> str:
    """
    Strip whitespace from text and handle None values.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text with whitespace removed
    """
    if text is None:
        return ""
    return " ".join(text.split())


def to_float(
    text: Optional[str], 
    default: float = 0.0,
    remove_chars: str = "$€£¥"
) -> float:
    """
    Convert text to float, handling currency symbols and formatting.
    
    Args:
        text: Input text to convert
        default: Default value to return if conversion fails
        remove_chars: Characters to remove before conversion
        
    Returns:
        Converted float value or default if conversion fails
    """
    if not text:
        return default
    
    try:
        # Remove currency symbols and other non-numeric characters
        clean_text = text
        for char in remove_chars:
            clean_text = clean_text.replace(char, "")
        
        # Handle European format (1.234,56 -> 1234.56)
        if "," in clean_text and "." in clean_text:
            if clean_text.rindex(".") < clean_text.rindex(","):
                # European format: periods for thousands, comma for decimal
                clean_text = clean_text.replace(".", "").replace(",", ".")
            else:
                # US/UK format: commas for thousands, period for decimal
                clean_text = clean_text.replace(",", "")
        # Handle format with only comma as decimal separator (123,45 -> 123.45)
        elif "," in clean_text:
            clean_text = clean_text.replace(",", ".")
        
        return float(clean_text)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert '{text}' to float: {str(e)}")
        return default


def normalize_currency(
    price_text: Optional[str], 
    default: float = 0.0,
    currency_symbol: Optional[str] = None
) -> Dict[str, Union[float, str]]:
    """
    Normalize currency values and extract currency symbol.
    
    Args:
        price_text: Input price text to normalize
        default: Default value to return if conversion fails
        currency_symbol: Optional currency symbol to use if not detected
        
    Returns:
        Dictionary with 'value' (float) and 'currency' (str) keys
    """
    if not price_text:
        return {"value": default, "currency": currency_symbol or ""}
    
    # Try to extract currency symbol
    currency = currency_symbol or ""
    common_symbols = ["$", "€", "£", "¥"]
    for symbol in common_symbols:
        if symbol in price_text:
            currency = symbol
            break
    
    # If no symbol found, try to extract currency code (USD, EUR, etc.)
    if not currency:
        currency_codes = ["USD", "EUR", "GBP", "JPY"]
        for code in currency_codes:
            if code in price_text:
                currency = code
                break
    
    # Convert to float
    value = to_float(price_text, default)
    
    return {"value": value, "currency": currency}


def normalize_text(text: Optional[str]) -> str:
    """
    Normalize text by removing extra whitespace, newlines, and tabs.
    
    Args:
        text: Input text to normalize
        
    Returns:
        Normalized text
    """
    if text is None:
        return ""
    
    # Replace newlines and tabs with spaces
    normalized = text.replace("\n", " ").replace("\t", " ").replace("\r", " ")
    
    # Remove extra spaces
    normalized = strip_whitespace(normalized)
    
    return normalized


def normalize_list(
    items: Union[List[str], str, None], 
    delimiter: str = ","
) -> List[str]:
    """
    Normalize a list of items or a string with delimiters into a clean list.
    
    Args:
        items: List of strings or a string with delimiters
        delimiter: Delimiter to split string items
        
    Returns:
        Normalized list of strings
    """
    if items is None:
        return []
    
    if isinstance(items, str):
        items = [item.strip() for item in items.split(delimiter) if item.strip()]
    
    # Clean each item and remove empty ones
    return [normalize_text(item) for item in items if item and normalize_text(item)]


def validate_sku_format(sku: Optional[str]) -> bool:
    """
    Validate if a SKU follows a common format.
    
    Args:
        sku: SKU string to validate
        
    Returns:
        True if SKU format is valid, False otherwise
    """
    if not sku:
        return False
    
    # Remove whitespace
    sku = strip_whitespace(sku)
    
    # Basic validation - SKUs are typically alphanumeric
    # and at least 3 characters long
    if len(sku) < 3:
        return False
    
    # Check if SKU contains only alphanumeric chars, dashes, and underscores
    return bool(re.match(r'^[A-Za-z0-9\-_]+$', sku))


def validate_required_field(value: Any) -> bool:
    """
    Validate if a required field has a value.
    
    Args:
        value: Value to check
        
    Returns:
        True if value exists, False otherwise
    """
    if value is None:
        return False
    
    if isinstance(value, str) and not value.strip():
        return False
    
    return True


def clean_and_validate_product_data(
    data: Dict[str, Any],
    required_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Clean and validate product data dictionary.
    
    Args:
        data: Dictionary of product data
        required_fields: List of field names that are required
        
    Returns:
        Cleaned and validated data dictionary with additional validation info
    """
    required_fields = required_fields or ["name", "sku"]
    result = {
        "data": {},
        "validation": {
            "is_valid": True,
            "missing_required_fields": []
        }
    }
    
    # Clean and process each field
    for field, value in data.items():
        cleaned_value = value
        
        # Apply appropriate cleaning based on field name
        if field in ["name", "description", "supplier_name"]:
            cleaned_value = normalize_text(value)
        elif field in ["price", "cost"]:
            if isinstance(value, (int, float)):
                cleaned_value = float(value)
            else:
                cleaned_value = to_float(value)
        elif field == "sku":
            cleaned_value = strip_whitespace(value)
        elif field == "colorways":
            cleaned_value = normalize_list(value)
        
        result["data"][field] = cleaned_value
    
    # Validate required fields
    for field in required_fields:
        if field not in result["data"] or not validate_required_field(result["data"][field]):
            result["validation"]["is_valid"] = False
            result["validation"]["missing_required_fields"].append(field)
    
    return result
