"""
Scheduler module for the Automated Product Data Scraper.

This module provides functionality for scheduling the scraper to run at specified intervals
using various scheduling methods such as cron, Python schedule, or cloud schedulers.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

# Try both import paths to handle different execution contexts
try:
    from src.utils.logging_config import get_logger
except ModuleNotFoundError:
    from utils.logging_config import get_logger


class Scheduler:
    """
    Scheduler class for managing the execution schedule of the scraper.
    
    This class provides methods for creating and managing cron jobs and
    other scheduling options for the scraper.
    """
    
    def __init__(self, script_path: Optional[str] = None, log_dir: Optional[str] = None):
        """
        Initialize the scheduler.
        
        Args:
            script_path: Path to the main script to be scheduled. If None, 
                         defaults to the main.py in the project root.
            log_dir: Directory where logs should be stored. If None,
                     defaults to a 'logs' directory in the project root.
        """
        self.logger = get_logger(__name__)
        
        # If script_path is not provided, use the default main.py
        if script_path is None:
            # Get the project root directory (parent of src)
            project_root = Path(__file__).parent.parent.parent
            self.script_path = str(project_root / "src" / "main.py")
        else:
            self.script_path = script_path
            
        # If log_dir is not provided, use the default logs directory
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.log_dir = str(project_root / "logs")
        else:
            self.log_dir = log_dir
            
        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.logger.info(f"Scheduler initialized with script path: {self.script_path}")
        self.logger.info(f"Logs will be stored in: {self.log_dir}")
    
    def create_cron_job(self, 
                        schedule: str = "0 0 1 * *", 
                        user: Optional[str] = None,
                        comment: str = "Automated Product Data Scraper") -> bool:
        """
        Create a cron job to run the scraper on a schedule.
        
        Args:
            schedule: Cron schedule expression (default: "0 0 1 * *", which is monthly at midnight on the 1st)
            user: User to run the cron job as. If None, uses the current user.
            comment: Comment to add to the cron job for identification.
            
        Returns:
            bool: True if the cron job was created successfully, False otherwise.
            
        Note:
            This method requires the crontab command to be available on the system.
            The default schedule (0 0 1 * *) runs the scraper monthly at midnight on the 1st day.
        """
        try:
            # Get the Python executable path
            python_executable = sys.executable
            
            # Create the log file path
            log_file = os.path.join(self.log_dir, "scraper_cron.log")
            
            # Create the cron command
            # Redirect both stdout and stderr to the log file and append with timestamps
            cron_command = f"{python_executable} {self.script_path} >> {log_file} 2>&1"
            
            # Create a temporary file with the current crontab
            temp_crontab = "/tmp/scraper_crontab"
            
            # Export the current crontab
            if user:
                export_cmd = f"crontab -u {user} -l > {temp_crontab} 2>/dev/null || echo '' > {temp_crontab}"
            else:
                export_cmd = f"crontab -l > {temp_crontab} 2>/dev/null || echo '' > {temp_crontab}"
                
            subprocess.run(export_cmd, shell=True, check=False)
            
            # Add the new cron job with a comment
            with open(temp_crontab, "a") as f:
                f.write(f"\n# {comment}\n")
                f.write(f"{schedule} {cron_command}\n")
            
            # Install the new crontab
            if user:
                install_cmd = f"crontab -u {user} {temp_crontab}"
            else:
                install_cmd = f"crontab {temp_crontab}"
                
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Clean up the temporary file
            os.remove(temp_crontab)
            
            self.logger.info(f"Cron job created with schedule: {schedule}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create cron job: {e}", exc_info=True)
            return False
    
    def remove_cron_job(self, user: Optional[str] = None, 
                        comment: str = "Automated Product Data Scraper") -> bool:
        """
        Remove the scraper cron job.
        
        Args:
            user: User whose crontab should be modified. If None, uses the current user.
            comment: Comment that identifies the cron job to remove.
            
        Returns:
            bool: True if the cron job was removed successfully, False otherwise.
        """
        try:
            # Create a temporary file for the crontab
            temp_crontab = "/tmp/scraper_crontab"
            
            # Export the current crontab
            if user:
                export_cmd = f"crontab -u {user} -l > {temp_crontab} 2>/dev/null || echo '' > {temp_crontab}"
            else:
                export_cmd = f"crontab -l > {temp_crontab} 2>/dev/null || echo '' > {temp_crontab}"
                
            subprocess.run(export_cmd, shell=True, check=False)
            
            # Read the current crontab
            with open(temp_crontab, "r") as f:
                lines = f.readlines()
            
            # Filter out the scraper cron job and its comment
            filtered_lines = []
            skip_next = False
            for line in lines:
                if comment in line and line.strip().startswith("#"):
                    skip_next = True
                    continue
                if skip_next:
                    skip_next = False
                    continue
                filtered_lines.append(line)
            
            # Write the filtered crontab back
            with open(temp_crontab, "w") as f:
                f.writelines(filtered_lines)
            
            # Install the new crontab
            if user:
                install_cmd = f"crontab -u {user} {temp_crontab}"
            else:
                install_cmd = f"crontab {temp_crontab}"
                
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Clean up the temporary file
            os.remove(temp_crontab)
            
            self.logger.info("Cron job removed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove cron job: {e}", exc_info=True)
            return False
    
    def list_cron_jobs(self, user: Optional[str] = None) -> List[str]:
        """
        List all cron jobs for the user.
        
        Args:
            user: User whose crontab should be listed. If None, uses the current user.
            
        Returns:
            List[str]: A list of cron job entries.
        """
        try:
            # Create the crontab command
            if user:
                cmd = f"crontab -u {user} -l"
            else:
                cmd = "crontab -l"
                
            # Run the command and capture the output
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # If the command was successful, return the output as a list of lines
            if result.returncode == 0:
                return result.stdout.strip().split("\n")
            else:
                self.logger.warning(f"No crontab found for {user or 'current user'}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to list cron jobs: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_common_schedules() -> Dict[str, str]:
        """
        Get a dictionary of common cron schedules with descriptions.
        
        Returns:
            Dict[str, str]: A dictionary mapping cron expressions to descriptions.
        """
        return {
            "0 0 1 * *": "Monthly (midnight on the 1st day of each month)",
            "0 0 * * 1": "Weekly (midnight every Monday)",
            "0 0 * * *": "Daily (midnight every day)",
            "0 */12 * * *": "Twice daily (every 12 hours)",
            "0 */6 * * *": "Every 6 hours",
            "0 */1 * * *": "Hourly",
            "*/30 * * * *": "Every 30 minutes",
            "*/15 * * * *": "Every 15 minutes",
            "*/5 * * * *": "Every 5 minutes",
            "*/1 * * * *": "Every minute"
        }
    
    @staticmethod
    def explain_cron_format() -> str:
        """
        Provide an explanation of the cron format.
        
        Returns:
            str: A string explaining the cron format.
        """
        return """
        Cron Format Explanation:
        
        A cron expression consists of five fields separated by spaces:
        
        ┌───────────── minute (0 - 59)
        │ ┌───────────── hour (0 - 23)
        │ │ ┌───────────── day of the month (1 - 31)
        │ │ │ ┌───────────── month (1 - 12)
        │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
        │ │ │ │ │
        * * * * *
        
        Special characters:
        * : any value
        , : value list separator (e.g., "1,3,5")
        - : range of values (e.g., "1-5")
        / : step values (e.g., "*/2" means every 2 units)
        
        Examples:
        "0 0 1 * *" : Run at midnight on the 1st day of each month
        "0 0 * * 1" : Run at midnight every Monday
        "*/15 * * * *" : Run every 15 minutes
        """
    
    def generate_cron_documentation(self, output_file: Optional[str] = None) -> str:
        """
        Generate documentation for cron scheduling.
        
        Args:
            output_file: Optional file to write the documentation to.
            
        Returns:
            str: The generated documentation.
        """
        # Create the documentation
        doc = """# Scheduling the Automated Product Data Scraper

