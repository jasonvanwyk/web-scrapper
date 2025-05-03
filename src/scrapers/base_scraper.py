"""
Abstract base class for scrapers.

This module defines the BaseScraper abstract base class that all concrete scraper
implementations must inherit from. It establishes a standard interface for all scrapers,
ensuring consistency across different supplier implementations.
"""

import abc
import logging
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin


class BaseScraper(abc.ABC):
    """
    Abstract base class for all scrapers.
    
    This class defines the interface that all concrete scraper implementations
    must adhere to. It includes abstract methods for login, pagination, and data extraction.
    
    Attributes:
        logger: A logger instance for the scraper.
        base_url: The base URL of the supplier website.
        name: The name of the supplier.
    """
    
    def __init__(self, name: str, base_url: str, **kwargs):
        """
        Initialize the base scraper.
        
        Args:
            name: The name of the supplier.
            base_url: The base URL of the supplier website.
            **kwargs: Additional keyword arguments for specific scraper implementations.
        """
        self.name = name
        self.base_url = base_url
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initializing {self.__class__.__name__} for supplier: {name}")
    
    @abc.abstractmethod
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the supplier website if required.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
            
        Returns:
            bool: True if login was successful, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def Maps_to_products(self, category_map: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Map category identifiers to product URLs.
        
        Args:
            category_map: A dictionary mapping category names to category URLs or identifiers.
            
        Returns:
            Dict[str, List[str]]: A dictionary mapping category names to lists of product URLs.
        """
        pass
    
    @abc.abstractmethod
    def get_product_urls(self, category_url: Optional[str] = None) -> List[str]:
        """
        Get URLs for individual product pages.
        
        Args:
            category_url: Optional URL for a specific category page.
                          If None, use the base URL or a default category page.
                          
        Returns:
            List[str]: A list of product page URLs.
        """
        pass
    
    @abc.abstractmethod
    def handle_pagination(self, url: str, page: int = 1) -> str:
        """
        Handle pagination for multi-page results.
        
        Args:
            url: The base URL for the page.
            page: The page number to navigate to.
            
        Returns:
            str: The URL for the specified page.
        """
        pass
    
    @abc.abstractmethod
    def extract_data(self, product_url: str) -> Dict[str, Any]:
        """
        Extract product data from a product page.
        
        Args:
            product_url: The URL of the product page.
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted product data.
                Expected keys include:
                - product_name: The name of the product.
                - sku: The SKU of the product.
                - description: The description of the product.
                - supplier_name: The name of the supplier.
                - cost: The cost of the product.
                - price: The price of the product.
                - colorways: A list of available colors.
                - image_url: The URL of the product image.
        """
        pass
    
    def build_absolute_url(self, relative_url: str) -> str:
        """
        Build an absolute URL from a relative URL.
        
        Args:
            relative_url: The relative URL to convert to an absolute URL.
            
        Returns:
            str: The absolute URL.
        """
        return urljoin(self.base_url, relative_url)
    
    def __str__(self) -> str:
        """Return a string representation of the scraper."""
        return f"{self.__class__.__name__}(name={self.name}, base_url={self.base_url})"
