"""
Scraper factory module.

This module provides a factory for creating scraper instances based on
supplier configuration. It dynamically loads the appropriate scraper module
and instantiates the correct scraper class.
"""

import importlib
import logging
from typing import Any, Dict, Optional, Type

# Try both import paths to handle different execution contexts
try:
    from src.scrapers.base_scraper import BaseScraper
    from src.config import SupplierConfig
except ModuleNotFoundError:
    from scrapers.base_scraper import BaseScraper
    from config import SupplierConfig


class ScraperFactory:
    """
    Factory for creating scraper instances.
    
    This class is responsible for dynamically loading and instantiating
    the appropriate scraper for a given supplier configuration.
    """
    
    def __init__(self):
        """Initialize the scraper factory."""
        self.logger = logging.getLogger(__name__)
    
    def get_scraper(self, supplier_config: SupplierConfig) -> BaseScraper:
        """
        Get a scraper instance for the given supplier configuration.
        
        Args:
            supplier_config: The configuration for the supplier.
            
        Returns:
            BaseScraper: An instance of the appropriate scraper for the supplier.
            
        Raises:
            ImportError: If the scraper module cannot be imported.
            ValueError: If the scraper class cannot be found in the module.
            Exception: For any other errors during scraper instantiation.
        """
        try:
            # Determine the module name based on supplier configuration
            module_name = self._get_module_name(supplier_config)
            
            # Import the module
            self.logger.debug(f"Importing scraper module: {module_name}")
            
            # Try both import paths to handle different execution contexts
            try:
                module = importlib.import_module(f"src.scrapers.{module_name}")
            except ModuleNotFoundError:
                module = importlib.import_module(f"scrapers.{module_name}")
            
            # Get the scraper class
            scraper_class = self._get_scraper_class(module, supplier_config)
            
            # Instantiate the scraper
            self.logger.info(f"Creating scraper instance: {scraper_class.__name__} for supplier: {supplier_config.name}")
            
            # Create the scraper instance with the supplier configuration
            scraper_instance = scraper_class(
                name=supplier_config.name,
                base_url=supplier_config.url,
                requires_login=supplier_config.requires_login,
                username=supplier_config.username,
                password=supplier_config.password,
                selectors=supplier_config.selectors
            )
            
            return scraper_instance
            
        except ImportError as e:
            self.logger.error(f"Failed to import scraper module for supplier {supplier_config.name}: {e}")
            raise ImportError(f"Scraper module not found for supplier {supplier_config.name}: {e}")
        except ValueError as e:
            self.logger.error(f"Failed to find scraper class for supplier {supplier_config.name}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating scraper for supplier {supplier_config.name}: {e}")
            raise
    
    def _get_module_name(self, supplier_config: SupplierConfig) -> str:
        """
        Determine the module name for the supplier.
        
        This method converts the supplier name to a valid Python module name.
        For example, "Supplier A" becomes "supplier_a".
        
        Args:
            supplier_config: The configuration for the supplier.
            
        Returns:
            str: The module name for the supplier.
        """
        # If supplier_config has a specific module name, use it
        if hasattr(supplier_config, 'module_name') and getattr(supplier_config, 'module_name'):
            return getattr(supplier_config, 'module_name')
        
        # Otherwise, use the scraper_type to determine the module
        scraper_type = supplier_config.scraper_type.lower()
        
        # Map scraper_type to module name
        if scraper_type == 'static':
            return 'static_scraper'
        elif scraper_type == 'dynamic':
            return 'dynamic_scraper'
        else:
            # For custom scrapers, convert supplier name to snake_case
            # e.g., "Supplier A" -> "supplier_a"
            module_name = supplier_config.name.lower().replace(' ', '_')
            return module_name
    
    def _get_scraper_class(self, module: Any, supplier_config: SupplierConfig) -> Type[BaseScraper]:
        """
        Get the scraper class from the module.
        
        Args:
            module: The imported module.
            supplier_config: The configuration for the supplier.
            
        Returns:
            Type[BaseScraper]: The scraper class.
            
        Raises:
            ValueError: If the scraper class cannot be found in the module.
        """
        # Try to find a class that matches the supplier name
        supplier_class_name = ''.join(word.capitalize() for word in supplier_config.name.split())
        supplier_class_name = f"{supplier_class_name}Scraper"
        
        # First, try to find a supplier-specific class
        if hasattr(module, supplier_class_name):
            return getattr(module, supplier_class_name)
        
        # If not found, look for a generic class based on scraper_type
        scraper_type = supplier_config.scraper_type.capitalize()
        generic_class_name = f"{scraper_type}Scraper"
        
        if hasattr(module, generic_class_name):
            return getattr(module, generic_class_name)
        
        # If still not found, look for any class that inherits from BaseScraper
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseScraper) and attr != BaseScraper:
                return attr
        
        # If no suitable class is found, raise an error
        raise ValueError(f"No scraper class found in module for supplier {supplier_config.name}")


# Create a singleton instance of the factory
factory = ScraperFactory()


def get_scraper(supplier_config: SupplierConfig) -> BaseScraper:
    """
    Convenience function to get a scraper instance for a supplier.
    
    Args:
        supplier_config: The configuration for the supplier.
        
    Returns:
        BaseScraper: An instance of the appropriate scraper for the supplier.
    """
    return factory.get_scraper(supplier_config)
