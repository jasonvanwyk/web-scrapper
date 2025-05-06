# Troubleshooting Guide for Automated Product Data Scraper

This guide provides solutions for common issues that may arise when using the Automated Product Data Scraper. Follow these steps to diagnose and resolve problems.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [Connection and Network Errors](#connection-and-network-errors)
4. [Authentication Failures](#authentication-failures)
5. [Scraping Issues](#scraping-issues)
6. [Output and Storage Problems](#output-and-storage-problems)
7. [Notification Errors](#notification-errors)
8. [Scheduling Problems](#scheduling-problems)
9. [Performance Concerns](#performance-concerns)
10. [Debugging Tips](#debugging-tips)

## Installation Issues

### Python Environment Setup

**Issue**: Unable to install dependencies or Python version conflicts.

**Solution**:
1. Ensure you're using Python 3.9 or higher:
   ```bash
   python --version
   ```

2. Create a virtual environment to avoid conflicts:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies with pip:
   ```bash
   pip install -r requirements.txt
   ```

4. If a specific package fails to install, try installing it separately:
   ```bash
   pip install package-name
   ```

### Module Import Errors

**Issue**: `ModuleNotFoundError` when running the scraper.

**Solution**:
1. Verify your Python path includes the project root:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```

2. Check that all dependencies are installed:
   ```bash
   pip list
   ```

3. Ensure you're running the script from the correct directory:
   ```bash
   cd /path/to/web-scrapper
   python src/main.py
   ```

## Configuration Problems

### Missing or Invalid Configuration

**Issue**: `ConfigError` or `ValidationError` when loading configuration.

**Solution**:
1. Verify your `.env` file exists and contains all required credentials.

2. Check the format of your configuration file against the examples in `examples/`.

3. Ensure all required fields are present:
   ```python
   # Minimum required configuration
   config = {
       "suppliers": [
           {
               "name": "supplier_name",
               "url": "https://example.com",
               "requires_login": False,
               "scraper_type": "static"
           }
       ],
       "output": {
           "path": "output/"
       }
   }
   ```

4. Validate your configuration using the built-in validation tool:
   ```bash
   python src/utils/validate_config.py path/to/config.json
   ```

### Environment Variables

**Issue**: Credentials not being loaded from environment variables.

**Solution**:
1. Verify that your `.env` file is in the project root and properly formatted:
   ```
   SMTP_USERNAME=your_email@example.com
   SMTP_PASSWORD=your_password
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
   ```

2. Ensure you're loading the `.env` file in your code:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. Check that environment variables are accessible:
   ```bash
   python -c "import os; print(os.environ.get('SMTP_USERNAME'))"
   ```

## Connection and Network Errors

### Request Failures

**Issue**: `ConnectionError`, `Timeout`, or `RequestException` when making HTTP requests.

**Solution**:
1. Verify your internet connection.

2. Check if the target website is accessible in a browser.

3. Increase the request timeout:
   ```python
   # In your configuration
   "http_client": {
       "timeout": 60,  # Seconds
       "retries": 3
   }
   ```

4. Add retry logic for transient errors:
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
   def make_request(url):
       # Your request code here
   ```

### Proxy Issues

**Issue**: Proxy connection failures or IP blocks.

**Solution**:
1. Verify your proxy configuration:
   ```python
   # In your configuration
   "proxies": {
       "http": "http://user:pass@proxy.example.com:8080",
       "https": "https://user:pass@proxy.example.com:8080"
   }
   ```

2. Test your proxy connection:
   ```bash
   curl -x http://user:pass@proxy.example.com:8080 https://api.ipify.org
   ```

3. Rotate proxies if you're experiencing IP blocks:
   ```python
   # Example proxy rotation
   proxies = [
       {"http": "http://proxy1.example.com:8080", "https": "https://proxy1.example.com:8080"},
       {"http": "http://proxy2.example.com:8080", "https": "https://proxy2.example.com:8080"}
   ]
   ```

## Authentication Failures

### Login Issues

**Issue**: Unable to log in to supplier websites.

**Solution**:
1. Verify your credentials are correct by logging in manually.

2. Check if the login process has changed on the website.

3. Enable debug logging to see the login process:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

4. Inspect the login form and update selectors if needed:
   ```python
   # Example login selectors
   login_selectors = {
       "username_field": "#username",
       "password_field": "#password",
       "submit_button": "button[type='submit']"
   }
   ```

### CAPTCHA Challenges

**Issue**: Login or navigation blocked by CAPTCHA.

**Solution**:
1. Use the browser automation mode instead of simple requests:
   ```python
   # In your configuration
   "scraper_type": "dynamic"  # Uses Playwright
   ```

2. Add stealth plugins to avoid detection:
   ```python
   # In BrowserHandler
   playwright.stealth_sync(page)
   ```

3. Consider implementing a CAPTCHA solver service integration if needed.

## Scraping Issues

### Selector Changes

**Issue**: Data not being extracted due to website HTML structure changes.

**Solution**:
1. Update your selectors to match the new structure:
   ```python
   # Example updated selectors
   selectors = {
       "product_name": ".product-title h1",  # Changed from .product-name
       "price": ".product-price .current-price",
       "sku": ".product-sku span"
   }
   ```

2. Use more robust selectors that are less likely to change:
   ```python
   # More robust selectors
   selectors = {
       "product_name": "[data-testid='product-title']",
       "price": "[data-testid='product-price']"
   }
   ```

3. Implement multiple fallback selectors:
   ```python
   def extract_product_name(soup):
       selectors = [
           ".product-title h1",
           ".product-name",
           "[data-testid='product-title']"
       ]
       for selector in selectors:
           element = soup.select_one(selector)
           if element:
               return element.text.strip()
       return None
   ```

### JavaScript-Rendered Content

**Issue**: Content not appearing in the HTML because it's rendered by JavaScript.

**Solution**:
1. Switch to dynamic scraping mode:
   ```python
   # In your configuration
   "scraper_type": "dynamic"  # Uses Playwright
   ```

2. Wait for specific elements to load:
   ```python
   # In BrowserHandler
   page.wait_for_selector(".product-price", state="visible", timeout=10000)
   ```

3. Execute JavaScript to extract data if needed:
   ```python
   # In BrowserHandler
   price = page.evaluate("() => document.querySelector('.product-price').innerText")
   ```

### Rate Limiting and Blocking

**Issue**: Being blocked or rate-limited by the website.

**Solution**:
1. Add random delays between requests:
   ```python
   import random
   import time
   
   time.sleep(random.uniform(2, 5))  # Random delay between 2-5 seconds
   ```

2. Respect robots.txt directives:
   ```python
   from urllib.robotparser import RobotFileParser
   
   def is_allowed(url):
       rp = RobotFileParser()
       rp.set_url(f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt")
       rp.read()
       return rp.can_fetch("*", url)
   ```

3. Use a realistic user agent:
   ```python
   headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
   }
   ```

## Output and Storage Problems

### File Permission Issues

**Issue**: Unable to write to output files due to permission errors.

**Solution**:
1. Check directory permissions:
   ```bash
   ls -la output/
   ```

2. Ensure the output directory exists and is writable:
   ```python
   import os
   os.makedirs("output", exist_ok=True)
   ```

3. Use absolute paths to avoid relative path issues:
   ```python
   from pathlib import Path
   output_path = Path(__file__).parent.parent / "output"
   output_path.mkdir(exist_ok=True)
   ```

### CSV Encoding Issues

**Issue**: Special characters appearing incorrectly in CSV files.

**Solution**:
1. Ensure UTF-8 encoding is used:
   ```python
   with open(file_path, 'w', encoding='utf-8', newline='') as f:
       writer = csv.writer(f)
       # Write data
   ```

2. Add a BOM (Byte Order Mark) for Excel compatibility:
   ```python
   with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
       writer = csv.writer(f)
       # Write data
   ```

### Image Download Failures

**Issue**: Images not downloading or corrupted.

**Solution**:
1. Verify image URLs are accessible:
   ```bash
   curl -I https://example.com/image.jpg
   ```

2. Handle redirects properly:
   ```python
   response = requests.get(url, allow_redirects=True)
   ```

3. Check for content type to ensure it's an image:
   ```python
   if 'image' not in response.headers.get('Content-Type', ''):
       logger.warning(f"URL {url} returned non-image content type: {response.headers.get('Content-Type')}")
   ```

4. Use streaming for large images:
   ```python
   with requests.get(url, stream=True) as response:
       with open(file_path, 'wb') as f:
           for chunk in response.iter_content(chunk_size=8192):
               f.write(chunk)
   ```

## Notification Errors

### Email Notification Failures

**Issue**: Email notifications not being sent.

**Solution**:
1. Verify SMTP credentials:
   ```python
   import smtplib
   
   with smtplib.SMTP("smtp.gmail.com", 587) as server:
       server.starttls()
       server.login("your_email@gmail.com", "your_password")
       # If no error, credentials are correct
   ```

2. For Gmail, ensure "Less secure app access" is enabled or use an App Password.

3. Check firewall settings to ensure SMTP ports are open.

4. Verify recipient email addresses are correct:
   ```python
   # In your configuration
   "notifications": {
       "email": [
           {
               "smtp_server": "smtp.gmail.com",
               "smtp_port": 587,
               "sender_email": "your_email@gmail.com",
               "recipient_emails": ["recipient1@example.com", "recipient2@example.com"],
               "username": "your_email@gmail.com",
               "password": "your_password"
           }
       ]
   }
   ```

### Slack Notification Issues

**Issue**: Slack notifications not being delivered.

**Solution**:
1. Verify your webhook URL is correct and active:
   ```bash
   curl -X POST -H 'Content-type: application/json' --data '{"text":"Test message"}' https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

2. Check that your Slack app has the necessary permissions.

3. Ensure your message format is correct:
   ```python
   payload = {
       "text": "Scraper completed successfully",
       "attachments": [
           {
               "color": "#36a64f",
               "title": "Scraper Summary",
               "text": "Processed 100 products from 5 suppliers"
           }
       ]
   }
   ```

## Scheduling Problems

### Cron Job Issues

**Issue**: Scheduled cron jobs not running.

**Solution**:
1. Verify your cron job is properly installed:
   ```bash
   crontab -l
   ```

2. Check system logs for cron errors:
   ```bash
   grep CRON /var/log/syslog
   ```

3. Ensure absolute paths are used in the cron command:
   ```
   0 0 1 * * /usr/bin/python /absolute/path/to/web-scrapper/src/main.py >> /absolute/path/to/web-scrapper/logs/scraper_cron.log 2>&1
   ```

4. Make sure the script has execute permissions:
   ```bash
   chmod +x /path/to/web-scrapper/src/main.py
   ```

### Scheduler Configuration

**Issue**: Scheduler not working as expected.

**Solution**:
1. Verify your scheduler configuration:
   ```python
   from src.scheduler.scheduler import Scheduler
   
   scheduler = Scheduler()
   print(scheduler.list_cron_jobs())
   ```

2. Test creating a cron job manually:
   ```python
   scheduler.create_cron_job(schedule="0 0 1 * *", comment="Monthly Product Data Scraper")
   ```

3. Check that the log directory exists and is writable:
   ```python
   import os
   log_dir = "/path/to/web-scrapper/logs"
   os.makedirs(log_dir, exist_ok=True)
   ```

## Performance Concerns

### Slow Scraping

**Issue**: Scraping process taking too long.

**Solution**:
1. Use static scraping (requests) instead of dynamic (Playwright) when possible:
   ```python
   # In your configuration
   "scraper_type": "static"  # Faster than "dynamic"
   ```

2. Implement concurrent requests for multiple products:
   ```python
   import concurrent.futures
   
   with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
       futures = [executor.submit(extract_data, url) for url in urls]
       for future in concurrent.futures.as_completed(futures):
           try:
               data = future.result()
               # Process data
           except Exception as e:
               logger.error(f"Error processing URL: {e}")
   ```

3. Optimize selectors to be more specific:
   ```python
   # More specific selectors are faster
   soup.select_one("#product-123 .price")  # Faster than
   soup.select(".price")  # Less specific
   ```

### Memory Usage

**Issue**: High memory usage during scraping.

**Solution**:
1. Use streaming for CSV writing instead of storing all data in memory:
   ```python
   with open(file_path, 'w', encoding='utf-8', newline='') as f:
       writer = csv.writer(f)
       writer.writerow(headers)
       for data in extract_data_generator():
           writer.writerow(data)
   ```

2. Process one product at a time instead of collecting all data first:
   ```python
   for url in product_urls:
       data = extract_data(url)
       write_to_csv(data)
       # Clear data from memory
       del data
   ```

3. Implement garbage collection for long-running processes:
   ```python
   import gc
   
   # After processing a batch
   gc.collect()
   ```

## Debugging Tips

### Enabling Debug Logs

To get more detailed logs for troubleshooting:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
```

### Testing Individual Components

Test specific components in isolation:

```bash
# Test a specific scraper
python -c "from src.scrapers.static_scraper import StaticScraper; scraper = StaticScraper('test', 'https://example.com'); print(scraper.get_product_urls())"

# Test the notification system
python -c "from src.notifications.factory import create_email_notifier; notifier = create_email_notifier(smtp_server='smtp.gmail.com', smtp_port=587, sender_email='test@gmail.com', recipient_emails=['recipient@example.com'], username='test@gmail.com', password='password'); notifier.send_completion_notification('Test', 'This is a test')"
```

### Using the Interactive Debugger

Use Python's built-in debugger for interactive debugging:

```python
import pdb

# Add this line where you want to start debugging
pdb.set_trace()
```

Or use the more advanced debugger from IPython:

```python
from IPython.core.debugger import set_trace

# Add this line where you want to start debugging
set_trace()
```

### Checking Website Changes

If a scraper suddenly stops working, check if the website structure has changed:

1. Compare the current HTML with a previously working version.
2. Use browser developer tools to inspect the elements.
3. Check for JavaScript-rendered content that might not be visible in the static HTML.

### Common Error Messages and Solutions

| Error Message | Possible Cause | Solution |
|---------------|----------------|----------|
| `ConnectionError: Max retries exceeded` | Network issues or site blocking | Implement exponential backoff, use proxies |
| `NoSuchElementException` | Element not found in page | Update selectors, wait for elements to load |
| `TimeoutException` | Page or element taking too long to load | Increase timeout, check network conditions |
| `PermissionError: [Errno 13]` | File permission issues | Check directory permissions |
| `UnicodeEncodeError` | Character encoding issues | Use UTF-8 encoding for all file operations |
| `ModuleNotFoundError` | Missing dependencies | Install required packages, check import paths |
| `JSONDecodeError` | Invalid JSON response | Check API response format, handle non-JSON responses |

## Getting Additional Help

If you're still experiencing issues after trying the solutions in this guide:

1. Check the project's GitHub issues for similar problems and solutions.
2. Review the documentation in the `docs/` directory for specific component details.
3. Run the test suite to verify component functionality:
   ```bash
   pytest tests/
   ```
4. Enable verbose logging and share the logs when asking for help.
