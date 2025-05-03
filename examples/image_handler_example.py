#!/usr/bin/env python3
"""
Example script demonstrating the usage of the ImageHandler module.

This script shows how to use the ImageHandler class to handle product images
either by saving URLs or downloading the actual image files.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.image_handler import ImageHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Demonstrate the usage of ImageHandler with sample product data."""
    # Define the output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'images')
    
    # Sample product data
    products = [
        {
            "product_name": "Premium Laptop",
            "sku": "LT-2023-001",
            "description": "High-performance laptop with 16GB RAM and 512GB SSD",
            "supplier_name": "TechSupplier",
            "cost": "800.00",
            "price": "1299.99",
            "colorways": "Silver, Space Gray, Gold",
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853"
        },
        {
            "product_name": "Ergonomic Office Chair",
            "sku": "OC-2023-002",
            "description": "Adjustable office chair with lumbar support",
            "supplier_name": "FurnitureSupplier",
            "cost": "150.00",
            "price": "299.99",
            "colorways": "Black, Gray, Blue",
            "image_url": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8"
        },
        {
            "product_name": "Wireless Headphones",
            "sku": "WH-2023-003",
            "description": "Noise-cancelling wireless headphones with 30-hour battery life",
            "supplier_name": "AudioSupplier",
            "cost": "120.00",
            "price": "249.99",
            "colorways": "Black, White, Red",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
        }
    ]
    
    # Example 1: URL-only mode (no downloading)
    logger.info("Example 1: URL-only mode (no downloading)")
    with ImageHandler(
        output_path=output_dir,
        download_images=False,
        supplier_name="example_supplier"
    ) as handler:
        for product in products:
            result = handler.handle_image(product["image_url"], product)
            logger.info(f"Product: {product['product_name']}, Image URL: {result}")
    
    # Example 2: Download mode with default settings
    logger.info("\nExample 2: Download mode with default settings")
    with ImageHandler(
        output_path=output_dir,
        download_images=True,
        supplier_name="example_supplier",
        include_timestamp=True
    ) as handler:
        for product in products:
            try:
                result = handler.handle_image(product["image_url"], product)
                logger.info(f"Product: {product['product_name']}, Image saved to: {result}")
            except Exception as e:
                logger.error(f"Error handling image for {product['product_name']}: {str(e)}")
    
    # Example 3: Download mode with custom filename pattern
    logger.info("\nExample 3: Download mode with custom filename pattern")
    with ImageHandler(
        output_path=output_dir,
        download_images=True,
        filename_pattern="{supplier}_{sku}.{ext}",
        supplier_name="custom_supplier"
    ) as handler:
        for product in products:
            try:
                result = handler.handle_image(product["image_url"], product)
                logger.info(f"Product: {product['product_name']}, Image saved to: {result}")
            except Exception as e:
                logger.error(f"Error handling image for {product['product_name']}: {str(e)}")
    
    # Example 4: Manual open/close usage
    logger.info("\nExample 4: Manual open/close usage")
    handler = ImageHandler(
        output_path=output_dir,
        download_images=True,
        supplier_name="manual_example"
    )
    
    try:
        handler.open()
        for product in products:
            result = handler.handle_image(product["image_url"], product)
            logger.info(f"Product: {product['product_name']}, Result: {result}")
    finally:
        handler.close()
    
    # Example 5: Error handling with invalid URLs
    logger.info("\nExample 5: Error handling with invalid URLs")
    with ImageHandler(
        output_path=output_dir,
        download_images=True
    ) as handler:
        # Valid URL
        result = handler.handle_image("https://images.unsplash.com/photo-1496181133206-80ce9b88a853", products[0])
        logger.info(f"Valid URL result: {result}")
        
        # Invalid URL
        result = handler.handle_image("https://example.com/nonexistent.jpg", products[0])
        logger.info(f"Invalid URL result: {result}")
        
        # Empty URL
        result = handler.handle_image("", products[0])
        logger.info(f"Empty URL result: {result}")
    
    logger.info("\nImage handling examples completed")
    logger.info(f"Output directory: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
