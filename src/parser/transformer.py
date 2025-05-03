"""
Data Transformer module for the Automated Product Data Scraper.

This module provides functions for cleaning, normalizing, and validating
data extracted from HTML content.
"""

import logging
import re
import html
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin
try:
    from pydantic import BaseModel, Field, field_validator
except ImportError:
    # For Pydantic v1 compatibility
    from pydantic import BaseModel, Field, validator as field_validator

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
                # Remove the currency code for conversion
                price_text = price_text.replace(code, "")
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


def sanitize_html_content(text: Optional[str]) -> str:
    """
    Remove HTML tags and decode HTML entities from text.
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Cleaned text with HTML tags removed and entities decoded
    """
    if text is None:
        return ""
    
    # Remove HTML tags using regex
    clean_text = re.sub(r'<[^>]*>', '', text)
    
    # Decode HTML entities
    clean_text = html.unescape(clean_text)
    
    # Normalize whitespace
    return normalize_text(clean_text)


def normalize_url(url: Optional[str], base_url: Optional[str] = None) -> str:
    """
    Normalize URL by converting relative URLs to absolute URLs.
    
    Args:
        url: URL to normalize
        base_url: Base URL to use for relative URLs
        
    Returns:
        Normalized URL
    """
    if not url:
        return ""
    
    # Strip whitespace
    url = strip_whitespace(url)
    
    # If base_url is provided and url is relative, convert to absolute
    if base_url and not (url.startswith('http://') or url.startswith('https://')):
        return urljoin(base_url, url)
    
    return url


def validate_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL format is valid, False otherwise
    """
    if url is None:
        raise TypeError("URL cannot be None")
        
    if not url:
        return False
    
    # Basic URL validation using regex
    url_pattern = re.compile(
        r'^(https?://)'  # http:// or https://
        r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?'  # domain
        r'(/[a-zA-Z0-9_\-\.~!*\'();:@&=+$,/%#\[\]?]*)?$'  # path, query, fragment
    )
    return bool(url_pattern.match(url))


# Pydantic model for product data validation
class ProductData(BaseModel):
    """Pydantic model for product data validation."""
    product_name: str = Field(default="")
    sku: str = Field(default="")
    description: str = Field(default="")
    supplier_name: str = Field(default="")
    cost: float = Field(default=0.0)
    price: float = Field(default=0.0)
    colorways: List[str] = Field(default_factory=list)
    image_url: str = Field(default="")
    
    @field_validator('sku')
    def validate_sku(cls, v):
        """Validate SKU format."""
        if not validate_sku_format(v):
            logger.warning(f"Invalid SKU format: {v}")
        return v
    
    @field_validator('cost', 'price')
    def validate_price(cls, v):
        """Validate price is non-negative."""
        if v < 0:
            logger.warning(f"Negative price/cost value: {v}")
            return 0.0
        return v
    
    @field_validator('image_url')
    def validate_image_url(cls, v):
        """Validate image URL format."""
        if v and not validate_url(v):
            logger.warning(f"Invalid image URL format: {v}")
        return v


def clean_and_validate_product_data(
    data: Dict[str, Any],
    required_fields: Optional[List[str]] = None,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clean and validate product data dictionary.
    
    Args:
        data: Dictionary of product data
        required_fields: List of field names that are required
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Cleaned and validated data dictionary with additional validation info
    """
    required_fields = required_fields or ["product_name", "sku"]
    
    # Check if there's an error field, if so, bypass validation
    if "error" in data:
        return {
            "product_name": data.get("product_name", ""),
            "sku": data.get("sku", ""),
            "description": data.get("description", ""),
            "supplier_name": data.get("supplier_name", ""),
            "cost": data.get("cost", 0.0),
            "price": data.get("price", 0.0),
            "colorways": data.get("colorways", []),
            "image_url": data.get("image_url", ""),
            "error": data["error"]
        }
    
    # Clean and normalize data
    cleaned_data = {}
    
    # Product name
    cleaned_data["product_name"] = normalize_text(data.get("product_name", ""))
    
    # SKU
    cleaned_data["sku"] = strip_whitespace(data.get("sku", ""))
    
    # Description - remove HTML tags if present
    cleaned_data["description"] = sanitize_html_content(data.get("description", ""))
    
    # Supplier name
    cleaned_data["supplier_name"] = normalize_text(data.get("supplier_name", ""))
    
    # Cost and price
    cleaned_data["cost"] = to_float(data.get("cost", 0.0)) if isinstance(data.get("cost"), str) else float(data.get("cost", 0.0))
    cleaned_data["price"] = to_float(data.get("price", 0.0)) if isinstance(data.get("price"), str) else float(data.get("price", 0.0))
    
    # Colorways
    cleaned_data["colorways"] = normalize_list(data.get("colorways", []))
    
    # Image URL - normalize relative URLs
    cleaned_data["image_url"] = normalize_url(data.get("image_url", ""), base_url)
    
    # Validate using Pydantic model
    try:
        validated_data = ProductData(**cleaned_data).model_dump()
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        validated_data = cleaned_data
    
    # Check required fields
    validation = {
        "is_valid": True,
        "missing_required_fields": []
    }
    
    for field in required_fields:
        if field not in validated_data or not validate_required_field(validated_data[field]):
            validation["is_valid"] = False
            validation["missing_required_fields"].append(field)
    
    return {**validated_data, "validation": validation}
