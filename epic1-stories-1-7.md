# Story 1: Project Setup & Core Structure

## Story

**As a** Development Team,
**I want** the foundational project structure, configuration management, and core orchestration logic set up,
**so that** we have a consistent environment and entry point for building the scraper application.

## Status

Draft

## Context

This initial story establishes the skeleton of the "Automated Product Data Scraper" application. It involves creating the basic directory structure, setting up environment configuration handling using Pydantic and `python-dotenv`[cite: 57], initializing the main orchestrator script (`main.py`), and ensuring basic logging is configured[cite: 30, 54]. This adheres to the modular design principles outlined in the architecture [cite: 86] and prepares the groundwork for subsequent development, including supplier-specific scrapers and data handling modules. Secure configuration handling is paramount, ensuring `.env` files are gitignored [cite: 35] and prioritizing environment variables or secrets managers in production[cite: 36, 68].

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] A standard Python project structure (e.g., `src/`, `tests/`, `requirements.txt`, `.gitignore`) is created and committed to the repository.
2. - [ ] `.gitignore` file includes `.env`, `__pycache__/`, `*.pyc`, and common OS/IDE files.
3. - [ ] `requirements.txt` includes necessary base libraries like `python-dotenv`[cite: 15, 57], `pydantic`[cite: 37, 57], and `requests`[cite: 57].
4. - [ ] A `src/` directory contains the initial application modules.
5. - [ ] A `src/config.py` module exists using Pydantic for configuration validation [cite: 37] and `python-dotenv` for loading `.env` files[cite: 15, 35].
6. - [ ] A placeholder `.env.example` file shows required environment variables (e.g., `LOG_LEVEL`, `OUTPUT_DIR`).
7. - [ ] A `src/main.py` file exists as the main orchestrator entry point[cite: 6, 33].
8. - [ ] Basic logging (using Python's `logging` module [cite: 54]) is configured in `main.py` to output to the console, controllable via an environment variable (e.g., `LOG_LEVEL`).
9. - [ ] The orchestrator (`main.py`) successfully initializes logging and loads configuration via the config module upon execution.

## Subtasks

1. - [ ] Initialize Git repository.
2. - [ ] Create base project structure (`src/`, `tests/`, `docs/`, `.gitignore`, `README.md`, `requirements.txt`).
3. - [ ] Configure `.gitignore`.
4. - [ ] Add initial dependencies (`python-dotenv`, `pydantic`, `requests`) to `requirements.txt`.
5. - [ ] Implement `src/config.py`:
   1. - [ ] Define Pydantic models for configuration settings.
   2. - [ ] Implement logic to load settings from `.env` [cite: 15, 35] and environment variables[cite: 36].
6. - [ ] Create `.env.example` file.
7. - [ ] Implement `src/main.py`:
   1. - [ ] Add script entry point (`if __name__ == "__main__":`).
   2. - [ ] Initialize basic Python logging[cite: 30, 54].
   3. - [ ] Import and instantiate configuration from `src/config.py`.
   4. - [ ] Log a startup message.
8. - [ ] Create initial (empty) test files in `tests/`.

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for the configuration loading logic.
* Basic integration test confirming `main.py` runs without errors and logs output.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 2: Abstract Base Scraper & Factory

## Story

**As a** Developer,
**I want** an abstract base class for scrapers and a factory pattern for instantiating specific scrapers,
**so that** we enforce a consistent interface for all scrapers and can dynamically load the correct scraper module per supplier.

## Status

Draft

## Context

Building on the project structure, this story introduces core abstractions outlined in the architecture[cite: 38, 86]. An `Abstract Base Class (ABC)` named `BaseScraper` will define the standard methods required for any scraper implementation (e.g., `login`, `extract_data`, `get_product_urls`)[cite: 38]. This promotes consistency and simplifies the orchestrator's interaction with different scraper types. A `ScraperFactory` [cite: 7, 15] will be implemented to dynamically import and instantiate the appropriate supplier-specific scraper class based on configuration, decoupling the orchestrator from concrete scraper implementations.

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] A `src/scrapers/base_scraper.py` module exists containing an abstract base class `BaseScraper`.
2. - [ ] `BaseScraper` defines abstract methods like `login()`, `extract_data()`, `get_product_urls()`, `handle_pagination()` as specified in the architecture[cite: 38].
3. - [ ] `BaseScraper` potentially includes common utility methods or properties (e.g., shared HTTP client session, logger instance).
4. - [ ] A `src/scrapers/factory.py` module exists containing a `ScraperFactory` class or function[cite: 15].
5. - [ ] The `ScraperFactory` can take a supplier configuration object as input.
6. - [ ] The `ScraperFactory` dynamically imports and instantiates the correct scraper class (e.g., based on a `scraper_type` or module name field in the supplier config).
7. - [ ] The factory raises an appropriate error if the specified scraper module/class cannot be found or instantiated.
8. - [ ] The `Orchestrator` (`main.py`) is updated to use the `ScraperFactory` to get scraper instances for configured suppliers (in a placeholder loop).

