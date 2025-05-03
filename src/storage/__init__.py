"""
Storage module for the Automated Product Data Scraper.

This module contains components for storing scraped data, including:
- CSVWriter: Handles writing data to CSV files with proper encoding and streaming
- ImageHandler: Handles product images by either saving URLs or downloading files
"""

from src.storage.csv_writer import CSVWriter
from src.storage.image_handler import ImageHandler

__all__ = ['CSVWriter', 'ImageHandler']
