# Automated Product Data Scraper -- Architecture Specification v1.1

## 1. Introduction

This architecture document (v1.1) refines the technical design for the **Automated Product Data Scraper** solution, originally outlined in v1.0 and based on the PRD. It incorporates findings from research into current best practices for web scraping, security, compliance, and scalability. It covers system components, data flows, an updated technology stack, module breakdown, deployment strategies, security considerations, compliance guidelines, and scaling options.

## 2. System Overview & Data Flow

The core data flow remains similar to v1.0, but with refinements in component interactions and robustness.

```mermaid
flowchart TD
subgraph Scheduling & Orchestration
Scheduler[Scheduler (Cron/Cloud/Airflow)] -->|Triggers| Orchestrator[Orchestrator (main.py)]
Orchestrator --> Config[Secure Config Loader (.env/Secrets Manager)]
Orchestrator --> Logger[Logging & Monitoring]
end

subgraph Scraping Core
Orchestrator -->|for each supplier| ScraperFactory[Scraper Factory]
ScraperFactory --> SupplierScraper[Supplier Scraper Module]
SupplierScraper --> HttpClient{HTTP Client / Browser Automation}
HttpClient -- Requests --> RequestHandler[RequestHandler (Requests + RetryLogic)]
HttpClient -- Playwright --> BrowserHandler[BrowserHandler (Playwright + Stealth)]
RequestHandler -->|Static HTML| TargetSite[Supplier Website]
BrowserHandler -->|Dynamic JS/CAPTCHA| TargetSite
TargetSite --> RequestHandler
TargetSite --> BrowserHandler
RequestHandler --> Parser[HTML/Data Parser (BeautifulSoup/LXML)]
BrowserHandler --> Parser
end

subgraph Data Processing & Output
Parser -->|Extracted Records| Transformer[Data Sanitizer & Validator]
Transformer --> CSVWriter[CSV Writer (Streaming)]
Transformer --> ImageHandler[Image Handler (URL/Download)]
CSVWriter --> OutputStore[Output Storage (Filesystem/Cloud Storage)]
ImageHandler --> OutputStore
end

subgraph Supporting Services
Logger --> LogStore[Log Aggregator (File/CloudWatch/etc.)]
Orchestrator --> Notifier[Notification Service (Email/Slack)]
HttpClient --> ProxyManager[Proxy Manager (Optional)]
BrowserHandler --> CaptchaSolver[CAPTCHA Solver Service (Optional)]
end

Logger -- Errors/Status --> Notifier
```

**Refined Flow:**

1. **Scheduler**: Triggers the orchestrator based on the defined schedule (e.g., monthly). Options include system cron, a cloud-native scheduler (AWS EventBridge, GCP Cloud Scheduler), or a workflow orchestrator like Apache Airflow for more complex needs.

2. **Orchestrator**: The main Python script. Initializes logging, loads configuration securely, and iterates through configured suppliers.

3. **Secure Config Loader**: Reads configuration (supplier URLs, output paths, settings) and credentials securely, prioritizing environment variables or a dedicated secrets management service over plaintext files in deployment. Uses python-dotenv for local .env files.

4. **Scraper Factory**: Dynamically loads the appropriate scraper module for each supplier based on the configuration.

5. **Supplier Scraper Module**: Encapsulates site-specific logic: login methods, navigation patterns (pagination), target URLs, and data extraction selectors/logic.

6. **HTTP Client / Browser Automation**: Abstracts the method of fetching web content.
   - **RequestHandler**: Uses requests (or potentially HTTPX for async benefits) with robust retry logic (e.g., using urllib3.util.retry or tenacity) and User-Agent rotation for fetching static HTML efficiently.
   - **BrowserHandler**: Uses Playwright (recommended over Selenium for modernity and anti-detection features) to control a headless browser for sites requiring JavaScript execution or complex interactions (including potential CAPTCHA handling). Includes stealth techniques to appear more like a regular user.

7. **Proxy Manager (Optional)**: Manages a pool of proxies (residential recommended for higher success rates) to rotate IP addresses, reducing the risk of blocks.

8. **CAPTCHA Solver Service (Optional)**: If CAPTCHAs are encountered, integrates with a third-party solving service (e.g., 2Captcha, Anti-Captcha) via API.

9. **Parser**: Uses BeautifulSoup or LXML (often faster) to parse HTML and extract raw data based on CSS selectors or XPath defined per supplier.

10. **Data Sanitizer & Validator**: Cleans, normalizes (e.g., numeric prices, consistent color lists), and validates extracted data against expected formats/types. Handles missing fields gracefully.

11. **CSV Writer**: Streams validated data rows incrementally to a UTF-8 encoded CSV file to handle large datasets without high memory usage.

12. **Image Handler**: Handles images based on configuration: either saves the image URL or downloads the image file. Uses efficient downloading (e.g., aiohttp for async downloads or standard requests).

13. **Output Storage**: Writes CSV files and potentially downloaded images to a configured location (local filesystem, network share, or cloud storage like S3/GCS). Considers timestamped filenames or overwrite/append strategies based on client needs.

