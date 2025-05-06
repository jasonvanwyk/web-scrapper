# Story 22: HTML/Data Parser Module Issues and Resolutions

This document captures the challenges encountered during the implementation of Story 22: HTML/Data Parser Module, and the solutions applied to resolve them.

## Issue 1: Handling Different HTML Content Types

### Problem
The existing parser functions were designed to handle either string or BeautifulSoup objects, but not Tag objects directly. This limitation made it difficult to parse individual product containers when extracting data from multiple products on a page.

### Solution
1. Enhanced all parser functions to accept and properly handle three types of inputs:
   - HTML content as a string
   - BeautifulSoup objects
   - Tag objects (for individual elements within a page)
2. Implemented consistent type checking using `isinstance()` to apply the appropriate parsing logic based on the input type
3. Added explicit error handling for unsupported input types

### Lessons Learned
- Design parsing functions to handle different input types explicitly from the beginning
- Use consistent type checking patterns across all related functions
- Document the expected input types clearly in function docstrings

## Issue 2: Integrating XPath and CSS Selector Support

### Problem
The existing implementation had partial support for XPath expressions, but it was implemented inconsistently across different extraction methods. This made it difficult to use XPath selectors reliably, especially for complex extraction scenarios.

### Solution
1. Added dedicated functions for XPath extraction (`extract_with_xpath` and `extract_structured_data_with_xpath`)
2. Standardized the approach for trying CSS selectors first, then falling back to XPath if needed
3. Improved error handling for both selector types to ensure consistent behavior
4. Added support for mixed selector configurations (some fields using CSS, others using XPath)

### Lessons Learned
- When supporting multiple selector types, implement dedicated functions for each type rather than mixing logic
- Establish a clear precedence order when multiple selector types are available
- Test both selector types thoroughly with various HTML structures

## Issue 3: Relative URL Resolution

### Problem
The parser was not consistently converting relative URLs (like image paths) to absolute URLs, which could lead to broken links when the data is used outside the context of the original website.

### Solution
1. Enhanced the `extract_image_url` function to accept a `base_url` parameter
2. Implemented automatic URL resolution using `urljoin` from the `urllib.parse` module
3. Applied this URL resolution consistently across both CSS and XPath extraction methods

### Lessons Learned
- Always convert relative URLs to absolute URLs when they will be used outside the context of the original website
- Use standard library functions like `urljoin` rather than implementing custom URL joining logic
- Apply URL handling consistently across all extraction methods

## Issue 4: Error Handling and Information Preservation

### Problem
Error information was not consistently preserved throughout the parsing process, making it difficult to diagnose issues when extraction failed.

### Solution
1. Implemented comprehensive error handling at multiple levels:
   - Individual extraction functions
   - Field-specific extraction methods
   - Overall parsing process
2. Ensured error information is included in the returned data structure
3. Added detailed logging with context information to aid debugging

### Lessons Learned
- Implement robust error handling from the beginning
- Preserve error context throughout the processing pipeline
- Use consistent error handling patterns across all components

## Issue 5: International Number Format Handling

### Problem
The parser needed to handle different number formats (like European format with comma as decimal separator) correctly when extracting price and cost information.

### Solution
1. Enhanced the `to_float` function to handle various number formats:
   - US/UK format (1,234.56)
   - European format (1.234,56)
   - Simple comma decimal format (123,45)
2. Added support for different currency symbols (€, £, $, ¥)
3. Implemented comprehensive testing with international formats

### Lessons Learned
- Consider international formats when handling numeric data
- Test with various regional formats to ensure correct parsing
- Implement robust conversion functions that handle different formats gracefully
