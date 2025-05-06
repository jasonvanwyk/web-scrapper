"""
Storage Configuration module for the Automated Product Data Scraper.

This module provides a unified interface for configuring and managing storage locations
for different output types (CSV files, images) with support for various storage backends.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from enum import Enum

logger = logging.getLogger(__name__)


class StorageBackend(str, Enum):
    """Enum for supported storage backends."""
    LOCAL = "local"
    S3 = "s3"  # Placeholder for future implementation


class StorageConfig:
    """
    Configuration for output storage with support for different backends.
    
    This class provides a unified interface for configuring and managing storage
    locations for different output types (CSV files, images) with proper
    permission handling and directory creation.
    """
    
    def __init__(
        self,
        base_path: Union[str, Path],
        storage_backend: StorageBackend = StorageBackend.LOCAL,
        csv_subdir: Optional[str] = None,
        image_subdir: Optional[str] = None,
        create_dirs: bool = True,
        file_permissions: Optional[int] = None,
        dir_permissions: Optional[int] = None,
    ):
        """
        Initialize the storage configuration.
        
        Args:
            base_path: Base directory for all output files
            storage_backend: Storage backend to use (local, s3, etc.)
            csv_subdir: Subdirectory for CSV files (relative to base_path)
            image_subdir: Subdirectory for image files (relative to base_path)
            create_dirs: Whether to create directories if they don't exist
            file_permissions: Unix permissions for created files (e.g., 0o644)
            dir_permissions: Unix permissions for created directories (e.g., 0o755)
        """
        self.base_path = Path(base_path) if isinstance(base_path, str) else base_path
        self.storage_backend = storage_backend
        self.csv_subdir = csv_subdir
        self.image_subdir = image_subdir
        self.create_dirs = create_dirs
        self.file_permissions = file_permissions
        self.dir_permissions = dir_permissions
        
        # Initialize paths
        self.csv_path = self._get_csv_path()
        self.image_path = self._get_image_path()
        
        # Create directories if needed
        if self.create_dirs:
            self._create_directories()
    
    def _get_csv_path(self) -> Path:
        """
        Get the full path for CSV files.
        
        Returns:
            Path: Full path for CSV files
        """
        if self.csv_subdir:
            return self.base_path / self.csv_subdir
        return self.base_path
    
    def _get_image_path(self) -> Path:
        """
        Get the full path for image files.
        
        Returns:
            Path: Full path for image files
        """
        if self.image_subdir:
            return self.base_path / self.image_subdir
        return self.base_path
    
    def _create_directories(self) -> None:
        """Create necessary directories with proper permissions."""
        try:
            # Create base directory
            self._create_directory(self.base_path)
            
            # Create CSV directory if different from base
            if self.csv_subdir:
                self._create_directory(self.csv_path)
                
            # Create image directory if different from base
            if self.image_subdir:
                self._create_directory(self.image_path)
                
            logger.info(f"Storage directories created/verified: {self.base_path}")
        except Exception as e:
            logger.error(f"Error creating storage directories: {str(e)}")
            raise
    
    def _create_directory(self, path: Path) -> None:
        """
        Create a directory with proper permissions.
        
        Args:
            path: Directory path to create
        """
        path.mkdir(parents=True, exist_ok=True)
        
        # Set directory permissions if specified
        if self.dir_permissions is not None and os.name == 'posix':
            try:
                os.chmod(path, self.dir_permissions)
                logger.debug(f"Set permissions {oct(self.dir_permissions)} on {path}")
            except Exception as e:
                logger.warning(f"Could not set permissions on {path}: {str(e)}")
    
    def get_csv_filepath(self, filename: str) -> Path:
        """
        Get the full path for a CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Path: Full path to the CSV file
        """
        return self.csv_path / filename
    
    def get_image_filepath(self, filename: str) -> Path:
        """
        Get the full path for an image file.
        
        Args:
            filename: Name of the image file
            
        Returns:
            Path: Full path to the image file
        """
        return self.image_path / filename
    
    def set_file_permissions(self, filepath: Path) -> None:
        """
        Set permissions on a file.
        
        Args:
            filepath: Path to the file
        """
        if self.file_permissions is not None and os.name == 'posix':
            try:
                os.chmod(filepath, self.file_permissions)
                logger.debug(f"Set permissions {oct(self.file_permissions)} on {filepath}")
            except Exception as e:
                logger.warning(f"Could not set permissions on {filepath}: {str(e)}")
    
    @classmethod
    def from_config(cls, config):
        """
        Create a StorageConfig instance from an OutputConfig object.
        
        Args:
            config: OutputConfig instance from the app configuration
            
        Returns:
            StorageConfig: Configured storage instance
        """
        return cls(
            base_path=config.output_dir,
            csv_subdir=None,  # Use output_dir directly
            image_subdir="images" if config.download_images else None,
            create_dirs=True,
            file_permissions=0o644,  # rw-r--r--
            dir_permissions=0o755,   # rwxr-xr-x
        )