14. **Logging & Monitoring**: Captures detailed logs (INFO, WARNING, ERROR levels) throughout the process. Uses standard Python logging, potentially configured to output to both file and console, or a centralized logging system in cloud deployments.

15. **Notification Service**: Sends notifications (e.g., email via smtplib, Slack webhook) on success, failure, or significant errors.

## 3. Component Breakdown (Refined)

### 3.1 Orchestrator (main.py)

- Entry point for the application.
- Initializes logging, secure configuration loading, and the chosen scheduler mechanism.
- Manages the overall workflow: iterates suppliers, invokes the factory, handles high-level exceptions.
- Coordinates notifications.

### 3.2 Secure Configuration Module

- Uses python-dotenv locally to load .env files. **Crucially, .env files must be in .gitignore**.
- In deployed environments, prioritizes OS environment variables or integrates with cloud secrets management services (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault).
- Uses Pydantic for validating configuration structure and types.
- Defines supplier configurations (URL, requires_login, specific selectors, scraper type: static/dynamic).

### 3.3 Scraper Modules (scrapers/)

- **BaseScraper**: Abstract base class defining core methods (login(), Maps(), extract_data(), get_product_urls(), handle_pagination()).
- **StaticScraper**: Concrete implementation using RequestHandler (requests/HTTPX).
- **DynamicScraper**: Concrete implementation using BrowserHandler (Playwright).
- **Supplier-Specific Scrapers** (supplier_a.py, etc.): Inherit from StaticScraper or DynamicScraper. Implement site-specific logic for login, navigation, pagination, and extraction using selectors/logic defined in config.

### 3.4 HTTP Client / Browser Automation Module

- **RequestHandler**: Wraps requests.Session or httpx.AsyncClient. Implements retry logic (e.g., Tenacity), User-Agent rotation, and timeout handling. Manages proxy usage if configured.
- **BrowserHandler**: Manages Playwright browser instances (e.g., Chromium). Implements page loading, waiting for elements, executing JavaScript, handling interactions, and incorporating stealth techniques. Manages proxy and CAPTCHA solver integration if configured.

### 3.5 Parser & Transformer Module

- Uses BeautifulSoup4 or LXML for parsing HTML/XML.
- Transformer functions sanitize data (strip whitespace, convert types, normalize formats like currency/dates) and validate against expected patterns. Implements graceful handling of missing or malformed data.

### 3.6 Storage Module

- **CSVWriter**: Uses Python's built-in csv module for efficient, streaming writes to CSV files, ensuring UTF-8 encoding. Handles header row creation.
- **ImageHandler**: Logic to either extract image URLs or download image files using requests or aiohttp for concurrency. Handles file naming conventions.
- **OutputStore Interface**: Abstract definition for where outputs are saved (local, S3, GCS), allowing easy swapping.

### 3.7 Scheduler Module / Integration

- If using cron: Relies on system configuration.
- If using Python schedule: Integrates within the Orchestrator's long-running process.
- If using Airflow or Cloud Schedulers: Configuration managed externally, triggering the script/container entry point.

### 3.8 Logging & Monitoring Module

- Uses Python's standard logging library.
- Configurable log levels and output destinations (file, console, cloud logging services like AWS CloudWatch).
- Includes contextual information (e.g., supplier name) in log messages.

### 3.9 Optional Modules

- **ProxyManager**: Rotates IPs from a provided list or proxy service API.
- **CaptchaSolver**: Interfaces with a third-party CAPTCHA solving service API.
- **NotificationClient**: Sends messages via Email (smtplib) or webhooks (Slack, etc.).

## 4. Technology Stack (v1.1)

| **Layer** | **Technology / Library** | **Rationale / Notes** |
|-----------|--------------------------|------------------------|
| **Language** | Python 3.9+ | Per PRD, widely used for scraping. |
| **Configuration** | Pydantic, python-dotenv | Validation, easy loading of .env locally. |
| **HTTP (Static)** | requests or HTTPX | Standard for HTTP requests. HTTPX offers async. |
| **Browser Automation** | Playwright | Handles dynamic JS sites, CAPTCHAs; modern alternative to Selenium. |
| **HTML/XML Parsing** | BeautifulSoup4, lxml | Robust HTML parsing. lxml is faster. |
| **Data Validation** | Pydantic (optional) | Ensures data integrity before writing. |
| **Scheduling** | cron, Python schedule, Cloud Scheduler, Airflow | Options based on complexity/reliability needs. |
| **Async IO** | asyncio, aiohttp | For concurrent image downloads or async HTTP (HTTPX). |
| **Retry Logic** | Tenacity or urllib3.util.retry | Robust handling of transient network errors. |
| **Data Storage (Output)** | Python csv module | Built-in, efficient CSV writing. |
| **Logging** | Python logging module | Standard Python logging. |
| **Secrets Management** | OS Env Vars, Cloud Secrets Manager | Recommended for production credentials (replaces insecure file storage). |
| **Containerization** | Docker (optional) | For packaging and consistent deployment. |
| **CI/CD** | GitHub Actions / GitLab CI / Jenkins | For automated testing and deployment. |
| **Optional Services** | Proxy Providers, CAPTCHA Solvers | External services to improve scraping success rate. |