## Subtasks

1. - [ ] Create `src/scrapers/` directory and `__init__.py`.
2. - [ ] Implement `src/scrapers/base_scraper.py`:
   1. - [ ] Define `BaseScraper` using `abc.ABC`.
   2. - [ ] Define required abstract methods (`@abc.abstractmethod`)[cite: 38].
   3. - [ ] Add type hints for methods.
3. - [ ] Implement `src/scrapers/factory.py`:
   1. - [ ] Define `ScraperFactory` (class or function).
   2. - [ ] Implement dynamic module/class loading logic (e.g., using `importlib`).
   3. - [ ] Add error handling for loading failures.
4. - [ ] Update `src/config.py` to include a placeholder for supplier configurations (list of dicts/Pydantic models), including a field to identify the scraper class/module (e.g., `supplier_module_name`).
5. - [ ] Update `src/main.py`:
   1. - [ ] Import `ScraperFactory`.
   2. - [ ] Add a loop to iterate through (placeholder) supplier configurations.
   3. - [ ] Inside the loop, call the factory to get a scraper instance.
   4. - [ ] Add basic logging for factory usage.
6. - [ ] Add unit tests for the `ScraperFactory`.

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for the `ScraperFactory` covering successful instantiation and error handling scenarios.
* Ensure `BaseScraper` cannot be instantiated directly.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 3: Static HTTP Scraper Implementation

## Story

**As a** Developer,
**I want** a concrete scraper implementation for handling websites that load content via static HTML, using the `requests` library,
**so that** we can efficiently scrape simple websites without needing browser automation.

## Status

Draft

## Context

This story creates the first concrete implementation of the `BaseScraper`, designed for websites where product data is available directly in the initial HTML source. Following the architecture[cite: 39, 18], this `StaticScraper` will inherit from `BaseScraper` and use the `requests` library (or potentially HTTPX [cite: 18, 57]) via a dedicated `RequestHandler` module[cite: 18, 42]. The `RequestHandler` will encapsulate `requests.Session` logic, including User-Agent rotation, timeout handling, and basic retry mechanisms[cite: 43, 71]. This module is crucial for efficient and polite scraping of non-JavaScript-heavy sites.

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] A `src/http_client/request_handler.py` module exists.
2. - [ ] `RequestHandler` class initializes a `requests.Session` (or `httpx.Client`).
3. - [ ] `RequestHandler` implements methods for common HTTP verbs (e.g., `get`, `post`).
4. - [ ] `RequestHandler` incorporates configurable User-Agent rotation (using a list of agents)[cite: 43, 72].
5. - [ ] `RequestHandler` includes configurable request timeouts[cite: 43].
6. - [ ] `RequestHandler` implements basic retry logic for transient network errors/specific HTTP status codes (e.g., using `Tenacity` or `urllib3.util.retry`)[cite: 18, 43, 57].
7. - [ ] A `src/scrapers/static_scraper.py` module exists containing a `StaticScraper` class inheriting from `BaseScraper`.
8. - [ ] `StaticScraper` constructor accepts and utilizes an instance of `RequestHandler`.
9. - [ ] `StaticScraper` implements the abstract methods defined in `BaseScraper` (even if just with placeholder logic or raising `NotImplementedError` initially for methods like `extract_data`).
10. - [ ] `StaticScraper` uses the `RequestHandler` instance to make HTTP requests in its methods (e.g., in a basic `Workspace_page` method).

