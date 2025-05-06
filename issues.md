# Project Issues and Resolutions Index

This document serves as an index to the reorganized issue documentation for the Automated Product Data Scraper project.

## Issue Documentation Structure

- [Story 1: Project Setup & Core Structure](docs/issues/story1_issues.md)
- [Story 2: Abstract Base Scraper & Factory](docs/issues/story2_issues.md)
- [Story 3: Static HTTP Scraper Implementation](docs/issues/story3_issues.md)
- [Story 4: Dynamic Browser Scraper Implementation](docs/issues/story4_issues.md)
- [Story 5: HTML Parsing & Data Transformation Module](docs/issues/story5_issues.md)
- [Story 6: CSV Output Storage Module](docs/issues/story6_issues.md)
- [Story 7: Basic Image Handling (URL Extraction)](docs/issues/story7_issues.md)
- [Story 8: Data Parser Module](docs/issues/story8_issues.md)
- [Story 9: Data Sanitizer & Validator Module](docs/issues/story9_issues.md)
- [Story 10: CSV Writer Module](docs/issues/story10_issues.md)
- [Story 12: Implement BaseScraper Abstract Class](docs/issues/story12_issues.md)
- [Story 13: Implement StaticScraper Concrete Class](docs/issues/story13_issues.md)
- [Story 14: Implement DynamicScraper Concrete Class](docs/issues/story14_issues.md)
- [Story 15: Implement RequestHandler Module](docs/issues/story15_issues.md)
- [Story 16: Implement BrowserHandler Module](docs/issues/story16_issues.md)
- [Story 17: Implement Parser & Transformer Module](docs/issues/story17_issues.md)
- [Story 20: Implement Basic Logging Module Configuration](docs/issues/story20_issues.md)
- [Story 21: Implement Secure Configuration Loading](docs/issues/story21_issues.md)
- [Story 22: HTML/Data Parser Module](docs/issues/story22_issues.md)
- [General Learnings](docs/issues/general_learnings.md)

## Quick Reference

### Common Issues by Category

