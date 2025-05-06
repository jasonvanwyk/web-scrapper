"""
Tests for the StorageConfig module.

This module tests the functionality of the StorageConfig class, ensuring
proper directory creation, file path handling, and permission management.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.storage.storage_config import StorageConfig, StorageBackend


class TestStorageConfig(unittest.TestCase):
    """Test cases for the StorageConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_directory_creation(self):
        """Test that directories are created correctly."""
        # Create a storage config with subdirectories
        base_path = os.path.join(self.temp_dir, "output")
        csv_subdir = "csv_files"
        image_subdir = "images"
        
        storage_config = StorageConfig(
            base_path=base_path,
            csv_subdir=csv_subdir,
            image_subdir=image_subdir,
            create_dirs=True
        )
        
        # Check that directories were created
        self.assertTrue(os.path.exists(base_path))
        self.assertTrue(os.path.exists(os.path.join(base_path, csv_subdir)))
        self.assertTrue(os.path.exists(os.path.join(base_path, image_subdir)))
    
    def test_file_paths(self):
        """Test that file paths are generated correctly."""
        # Create a storage config
        base_path = os.path.join(self.temp_dir, "output")
        csv_subdir = "csv_files"
        image_subdir = "images"
        
        storage_config = StorageConfig(
            base_path=base_path,
            csv_subdir=csv_subdir,
            image_subdir=image_subdir
        )
        
        # Test CSV file path
        csv_filename = "products.csv"
        csv_path = storage_config.get_csv_filepath(csv_filename)
        expected_csv_path = Path(base_path) / csv_subdir / csv_filename
        self.assertEqual(csv_path, expected_csv_path)
        
        # Test image file path
        image_filename = "product.jpg"
        image_path = storage_config.get_image_filepath(image_filename)
        expected_image_path = Path(base_path) / image_subdir / image_filename
        self.assertEqual(image_path, expected_image_path)
    
    def test_permissions(self):
        """Test that file permissions are set correctly."""
        # Skip on non-POSIX systems
        if os.name != 'posix':
            self.skipTest("File permission tests only run on POSIX systems")
        
        # Create a storage config with permissions
        base_path = os.path.join(self.temp_dir, "output")
        file_permissions = 0o644  # rw-r--r--
        dir_permissions = 0o755   # rwxr-xr-x
        
        storage_config = StorageConfig(
            base_path=base_path,
            file_permissions=file_permissions,
            dir_permissions=dir_permissions
        )
        
        # Check directory permissions
        self.assertEqual(os.stat(base_path).st_mode & 0o777, dir_permissions)
        
        # Create a test file and set permissions
        test_file = os.path.join(base_path, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        storage_config.set_file_permissions(test_file)
        
        # Check file permissions
        self.assertEqual(os.stat(test_file).st_mode & 0o777, file_permissions)
    
    def test_from_config(self):
        """Test creating StorageConfig from an OutputConfig object."""
        # Create a mock OutputConfig
        class MockOutputConfig:
            def __init__(self, temp_dir):
                self.output_dir = Path(os.path.join(temp_dir, "output"))
                self.download_images = True
        
        mock_config = MockOutputConfig(self.temp_dir)
        
        # Create StorageConfig from the mock config
        storage_config = StorageConfig.from_config(mock_config)
        
        # Check that paths are set correctly
        self.assertEqual(storage_config.base_path, mock_config.output_dir)
        self.assertEqual(storage_config.image_path, mock_config.output_dir / "images")


if __name__ == '__main__':
    unittest.main()