## 5. Deployment & Infrastructure

- **Local / VM**: Suitable for development or small-scale use. Requires Python environment setup and manual scheduler configuration (e.g., cron). Manage secrets via environment variables or OS keyring.

- **Docker Container**: Recommended for consistent environments and easier deployment. Build an image containing the application and dependencies. Run using docker run or docker-compose. Manage secrets using Docker secrets or environment variables passed securely. Schedule using host cron calling docker exec, or a scheduler within the container.

- **Cloud Function / Serverless**: (e.g., AWS Lambda, GCP Cloud Functions) Suitable if individual supplier scrapes are short-lived. Triggered by cloud schedulers. Requires packaging code and dependencies; state management might be needed. Good for parallel execution.

- **Cloud VM / Instance**: Similar to local VM but hosted in the cloud. Provides more control. Use cloud-native scheduling and secrets management.

- **Workflow Orchestrator**: Deploying alongside Airflow (self-hosted or managed service like Astronomer, MWAA, Cloud Composer) provides robust scheduling, monitoring, retries, and UI.

## 6. Security Considerations (Enhanced)

- **Credential Management**: **Never hardcode credentials**. Use python-dotenv for local .env files (excluded from Git). For deployment, use OS environment variables injected securely by the infrastructure (Docker, K8s, Cloud platform) or retrieve from a dedicated secrets management service (e.g., AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault).

- **Politeness & Rate Limiting**:
  - Respect robots.txt directives. Make this configurable.
  - Implement delays (e.g., time.sleep()) between requests, ideally randomized, to avoid overwhelming servers. Configure delay ranges.
  - Limit concurrent requests, especially when using async operations or browser automation.
  - Use descriptive, non-generic User-Agents; rotate them realistically.

- **CAPTCHA & Blocking**:
  - Use Playwright with stealth settings to reduce bot detection.
  - Implement proxy rotation (preferably residential/mobile IPs) if blocking occurs.
  - Integrate CAPTCHA solving services as a fallback if CAPTCHAs are unavoidable, acknowledging cost and ethical considerations.

- **Input Sanitization**: Although primarily scraping, sanitize any configuration inputs (like URLs) to prevent potential injection issues if config formats become complex.

- **Output Handling**: Ensure output directories have correct permissions. Be mindful if writing to shared locations.

## 7. Compliance & Ethical Considerations

- **Terms of Service (ToS)**: **Review the ToS** for each target supplier website. Scraping may be explicitly prohibited. Proceeding against ToS carries legal risks. Prioritize suppliers where scraping is permitted or where ToS are ambiguous (browsewrap) and data is clearly public, accepting the residual risk. Avoid sites with clear prohibitions (clickwrap agreements against scraping).

- **Copyright**: Only extract factual product data as defined in the PRD. Do not scrape and republish extensive descriptive text, articles, or other potentially copyrighted content without permission or clear fair use justification.

- **Data Privacy (GDPR/CCPA)**:
  - **Crucially, avoid collecting any Personal Data** (information relating to an identifiable individual) unless there is an explicit, documented legal basis like consent (highly unlikely for scraping).
  - The defined scope (Product Name, SKU, Description, Supplier Name, Cost, Price, Colorways, Image URL) appears focused on product data, not personal data. **Maintain this strict focus.**
  - If any potentially personal data fields were ever considered, they must be excluded unless strict compliance (consent, transparency, minimization etc.) can be demonstrated.

- **robots.txt**: Adhere to Disallow directives for specified user agents as a standard practice of politeness.

## 8. Non-Functional & Scaling (Enhanced)

- **Maintainability**: Modular design (separation of concerns: config, orchestration, scraping, parsing, storage) facilitates updates and adding new suppliers. Use clear abstractions (BaseScraper). Ensure good code documentation and unit/integration tests.

- **Performance**:
  - Use requests/HTTPX for static sites where possible (faster than browser automation).
  - Utilize Playwright efficiently for dynamic sites.
  - Implement asynchronous operations (aiohttp, Playwright async, HTTPX) for I/O-bound tasks like image downloads or concurrent requests (respecting rate limits).
  - Use streaming CSV writing to handle large outputs.

- **Reliability**: Implement robust error handling, retries for transient issues, and clear logging/notifications. Use appropriate scheduling tools for automated recovery.

- **Scalability**:
  - **Current**: Scales by adding new supplier scraper modules. Runs sequentially per supplier.
  - **Future Paths**:
    - *Parallelism*: Run supplier scrapes in parallel processes or threads (limited by GIL for CPU-bound tasks, okay for I/O-bound) or using asyncio.
    - *Distributed Tasks*: For large numbers of suppliers or very long scrapes, use a task queue system (e.g., Celery with Redis/RabbitMQ) to distribute work across multiple workers/machines.
    - *Serverless*: Utilize cloud functions for highly parallel, independent scraping tasks per supplier/page.
    - *Framework*: Migrate to Scrapy if complex crawling, pipeline processing, or built-in scaling features become necessary.

*End of Architecture Specification v1.1.*
