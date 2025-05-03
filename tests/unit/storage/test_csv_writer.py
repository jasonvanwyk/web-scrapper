"""
Unit tests for the CSVWriter class.
"""

import os
import csv
import tempfile
import unittest
import shutil
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

import pytest

from src.storage.csv_writer import CSVWriter


class TestCSVWriter(unittest.TestCase):
    """Test cases for the CSVWriter class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_headers = ["product_name", "sku", "price", "image_url"]
        self.test_data = {
            "product_name": "Test Product",
            "sku": "TP123",
            "price": "99.99",
            "image_url": "http://example.com/image.jpg"
        }

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory using shutil.rmtree to handle subdirectories
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_values(self):
        """Test initialization with default values."""
        writer = CSVWriter(self.temp_dir)
        self.assertEqual(os.path.abspath(self.temp_dir), writer.output_path)
        self.assertEqual("{supplier}_{timestamp}.csv", writer.filename_pattern)
        self.assertEqual("data", writer.supplier_name)
        self.assertTrue(writer.include_timestamp)
        self.assertEqual("utf-8", writer.encoding)
        self.assertEqual("", writer.newline)

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        writer = CSVWriter(
            output_path=self.temp_dir,
            filename_pattern="custom_{supplier}.csv",
            supplier_name="test_supplier",
            include_timestamp=False,
            encoding="latin-1",
            newline="\n"
        )
        self.assertEqual(os.path.abspath(self.temp_dir), writer.output_path)
        self.assertEqual("custom_{supplier}.csv", writer.filename_pattern)
        self.assertEqual("test_supplier", writer.supplier_name)
        self.assertFalse(writer.include_timestamp)
        self.assertEqual("latin-1", writer.encoding)
        self.assertEqual("\n", writer.newline)

    def test_generate_filename(self):
        """Test filename generation."""
        # Test with timestamp
        writer = CSVWriter(
            output_path=self.temp_dir,
            supplier_name="test_supplier",
            include_timestamp=True
        )
        filename = writer._generate_filename()
        self.assertTrue(filename.startswith("test_supplier_"))
        self.assertTrue(filename.endswith(".csv"))
        
        # Test without timestamp
        writer = CSVWriter(
            output_path=self.temp_dir,
            supplier_name="test_supplier",
            include_timestamp=False
        )
        filename = writer._generate_filename()
        self.assertEqual("test_supplier_.csv", filename)
        
        # Test custom pattern
        writer = CSVWriter(
            output_path=self.temp_dir,
            filename_pattern="data_{supplier}.csv",
            supplier_name="test_supplier",
            include_timestamp=False
        )
        filename = writer._generate_filename()
        self.assertEqual("data_test_supplier.csv", filename)

    def test_context_manager(self):
        """Test using CSVWriter as a context manager."""
        with patch('builtins.open', mock_open()) as mock_file:
            with CSVWriter(self.temp_dir) as writer:
                self.assertIsNotNone(writer.file)
            mock_file().close.assert_called_once()

    def test_open_creates_directory(self):
        """Test that open() creates the output directory if it doesn't exist."""
        test_dir = os.path.join(self.temp_dir, "new_dir")
        writer = CSVWriter(test_dir)
        
        # Directory should not exist yet
        self.assertFalse(os.path.exists(test_dir))
        
        # Open should create the directory
        writer.open()
        self.assertTrue(os.path.exists(test_dir))
        
        # Clean up
        writer.close()

    def test_write_header(self):
        """Test writing header to CSV file."""
        # Use a real temporary file for this test
        temp_file = os.path.join(self.temp_dir, "test_header.csv")
        
        writer = CSVWriter(self.temp_dir)
        writer.filename = "test_header.csv"
        
        with patch('builtins.open', mock_open()) as mock_file:
            writer.file = mock_file()
            mock_csv_writer = MagicMock()
            
            with patch('csv.DictWriter', return_value=mock_csv_writer) as mock_dict_writer:
                writer.write_header(self.test_headers)
                
                # Check that DictWriter was created with correct parameters
                mock_dict_writer.assert_called_once_with(mock_file(), fieldnames=self.test_headers)
                
                # Check that writeheader was called
                mock_csv_writer.writeheader.assert_called_once()

    def test_write_row(self):
        """Test writing a single row to CSV file."""
        with patch('builtins.open', mock_open()) as mock_file:
            writer = CSVWriter(self.temp_dir)
            writer.file = mock_file()
            mock_csv_writer = MagicMock()
            writer.writer = mock_csv_writer
            
            writer.write_row(self.test_data)
            
            # Check that writerow was called with the correct data
            mock_csv_writer.writerow.assert_called_once_with(self.test_data)

    def test_write_rows(self):
        """Test writing multiple rows to CSV file."""
        with patch('builtins.open', mock_open()) as mock_file:
            writer = CSVWriter(self.temp_dir)
            writer.file = mock_file()
            mock_csv_writer = MagicMock()
            writer.writer = mock_csv_writer
            
            test_rows = [self.test_data, self.test_data]
            writer.write_rows(test_rows)
            
            # Check that writerows was called with the correct data
            mock_csv_writer.writerows.assert_called_once_with(test_rows)

    def test_error_handling(self):
        """Test error handling for various scenarios."""
        writer = CSVWriter(self.temp_dir)
        
        # Test writing header without opening file
        with self.assertRaises(ValueError):
            writer.write_header(self.test_headers)
        
        # Test writing row without opening file
        with self.assertRaises(ValueError):
            writer.write_row(self.test_data)
        
        # Test writing row without setting headers
        writer.file = MagicMock()
        with self.assertRaises(ValueError):
            writer.write_row(self.test_data)

    def test_integration(self):
        """Integration test for the full CSV writing process."""
        # Create a real CSV file
        writer = CSVWriter(
            output_path=self.temp_dir,
            filename_pattern="test_integration.csv",
            include_timestamp=False
        )
        
        with writer:
            writer.write_header(self.test_headers)
            writer.write_row(self.test_data)
            writer.write_row({
                "product_name": "Another Product",
                "sku": "AP456",
                "price": "199.99",
                "image_url": "http://example.com/another.jpg"
            })
        
        # Verify the file was created
        csv_path = os.path.join(self.temp_dir, "test_integration.csv")
        self.assertTrue(os.path.exists(csv_path))
        
        # Read the file and verify contents
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check number of rows
            self.assertEqual(2, len(rows))
            
            # Check first row content
            self.assertEqual("Test Product", rows[0]["product_name"])
            self.assertEqual("TP123", rows[0]["sku"])
            self.assertEqual("99.99", rows[0]["price"])
            self.assertEqual("http://example.com/image.jpg", rows[0]["image_url"])
            
            # Check second row content
            self.assertEqual("Another Product", rows[1]["product_name"])
            self.assertEqual("AP456", rows[1]["sku"])
            self.assertEqual("199.99", rows[1]["price"])
            self.assertEqual("http://example.com/another.jpg", rows[1]["image_url"])

    def test_utf8_encoding(self):
        """Test that UTF-8 encoding is properly handled."""
        # Create a real CSV file with international characters
        writer = CSVWriter(
            output_path=self.temp_dir,
            filename_pattern="test_utf8.csv",
            include_timestamp=False
        )
        
        test_data = {
            "product_name": "Café Français",  # Contains non-ASCII characters
            "sku": "CF789",
            "price": "€29.99",  # Euro symbol
            "image_url": "http://example.com/café.jpg"
        }
        
        with writer:
            writer.write_header(self.test_headers)
            writer.write_row(test_data)
        
        # Verify the file was created
        csv_path = os.path.join(self.temp_dir, "test_utf8.csv")
        self.assertTrue(os.path.exists(csv_path))
        
        # Read the file and verify contents
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check that international characters were preserved
            self.assertEqual("Café Français", rows[0]["product_name"])
            self.assertEqual("€29.99", rows[0]["price"])


if __name__ == '__main__':
    unittest.main()
