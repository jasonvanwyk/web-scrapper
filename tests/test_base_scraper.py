"""
Tests for the BaseScraper abstract base class.
"""

import pytest
from abc import ABC
import logging

# Import the BaseScraper class
try:
    from src.scrapers.base_scraper import BaseScraper
except ModuleNotFoundError:
    from scrapers.base_scraper import BaseScraper


class TestBaseScraper:
    """Tests for the BaseScraper abstract base class."""

    def test_base_scraper_is_abstract(self):
        """Test that BaseScraper is an abstract base class."""
        assert issubclass(BaseScraper, ABC)
        
        # Verify that BaseScraper has abstract methods
        abstract_methods = BaseScraper.__abstractmethods__
        
        # Check that all required abstract methods are defined
        assert "login" in abstract_methods
        assert "Maps_to_products" in abstract_methods
        assert "get_product_urls" in abstract_methods
        assert "handle_pagination" in abstract_methods
        assert "extract_data" in abstract_methods
    
    def test_base_scraper_cannot_be_instantiated(self):
        """Test that BaseScraper cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseScraper(name="Test", base_url="https://example.com")
    
    def test_build_absolute_url(self):
        """Test the build_absolute_url utility method."""
        # Create a concrete implementation of BaseScraper for testing
        class ConcreteScraper(BaseScraper):
            def login(self, username, password):
                return True
            
            def Maps_to_products(self, category_map):
                return {k: [] for k in category_map}
            
            def get_product_urls(self, category_url=None):
                return []
            
            def handle_pagination(self, url, page=1):
                return url
            
            def extract_data(self, product_url):
                return {}
        
        # Instantiate the concrete scraper
        scraper = ConcreteScraper(name="Test", base_url="https://example.com")
        
        # Test building absolute URLs
        assert scraper.build_absolute_url("/path") == "https://example.com/path"
        assert scraper.build_absolute_url("path") == "https://example.com/path"
        assert scraper.build_absolute_url("/path/to/resource") == "https://example.com/path/to/resource"
        
        # Test with base URL that already has a path
        scraper = ConcreteScraper(name="Test", base_url="https://example.com/base/")
        assert scraper.build_absolute_url("resource") == "https://example.com/base/resource"
        
        # Test with absolute URL
        assert scraper.build_absolute_url("https://other.com/path") == "https://other.com/path"
    
    def test_str_representation(self):
        """Test the string representation of a scraper."""
        # Create a concrete implementation of BaseScraper for testing
        class ConcreteScraper(BaseScraper):
            def login(self, username, password):
                return True
            
            def Maps_to_products(self, category_map):
                return {k: [] for k in category_map}
            
            def get_product_urls(self, category_url=None):
                return []
            
            def handle_pagination(self, url, page=1):
                return url
            
            def extract_data(self, product_url):
                return {}
        
        # Instantiate the concrete scraper
        scraper = ConcreteScraper(name="Test", base_url="https://example.com")
        
        # Test string representation
        assert str(scraper) == "ConcreteScraper(name=Test, base_url=https://example.com)"
    
    def test_logger_initialization(self):
        """Test that the logger is properly initialized."""
        # Create a concrete implementation of BaseScraper for testing
        class ConcreteScraper(BaseScraper):
            def login(self, username, password):
                return True
            
            def Maps_to_products(self, category_map):
                return {k: [] for k in category_map}
            
            def get_product_urls(self, category_url=None):
                return []
            
            def handle_pagination(self, url, page=1):
                return url
            
            def extract_data(self, product_url):
                return {}
        
        # Instantiate the concrete scraper
        scraper = ConcreteScraper(name="Test", base_url="https://example.com")
        
        # Test logger initialization
        assert isinstance(scraper.logger, logging.Logger)
        assert scraper.logger.name.endswith("ConcreteScraper")
