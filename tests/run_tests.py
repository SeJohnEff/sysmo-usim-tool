"""
Test runner with coverage reporting
Run all tests and generate coverage report
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests_with_coverage():
    """Run all tests with coverage reporting"""
    try:
        import coverage
        
        # Start coverage
        cov = coverage.Coverage(source=['managers', 'utils', 'widgets', 'dialogs'])
        cov.start()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Print coverage report
        print("\n" + "="*70)
        print("COVERAGE REPORT")
        print("="*70)
        cov.report()
        
        # Generate HTML coverage report
        print("\nGenerating HTML coverage report...")
        cov.html_report(directory='htmlcov')
        print("HTML report generated in 'htmlcov' directory")
        
        # Check if we met 95% coverage target
        total_coverage = cov.report(show_missing=False)
        print(f"\nTotal coverage: {total_coverage:.1f}%")
        
        if total_coverage >= 95.0:
            print("✓ Coverage target of 95% MET!")
        else:
            print(f"✗ Coverage target of 95% NOT MET (currently {total_coverage:.1f}%)")
        
        return result.wasSuccessful() and total_coverage >= 95.0
        
    except ImportError:
        print("Warning: 'coverage' package not installed. Running tests without coverage...")
        print("Install with: pip install coverage")
        
        # Run tests without coverage
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


def run_tests_only():
    """Run tests without coverage"""
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run sysmo-usim-tool tests')
    parser.add_argument('--no-coverage', action='store_true',
                        help='Run tests without coverage reporting')
    
    args = parser.parse_args()
    
    if args.no_coverage:
        success = run_tests_only()
    else:
        success = run_tests_with_coverage()
    
    sys.exit(0 if success else 1)
