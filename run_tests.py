#!/usr/bin/env python
"""
Test runner for POS Monitor
Runs unit tests and generates coverage report
"""

import sys
import os
import unittest
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_tests():
    """Run all unit tests"""
    print("POS Monitor Test Suite")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_coverage():
    """Run tests with coverage analysis"""
    try:
        import coverage
    except ImportError:
        print("Coverage module not installed. Install with: pip install coverage")
        return 1
    
    print("Running tests with coverage analysis...")
    
    # Initialize coverage
    cov = coverage.Coverage(source=['pos_monitor_core', 'pos_monitor_async_logger'])
    cov.start()
    
    # Run tests
    exit_code = run_tests()
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\nCoverage Report:")
    print("-" * 60)
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='htmlcov')
    print(f"\nDetailed HTML coverage report generated in: htmlcov/index.html")
    
    return exit_code


if __name__ == "__main__":
    # Check for coverage flag
    if "--coverage" in sys.argv:
        exit_code = run_coverage()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)