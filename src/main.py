"""
Main orchestrator module for the Automated Product Data Scraper.

This module serves as the entry point for the application, initializing logging,
loading configuration, and coordinating the scraping process.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Fix the import to work when running from src directory
try:
    from src.config import config
    from src.scrapers.factory import get_scraper
    from src.storage.csv_writer import CSVWriter
    from src.utils.logging_config import setup_logging, get_logger
except ModuleNotFoundError:
    # When running directly from src directory
    from config import config
    from scrapers.factory import get_scraper
    from storage.csv_writer import CSVWriter
    from utils.logging_config import setup_logging, get_logger


def resolve_path(path: Path) -> Path:
    """
    Resolve a path to be absolute, handling both absolute and relative paths.
    
    Args:
        path: The path to resolve
        
    Returns:
        Path: The resolved absolute path
    """
    if not path.is_absolute():
        # If path is relative, make it relative to the project root, not the src directory
        project_root = Path(__file__).parent.parent
        return project_root / path
    return path


def main() -> None:
    """
    Main function that orchestrates the scraping process.
    """
    logger = get_logger(__name__)
    
    logger.info("Starting Automated Product Data Scraper")
    
    # Resolve output directory path
    output_dir = resolve_path(Path(config.output.output_dir))
    
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Download images: {config.output.download_images}")
    
    if not config.suppliers:
        logger.warning("No suppliers configured. Please add supplier configurations.")
        return
    
    logger.info(f"Found {len(config.suppliers)} supplier(s) to process")
    
    # Define the CSV headers for product data
    csv_headers = [
        "product_name", 
        "sku", 
        "description", 
        "supplier_name", 
        "cost", 
        "price", 
        "colorways", 
        "image_url"
    ]
    
    # Process each supplier using the ScraperFactory
    for supplier in config.suppliers:
        logger.info(f"Processing supplier: {supplier.name}")
        try:
            # Get the appropriate scraper for this supplier
            scraper = get_scraper(supplier)
            logger.info(f"Using scraper: {scraper}")
            
            # If login is required, attempt to login
            if supplier.requires_login and supplier.username and supplier.password:
                logger.info(f"Attempting login for supplier: {supplier.name}")
                login_success = scraper.login(supplier.username, supplier.password)
                if not login_success:
                    logger.error(f"Login failed for supplier: {supplier.name}")
                    continue
                logger.info(f"Login successful for supplier: {supplier.name}")
            
            # Initialize the CSV writer for this supplier
            csv_writer = CSVWriter(
                output_path=str(output_dir),
                filename_pattern=config.output.csv_filename_pattern,
                supplier_name=supplier.name,
                include_timestamp=config.output.include_timestamp,
                encoding=config.output.csv_encoding
            )
            
            # Open the CSV file and write the header
            with csv_writer:
                csv_writer.write_header(csv_headers)
                
                # Get product URLs (this will be implemented in future stories)
                # For now, we'll use a placeholder
                logger.info(f"Getting product URLs for supplier: {supplier.name}")
                product_urls = []  # This would be populated by scraper.get_product_urls()
                
                # For demonstration purposes, add a placeholder product URL
                product_urls.append("https://example.com/product1")
                
                logger.info(f"Found {len(product_urls)} product URLs")
                
                # Process each product URL
                for url in product_urls:
                    try:
                        logger.info(f"Processing product URL: {url}")
                        
                        # Extract product data (this will be implemented in future stories)
                        # For now, we'll use placeholder data
                        product_data = {
                            "product_name": f"Product from {supplier.name}",
                            "sku": "SKU123",
                            "description": "This is a placeholder product description",
                            "supplier_name": supplier.name,
                            "cost": "99.99",
                            "price": "149.99",
                            "colorways": "Red, Blue, Green",
                            "image_url": "https://example.com/image.jpg"
                        }
                        
                        # Write the product data to the CSV file
                        csv_writer.write_row(product_data)
                        logger.info(f"Wrote product data for: {product_data['product_name']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing product URL {url}: {e}", exc_info=True)
                
                logger.info(f"Completed processing supplier: {supplier.name}")
            
        except ImportError as e:
            logger.error(f"Failed to load scraper for supplier {supplier.name}: {e}")
        except Exception as e:
            logger.error(f"Error processing supplier {supplier.name}: {e}", exc_info=True)
    
    logger.info("Scraping process completed")


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    try:
        # Run the main function
        main()
    except Exception as e:
        get_logger(__name__).error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
