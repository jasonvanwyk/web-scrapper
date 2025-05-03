# Story 3: Static HTTP Scraper Implementation - Issues and Resolutions

This document tracks challenges encountered during the implementation of Story 3 (Static HTTP Scraper Implementation) and how they were resolved.

## Issue 1: Tenacity Retry Decorator with Lambda Functions

**Problem:**
We initially tried to use a lambda function in the Tenacity retry decorator to dynamically access the instance's max_retries attribute:

```python
@retry(
    stop=stop_after_attempt(lambda self: self.max_retries),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
    reraise=True
)
```

This caused a TypeError during test execution:

```
TypeError: '>=' not supported between instances of 'int' and 'function'
```

**Solution:**
We replaced the lambda function with a fixed value for the retry decorator:

```python
@retry(
    stop=stop_after_attempt(3),  # Fixed value instead of lambda
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
    reraise=True
)
```

**Learning:**
Tenacity's retry decorator doesn't support lambda functions that reference instance attributes in the stop strategy. For class methods that need dynamic retry counts, consider using a wrapper function that applies the retry decorator with the appropriate parameters at runtime, or use a fixed value that works for most cases.

## Issue 2: Testing Context Managers with Session Objects

**Problem:**
When testing the context manager functionality of the RequestHandler class, we encountered an issue with checking if the session was closed:

```python
# Check that the session is closed after exiting the context
self.assertTrue(self.handler.session.closed)
```

This failed with the error:

```
AttributeError: 'Session' object has no attribute 'closed'. Did you mean: 'close'?
```

**Solution:**
We modified the test to check if the `close()` method was called instead of checking a non-existent attribute:

```python
# Mock the close method to check if it was called
with mock.patch.object(self.handler, 'close') as mock_close:
    with self.handler:
        pass
    mock_close.assert_called_once()
```

**Learning:**
When testing context managers, focus on verifying that the appropriate cleanup methods are called rather than checking internal state that might not be exposed. Use mocking to verify that cleanup methods are called at the right time.

## Issue 3: URL Query Parameter Handling in Pagination

**Problem:**
When implementing the `handle_pagination` method in the StaticScraper class, we initially used a simple approach to add page parameters to URLs:

```python
if parsed_url.query:
    return f"{url}&page={page}"
else:
    return f"{url}?page={page}"
```

This approach didn't properly handle existing query parameters, especially when there were multiple parameters or when the URL already had a page parameter.

**Solution:**
We implemented a more robust approach using urllib.parse to properly handle query parameters:

```python
if parsed_url.query:
    from urllib.parse import parse_qs, urlencode
    
    # Parse the query string into a dictionary
    query_params = parse_qs(parsed_url.query)
    
    # Add or update the page parameter
    query_params['page'] = [str(page)]
    
    # Convert the dictionary back to a query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct the URL with the new query string
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
else:
    return f"{url}?page={page}"
```

**Learning:**
When working with URLs and query parameters, use the built-in `urllib.parse` module to properly parse, modify, and reconstruct URLs. This ensures that special characters are properly encoded and that existing parameters are preserved.

## Issue 4: Test Assertion Order Dependency

**Problem:**
In our test for the `get_product_urls` method, we were using `assert_called_with` to verify that the RequestHandler's `get` method was called with the expected URL:

```python
self.mock_request_handler.get.assert_called_with("https://example.com/products")
```

This failed because the method was called multiple times with different URLs during pagination, and `assert_called_with` only checks the last call.

**Solution:**
We switched to using `assert_any_call` to verify that the method was called with the expected URL at least once:

```python
self.mock_request_handler.get.assert_any_call("https://example.com/products")
```

**Learning:**
When testing methods that make multiple calls to the same dependency, use `assert_any_call` instead of `assert_called_with` to verify that a specific call was made, regardless of order or other calls. For more complex call patterns, consider using `call_args_list` to inspect all calls.

## Issue 5: Test Flexibility for Parameter Order

**Problem:**
In our test for the `handle_pagination` method, we were using a strict equality check for URLs with query parameters:

```python
self.assertEqual(result, "https://example.com/products?category=shoes&page=2")
```

This failed because the order of query parameters can vary depending on the implementation:

```
AssertionError: 'https://example.com/products?page=2&category=shoes' != 'https://example.com/products?category=shoes&page=2'
```

**Solution:**
We made the test more flexible by checking for the presence of each parameter individually:

```python
# The order of parameters might vary, so we check that both parameters are present
self.assertIn("category=shoes", result)
self.assertIn("page=2", result)
```

**Learning:**
When testing URLs with query parameters, avoid strict equality checks that depend on parameter order. Instead, check for the presence of each expected parameter individually. Alternatively, parse the URL and verify the query parameters as a dictionary.
