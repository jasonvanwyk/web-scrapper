# Project Issues and Resolutions Index

This document serves as an index to the reorganized issue documentation for the Automated Product Data Scraper project.

## Issue Documentation Structure

- [Story 1: Project Setup & Core Structure](docs/issues/story1_issues.md)
- [Story 2: Abstract Base Scraper & Factory](docs/issues/story2_issues.md)
- [Story 3: Static HTTP Scraper Implementation](docs/issues/story3_issues.md)
- [General Learnings](docs/issues/general_learnings.md)

## Quick Reference

### Common Issues by Category

#### Import and Path Resolution
- [Story 1: Import Path Resolution](docs/issues/story1_issues.md#issue-2-import-path-resolution)
- [Story 1: Path Resolution for Output Directory](docs/issues/story1_issues.md#issue-1-path-resolution-for-output-directory)
- [Story 2: Import Path Resolution in Factory](docs/issues/story2_issues.md#issue-3-import-path-resolution-in-factory)
- [Story 2: Circular Import in Tests](docs/issues/story2_issues.md#issue-4-circular-import-in-tests)

#### Testing Challenges
- [Story 1: Testing Module Execution](docs/issues/story1_issues.md#issue-4-testing-module-execution)
- [Story 2: Testing Abstract Base Classes](docs/issues/story2_issues.md#issue-1-testing-abstract-base-classes)
- [Story 2: Mocking Challenges in Factory Tests](docs/issues/story2_issues.md#issue-2-mocking-challenges-in-factory-tests)
- [Story 3: Testing Context Managers with Session Objects](docs/issues/story3_issues.md#issue-2-testing-context-managers-with-session-objects)
- [Story 3: Test Assertion Order Dependency](docs/issues/story3_issues.md#issue-4-test-assertion-order-dependency)
- [Story 3: Test Flexibility for Parameter Order](docs/issues/story3_issues.md#issue-5-test-flexibility-for-parameter-order)

#### Library-Specific Issues
- [Story 1: Pydantic Validation in Tests](docs/issues/story1_issues.md#issue-3-pydantic-validation-in-tests)
- [Story 1: Pydantic Deprecated Validators](docs/issues/story1_issues.md#issue-5-pydantic-deprecated-validators)
- [Story 3: Tenacity Retry Decorator with Lambda Functions](docs/issues/story3_issues.md#issue-1-tenacity-retry-decorator-with-lambda-functions)
- [Story 3: URL Query Parameter Handling in Pagination](docs/issues/story3_issues.md#issue-3-url-query-parameter-handling-in-pagination)

## Summary of Key Learnings

1. **Project Structure**: A well-defined project structure from the beginning makes development and testing much easier.

2. **Path Handling**: Always be explicit about path resolution, especially when dealing with file operations.

3. **Import Strategies**: Consider how your application will be imported and executed from different contexts.

4. **Testing Approach**: Write tests that directly test behavior rather than implementation details when possible.

5. **Error Handling**: Implement robust error handling from the beginning to make debugging easier.

6. **Library Version Awareness**: Stay aware of major version changes in dependencies and plan for migration.

7. **Pragmatic Mocking**: Use real implementations rather than excessive mocking when testing complex behaviors.

For more detailed learnings, see the [General Learnings](docs/issues/general_learnings.md) document.
