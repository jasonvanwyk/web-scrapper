#!/usr/bin/env python3
"""
Example script demonstrating how to use the Python 'schedule' library
to run the Automated Product Data Scraper on a schedule.

This is an alternative to using cron jobs and is useful for applications
that run continuously or in environments where cron is not available.

Requirements:
    pip install schedule
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
import schedule

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import logging configuration
try:
    from src.utils.logging_config import setup_logging, get_logger
except ImportError:
    # Simple logging setup if the import fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    def get_logger(name):
        return logging.getLogger(name)
    
    def setup_logging():
        pass

# Set up logging
setup_logging()
logger = get_logger(__name__)


def run_scraper():
    """
    Run the scraper script as a subprocess.
    """
    logger.info("Starting scheduled scraper run")
    
    # Get the path to the main script
    main_script = str(project_root / "src" / "main.py")
    
    # Get the Python executable
    python_executable = sys.executable
    
    try:
        # Run the scraper
        result = subprocess.run(
            [python_executable, main_script],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Log the output
        logger.info(f"Scraper completed successfully")
        logger.debug(f"Scraper output: {result.stdout}")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Scraper failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Failed to run scraper: {e}")
        return False


def setup_monthly_schedule():
    """
    Set up a monthly schedule to run the scraper on the 1st day of each month at midnight.
    """
    # Schedule the job to run monthly (at midnight on the 1st day of each month)
    schedule.every().month.at("00:00").do(run_scraper)
    logger.info("Scheduled scraper to run monthly at midnight on the 1st day")


def setup_weekly_schedule():
    """
    Set up a weekly schedule to run the scraper every Monday at midnight.
    """
    # Schedule the job to run weekly (at midnight every Monday)
    schedule.every().monday.at("00:00").do(run_scraper)
    logger.info("Scheduled scraper to run weekly at midnight every Monday")


def setup_daily_schedule():
    """
    Set up a daily schedule to run the scraper every day at midnight.
    """
    # Schedule the job to run daily (at midnight)
    schedule.every().day.at("00:00").do(run_scraper)
    logger.info("Scheduled scraper to run daily at midnight")


def setup_hourly_schedule():
    """
    Set up an hourly schedule to run the scraper every hour.
    """
    # Schedule the job to run hourly
    schedule.every().hour.do(run_scraper)
    logger.info("Scheduled scraper to run hourly")


def setup_custom_schedule(interval_minutes=30):
    """
    Set up a custom schedule to run the scraper at specified intervals.
    
    Args:
        interval_minutes: Interval in minutes between runs
    """
    # Schedule the job to run at the specified interval
    schedule.every(interval_minutes).minutes.do(run_scraper)
    logger.info(f"Scheduled scraper to run every {interval_minutes} minutes")


def main():
    """
    Main function to set up and run the scheduler.
    """
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run the Automated Product Data Scraper on a schedule using the 'schedule' library"
    )
    
    parser.add_argument(
        "--schedule-type",
        choices=["monthly", "weekly", "daily", "hourly", "custom"],
        default="monthly",
        help="Type of schedule to use (default: monthly)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval in minutes for custom schedule (default: 30)"
    )
    
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run the scraper immediately before starting the schedule"
    )
    
    args = parser.parse_args()
    
    # Set up the schedule based on the specified type
    if args.schedule_type == "monthly":
        setup_monthly_schedule()
    elif args.schedule_type == "weekly":
        setup_weekly_schedule()
    elif args.schedule_type == "daily":
        setup_daily_schedule()
    elif args.schedule_type == "hourly":
        setup_hourly_schedule()
    elif args.schedule_type == "custom":
        setup_custom_schedule(args.interval)
    
    # Run the scraper immediately if requested
    if args.run_now:
        logger.info("Running scraper immediately")
        run_scraper()
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    # Keep the script running and check for scheduled jobs
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    main()
