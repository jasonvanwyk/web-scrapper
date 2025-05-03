"""
Static scraper module.

This module provides a concrete implementation of the BaseScraper for static HTML websites.
It will be fully implemented in Story 3, but is included here as a placeholder to support testing.
"""

from typing import Dict, List, Optional, Any

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.base_scraper import BaseScraper
except ModuleNotFoundError:
    from scrapers.base_scraper import BaseScraper


class StaticScraper(BaseScraper):
    """
    Concrete implementation of BaseScraper for static HTML websites.
    
    This is a placeholder implementation that will be fully implemented in Story 3.
    """
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the supplier website if required.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
            
        Returns:
            bool: True if login was successful, False otherwise.
        """
        self.logger.info(f"Login called for {self.name} (placeholder implementation)")
        return True
    
    def get_product_urls(self, category_url: Optional[str] = None) -> List[str]:
        """
        Get URLs for individual product pages.
        
        Args:
            category_url: Optional URL for a specific category page.
                          If None, use the base URL or a default category page.
                          
        Returns:
            List[str]: A list of product page URLs.
        """
        self.logger.info(f"Getting product URLs for {self.name} (placeholder implementation)")
        return []
    
    def handle_pagination(self, url: str, page: int = 1) -> str:
        """
        Handle pagination for multi-page results.
        
        Args:
            url: The base URL for the page.
            page: The page number to navigate to.
            
        Returns:
            str: The URL for the specified page.
        """
        self.logger.info(f"Handling pagination for {self.name} (placeholder implementation)")
        return url
    
    def extract_data(self, product_url: str) -> Dict[str, Any]:
        """
        Extract product data from a product page.
        
        Args:
            product_url: The URL of the product page.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted product data.
        """
        self.logger.info(f"Extracting data for {self.name} (placeholder implementation)")
        return {
            "product_name": "Placeholder Product",
            "sku": "PLACEHOLDER-SKU",
            "description": "Placeholder description",
            "supplier_name": self.name,
            "cost": 0.0,
            "price": 0.0,
            "colorways": [],
            "image_url": "",
        }
