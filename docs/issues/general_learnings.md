# General Learnings

This document captures general learnings and best practices derived from challenges encountered across multiple stories in the Automated Product Data Scraper project.

## Project Structure and Organization

1. **Well-defined Project Structure**: A clear and consistent project structure from the beginning makes development and testing much easier. Follow established Python project conventions.

2. **Path Handling**: Always be explicit about path resolution, especially when dealing with file operations. Consider the context from which the application might be run (project root vs. specific directory) and handle both cases appropriately.

3. **Import Strategies**: Consider how your application will be imported and executed from different contexts. Use try/except blocks for imports when necessary, but consider proper Python packaging for larger projects.

## Testing Best Practices

1. **Test Behavior, Not Implementation**: Write tests that directly test behavior rather than implementation details when possible. This makes tests more resilient to refactoring.

2. **Pragmatic Mocking**: Use real implementations rather than excessive mocking when testing complex behaviors. Only mock the specific parts that need to be controlled (like external dependencies or error conditions).

3. **Avoid Brittle Assertions**: Make assertions flexible enough to handle variations that don't affect functionality (like query parameter order in URLs).

4. **Test Context Managers**: When testing context managers, focus on verifying that the appropriate cleanup methods are called rather than checking internal state.

5. **Test Multiple Calls**: Use `assert_any_call` instead of `assert_called_with` when testing methods that make multiple calls to the same dependency.

6. **Floating-Point Comparisons**: Never use exact equality for floating-point comparisons in tests. Use approximate equality checks with a small tolerance or specialized tools like `pytest.approx()`.

7. **Test Resource Cleanup**: Use specialized tools like `shutil.rmtree()` for cleaning up complex resources like directory trees in tests. Consider using `try/finally` or context managers to ensure cleanup happens even if tests fail.

## Error Handling and Resilience

1. **Robust Error Handling**: Implement comprehensive error handling from the beginning to make debugging easier and improve application resilience.

2. **Retry Logic**: Use appropriate retry mechanisms for operations that might fail transiently, especially network requests.

3. **Graceful Degradation**: Design components to handle failures gracefully, providing meaningful error messages and fallback behavior when possible.

4. **Default Values**: Always provide sensible default values for functions that might encounter errors or missing data.

5. **File Operation Safety**: Always check for file existence, handle permissions issues, and use proper error handling for all file operations. Consider using context managers to ensure resources are properly closed.

## Configuration and Validation

1. **Configuration Management**: Using Pydantic for configuration validation provides strong type checking and validation, but requires understanding its validation mechanisms.

2. **Library Version Awareness**: Stay aware of major version changes in dependencies (like Pydantic v1 to v2) and plan for migration to avoid deprecated features.

3. **Data Validation**: Validate data as close to the extraction point as possible to ensure data quality. Implement validation functions for common data types and formats.

4. **Configuration Flexibility**: Make configuration options flexible enough to handle different use cases, but with sensible defaults to simplify common scenarios.

## Data Processing and Transformation

1. **Internationalization**: Consider different regional formats when handling numeric and date data. Implement robust parsing for different number formats (e.g., US vs. European).

2. **Separation of Concerns**: Separate parsing logic from data transformation to improve maintainability and testability.

3. **Consistent Error Handling**: Use consistent error handling patterns across all data processing functions to ensure reliability.

4. **Logging Context**: Include sufficient context in log messages to make debugging easier, especially for data extraction and transformation errors.

5. **Character Encoding**: Always specify encoding explicitly (preferably UTF-8) when dealing with text files, especially for international data.

6. **URL Handling**: Always convert relative URLs to absolute URLs when they will be used outside the context of the original website. This makes the data directly usable without additional processing.

7. **Consistent Data Formats**: Ensure consistent data formats across different implementations of similar functionality to simplify downstream processing.

## Resource Management

1. **Context Managers**: Implement and use context managers (`__enter__` and `__exit__` methods) for classes that manage resources like file handles, network connections, or database sessions.

2. **Explicit Cleanup**: Provide explicit cleanup methods (like `close()`) in addition to context manager support to give users flexibility in resource management.

3. **Defensive Cleanup**: Implement cleanup operations defensively, checking if resources are still open before attempting to close them and handling exceptions during cleanup.

4. **Resource Lifecycle Logging**: Log resource lifecycle events (creation, opening, closing) at appropriate levels to aid debugging.

## System Dependencies and Integration

1. **Beyond Package Dependencies**: For complex tools like browser automation, be aware of system-level dependencies that may be required beyond Python packages.

2. **Dependency Installation Scripts**: Provide automation scripts for installing system dependencies to simplify setup across different environments.

3. **Containerization Consideration**: For projects with complex dependencies, consider containerization (Docker) to ensure consistent environments across development, testing, and production.

4. **Skippable Integration Tests**: Design integration tests to be skippable in environments where all dependencies cannot be installed, using environment variables to control test execution.

## Browser Automation Best Practices

1. **Resource Management**: Always ensure proper cleanup of browser resources, even in error scenarios, to prevent memory leaks and orphaned processes.

2. **Stealth Techniques**: When scraping websites that may employ anti-bot measures, implement stealth techniques to minimize detection risk.

3. **Configurable Timeouts and Delays**: Make timeouts and delays configurable to handle different network conditions and website response times.

4. **Error Recovery**: Implement robust error handling with appropriate recovery mechanisms for common browser automation failures.

## Development Environment

1. **Environment Setup**: Ensure virtual environments and dependencies are properly set up before running the application.

2. **Consistent Coding Style**: Follow a consistent coding style throughout the project to improve readability and maintainability.

3. **Documentation**: Document code, especially complex logic, to make it easier for other developers (and your future self) to understand.

## Refactoring and Code Evolution

1. **Interface Stability**: When refactoring, maintain the same interface to minimize disruption to existing code.

2. **Phased Approach**: Consider a phased approach to refactoring rather than changing everything at once.

3. **Backward Compatibility**: Keep backward compatibility in mind when improving existing components.

4. **Test Coverage**: Ensure comprehensive test coverage before and after refactoring to catch regressions.

## File Operations

1. **Path Abstraction**: Use `pathlib.Path` for modern, object-oriented path manipulation instead of string operations or `os.path` functions.

2. **Directory Creation**: Use `os.makedirs(exist_ok=True)` to create directories, which handles both creating parent directories and avoiding errors if the directory already exists.

3. **File Encoding**: Always specify encoding (typically UTF-8) when opening text files to ensure consistent behavior across different operating systems and locales.

4. **Streaming Writes**: For large datasets, use streaming writes (writing one row at a time) rather than building the entire dataset in memory before writing.

5. **Timestamped Filenames**: Consider using timestamps in filenames for output files to avoid overwriting previous results and provide an audit trail.
