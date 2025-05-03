# Story 12: Implement BaseScraper Abstract Class - Issues and Resolutions

This document tracks challenges encountered during the implementation of Story 12 (Implement BaseScraper Abstract Class) and how they were resolved.

## Issue 1: Existing Implementation with Missing Method

**Problem:**
When implementing Story 12, we discovered that the `BaseScraper` abstract class already existed with most of the required methods, but was missing the `Maps_to_products` abstract method specified in the acceptance criteria.

**Solution:**
We added the missing `Maps_to_products` abstract method to the existing implementation:

```python
@abc.abstractmethod
def Maps_to_products(self, category_map: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Map category identifiers to product URLs.
    
    Args:
        category_map: A dictionary mapping category names to category URLs or identifiers.
        
    Returns:
        Dict[str, List[str]]: A dictionary mapping category names to lists of product URLs.
    """
    pass
```

**Learning:**
When implementing a new feature or class, it's important to check if parts of it already exist in the codebase. In this case, we needed to carefully review the existing implementation and only add what was missing, rather than creating a completely new implementation that might conflict with existing code.

## Issue 2: Updating Tests for New Abstract Method

**Problem:**
After adding the new abstract method, we needed to update all the test cases that used concrete implementations of the `BaseScraper` class. This included updating the test that verifies the abstract methods as well as implementing the method in all test concrete classes.

**Solution:**
We updated the test_base_scraper.py file to:
1. Add an assertion to check for the new abstract method:
   ```python
   assert "Maps_to_products" in abstract_methods
   ```
2. Add implementations of the method to all concrete test classes:
   ```python
   def Maps_to_products(self, category_map):
       return {k: [] for k in category_map}
   ```

**Learning:**
When adding new abstract methods to an existing abstract base class, it's crucial to update all tests that use concrete implementations of that class. This ensures that the tests continue to pass and that all concrete implementations adhere to the updated interface.
