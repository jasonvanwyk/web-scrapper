# Logging Configuration Guide

This document explains how to use the logging configuration module implemented in the Automated Product Data Scraper project.

## Overview

The logging configuration module provides a standardized way to set up and use logging throughout the application. It uses Python's standard `logging` module and provides additional functionality for configuring log levels, formats, and output destinations.

## Basic Usage

### Setting Up Logging

Logging should be set up at the application entry point, typically in `main.py`:

```python
from utils.logging_config import setup_logging

# Set up logging with default settings
setup_logging()

# Or with custom settings
setup_logging(
    level="DEBUG",                    # Log level
    log_to_console=True,              # Log to console
    log_to_file=True,                 # Log to file
    log_format="%(levelname)s: %(message)s",  # Custom format
    log_file="/path/to/custom.log"    # Custom log file path
)
```

### Getting a Logger

In each module where you need logging, use the `get_logger` function:

```python
from utils.logging_config import get_logger

# Get a logger with the module name
logger = get_logger(__name__)

# Use the logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Include exception info
try:
    # Some code that might raise an exception
    result = 1 / 0
except Exception as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
```

## Configuration Options

### Environment Variables

The logging module respects the following environment variables:

- `LOG_LEVEL`: The log level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FORMAT`: The format string for log messages
- `LOG_FILE`: The path to the log file

These can be set in the `.env` file or directly in the environment:

```
LOG_LEVEL=DEBUG
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=./logs/app.log
```

### Log Levels

The following log levels are available, in order of increasing severity:

1. `DEBUG`: Detailed information, typically useful only for diagnosing problems
2. `INFO`: Confirmation that things are working as expected
3. `WARNING`: An indication that something unexpected happened, or may happen in the future
4. `ERROR`: Due to a more serious problem, the software has not been able to perform a function
5. `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running

### Log Format

The default log format includes:
- Timestamp: When the log was created
- Logger name: Usually the module name
- Log level: DEBUG, INFO, etc.
- Message: The actual log message

Example: `2025-05-03 21:13:40,123 - src.main - INFO - Starting Automated Product Data Scraper`

## Best Practices

1. **Use Appropriate Log Levels**: 
   - `DEBUG` for detailed diagnostic information
   - `INFO` for general operational information
   - `WARNING` for unexpected events that don't prevent normal operation
   - `ERROR` for errors that prevent a specific operation from completing
   - `CRITICAL` for errors that prevent the application from continuing

2. **Include Context**: Always include relevant context in log messages to make debugging easier.

3. **Log Exceptions**: When catching exceptions, log them with `exc_info=True` to include the stack trace.

4. **Sensitive Information**: Never log sensitive information like passwords or API keys.

5. **Performance Considerations**: For expensive log messages, check the log level before constructing the message:
   ```python
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug(f"Expensive operation result: {calculate_expensive_result()}")
   ```

## Integration with Other Components

The logging module is designed to work with all other components of the application. Each component should:

1. Get its own logger using `get_logger(__name__)`
2. Use appropriate log levels for different types of messages
3. Include relevant context in log messages

## Extending the Logging System

For future enhancements, consider:

1. **Cloud Logging Integration**: Add handlers for cloud logging services like AWS CloudWatch or GCP Cloud Logging
2. **Structured Logging**: Use JSON formatting for better parsing and analysis
3. **Log Rotation**: Implement log rotation for long-running applications
4. **Custom Filters**: Add filters to control which log messages are output based on criteria beyond log level
