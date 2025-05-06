#!/usr/bin/env python3
"""
Example script for setting up a scheduled job for the Automated Product Data Scraper.

This script demonstrates how to use the scheduler module to create a cron job
that runs the scraper on a monthly basis.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the scheduler
from src.scheduler.scheduler import get_scheduler
from src.utils.logging_config import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Set up a scheduled job for the Automated Product Data Scraper"
    )
    
    parser.add_argument(
        "--schedule", 
        default="0 0 1 * *",
        help="Cron schedule expression (default: monthly at midnight on the 1st)"
    )
    parser.add_argument(
        "--user", 
        help="User to run the cron job as (default: current user)"
    )
    parser.add_argument(
        "--comment", 
        default="Automated Product Data Scraper",
        help="Comment to add to the cron job for identification"
    )
    parser.add_argument(
        "--log-dir", 
        default=str(project_root / "logs"),
        help="Directory where logs should be stored"
    )
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List current cron jobs instead of creating a new one"
    )
    parser.add_argument(
        "--remove", 
        action="store_true",
        help="Remove the cron job instead of creating a new one"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main function for the setup_schedule script.
    """
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Parse command-line arguments
    args = parse_args()
    
    # Get the path to the main script
    main_script = str(project_root / "src" / "main.py")
    
    # Create the scheduler
    scheduler = get_scheduler(script_path=main_script, log_dir=args.log_dir)
    
    try:
        # List current cron jobs
        if args.list:
            jobs = scheduler.list_cron_jobs(user=args.user)
            if jobs:
                print("Current cron jobs:")
                for job in jobs:
                    if job.strip():  # Skip empty lines
                        print(f"  {job}")
            else:
                print(f"No cron jobs found for {args.user or 'current user'}")
            return
        
        # Remove the cron job
        if args.remove:
            success = scheduler.remove_cron_job(
                user=args.user,
                comment=args.comment
            )
            if success:
                print("Cron job removed successfully")
            else:
                print("Failed to remove cron job")
                sys.exit(1)
            return
        
        # Create the cron job
        success = scheduler.create_cron_job(
            schedule=args.schedule,
            user=args.user,
            comment=args.comment
        )
        
        if success:
            print(f"Cron job created with schedule: {args.schedule}")
            print(f"The scraper will run according to the following schedule:")
            
            # Explain the schedule in human-readable terms
            schedules = scheduler.get_common_schedules()
            if args.schedule in schedules:
                print(f"  {schedules[args.schedule]}")
            else:
                print(f"  Custom schedule: {args.schedule}")
                
            print(f"Logs will be stored in: {args.log_dir}")
        else:
            print("Failed to create cron job")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
