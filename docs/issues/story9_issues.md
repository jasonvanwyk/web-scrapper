# Story 9: Data Sanitizer & Validator Module Issues and Resolutions

This document captures the challenges encountered during the implementation of Story 9: Data Sanitizer & Validator Module, and the solutions applied to resolve them.

## Issue 1: Currency Code Handling in Price Normalization

### Problem
The `normalize_currency` function was correctly identifying currency codes (USD, EUR, etc.) in price strings, but was not removing them before attempting to convert the string to a float. This caused the conversion to fail and return the default value (0.0) instead of the actual price.

### Solution
1. Modified the `normalize_currency` function to remove the identified currency code from the price text before passing it to the `to_float` function
2. Added a specific step in the currency code detection loop to replace the code with an empty string when found
3. Ensured the modified string is passed to the conversion function

### Lessons Learned
- When extracting metadata (like currency symbols or codes) from values, ensure the extraction process doesn't interfere with subsequent processing
- Test with a variety of real-world input formats to catch edge cases
- Consider the full processing pipeline when implementing individual components

## Issue 2: URL Validation Regex Pattern

### Problem
The initial implementation of the `validate_url` function used a regex pattern that didn't properly account for query parameters in URLs. This caused validation to fail for valid URLs containing query strings (e.g., "https://example.com/search?q=test").

### Solution
1. Updated the regex pattern to include the question mark character ('?') in the allowed characters for the path portion of the URL
2. Ensured the pattern correctly handles common URL components (protocol, domain, path, query string)
3. Added comprehensive tests for various URL formats including those with query parameters

### Lessons Learned
- When implementing regex patterns for validation, test with a comprehensive set of valid and invalid examples
- URL validation is complex and requires careful consideration of all possible components
- Consider using specialized libraries for complex validation tasks in production environments

## Issue 3: Type Handling in Pydantic Model

### Problem
When directly passing raw product data (with string representations of prices and costs) to the Pydantic model, validation errors occurred because Pydantic expected numeric types for these fields. This caused the example script to fail when demonstrating direct use of the model.

### Solution
1. Added pre-processing of the raw data before passing it to the Pydantic model in the example script
2. Used the appropriate transformer functions (`to_float`, `normalize_text`, etc.) to convert the data to the expected types
3. Ensured the processed data matches the expected schema of the Pydantic model

### Lessons Learned
- Pydantic models validate types strictly by default, unlike our custom validation functions that handle type conversion
- When using validation libraries, understand their type handling behavior and prepare data accordingly
- Consider implementing helper functions to bridge between raw data and validation models

## Issue 4: Error Preservation in Validation Pipeline

### Problem
The initial implementation of the `clean_and_validate_product_data` function was overwriting error information from the parser when cleaning and validating the data. This caused loss of important context about why parsing might have failed.

### Solution
1. Modified the function to check for an "error" field in the input data
2. Added a bypass path that preserves the error information while still providing default values for all expected fields
3. Ensured the error field is included in the returned data structure

### Lessons Learned
- Error information should be preserved throughout the processing pipeline
- Design validation functions to handle and pass through error context
- Consider the full data flow when implementing validation logic

## Issue 5: None Value Handling in Validation Functions

### Problem
Some validation functions, particularly `validate_url`, didn't properly handle None values, which could lead to unexpected errors when processing data with missing fields.

### Solution
1. Updated the `validate_url` function to explicitly check for None values and raise an appropriate TypeError
2. Added explicit tests for None value handling in all validation functions
3. Ensured consistent behavior across all functions when handling None or empty values

### Lessons Learned
- Always consider None values as possible inputs to functions
- Be explicit about how None values should be handled (convert to default, raise error, etc.)
- Test edge cases including None and empty values for all functions
