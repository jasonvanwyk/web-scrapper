#!/usr/bin/env python3
"""
Example script demonstrating how to use the notification system.

This script shows how to send different types of notifications
using the notification system.
"""

import os
import sys
import datetime
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the notification modules
from src.notifications.notification_manager import get_notification_manager
from src.notifications.email_notifier import EmailNotifier
from src.notifications.slack_notifier import SlackNotifier
from src.utils.logging_config import setup_logging, get_logger


def send_test_notifications():
    """
    Send test notifications using the notification system.
    """
    logger = get_logger(__name__)
    logger.info("Sending test notifications")
    
    # Create a notification manager
    notification_manager = get_notification_manager()
    
    # Create an email notifier
    email_notifier = EmailNotifier(
        name="Example Email Notifier",
        smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        sender_email=os.getenv("SENDER_EMAIL", ""),
        recipient_emails=os.getenv("RECIPIENT_EMAILS", "").split(",") if os.getenv("RECIPIENT_EMAILS") else [],
        username=os.getenv("SMTP_USERNAME"),
        password=os.getenv("SMTP_PASSWORD", ""),
        use_tls=os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "t")
    )
    
    # Create a Slack notifier
    slack_notifier = SlackNotifier(
        name="Example Slack Notifier",
        webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
        channel=os.getenv("SLACK_CHANNEL"),
        username=os.getenv("SLACK_USERNAME", "Scraper Bot"),
        icon_emoji=os.getenv("SLACK_ICON_EMOJI", ":robot_face:")
    )
    
    # Add the notifiers to the manager
    notification_manager.add_notifier(email_notifier)
    notification_manager.add_notifier(slack_notifier)
    
    # Send a completion notification
    logger.info("Sending completion notification")
    notification_manager.send_completion_notification(
        subject="Test Completion Notification",
        message="This is a test completion notification from the Automated Product Data Scraper."
    )
    
    # Send an error notification
    logger.info("Sending error notification")
    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception as e:
        notification_manager.send_error_notification(
            subject="Test Error Notification",
            message="This is a test error notification from the Automated Product Data Scraper.",
            error=e
        )
    
    # Create sample summary data
    now = datetime.datetime.now()
    start_time = now - datetime.timedelta(minutes=30)
    summary_data = {
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": str(now - start_time),
        "suppliers": [
            {
                "name": "Example Supplier A",
                "status": "success",
                "products_found": 10,
                "products_processed": 10,
                "errors": []
            },
            {
                "name": "Example Supplier B",
                "status": "failed",
                "products_found": 5,
                "products_processed": 3,
                "errors": [
                    "Error processing product 1: Connection timeout",
                    "Error processing product 2: Invalid data format"
                ]
            }
        ],
        "total_products": 15,
        "successful_products": 13,
        "failed_products": 2,
        "total_suppliers": 2,
        "successful_suppliers": 1,
        "failed_suppliers": 1,
        "output_files": [
            "output/example_supplier_a.csv",
            "output/example_supplier_b.csv"
        ]
    }
    
    # Send a summary notification
    logger.info("Sending summary notification")
    notification_manager.send_summary_notification(
        subject="Test Summary Notification",
        summary_data=summary_data
    )
    
    logger.info("All test notifications sent")


def main():
    """
    Main function for the notification example script.
    """
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    try:
        # Send test notifications
        send_test_notifications()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
