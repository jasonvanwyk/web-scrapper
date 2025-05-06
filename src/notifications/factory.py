"""
Notifier factory module for the Automated Product Data Scraper.

This module provides a factory for creating notifier instances based on
configuration. It dynamically loads the appropriate notifier module
and instantiates the correct notifier class.
"""

import logging
from typing import Dict, List, Optional, Any, Union

# Try both import paths to handle different execution contexts
try:
    from src.notifications.base_notifier import BaseNotifier
    from src.notifications.email_notifier import EmailNotifier
    from src.notifications.slack_notifier import SlackNotifier
except ModuleNotFoundError:
    from notifications.base_notifier import BaseNotifier
    from notifications.email_notifier import EmailNotifier
    from notifications.slack_notifier import SlackNotifier


class NotifierFactory:
    """
    Factory for creating notifier instances.
    
    This class is responsible for creating and managing notifier instances
    based on configuration.
    """
    
    def __init__(self):
        """Initialize the notifier factory."""
        self.logger = logging.getLogger(__name__)
        self.notifiers = {}
    
    def create_email_notifier(self, 
                             name: str = "Email Notifier",
                             smtp_server: str = "smtp.gmail.com",
                             smtp_port: int = 587,
                             sender_email: str = "",
                             recipient_emails: List[str] = None,
                             username: Optional[str] = None,
                             password: Optional[str] = None,
                             use_tls: bool = True,
                             **kwargs) -> EmailNotifier:
        """
        Create an email notifier instance.
        
        Args:
            name: The name of the notifier.
            smtp_server: The SMTP server to use for sending emails.
            smtp_port: The port to use for the SMTP server.
            sender_email: The email address to send notifications from.
            recipient_emails: A list of email addresses to send notifications to.
            username: The username for SMTP authentication. If None, uses sender_email.
            password: The password for SMTP authentication.
            use_tls: Whether to use TLS for the SMTP connection.
            **kwargs: Additional keyword arguments.
            
        Returns:
            EmailNotifier: An instance of the email notifier.
        """
        notifier = EmailNotifier(
            name=name,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            sender_email=sender_email,
            recipient_emails=recipient_emails,
            username=username,
            password=password,
            use_tls=use_tls,
            **kwargs
        )
        
        self.notifiers[name] = notifier
        self.logger.info(f"Created email notifier: {name}")
        
        return notifier
    
    def create_slack_notifier(self,
                             name: str = "Slack Notifier",
                             webhook_url: str = "",
                             channel: Optional[str] = None,
                             username: str = "Scraper Bot",
                             icon_emoji: str = ":robot_face:",
                             **kwargs) -> SlackNotifier:
        """
        Create a Slack notifier instance.
        
        Args:
            name: The name of the notifier.
            webhook_url: The Slack webhook URL to send notifications to.
            channel: The Slack channel to send notifications to (optional).
            username: The username to use for the Slack bot.
            icon_emoji: The emoji to use as the icon for the Slack bot.
            **kwargs: Additional keyword arguments.
            
        Returns:
            SlackNotifier: An instance of the Slack notifier.
        """
        notifier = SlackNotifier(
            name=name,
            webhook_url=webhook_url,
            channel=channel,
            username=username,
            icon_emoji=icon_emoji,
            **kwargs
        )
        
        self.notifiers[name] = notifier
        self.logger.info(f"Created Slack notifier: {name}")
        
        return notifier
    
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
    
    def get_all_notifiers(self) -> Dict[str, BaseNotifier]:
        """
        Get all registered notifiers.
        
        Returns:
            Dict[str, BaseNotifier]: A dictionary of all registered notifiers.
        """
        return self.notifiers
    
    def create_notifiers_from_config(self, config: Dict[str, Any]) -> Dict[str, BaseNotifier]:
        """
        Create notifiers from a configuration dictionary.
        
        Args:
            config: A dictionary containing notifier configurations.
            
        Returns:
            Dict[str, BaseNotifier]: A dictionary of created notifiers.
        """
        if not config:
            self.logger.warning("No notifier configuration provided")
            return {}
        
        # Create email notifiers
        if "email" in config:
            for email_config in config["email"]:
                name = email_config.get("name", f"Email Notifier {len(self.notifiers) + 1}")
                self.create_email_notifier(
                    name=name,
                    smtp_server=email_config.get("smtp_server", "smtp.gmail.com"),
                    smtp_port=email_config.get("smtp_port", 587),
                    sender_email=email_config.get("sender_email", ""),
                    recipient_emails=email_config.get("recipient_emails", []),
                    username=email_config.get("username"),
                    password=email_config.get("password"),
                    use_tls=email_config.get("use_tls", True)
                )
        
        # Create Slack notifiers
        if "slack" in config:
            for slack_config in config["slack"]:
                name = slack_config.get("name", f"Slack Notifier {len(self.notifiers) + 1}")
                self.create_slack_notifier(
                    name=name,
                    webhook_url=slack_config.get("webhook_url", ""),
                    channel=slack_config.get("channel"),
                    username=slack_config.get("username", "Scraper Bot"),
                    icon_emoji=slack_config.get("icon_emoji", ":robot_face:")
                )
        
        return self.notifiers


# Create a singleton instance of the factory
factory = NotifierFactory()


def get_notifier(name: str) -> Optional[BaseNotifier]:
    """
    Convenience function to get a notifier by name.
    
    Args:
        name: The name of the notifier to get.
        
    Returns:
        BaseNotifier: The notifier instance, or None if not found.
    """
    return factory.get_notifier(name)


def create_email_notifier(**kwargs) -> EmailNotifier:
    """
    Convenience function to create an email notifier.
    
    Args:
        **kwargs: Keyword arguments for the email notifier.
        
    Returns:
        EmailNotifier: An instance of the email notifier.
    """
    return factory.create_email_notifier(**kwargs)


def create_slack_notifier(**kwargs) -> SlackNotifier:
    """
    Convenience function to create a Slack notifier.
    
    Args:
        **kwargs: Keyword arguments for the Slack notifier.
        
    Returns:
        SlackNotifier: An instance of the Slack notifier.
    """
    return factory.create_slack_notifier(**kwargs)


def create_notifiers_from_config(config: Dict[str, Any]) -> Dict[str, BaseNotifier]:
    """
    Convenience function to create notifiers from a configuration dictionary.
    
    Args:
        config: A dictionary containing notifier configurations.
        
    Returns:
        Dict[str, BaseNotifier]: A dictionary of created notifiers.
    """
    return factory.create_notifiers_from_config(config)
