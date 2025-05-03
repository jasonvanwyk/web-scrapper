#!/usr/bin/env python3
"""
Example script demonstrating the usage of the CSVWriter module.

This script shows how to use the CSVWriter class to write product data to a CSV file
with proper UTF-8 encoding and streaming support.
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.storage.csv_writer import CSVWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Demonstrate the usage of CSVWriter with sample product data."""
    # Define the output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    
    # Sample product data
    headers = ["product_name", "sku", "description", "supplier_name", "cost", "price", "colorways", "image_url"]
    
    products = [
        {
            "product_name": "Premium Laptop",
            "sku": "LT-2023-001",
            "description": "High-performance laptop with 16GB RAM and 512GB SSD",
            "supplier_name": "TechSupplier",
            "cost": "800.00",
            "price": "1299.99",
            "colorways": "Silver, Space Gray, Gold",
            "image_url": "https://example.com/images/laptop.jpg"
        },
        {
            "product_name": "Ergonomic Office Chair",
            "sku": "OC-2023-002",
            "description": "Adjustable office chair with lumbar support",
            "supplier_name": "FurnitureSupplier",
            "cost": "150.00",
            "price": "299.99",
            "colorways": "Black, Gray, Blue",
            "image_url": "https://example.com/images/chair.jpg"
        },
        {
            "product_name": "Wireless Headphones",
            "sku": "WH-2023-003",
            "description": "Noise-cancelling wireless headphones with 30-hour battery life",
            "supplier_name": "AudioSupplier",
            "cost": "120.00",
            "price": "249.99",
            "colorways": "Black, White, Red",
            "image_url": "https://example.com/images/headphones.jpg"
        },
        {
            "product_name": "Smart Watch",
            "sku": "SW-2023-004",
            "description": "Fitness tracker with heart rate monitoring and GPS",
            "supplier_name": "WearableSupplier",
            "cost": "90.00",
            "price": "199.99",
            "colorways": "Black, Silver, Rose Gold",
            "image_url": "https://example.com/images/smartwatch.jpg"
        },
        {
            "product_name": "Café Français Coffee Maker",
            "sku": "CF-2023-005",
            "description": "Premium French press coffee maker with double-wall insulation",
            "supplier_name": "KitchenSupplier",
            "cost": "35.00",
            "price": "€79.99",
            "colorways": "Stainless Steel, Matte Black, Copper",
            "image_url": "https://example.com/images/coffeemaker.jpg"
        }
    ]
    
    # Method 1: Using context manager (recommended)
    logger.info("Writing products using context manager...")
    with CSVWriter(
        output_path=output_dir,
        supplier_name="example_supplier",
        include_timestamp=True
    ) as writer:
        writer.write_header(headers)
        
        # Write products one by one (streaming approach)
        for product in products:
            writer.write_row(product)
            logger.info(f"Wrote product: {product['product_name']}")
    
    # Method 2: Manual open/close
    logger.info("\nWriting products using manual open/close...")
    writer = CSVWriter(
        output_path=output_dir,
        filename_pattern="bulk_write_{supplier}_{timestamp}.csv",
        supplier_name="example_supplier"
    )
    
    try:
        writer.open()
        writer.write_header(headers)
        
        # Write all products at once (bulk approach)
        writer.write_rows(products)
        logger.info(f"Wrote {len(products)} products in bulk")
    finally:
        writer.close()
    
    logger.info("\nCSV files have been written to the output directory")
    logger.info(f"Output directory: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
