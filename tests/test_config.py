"""
Tests for the configuration module.
"""

import os
from pathlib import Path
from unittest import mock

import pytest
from pydantic import ValidationError, SecretStr

from src.config import (
    AppConfig, 
    LoggingConfig, 
    OutputConfig, 
    ScrapingConfig, 
    SupplierConfig, 
    load_config,
    get_env_value,
    get_secret,
    EnvFileSecretsProvider,
    AwsSecretsProvider,
    GcpSecretsProvider
)


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
        "TEST_SECRET": "secret_value",
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
        password=SecretStr("pass")
    )
    assert config.requires_login is True
    assert config.username == "user"
    assert isinstance(config.password, SecretStr)
    assert config.get_password() == "pass"
    
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


def test_get_env_value(mock_env_vars):
    """Test get_env_value function."""
    # Test existing environment variable
    assert get_env_value("LOG_LEVEL") == "DEBUG"
    
    # Test non-existent environment variable with default
    assert get_env_value("NON_EXISTENT", "default") == "default"
    
    # Test non-existent environment variable without default
    assert get_env_value("NON_EXISTENT") is None


def test_env_file_secrets_provider(mock_env_vars):
    """Test EnvFileSecretsProvider."""
    provider = EnvFileSecretsProvider(load_dotenv_file=False)
    
    # Test existing secret
    assert provider.get_secret("TEST_SECRET") == "secret_value"
    
    # Test non-existent secret
    assert provider.get_secret("NON_EXISTENT_SECRET") == ""


def test_aws_secrets_provider():
    """Test AwsSecretsProvider placeholder."""
    provider = AwsSecretsProvider()
    
    # Test that the placeholder returns empty string
    assert provider.get_secret("any_secret") == ""


def test_gcp_secrets_provider():
    """Test GcpSecretsProvider placeholder."""
    provider = GcpSecretsProvider()
    
    # Test that the placeholder returns empty string
    assert provider.get_secret("any_secret") == ""


def test_get_secret(mock_env_vars):
    """Test get_secret function."""
    # Test with default provider
    assert get_secret("TEST_SECRET") == "secret_value"
    
    # Test with custom provider
    custom_provider = mock.Mock()
    custom_provider.get_secret.return_value = "custom_secret_value"
    assert get_secret("TEST_SECRET", provider=custom_provider) == "custom_secret_value"
    custom_provider.get_secret.assert_called_once_with("TEST_SECRET")


def test_password_masking():
    """Test that passwords are properly masked in string representation."""
    config = SupplierConfig(
        name="Test Supplier",
        url="https://example.com",
        requires_login=True,
        username="user",
        password=SecretStr("sensitive_password")
    )
    
    # Check that password is not exposed in string representation
    config_str = str(config)
    assert "sensitive_password" not in config_str
    
    # But can be accessed when needed
    assert config.get_password() == "sensitive_password"


def test_environment_variable_priority():
    """Test that OS environment variables take priority over .env variables."""
    # Create a mock .env content
    dotenv_values = {
        "PRIORITY_TEST": "dotenv_value"
    }
    
    # Create a mock OS environment with the same key but different value
    os_environ = {
        "PRIORITY_TEST": "os_environ_value"
    }
    
    # Mock both dotenv.load_dotenv and os.environ
    with mock.patch("src.config.load_dotenv") as mock_load_dotenv, \
         mock.patch.dict(os.environ, os_environ, clear=True):
        
        # Mock dotenv.load_dotenv to set up the test environment
        mock_load_dotenv.return_value = True
        
        # Create a provider and test priority
        provider = EnvFileSecretsProvider()
        
        # OS environment should take priority
        assert get_env_value("PRIORITY_TEST") == "os_environ_value"
