#!/usr/bin/env python3
"""
Custom runner script for the Automated Product Data Scraper.

This script loads a custom configuration file and runs the scraper.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any

from src.scrapers.factory import get_scraper
from src.storage.csv_writer import CSVWriter
from src.utils.logging_config import setup_logging, get_logger
from src.config import SupplierConfig


def load_custom_config(config_file: str) -> Dict[str, Any]:
    """
    Load a custom configuration file.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        Dict[str, Any]: The loaded configuration
    """
    with open(config_file, 'r') as f:
        return json.load(f)


def run_with_custom_config(config_file: str) -> None:
    """
    Run the scraper with a custom configuration file.
    
    Args:
        config_file: Path to the configuration file
    """
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info(f"Loading custom configuration from {config_file}")
    
    # Load the custom configuration
    config = load_custom_config(config_file)
    
    # Process each supplier in the configuration
    for supplier_config in config["suppliers"]:
        supplier_name = supplier_config["name"]
        supplier_url = supplier_config["url"]
        requires_login = supplier_config.get("requires_login", False)
        scraper_type = supplier_config.get("scraper_type", "static")
        selectors = supplier_config.get("selectors", {})
        
        logger.info(f"Processing supplier: {supplier_name}")
        
        # Create a SupplierConfig object
        supplier_config_obj = SupplierConfig(
            name=supplier_name,
            url=supplier_url,
            requires_login=requires_login,
            scraper_type=scraper_type,
            selectors=selectors
        )
        
        # Create the scraper
        scraper = get_scraper(supplier_config_obj)
        
        logger.info(f"Using scraper: {scraper}")
        
        # Create the CSV writer
        output_dir = config["output"]["output_dir"]
        filename_pattern = config["output"]["filename_pattern"]
        include_timestamp = config["output"].get("include_timestamp", True)
        csv_encoding = config["output"].get("csv_encoding", "utf-8")
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Define CSV headers
        csv_headers = [
            "product_name", "sku", "description", "supplier_name",
            "price", "cost", "colorways", "image_url"
        ]
        
        with CSVWriter(
            output_path=output_dir,
            filename_pattern=filename_pattern,
            supplier_name=supplier_name,
            include_timestamp=include_timestamp,
            encoding=csv_encoding
        ) as csv_writer:
            # Write the header row
            csv_writer.write_header(csv_headers)
            
            # Get product URLs
            logger.info(f"Getting product URLs for supplier: {supplier_name}")
            product_urls = scraper.get_product_urls()
            
            logger.info(f"Found {len(product_urls)} product URLs")
            
            # Process each product URL
            for url in product_urls:
                try:
                    logger.info(f"Processing product URL: {url}")
                    
                    # Extract product data
                    product_data = scraper.extract_data(url)
                    
                    # Write the product data to the CSV file
                    csv_writer.write_row(product_data)
                    logger.info(f"Wrote product data for: {product_data.get('product_name', 'Unknown product')}")
                    
                except Exception as e:
                    logger.error(f"Error processing product URL {url}: {e}", exc_info=True)
            
            logger.info(f"Completed processing supplier: {supplier_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the scraper with a custom configuration file")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    args = parser.parse_args()
    
    run_with_custom_config(args.config)
