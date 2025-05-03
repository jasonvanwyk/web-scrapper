"""
Configuration module for the Automated Product Data Scraper.

This module uses Pydantic for configuration validation and python-dotenv for loading
environment variables from .env files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator, model_validator


# Load environment variables from .env file
load_dotenv()


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )


class OutputConfig(BaseModel):
    """Configuration for output files."""
    output_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", "./output")),
        description="Directory for output files"
    )
    csv_filename: str = Field(
        default_factory=lambda: os.getenv("CSV_FILENAME", "product_data.csv"),
        description="Name of the CSV output file"
    )
    csv_filename_pattern: str = Field(
        default_factory=lambda: os.getenv("CSV_FILENAME_PATTERN", "{supplier}_{timestamp}.csv"),
        description="Pattern for CSV filename with placeholders for supplier and timestamp"
    )
    include_timestamp: bool = Field(
        default_factory=lambda: os.getenv("INCLUDE_TIMESTAMP", "True").lower() in ("true", "1", "t"),
        description="Whether to include timestamp in CSV filenames"
    )
    csv_encoding: str = Field(
        default_factory=lambda: os.getenv("CSV_ENCODING", "utf-8"),
        description="Encoding to use for CSV files"
    )
    download_images: bool = Field(
        default_factory=lambda: os.getenv("DOWNLOAD_IMAGES", "False").lower() in ("true", "1", "t"),
        description="Whether to download images or just store URLs"
    )
    image_dir: Optional[Path] = Field(
        default_factory=lambda: Path(os.getenv("IMAGE_DIR", "./output/images")) if os.getenv("DOWNLOAD_IMAGES", "False").lower() in ("true", "1", "t") else None,
        description="Directory for downloaded images"
    )

    @validator("output_dir", "image_dir", pre=True)
    def validate_directory(cls, v):
        """Validate and create directory if it doesn't exist."""
        if v is not None:
            path = Path(v)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return v


class ScrapingConfig(BaseModel):
    """Configuration for web scraping."""
    request_timeout: int = Field(
        default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "30")),
        description="Timeout for HTTP requests in seconds"
    )
    request_retries: int = Field(
        default_factory=lambda: int(os.getenv("REQUEST_RETRIES", "3")),
        description="Number of retries for failed HTTP requests"
    )
    request_delay: float = Field(
        default_factory=lambda: float(os.getenv("REQUEST_DELAY", "1.0")),
        description="Delay between HTTP requests in seconds"
    )
    respect_robots_txt: bool = Field(
        default_factory=lambda: os.getenv("RESPECT_ROBOTS_TXT", "True").lower() in ("true", "1", "t"),
        description="Whether to respect robots.txt"
    )
    browser_timeout: int = Field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30000")),
        description="Timeout for browser operations in milliseconds"
    )
    browser_delay: float = Field(
        default_factory=lambda: float(os.getenv("BROWSER_DELAY", "2.0")),
        description="Delay between browser actions in seconds"
    )
    headless: bool = Field(
        default_factory=lambda: os.getenv("HEADLESS", "True").lower() in ("true", "1", "t"),
        description="Whether to run the browser in headless mode"
    )
    browser_type: str = Field(
        default_factory=lambda: os.getenv("BROWSER_TYPE", "chromium"),
        description="Type of browser to use (chromium, firefox, webkit)"
    )
    stealth_mode: bool = Field(
        default_factory=lambda: os.getenv("STEALTH_MODE", "True").lower() in ("true", "1", "t"),
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
    password: Optional[str] = Field(default=None, description="Password for login")
    selectors: Dict[str, str] = Field(default_factory=dict, description="CSS selectors for data extraction")

    model_config = {"validate_assignment": True}

    @model_validator(mode='after')
    def validate_credentials_if_login_required(self):
        """Validate that credentials are provided if login is required."""
        if self.requires_login and (self.username is None or self.password is None):
            raise ValueError("Username and password are required when login is required")
        return self


class AppConfig(BaseModel):
    """Main application configuration."""
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    suppliers: List[SupplierConfig] = Field(default_factory=list, description="List of suppliers to scrape")


def load_config() -> AppConfig:
    """
    Load and validate application configuration.
    
    Returns:
        AppConfig: Validated application configuration
    """
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
    
    return AppConfig(
        logging=LoggingConfig(),
        output=OutputConfig(),
        scraping=ScrapingConfig(),
        suppliers=suppliers,
    )


# Global configuration instance
config = load_config()
