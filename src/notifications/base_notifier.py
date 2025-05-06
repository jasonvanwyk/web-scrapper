"""
Base notifier module for the Automated Product Data Scraper.

This module defines the BaseNotifier abstract base class that all concrete notifier
implementations must inherit from. It establishes a standard interface for all notifiers,
ensuring consistency across different notification methods.
"""

import abc
import logging
from typing import Dict, List, Optional, Any, Union


class BaseNotifier(abc.ABC):
    """
    Abstract base class for all notifiers.
    
    This class defines the interface that all concrete notifier implementations
    must adhere to. It includes abstract methods for sending different types of
    notifications.
    
    Attributes:
        logger: A logger instance for the notifier.
        name: The name of the notifier.
    """
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize the base notifier.
        
        Args:
            name: The name of the notifier.
            **kwargs: Additional keyword arguments for specific notifier implementations.
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initializing {self.__class__.__name__} notifier")
    
    @abc.abstractmethod
    def send_completion_notification(self, 
                                    subject: str, 
                                    message: str, 
                                    **kwargs) -> bool:
        """
        Send a notification when the scraper completes successfully.
        
        Args:
            subject: The subject of the notification.
            message: The message body of the notification.
            **kwargs: Additional keyword arguments for specific notifier implementations.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def send_error_notification(self, 
                               subject: str, 
                               message: str, 
                               error: Optional[Exception] = None, 
                               **kwargs) -> bool:
        """
        Send a notification when an error occurs during scraping.
        
        Args:
            subject: The subject of the notification.
            message: The message body of the notification.
            error: The exception that occurred, if any.
            **kwargs: Additional keyword arguments for specific notifier implementations.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        pass
    
    @abc.abstractmethod
    def send_summary_notification(self, 
                                 subject: str, 
                                 summary_data: Dict[str, Any], 
                                 **kwargs) -> bool:
        """
        Send a summary notification with details about the scraping process.
        
        Args:
            subject: The subject of the notification.
            summary_data: A dictionary containing summary data about the scraping process.
            **kwargs: Additional keyword arguments for specific notifier implementations.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        pass
    
    def format_summary(self, summary_data: Dict[str, Any]) -> str:
        """
        Format summary data into a human-readable message.
        
        Args:
            summary_data: A dictionary containing summary data about the scraping process.
            
        Returns:
            str: A formatted message containing the summary data.
        """
        # Start with a header
        message = "Scraper Execution Summary\n"
        message += "========================\n\n"
        
        # Add execution time information if available
        if "start_time" in summary_data and "end_time" in summary_data:
            message += f"Start Time: {summary_data['start_time']}\n"
            message += f"End Time: {summary_data['end_time']}\n"
            
            if "duration" in summary_data:
                message += f"Duration: {summary_data['duration']}\n"
            
            message += "\n"
        
        # Add supplier information if available
        if "suppliers" in summary_data:
            message += "Supplier Results:\n"
            message += "-----------------\n"
            
            for supplier in summary_data["suppliers"]:
                message += f"\n- {supplier['name']}:\n"
                message += f"  Status: {supplier['status']}\n"
                
                if "products_found" in supplier:
                    message += f"  Products Found: {supplier['products_found']}\n"
                
                if "products_processed" in supplier:
                    message += f"  Products Processed: {supplier['products_processed']}\n"
                
                if "errors" in supplier and supplier["errors"]:
                    message += f"  Errors: {len(supplier['errors'])}\n"
                    for error in supplier["errors"][:3]:  # Show only the first 3 errors
                        message += f"    - {error}\n"
                    
                    if len(supplier["errors"]) > 3:
                        message += f"    - ... and {len(supplier['errors']) - 3} more\n"
        
        # Add overall statistics if available
        if "total_products" in summary_data:
            message += "\nOverall Statistics:\n"
            message += "-------------------\n"
            message += f"Total Products: {summary_data['total_products']}\n"
            
            if "successful_products" in summary_data:
                message += f"Successfully Processed: {summary_data['successful_products']}\n"
            
            if "failed_products" in summary_data:
                message += f"Failed to Process: {summary_data['failed_products']}\n"
            
            if "total_suppliers" in summary_data:
                message += f"Total Suppliers: {summary_data['total_suppliers']}\n"
            
            if "successful_suppliers" in summary_data:
                message += f"Successful Suppliers: {summary_data['successful_suppliers']}\n"
            
            if "failed_suppliers" in summary_data:
                message += f"Failed Suppliers: {summary_data['failed_suppliers']}\n"
        
        # Add output information if available
        if "output_files" in summary_data and summary_data["output_files"]:
            message += "\nOutput Files:\n"
            message += "-------------\n"
            
            for output_file in summary_data["output_files"]:
                message += f"- {output_file}\n"
        
        return message
    
    def __str__(self) -> str:
        """Return a string representation of the notifier."""
        return f"{self.__class__.__name__}(name={self.name})"
