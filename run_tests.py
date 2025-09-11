#!/usr/bin/env python
"""
Test runner script for the rsyslog logger.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run with coverage report
    python run_tests.py --verbose    # Run with verbose output
"""

import sys
import subprocess
import argparse


def run_tests(coverage=False, verbose=False, specific_test=None):
    """Run the test suite with optional coverage reporting."""

    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test path
    cmd.append("tests/")

    # Add coverage if requested
    if coverage:
        cmd.extend(
            [
                "--cov=logger",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-fail-under=80",  # Require 80% coverage
            ]
        )

    # Add verbose output if requested
    if verbose:
        cmd.append("-v")

    # Run specific test if provided
    if specific_test:
        cmd.append(f"tests/{specific_test}")

    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    # Execute the tests
    result = subprocess.run(cmd)

    if coverage and result.returncode == 0:
        print("\nCoverage report generated in htmlcov/index.html")

    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for rsyslog logger")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--test", "-t", type=str, help="Run specific test file (e.g., test_rotation.py)"
    )

    args = parser.parse_args()

    exit_code = run_tests(
        coverage=args.coverage, verbose=args.verbose, specific_test=args.test
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
