"""
Tests for the configuration module.
"""

import os
from pathlib import Path
from unittest import mock

import pytest
from pydantic import ValidationError

from src.config import AppConfig, LoggingConfig, OutputConfig, ScrapingConfig, SupplierConfig, load_config


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables."""
    with mock.patch.dict(os.environ, {
        "LOG_LEVEL": "DEBUG",
        "OUTPUT_DIR": "./test_output",
        "CSV_FILENAME": "test_data.csv",
        "DOWNLOAD_IMAGES": "True",
        "IMAGE_DIR": "./test_output/images",
        "REQUEST_TIMEOUT": "15",
        "REQUEST_RETRIES": "5",
        "REQUEST_DELAY": "2.0",
        "RESPECT_ROBOTS_TXT": "True",
    }):
        yield


def test_logging_config():
    """Test LoggingConfig initialization and validation."""
    # Default values
    config = LoggingConfig()
    assert config.level == "INFO"
    
    # Custom values
    config = LoggingConfig(level="DEBUG")
    assert config.level == "DEBUG"


def test_output_config():
    """Test OutputConfig initialization and validation."""
    # Default values
    config = OutputConfig()
    assert config.output_dir == Path("./output")
    assert config.csv_filename == "product_data.csv"
    assert config.download_images is False
    
    # Custom values
    config = OutputConfig(
        output_dir=Path("./custom_output"),
        csv_filename="custom.csv",
        download_images=True,
        image_dir=Path("./custom_output/images")
    )
    assert config.output_dir == Path("./custom_output")
    assert config.csv_filename == "custom.csv"
    assert config.download_images is True
    assert config.image_dir == Path("./custom_output/images")


def test_scraping_config():
    """Test ScrapingConfig initialization and validation."""
    # Default values
    config = ScrapingConfig()
    assert config.request_timeout == 30
    assert config.request_retries == 3
    assert config.request_delay == 1.0
    assert config.respect_robots_txt is True
    
    # Custom values
    config = ScrapingConfig(
        request_timeout=15,
        request_retries=5,
        request_delay=2.0,
        respect_robots_txt=False
    )
    assert config.request_timeout == 15
    assert config.request_retries == 5
    assert config.request_delay == 2.0
    assert config.respect_robots_txt is False


def test_supplier_config():
    """Test SupplierConfig initialization and validation."""
    # Minimal valid config
    config = SupplierConfig(name="Test Supplier", url="https://example.com")
    assert config.name == "Test Supplier"
    assert config.url == "https://example.com"
    assert config.scraper_type == "static"
    assert config.requires_login is False
    assert config.username is None
    assert config.password is None
    
    # Config with login
    config = SupplierConfig(
        name="Test Supplier",
        url="https://example.com",
        requires_login=True,
        username="user",
        password="pass"
    )
    assert config.requires_login is True
    assert config.username == "user"
    assert config.password == "pass"
    
    # Test validation error when setting requires_login to True after creation
    config = SupplierConfig(
        name="Test Supplier",
        url="https://example.com"
    )
    
    # This should raise a validation error
    with pytest.raises(ValueError):
        config.requires_login = True


def test_app_config():
    """Test AppConfig initialization and validation."""
    # Default config
    config = AppConfig()
    assert isinstance(config.logging, LoggingConfig)
    assert isinstance(config.output, OutputConfig)
    assert isinstance(config.scraping, ScrapingConfig)
    assert config.suppliers == []
    
    # Config with suppliers
    config = AppConfig(
        suppliers=[
            SupplierConfig(name="Supplier 1", url="https://example1.com"),
            SupplierConfig(name="Supplier 2", url="https://example2.com"),
        ]
    )
    assert len(config.suppliers) == 2
    assert config.suppliers[0].name == "Supplier 1"
    assert config.suppliers[1].name == "Supplier 2"


def test_load_config(mock_env_vars):
    """Test load_config function with mocked environment variables."""
    config = load_config()
    
    assert config.logging.level == "DEBUG"
    assert config.output.output_dir == Path("./test_output")
    assert config.output.csv_filename == "test_data.csv"
    assert config.output.download_images is True
    assert config.output.image_dir == Path("./test_output/images")
    assert config.scraping.request_timeout == 15
    assert config.scraping.request_retries == 5
    assert config.scraping.request_delay == 2.0
    assert config.scraping.respect_robots_txt is True
