"""Tests for DocumentationChecker."""

import ast
import tempfile
from pathlib import Path

import pytest

from src_check.models.check_result import Severity
from src_check.rules.documentation import DocumentationChecker


class TestDocumentationChecker:
    """Test cases for DocumentationChecker."""

    @pytest.fixture
    def checker(self):
        """Create a DocumentationChecker instance."""
        return DocumentationChecker()

    def test_missing_module_docstring(self, checker, tmp_path):
        """Test detection of missing module docstring."""
        test_file = tmp_path / "test_module.py"
        content = """
# No module docstring
def function():
    pass
"""
        test_file.write_text(content)

        # Parse AST
        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert result.failure_count >= 1  # May find both module and function issues
        assert any(
            "module docstring" in loc.message.lower()
            for loc in result.failure_locations
        )

    def test_missing_function_docstring(self, checker, tmp_path):
        """Test detection of missing function docstring."""
        test_file = tmp_path / "test_func.py"
        content = '''"""Module docstring."""

def function_without_docstring():
    return 42

def function_with_docstring():
    """This function has a docstring."""
    return 43
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert result.failure_count == 1
        assert any(
            "function_without_docstring" in loc.message
            for loc in result.failure_locations
        )

    def test_missing_class_docstring(self, checker, tmp_path):
        """Test detection of missing class docstring."""
        test_file = tmp_path / "test_class.py"
        content = '''"""Module docstring."""

class ClassWithoutDocstring:
    def method(self):
        """Method docstring."""
        pass

class ClassWithDocstring:
    """This class has a docstring."""
    
    def method(self):
        """Method docstring."""
        pass
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert result.failure_count == 1
        assert any(
            "ClassWithoutDocstring" in loc.message for loc in result.failure_locations
        )

    def test_incomplete_function_docstring(self, checker, tmp_path):
        """Test detection of incomplete function docstring."""
        test_file = tmp_path / "test_incomplete.py"
        content = '''"""Module docstring."""

def function_with_params(param1: str, param2: int) -> bool:
    """This function is missing parameter documentation."""
    return len(param1) > param2

def function_complete(param1: str, param2: int) -> bool:
    """Check if string length exceeds threshold.
    
    Args:
        param1: The string to check
        param2: The length threshold
        
    Returns:
        True if string length exceeds threshold
    """
    return len(param1) > param2
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert result.failure_count >= 1
        assert any(
            "parameter" in loc.message.lower() for loc in result.failure_locations
        )

    def test_missing_return_documentation(self, checker, tmp_path):
        """Test detection of missing return value documentation."""
        test_file = tmp_path / "test_return.py"
        content = '''"""Module docstring."""

def function_missing_return() -> int:
    """This function returns something but doesn't document it."""
    return 42

def function_with_return() -> int:
    """Calculate the answer.
    
    Returns:
        The answer to everything
    """
    return 42
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert any("return" in loc.message.lower() for loc in result.failure_locations)

    def test_good_documentation(self, checker, tmp_path):
        """Test that well-documented code passes."""
        test_file = tmp_path / "test_good.py"
        content = '''"""Well-documented module for testing."""

class WellDocumentedClass:
    """A class with proper documentation."""
    
    def __init__(self, value: int):
        """Initialize the class.
        
        Args:
            value: The initial value
        """
        self.value = value
    
    def get_value(self) -> int:
        """Get the current value.
        
        Returns:
            The current value
        """
        return self.value
    
    def set_value(self, value: int) -> None:
        """Set a new value.
        
        Args:
            value: The new value to set
        """
        self.value = value

def standalone_function(text: str) -> str:
    """Process the given text.
    
    Args:
        text: The text to process
        
    Returns:
        The processed text
    """
    return text.upper()
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is None  # Should return None if no issues found

    def test_private_methods_optional(self, checker, tmp_path):
        """Test that private methods don't require docstrings."""
        test_file = tmp_path / "test_private.py"
        content = '''"""Module with private methods."""

class MyClass:
    """A class with private methods."""
    
    def public_method(self):
        """Public method needs docstring."""
        pass
    
    def _private_method(self):
        # Private methods don't require docstrings
        pass
    
    def __dunder_method__(self):
        # Dunder methods don't require docstrings
        pass
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is None  # Should pass

    def test_docstring_format_checking(self, checker, tmp_path):
        """Test detection of malformed docstrings."""
        test_file = tmp_path / "test_format.py"
        content = '''"""Module docstring."""

def bad_format(param: str) -> str:
    """This docstring has bad formatting
    Args: param - the parameter (wrong format)
    Returns: something
    """
    return param

def good_format(param: str) -> str:
    """Process the parameter.
    
    Args:
        param: The parameter to process
        
    Returns:
        The processed parameter
    """
    return param
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        # Should detect formatting issues
        assert result is not None
        assert not result.passed

    def test_async_function_documentation(self, checker, tmp_path):
        """Test async function documentation requirements."""
        test_file = tmp_path / "test_async.py"
        content = '''"""Module with async functions."""

async def async_function_no_doc():
    return "result"

async def async_function_with_doc():
    """Async function with proper documentation."""
    return "result"
'''
        test_file.write_text(content)

        tree = ast.parse(content, filename=str(test_file))
        result = checker.check(tree, str(test_file))

        assert result is not None
        assert not result.passed
        assert any(
            "async_function_no_doc" in loc.message for loc in result.failure_locations
        )