## Cron Job Configuration

The scraper can be scheduled to run automatically using cron jobs. This document explains how to set up and manage these schedules.

### Cron Format

{}

### Common Schedules

The following are common schedules you might want to use:

| Cron Expression | Description |
|----------------|-------------|
""".format(self.explain_cron_format())

        # Add the common schedules to the documentation
        for cron_expr, description in self.get_common_schedules().items():
            doc += f"| `{cron_expr}` | {description} |\n"
            
        # Add examples of how to use the scheduler
        doc += """
## Using the Scheduler

### Creating a Monthly Schedule

To schedule the scraper to run monthly (at midnight on the 1st day of each month):

```python
from src.scheduler.scheduler import Scheduler

# Initialize the scheduler
scheduler = Scheduler()

# Create a monthly cron job
scheduler.create_cron_job(schedule="0 0 1 * *", comment="Monthly Product Data Scraper")
```

### Creating a Weekly Schedule

To schedule the scraper to run weekly (at midnight every Monday):

```python
from src.scheduler.scheduler import Scheduler

# Initialize the scheduler
scheduler = Scheduler()

# Create a weekly cron job
scheduler.create_cron_job(schedule="0 0 * * 1", comment="Weekly Product Data Scraper")
```

### Removing a Scheduled Job

To remove a previously created cron job:

```python
from src.scheduler.scheduler import Scheduler

# Initialize the scheduler
scheduler = Scheduler()

# Remove the cron job
scheduler.remove_cron_job(comment="Monthly Product Data Scraper")
```

### Listing Current Cron Jobs

To list all current cron jobs:

```python
from src.scheduler.scheduler import Scheduler

# Initialize the scheduler
scheduler = Scheduler()

# List all cron jobs
jobs = scheduler.list_cron_jobs()
for job in jobs:
    print(job)
```

## Alternative Scheduling Methods

### Using Python's schedule Library

For applications that run continuously, you can use the `schedule` library:

```python
import schedule
import time
import subprocess
import sys

def run_scraper():
    subprocess.run([sys.executable, "path/to/src/main.py"])

# Schedule the job to run monthly
schedule.every().month.at("00:00").do(run_scraper)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Using Cloud Schedulers

For cloud deployments, consider using:

- **AWS**: AWS EventBridge or CloudWatch Events
- **GCP**: Cloud Scheduler
- **Azure**: Azure Functions with Timer trigger

These services provide reliable scheduling with additional monitoring and logging capabilities.
"""
        
        # Write to file if specified
        if output_file:
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            with open(output_file, "w") as f:
                f.write(doc)
            self.logger.info(f"Cron documentation written to {output_file}")
            
        return doc


# Convenience function to create a scheduler instance
def get_scheduler(script_path: Optional[str] = None, log_dir: Optional[str] = None) -> Scheduler:
    """
    Get a scheduler instance.
    
    Args:
        script_path: Path to the main script to be scheduled.
        log_dir: Directory where logs should be stored.
        
    Returns:
        Scheduler: A scheduler instance.
    """
    return Scheduler(script_path=script_path, log_dir=log_dir)
