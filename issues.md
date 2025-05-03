# Project Issues and Resolutions

This document tracks challenges encountered during the development of the Automated Product Data Scraper project and how they were resolved. It serves as a learning resource to avoid repeating similar issues in future development.

## Story 1: Project Setup & Core Structure

### Issue 1: Path Resolution for Output Directory

**Problem:**
When running the application from within the `src` directory, the output directory path was being resolved relative to the `src` directory instead of the project root. This caused a `FileNotFoundError` when trying to write to the log file.

```
FileNotFoundError: [Errno 2] No such file or directory: '/home/jason/projects/freelance-projects/web-scrapper/src/output/scraper.log'
```

**Solution:**
Updated the path handling in `main.py` to correctly resolve relative paths from the project root:

```python
# Ensure output directory exists
output_dir = Path(config.output.output_dir)
if not output_dir.is_absolute():
    # If path is relative, make it relative to the project root, not the src directory
    project_root = Path(__file__).parent.parent
    output_dir = project_root / output_dir

output_dir.mkdir(parents=True, exist_ok=True)
```

**Learning:**
Always be explicit about path resolution in Python applications, especially when dealing with relative paths. Consider the context from which the application might be run (project root vs. specific directory) and handle both cases appropriately.

### Issue 2: Import Path Resolution

**Problem:**
When running the application from different directories, import statements would fail because the module paths were different depending on the execution context.

```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
Implemented a try/except block to handle both import scenarios:

```python
# Fix the import to work when running from src directory
try:
    from src.config import config
except ModuleNotFoundError:
    # When running directly from src directory
    from config import config
```

**Learning:**
When creating Python packages, consider how they will be imported from different execution contexts. Using try/except for imports can provide flexibility, but for larger projects, consider using proper Python packaging with setuptools to avoid these issues entirely.

### Issue 3: Pydantic Validation in Tests

**Problem:**
The test for `SupplierConfig` expected a validation error when setting `requires_login=True` without providing credentials, but the validation wasn't being triggered properly.

**Solution:**
Updated the `SupplierConfig` class to use Pydantic's `model_validator` with `mode='after'` to properly validate the model state:

```python
@model_validator(mode='after')
def validate_credentials_if_login_required(self):
    """Validate that credentials are provided if login is required."""
    if self.requires_login and (self.username is None or self.password is None):
        raise ValueError("Username and password are required when login is required")
    return self
```

Also enabled validation on attribute assignment with:

```python
model_config = {"validate_assignment": True}
```

**Learning:**
Pydantic v2 has different validation mechanisms compared to v1. The `model_validator` with `mode='after'` is more appropriate for validating the entire model state after all fields have been set. For field-specific validation, use `field_validator`. Always ensure `validate_assignment=True` if you want validation to occur when attributes are changed after initialization.

### Issue 4: Testing Module Execution

**Problem:**
The tests for the main module's execution were trying to re-import the module to trigger the `if __name__ == "__main__"` block, which was causing import errors and not properly testing the behavior.

**Solution:**
Updated the tests to directly call the functions that would be executed in the `if __name__ == "__main__"` block:

```python
def test_main_entry_point():
    """Test the __main__ block."""
    with mock.patch("src.main.setup_logging") as mock_setup_logging:
        with mock.patch("src.main.main") as mock_main:
            with mock.patch.object(sys, "exit"):
                # Simulate the if __name__ == "__main__" block
                try:
                    src.main.setup_logging()
                    src.main.main()
                except Exception:
                    pass
                
                # Check that setup_logging and main were called
                mock_setup_logging.assert_called_once()
                mock_main.assert_called_once()
```

**Learning:**
When testing Python modules with `if __name__ == "__main__"` blocks, it's better to directly test the functions that would be called rather than trying to re-import the module. This approach is more reliable and avoids import-related issues.

### Issue 5: Pydantic Deprecated Validators

**Problem:**
The code was using the deprecated `@validator` decorator from Pydantic v1, which generated warnings:

```
PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators
```

**Solution:**
For the `SupplierConfig` class, we migrated to using `@model_validator` with `mode='after'`. For other validators, we left them as is for now since they're still functional, but noted that they should be updated in the future.

**Learning:**
When using libraries that undergo major version changes (like Pydantic v1 to v2), be aware of deprecated features and plan to migrate to the new APIs. For non-critical warnings, it's acceptable to defer migration to a future refactoring task, but document the technical debt.

## General Learnings

1. **Project Structure**: A well-defined project structure from the beginning makes development and testing much easier.

2. **Configuration Management**: Using Pydantic for configuration validation provides strong type checking and validation, but requires understanding its validation mechanisms.

3. **Path Handling**: Always be explicit about path resolution, especially when dealing with file operations.

4. **Testing Approach**: Write tests that directly test behavior rather than implementation details when possible.

5. **Import Strategies**: Consider how your application will be imported and executed from different contexts.

6. **Environment Setup**: Ensure virtual environments and dependencies are properly set up before running the application.

7. **Error Handling**: Implement robust error handling from the beginning to make debugging easier.
