"""
Notification manager module for the Automated Product Data Scraper.

This module provides a manager for sending notifications through multiple channels.
It coordinates sending notifications to different notifiers based on configuration.
"""

import logging
import datetime
from typing import Dict, List, Optional, Any, Union

# Try both import paths to handle different execution contexts
try:
    from src.notifications.base_notifier import BaseNotifier
    from src.notifications.factory import factory, create_notifiers_from_config
except ModuleNotFoundError:
    from notifications.base_notifier import BaseNotifier
    from notifications.factory import factory, create_notifiers_from_config


class NotificationManager:
    """
    Manager for sending notifications through multiple channels.
    
    This class coordinates sending notifications to different notifiers
    based on configuration. It provides a single interface for sending
    notifications regardless of the underlying notification channels.
    
    Attributes:
        notifiers: A dictionary of notifier instances.
        logger: A logger instance for the notification manager.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the notification manager.
        
        Args:
            config: A dictionary containing notifier configurations.
        """
        self.logger = logging.getLogger(__name__)
        self.notifiers = {}
        
        # Create notifiers from configuration if provided
        if config:
            self.notifiers = create_notifiers_from_config(config)
            self.logger.info(f"Created {len(self.notifiers)} notifiers from configuration")
    
    def add_notifier(self, notifier: BaseNotifier) -> None:
        """
        Add a notifier to the manager.
        
        Args:
            notifier: The notifier instance to add.
        """
        self.notifiers[notifier.name] = notifier
        self.logger.info(f"Added notifier: {notifier.name}")
    
    def remove_notifier(self, name: str) -> bool:
        """
        Remove a notifier from the manager.
        
        Args:
            name: The name of the notifier to remove.
            
        Returns:
            bool: True if the notifier was removed, False otherwise.
        """
        if name in self.notifiers:
            del self.notifiers[name]
            self.logger.info(f"Removed notifier: {name}")
            return True
        
        self.logger.warning(f"Notifier not found: {name}")
        return False
    
    def get_notifier(self, name: str) -> Optional[BaseNotifier]:
        """
        Get a notifier by name.
        
        Args:
            name: The name of the notifier to get.
            
        Returns:
            BaseNotifier: The notifier instance, or None if not found.
        """
        if name in self.notifiers:
            return self.notifiers[name]
        
        self.logger.warning(f"Notifier not found: {name}")
        return None
    
    def send_completion_notification(self, 
                                    subject: str = "", 
                                    message: str = "", 
                                    notifier_names: Optional[List[str]] = None, 
                                    **kwargs) -> Dict[str, bool]:
        """
        Send a completion notification to specified notifiers.
        
        Args:
            subject: The subject of the notification.
            message: The message body of the notification.
            notifier_names: A list of notifier names to send the notification to.
                           If None, sends to all notifiers.
            **kwargs: Additional keyword arguments to pass to the notifiers.
            
        Returns:
            Dict[str, bool]: A dictionary mapping notifier names to success status.
        """
        results = {}
        
        # Determine which notifiers to use
        notifiers_to_use = self.notifiers
        if notifier_names:
            notifiers_to_use = {name: self.notifiers[name] for name in notifier_names if name in self.notifiers}
        
        # Send the notification to each notifier
        for name, notifier in notifiers_to_use.items():
            try:
                success = notifier.send_completion_notification(subject, message, **kwargs)
                results[name] = success
                
                if success:
                    self.logger.info(f"Sent completion notification via {name}")
                else:
                    self.logger.warning(f"Failed to send completion notification via {name}")
            except Exception as e:
                self.logger.error(f"Error sending completion notification via {name}: {e}", exc_info=True)
                results[name] = False
        
        return results
    
    def send_error_notification(self, 
                               subject: str = "", 
                               message: str = "", 
                               error: Optional[Exception] = None,
                               notifier_names: Optional[List[str]] = None, 
                               **kwargs) -> Dict[str, bool]:
        """
        Send an error notification to specified notifiers.
        
        Args:
            subject: The subject of the notification.
            message: The message body of the notification.
            error: The exception that occurred, if any.
            notifier_names: A list of notifier names to send the notification to.
                           If None, sends to all notifiers.
            **kwargs: Additional keyword arguments to pass to the notifiers.
            
        Returns:
            Dict[str, bool]: A dictionary mapping notifier names to success status.
        """
        results = {}
        
        # Determine which notifiers to use
        notifiers_to_use = self.notifiers
        if notifier_names:
            notifiers_to_use = {name: self.notifiers[name] for name in notifier_names if name in self.notifiers}
        
        # Send the notification to each notifier
        for name, notifier in notifiers_to_use.items():
            try:
                success = notifier.send_error_notification(subject, message, error, **kwargs)
                results[name] = success
                
                if success:
                    self.logger.info(f"Sent error notification via {name}")
                else:
                    self.logger.warning(f"Failed to send error notification via {name}")
            except Exception as e:
                self.logger.error(f"Error sending error notification via {name}: {e}", exc_info=True)
                results[name] = False
        
        return results
    
    def send_summary_notification(self, 
                                 subject: str = "", 
                                 summary_data: Optional[Dict[str, Any]] = None,
                                 notifier_names: Optional[List[str]] = None, 
                                 **kwargs) -> Dict[str, bool]:
        """
        Send a summary notification to specified notifiers.
        
        Args:
            subject: The subject of the notification.
            summary_data: A dictionary containing summary data about the scraping process.
            notifier_names: A list of notifier names to send the notification to.
                           If None, sends to all notifiers.
            **kwargs: Additional keyword arguments to pass to the notifiers.
            
        Returns:
            Dict[str, bool]: A dictionary mapping notifier names to success status.
        """
        results = {}
        
        # Use an empty dictionary if no summary data is provided
        if summary_data is None:
            summary_data = {}
        
        # Determine which notifiers to use
        notifiers_to_use = self.notifiers
        if notifier_names:
            notifiers_to_use = {name: self.notifiers[name] for name in notifier_names if name in self.notifiers}
        
        # Send the notification to each notifier
        for name, notifier in notifiers_to_use.items():
            try:
                success = notifier.send_summary_notification(subject, summary_data, **kwargs)
                results[name] = success
                
                if success:
                    self.logger.info(f"Sent summary notification via {name}")
                else:
                    self.logger.warning(f"Failed to send summary notification via {name}")
            except Exception as e:
                self.logger.error(f"Error sending summary notification via {name}: {e}", exc_info=True)
                results[name] = False
        
        return results


# Singleton instance of the notification manager
_manager = None


def get_notification_manager(config: Optional[Dict[str, Any]] = None) -> NotificationManager:
    """
    Get the singleton instance of the notification manager.
    
    Args:
        config: A dictionary containing notifier configurations.
        
    Returns:
        NotificationManager: The notification manager instance.
    """
    global _manager
    
    if _manager is None:
        _manager = NotificationManager(config)
    elif config:
        # If a new configuration is provided, create new notifiers
        new_notifiers = create_notifiers_from_config(config)
        for name, notifier in new_notifiers.items():
            _manager.add_notifier(notifier)
    
    return _manager
