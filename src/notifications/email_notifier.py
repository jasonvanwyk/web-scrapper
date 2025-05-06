"""
Email notifier module for the Automated Product Data Scraper.

This module provides functionality for sending email notifications about the scraper's
status, including completion, errors, and execution summaries.
"""

import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Union
import traceback

# Try both import paths to handle different execution contexts
try:
    from src.notifications.base_notifier import BaseNotifier
except ModuleNotFoundError:
    from notifications.base_notifier import BaseNotifier


class EmailNotifier(BaseNotifier):
    """
    Email notifier for sending notifications via email.
    
    This class implements the BaseNotifier interface to send notifications
    via email using SMTP.
    
    Attributes:
        smtp_server: The SMTP server to use for sending emails.
        smtp_port: The port to use for the SMTP server.
        sender_email: The email address to send notifications from.
        recipient_emails: A list of email addresses to send notifications to.
        username: The username for SMTP authentication.
        password: The password for SMTP authentication.
        use_tls: Whether to use TLS for the SMTP connection.
    """
    
    def __init__(self, 
                 name: str = "Email Notifier",
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: str = "",
                 recipient_emails: List[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 use_tls: bool = True,
                 **kwargs):
        """
        Initialize the email notifier.
        
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
        """
        super().__init__(name=name, **kwargs)
        
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.recipient_emails = recipient_emails or []
        self.username = username or sender_email
        self.password = password
        self.use_tls = use_tls
        
        # Validate configuration
        if not self.sender_email:
            self.logger.warning("Sender email not provided. Email notifications will not be sent.")
        
        if not self.recipient_emails:
            self.logger.warning("No recipient emails provided. Email notifications will not be sent.")
        
        if not self.password:
            self.logger.warning("SMTP password not provided. Email notifications may fail if authentication is required.")
    
    def send_email(self, subject: str, message: str, html_message: Optional[str] = None) -> bool:
        """
        Send an email notification.
        
        Args:
            subject: The subject of the email.
            message: The plain text message body of the email.
            html_message: The HTML message body of the email (optional).
            
        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        if not self.sender_email or not self.recipient_emails:
            self.logger.warning("Cannot send email: sender or recipients not configured.")
            return False
        
        try:
            # Create a multipart message
            email_message = MIMEMultipart("alternative")
            email_message["Subject"] = subject
            email_message["From"] = self.sender_email
            email_message["To"] = ", ".join(self.recipient_emails)
            
            # Add plain text and HTML parts
            email_message.attach(MIMEText(message, "plain"))
            if html_message:
                email_message.attach(MIMEText(html_message, "html"))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=ssl.create_default_context())
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.sendmail(
                    self.sender_email,
                    self.recipient_emails,
                    email_message.as_string()
                )
            
            self.logger.info(f"Email notification sent to {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}", exc_info=True)
            return False
    
    def send_completion_notification(self, 
                                    subject: str, 
                                    message: str, 
                                    **kwargs) -> bool:
        """
        Send a notification when the scraper completes successfully.
        
        Args:
            subject: The subject of the notification.
            message: The message body of the notification.
            **kwargs: Additional keyword arguments.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        # Create a more informative subject if not specified
        if subject == "":
            subject = "Scraper Completed Successfully"
        
        # Create HTML version of the message
        html_message = f"<html><body><h2>{subject}</h2><p>{message.replace(os.linesep, '<br>')}</p></body></html>"
        
        return self.send_email(subject, message, html_message)
    
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
            **kwargs: Additional keyword arguments.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        # Create a more informative subject if not specified
        if subject == "":
            subject = "Scraper Error Alert"
        
        # Add error details to the message if provided
        full_message = message
        if error:
            full_message += f"\n\nError details:\n{str(error)}\n\n"
            full_message += f"Traceback:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
        
        # Create HTML version of the message
        html_message = f"""
        <html>
        <body>
            <h2 style="color: #cc0000;">{subject}</h2>
            <p>{message.replace(os.linesep, '<br>')}</p>
            
            {f'<h3>Error Details:</h3><pre>{str(error)}</pre>' if error else ''}
            
            {f'<h3>Traceback:</h3><pre>{"".join(traceback.format_exception(type(error), error, error.__traceback__))}</pre>' if error else ''}
        </body>
        </html>
        """
        
        return self.send_email(subject, full_message, html_message)
    
    def send_summary_notification(self, 
                                 subject: str, 
                                 summary_data: Dict[str, Any], 
                                 **kwargs) -> bool:
        """
        Send a summary notification with details about the scraping process.
        
        Args:
            subject: The subject of the notification.
            summary_data: A dictionary containing summary data about the scraping process.
            **kwargs: Additional keyword arguments.
            
        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        # Create a more informative subject if not specified
        if subject == "":
            subject = "Scraper Execution Summary"
        
        # Format the summary data into a readable message
        message = self.format_summary(summary_data)
        
        # Create HTML version of the message
        html_message = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <div style="font-family: monospace; white-space: pre-wrap;">{message.replace(os.linesep, '<br>')}</div>
        </body>
        </html>
        """
        
        return self.send_email(subject, message, html_message)
