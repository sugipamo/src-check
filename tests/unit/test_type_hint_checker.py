"""Tests for TypeHintChecker."""

import ast
import tempfile
from pathlib import Path

import pytest

from src_check.models.check_result import Severity
from src_check.rules.type_hints import TypeHintChecker


class TestTypeHintChecker:
    """Test cases for TypeHintChecker."""

    @pytest.fixture
    def checker(self):
        """Create a TypeHintChecker instance."""
        return TypeHintChecker()

    def test_missing_function_type_hints(self, checker, tmp_path):
        """Test detection of missing function type hints."""
        test_file = tmp_path / "test_func.py"
        content = '''"""Module with functions lacking type hints."""

def add(a, b):
    """Add two numbers."""
    return a + b

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        assert any("add" in loc.message and "type hint" in loc.message.lower() for loc in result.failure_locations)

    def test_missing_return_type_hint(self, checker, tmp_path):
        """Test detection of missing return type hints."""
        test_file = tmp_path / "test_return.py"
        content = '''"""Module with missing return type hints."""

def get_value(key: str):
    """Get value by key."""
    return values.get(key, None)

def set_value(key: str, value: int) -> None:
    """Set value for key."""
    values[key] = value
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        assert any("get_value" in loc.message and "return type" in loc.message.lower() for loc in result.failure_locations)

    def test_missing_parameter_type_hints(self, checker, tmp_path):
        """Test detection of missing parameter type hints."""
        test_file = tmp_path / "test_params.py"
        content = '''"""Module with missing parameter type hints."""

def process(data) -> str:
    """Process data."""
    return str(data)

def transform(input_data: dict, options) -> dict:
    """Transform data with options."""
    return {**input_data, **options}
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        # Should find issues with both functions
        assert any("process" in loc.message for loc in result.failure_locations)
        assert any("transform" in loc.message for loc in result.failure_locations)

    def test_class_method_type_hints(self, checker, tmp_path):
        """Test type hint checking in class methods."""
        test_file = tmp_path / "test_class.py"
        content = '''"""Module with class methods."""

class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        assert any("add" in loc.message for loc in result.failure_locations)

    def test_good_type_hints(self, checker, tmp_path):
        """Test that properly typed code passes."""
        test_file = tmp_path / "test_good.py"
        content = '''"""Well-typed module."""

from typing import List, Dict, Optional, Union

def process_list(items: List[str]) -> List[str]:
    """Process a list of strings."""
    return [item.upper() for item in items]

def get_config(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration value."""
    return config.get(key, default)

class DataProcessor:
    """Process various data types."""
    
    def __init__(self, name: str) -> None:
        """Initialize processor."""
        self.name = name
    
    def process(self, data: Union[str, Dict[str, str]]) -> str:
        """Process data."""
        if isinstance(data, dict):
            return str(data)
        return data
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is None  # Should pass with no issues

    def test_private_methods_optional(self, checker, tmp_path):
        """Test that private methods don't require type hints."""
        test_file = tmp_path / "test_private.py"
        content = '''"""Module with private methods."""

class MyClass:
    """A class with private methods."""
    
    def public_method(self, value: int) -> int:
        """Public method with type hints."""
        return self._helper(value)
    
    def _helper(self, value):
        """Private helper method."""
        return value * 2
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is None  # Should pass

    def test_init_return_type_not_required(self, checker, tmp_path):
        """Test that __init__ doesn't require return type hint."""
        test_file = tmp_path / "test_init.py"
        content = '''"""Module with __init__ methods."""

class MyClass:
    """A simple class."""
    
    def __init__(self, value: int):
        """Initialize with value."""
        self.value = value
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is None  # Should pass

    def test_generic_types(self, checker, tmp_path):
        """Test detection of missing generic type parameters."""
        test_file = tmp_path / "test_generic.py"
        content = '''"""Module with generic types."""

def process_dict(data: dict) -> list:
    """Process dictionary - missing generic parameters."""
    return list(data.values())

from typing import Dict, List

def process_typed_dict(data: Dict[str, int]) -> List[int]:
    """Process typed dictionary - properly typed."""
    return list(data.values())
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        # Should complain about untyped dict and list
        assert any("generic" in loc.message.lower() for loc in result.failure_locations)

    def test_async_function_type_hints(self, checker, tmp_path):
        """Test type hint checking for async functions."""
        test_file = tmp_path / "test_async.py"
        content = '''"""Module with async functions."""

async def fetch_data(url):
    """Fetch data from URL - missing type hints."""
    return await http_get(url)

async def process_data(data: dict) -> dict:
    """Process data asynchronously - properly typed."""
    return await transform(data)
'''
        test_file.write_text(content)
        
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))
        
        assert result is not None
        assert not result.passed
        assert any("fetch_data" in loc.message for loc in result.failure_locations)