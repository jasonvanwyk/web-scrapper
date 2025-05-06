"""
Tests for the notification module.

This module contains tests for the notification functionality, including
sending notifications via email and Slack.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.notifications.base_notifier import BaseNotifier
from src.notifications.email_notifier import EmailNotifier
from src.notifications.slack_notifier import SlackNotifier
from src.notifications.factory import (
    NotifierFactory, 
    get_notifier, 
    create_email_notifier, 
    create_slack_notifier,
    create_notifiers_from_config
)
from src.notifications.notification_manager import NotificationManager, get_notification_manager


class TestBaseNotifier(unittest.TestCase):
    """Test cases for the BaseNotifier class."""
    
    def test_format_summary(self):
        """Test formatting summary data."""
        # Create a concrete implementation of BaseNotifier for testing
        class TestNotifier(BaseNotifier):
            def send_completion_notification(self, subject, message, **kwargs):
                return True
            
            def send_error_notification(self, subject, message, error=None, **kwargs):
                return True
            
            def send_summary_notification(self, subject, summary_data, **kwargs):
                return True
        
        # Create a test notifier
        notifier = TestNotifier(name="Test Notifier")
        
        # Create test summary data
        summary_data = {
            "start_time": "2025-05-06 10:00:00",
            "end_time": "2025-05-06 10:30:00",
            "duration": "0:30:00",
            "suppliers": [
                {
                    "name": "Supplier A",
                    "status": "success",
                    "products_found": 10,
                    "products_processed": 10,
                    "errors": []
                },
                {
                    "name": "Supplier B",
                    "status": "failed",
                    "products_found": 5,
                    "products_processed": 3,
                    "errors": ["Error 1", "Error 2", "Error 3", "Error 4"]
                }
            ],
            "total_products": 15,
            "successful_products": 13,
            "failed_products": 2,
            "total_suppliers": 2,
            "successful_suppliers": 1,
            "failed_suppliers": 1,
            "output_files": ["output/supplier_a.csv", "output/supplier_b.csv"]
        }
        
        # Format the summary
        formatted_summary = notifier.format_summary(summary_data)
        
        # Check that the formatted summary contains expected information
        self.assertIn("Scraper Execution Summary", formatted_summary)
        self.assertIn("Start Time: 2025-05-06 10:00:00", formatted_summary)
        self.assertIn("End Time: 2025-05-06 10:30:00", formatted_summary)
        self.assertIn("Duration: 0:30:00", formatted_summary)
        self.assertIn("Supplier A", formatted_summary)
        self.assertIn("Status: success", formatted_summary)
        self.assertIn("Products Found: 10", formatted_summary)
        self.assertIn("Products Processed: 10", formatted_summary)
        self.assertIn("Supplier B", formatted_summary)
        self.assertIn("Status: failed", formatted_summary)
        self.assertIn("Products Found: 5", formatted_summary)
        self.assertIn("Products Processed: 3", formatted_summary)
        self.assertIn("Errors: 4", formatted_summary)
        self.assertIn("... and 1 more", formatted_summary)
        self.assertIn("Total Products: 15", formatted_summary)
        self.assertIn("Successfully Processed: 13", formatted_summary)
        self.assertIn("Failed to Process: 2", formatted_summary)
        self.assertIn("Total Suppliers: 2", formatted_summary)
        self.assertIn("Successful Suppliers: 1", formatted_summary)
        self.assertIn("Failed Suppliers: 1", formatted_summary)
        self.assertIn("output/supplier_a.csv", formatted_summary)
        self.assertIn("output/supplier_b.csv", formatted_summary)


class TestEmailNotifier(unittest.TestCase):
    """Test cases for the EmailNotifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notifier = EmailNotifier(
            name="Test Email Notifier",
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender_email="sender@example.com",
            recipient_emails=["recipient@example.com"],
            username="username",
            password="password",
            use_tls=True
        )
    
    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        """Test sending an email."""
        # Set up the mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Call the method under test
        result = self.notifier.send_email(
            subject="Test Subject",
            message="Test Message",
            html_message="<html><body><p>Test Message</p></body></html>"
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that SMTP was initialized with the correct parameters
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        
        # Check that TLS was started
        mock_smtp_instance.starttls.assert_called_once()
        
        # Check that login was called with the correct credentials
        mock_smtp_instance.login.assert_called_once_with("username", "password")
        
        # Check that sendmail was called with the correct parameters
        self.assertEqual(mock_smtp_instance.sendmail.call_count, 1)
        args, _ = mock_smtp_instance.sendmail.call_args
        self.assertEqual(args[0], "sender@example.com")
        self.assertEqual(args[1], ["recipient@example.com"])
        # The third argument is the email message as a string, which is complex to verify
    
    @patch('smtplib.SMTP')
    def test_send_completion_notification(self, mock_smtp):
        """Test sending a completion notification."""
        # Set up the mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Call the method under test
        result = self.notifier.send_completion_notification(
            subject="Scraper Completed",
            message="The scraper has completed successfully."
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that sendmail was called
        self.assertEqual(mock_smtp_instance.sendmail.call_count, 1)
    
    @patch('smtplib.SMTP')
    def test_send_error_notification(self, mock_smtp):
        """Test sending an error notification."""
        # Set up the mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Create a test error
        test_error = ValueError("Test error")
        
        # Call the method under test
        result = self.notifier.send_error_notification(
            subject="Scraper Error",
            message="An error occurred during scraping.",
            error=test_error
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that sendmail was called
        self.assertEqual(mock_smtp_instance.sendmail.call_count, 1)
    
    @patch('smtplib.SMTP')
    def test_send_summary_notification(self, mock_smtp):
        """Test sending a summary notification."""
        # Set up the mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Create test summary data
        summary_data = {
            "start_time": "2025-05-06 10:00:00",
            "end_time": "2025-05-06 10:30:00",
            "duration": "0:30:00",
            "suppliers": [
                {
                    "name": "Supplier A",
                    "status": "success",
                    "products_found": 10,
                    "products_processed": 10,
                    "errors": []
                }
            ],
            "total_products": 10,
            "successful_products": 10,
            "failed_products": 0,
            "total_suppliers": 1,
            "successful_suppliers": 1,
            "failed_suppliers": 0,
            "output_files": ["output/supplier_a.csv"]
        }
        
        # Call the method under test
        result = self.notifier.send_summary_notification(
            subject="Scraper Summary",
            summary_data=summary_data
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that sendmail was called
        self.assertEqual(mock_smtp_instance.sendmail.call_count, 1)


class TestSlackNotifier(unittest.TestCase):
    """Test cases for the SlackNotifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notifier = SlackNotifier(
            name="Test Slack Notifier",
            webhook_url="https://hooks.slack.com/services/test/webhook",
            channel="#test-channel",
            username="Test Bot",
            icon_emoji=":test:"
        )
    
    @patch('requests.post')
    def test_send_slack_message(self, mock_post):
        """Test sending a Slack message."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Call the method under test
        result = self.notifier.send_slack_message(
            text="Test message",
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": "Test message"}}]
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that requests.post was called with the correct parameters
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://hooks.slack.com/services/test/webhook")
        self.assertEqual(kwargs["headers"], {"Content-Type": "application/json"})
        
        # Parse the payload to check its contents
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["text"], "Test message")
        self.assertEqual(payload["username"], "Test Bot")
        self.assertEqual(payload["icon_emoji"], ":test:")
        self.assertEqual(payload["channel"], "#test-channel")
        self.assertEqual(payload["blocks"], [{"type": "section", "text": {"type": "mrkdwn", "text": "Test message"}}])
    
    @patch('requests.post')
    def test_send_completion_notification(self, mock_post):
        """Test sending a completion notification."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Call the method under test
        result = self.notifier.send_completion_notification(
            subject="Scraper Completed",
            message="The scraper has completed successfully."
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that requests.post was called
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_error_notification(self, mock_post):
        """Test sending an error notification."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create a test error
        test_error = ValueError("Test error")
        
        # Call the method under test
        result = self.notifier.send_error_notification(
            subject="Scraper Error",
            message="An error occurred during scraping.",
            error=test_error
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that requests.post was called
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_summary_notification(self, mock_post):
        """Test sending a summary notification."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create test summary data
        summary_data = {
            "start_time": "2025-05-06 10:00:00",
            "end_time": "2025-05-06 10:30:00",
            "duration": "0:30:00",
            "suppliers": [
                {
                    "name": "Supplier A",
                    "status": "success",
                    "products_found": 10,
                    "products_processed": 10,
                    "errors": []
                }
            ],
            "total_products": 10,
            "successful_products": 10,
            "failed_products": 0,
            "total_suppliers": 1,
            "successful_suppliers": 1,
            "failed_suppliers": 0,
            "output_files": ["output/supplier_a.csv"]
        }
        
        # Call the method under test
        result = self.notifier.send_summary_notification(
            subject="Scraper Summary",
            summary_data=summary_data
        )
        
        # Check that the result is True (success)
        self.assertTrue(result)
        
        # Check that requests.post was called
        mock_post.assert_called_once()


class TestNotifierFactory(unittest.TestCase):
    """Test cases for the NotifierFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = NotifierFactory()
    
    def test_create_email_notifier(self):
        """Test creating an email notifier."""
        # Call the method under test
        notifier = self.factory.create_email_notifier(
            name="Test Email Notifier",
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender_email="sender@example.com",
            recipient_emails=["recipient@example.com"],
            username="username",
            password="password",
            use_tls=True
        )
        
        # Check that the notifier was created correctly
        self.assertIsInstance(notifier, EmailNotifier)
        self.assertEqual(notifier.name, "Test Email Notifier")
        self.assertEqual(notifier.smtp_server, "smtp.example.com")
        self.assertEqual(notifier.smtp_port, 587)
        self.assertEqual(notifier.sender_email, "sender@example.com")
        self.assertEqual(notifier.recipient_emails, ["recipient@example.com"])
        self.assertEqual(notifier.username, "username")
        self.assertEqual(notifier.password, "password")
        self.assertEqual(notifier.use_tls, True)
        
        # Check that the notifier was added to the factory
        self.assertIn("Test Email Notifier", self.factory.notifiers)
        self.assertEqual(self.factory.notifiers["Test Email Notifier"], notifier)
    
    def test_create_slack_notifier(self):
        """Test creating a Slack notifier."""
        # Call the method under test
        notifier = self.factory.create_slack_notifier(
            name="Test Slack Notifier",
            webhook_url="https://hooks.slack.com/services/test/webhook",
            channel="#test-channel",
            username="Test Bot",
            icon_emoji=":test:"
        )
        
        # Check that the notifier was created correctly
        self.assertIsInstance(notifier, SlackNotifier)
        self.assertEqual(notifier.name, "Test Slack Notifier")
        self.assertEqual(notifier.webhook_url, "https://hooks.slack.com/services/test/webhook")
        self.assertEqual(notifier.channel, "#test-channel")
        self.assertEqual(notifier.username, "Test Bot")
        self.assertEqual(notifier.icon_emoji, ":test:")
        
        # Check that the notifier was added to the factory
        self.assertIn("Test Slack Notifier", self.factory.notifiers)
        self.assertEqual(self.factory.notifiers["Test Slack Notifier"], notifier)
    
    def test_get_notifier(self):
        """Test getting a notifier by name."""
        # Create a test notifier
        notifier = self.factory.create_email_notifier(name="Test Notifier")
        
        # Call the method under test
        result = self.factory.get_notifier("Test Notifier")
        
        # Check that the correct notifier was returned
        self.assertEqual(result, notifier)
        
        # Check that None is returned for a non-existent notifier
        self.assertIsNone(self.factory.get_notifier("Non-existent Notifier"))
    
    def test_get_all_notifiers(self):
        """Test getting all notifiers."""
        # Create test notifiers
        notifier1 = self.factory.create_email_notifier(name="Test Notifier 1")
        notifier2 = self.factory.create_slack_notifier(name="Test Notifier 2")
        
        # Call the method under test
        result = self.factory.get_all_notifiers()
        
        # Check that all notifiers are returned
        self.assertEqual(len(result), 2)
        self.assertEqual(result["Test Notifier 1"], notifier1)
        self.assertEqual(result["Test Notifier 2"], notifier2)
    
    def test_create_notifiers_from_config(self):
        """Test creating notifiers from a configuration dictionary."""
        # Create a test configuration
        config = {
            "email": [
                {
                    "name": "Test Email Notifier",
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "sender_email": "sender@example.com",
                    "recipient_emails": ["recipient@example.com"],
                    "username": "username",
                    "password": "password",
                    "use_tls": True
                }
            ],
            "slack": [
                {
                    "name": "Test Slack Notifier",
                    "webhook_url": "https://hooks.slack.com/services/test/webhook",
                    "channel": "#test-channel",
                    "username": "Test Bot",
                    "icon_emoji": ":test:"
                }
            ]
        }
        
        # Call the method under test
        result = self.factory.create_notifiers_from_config(config)
        
        # Check that the correct notifiers were created
        self.assertEqual(len(result), 2)
        self.assertIn("Test Email Notifier", result)
        self.assertIn("Test Slack Notifier", result)
        self.assertIsInstance(result["Test Email Notifier"], EmailNotifier)
        self.assertIsInstance(result["Test Slack Notifier"], SlackNotifier)


class TestNotificationManager(unittest.TestCase):
    """Test cases for the NotificationManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = NotificationManager()
        
        # Create test notifiers
        self.email_notifier = MagicMock(spec=EmailNotifier)
        self.email_notifier.name = "Test Email Notifier"
        self.email_notifier.send_completion_notification.return_value = True
        self.email_notifier.send_error_notification.return_value = True
        self.email_notifier.send_summary_notification.return_value = True
        
        self.slack_notifier = MagicMock(spec=SlackNotifier)
        self.slack_notifier.name = "Test Slack Notifier"
        self.slack_notifier.send_completion_notification.return_value = True
        self.slack_notifier.send_error_notification.return_value = True
        self.slack_notifier.send_summary_notification.return_value = True
        
        # Add the notifiers to the manager
        self.manager.add_notifier(self.email_notifier)
        self.manager.add_notifier(self.slack_notifier)
    
    def test_add_notifier(self):
        """Test adding a notifier to the manager."""
        # Create a new notifier
        notifier = MagicMock(spec=BaseNotifier)
        notifier.name = "New Notifier"
        
        # Call the method under test
        self.manager.add_notifier(notifier)
        
        # Check that the notifier was added
        self.assertIn("New Notifier", self.manager.notifiers)
        self.assertEqual(self.manager.notifiers["New Notifier"], notifier)
    
    def test_remove_notifier(self):
        """Test removing a notifier from the manager."""
        # Call the method under test
        result = self.manager.remove_notifier("Test Email Notifier")
        
        # Check that the notifier was removed
        self.assertTrue(result)
        self.assertNotIn("Test Email Notifier", self.manager.notifiers)
        
        # Check that False is returned for a non-existent notifier
        self.assertFalse(self.manager.remove_notifier("Non-existent Notifier"))
    
    def test_get_notifier(self):
        """Test getting a notifier by name."""
        # Call the method under test
        result = self.manager.get_notifier("Test Email Notifier")
        
        # Check that the correct notifier was returned
        self.assertEqual(result, self.email_notifier)
        
        # Check that None is returned for a non-existent notifier
        self.assertIsNone(self.manager.get_notifier("Non-existent Notifier"))
    
    def test_send_completion_notification(self):
        """Test sending a completion notification to all notifiers."""
        # Call the method under test
        result = self.manager.send_completion_notification(
            subject="Scraper Completed",
            message="The scraper has completed successfully."
        )
        
        # Check that the notification was sent to all notifiers
        self.email_notifier.send_completion_notification.assert_called_once_with(
            "Scraper Completed", "The scraper has completed successfully."
        )
        self.slack_notifier.send_completion_notification.assert_called_once_with(
            "Scraper Completed", "The scraper has completed successfully."
        )
        
        # Check that the result contains the success status for each notifier
        self.assertEqual(result, {
            "Test Email Notifier": True,
            "Test Slack Notifier": True
        })
    
    def test_send_completion_notification_with_specific_notifiers(self):
        """Test sending a completion notification to specific notifiers."""
        # Call the method under test
        result = self.manager.send_completion_notification(
            subject="Scraper Completed",
            message="The scraper has completed successfully.",
            notifier_names=["Test Email Notifier"]
        )
        
        # Check that the notification was sent only to the specified notifier
        self.email_notifier.send_completion_notification.assert_called_once_with(
            "Scraper Completed", "The scraper has completed successfully."
        )
        self.slack_notifier.send_completion_notification.assert_not_called()
        
        # Check that the result contains the success status for the specified notifier
        self.assertEqual(result, {
            "Test Email Notifier": True
        })
    
    def test_send_error_notification(self):
        """Test sending an error notification to all notifiers."""
        # Create a test error
        test_error = ValueError("Test error")
        
        # Call the method under test
        result = self.manager.send_error_notification(
            subject="Scraper Error",
            message="An error occurred during scraping.",
            error=test_error
        )
        
        # Check that the notification was sent to all notifiers
        self.email_notifier.send_error_notification.assert_called_once_with(
            "Scraper Error", "An error occurred during scraping.", test_error
        )
        self.slack_notifier.send_error_notification.assert_called_once_with(
            "Scraper Error", "An error occurred during scraping.", test_error
        )
        
        # Check that the result contains the success status for each notifier
        self.assertEqual(result, {
            "Test Email Notifier": True,
            "Test Slack Notifier": True
        })
    
    def test_send_summary_notification(self):
        """Test sending a summary notification to all notifiers."""
        # Create test summary data
        summary_data = {
            "start_time": "2025-05-06 10:00:00",
            "end_time": "2025-05-06 10:30:00",
            "duration": "0:30:00",
            "suppliers": [
                {
                    "name": "Supplier A",
                    "status": "success",
                    "products_found": 10,
                    "products_processed": 10,
                    "errors": []
                }
            ],
            "total_products": 10,
            "successful_products": 10,
            "failed_products": 0,
            "total_suppliers": 1,
            "successful_suppliers": 1,
            "failed_suppliers": 0,
            "output_files": ["output/supplier_a.csv"]
        }
        
        # Call the method under test
        result = self.manager.send_summary_notification(
            subject="Scraper Summary",
            summary_data=summary_data
        )
        
        # Check that the notification was sent to all notifiers
        self.email_notifier.send_summary_notification.assert_called_once_with(
            "Scraper Summary", summary_data
        )
        self.slack_notifier.send_summary_notification.assert_called_once_with(
            "Scraper Summary", summary_data
        )
        
        # Check that the result contains the success status for each notifier
        self.assertEqual(result, {
            "Test Email Notifier": True,
            "Test Slack Notifier": True
        })


if __name__ == "__main__":
    unittest.main()
