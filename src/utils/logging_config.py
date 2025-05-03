"""
Logging configuration module for the Automated Product Data Scraper.

This module provides functions to set up and configure the Python standard logging
module with appropriate handlers, formatters, and log levels based on configuration.
It supports logging to console and/or file with configurable log levels.
"""

import logging
import os
import sys
import atexit
from pathlib import Path
from typing import Dict, List, Optional, Union

# Try different import paths to handle execution from different contexts
try:
    from src.config import config
except ImportError:
    try:
        from config import config
    except ImportError:
        # If config module is not available, we'll use environment variables directly
        pass


# Global registry of file handlers to ensure proper cleanup
_file_handlers = []


def _close_file_handlers():
    """Close all registered file handlers to prevent resource leaks."""
    global _file_handlers
    for handler in _file_handlers:
        if handler and hasattr(handler, 'close'):
            try:
                handler.close()
            except Exception:
                pass  # Ignore errors during cleanup
    _file_handlers = []


# Register the cleanup function to run at exit
atexit.register(_close_file_handlers)


def get_log_level(level_name: Optional[str] = None) -> int:
    """
    Convert a string log level to the corresponding logging module constant.
    
    Args:
        level_name: String representation of the log level (e.g., "INFO", "DEBUG")
                   If None, will try to get from config or environment variable
    
    Returns:
        int: The logging module level constant (e.g., logging.INFO)
    """
    if level_name is None:
        # First check environment variable
        env_level = os.getenv("LOG_LEVEL")
        if env_level:
            level_name = env_level
        else:
            # Then try config
            try:
                level_name = config.logging.level
            except (NameError, AttributeError):
                # Default to INFO if all else fails
                level_name = "INFO"
    
    # Convert to uppercase and get the corresponding logging level
    level_name = str(level_name).upper()
    return getattr(logging, level_name, logging.INFO)


def get_log_format() -> str:
    """
    Get the log format string from environment variable or use default.
    
    Returns:
        str: The log format string
    """
    return os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def get_log_file_path() -> Optional[Path]:
    """
    Get the log file path from environment variable or config.
    
    Returns:
        Optional[Path]: The path to the log file, or None if not configured
    """
    log_file = os.getenv("LOG_FILE")
    
    if log_file:
        path = Path(log_file)
    else:
        # Try to use the output directory from config
        try:
            output_dir = Path(config.output.output_dir)
            path = output_dir / "scraper.log"
        except (NameError, AttributeError):
            # If config is not available, use a default path
            path = Path("./output/scraper.log")
    
    # Ensure the directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    return path


def setup_logging(
    level: Optional[str] = None,
    log_to_console: bool = True,
    log_to_file: bool = True,
    log_format: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None
) -> None:
    """
    Set up logging configuration with the specified parameters.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If None, will be determined from config or environment
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        log_format: Format string for log messages
                   If None, will be determined from environment or default
        log_file: Path to log file
                 If None, will be determined from config or environment
    """
    # Get log level
    log_level = get_log_level(level)
    
    # Get log format
    if log_format is None:
        log_format = get_log_format()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            # Close file handlers properly
            handler.close()
        root_logger.removeHandler(handler)
    
    # Clear the global registry of file handlers
    _close_file_handlers()
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        if log_file is None:
            log_file = get_log_file_path()
        else:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)
        
        # Register the file handler for cleanup
        _file_handlers.append(file_handler)
    
    # Log initial message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at level: {logging.getLevelName(log_level)}")
    if log_to_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    This is a convenience function to get a logger with the correct name.
    It ensures that logging is set up before returning the logger.
    
    Args:
        name: Name of the logger, typically __name__
        
    Returns:
        logging.Logger: The logger instance
    """
    # Ensure root logger has at least one handler
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        setup_logging()
    
    return logging.getLogger(name)
