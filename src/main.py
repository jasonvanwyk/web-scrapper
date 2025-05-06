"""
Main orchestrator module for the Automated Product Data Scraper.

This module serves as the entry point for the application, initializing logging,
loading configuration, and coordinating the scraping process.
"""

import logging
import sys
import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Fix the import to work when running from src directory
try:
    from src.config import config
    from src.scrapers.factory import get_scraper
    from src.storage.csv_writer import CSVWriter
    from src.utils.logging_config import setup_logging, get_logger
    from src.notifications.notification_manager import get_notification_manager
except ModuleNotFoundError:
    # When running directly from src directory
    from config import config
    from scrapers.factory import get_scraper
    from storage.csv_writer import CSVWriter
    from utils.logging_config import setup_logging, get_logger
    from notifications.notification_manager import get_notification_manager


def resolve_path(path: Path) -> Path:
    """
    Resolve a path to be absolute, handling both absolute and relative paths.
    
    Args:
        path: The path to resolve
        
    Returns:
        Path: The resolved absolute path
    """
    if not path.is_absolute():
        # If path is relative, make it relative to the project root, not the src directory
        project_root = Path(__file__).parent.parent
        return project_root / path
    return path


def main() -> None:
    """
    Main function that orchestrates the scraping process.
    """
    logger = get_logger(__name__)
    
    logger.info("Starting Automated Product Data Scraper")
    
    # Initialize summary data for notifications
    summary_data = {
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "suppliers": [],
        "total_products": 0,
        "successful_products": 0,
        "failed_products": 0,
        "total_suppliers": len(config.suppliers),
        "successful_suppliers": 0,
        "failed_suppliers": 0,
        "output_files": []
    }
    
    # Initialize notification manager if notifications are enabled
    notification_manager = None
    if config.notifications.enabled:
        notification_manager = get_notification_manager(config.notifications.model_dump())
        logger.info("Notifications enabled")
    
    # Resolve output directory path
    output_dir = resolve_path(Path(config.output.output_dir))
    
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Download images: {config.output.download_images}")
    
    if not config.suppliers:
        logger.warning("No suppliers configured. Please add supplier configurations.")
        
        # Send error notification if enabled
        if notification_manager and config.notifications.send_on_error:
            notification_manager.send_error_notification(
                subject="Scraper Error: No Suppliers Configured",
                message="The scraper was started but no suppliers were configured. Please add supplier configurations."
            )
        
        return
    
    logger.info(f"Found {len(config.suppliers)} supplier(s) to process")
    
    # Define the CSV headers for product data
    csv_headers = [
        "product_name", 
        "sku", 
        "description", 
        "supplier_name", 
        "cost", 
        "price", 
        "colorways", 
        "image_url"
    ]
    
    # Process each supplier using the ScraperFactory
    for supplier in config.suppliers:
        logger.info(f"Processing supplier: {supplier.name}")
        
        # Initialize supplier summary data
        supplier_summary = {
            "name": supplier.name,
            "status": "failed",  # Default to failed, will update to success if completed
            "products_found": 0,
            "products_processed": 0,
            "errors": []
        }
        
        try:
            # Get the appropriate scraper for this supplier
            scraper = get_scraper(supplier)
            logger.info(f"Using scraper: {scraper}")
            
            # If login is required, attempt to login
            if supplier.requires_login and supplier.username and supplier.password:
                logger.info(f"Attempting login for supplier: {supplier.name}")
                login_success = scraper.login(supplier.username, supplier.password)
                if not login_success:
                    error_msg = f"Login failed for supplier: {supplier.name}"
                    logger.error(error_msg)
                    supplier_summary["errors"].append(error_msg)
                    summary_data["suppliers"].append(supplier_summary)
                    summary_data["failed_suppliers"] += 1
                    continue
                logger.info(f"Login successful for supplier: {supplier.name}")
            
            # Initialize the CSV writer for this supplier
            csv_writer = CSVWriter(
                output_path=str(output_dir),
                filename_pattern=config.output.csv_filename_pattern,
                supplier_name=supplier.name,
                include_timestamp=config.output.include_timestamp,
                encoding=config.output.csv_encoding
            )
            
            # Open the CSV file and write the header
            with csv_writer:
                csv_writer.write_header(csv_headers)
                
                # Get product URLs (this will be implemented in future stories)
                # For now, we'll use a placeholder
                logger.info(f"Getting product URLs for supplier: {supplier.name}")
                product_urls = []  # This would be populated by scraper.get_product_urls()
                
                # For demonstration purposes, add a placeholder product URL
                product_urls.append("https://example.com/product1")
                
                # Update supplier summary with products found
                supplier_summary["products_found"] = len(product_urls)
                
                logger.info(f"Found {len(product_urls)} product URLs")
                
                # Process each product URL
                for url in product_urls:
                    try:
                        logger.info(f"Processing product URL: {url}")
                        
                        # Extract product data (this will be implemented in future stories)
                        # For now, we'll use placeholder data
                        product_data = {
                            "product_name": f"Product from {supplier.name}",
                            "sku": "SKU123",
                            "description": "This is a placeholder product description",
                            "supplier_name": supplier.name,
                            "cost": "99.99",
                            "price": "149.99",
                            "colorways": "Red, Blue, Green",
                            "image_url": "https://example.com/image.jpg"
                        }
                        
                        # Write the product data to the CSV file
                        csv_writer.write_row(product_data)
                        logger.info(f"Wrote product data for: {product_data['product_name']}")
                        
                        # Update summary data
                        summary_data["total_products"] += 1
                        summary_data["successful_products"] += 1
                        supplier_summary["products_processed"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing product URL {url}: {e}", exc_info=True)
                        
                        # Update summary data
                        summary_data["total_products"] += 1
                        summary_data["failed_products"] += 1
                        supplier_summary["errors"].append(f"Error processing {url}: {str(e)}")
                
                # Add the output file to the summary
                output_file = csv_writer.get_output_filename()
                if output_file:
                    summary_data["output_files"].append(output_file)
                
                # Update supplier status to success
                supplier_summary["status"] = "success"
                summary_data["successful_suppliers"] += 1
                
                logger.info(f"Completed processing supplier: {supplier.name}")
            
        except ImportError as e:
            error_msg = f"Failed to load scraper for supplier {supplier.name}: {e}"
            logger.error(error_msg)
            supplier_summary["errors"].append(error_msg)
            summary_data["failed_suppliers"] += 1
        except Exception as e:
            error_msg = f"Error processing supplier {supplier.name}: {e}"
            logger.error(error_msg, exc_info=True)
            supplier_summary["errors"].append(error_msg)
            summary_data["failed_suppliers"] += 1
        
        # Add supplier summary to the overall summary
        summary_data["suppliers"].append(supplier_summary)
    
    # Update end time and calculate duration
    end_time = datetime.datetime.now()
    summary_data["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    start_time = datetime.datetime.strptime(summary_data["start_time"], "%Y-%m-%d %H:%M:%S")
    duration = end_time - start_time
    summary_data["duration"] = str(duration)
    
    logger.info("Scraping process completed")
    logger.info(f"Total products processed: {summary_data['total_products']}")
    logger.info(f"Successful products: {summary_data['successful_products']}")
    logger.info(f"Failed products: {summary_data['failed_products']}")
    
    # Send notifications if enabled
    if notification_manager:
        # Send completion notification
        if config.notifications.send_on_completion and summary_data["successful_suppliers"] > 0:
            notification_manager.send_completion_notification(
                subject="Scraper Completed Successfully",
                message=f"The scraper has completed successfully. Processed {summary_data['total_products']} products from {summary_data['successful_suppliers']} suppliers."
            )
        
        # Send error notification if there were failures
        if config.notifications.send_on_error and summary_data["failed_suppliers"] > 0:
            notification_manager.send_error_notification(
                subject="Scraper Completed with Errors",
                message=f"The scraper completed with errors. {summary_data['failed_suppliers']} suppliers failed. See the summary for details."
            )
        
        # Send summary notification
        if config.notifications.send_summary:
            notification_manager.send_summary_notification(
                subject="Scraper Execution Summary",
                summary_data=summary_data
            )


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    try:
        # Run the main function
        main()
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"An error occurred: {e}", exc_info=True)
        
        # Send error notification if enabled
        try:
            if config.notifications.enabled and config.notifications.send_on_error:
                notification_manager = get_notification_manager(config.notifications.model_dump())
                notification_manager.send_error_notification(
                    subject="Scraper Failed with Critical Error",
                    message="The scraper encountered a critical error and had to terminate.",
                    error=e
                )
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {notify_error}", exc_info=True)
        
        sys.exit(1)
