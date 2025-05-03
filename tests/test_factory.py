"""
Tests for the ScraperFactory.
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the necessary classes
try:
    from src.scrapers.factory import ScraperFactory
    from src.scrapers.base_scraper import BaseScraper
    from src.config import SupplierConfig
    from src.scrapers.static_scraper import StaticScraper
except ModuleNotFoundError:
    from scrapers.factory import ScraperFactory
    from scrapers.base_scraper import BaseScraper
    from config import SupplierConfig
    from scrapers.static_scraper import StaticScraper


class TestScraperFactory:
    """Tests for the ScraperFactory."""

    def test_get_module_name(self):
        """Test the _get_module_name method."""
        factory = ScraperFactory()
        
        # Test with module_name specified
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            module_name="custom_module"
        )
        assert factory._get_module_name(supplier_config) == "custom_module"
        
        # Test with static scraper_type
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="static"
        )
        assert factory._get_module_name(supplier_config) == "static_scraper"
        
        # Test with dynamic scraper_type
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="dynamic"
        )
        assert factory._get_module_name(supplier_config) == "dynamic_scraper"
        
        # Test with custom scraper_type
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="custom"
        )
        assert factory._get_module_name(supplier_config) == "test_supplier"
        
        # Test with supplier name containing spaces
        supplier_config = SupplierConfig(
            name="Supplier A",
            url="https://example.com",
            scraper_type="custom"
        )
        assert factory._get_module_name(supplier_config) == "supplier_a"
    
    def test_get_scraper_with_static_type(self):
        """Test getting a scraper with static scraper_type."""
        # This test uses the actual StaticScraper implementation
        factory = ScraperFactory()
        
        # Create a supplier config with static scraper_type
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="static"
        )
        
        # Get the scraper
        scraper = factory.get_scraper(supplier_config)
        
        # Verify that the correct scraper was returned
        assert isinstance(scraper, StaticScraper)
        assert scraper.name == "Test Supplier"
        assert scraper.base_url == "https://example.com"
    
    @patch("importlib.import_module")
    def test_get_scraper_with_import_error(self, mock_import_module):
        """Test get_scraper with import error."""
        factory = ScraperFactory()
        
        # Create a supplier config
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="nonexistent"
        )
        
        # Configure the mock to raise ImportError
        mock_import_module.side_effect = ImportError("Module not found")
        
        # Test that ImportError is raised
        with pytest.raises(ImportError):
            factory.get_scraper(supplier_config)
    
    def test_get_scraper_function(self):
        """Test the get_scraper function."""
        # Import the function here to avoid circular imports in tests
        try:
            from src.scrapers.factory import get_scraper
        except ImportError:
            from scrapers.factory import get_scraper
            
        # Create a supplier config with static scraper_type
        supplier_config = SupplierConfig(
            name="Test Supplier",
            url="https://example.com",
            scraper_type="static"
        )
        
        # Call the function
        scraper = get_scraper(supplier_config)
        
        # Verify that the correct scraper was returned
        assert isinstance(scraper, StaticScraper)
        assert scraper.name == "Test Supplier"
        assert scraper.base_url == "https://example.com"
