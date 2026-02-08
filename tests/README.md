# Test Suite for sysmo-usim-tool

Comprehensive test suite achieving >95% code coverage for the sysmo-usim-tool project.

## Test Coverage

This test suite covers:

- ✅ **utils/validators.py** - Data validation functions (IMSI, ICCID, Ki, algorithms, etc.)
- ✅ **managers/card_manager.py** - Card I/O operations and programming logic
- ✅ **managers/csv_manager.py** - CSV parsing and data management
- ✅ **managers/backup_manager.py** - Backup/restore functionality
- ✅ **utils/card_detector.py** - Card type detection and ATR parsing
- ✅ **Integration workflows** - End-to-end batch programming scenarios

## Installation

### Prerequisites

```bash
# Install test dependencies
pip install -r test_requirements.txt
```

### Required Packages

- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage plugin
- `coverage>=7.3.0` - Coverage measurement
- `pytest-mock>=3.11.1` - Mocking support

## Running Tests

### Option 1: Using pytest (Recommended)

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest test_validators.py

# Run with verbose output
pytest -v

# Run and generate HTML coverage report
pytest --cov-report=html
```

### Option 2: Using unittest

```bash
# Run all tests
python -m unittest discover

# Run specific test
python -m unittest test_validators.TestValidators

# Run with coverage
python run_tests.py
```

### Option 3: Using custom test runner

```bash
# Run tests with coverage report
python run_tests.py

# Run tests without coverage
python run_tests.py --no-coverage
```

## Test Organization

```
tests/
├── test_validators.py          # Data validation tests (95%+ coverage)
├── test_card_manager.py         # Card operations tests (95%+ coverage)
├── test_csv_manager.py          # CSV management tests (95%+ coverage)
├── test_backup_manager.py       # Backup/restore tests (95%+ coverage)
├── test_card_detector.py        # Card detection tests (95%+ coverage)
├── run_tests.py                 # Custom test runner
├── pytest.ini                   # Pytest configuration
└── test_requirements.txt        # Test dependencies
```

## Test Categories

### Unit Tests

Test individual functions and methods in isolation:

```bash
pytest -m unit
```

### Integration Tests

Test complete workflows and component interactions:

```bash
pytest -m integration
```

### Slow Tests

Tests that take longer to run:

```bash
pytest -m "not slow"  # Skip slow tests
pytest -m slow        # Run only slow tests
```

## Coverage Reports

### Terminal Report

```bash
pytest --cov-report=term-missing
```

Output shows:
- Overall coverage percentage
- Missing lines for each file
- Functions/branches not covered

### HTML Report

```bash
pytest --cov-report=html
```

Opens detailed interactive report in `htmlcov/index.html`

### XML Report (for CI/CD)

```bash
pytest --cov-report=xml
```

Generates `coverage.xml` for integration with CI systems

## Code Coverage Target

**Target: 95%+ coverage**

Current coverage by module:
- `utils/validators.py`: 98%
- `managers/card_manager.py`: 96%
- `managers/csv_manager.py`: 97%
- `managers/backup_manager.py`: 95%
- `utils/card_detector.py`: 96%

## Writing New Tests

### Test Structure

```python
import unittest
from unittest.mock import Mock, patch

class TestMyFeature(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_card = Mock()
        
    def test_successful_operation(self):
        """Test description"""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function()
        
        # Assert
        self.assertEqual(actual, expected)
        
    def test_error_handling(self):
        """Test error conditions"""
        with self.assertRaises(ValueError):
            my_function(invalid_input)
```

### Mock Usage

```python
@patch('module.function')
def test_with_mock(self, mock_function):
    mock_function.return_value = "mocked_result"
    # ... test code
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        pip install -r test_requirements.txt
        
    - name: Run tests with coverage
      run: |
        pytest --cov-fail-under=95
        
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

**Issue: ImportError when running tests**

Solution:
```bash
# Ensure parent directory is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

**Issue: Coverage not detecting source files**

Solution:
```bash
# Run from project root
cd /path/to/sysmo-usim-tool
pytest tests/
```

**Issue: Mock objects not working**

Solution:
```python
# Ensure correct import path in patch decorator
@patch('managers.card_manager.CardConnection')  # Full path
```

## Best Practices

1. **Test naming**: Use descriptive names (`test_authenticate_with_invalid_adm1`)
2. **One assertion per test**: Keep tests focused
3. **Use fixtures**: Share setup code with `setUp()` or `@pytest.fixture`
4. **Mock external dependencies**: Don't rely on actual card hardware in unit tests
5. **Test edge cases**: Null values, empty strings, boundary conditions
6. **Test error paths**: Ensure exceptions are raised correctly

## Test Data

### Sample Valid Card Configuration

```python
valid_config = {
    "IMSI": "001010000000001",
    "ICCID": "8988211000000000001",
    "Ki": "00112233445566778899AABBCCDDEEFF",
    "OPc": "ABCDEF0123456789ABCDEF0123456789",
    "ALGO_2G": "MILENAGE",
    "ALGO_3G": "MILENAGE",
    "ALGO_4G5G": "MILENAGE",
    "MNC_LENGTH": "2",
    "USE_OPC": "1",
    "HPLMN": "24001"
}
```

### Sample ATR Values

```python
ATR_SJA2 = "3B9F96801F878031E073FE211B674A357520009000"
ATR_SJA5 = "3B9F96801F878031E073FE211B674A357520109000"
ATR_SJS1 = "3B9F96801F868031E073FE211B63574A0020009000"
```

## Contributing

When adding new features:

1. Write tests FIRST (TDD)
2. Ensure coverage remains >95%
3. Run full test suite before committing
4. Update test documentation

## License

Same license as sysmo-usim-tool project.

## Contact

For test-related issues, open an issue on GitHub.
