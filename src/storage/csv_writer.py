"""
CSV Writer module for the Automated Product Data Scraper.

This module provides the CSVWriter class for efficiently writing scraped data
to CSV files with proper UTF-8 encoding and streaming support.
"""

import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)


class CSVWriter:
    """
    Handles writing scraped data to CSV files with proper encoding and streaming.
    
    This class manages the creation of output directories, file naming,
    and efficient writing of data rows to CSV files.
    """
    
    def __init__(
        self,
        output_path: str,
        filename_pattern: Optional[str] = None,
        supplier_name: Optional[str] = None,
        include_timestamp: bool = True,
        encoding: str = 'utf-8',
        newline: str = '',
    ):
        """
        Initialize the CSVWriter.
        
        Args:
            output_path: Directory path where CSV files will be saved
            filename_pattern: Pattern for the filename (default: "{supplier}_{timestamp}.csv")
            supplier_name: Name of the supplier (used in filename if provided)
            include_timestamp: Whether to include a timestamp in the filename
            encoding: File encoding (default: 'utf-8')
            newline: Newline character(s) to use (default: '' - platform specific)
        """
        self.output_path = os.path.abspath(output_path)
        self.filename_pattern = filename_pattern or "{supplier}_{timestamp}.csv"
        self.supplier_name = supplier_name or "data"
        self.include_timestamp = include_timestamp
        self.encoding = encoding
        self.newline = newline
        self.file = None
        self.writer = None
        self.headers = None
        self.filename = None
        
    def __enter__(self):
        """Context manager entry point - opens the file."""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - closes the file."""
        self.close()
        
    def _generate_filename(self) -> str:
        """
        Generate a filename based on the pattern, supplier, and timestamp.
        
        Returns:
            str: The generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if self.include_timestamp else ""
        return self.filename_pattern.format(
            supplier=self.supplier_name,
            timestamp=timestamp
        )
        
    def open(self) -> 'CSVWriter':
        """
        Open the CSV file for writing, creating the output directory if needed.
        
        Returns:
            CSVWriter: Self for method chaining
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_path, exist_ok=True)
            
            # Generate filename
            self.filename = self._generate_filename()
            
            # Create full path
            filepath = os.path.join(self.output_path, self.filename)
            
            # Open file with proper encoding
            self.file = open(filepath, 'w', encoding=self.encoding, newline=self.newline)
            logger.info(f"Opened CSV file for writing: {filepath}")
            
            return self
        except Exception as e:
            logger.error(f"Error opening CSV file: {str(e)}")
            raise
            
    def write_header(self, headers: List[str]) -> None:
        """
        Write the header row to the CSV file.
        
        Args:
            headers: List of column headers
        
        Raises:
            ValueError: If the file is not open
        """
        if not self.file:
            raise ValueError("File is not open. Call open() first or use with statement.")
            
        try:
            self.headers = headers
            self.writer = csv.DictWriter(self.file, fieldnames=headers)
            self.writer.writeheader()
            logger.debug(f"Wrote CSV header: {headers}")
        except Exception as e:
            logger.error(f"Error writing CSV header: {str(e)}")
            raise
            
    def write_row(self, data: Dict[str, Any]) -> None:
        """
        Write a single data row to the CSV file.
        
        Args:
            data: Dictionary mapping column names to values
        
        Raises:
            ValueError: If the file is not open or headers are not set
        """
        if not self.file:
            raise ValueError("File is not open. Call open() first or use with statement.")
            
        if not self.writer:
            raise ValueError("Headers not set. Call write_header() first.")
            
        try:
            self.writer.writerow(data)
        except Exception as e:
            logger.error(f"Error writing CSV row: {str(e)}")
            raise
            
    def write_rows(self, data_rows: List[Dict[str, Any]]) -> None:
        """
        Write multiple data rows to the CSV file.
        
        Args:
            data_rows: List of dictionaries mapping column names to values
        
        Raises:
            ValueError: If the file is not open or headers are not set
        """
        if not self.file:
            raise ValueError("File is not open. Call open() first or use with statement.")
            
        if not self.writer:
            raise ValueError("Headers not set. Call write_header() first.")
            
        try:
            self.writer.writerows(data_rows)
            logger.debug(f"Wrote {len(data_rows)} rows to CSV")
        except Exception as e:
            logger.error(f"Error writing CSV rows: {str(e)}")
            raise
            
    def close(self) -> None:
        """Close the CSV file if it's open."""
        if self.file:
            try:
                self.file.close()
                logger.info(f"Closed CSV file: {self.filename}")
                self.file = None
                self.writer = None
            except Exception as e:
                logger.error(f"Error closing CSV file: {str(e)}")
                raise