## Subtasks

1. - [ ] Create `src/http_client/` directory and `__init__.py`.
2. - [ ] Implement `src/http_client/request_handler.py`:
   1. - [ ] Define `RequestHandler` class.
   2. - [ ] Initialize `requests.Session` in `__init__`.
   3. - [ ] Implement `get`/`post` methods wrapping session calls.
   4. - [ ] Add configuration parameters for User-Agents, timeouts, retry attempts/statuses.
   5. - [ ] Integrate User-Agent rotation logic[cite: 43, 72].
   6. - [ ] Integrate retry logic (e.g., using `Tenacity` decorators)[cite: 43, 57, 90].
3. - [ ] Implement `src/scrapers/static_scraper.py`:
   1. - [ ] Define `StaticScraper` inheriting from `BaseScraper`.
   2. - [ ] Implement `__init__` to accept `RequestHandler`.
   3. - [ ] Provide concrete implementations for abstract methods from `BaseScraper`, using the `RequestHandler` for network calls. Start with placeholder logic (e.g., log method calls).
4. - [ ] Add unit tests for `RequestHandler` (mocking `requests`).
5. - [ ] Add basic unit tests for `StaticScraper` (mocking `RequestHandler`).

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for `RequestHandler` covering User-Agent rotation, timeout handling, and retry logic.
* Unit tests for `StaticScraper` confirming it uses the `RequestHandler`.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 4: Dynamic Browser Scraper Implementation (Playwright)

## Story

**As a** Developer,
**I want** a concrete scraper implementation using Playwright for handling websites that require JavaScript execution or complex interactions,
**so that** we can scrape dynamic websites effectively.

## Status

Draft

## Context

This story introduces the `DynamicScraper`, designed for modern websites relying heavily on JavaScript to render content or requiring user interactions (like button clicks to load data) that `requests` cannot handle. Following the architecture[cite: 39, 19], this scraper will inherit from `BaseScraper` and utilize `Playwright` [cite: 19, 57] via a dedicated `BrowserHandler` module[cite: 44]. The `BrowserHandler` will manage Playwright browser instances, page navigation, waiting for elements, JavaScript execution, and incorporating stealth techniques to minimize bot detection[cite: 20, 44, 73]. This component is essential for tackling more complex target sites.

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] `Playwright` is added to `requirements.txt` and installed.
2. - [ ] A `src/browser_automation/browser_handler.py` module exists.
3. - [ ] `BrowserHandler` class manages Playwright instances (launching browsers, creating contexts/pages).
4. - [ ] `BrowserHandler` provides methods for core browser actions (e.g., `goto`, `wait_for_selector`, `click`, `get_content`, `close`).
5. - [ ] `BrowserHandler` incorporates basic Playwright stealth/anti-detection configurations where possible[cite: 20, 44, 73].
6. - [ ] `BrowserHandler` includes configurable timeouts for Playwright operations.
7. - [ ] A `src/scrapers/dynamic_scraper.py` module exists containing a `DynamicScraper` class inheriting from `BaseScraper`.
8. - [ ] `DynamicScraper` constructor accepts and utilizes an instance of `BrowserHandler`.
9. - [ ] `DynamicScraper` implements the abstract methods defined in `BaseScraper` using the `BrowserHandler` for browser interactions (e.g., fetching page content via `browser_handler.get_content()`).
10. - [ ] Playwright browsers/contexts/pages are properly closed/cleaned up by `BrowserHandler` or `DynamicScraper`.

