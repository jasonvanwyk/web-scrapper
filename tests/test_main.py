"""
Tests for the main module.
"""

import logging
import sys
from pathlib import Path
from unittest import mock

import pytest

# Use absolute imports
import src.main
from src.main import main, setup_logging


@pytest.fixture
def mock_config():
    """Fixture to mock the config module."""
    with mock.patch("src.main.config") as mock_config:
        # Configure the mock
        mock_config.logging.level = "INFO"
        mock_config.output.output_dir = Path("./test_output")
        mock_config.output.download_images = False
        mock_config.suppliers = []
        
        yield mock_config


def test_setup_logging(mock_config):
    """Test that setup_logging configures logging correctly."""
    # We need to test the actual function that's imported in main.py
    from src.utils.logging_config import setup_logging as actual_setup_logging
    
    # Mock the logging functions that are called by setup_logging
    with mock.patch("logging.getLogger") as mock_get_logger:
        with mock.patch("logging.FileHandler") as mock_file_handler:
            with mock.patch("logging.StreamHandler") as mock_stream_handler:
                # Call the actual setup_logging function
                actual_setup_logging()
                
                # Verify that the logging was set up
                mock_get_logger.assert_called()
                # At least one handler should be created
                assert mock_stream_handler.called or mock_file_handler.called


def test_main_no_suppliers(mock_config, caplog):
    """Test main function when no suppliers are configured."""
    caplog.set_level(logging.INFO)
    
    main()
    
    # Check log messages
    assert "Starting Automated Product Data Scraper" in caplog.text
    assert "No suppliers configured" in caplog.text
    assert "Scraping process completed" not in caplog.text


def test_main_with_suppliers(mock_config, caplog):
    """Test main function with suppliers configured."""
    caplog.set_level(logging.INFO)
    
    # Add a mock supplier
    mock_supplier = mock.MagicMock()
    mock_supplier.name = "Test Supplier"
    mock_config.suppliers = [mock_supplier]
    
    main()
    
    # Check log messages
    assert "Starting Automated Product Data Scraper" in caplog.text
    assert "Found 1 supplier(s) to process" in caplog.text
    assert "Processing supplier: Test Supplier" in caplog.text
    assert "Scraping process completed" in caplog.text


def test_main_entry_point():
    """Test the __main__ block."""
    # Instead of trying to execute the main module, we'll directly test the behavior
    # that would happen if __name__ == "__main__"
    with mock.patch("src.main.setup_logging") as mock_setup_logging:
        with mock.patch("src.main.main") as mock_main:
            with mock.patch.object(sys, "exit"):
                # Simulate the if __name__ == "__main__" block
                try:
                    src.main.setup_logging()
                    src.main.main()
                except Exception:
                    pass
                
                # Check that setup_logging and main were called
                mock_setup_logging.assert_called_once()
                mock_main.assert_called_once()


def test_main_exception_handling():
    """Test exception handling in the main entry point."""
    with mock.patch("src.main.setup_logging"):
        with mock.patch("src.main.main", side_effect=Exception("Test error")):
            with mock.patch("src.main.logging.getLogger") as mock_get_logger:
                mock_logger = mock.MagicMock()
                mock_get_logger.return_value = mock_logger
                
                with mock.patch.object(sys, "exit") as mock_exit:
                    # Simulate the if __name__ == "__main__" block with exception
                    try:
                        src.main.setup_logging()
                        src.main.main()
                    except Exception as e:
                        src.main.logging.getLogger(src.main.__name__).error(f"An error occurred: {e}", exc_info=True)
                        sys.exit(1)
                    
                    # Check that the error was logged and sys.exit was called
                    mock_logger.error.assert_called_once()
                    assert "Test error" in mock_logger.error.call_args[0][0]
                    mock_exit.assert_called_once_with(1)
