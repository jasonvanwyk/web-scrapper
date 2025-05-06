# Scheduling the Automated Product Data Scraper

This document explains how to set up and manage automatic scheduling for the Automated Product Data Scraper. The scraper can be configured to run at regular intervals (e.g., monthly) using various scheduling methods.

## Cron Job Configuration

The primary method for scheduling the scraper is using cron jobs, which are a standard way to schedule tasks on Unix-like operating systems.

### Cron Format

A cron expression consists of five fields separated by spaces:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

Special characters:
* `*` : any value
* `,` : value list separator (e.g., "1,3,5")
* `-` : range of values (e.g., "1-5")
* `/` : step values (e.g., "*/2" means every 2 units)

### Common Schedules

| Cron Expression | Description |
|----------------|-------------|
| `0 0 1 * *` | Monthly (midnight on the 1st day of each month) |
| `0 0 * * 1` | Weekly (midnight every Monday) |
| `0 0 * * *` | Daily (midnight every day) |
| `0 */12 * * *` | Twice daily (every 12 hours) |
| `0 */6 * * *` | Every 6 hours |
| `0 */1 * * *` | Hourly |
| `*/30 * * * *` | Every 30 minutes |
| `*/15 * * * *` | Every 15 minutes |
| `*/5 * * * *` | Every 5 minutes |
| `*/1 * * * *` | Every minute |

## Setting Up a Schedule

### Using the Command-Line Interface

The scraper provides a command-line interface for creating and managing cron jobs:

#### Creating a Monthly Schedule

```bash
# Navigate to the project directory
cd /path/to/web-scrapper

# Create a monthly cron job (runs at midnight on the 1st day of each month)
python -m src.scheduler.cli create --schedule "0 0 1 * *"
```

#### Creating a Weekly Schedule

```bash
# Create a weekly cron job (runs at midnight every Monday)
python -m src.scheduler.cli create --schedule "0 0 * * 1"
```

#### Listing Current Cron Jobs

```bash
# List all current cron jobs
python -m src.scheduler.cli list
```

#### Removing a Cron Job

```bash
# Remove a previously created cron job
python -m src.scheduler.cli remove
```

#### Generating Documentation

```bash
# Generate documentation for cron scheduling
python -m src.scheduler.cli doc --output-file docs/custom_scheduling.md
```

#### Viewing Common Schedules

```bash
# List common cron schedules
python -m src.scheduler.cli schedules
```

### Using the Setup Script

For convenience, a setup script is provided that simplifies the process of creating a cron job:

```bash
# Navigate to the project directory
cd /path/to/web-scrapper

# Create a monthly cron job (runs at midnight on the 1st day of each month)
./scripts/setup_schedule.py

# Create a custom schedule
./scripts/setup_schedule.py --schedule "0 0 * * 1" --comment "Weekly Product Data Scraper"

# List current cron jobs
./scripts/setup_schedule.py --list

# Remove a cron job
./scripts/setup_schedule.py --remove
```

### Using the Scheduler API

You can also use the scheduler programmatically in your own scripts:

```python
from src.scheduler.scheduler import get_scheduler

# Initialize the scheduler
scheduler = get_scheduler()

# Create a monthly cron job
scheduler.create_cron_job(
    schedule="0 0 1 * *",
    comment="Monthly Product Data Scraper"
)

# List current cron jobs
jobs = scheduler.list_cron_jobs()
for job in jobs:
    print(job)

# Remove a cron job
scheduler.remove_cron_job(comment="Monthly Product Data Scraper")
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

To use this method, you'll need to install the `schedule` library:

```bash
pip install schedule
```

### Using Cloud Schedulers

For cloud deployments, consider using:

- **AWS**: AWS EventBridge or CloudWatch Events
- **GCP**: Cloud Scheduler
- **Azure**: Azure Functions with Timer trigger

These services provide reliable scheduling with additional monitoring and logging capabilities.

#### AWS EventBridge Example

1. Create an AWS Lambda function that runs your scraper
2. Set up an EventBridge rule with a cron expression:
   ```
   cron(0 0 1 * ? *)  # Runs at midnight on the 1st day of each month
   ```
3. Set the Lambda function as the target for the rule

#### GCP Cloud Scheduler Example

1. Deploy your scraper as a Cloud Function or Cloud Run service
2. Create a Cloud Scheduler job with a cron expression:
   ```
   0 0 1 * *  # Runs at midnight on the 1st day of each month
   ```
3. Set the HTTP endpoint of your function/service as the target

## Testing the Schedule

To test that your cron job is correctly set up without waiting for the scheduled time:

1. Create a test cron job with a schedule that will run in the next few minutes:
   ```bash
   python -m src.scheduler.cli create --schedule "*/5 * * * *" --comment "Test Scraper"
   ```

2. Wait for the job to run and check the logs in the configured log directory.

3. Once confirmed, remove the test job:
   ```bash
   python -m src.scheduler.cli remove --comment "Test Scraper"
   ```

4. Set up your actual production schedule.

## Troubleshooting

### Common Issues

1. **Cron job doesn't run**:
   - Check if the cron service is running: `systemctl status cron`
   - Verify the cron job was created: `crontab -l`
   - Check the system logs: `grep CRON /var/log/syslog`

2. **Permission issues**:
   - Ensure the script has execute permissions: `chmod +x /path/to/script.py`
   - Check if the user has permission to access required files and directories

3. **Path issues**:
   - Use absolute paths in cron jobs
   - Set the correct working directory in the script

### Viewing Cron Logs

Logs from the scheduled runs will be stored in the configured log directory (default: `logs/scraper_cron.log` in the project root).

To view the logs:

```bash
# View the last 50 lines of the log
tail -n 50 /path/to/web-scrapper/logs/scraper_cron.log

# Follow the log in real-time
tail -f /path/to/web-scrapper/logs/scraper_cron.log
```