## Subtasks

1. - [ ] Add `playwright` to `requirements.txt`.
2. - [ ] Run `playwright install` to download necessary browser binaries (document this step in README).
3. - [ ] Create `src/browser_automation/` directory and `__init__.py`.
4. - [ ] Implement `src/browser_automation/browser_handler.py`:
   1. - [ ] Define `BrowserHandler` class.
   2. - [ ] Implement methods to manage Playwright lifecycle (`launch`, `new_page`, `close`). Consider async context managers (`async with`).
   3. - [ ] Implement wrapper methods for common Playwright actions (`goto`, `click`, `wait_for_selector`, `content`, etc.) adding error handling and logging[cite: 44].
   4. - [ ] Add configuration options (e.g., browser type, headless mode, timeouts).
   5. - [ ] Research and apply basic Playwright stealth options[cite: 20, 73].
5. - [ ] Implement `src/scrapers/dynamic_scraper.py`:
   1. - [ ] Define `DynamicScraper` inheriting from `BaseScraper`.
   2. - [ ] Implement `__init__` to accept `BrowserHandler`.
   3. - [ ] Provide concrete implementations for abstract methods, using the `BrowserHandler` for browser interactions. Start with placeholder logic.
6. - [ ] Add basic unit tests for `BrowserHandler` (mocking Playwright objects where feasible, or focusing on logic).
7. - [ ] Add basic unit tests for `DynamicScraper` (mocking `BrowserHandler`).

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for `BrowserHandler` focusing on lifecycle management and action wrapping logic.
* Integration tests might be needed to verify actual Playwright browser interaction (can be slower and run separately).
* Unit tests for `DynamicScraper` confirming it uses the `BrowserHandler`.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 5: HTML Parsing & Data Transformation Module

## Story

**As a** Developer,
**I want** a dedicated module for parsing HTML content and transforming/sanitizing the extracted data,
**so that** scraper modules can delegate parsing logic and we ensure data consistency and cleanliness before output.

## Status

Draft

## Context

Once raw HTML content is fetched (by either `StaticScraper` or `DynamicScraper`), it needs to be parsed to extract the required data fields (Product Name, SKU, Description, etc. [cite: 83]). This story creates a `Parser & Transformer` module responsible for this task. It will utilize libraries like `BeautifulSoup4` or `lxml` [cite: 23, 45, 57] for efficient HTML parsing based on selectors defined in the supplier configuration[cite: 37]. Crucially, this module also includes functions to sanitize (e.g., strip whitespace, convert currency strings to numbers [cite: 24, 46]) and validate [cite: 24] the extracted data, handling missing or malformed fields gracefully [cite: 25, 47] before the data is passed on for storage.

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] `BeautifulSoup4` and `lxml` are included in `requirements.txt`.
2. - [ ] A `src/parser/` directory exists with `__init__.py`.
3. - [ ] A `src/parser/html_parser.py` module contains functions or a class for parsing HTML.
4. - [ ] Parsing functions accept HTML content (string) and selectors (e.g., CSS selectors) as input.
5. - [ ] Parsing functions use `BeautifulSoup4` or `lxml` to find elements and extract text/attributes[cite: 23, 45].
6. - [ ] Parsing functions handle cases where selectors don't find any elements (return default value like `None` or empty string).
7. - [ ] A `src/parser/transformer.py` module contains functions for data cleaning and validation[cite: 24, 46].
8. - [ ] Transformer functions exist for common tasks (e.g., `strip_whitespace`, `to_float`, `normalize_currency`, `validate_sku_format`).
9. - [ ] Transformer functions handle potential errors during conversion (e.g., `ValueError` when converting text to float) gracefully[cite: 47].
10. - [ ] Scraper modules (`StaticScraper`, `DynamicScraper`, or their future children) are updated to utilize the `html_parser` and `transformer` modules within their `extract_data` methods (or similar).

## Subtasks

