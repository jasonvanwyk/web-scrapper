#!/usr/bin/env python3
"""
Test runner script for the Automated Product Data Scraper.

This script runs all tests and generates a coverage report.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent


def run_tests(test_path=None, coverage=True, qa=False):
    """
    Run tests and generate a coverage report.
    
    Args:
        test_path: Path to specific test file or directory to run
        coverage: Whether to generate a coverage report
        qa: Whether to run QA tests against real supplier sites
    
    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Determine which tests to run
    if test_path:
        test_target = test_path
    elif qa:
        test_target = str(project_root / "tests" / "qa")
    else:
        test_target = str(project_root / "tests")
    
    # Build the command
    if coverage:
        cmd = [
            "python3", "-m", "pytest",
            test_target,
            "--cov=src",
            "--cov-report=term",
            "--cov-report=html:coverage_report",
            "-v"
        ]
        
        # Exclude QA tests from regular coverage runs unless specifically requested
        if not qa and not test_path:
            cmd.append("--ignore=tests/qa")
    else:
        cmd = ["python3", "-m", "pytest", test_target, "-v"]
        
        # Exclude QA tests from regular runs unless specifically requested
        if not qa and not test_path:
            cmd.append("--ignore=tests/qa")
    
    # Run the tests
    print(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Print coverage report location if generated
    if coverage and result.returncode == 0:
        print("\nCoverage report generated in coverage_report/index.html")
    
    return result.returncode


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run tests for the Automated Product Data Scraper")
    parser.add_argument("--test-path", help="Path to specific test file or directory to run")
    parser.add_argument("--no-coverage", action="store_true", help="Don't generate coverage report")
    parser.add_argument("--qa", action="store_true", help="Run QA tests against real supplier sites")
    
    args = parser.parse_args()
    
    # Run the tests
    exit_code = run_tests(
        test_path=args.test_path,
        coverage=not args.no_coverage,
        qa=args.qa
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
