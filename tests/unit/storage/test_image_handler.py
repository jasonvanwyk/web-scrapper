"""
Unit tests for the ImageHandler class.
"""

import os
import tempfile
import unittest
import shutil
from unittest.mock import patch, mock_open, MagicMock, ANY

import pytest
import requests

from src.storage.image_handler import ImageHandler


class TestImageHandler(unittest.TestCase):
    """Test cases for the ImageHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://example.com/image.jpg"
        self.test_product_data = {
            "product_name": "Test Product",
            "sku": "TP123",
            "price": "99.99",
            "image_url": self.test_url
        }

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory using shutil.rmtree to handle subdirectories
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_values(self):
        """Test initialization with default values."""
        handler = ImageHandler(self.temp_dir)
        self.assertEqual(os.path.abspath(self.temp_dir), handler.output_path)
        self.assertFalse(handler.download_images)
        self.assertEqual("{sku}_{timestamp}.{ext}", handler.filename_pattern)
        self.assertEqual("product", handler.supplier_name)
        self.assertFalse(handler.include_timestamp)
        self.assertTrue(handler.include_sku)
        self.assertEqual(30, handler.timeout)
        self.assertEqual(8192, handler.chunk_size)

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        handler = ImageHandler(
            output_path=self.temp_dir,
            download_images=True,
            filename_pattern="custom_{supplier}_{sku}.{ext}",
            supplier_name="test_supplier",
            include_timestamp=True,
            include_sku=False,
            timeout=60,
            chunk_size=4096
        )
        self.assertEqual(os.path.abspath(self.temp_dir), handler.output_path)
        self.assertTrue(handler.download_images)
        self.assertEqual("custom_{supplier}_{sku}.{ext}", handler.filename_pattern)
        self.assertEqual("test_supplier", handler.supplier_name)
        self.assertTrue(handler.include_timestamp)
        self.assertFalse(handler.include_sku)
        self.assertEqual(60, handler.timeout)
        self.assertEqual(4096, handler.chunk_size)

    def test_context_manager(self):
        """Test using ImageHandler as a context manager."""
        with patch('requests.Session') as mock_session:
            # Set download_images to True to test session creation
            with ImageHandler(self.temp_dir, download_images=True) as handler:
                self.assertIsNotNone(handler.session)
            # Check that session.close was called
            mock_session.return_value.close.assert_called_once()

    def test_url_only_mode(self):
        """Test URL-only mode (no downloading)."""
        handler = ImageHandler(self.temp_dir, download_images=False)
        result = handler.handle_image(self.test_url, self.test_product_data)
        
        # Should return the original URL
        self.assertEqual(self.test_url, result)
        
        # No session should be created
        self.assertIsNone(handler.session)

    def test_empty_url_handling(self):
        """Test handling of empty URLs."""
        handler = ImageHandler(self.temp_dir, download_images=True)
        result = handler.handle_image("", self.test_product_data)
        
        # Should return an empty string
        self.assertEqual("", result)

    def test_generate_filename(self):
        """Test filename generation."""
        # Test with SKU and without timestamp
        handler = ImageHandler(
            output_path=self.temp_dir,
            supplier_name="test_supplier",
            include_timestamp=False,
            include_sku=True
        )
        filename = handler._generate_filename(self.test_url, self.test_product_data)
        self.assertEqual("TP123_.jpg", filename)
        
        # Test with SKU and with timestamp
        handler = ImageHandler(
            output_path=self.temp_dir,
            supplier_name="test_supplier",
            include_timestamp=True,
            include_sku=True
        )
        filename = handler._generate_filename(self.test_url, self.test_product_data)
        # Check that filename contains SKU and has timestamp format
        self.assertTrue(filename.startswith("TP123_"))
        self.assertTrue(filename.endswith(".jpg"))
        
        # Test with custom pattern
        handler = ImageHandler(
            output_path=self.temp_dir,
            filename_pattern="{supplier}_{sku}.{ext}",
            supplier_name="test_supplier",
            include_sku=True
        )
        filename = handler._generate_filename(self.test_url, self.test_product_data)
        self.assertEqual("test_supplier_TP123.jpg", filename)
        
        # Test without SKU (should generate hash-based name)
        handler = ImageHandler(
            output_path=self.temp_dir,
            include_sku=True
        )
        filename = handler._generate_filename(self.test_url, {})  # No SKU in data
        self.assertTrue(filename.startswith("img_"))
        self.assertTrue(filename.endswith(".jpg"))
        
        # Test with different URL extensions
        handler = ImageHandler(self.temp_dir)
        filename = handler._generate_filename("https://example.com/image.png", self.test_product_data)
        self.assertTrue(filename.endswith(".png"))
        
        filename = handler._generate_filename("https://example.com/image.PNG", self.test_product_data)
        self.assertTrue(filename.endswith(".png"))  # Should be lowercase
        
        filename = handler._generate_filename("https://example.com/image", self.test_product_data)
        self.assertTrue(filename.endswith(".jpg"))  # Default extension

    @patch('requests.Session')
    def test_download_image_success(self, mock_session):
        """Test successful image download."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_response.iter_content.return_value = [b'test image data']
        
        # Configure the mock session
        mock_session.return_value.get.return_value.__enter__.return_value = mock_response
        
        # Create handler and download image
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.session = mock_session.return_value
        
        with patch('builtins.open', mock_open()) as mock_file:
            filepath = handler._download_image(self.test_url, self.test_product_data)
            
            # Check that the URL was requested
            mock_session.return_value.get.assert_called_once_with(
                self.test_url, stream=True, timeout=30
            )
            
            # Check that the file was written
            mock_file.return_value.write.assert_called_once_with(b'test image data')
            
            # Check that the filepath was returned
            self.assertTrue(filepath.startswith(self.temp_dir))
            self.assertTrue("TP123_" in filepath)

    @patch('requests.Session')
    def test_download_image_http_error(self, mock_session):
        """Test handling of HTTP errors during download."""
        # Mock the response to raise an exception
        mock_session.return_value.get.return_value.__enter__.side_effect = \
            requests.exceptions.HTTPError("404 Client Error")
        
        # Create handler and attempt download
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.session = mock_session.return_value
        
        with self.assertRaises(IOError):
            handler._download_image(self.test_url, self.test_product_data)

    @patch('requests.Session')
    def test_download_image_connection_error(self, mock_session):
        """Test handling of connection errors during download."""
        # Mock the response to raise an exception
        mock_session.return_value.get.return_value.__enter__.side_effect = \
            requests.exceptions.ConnectionError("Connection refused")
        
        # Create handler and attempt download
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.session = mock_session.return_value
        
        with self.assertRaises(IOError):
            handler._download_image(self.test_url, self.test_product_data)

    @patch('requests.Session')
    def test_download_image_timeout(self, mock_session):
        """Test handling of timeout errors during download."""
        # Mock the response to raise an exception
        mock_session.return_value.get.return_value.__enter__.side_effect = \
            requests.exceptions.Timeout("Request timed out")
        
        # Create handler and attempt download
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.session = mock_session.return_value
        
        with self.assertRaises(IOError):
            handler._download_image(self.test_url, self.test_product_data)

    @patch('requests.Session')
    def test_handle_image_with_error(self, mock_session):
        """Test that handle_image returns the original URL when download fails."""
        # Mock the response to raise an exception
        mock_session.return_value.get.return_value.__enter__.side_effect = \
            requests.exceptions.RequestException("Download failed")
        
        # Create handler and attempt download
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.session = mock_session.return_value
        
        # Should return the original URL when download fails
        result = handler.handle_image(self.test_url, self.test_product_data)
        self.assertEqual(self.test_url, result)

    @patch('os.makedirs')
    def test_directory_creation(self, mock_makedirs):
        """Test that directories are created when needed."""
        # Test with download_images=True
        handler = ImageHandler(self.temp_dir, download_images=True)
        handler.open()
        
        # Check that makedirs was called
        mock_makedirs.assert_called_once_with(self.temp_dir, exist_ok=True)

    def test_non_image_content_type_warning(self):
        """Test warning when content type is not an image."""
        with patch('requests.Session') as mock_session:
            # Mock the response with non-image content type
            mock_response = MagicMock()
            mock_response.headers = {'Content-Type': 'text/html'}
            mock_response.iter_content.return_value = [b'<html>Not an image</html>']
            
            # Configure the mock session
            mock_session.return_value.get.return_value.__enter__.return_value = mock_response
            
            # Create handler and download image
            handler = ImageHandler(self.temp_dir, download_images=True)
            handler.session = mock_session.return_value
            
            with patch('builtins.open', mock_open()):
                with self.assertLogs(level='WARNING') as log:
                    handler._download_image(self.test_url, self.test_product_data)
                    
                    # Check that a warning was logged
                    self.assertTrue(any("non-image content type" in msg for msg in log.output))


if __name__ == '__main__':
    unittest.main()
