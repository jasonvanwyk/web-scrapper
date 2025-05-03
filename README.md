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
5. Copy `.env.example` to `.env` and configure your environment variables
6. Run the application: `python src/main.py`

## Configuration

The application uses environment variables for configuration. See `.env.example` for available options.

## License

[License information]
