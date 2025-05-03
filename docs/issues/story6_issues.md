# Story 6: CSV Output Storage Module - Issues and Resolutions

This document captures the challenges encountered during the implementation of Story 6 (CSV Output Storage Module) and the solutions applied to resolve them.

## Issue 1: Directory Cleanup in Tests

### Problem

When implementing the unit tests for the CSVWriter class, we encountered an issue with the test cleanup process. Specifically, in the `test_open_creates_directory` test, we created a subdirectory within our temporary test directory. During the tearDown method, we attempted to remove all files in the temporary directory and then remove the directory itself, but this approach failed because we were trying to remove a subdirectory as if it were a file.

The error was:
```
IsADirectoryError: [Errno 21] Is a directory: '/tmp/tmpwou2m61n/new_dir'
```

### Solution

We improved the test cleanup by using `shutil.rmtree()` with the `ignore_errors=True` parameter instead of manually iterating through files. This approach is more robust as it:

1. Recursively removes directories and their contents
2. Handles both files and subdirectories appropriately
3. Continues even if some files cannot be removed (due to permissions or other issues)

```python
def tearDown(self):
    """Tear down test fixtures."""
    # Clean up temporary directory using shutil.rmtree to handle subdirectories
    shutil.rmtree(self.temp_dir, ignore_errors=True)
```

### Lessons Learned

1. When cleaning up test resources, use specialized tools like `shutil.rmtree()` for directory removal
2. Consider the full hierarchy of resources that might be created during tests
3. Use `ignore_errors=True` for cleanup operations to ensure tests don't fail during teardown

## Issue 2: Path Resolution for Output Directory

### Problem

When implementing the CSVWriter, we needed to ensure proper handling of both absolute and relative paths for the output directory. This was similar to an issue encountered in Story 1, where path resolution needed to be consistent regardless of the execution context.

### Solution

We addressed this by:

1. Using `os.path.abspath()` in the CSVWriter constructor to convert all paths to absolute paths
2. Creating a separate `resolve_path()` utility function in main.py to handle path resolution consistently
3. Using `os.makedirs(exist_ok=True)` to create output directories if they don't exist

```python
def resolve_path(path: Path) -> Path:
    """
    Resolve a path to be absolute, handling both absolute and relative paths.
    """
    if not path.is_absolute():
        # If path is relative, make it relative to the project root, not the src directory
        project_root = Path(__file__).parent.parent
        return project_root / path
    return path
```

### Lessons Learned

1. Always be explicit about path resolution, especially when dealing with file operations
2. Create utility functions for common operations like path resolution to ensure consistency
3. Consider the context from which the application might be run (project root vs. specific directory)

## Issue 3: UTF-8 Encoding for International Characters

### Problem

When implementing the CSV writer, we needed to ensure proper handling of international characters in the product data. Without explicit encoding settings, CSV files might use the system default encoding, which could lead to character corruption when handling non-ASCII characters.

### Solution

We addressed this by:

1. Adding explicit UTF-8 encoding in the CSVWriter class:
   ```python
   self.file = open(filepath, 'w', encoding=self.encoding, newline=self.newline)
   ```

2. Making the encoding configurable with a default of 'utf-8':
   ```python
   encoding: str = 'utf-8'
   ```

3. Adding a specific test case for UTF-8 encoding with international characters:
   ```python
   test_data = {
       "product_name": "Café Français",  # Contains non-ASCII characters
       "sku": "CF789",
       "price": "€29.99",  # Euro symbol
       "image_url": "http://example.com/café.jpg"
   }
   ```

4. Updating the configuration system to include a CSV encoding setting:
   ```python
   csv_encoding: str = Field(
       default_factory=lambda: os.getenv("CSV_ENCODING", "utf-8"),
       description="Encoding to use for CSV files"
   )
   ```

### Lessons Learned

1. Always specify encoding explicitly when dealing with text files, especially in international contexts
2. Make encoding configurable to handle different requirements
3. Include test cases with international characters to verify encoding works correctly
4. Document encoding requirements in configuration and code comments

## Issue 4: Context Manager Implementation

### Problem

When implementing the CSVWriter class as a context manager, we needed to ensure proper resource management, especially for file handles. Improper implementation could lead to resource leaks or files not being properly closed.

### Solution

We implemented the context manager protocol (`__enter__` and `__exit__` methods) to ensure proper file handling:

```python
def __enter__(self):
    """Context manager entry point - opens the file."""
    self.open()
    return self
    
def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit point - closes the file."""
    self.close()
```

This allows the CSVWriter to be used with a `with` statement, ensuring the file is properly closed even if an exception occurs:

```python
with csv_writer:
    csv_writer.write_header(csv_headers)
    csv_writer.write_row(data)
```

### Lessons Learned

1. Use context managers for resource management, especially for file operations
2. Ensure proper cleanup in both normal and exception cases
3. Test context manager behavior specifically to verify resource cleanup
4. Consider implementing context managers for any class that manages resources
