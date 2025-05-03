"""
Example script demonstrating how to use the Transformer module.

This script shows how to use the Transformer module to sanitize, normalize,
and validate product data extracted from HTML content.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import the transformer functions
try:
    from src.parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, sanitize_html_content, normalize_url,
        clean_and_validate_product_data, ProductData
    )
except ImportError:
    from parser.transformer import (
        strip_whitespace, to_float, normalize_text, normalize_list,
        normalize_currency, sanitize_html_content, normalize_url,
        clean_and_validate_product_data, ProductData
    )


def main():
    """
    Main function demonstrating the use of the Transformer module.
    """
    print("Transformer Module Example\n")
    
    # Example 1: Basic text sanitization
    print("Example 1: Basic Text Sanitization")
    raw_text = "  This is a   product   description with extra   spaces.  "
    cleaned_text = strip_whitespace(raw_text)
    print(f"Raw text: '{raw_text}'")
    print(f"Cleaned text: '{cleaned_text}'")
    print()
    
    # Example 2: Price normalization
    print("Example 2: Price Normalization")
    price_examples = [
        "$123.45",
        "€99,99",
        "1,234.56",
        "1.234,56",
        "¥5000"
    ]
    print("Converting various price formats to float:")
    for price in price_examples:
        normalized_price = to_float(price)
        print(f"  {price} -> {normalized_price}")
    print()
    
    # Example 3: Currency extraction
    print("Example 3: Currency Extraction")
    for price in price_examples:
        result = normalize_currency(price)
        print(f"  {price} -> Value: {result['value']}, Currency: '{result['currency']}'")
    print()
    
    # Example 4: HTML content sanitization
    print("Example 4: HTML Content Sanitization")
    html_content = "<p>This is a <strong>product description</strong> with <em>HTML tags</em> and &amp; entities.</p>"
    cleaned_content = sanitize_html_content(html_content)
    print(f"HTML content: '{html_content}'")
    print(f"Cleaned content: '{cleaned_content}'")
    print()
    
    # Example 5: URL normalization
    print("Example 5: URL Normalization")
    base_url = "https://example.com/products/"
    relative_urls = [
        "image.jpg",
        "/images/product.png",
        "../images/thumbnail.jpg",
        "https://cdn.example.com/images/large.jpg"
    ]
    print(f"Base URL: {base_url}")
    print("Converting relative URLs to absolute URLs:")
    for url in relative_urls:
        absolute_url = normalize_url(url, base_url)
        print(f"  {url} -> {absolute_url}")
    print()
    
    # Example 6: List normalization
    print("Example 6: List Normalization")
    colors_string = "Red, Green,  Blue, Yellow "
    colors_list = normalize_list(colors_string)
    print(f"Colors string: '{colors_string}'")
    print(f"Normalized list: {colors_list}")
    print()
    
    # Example 7: Complete product data cleaning and validation
    print("Example 7: Complete Product Data Cleaning and Validation")
    raw_product_data = {
        "product_name": "  Example Product  ",
        "sku": "  EX12345  ",
        "description": "<p>This is an <strong>example</strong> product.</p>",
        "supplier_name": "Example Supplier\n",
        "cost": "$45.00",
        "price": "€89,99",
        "colorways": ["  Black  ", "White", "  Silver  "],
        "image_url": "/image.jpg"
    }
    
    print("Raw product data:")
    for key, value in raw_product_data.items():
        print(f"  {key}: {value}")
    
    cleaned_data = clean_and_validate_product_data(
        raw_product_data,
        required_fields=["product_name", "sku"],
        base_url="https://example.com"
    )
    
    print("\nCleaned and validated product data:")
    for key, value in cleaned_data.items():
        if key != "validation":
            print(f"  {key}: {value}")
    
    print(f"\nValidation result:")
    print(f"  Valid: {cleaned_data['validation']['is_valid']}")
    print(f"  Missing required fields: {cleaned_data['validation']['missing_required_fields']}")
    print()
    
    # Example 8: Using the Pydantic model directly
    print("Example 8: Using the Pydantic Model Directly")
    
    # Pre-process the data before passing to Pydantic
    processed_data = {
        "product_name": normalize_text(raw_product_data["product_name"]),
        "sku": strip_whitespace(raw_product_data["sku"]),
        "description": sanitize_html_content(raw_product_data["description"]),
        "supplier_name": normalize_text(raw_product_data["supplier_name"]),
        "cost": to_float(raw_product_data["cost"]),
        "price": to_float(raw_product_data["price"]),
        "colorways": normalize_list(raw_product_data["colorways"]),
        "image_url": normalize_url(raw_product_data["image_url"], "https://example.com")
    }
    
    product = ProductData(**processed_data)
    print("Product data model fields:")
    print(f"  product_name: {product.product_name}")
    print(f"  sku: {product.sku}")
    print(f"  description: {product.description}")
    print(f"  supplier_name: {product.supplier_name}")
    print(f"  cost: {product.cost}")
    print(f"  price: {product.price}")
    print(f"  colorways: {product.colorways}")
    print(f"  image_url: {product.image_url}")


if __name__ == "__main__":
    main()
