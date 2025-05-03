"""
Configuration module for the Automated Product Data Scraper.

This module uses Pydantic for configuration validation and python-dotenv for loading
environment variables from .env files. It prioritizes OS environment variables over
.env file variables for deployment scenarios and includes secure handling of sensitive data.

The module provides:
- Pydantic models for configuration validation
- Environment variable loading with proper prioritization
- Secure handling of sensitive values
- Placeholder interfaces for cloud secrets management
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, model_validator


# Create a logger for this module
logger = logging.getLogger(__name__)


class SecretsProvider(ABC):
    """Abstract base class for secrets management providers."""
    
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret by name.
        
        Args:
            secret_name: The name of the secret to retrieve
            
        Returns:
            str: The secret value
        """
        pass


class EnvFileSecretsProvider(SecretsProvider):
    """Secrets provider that uses environment variables and .env files."""
    
    def __init__(self, load_dotenv_file: bool = True):
        """
        Initialize the environment-based secrets provider.
        
        Args:
            load_dotenv_file: Whether to load variables from .env file
        """
        if load_dotenv_file:
            # Load environment variables from .env file
            # This will NOT override existing OS environment variables
            load_dotenv()
    
    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve a secret from environment variables.
        
        Args:
            secret_name: The name of the environment variable
            
        Returns:
            str: The secret value or empty string if not found
        """
        return os.getenv(secret_name, "")


class AwsSecretsProvider(SecretsProvider):
    """
    Placeholder for AWS Secrets Manager integration.
    
    This class would be implemented to retrieve secrets from AWS Secrets Manager
    in a production environment.
    """
    
    def get_secret(self, secret_name: str) -> str:
        """
        Placeholder for retrieving a secret from AWS Secrets Manager.
        
        Args:
            secret_name: The name/path of the secret in AWS Secrets Manager
            
        Returns:
            str: The secret value
        """
        logger.warning("AWS Secrets Manager integration is not implemented")
        return ""


class GcpSecretsProvider(SecretsProvider):
    """
    Placeholder for Google Cloud Secret Manager integration.
    
    This class would be implemented to retrieve secrets from GCP Secret Manager
    in a production environment.
    """
    
    def get_secret(self, secret_name: str) -> str:
        """
        Placeholder for retrieving a secret from GCP Secret Manager.
        
        Args:
            secret_name: The name/path of the secret in GCP Secret Manager
            
        Returns:
            str: The secret value
        """
        logger.warning("GCP Secret Manager integration is not implemented")
        return ""


# Create the default secrets provider
secrets_provider = EnvFileSecretsProvider()


def get_env_value(key: str, default: Any = None) -> Any:
    """
    Get a value from environment variables with a default fallback.
    
    This function prioritizes OS environment variables over .env file variables,
    which is important for deployment scenarios.
    
    Args:
        key: The environment variable name
        default: Default value if the environment variable is not set
        
    Returns:
        The value from environment or the default
    """
    return os.environ.get(key, default)


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field(
        default_factory=lambda: get_env_value("LOG_LEVEL", "INFO"),
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )


class OutputConfig(BaseModel):
    """Configuration for output files."""
    output_dir: Path = Field(
        default_factory=lambda: Path(get_env_value("OUTPUT_DIR", "./output")),
        description="Directory for output files"
    )
    csv_filename: str = Field(
        default_factory=lambda: get_env_value("CSV_FILENAME", "product_data.csv"),
        description="Name of the CSV output file"
    )
    csv_filename_pattern: str = Field(
        default_factory=lambda: get_env_value("CSV_FILENAME_PATTERN", "{supplier}_{timestamp}.csv"),
        description="Pattern for CSV filename with placeholders for supplier and timestamp"
    )
    include_timestamp: bool = Field(
        default_factory=lambda: get_env_value("INCLUDE_TIMESTAMP", "True").lower() in ("true", "1", "t"),
        description="Whether to include timestamp in CSV filenames"
    )
    csv_encoding: str = Field(
        default_factory=lambda: get_env_value("CSV_ENCODING", "utf-8"),
        description="Encoding to use for CSV files"
    )
    download_images: bool = Field(
        default_factory=lambda: get_env_value("DOWNLOAD_IMAGES", "False").lower() in ("true", "1", "t"),
        description="Whether to download images or just store URLs"
    )
    image_dir: Optional[Path] = Field(
        default_factory=lambda: Path(get_env_value("IMAGE_DIR", "./output/images")) if get_env_value("DOWNLOAD_IMAGES", "False").lower() in ("true", "1", "t") else None,
        description="Directory for downloaded images"
    )

    @model_validator(mode='after')
    def validate_directories(self):
        """Validate and create directories if they don't exist."""
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.image_dir and self.download_images:
            self.image_dir.mkdir(parents=True, exist_ok=True)
        
        return self


