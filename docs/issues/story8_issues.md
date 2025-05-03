# Story 8: Data Parser Module Issues and Resolutions

This document captures the challenges encountered during the implementation of Story 8: Data Parser Module, and the solutions applied to resolve them.

## Issue 1: XPath Selector Support

### Problem
The initial implementation of the Parser class only supported CSS selectors using BeautifulSoup, but the requirements specified that both CSS selectors and XPath expressions should be supported. When attempting to use XPath selectors, the tests failed because BeautifulSoup's XPath support is limited.

### Solution
We integrated lxml.html for proper XPath support:

1. Added lxml.html as a dependency for XPath parsing
2. Implemented separate code paths for CSS selectors (using BeautifulSoup) and XPath expressions (using lxml.html)
3. Created consistent extraction methods that work with both selector types
4. Used the `text_content()` method from lxml.html elements to extract text content

### Lessons Learned
- BeautifulSoup's native XPath support is limited; use specialized libraries like lxml for robust XPath functionality
- When supporting multiple selector types, ensure consistent behavior and error handling across all types
- Test both selector types thoroughly with various HTML structures

## Issue 2: Error Information Preservation

### Problem
The Parser class was not including error information in the returned data when parsing failed. The `clean_and_validate_product_data` function from the transformer module was removing the error field from the result.

### Solution
1. Modified the error handling in the Parser class to bypass the `clean_and_validate_product_data` function when an error occurs
2. Created a consistent error response structure that includes both default values for all expected fields and an additional "error" field with the error message
3. Added specific handling for malformed HTML with unclosed tags to ensure error information is captured

### Lessons Learned
- When using validation functions, be aware of how they might modify or filter your data structure
- Error information should be preserved throughout the processing pipeline
- Include specific handling for common error cases (like malformed HTML)

## Issue 3: HTML Content Processing

### Problem
The Parser class needed to handle different types of HTML content inputs (strings, BeautifulSoup objects, and Tag objects) consistently. This created complexity in the extraction methods and made error handling more challenging.

### Solution
1. Implemented type checking using `isinstance()` to handle different input types appropriately
2. Created a consistent approach for processing each input type
3. Added robust error handling for each extraction method
4. Used the `create_soup` function from the html_parser module to ensure consistent HTML parsing

### Lessons Learned
- Design functions to handle different input types explicitly rather than relying on duck typing for critical parsing operations
- Document the expected input types clearly in function docstrings
- Implement consistent error handling for all input types

## Issue 4: Integration with Existing Modules

### Problem
The Parser class needed to leverage existing functionality from the html_parser and transformer modules while adding new capabilities. This required careful integration to avoid duplication and ensure consistent behavior.

### Solution
1. Imported and reused existing functions from html_parser and transformer modules
2. Extended functionality where needed while maintaining compatibility
3. Ensured consistent error handling between the Parser class and existing modules
4. Used the same data structure and field naming conventions for compatibility

### Lessons Learned
- When extending existing functionality, maintain consistency with established patterns
- Reuse existing functions rather than duplicating code
- Ensure error handling is consistent across all components

## Issue 5: URL Handling for Image URLs

### Problem
The Parser needed to convert relative image URLs to absolute URLs using the base URL of the supplier website. This required careful handling of different URL formats and edge cases.

### Solution
1. Used the `urljoin` function from the urllib.parse module to properly convert relative URLs to absolute URLs
2. Added specific handling for image URLs in the `_extract_image_url` method
3. Ensured the base URL is properly stored and used throughout the Parser class

### Lessons Learned
- Always convert relative URLs to absolute URLs when they will be used outside the context of the original website
- Use standard library functions like `urljoin` rather than implementing custom URL joining logic
- Test URL joining with various edge cases (relative paths, absolute paths, protocol-relative URLs, etc.)
