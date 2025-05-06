"""
Slack notifier module for the Automated Product Data Scraper.

This module provides functionality for sending Slack notifications about the scraper's
status, including completion, errors, and execution summaries.
"""

import json
import logging
import traceback
from typing import Dict, List, Optional, Any, Union
import requests

# Try both import paths to handle different execution contexts
try:
    from src.notifications.base_notifier import BaseNotifier
except ModuleNotFoundError:
    from notifications.base_notifier import BaseNotifier


class SlackNotifier(BaseNotifier):
    """
    Slack notifier for sending notifications to Slack channels.
    
    This class implements the BaseNotifier interface to send notifications
    to Slack channels using webhooks.
    
    Attributes:
        webhook_url: The Slack webhook URL to send notifications to.
        channel: The Slack channel to send notifications to.
        username: The username to use for the Slack bot.
        icon_emoji: The emoji to use as the icon for the Slack bot.
    """
    
    def __init__(self, 
                 name: str = "Slack Notifier",
                 webhook_url: str = "",
                 channel: Optional[str] = None,
                 username: str = "Scraper Bot",
                 icon_emoji: str = ":robot_face:",
                 **kwargs):
        """
        Initialize the Slack notifier.
        
        Args:
            name: The name of the notifier.
            webhook_url: The Slack webhook URL to send notifications to.
            channel: The Slack channel to send notifications to (optional).
            username: The username to use for the Slack bot.
            icon_emoji: The emoji to use as the icon for the Slack bot.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, **kwargs)
        
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        
        # Validate configuration
        if not self.webhook_url:
            self.logger.warning("Slack webhook URL not provided. Slack notifications will not be sent.")
    
    def send_slack_message(self, 
                          text: str, 
                          blocks: Optional[List[Dict[str, Any]]] = None,
                          attachments: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Send a message to Slack.
        
        Args:
            text: The text of the message.
            blocks: A list of block objects for the message (optional).
            attachments: A list of attachment objects for the message (optional).
            
        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if not self.webhook_url:
            self.logger.warning("Cannot send Slack message: webhook URL not configured.")
            return False
        
        try:
            # Create the payload
            payload = {
                "text": text,
                "username": self.username,
                "icon_emoji": self.icon_emoji
            }
            
            # Add channel if specified
            if self.channel:
                payload["channel"] = self.channel
            
            # Add blocks if provided
            if blocks:
                payload["blocks"] = blocks
            
            # Add attachments if provided
            if attachments:
                payload["attachments"] = attachments
            
            # Send the request
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            self.logger.info(f"Slack notification sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}", exc_info=True)
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
        
        # Create blocks for the message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": subject,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":white_check_mark: *Status:* Success"
                    }
                ]
            }
        ]
        
        return self.send_slack_message(
            text=f"{subject}: {message}",
            blocks=blocks
        )
    
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
        
        # Create blocks for the message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": subject,
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":x: *Status:* Error"
                    }
                ]
            }
        ]
        
        # Add error details if provided
        if error:
            error_text = f"```{str(error)}```"
            traceback_text = f"```{''.join(traceback.format_exception(type(error), error, error.__traceback__))}```"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Details:*\n{error_text}"
                }
            })
            
            # Only include traceback if it's not too long for Slack
            if len(traceback_text) < 3000:  # Slack has a limit on text field size
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Traceback:*\n{traceback_text}"
                    }
                })
        
        return self.send_slack_message(
            text=f"{subject}: {message}",
            blocks=blocks
        )
    
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
        
        # Determine the overall status
        status = ":white_check_mark: Success"
        if "failed_suppliers" in summary_data and summary_data["failed_suppliers"] > 0:
            status = ":warning: Partial Success"
        if "successful_suppliers" in summary_data and summary_data["successful_suppliers"] == 0:
            status = ":x: Failure"
        
        # Create blocks for the message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": subject,
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:* {status}"
                    }
                ]
            }
        ]
        
        # Add execution time information if available
        if "start_time" in summary_data and "end_time" in summary_data:
            time_text = f"*Start Time:* {summary_data['start_time']}\n*End Time:* {summary_data['end_time']}"
            
            if "duration" in summary_data:
                time_text += f"\n*Duration:* {summary_data['duration']}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": time_text
                }
            })
        
        # Add overall statistics if available
        if "total_products" in summary_data:
            stats_text = f"*Total Products:* {summary_data['total_products']}"
            
            if "successful_products" in summary_data:
                stats_text += f"\n*Successfully Processed:* {summary_data['successful_products']}"
            
            if "failed_products" in summary_data:
                stats_text += f"\n*Failed to Process:* {summary_data['failed_products']}"
            
            if "total_suppliers" in summary_data:
                stats_text += f"\n*Total Suppliers:* {summary_data['total_suppliers']}"
            
            if "successful_suppliers" in summary_data:
                stats_text += f"\n*Successful Suppliers:* {summary_data['successful_suppliers']}"
            
            if "failed_suppliers" in summary_data:
                stats_text += f"\n*Failed Suppliers:* {summary_data['failed_suppliers']}"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": stats_text
                }
            })
        
        # Add supplier information if available (simplified for Slack)
        if "suppliers" in summary_data:
            supplier_text = "*Supplier Results:*\n"
            
            for supplier in summary_data["suppliers"]:
                status_emoji = ":white_check_mark:" if supplier["status"] == "success" else ":x:"
                supplier_text += f"\n• *{supplier['name']}*: {status_emoji} {supplier['status'].capitalize()}"
                
                if "products_found" in supplier:
                    supplier_text += f", {supplier['products_found']} products found"
                
                if "products_processed" in supplier:
                    supplier_text += f", {supplier['products_processed']} processed"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": supplier_text
                }
            })
        
        # Add output information if available
        if "output_files" in summary_data and summary_data["output_files"]:
            output_text = "*Output Files:*\n"
            
            for output_file in summary_data["output_files"]:
                output_text += f"• {output_file}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": output_text
                }
            })
        
        # Send the message with the formatted blocks
        return self.send_slack_message(
            text=subject,
            blocks=blocks
        )
