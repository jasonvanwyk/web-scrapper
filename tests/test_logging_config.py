"""
Unit tests for the logging configuration module.
"""

import unittest
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Fix the import to work when running from different contexts
try:
    from src.utils.logging_config import setup_logging, get_logger, get_log_level
except ImportError:
    # When running directly from tests directory
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.utils.logging_config import setup_logging, get_logger, get_log_level


class TestLoggingConfig(unittest.TestCase):
    """Test cases for the logging configuration module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = Path(self.temp_dir.name) / "test.log"
        
        # Reset the root logger before each test
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
        
        # Reset the root logger after each test
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_get_log_level(self):
        """Test the get_log_level function."""
        # Test with explicit level
        self.assertEqual(get_log_level("DEBUG"), logging.DEBUG)
        self.assertEqual(get_log_level("INFO"), logging.INFO)
        self.assertEqual(get_log_level("WARNING"), logging.WARNING)
        self.assertEqual(get_log_level("ERROR"), logging.ERROR)
        self.assertEqual(get_log_level("CRITICAL"), logging.CRITICAL)
        
        # Test with lowercase level
        self.assertEqual(get_log_level("debug"), logging.DEBUG)
        
        # Test with invalid level (should default to INFO)
        self.assertEqual(get_log_level("INVALID"), logging.INFO)
        
        # Test with None and environment variable
        with patch.dict('os.environ', {'LOG_LEVEL': 'DEBUG'}, clear=True):
            self.assertEqual(get_log_level(None), logging.DEBUG)
    
    def test_setup_logging_console_only(self):
        """Test setup_logging with console output only."""
        setup_logging(level="DEBUG", log_to_console=True, log_to_file=False)
        
        # Check that the root logger has the correct level
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)
        
        # Check that there is exactly one handler (console)
        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsInstance(root_logger.handlers[0], logging.StreamHandler)
    
    def test_setup_logging_file_only(self):
        """Test setup_logging with file output only."""
        setup_logging(
            level="INFO", 
            log_to_console=False, 
            log_to_file=True,
            log_file=self.log_file
        )
        
        # Check that the root logger has the correct level
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)
        
        # Check that there is exactly one handler (file)
        self.assertEqual(len(root_logger.handlers), 1)
        self.assertIsInstance(root_logger.handlers[0], logging.FileHandler)
        
        # Check that the file handler has the correct path
        self.assertEqual(root_logger.handlers[0].baseFilename, str(self.log_file))
    
    def test_setup_logging_both_outputs(self):
        """Test setup_logging with both console and file output."""
        setup_logging(
            level="WARNING", 
            log_to_console=True, 
            log_to_file=True,
            log_file=self.log_file
        )
        
        # Check that the root logger has the correct level
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.WARNING)
        
        # Check that there are exactly two handlers
        self.assertEqual(len(root_logger.handlers), 2)
        
        # Check handler types
        handler_types = [type(h) for h in root_logger.handlers]
        self.assertIn(logging.StreamHandler, handler_types)
        self.assertIn(logging.FileHandler, handler_types)
    
    def test_setup_logging_custom_format(self):
        """Test setup_logging with a custom format."""
        custom_format = "%(levelname)s - %(message)s"
        setup_logging(
            level="INFO", 
            log_format=custom_format,
            log_to_console=True, 
            log_to_file=False
        )
        
        # Check that the handler has the correct formatter
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        self.assertEqual(handler.formatter._fmt, custom_format)
    
    def test_get_logger(self):
        """Test the get_logger function."""
        # Should set up logging if not already set up
        logger = get_logger("test_logger")
        
        # Check that the logger has the correct name
        self.assertEqual(logger.name, "test_logger")
        
        # Check that the root logger has at least one handler
        root_logger = logging.getLogger()
        self.assertGreater(len(root_logger.handlers), 0)
    
    def test_log_message_to_file(self):
        """Test that log messages are written to the file."""
        setup_logging(
            level="INFO", 
            log_to_console=False, 
            log_to_file=True,
            log_file=self.log_file
        )
        
        # Log a test message
        logger = get_logger("test_logger")
        test_message = "This is a test log message"
        logger.info(test_message)
        
        # Check that the message was written to the file
        with open(self.log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
            self.assertIn(test_message, log_content)
            self.assertIn("test_logger", log_content)
            self.assertIn("INFO", log_content)


if __name__ == "__main__":
    unittest.main()
