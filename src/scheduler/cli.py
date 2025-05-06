"""
Command-line interface for the scheduler module.

This module provides a command-line interface for creating and managing
cron jobs for the Automated Product Data Scraper.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Try both import paths to handle different execution contexts
try:
    from src.scheduler.scheduler import Scheduler, get_scheduler
    from src.utils.logging_config import setup_logging, get_logger
except ModuleNotFoundError:
    from scheduler.scheduler import Scheduler, get_scheduler
    from utils.logging_config import setup_logging, get_logger


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Scheduler for the Automated Product Data Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=Scheduler.explain_cron_format()
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create parser for the "create" command
    create_parser = subparsers.add_parser("create", help="Create a cron job")
    create_parser.add_argument(
        "--schedule", 
        default="0 0 1 * *",
        help="Cron schedule expression (default: monthly at midnight on the 1st)"
    )
    create_parser.add_argument(
        "--user", 
        help="User to run the cron job as (default: current user)"
    )
    create_parser.add_argument(
        "--comment", 
        default="Automated Product Data Scraper",
        help="Comment to add to the cron job for identification"
    )
    create_parser.add_argument(
        "--script-path", 
        help="Path to the main script to be scheduled"
    )
    create_parser.add_argument(
        "--log-dir", 
        help="Directory where logs should be stored"
    )
    
    # Create parser for the "remove" command
    remove_parser = subparsers.add_parser("remove", help="Remove a cron job")
    remove_parser.add_argument(
        "--user", 
        help="User whose crontab should be modified (default: current user)"
    )
    remove_parser.add_argument(
        "--comment", 
        default="Automated Product Data Scraper",
        help="Comment that identifies the cron job to remove"
    )
    
    # Create parser for the "list" command
    list_parser = subparsers.add_parser("list", help="List all cron jobs")
    list_parser.add_argument(
        "--user", 
        help="User whose crontab should be listed (default: current user)"
    )
    
    # Create parser for the "doc" command
    doc_parser = subparsers.add_parser("doc", help="Generate documentation for cron scheduling")
    doc_parser.add_argument(
        "--output-file", 
        default="docs/scheduling.md",
        help="File to write the documentation to (default: docs/scheduling.md)"
    )
    
    # Create parser for the "schedules" command
    schedules_parser = subparsers.add_parser("schedules", help="List common cron schedules")
    
    return parser.parse_args()


def main() -> None:
    """
    Main function for the scheduler CLI.
    """
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Parse command-line arguments
    args = parse_args()
    
    # If no command is specified, show help and exit
    if not args.command:
        print("Error: No command specified")
        print("Use --help to see available commands")
        sys.exit(1)
    
    try:
        # Handle the "create" command
        if args.command == "create":
            scheduler = get_scheduler(script_path=args.script_path, log_dir=args.log_dir)
            success = scheduler.create_cron_job(
                schedule=args.schedule,
                user=args.user,
                comment=args.comment
            )
            if success:
                print(f"Cron job created with schedule: {args.schedule}")
            else:
                print("Failed to create cron job")
                sys.exit(1)
        
        # Handle the "remove" command
        elif args.command == "remove":
            scheduler = get_scheduler()
            success = scheduler.remove_cron_job(
                user=args.user,
                comment=args.comment
            )
            if success:
                print("Cron job removed successfully")
            else:
                print("Failed to remove cron job")
                sys.exit(1)
        
        # Handle the "list" command
        elif args.command == "list":
            scheduler = get_scheduler()
            jobs = scheduler.list_cron_jobs(user=args.user)
            if jobs:
                print("Current cron jobs:")
                for job in jobs:
                    if job.strip():  # Skip empty lines
                        print(f"  {job}")
            else:
                print(f"No cron jobs found for {args.user or 'current user'}")
        
        # Handle the "doc" command
        elif args.command == "doc":
            scheduler = get_scheduler()
            doc = scheduler.generate_cron_documentation(output_file=args.output_file)
            print(f"Documentation generated and saved to {args.output_file}")
        
        # Handle the "schedules" command
        elif args.command == "schedules":
            print("Common cron schedules:")
            for cron_expr, description in Scheduler.get_common_schedules().items():
                print(f"  {cron_expr} : {description}")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