#### Import and Path Resolution
- [Story 1: Import Path Resolution](docs/issues/story1_issues.md#issue-2-import-path-resolution)
- [Story 1: Path Resolution for Output Directory](docs/issues/story1_issues.md#issue-1-path-resolution-for-output-directory)
- [Story 2: Import Path Resolution in Factory](docs/issues/story2_issues.md#issue-3-import-path-resolution-in-factory)
- [Story 2: Circular Import in Tests](docs/issues/story2_issues.md#issue-4-circular-import-in-tests)
- [Story 6: Path Resolution for Output Directory](docs/issues/story6_issues.md#issue-2-path-resolution-for-output-directory)
- [Story 10: Output Directory Creation](docs/issues/story10_issues.md#issue-1-output-directory-creation)
- [Story 17: Import Path Resolution in Tests](docs/issues/story17_issues.md#issue-2-import-path-resolution-in-tests)

#### Testing Challenges
- [Story 1: Testing Module Execution](docs/issues/story1_issues.md#issue-4-testing-module-execution)
- [Story 2: Testing Abstract Base Classes](docs/issues/story2_issues.md#issue-1-testing-abstract-base-classes)
- [Story 2: Mocking Challenges in Factory Tests](docs/issues/story2_issues.md#issue-2-mocking-challenges-in-factory-tests)
- [Story 3: Testing Context Managers with Session Objects](docs/issues/story3_issues.md#issue-2-testing-context-managers-with-session-objects)
- [Story 3: Test Assertion Order Dependency](docs/issues/story3_issues.md#issue-4-test-assertion-order-dependency)
- [Story 3: Test Flexibility for Parameter Order](docs/issues/story3_issues.md#issue-5-test-flexibility-for-parameter-order)
- [Story 4: Testing Browser Automation Code](docs/issues/story4_issues.md#issue-4-testing-browser-automation-code)
- [Story 14: Testing Browser Automation Code](docs/issues/story14_issues.md#issue-4-testing-browser-automation-code)
- [Story 15: Test Assertion Mismatch with Retry Logic](docs/issues/story15_issues.md#issue-1-test-assertion-mismatch-with-retry-logic)
- [Story 5: Test Design for Floating-Point Comparisons](docs/issues/story5_issues.md#issue-4-test-design-for-floating-point-comparisons)
- [Story 6: Directory Cleanup in Tests](docs/issues/story6_issues.md#issue-1-directory-cleanup-in-tests)
- [Story 8: Testing Edge Cases and Error Conditions](docs/issues/story8_issues.md#issue-2-error-information-preservation)
- [Story 16: Testing Browser Automation Code](docs/issues/story16_issues.md#issue-4-testing-browser-automation-code)
- [Story 17: Mocking Challenges with Nested Imports](docs/issues/story17_issues.md#issue-3-mocking-challenges-with-nested-imports)

#### Library-Specific Issues
- [Story 1: Pydantic Validation in Tests](docs/issues/story1_issues.md#issue-3-pydantic-validation-in-tests)
- [Story 1: Pydantic Deprecated Validators](docs/issues/story1_issues.md#issue-5-pydantic-deprecated-validators)
- [Story 3: Tenacity Retry Decorator with Lambda Functions](docs/issues/story3_issues.md#issue-1-tenacity-retry-decorator-with-lambda-functions)
- [Story 3: URL Query Parameter Handling in Pagination](docs/issues/story3_issues.md#issue-3-url-query-parameter-handling-in-pagination)
- [Story 4: Playwright API Stability](docs/issues/story4_issues.md#issue-6-playwright-api-stability)
- [Story 5: Number Format Handling in Transformer Module](docs/issues/story5_issues.md#issue-1-number-format-handling-in-transformer-module)
- [Story 8: XPath Selector Support](docs/issues/story8_issues.md#issue-1-xpath-selector-support)
- [Story 15: Pydantic Deprecation Warnings](docs/issues/story15_issues.md#issue-3-pydantic-deprecation-warnings)

#### Browser Automation Issues
- [Story 4: Browser Lifecycle Management](docs/issues/story4_issues.md#issue-1-browser-lifecycle-management)
- [Story 4: Stealth Mode Implementation](docs/issues/story4_issues.md#issue-2-stealth-mode-implementation)
- [Story 4: Error Handling in Browser Automation](docs/issues/story4_issues.md#issue-3-error-handling-in-browser-automation)
- [Story 4: Configuration Management](docs/issues/story4_issues.md#issue-5-configuration-management)
- [Story 4: Integration Testing with Real Browsers](docs/issues/story4_issues.md#issue-7-integration-testing-with-real-browsers)
- [Story 4: System Dependencies for Playwright](docs/issues/story4_issues.md#issue-8-system-dependencies-for-playwright)
- [Story 14: Resource Management with Context Managers](docs/issues/story14_issues.md#issue-2-resource-management-with-context-managers)
- [Story 16: Resource Management with Context Managers](docs/issues/story16_issues.md#issue-1-resource-management-with-context-managers)
- [Story 16: Stealth Mode Implementation](docs/issues/story16_issues.md#issue-2-stealth-mode-implementation)
- [Story 16: Error Handling in Browser Automation](docs/issues/story16_issues.md#issue-3-error-handling-in-browser-automation)
- [Story 16: CAPTCHA Handling Integration](docs/issues/story16_issues.md#issue-5-captcha-handling-integration)

#### Data Handling Issues
- [Story 5: Error Handling in HTML Parser](docs/issues/story5_issues.md#issue-2-error-handling-in-html-parser)
- [Story 5: Integration with Existing Scrapers](docs/issues/story5_issues.md#issue-3-integration-with-existing-scrapers)
- [Story 6: UTF-8 Encoding for International Characters](docs/issues/story6_issues.md#issue-3-utf-8-encoding-for-international-characters)
- [Story 7: Relative vs. Absolute Image URLs](docs/issues/story7_issues.md#issue-1-relative-vs-absolute-image-urls)
- [Story 7: Consistent URL Handling Across Scraper Types](docs/issues/story7_issues.md#issue-2-consistent-url-handling-across-scraper-types)
- [Story 8: HTML Content Processing](docs/issues/story8_issues.md#issue-3-html-content-processing)
- [Story 8: URL Handling for Image URLs](docs/issues/story8_issues.md#issue-5-url-handling-for-image-urls)
- [Story 9: Currency Code Handling in Price Normalization](docs/issues/story9_issues.md#issue-1-currency-code-handling-in-price-normalization)
- [Story 9: URL Validation Regex Pattern](docs/issues/story9_issues.md#issue-2-url-validation-regex-pattern)
- [Story 10: UTF-8 Encoding for International Characters](docs/issues/story10_issues.md#issue-3-utf-8-encoding-for-international-characters)
- [Story 14: Data Processing in extract_data Method](docs/issues/story14_issues.md#issue-3-data-processing-in-extract_data-method)
- [Story 22: Handling Different HTML Content Types](docs/issues/story22_issues.md#issue-1-handling-different-html-content-types)
- [Story 22: Relative URL Resolution](docs/issues/story22_issues.md#issue-3-relative-url-resolution)
- [Story 22: International Number Format Handling](docs/issues/story22_issues.md#issue-5-international-number-format-handling)

#### Integration and Reuse
- [Story 8: Integration with Existing Modules](docs/issues/story8_issues.md#issue-4-integration-with-existing-modules)
- [Story 9: Error Preservation in Validation Pipeline](docs/issues/story9_issues.md#issue-4-error-preservation-in-validation-pipeline)
- [Story 14: Missing Abstract Method Implementation](docs/issues/story14_issues.md#issue-1-missing-maps_to_products-method)
- [Story 17: Integration vs. Duplication](docs/issues/story17_issues.md#issue-1-integration-vs-duplication)
- [Story 17: Maintaining Compatibility with Existing Code](docs/issues/story17_issues.md#issue-4-maintaining-compatibility-with-existing-code)
- [Story 22: Integrating XPath and CSS Selector Support](docs/issues/story22_issues.md#issue-2-integrating-xpath-and-css-selector-support)
- [Story 22: Error Handling and Information Preservation](docs/issues/story22_issues.md#issue-4-error-handling-and-information-preservation)

#### Resource Management
- [Story 6: Context Manager Implementation](docs/issues/story6_issues.md#issue-4-context-manager-implementation)
- [Story 10: Resource Management with Context Managers](docs/issues/story10_issues.md#issue-2-resource-management-with-context-managers)
- [Story 14: Resource Management with Context Managers](docs/issues/story14_issues.md#issue-2-resource-management-with-context-managers)
- [Story 16: Resource Management with Context Managers](docs/issues/story16_issues.md#issue-1-resource-management-with-context-managers)
- [Story 20: Resource Management for File Handlers](docs/issues/story20_issues.md#issue-1-resource-management-for-file-handlers)

#### Validation and Type Handling
- [Story 9: Type Handling in Pydantic Model](docs/issues/story9_issues.md#issue-3-type-handling-in-pydantic-model)
- [Story 9: None Value Handling in Validation Functions](docs/issues/story9_issues.md#issue-5-none-value-handling-in-validation-functions)

#### Configuration and Environment Variables
- [Story 20: Environment Variable Handling in Tests](docs/issues/story20_issues.md#issue-2-environment-variable-handling-in-tests)
- [Story 21: Environment Variable Prioritization](docs/issues/story21_issues.md#issue-3-environment-variable-prioritization)
- [Story 21: Secure Credential Management](docs/issues/story21_issues.md#issue-1-balancing-security-and-usability)
- [Story 21: Cloud Secrets Management Integration](docs/issues/story21_issues.md#issue-5-extensibility-for-cloud-secrets-management)

## Summary of Key Learnings

1. **Project Structure**: A well-defined project structure from the beginning makes development and testing much easier.

2. **Path Handling**: Always be explicit about path resolution, especially when dealing with file operations.

3. **Import Strategies**: Consider how your application will be imported and executed from different contexts.

4. **Testing Approach**: Write tests that directly test behavior rather than implementation details when possible.

5. **Error Handling**: Implement robust error handling from the beginning to make debugging easier.

6. **Library Version Awareness**: Stay aware of major version changes in dependencies and plan for migration.

7. **Pragmatic Mocking**: Use real implementations rather than excessive mocking when testing complex behaviors.

8. **Data Validation**: Validate data as close to the extraction point as possible to ensure data quality.

9. **Internationalization**: Consider different regional formats when handling numeric and date data.

10. **Resource Management**: Use context managers for proper resource cleanup, especially for file operations.

11. **Specialized Libraries**: Use specialized libraries for specific tasks rather than relying on general-purpose libraries with limited support.

12. **Error Information Preservation**: Ensure error information is preserved throughout the processing pipeline for better debugging.

13. **Integration over Duplication**: When adding new functionality to a modular system, consider how to integrate with existing components before creating new ones.

For more detailed learnings, see the [General Learnings](docs/issues/general_learnings.md) document.
