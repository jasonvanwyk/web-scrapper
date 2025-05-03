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

## Error Handling and Resilience

1. **Robust Error Handling**: Implement comprehensive error handling from the beginning to make debugging easier and improve application resilience.

2. **Retry Logic**: Use appropriate retry mechanisms for operations that might fail transiently, especially network requests.

3. **Graceful Degradation**: Design components to handle failures gracefully, providing meaningful error messages and fallback behavior when possible.

## Configuration and Validation

1. **Configuration Management**: Using Pydantic for configuration validation provides strong type checking and validation, but requires understanding its validation mechanisms.

2. **Library Version Awareness**: Stay aware of major version changes in dependencies (like Pydantic v1 to v2) and plan for migration to avoid deprecated features.

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