1. - [ ] Add `beautifulsoup4` and `lxml` to `requirements.txt`.
2. - [ ] Create `src/parser/` directory and `__init__.py`.
3. - [ ] Implement `src/parser/html_parser.py`:
   1. - [ ] Define parsing functions (e.g., `extract_text`, `extract_attribute`).
   2. - [ ] Use `BeautifulSoup` or `lxml` for element selection (e.g., `soup.select_one()`).
   3. - [ ] Implement error handling for `None` results from selectors.
4. - [ ] Implement `src/parser/transformer.py`:
   1. - [ ] Define various data transformation functions (cleaning, type conversion, normalization)[cite: 24, 46].
   2. - [ ] Add validation functions (e.g., using regex or simple checks).
   3. - [ ] Ensure functions handle potential input errors (e.g., `None`, incorrect types)[cite: 47].
5. - [ ] Refactor placeholder `extract_data` methods in `StaticScraper` and `DynamicScraper` to demonstrate usage:
   1. - [ ] Accept HTML content.
   2. - [ ] Call `html_parser` functions with example selectors.
   3. - [ ] Call `transformer` functions on the results.
   4. - [ ] Return a structured dictionary of extracted (placeholder) data.
6. - [ ] Add unit tests for `html_parser` functions (using sample HTML).
7. - [ ] Add unit tests for `transformer` functions covering various inputs and edge cases.

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for HTML parsing functions with different HTML snippets and selectors.
* Unit tests for data transformation functions covering expected inputs, edge cases (None, empty strings), and error handling.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 6: CSV Output Storage Module

## Story

**As a** Developer,
**I want** a module responsible for writing the extracted and transformed product data to CSV files,
**so that** the scraped data can be persistently stored in a structured format as required.

## Status

Draft

## Context

After data is extracted and transformed, it needs to be saved. This story focuses on implementing the `Storage Module`, specifically the `CSVWriter` component, as defined in the architecture[cite: 47]. This writer will handle the creation and appending of data to CSV files efficiently. It should use Python's built-in `csv` module [cite: 57] and implement streaming writes to handle potentially large datasets without consuming excessive memory[cite: 25, 89]. Configuration options for the output directory and filename conventions (e.g., timestamped [cite: 29]) should be included. UTF-8 encoding must be enforced[cite: 25, 47].

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] A `src/storage/` directory exists with `__init__.py`.
2. - [ ] A `src/storage/csv_writer.py` module exists containing a `CSVWriter` class.
3. - [ ] `CSVWriter` constructor takes configuration parameters like output path and filename pattern.
4. - [ ] `CSVWriter` has methods like `open()`, `write_header(headers)`, `write_row(data_dict)`, and `close()`.
5. - [ ] The `write_row` method accepts a dictionary and writes it according to the header order.
6. - [ ] CSV files are opened with `utf-8` encoding[cite: 25, 47].
7. - [ ] The writer uses `csv.DictWriter` (or similar logic) for writing rows based on dictionary keys.
8. - [ ] Files are handled using context managers (`with open(...)`) to ensure they are closed properly.
9. - [ ] Output directory is created if it doesn't exist.
10. - [ ] The Orchestrator (`main.py`) is updated to instantiate and use the `CSVWriter` to save placeholder data generated by the scrapers.

## Subtasks

1. - [ ] Create `src/storage/` directory and `__init__.py`.
2. - [ ] Implement `src/storage/csv_writer.py`:
   1. - [ ] Define `CSVWriter` class.
   2. - [ ] Implement `__init__` to store output path, filename details.
   3. - [ ] Implement `open`/`close` methods (potentially using context manager protocol `__enter__`, `__exit__`).
   4. - [ ] Implement `write_header` using `csv.DictWriter.writeheader`.
   5. - [ ] Implement `write_row` using `csv.DictWriter.writerow`, ensuring UTF-8 encoding[cite: 25, 47].
   6. - [ ] Add logic to create the output directory (`os.makedirs(exist_ok=True)`).
   7. - [ ] Add logic for filename generation (e.g., based on supplier and timestamp [cite: 29]).
