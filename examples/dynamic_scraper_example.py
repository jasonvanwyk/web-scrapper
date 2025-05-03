"""
Example script demonstrating the use of the DynamicScraper.

This script shows how to configure and use the DynamicScraper to scrape
a dynamic website that requires JavaScript execution.
"""

import logging
import sys
import os
from pathlib import Path

# Add the project root to the Python path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.config import SupplierConfig
    from src.scrapers.factory import get_scraper
except ModuleNotFoundError:
    from config import SupplierConfig
    from scrapers.factory import get_scraper


def main():
    """Run the dynamic scraper example."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create a supplier configuration for a dynamic website
    supplier_config = SupplierConfig(
        name="Example Dynamic Supplier",
        url="https://example.com",
        scraper_type="dynamic",  # This tells the factory to use DynamicScraper
        requires_login=False,
        selectors={
            # CSS selectors for data extraction
            "product_name": "h1.product-title",
            "sku": ".product-sku",
            "description": ".product-description",
            "price": ".product-price",
            "cost": ".product-cost",
            "colorways": ".product-colors .color",
            "image_url": ".product-image img",
            
            # Selectors for navigation
            "product_links": ".products .product a",
            "next_page": ".pagination .next",
            
            # Pagination format (query_param or path)
            "pagination_format": "query_param",
            "page_param": "page",
            
            # Maximum number of pages to scrape
            "max_pages": "3"
        }
    )
    
    # Get a scraper instance for the supplier
    scraper = get_scraper(supplier_config)
    
    try:
        # Example: Get product URLs
        product_urls = scraper.get_product_urls("https://example.com/products")
        
        logging.info(f"Found {len(product_urls)} product URLs")
        
        # Example: Extract data from the first product URL
        if product_urls:
            product_data = scraper.extract_data(product_urls[0])
            logging.info(f"Extracted product data: {product_data}")
        
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
    
    finally:
        # Make sure to close the browser
        if hasattr(scraper, 'close'):
            scraper.close()


if __name__ == "__main__":
    main()
