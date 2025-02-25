# Python Testing Guide

## Table of Contents
- [Overview](#overview)
- [Test Setup](#test-setup)
- [Running Tests](#running-tests)
- [Coverage Reports](#coverage-reports)
- [Test Structure](#test-structure)
- [Mocking](#mocking)
- [Best Practices](#best-practices)

## Overview

This guide covers the testing framework for the Python codebase. We use pytest as our testing framework along with unittest.mock for mocking dependencies. The guide will help you understand how to write, run, and maintain tests across the project.

## Test Setup

### Required Packages
```bash
pip install pytest pytest-cov
```

### Project Structure
```
project/
├── src/
│   ├── __init__.py
│   ├── module1.py
│   ├── module2.py
│   └── ...
└── tests/
    ├── __init__.py
    ├── test_module1.py
    ├── test_module2.py
    └── ...
```

### Creating New Test Files
- Name test files with prefix `test_`
- Mirror the src directory structure in tests
- One test file per source file (generally)

Example:
```python
# src/data_processor.py -> tests/test_data_processor.py

from src.data_processor import DataProcessor

def test_process_data():
    processor = DataProcessor()
    result = processor.process([1, 2, 3])
    assert result == [2, 4, 6]
```

## Running Tests

### Basic Commands
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_module1.py

# Run tests matching pattern
pytest -k "pattern"

# Run tests and stop on first failure
pytest -x

# Show print statements during tests
pytest -s
```

### Coverage Testing
```bash
# Run tests with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ -v --cov=src --cov-report=html

# Generate XML coverage report (for CI tools)
pytest tests/ -v --cov=src --cov-report=xml
```

## Coverage Reports

### Understanding Coverage Output
```
Name                    Stmts   Miss Branch   Miss  Cover
---------------------------------------------------
src/module1.py            45      2     12      1    95%
src/module2.py            30      0      8      0   100%
```

- `Stmts`: Number of statements
- `Miss`: Number of statements not covered
- `Branch`: Number of branches (if/else)
- `Cover`: Overall coverage percentage

### Coverage Configuration
Create `pytest.ini` for custom settings:
```ini
[pytest]
addopts = -v --cov=src --cov-report=term-missing
testpaths = tests
python_files = test_*.py
```

## Test Structure

### Basic Test Structure
```python
import pytest
from unittest.mock import MagicMock, patch

def test_simple_function():
    """Test a simple function without setup."""
    result = my_function(1, 2)
    assert result == 3

class TestComplexClass:
    """Group tests for a complex class."""
    
    def setup_method(self):
        """Runs before each test method."""
        self.object = MyClass()
    
    def test_method_one(self):
        result = self.object.method_one()
        assert result == expected_value
```

### Using Fixtures
```python
@pytest.fixture
def sample_data():
    """Fixture providing sample data."""
    return {
        'id': 1,
        'name': 'test'
    }

@pytest.fixture
def mock_database():
    """Fixture providing a mock database."""
    db = MagicMock()
    db.query.return_value = ['result1', 'result2']
    return db

def test_with_fixtures(sample_data, mock_database):
    result = process_data(sample_data, mock_database)
    assert result == expected_output
```

## Mocking

### Basic Mocking
```python
# Mock an object
mock_object = MagicMock()
mock_object.method.return_value = 'result'

# Mock with side effects
mock_object.method.side_effect = [1, 2, 3]  # Returns values in sequence
mock_object.method.side_effect = Exception('error')  # Raises exception

# Verify calls
mock_object.method.assert_called()
mock_object.method.assert_called_once_with('arg')
```

### Patching
```python
# Patch a module
@patch('module.ClassName')
def test_function(mock_class):
    mock_class.return_value.method.return_value = 'result'
    # Test code here

# Patch multiple items
@patch('module.Class1')
@patch('module.Class2')
def test_function(mock_class2, mock_class1):
    # Decorators are applied bottom-up
    # Test code here

# Patch context manager
def test_function():
    with patch('module.ClassName') as mock_class:
        # Test code here
```

## Best Practices

### Writing Good Tests

1. **Clear Names**
```python
# Good
def test_user_creation_with_valid_data():
    
# Avoid
def test_user_1():
```

2. **One Assert Per Test**
```python
# Good
def test_user_name_validation():
    user = create_user("John")
    assert user.name == "John"

def test_user_email_validation():
    user = create_user("John", "john@example.com")
    assert user.email == "john@example.com"
```

3. **Test Independence**
```python
def test_independent():
    # Each test should be able to run independently
    # Don't rely on state from other tests
    setup_required_state()
    run_test()
    cleanup_state()
```

4. **Testing Exceptions**
```python
def test_invalid_input():
    with pytest.raises(ValueError) as exc_info:
        process_data(-1)
    assert str(exc_info.value) == "Input must be positive"
```

### Test Documentation

1. **Docstrings**
```python
def test_order_processing():
    """
    Test order processing with valid input.
    
    Verifies:
    - Order is saved to database
    - Confirmation email is sent
    - Inventory is updated
    """
```

2. **Comments for Complex Tests**
```python
def test_complex_scenario():
    # Setup initial state
    setup_data()
    
    # Simulate user action
    result = perform_action()
    
    # Verify multiple outcomes
    assert result.status == 'success'
    assert result.data['processed'] == True
```

### Organizing Test Files

1. **Group Related Tests**
```python
class TestUserAuthentication:
    """Tests for user authentication flow."""
    
    def test_login(self):
        pass
        
    def test_logout(self):
        pass

class TestUserProfile:
    """Tests for user profile management."""
    
    def test_update_profile(self):
        pass
```

2. **Shared Fixtures**
```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def database_connection():
    """Shared database fixture."""
    connection = create_connection()
    yield connection
    connection.close()
```

Remember:
- Write tests as you write code
- Aim for high coverage but focus on critical paths
- Keep tests simple and readable
- Use meaningful test data
- Consider edge cases and error conditions