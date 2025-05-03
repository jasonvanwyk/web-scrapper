"""
Main orchestrator module for the Automated Product Data Scraper.

This module serves as the entry point for the application, initializing logging,
loading configuration, and coordinating the scraping process.
"""

import logging
import sys
import os
from pathlib import Path

# Fix the import to work when running from src directory
try:
    from src.config import config
except ModuleNotFoundError:
    # When running directly from src directory
    from config import config


def setup_logging() -> None:
    """
    Set up logging configuration based on the application config.
    """
    log_level = getattr(logging, config.logging.level.upper(), logging.INFO)
    
    # Ensure output directory exists
    output_dir = Path(config.output.output_dir)
    if not output_dir.is_absolute():
        # If path is relative, make it relative to the project root, not the src directory
        project_root = Path(__file__).parent.parent
        output_dir = project_root / output_dir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(output_dir / "scraper.log"),
        ],
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at level: {config.logging.level}")


def main() -> None:
    """
    Main function that orchestrates the scraping process.
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Automated Product Data Scraper")
    
    # Resolve output directory path
    output_dir = Path(config.output.output_dir)
    if not output_dir.is_absolute():
        # If path is relative, make it relative to the project root, not the src directory
        project_root = Path(__file__).parent.parent
        output_dir = project_root / output_dir
    
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Download images: {config.output.download_images}")
    
    if not config.suppliers:
        logger.warning("No suppliers configured. Please add supplier configurations.")
        return
    
    logger.info(f"Found {len(config.suppliers)} supplier(s) to process")
    
    # Placeholder for supplier processing loop
    for supplier in config.suppliers:
        logger.info(f"Processing supplier: {supplier.name}")
        # In future stories, we'll use the ScraperFactory to get the appropriate scraper
        # and process each supplier
    
    logger.info("Scraping process completed")


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    try:
        # Run the main function
        main()
    except Exception as e:
        logging.getLogger(__name__).error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