3. - [ ] Update `src/main.py`:
   1. - [ ] Import `CSVWriter`.
   2. - [ ] Instantiate `CSVWriter` based on configuration (add output path to config).
   3. - [ ] In the supplier loop, after getting placeholder data from the scraper, call `csv_writer.write_row()`.
   4. - [ ] Ensure the writer is properly opened/closed (e.g., using a `with` statement around the supplier loop or inside it).
4. - [ ] Add unit tests for `CSVWriter` (mocking file system operations using `unittest.mock` or `pyfakefs`).

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for `CSVWriter` covering file/directory creation, header writing, row writing (including handling different data types), and UTF-8 encoding.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...

---

# Story 7: Basic Image Handling (URL Extraction)

## Story

**As a** Developer,
**I want** the system to extract image URLs during scraping and include them in the output CSV,
**so that** the primary image associated with each product is recorded alongside other data.

## Status

Draft

## Context

This story addresses the basic requirement of handling product images by extracting their URLs. Based on the architecture[cite: 26, 48], the `Parser & Transformer` module should be extended to identify and extract image source URLs (`src` attributes from `<img>` tags, typically) based on configured selectors. The `ImageHandler` logic within the `Storage Module`[cite: 48], for this story, will simply involve ensuring the extracted URL is passed through and included as a column in the CSV output generated by the `CSVWriter`. Downloading the actual image files [cite: 26, 48] will be handled in a separate, subsequent story if required.

## Estimation

Story Points: {Story Points (1 SP=1 day of Human Development, or 10 minutes of AI development)}

## Acceptance Criteria

1. - [ ] `src/parser/html_parser.py` includes a function (e.g., `extract_image_url`) specifically for extracting the `src` attribute from an image element identified by a selector.
2. - [ ] The parsing function handles cases where the image or `src` attribute is missing.
3. - [ ] The placeholder `extract_data` methods in scraper implementations are updated to call the `extract_image_url` function using an example image selector.
4. - [ ] The data structure returned by `extract_data` includes an `image_url` field.
5. - [ ] The `CSVWriter` setup in `main.py` includes `image_url` in the header row definition.
6. - [ ] The output CSV file correctly includes the extracted image URL (or an empty string/None if not found) in the appropriate column.
7. - [ ] No actual image downloading occurs in this story[cite: 48].

## Subtasks

1. - [ ] Update `src/parser/html_parser.py`:
   1. - [ ] Add `extract_image_url(element)` or similar function that takes a BeautifulSoup/lxml element (or selector + soup) and returns the `src` attribute value.
   2. - [ ] Ensure it handles missing elements or `src` attributes gracefully.
2. - [ ] Update placeholder `extract_data` in `StaticScraper` and `DynamicScraper`:
   1. - [ ] Add a step to find the image element using a placeholder selector.
   2. - [ ] Call `extract_image_url`.
   3. - [ ] Add the result to the returned data dictionary under the key `image_url`.
3. - [ ] Update `src/main.py`:
   1. - [ ] Modify the `CSVWriter` header definition to include `image_url`.
4. - [ ] Update relevant unit tests for `html_parser` to cover image URL extraction.
5. - [ ] Update relevant unit tests for scraper `extract_data` methods.
6. - [ ] Update unit tests for `CSVWriter` interaction in `main.py` to verify the `image_url` column is handled.

## Testing Requirements:

* Reiterate the required code coverage percentage (>= 85%).
* Unit tests for the image URL extraction logic in `html_parser`.
* Unit tests confirming the `image_url` field is correctly populated by scrapers and written to the CSV.

## Story Wrap Up (To be filled in AFTER agent execution):

* **Agent Model Used:** `<Agent Model Name/Version>`
* **Agent Credit or Cost:** `<Cost/Credits Consumed>`
* **Date/Time Completed:** `<Timestamp>`
* **Commit Hash:** `<Git Commit Hash of resulting code>`
* **Change Log**
* change X
* change Y
...