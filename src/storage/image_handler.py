"""
Image Handler module for the Automated Product Data Scraper.

This module provides the ImageHandler class for handling product images,
either by saving the URL or downloading the actual image file based on configuration.
"""

import os
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse, unquote

try:
    from src.storage.storage_config import StorageConfig
except ImportError:
    # When running from src directory
    from storage.storage_config import StorageConfig

logger = logging.getLogger(__name__)


class ImageHandler:
    """
    Handles product images based on configuration.
    
    This class can either save the image URL or download the actual image file
    based on the provided configuration. It manages output directories, file naming,
    and error handling for image downloads.
    """
    
    def __init__(
        self,
        output_path: Union[str, Path, StorageConfig],
        download_images: bool = False,
        filename_pattern: Optional[str] = None,
        supplier_name: Optional[str] = None,
        include_timestamp: bool = False,
        include_sku: bool = True,
        timeout: int = 30,
        chunk_size: int = 8192,
    ):
        """
        Initialize the ImageHandler.
        
        Args:
            output_path: Directory path where images will be saved or a StorageConfig instance
            download_images: Whether to download images (True) or just return URLs (False)
            filename_pattern: Pattern for the filename (default: "{sku}_{timestamp}.{ext}")
            supplier_name: Name of the supplier (used in filename if provided)
            include_timestamp: Whether to include a timestamp in the filename
            include_sku: Whether to include the SKU in the filename
            timeout: Timeout for image download requests in seconds
            chunk_size: Chunk size for streaming downloads in bytes
        """
        # Handle different output_path types
        if isinstance(output_path, StorageConfig):
            self.storage_config = output_path
            self.output_path = str(self.storage_config.image_path)
        else:
            self.storage_config = None
            self.output_path = os.path.abspath(str(output_path))
            
        self.download_images = download_images
        self.filename_pattern = filename_pattern or "{sku}_{timestamp}.{ext}"
        self.supplier_name = supplier_name or "product"
        self.include_timestamp = include_timestamp
        self.include_sku = include_sku
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.session = None
        
    def __enter__(self):
        """Context manager entry point - initializes the session."""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - closes the session."""
        self.close()
        
    def open(self) -> 'ImageHandler':
        """
        Initialize the requests session for downloading images.
        
        Returns:
            ImageHandler: Self for method chaining
        """
        if self.download_images:
            self.session = requests.Session()
            logger.debug("Initialized requests session for image downloads")
            
            # Create output directory if needed
            if self.storage_config:
                # Directory creation is handled by StorageConfig
                pass
            else:
                # Create output directory if it doesn't exist
                os.makedirs(self.output_path, exist_ok=True)
                logger.debug(f"Created output directory: {self.output_path}")
                
        return self
        
    def close(self) -> None:
        """Close the requests session if it's open."""
        if self.session:
            self.session.close()
            self.session = None
            logger.debug("Closed requests session")
            
    def handle_image(self, image_url: str, product_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle an image URL based on configuration.
        
        If download_images is False, simply returns the original URL.
        If download_images is True, downloads the image and returns the local file path.
        
        Args:
            image_url: URL of the image to handle
            product_data: Optional dictionary containing product data (used for filename generation)
                          Should contain 'sku' if include_sku is True
        
        Returns:
            str: Either the original URL (if download_images is False) or the local file path
        
        Raises:
            ValueError: If image_url is empty or invalid
            IOError: If there's an error downloading or saving the image
        """
        if not image_url:
            logger.warning("Empty image URL provided")
            return ""
            
        # If we're not downloading images, just return the URL
        if not self.download_images:
            logger.debug(f"URL-only mode, returning original URL: {image_url}")
            return image_url
            
        # Ensure the session is initialized
        if not self.session:
            self.open()
            
        try:
            # Download and save the image
            local_path = self._download_image(image_url, product_data)
            logger.info(f"Downloaded image from {image_url} to {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"Error handling image {image_url}: {str(e)}")
            # Return the original URL as a fallback
            return image_url
            
    def _generate_filename(self, image_url: str, product_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a filename for the downloaded image.
        
        Args:
            image_url: URL of the image
            product_data: Optional dictionary containing product data
        
        Returns:
            str: The generated filename
        """
        # Extract original filename and extension from URL
        parsed_url = urlparse(image_url)
        original_filename = os.path.basename(unquote(parsed_url.path))
        _, ext = os.path.splitext(original_filename)
        
        # Default extension if none found
        ext = ext.lower() if ext else ".jpg"
        # Remove the leading dot if present
        ext = ext[1:] if ext.startswith(".") else ext
        
        # Get SKU from product data if available
        sku = ""
        if self.include_sku and product_data and 'sku' in product_data:
            sku = product_data['sku']
        elif self.include_sku:
            # Generate a simple hash from the URL if no SKU provided
            sku = f"img_{hash(image_url) % 10000:04d}"
            
        # Generate timestamp if needed
        timestamp = ""
        if self.include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # Generate the filename using the pattern
        return self.filename_pattern.format(
            supplier=self.supplier_name,
            sku=sku,
            timestamp=timestamp,
            ext=ext
        )
        
    def _download_image(self, image_url: str, product_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Download an image from a URL and save it to the output directory.
        
        Args:
            image_url: URL of the image to download
            product_data: Optional dictionary containing product data
        
        Returns:
            str: Path to the saved image file
        
        Raises:
            ValueError: If image_url is empty or invalid
            IOError: If there's an error downloading or saving the image
        """
        if not image_url:
            raise ValueError("Empty image URL provided")
            
        # Generate filename
        filename = self._generate_filename(image_url, product_data)
        
        # Get filepath based on storage configuration
        if self.storage_config:
            filepath = self.storage_config.get_image_filepath(filename)
        else:
            # Ensure the output directory exists
            os.makedirs(self.output_path, exist_ok=True)
            filepath = os.path.join(self.output_path, filename)
        
        # Download the image
        try:
            # Stream the download to handle large files efficiently
            with self.session.get(image_url, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                
                # Check content type to ensure it's an image
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"URL {image_url} returned non-image content type: {content_type}")
                
                # Save the image
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=self.chunk_size):
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)
                
                # Set file permissions if using StorageConfig
                if self.storage_config:
                    self.storage_config.set_file_permissions(filepath)
                            
            return str(filepath)
        except requests.RequestException as e:
            logger.error(f"Error downloading image from {image_url}: {str(e)}")
            raise IOError(f"Failed to download image: {str(e)}")
        except IOError as e:
            logger.error(f"Error saving image to {filepath}: {str(e)}")
            raise IOError(f"Failed to save image: {str(e)}")