class ScrapingConfig(BaseModel):
    """Configuration for web scraping."""
    request_timeout: int = Field(
        default_factory=lambda: int(get_env_value("REQUEST_TIMEOUT", "30")),
        description="Timeout for HTTP requests in seconds"
    )
    request_retries: int = Field(
        default_factory=lambda: int(get_env_value("REQUEST_RETRIES", "3")),
        description="Number of retries for failed HTTP requests"
    )
    request_delay: float = Field(
        default_factory=lambda: float(get_env_value("REQUEST_DELAY", "1.0")),
        description="Delay between HTTP requests in seconds"
    )
    respect_robots_txt: bool = Field(
        default_factory=lambda: get_env_value("RESPECT_ROBOTS_TXT", "True").lower() in ("true", "1", "t"),
        description="Whether to respect robots.txt"
    )
    browser_timeout: int = Field(
        default_factory=lambda: int(get_env_value("BROWSER_TIMEOUT", "30000")),
        description="Timeout for browser operations in milliseconds"
    )
    browser_delay: float = Field(
        default_factory=lambda: float(get_env_value("BROWSER_DELAY", "2.0")),
        description="Delay between browser actions in seconds"
    )
    headless: bool = Field(
        default_factory=lambda: get_env_value("HEADLESS", "True").lower() in ("true", "1", "t"),
        description="Whether to run the browser in headless mode"
    )
    browser_type: str = Field(
        default_factory=lambda: get_env_value("BROWSER_TYPE", "chromium"),
        description="Type of browser to use (chromium, firefox, webkit)"
    )
    stealth_mode: bool = Field(
        default_factory=lambda: get_env_value("STEALTH_MODE", "True").lower() in ("true", "1", "t"),
        description="Whether to use stealth mode to minimize bot detection"
    )


class SupplierConfig(BaseModel):
    """Configuration for a supplier."""
    name: str = Field(..., description="Name of the supplier")
    url: str = Field(..., description="URL of the supplier website")
    scraper_type: str = Field(default="static", description="Type of scraper to use (static or dynamic)")
    module_name: Optional[str] = Field(default=None, description="Optional specific module name for the scraper")
    requires_login: bool = Field(default=False, description="Whether login is required")
    username: Optional[str] = Field(default=None, description="Username for login")
    password: Optional[SecretStr] = Field(default=None, description="Password for login")
    selectors: Dict[str, str] = Field(default_factory=dict, description="CSS selectors for data extraction")

    model_config = {"validate_assignment": True}

    @model_validator(mode='after')
    def validate_credentials_if_login_required(self):
        """Validate that credentials are provided if login is required."""
        if self.requires_login and (self.username is None or self.password is None):
            raise ValueError("Username and password are required when login is required")
        return self
    
    def get_password(self) -> Optional[str]:
        """
        Get the password as a string, if set.
        
        This method should be used carefully and only when the password is needed
        for authentication. The password should not be logged or stored in plaintext.
        
        Returns:
            Optional[str]: The password as a string, or None if not set
        """
        if self.password is None:
            return None
        return self.password.get_secret_value()


class AppConfig(BaseModel):
    """Main application configuration."""
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    suppliers: List[SupplierConfig] = Field(default_factory=list, description="List of suppliers to scrape")


def load_config() -> AppConfig:
    """
    Load and validate application configuration.
    
    This function loads configuration from environment variables (prioritized)
    and .env file (fallback), then validates it using Pydantic models.
    
    Returns:
        AppConfig: Validated application configuration
    """
    logger.debug("Loading application configuration")
    
    # Create supplier configurations
    suppliers = []
    
    # Add Isivunu Naturals supplier
    suppliers.append(
        SupplierConfig(
            name="Isivunu Naturals",
            url="https://www.isivunonaturals.com/",
            scraper_type="static",  # Using static scraper since the site doesn't require JavaScript rendering
            requires_login=False,
            selectors={
                # CSS selectors for product extraction
                "product_list": ".grid__item",
                "product_name": "h3",
                "product_price": ".price",
                "product_description": ".rte",
                "product_image": "img.grid-view-item__image",
                "product_link": "a.grid-view-item__link",
                "product_sku": ".product-single__sku",
                "collection_links": ".grid-link__container a"
            }
        )
    )
    
    # Create and validate the full configuration
    app_config = AppConfig(
        logging=LoggingConfig(),
        output=OutputConfig(),
        scraping=ScrapingConfig(),
        suppliers=suppliers,
    )
    
    logger.debug("Configuration loaded and validated successfully")
    return app_config


# Global configuration instance
config = load_config()


def get_secret(secret_name: str, provider: Optional[SecretsProvider] = None) -> str:
    """
    Get a secret value from the configured secrets provider.
    
    This function provides a unified interface for retrieving secrets,
    regardless of where they are stored (environment variables, AWS Secrets Manager, etc.)
    
    Args:
        secret_name: The name of the secret to retrieve
        provider: Optional specific provider to use, defaults to the global provider
        
    Returns:
        str: The secret value or empty string if not found
    """
    if provider is None:
        provider = secrets_provider
    
    return provider.get_secret(secret_name)
