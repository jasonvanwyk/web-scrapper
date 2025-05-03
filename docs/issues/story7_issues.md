# Story 7: Basic Image Handling (URL Extraction) - Issues and Resolutions

This document outlines the challenges encountered during the implementation of Story 7 and the solutions applied to resolve them.

## Issue 1: Relative vs. Absolute Image URLs

### Problem

During testing, we discovered that the image URLs extracted from HTML were being stored as relative URLs (e.g., `/images/product.jpg`) rather than absolute URLs (e.g., `https://example.com/images/product.jpg`). This caused test failures because:

1. The test cases expected absolute URLs
2. Relative URLs would not be directly usable in external applications consuming the CSV data

### Solution

We modified the `extract_data` method in both the `StaticScraper` and `DynamicScraper` classes to convert relative image URLs to absolute URLs by wrapping the `extract_image_url` call with the `build_absolute_url` method:

```python
# Before
"image_url": extract_image_url(html_content, self.selectors.get('image_url', '')),

# After
"image_url": self.build_absolute_url(extract_image_url(html_content, self.selectors.get('image_url', ''))),
```

This ensures that all image URLs in the output CSV are absolute URLs that include the domain, making them directly usable without further processing.

### Lessons Learned

1. When extracting URLs from HTML, always consider whether they should be relative or absolute based on how they'll be used.
2. Leverage existing utility methods (like `build_absolute_url`) to maintain consistency across the codebase.
3. Test cases can help identify issues with URL formatting that might not be immediately apparent during development.

## Issue 2: Consistent URL Handling Across Scraper Types

### Problem

The issue with relative URLs was present in both scraper implementations (`StaticScraper` and `DynamicScraper`), highlighting the need for consistent URL handling across different scraper types.

### Solution

We applied the same fix to both scraper classes, ensuring consistent behavior regardless of which scraper type is used. This maintains the principle that the same data structure should be returned by all scraper implementations, making the downstream processing simpler.

### Lessons Learned

1. When implementing similar functionality across different classes, ensure consistent behavior and output formats.
2. Changes to one implementation often need to be mirrored in related implementations.
3. Shared utility methods (like `build_absolute_url`) help maintain consistency and reduce code duplication.
