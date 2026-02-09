"""
Test runner with coverage reporting.
Discovers and runs unit, integration, and e2e tests.
"""

import unittest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests_with_coverage():
    """Run all tests with coverage reporting."""
    try:
        import coverage

        cov = coverage.Coverage(
            source=[
                os.path.join(project_root, 'managers'),
                os.path.join(project_root, 'utils'),
                os.path.join(project_root, 'widgets'),
                os.path.join(project_root, 'dialogs'),
            ]
        )
        cov.start()

        suite = _discover_all_tests()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        cov.stop()
        cov.save()

        print("\n" + "=" * 70)
        print("COVERAGE REPORT")
        print("=" * 70)
        total_coverage = cov.report()

        try:
            cov.html_report(directory=os.path.join(project_root, 'htmlcov'))
            print("\nHTML report generated in 'htmlcov' directory")
        except Exception:
            pass

        print(f"\nTotal coverage: {total_coverage:.1f}%")
        target = 90.0
        if total_coverage >= target:
            print(f"Coverage target of {target}% MET!")
        else:
            print(f"Coverage target of {target}% NOT MET (currently {total_coverage:.1f}%)")

        return result.wasSuccessful()

    except ImportError:
        print("Warning: 'coverage' package not installed. Running tests without coverage...")
        print("Install with: pip install coverage")
        return run_tests_only()


def run_tests_only():
    """Run all tests without coverage."""
    suite = _discover_all_tests()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def _discover_all_tests():
    """Discover tests from all directories: unit, integration, e2e."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Unit tests (tests/*.py)
    unit_suite = loader.discover(test_dir, pattern='test_*.py', top_level_dir=test_dir)
    suite.addTests(unit_suite)

    # Integration tests (tests/integration/*.py)
    integration_dir = os.path.join(test_dir, 'integration')
    if os.path.isdir(integration_dir):
        int_suite = loader.discover(integration_dir, pattern='test_*.py', top_level_dir=test_dir)
        suite.addTests(int_suite)

    # E2E tests (tests/e2e/*.py)
    e2e_dir = os.path.join(test_dir, 'e2e')
    if os.path.isdir(e2e_dir):
        e2e_suite = loader.discover(e2e_dir, pattern='test_*.py', top_level_dir=test_dir)
        suite.addTests(e2e_suite)

    return suite


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run sysmo-usim-tool tests')
    parser.add_argument('--no-coverage', action='store_true',
                        help='Run tests without coverage reporting')
    parser.add_argument('--unit-only', action='store_true',
                        help='Run only unit tests')

    args = parser.parse_args()

    if args.no_coverage:
        success = run_tests_only()
    else:
        success = run_tests_with_coverage()

    sys.exit(0 if success else 1)
