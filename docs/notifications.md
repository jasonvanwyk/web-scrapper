# Notification System Documentation

This document explains how to configure and use the notification system in the Automated Product Data Scraper. The system can send notifications about the scraper's status, including completion, errors, and execution summaries.

## Overview

The notification system supports multiple notification channels:

1. **Email Notifications**: Send notifications via email using SMTP
2. **Slack Notifications**: Send notifications to Slack channels using webhooks

The system can send three types of notifications:

1. **Completion Notifications**: Sent when the scraper completes successfully
2. **Error Notifications**: Sent when errors occur during scraping
3. **Summary Notifications**: Sent at the end of the scraping process with detailed statistics

## Configuration

Notifications are configured through environment variables or the `.env` file. Here's an example configuration:

```
# Global notification settings
NOTIFICATIONS_ENABLED=True
NOTIFY_ON_COMPLETION=True
NOTIFY_ON_ERROR=True
NOTIFY_SUMMARY=True

# Email notification settings
EMAIL_NOTIFICATIONS_ENABLED=True
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@example.com
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_USE_TLS=True

# Slack notification settings
SLACK_NOTIFICATIONS_ENABLED=True
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
SLACK_CHANNEL=#scraper-notifications
SLACK_USERNAME=Scraper Bot
SLACK_ICON_EMOJI=:robot_face:
```

### Configuration Options

#### Global Settings

| Option | Description | Default |
|--------|-------------|---------|
| `NOTIFICATIONS_ENABLED` | Enable or disable all notifications | `False` |
| `NOTIFY_ON_COMPLETION` | Send notifications when the scraper completes successfully | `True` |
| `NOTIFY_ON_ERROR` | Send notifications when errors occur | `True` |
| `NOTIFY_SUMMARY` | Send summary notifications with detailed statistics | `True` |

#### Email Settings

| Option | Description | Default |
|--------|-------------|---------|
| `EMAIL_NOTIFICATIONS_ENABLED` | Enable or disable email notifications | `False` |
| `SMTP_SERVER` | SMTP server for sending emails | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SENDER_EMAIL` | Email address to send notifications from | `""` |
| `RECIPIENT_EMAILS` | Comma-separated list of email addresses to send notifications to | `[]` |
| `SMTP_USERNAME` | Username for SMTP authentication (if different from sender_email) | `None` |
| `SMTP_PASSWORD` | Password for SMTP authentication | `""` |
| `SMTP_USE_TLS` | Whether to use TLS for SMTP connection | `True` |

#### Slack Settings

| Option | Description | Default |
|--------|-------------|---------|
| `SLACK_NOTIFICATIONS_ENABLED` | Enable or disable Slack notifications | `False` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL for sending notifications | `""` |
| `SLACK_CHANNEL` | Slack channel to send notifications to | `None` |
| `SLACK_USERNAME` | Username to use for Slack notifications | `"Scraper Bot"` |
| `SLACK_ICON_EMOJI` | Emoji to use as the icon for Slack notifications | `":robot_face:"` |

## Email Notifications

### Gmail Configuration

If you're using Gmail as your SMTP server, you'll need to:

1. Enable 2-Step Verification for your Google account
2. Create an App Password for the scraper
3. Use this App Password in the `SMTP_PASSWORD` setting

### Other Email Providers

For other email providers, you'll need to:

1. Find the SMTP server and port for your email provider
2. Configure the appropriate authentication settings
3. Make sure your email provider allows sending emails from applications

## Slack Notifications

To set up Slack notifications:

1. Create a Slack App in your workspace
2. Enable Incoming Webhooks for your app
3. Create a new webhook for your channel
4. Copy the webhook URL to the `SLACK_WEBHOOK_URL` setting

## Notification Types

### Completion Notifications

Sent when the scraper completes successfully. Includes:
- A success message
- The number of products processed
- The number of suppliers processed

### Error Notifications

Sent when errors occur during scraping. Includes:
- An error message
- Details about the error
- A traceback (for email notifications)

### Summary Notifications

Sent at the end of the scraping process. Includes:
- Start and end times
- Duration
- Number of products processed
- Number of successful and failed products
- Number of suppliers processed
- Number of successful and failed suppliers
- List of output files
- Details about each supplier

## Programmatic Usage

You can also use the notification system programmatically in your own code:

```python
from src.notifications.notification_manager import get_notification_manager

# Initialize the notification manager
notification_manager = get_notification_manager()

# Send a completion notification
notification_manager.send_completion_notification(
    subject="Scraper Completed",
    message="The scraper has completed successfully."
)

# Send an error notification
notification_manager.send_error_notification(
    subject="Scraper Error",
    message="An error occurred during scraping.",
    error=exception
)

# Send a summary notification
notification_manager.send_summary_notification(
    subject="Scraper Summary",
    summary_data={
        "start_time": "2025-05-06 10:00:00",
        "end_time": "2025-05-06 10:30:00",
        "duration": "0:30:00",
        "suppliers": [...],
        "total_products": 10,
        "successful_products": 10,
        "failed_products": 0,
        "total_suppliers": 1,
        "successful_suppliers": 1,
        "failed_suppliers": 0,
        "output_files": ["output/supplier_a.csv"]
    }
)
```

## Troubleshooting

### Email Notifications

If email notifications are not being sent:

1. Check that `NOTIFICATIONS_ENABLED` and `EMAIL_NOTIFICATIONS_ENABLED` are set to `True`
2. Verify that the SMTP server and port are correct
3. Make sure the sender email and password are correct
4. Check that the recipient emails are valid
5. If using Gmail, make sure you're using an App Password

### Slack Notifications

If Slack notifications are not being sent:

1. Check that `NOTIFICATIONS_ENABLED` and `SLACK_NOTIFICATIONS_ENABLED` are set to `True`
2. Verify that the webhook URL is correct
3. Make sure the Slack app has the necessary permissions
4. Check that the channel name is valid (if specified)

## Security Considerations

The notification system handles sensitive information such as email credentials. To ensure security:

1. Never hardcode credentials in your code
2. Use environment variables or a secure `.env` file
3. Make sure your `.env` file is in `.gitignore` to prevent it from being committed to version control
4. Consider using a secrets management service in production environments
