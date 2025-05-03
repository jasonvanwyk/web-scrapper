# Story 2: Abstract Base Scraper & Factory - Issues and Resolutions

This document tracks challenges encountered during the implementation of Story 2 (Abstract Base Scraper & Factory) and how they were resolved.

## Issue 1: Testing Abstract Base Classes

**Problem:**
When testing the `BaseScraper` abstract base class, we initially tried to check for abstract methods using a method that accessed the `__isabstractmethod__` attribute of class methods. This approach failed with an error:

```
AttributeError: 'frozenset' object has no attribute '__isabstractmethod__'
```

**Solution:**
Updated the test to use the `__abstractmethods__` attribute of the class itself, which provides a frozenset of all abstract method names:

```python
def test_base_scraper_is_abstract(self):
    """Test that BaseScraper is an abstract base class."""
    assert issubclass(BaseScraper, ABC)
    
    # Verify that BaseScraper has abstract methods
    abstract_methods = BaseScraper.__abstractmethods__
    
    # Check that all required abstract methods are defined
    assert "login" in abstract_methods
    assert "get_product_urls" in abstract_methods
    assert "handle_pagination" in abstract_methods
    assert "extract_data" in abstract_methods
```

**Learning:**
When testing abstract base classes in Python, use the `__abstractmethods__` class attribute to get the set of abstract method names. This is more reliable than trying to inspect individual methods for the `__isabstractmethod__` attribute.

## Issue 2: Mocking Challenges in Factory Tests

**Problem:**
Our initial approach to testing the `ScraperFactory` used complex mocking with `MagicMock` and `patch` decorators. This led to several issues:

1. Mock objects didn't have the `__name__` attribute needed by the factory
2. The test was too focused on implementation details rather than behavior
3. Assertions were failing because the mock objects weren't behaving as expected

```
AttributeError: __name__
```

**Solution:**
We took a more pragmatic approach to testing the factory:

1. Created a real `StaticScraper` implementation as a placeholder for testing
2. Used this real implementation to test the factory's behavior
3. Limited mocking to only the parts that needed it (like import errors)

```python
def test_get_scraper_with_static_type(self):
    """Test getting a scraper with static scraper_type."""
    # This test uses the actual StaticScraper implementation
    factory = ScraperFactory()
    
    # Create a supplier config with static scraper_type
    supplier_config = SupplierConfig(
        name="Test Supplier",
        url="https://example.com",
        scraper_type="static"
    )
    
    # Get the scraper
    scraper = factory.get_scraper(supplier_config)
    
    # Verify that the correct scraper was returned
    assert isinstance(scraper, StaticScraper)
    assert scraper.name == "Test Supplier"
    assert scraper.base_url == "https://example.com"
```

**Learning:**
When testing complex behaviors like dynamic imports and class instantiation, it's often better to use real implementations rather than excessive mocking. This leads to more reliable tests that verify actual behavior rather than implementation details. Only mock the specific parts that need to be controlled (like external dependencies or error conditions).

## Issue 3: Import Path Resolution in Factory

**Problem:**
The factory needed to dynamically import scraper modules, but the import paths would be different depending on whether the code was run from the project root or from within the src directory.

**Solution:**
Implemented a try/except block in the factory to handle both import scenarios:

```python
# Try both import paths to handle different execution contexts
try:
    module = importlib.import_module(f"src.scrapers.{module_name}")
except ModuleNotFoundError:
    module = importlib.import_module(f"scrapers.{module_name}")
```

**Learning:**
When dynamically importing modules, consider the different execution contexts and handle them appropriately. This is especially important for factory patterns that rely on dynamic imports.

## Issue 4: Circular Import in Tests

**Problem:**
In our test for the `get_scraper` function, we ran into circular import issues because we were importing the function at the module level while also trying to patch it.

**Solution:**
Moved the import statement inside the test function and within the patch context:

```python
def test_get_scraper_function(self):
    """Test the get_scraper function."""
    # Import the function here to avoid circular imports in tests
    try:
        from src.scrapers.factory import get_scraper
    except ImportError:
        from scrapers.factory import get_scraper
        
    # Create a supplier config with static scraper_type
    supplier_config = SupplierConfig(
        name="Test Supplier",
        url="https://example.com",
        scraper_type="static"
    )
    
    # Call the function
    scraper = get_scraper(supplier_config)
    
    # Verify that the correct scraper was returned
    assert isinstance(scraper, StaticScraper)
    assert scraper.name == "Test Supplier"
    assert scraper.base_url == "https://example.com"
```

**Learning:**
When testing functions that might be involved in circular imports, import them inside the test function rather than at the module level. This is especially important when using patch decorators that affect the import system.
