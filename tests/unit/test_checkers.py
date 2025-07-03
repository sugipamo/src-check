"""
Unit tests for quality checkers.
"""

import ast

import pytest

from src_check.rules import (
    ArchitectureChecker,
    CodeQualityChecker,
    SecurityChecker,
    TestQualityChecker,
)


class TestSecurityChecker:
    """Test SecurityChecker."""

    @pytest.mark.unit
    def test_hardcoded_password(self):
        """Test detection of hardcoded passwords."""
        code = """
password = "secret123"
api_key = "sk-1234567890"
"""
        tree = ast.parse(code)
        checker = SecurityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert result.failure_count == 2
        assert any("password" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_eval_usage(self):
        """Test detection of eval usage."""
        code = """
user_input = input("Enter code: ")
result = eval(user_input)
"""
        tree = ast.parse(code)
        checker = SecurityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("eval" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_sql_injection(self):
        """Test detection of SQL injection."""
        code = """
query = "SELECT * FROM users WHERE id = " + user_id
"""
        tree = ast.parse(code)
        checker = SecurityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("SQL injection" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_pickle_usage(self):
        """Test detection of pickle usage."""
        code = """
import pickle
data = pickle.loads(user_data)
"""
        tree = ast.parse(code)
        checker = SecurityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert result.failure_count >= 2  # import and usage


class TestCodeQualityChecker:
    """Test CodeQualityChecker."""

    @pytest.mark.unit
    def test_naming_convention(self):
        """Test detection of naming convention violations."""
        code = """
def camelCaseFunction():
    pass

class lower_case_class:
    pass

BADCONSTANT = 10
"""
        tree = ast.parse(code)
        checker = CodeQualityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert result.failure_count >= 2  # At least function and class

    @pytest.mark.unit
    def test_print_statements(self):
        """Test detection of print statements."""
        code = """
def process_data(data):
    print("Processing:", data)
    return data * 2
"""
        tree = ast.parse(code)
        checker = CodeQualityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("print" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_complex_function(self):
        """Test detection of complex functions."""
        code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:  # Add one more to exceed threshold
                                return "big"
    elif x < 0:
        if x < -10:
            if x < -20:
                return "small"
    else:
        return "zero"
"""
        tree = ast.parse(code)
        checker = CodeQualityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("complex" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_unused_imports(self):
        """Test detection of unused imports."""
        code = """
import os
import sys
import json

def hello():
    print("Hello")
"""
        tree = ast.parse(code)
        checker = CodeQualityChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert result.failure_count >= 2  # At least 2 unused imports


class TestArchitectureChecker:
    """Test ArchitectureChecker."""

    @pytest.mark.unit
    def test_circular_import_detection(self):
        """Test detection of potential circular imports."""
        code = """
def get_user():
    from models import User  # Import inside function
    return User()
"""
        tree = ast.parse(code)
        checker = ArchitectureChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("circular" in str(loc).lower() for loc in result.failure_locations)

    @pytest.mark.unit
    def test_god_class(self):
        """Test detection of god classes."""
        code = """
class GodClass:
""" + "\n".join(
            [f"    def method{i}(self): pass" for i in range(25)]
        )

        tree = ast.parse(code)
        checker = ArchitectureChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("God class" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_high_coupling(self):
        """Test detection of high coupling."""
        code = """
import module1
import module2
import module3
import module4
import module5
import module6
import module7
import module8
import module9
import module10
import module11
import module12

def process():
    module1.func()
    module2.func()
"""
        tree = ast.parse(code)
        checker = ArchitectureChecker()
        result = checker.check(tree, "test.py")

        assert result is not None
        assert any("coupling" in str(loc).lower() for loc in result.failure_locations)


class TestTestQualityChecker:
    """Test TestQualityChecker."""

    @pytest.mark.unit
    def test_empty_test_detection(self):
        """Test detection of empty tests."""
        code = """
def test_empty():
    pass
"""
        tree = ast.parse(code)
        checker = TestQualityChecker()
        result = checker.check(tree, "test_file.py")

        assert result is not None
        assert any("Empty test" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_missing_assertions(self):
        """Test detection of tests without assertions."""
        code = """
def test_no_assert():
    x = 1 + 1
    y = x * 2
    # No assertions!
"""
        tree = ast.parse(code)
        checker = TestQualityChecker()
        result = checker.check(tree, "test_file.py")

        assert result is not None
        assert any("no assertions" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_trivial_assertions(self):
        """Test detection of trivial assertions."""
        code = """
def test_trivial():
    assert True
"""
        tree = ast.parse(code)
        checker = TestQualityChecker()
        result = checker.check(tree, "test_file.py")

        assert result is not None
        assert any("Trivial assertion" in str(loc) for loc in result.failure_locations)

    @pytest.mark.unit
    def test_generic_test_names(self):
        """Test detection of generic test names."""
        code = """
def test1():
    assert True

def test_():
    assert True

class Test:
    pass
"""
        tree = ast.parse(code)
        checker = TestQualityChecker()
        result = checker.check(tree, "test_file.py")

        assert result is not None
        # Should detect generic names
        assert any(
            "Generic" in str(loc) or "needs a description" in str(loc)
            for loc in result.failure_locations
        )
