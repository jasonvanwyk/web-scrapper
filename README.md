# Automated Product Data Scraper

A Python-based automation tool that scrapes product information from supplier websites and outputs standardized CSV files.

## Overview

This tool allows users to:
- Scrape product data from supplier websites (with or without authentication)
- Extract standardized product information (name, SKU, description, supplier, costs, etc.)
- Output data to CSV files and optionally download images
- Run on a schedule with minimal intervention

## Project Structure

```
.
├── src/                # Source code
│   ├── scrapers/       # Scraper modules
│   ├── http_client/    # HTTP client modules
│   ├── browser_automation/ # Browser automation modules
│   ├── config.py       # Configuration management
│   └── main.py         # Main entry point
├── tests/              # Test files
├── docs/               # Documentation
├── .env.example        # Example environment variables
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install Playwright browsers: `playwright install`
6. Copy `.env.example` to `.env` and configure your environment variables
7. Run the application: `python src/main.py`

## Scraper Types

The application supports two types of scrapers:

### Static Scraper

The `StaticScraper` is designed for websites where content is directly available in the HTML source. It uses the `requests` library to fetch pages and `BeautifulSoup` to parse the HTML.

### Dynamic Scraper

The `DynamicScraper` is designed for modern websites that rely on JavaScript to render content or require complex interactions. It uses `Playwright` for browser automation with the following features:

- Support for multiple browser engines (Chromium, Firefox, WebKit)
- Stealth mode to minimize bot detection
- Handling of complex interactions (clicks, form filling, etc.)
- Waiting for elements and page states

Configure the browser behavior in your `.env` file using the browser automation settings.

## Testing

### Unit Tests

Run the unit tests with:

```bash
python -m pytest tests/
```

### Integration Tests

For integration tests that use actual browser instances, you need to install the Playwright system dependencies first:

```bash
# Install Playwright system dependencies (requires sudo)
sudo ./scripts/install_playwright_deps.sh

# Run the integration tests
python -m pytest tests/integration/
```

If you want to skip the integration tests (e.g., in CI environments without browser support), you can set the `SKIP_INTEGRATION_TESTS` environment variable:

```bash
SKIP_INTEGRATION_TESTS=true python -m pytest tests/
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for available options.

## License

[License information]
