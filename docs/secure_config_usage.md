# Secure Configuration Loading

This document explains how to use the secure configuration loading system implemented in the Automated Product Data Scraper project.

## Overview

The configuration system provides:

- Secure loading of configuration values from environment variables and `.env` files
- Prioritization of OS environment variables over `.env` file variables
- Validation of configuration structure and types using Pydantic
- Secure handling of sensitive data (passwords, API keys)
- Placeholder interfaces for cloud secrets management services

## Basic Usage

### Accessing Configuration

The configuration is loaded automatically when the application starts and is available as a global instance:

```python
from src.config import config

# Access configuration values
log_level = config.logging.level
output_dir = config.output.output_dir
request_timeout = config.scraping.request_timeout
```

### Environment Variables

Configuration values can be set using environment variables. The system will look for environment variables with specific names, such as:

```
LOG_LEVEL=DEBUG
OUTPUT_DIR=./custom_output
CSV_FILENAME=data.csv
DOWNLOAD_IMAGES=True
```

### .env File

For local development, you can use a `.env` file to set environment variables. Create a file named `.env` in the project root directory with your configuration values:

```
# Logging configuration
LOG_LEVEL=DEBUG

# Output configuration
OUTPUT_DIR=./output
CSV_FILENAME=product_data.csv
DOWNLOAD_IMAGES=False

# Scraping configuration
REQUEST_TIMEOUT=30
REQUEST_RETRIES=3
```

**Important**: The `.env` file should never be committed to version control as it may contain sensitive information. It is already included in the `.gitignore` file.

### Priority

The system prioritizes values in the following order:
1. OS environment variables (highest priority)
2. `.env` file variables
3. Default values (lowest priority)

This allows you to override configuration in different environments without modifying code.

## Handling Sensitive Data

### Passwords and API Keys

Sensitive data like passwords and API keys are handled securely using Pydantic's `SecretStr` type, which prevents accidental exposure in logs or string representations:

```python
# Setting a password
supplier_config = SupplierConfig(
    name="Example Supplier",
    url="https://example.com",
    requires_login=True,
    username="user",
    password=SecretStr("secure_password")
)

# Accessing the password when needed (e.g., for authentication)
password = supplier_config.get_password()
```

### Secrets Management

The system includes a flexible secrets management interface that can be extended to support different backends:

```python
from src.config import get_secret

# Get a secret from the default provider (environment variables)
api_key = get_secret("API_KEY")

# Use a specific provider
from src.config import AwsSecretsProvider
aws_provider = AwsSecretsProvider()
aws_secret = get_secret("DB_PASSWORD", provider=aws_provider)
```

## Configuration Structure

The configuration is organized into several sections:

### Logging Configuration

```python
config.logging.level  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

### Output Configuration

```python
config.output.output_dir        # Directory for output files
config.output.csv_filename      # Name of the CSV output file
config.output.csv_encoding      # Encoding for CSV files (default: utf-8)
config.output.download_images   # Whether to download images or just store URLs
config.output.image_dir         # Directory for downloaded images
```

### Scraping Configuration

```python
config.scraping.request_timeout    # Timeout for HTTP requests in seconds
config.scraping.request_retries    # Number of retries for failed HTTP requests
config.scraping.request_delay      # Delay between HTTP requests in seconds
config.scraping.respect_robots_txt # Whether to respect robots.txt
config.scraping.browser_timeout    # Timeout for browser operations in milliseconds
config.scraping.browser_delay      # Delay between browser actions in seconds
config.scraping.headless           # Whether to run the browser in headless mode
config.scraping.browser_type       # Type of browser to use (chromium, firefox, webkit)
config.scraping.stealth_mode       # Whether to use stealth mode to minimize bot detection
```

### Supplier Configuration

```python
# Access the first supplier
supplier = config.suppliers[0]

supplier.name          # Name of the supplier
supplier.url           # URL of the supplier website
supplier.scraper_type  # Type of scraper to use (static or dynamic)
supplier.requires_login # Whether login is required
supplier.username      # Username for login
supplier.get_password() # Get the password as a string (use only when needed)
supplier.selectors     # CSS selectors for data extraction
```

## Advanced Usage

### Custom Configuration Loading

If you need to load configuration in a custom way, you can use the `load_config` function:

```python
from src.config import load_config

# Load and validate configuration
custom_config = load_config()
```

### Cloud Secrets Management

The system includes placeholder implementations for AWS Secrets Manager and Google Cloud Secret Manager. These can be extended to provide actual integration with these services:

```python
from src.config import AwsSecretsProvider, GcpSecretsProvider

# AWS Secrets Manager
aws_provider = AwsSecretsProvider()
aws_secret = aws_provider.get_secret("my/secret/path")

# Google Cloud Secret Manager
gcp_provider = GcpSecretsProvider()
gcp_secret = gcp_provider.get_secret("projects/my-project/secrets/my-secret")
```

### Creating Custom Secrets Providers

You can create custom secrets providers by implementing the `SecretsProvider` interface:

```python
from src.config import SecretsProvider

class CustomSecretsProvider(SecretsProvider):
    def get_secret(self, secret_name: str) -> str:
        # Implement your custom logic to retrieve secrets
        return "secret_value"
```

## Best Practices

1. **Never hardcode sensitive information** like passwords, API keys, or tokens in your code.
2. **Use environment variables** for configuration in production environments.
3. **Keep the `.env` file out of version control** (it's already in `.gitignore`).
4. **Only access sensitive values when needed** and never log them.
5. **Validate configuration** early in the application startup to fail fast if required values are missing.
6. **Provide sensible defaults** for non-critical configuration values.
7. **Document all configuration options** so others know what can be configured.
