"""
Example script demonstrating how to use the Parser class.

This script shows how to use the Parser class to extract structured data
from HTML content using CSS selectors or XPath expressions.
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

# Import the Parser class
try:
    from src.parser.parser import Parser
except ImportError:
    from parser.parser import Parser


def main():
    """
    Main function demonstrating the use of the Parser class.
    """
    # Sample HTML content
    sample_html = """
    <html>
        <head><title>Example Product</title></head>
        <body>
            <h1 class="product-title">Example Product</h1>
            <span class="product-sku">EX12345</span>
            <div class="product-description">This is an example product description.</div>
            <span class="supplier">Example Supplier</span>
            <span class="cost">$45.00</span>
            <span class="price">$89.99</span>
            <ul class="colors">
                <li>Black</li>
                <li>White</li>
                <li>Silver</li>
            </ul>
            <img class="product-image" src="/images/example.jpg" alt="Example Product">
        </body>
    </html>
    """
    
    # Define CSS selectors for the product data
    selectors = {
        "product_name": "h1.product-title",
        "sku": "span.product-sku",
        "description": "div.product-description",
        "supplier_name": "span.supplier",
        "cost": "span.cost",
        "price": "span.price",
        "colorways": "ul.colors li",
        "image_url": "img.product-image"
    }
    
    # Create a Parser instance
    parser = Parser(
        base_url="https://example.com",
        selectors=selectors
    )
    
    # Parse the HTML content
    print("Parsing HTML content with CSS selectors...")
    product_data = parser.parse(sample_html)
    
    # Print the extracted data
    print("\nExtracted Product Data:")
    print(f"Product Name: {product_data['product_name']}")
    print(f"SKU: {product_data['sku']}")
    print(f"Description: {product_data['description']}")
    print(f"Supplier: {product_data['supplier_name']}")
    print(f"Cost: ${product_data['cost']}")
    print(f"Price: ${product_data['price']}")
    print(f"Colorways: {', '.join(product_data['colorways'])}")
    print(f"Image URL: {product_data['image_url']}")
    
    # Example with XPath selectors
    print("\n\nParsing HTML content with XPath selectors...")
    xpath_selectors = {
        "product_name": "//h1[@class='product-title']",
        "sku": "//span[@class='product-sku']",
        "description": "//div[@class='product-description']",
        "supplier_name": "//span[@class='supplier']",
        "cost": "//span[@class='cost']",
        "price": "//span[@class='price']",
        "colorways": "//ul[@class='colors']/li",
        "image_url": "//img[@class='product-image']"
    }
    
    # Create a Parser instance with XPath selectors
    xpath_parser = Parser(
        base_url="https://example.com",
        xpath_selectors=xpath_selectors
    )
    
    # Parse the HTML content
    product_data = xpath_parser.parse(sample_html)
    
    # Print the extracted data
    print("\nExtracted Product Data (using XPath):")
    print(f"Product Name: {product_data['product_name']}")
    print(f"SKU: {product_data['sku']}")
    print(f"Description: {product_data['description']}")
    print(f"Supplier: {product_data['supplier_name']}")
    print(f"Cost: ${product_data['cost']}")
    print(f"Price: ${product_data['price']}")
    print(f"Colorways: {', '.join(product_data['colorways'])}")
    print(f"Image URL: {product_data['image_url']}")


if __name__ == "__main__":
    main()
