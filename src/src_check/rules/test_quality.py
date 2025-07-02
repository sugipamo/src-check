"""
Test quality checkers.
"""

import ast
import re
from typing import Optional

from src_check.core.base import BaseChecker
from src_check.models import CheckResult, Severity


class TestQualityChecker(BaseChecker):
    """Checks for test quality and coverage issues."""

    @property
    def name(self) -> str:
        return "test_quality"

    @property
    def description(self) -> str:
        return "Test quality and coverage"

    @property
    def category(self) -> str:
        return "test"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for test quality issues."""
        result = self.create_result()

        # Determine if this is a test file
        is_test_file = self._is_test_file(file_path)

        if is_test_file:
            # Check test file quality
            visitors = [
                TestStructureVisitor(file_path, result),
                TestAssertionVisitor(file_path, result),
                TestNamingVisitor(file_path, result),
            ]
        else:
            # Check for missing tests
            visitors = [
                MissingTestsVisitor(file_path, result),
            ]

        for visitor in visitors:
            visitor.visit(ast_tree)
            # Call finalize for visitors that need it
            if hasattr(visitor, "finalize"):
                visitor.finalize()

        # Set severity based on findings
        if result.failure_count > 0:
            result.severity = Severity.MEDIUM

            # Add fix policy
            result.fix_policy = (
                "Test quality improvements:\n"
                "1. Ensure all functions have corresponding tests\n"
                "2. Use descriptive test names that explain what is being tested\n"
                "3. Include meaningful assertions, not just 'assert True'\n"
                "4. Structure tests with Arrange-Act-Assert pattern\n"
                "5. Avoid empty test functions"
            )

            return result

        return None

    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        return "test" in file_path.lower() or file_path.endswith("_test.py")


class TestStructureVisitor(ast.NodeVisitor):
    """Checks test structure and organization."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check test function structure."""
        if node.name.startswith("test_"):
            # Check for empty test
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Empty test function: {node.name}",
                    code_snippet=f"def {node.name}(): pass",
                )

            # Check for missing docstring
            if not ast.get_docstring(node):
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Test function '{node.name}' missing docstring",
                    code_snippet=f"def {node.name}():",
                )

            # Check test length (too long tests are hard to understand)
            if hasattr(node, "end_lineno"):
                test_lines = node.end_lineno - node.lineno
                if test_lines > 50:
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Test function '{node.name}' is too long ({test_lines} lines)",
                        code_snippet=f"def {node.name}(): # {test_lines} lines",
                    )

        self.generic_visit(node)


class TestAssertionVisitor(ast.NodeVisitor):
    """Checks for proper test assertions."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.current_test = None
        self.assertion_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track test functions."""
        if node.name.startswith("test_"):
            old_test = self.current_test
            old_count = self.assertion_count

            self.current_test = node.name
            self.assertion_count = 0

            self.generic_visit(node)

            # Check assertion count
            if self.assertion_count == 0:
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Test '{node.name}' has no assertions",
                    code_snippet=f"def {node.name}(): # no assert",
                )
            elif self.assertion_count > 10:
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Test '{node.name}' has too many assertions ({self.assertion_count})",
                    code_snippet=f"def {node.name}(): # {self.assertion_count} asserts",
                )

            self.current_test = old_test
            self.assertion_count = old_count
        else:
            self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        """Count assertions."""
        if self.current_test:
            self.assertion_count += 1

            # Check for trivial assertions
            if isinstance(node.test, ast.Constant):
                if node.test.value is True:
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Trivial assertion: 'assert True'",
                        code_snippet="assert True",
                    )
                elif node.test.value is False:
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Test will always fail: 'assert False'",
                        code_snippet="assert False",
                    )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Count assertion method calls."""
        if self.current_test:
            func_name = self._get_function_name(node.func)

            # Common assertion methods
            if any(
                assert_name in func_name
                for assert_name in [
                    "assert",
                    "assertEqual",
                    "assertTrue",
                    "assertFalse",
                    "assertIn",
                    "assertRaises",
                    "pytest.raises",
                ]
            ):
                self.assertion_count += 1

        self.generic_visit(node)

    def _get_function_name(self, node) -> str:
        """Extract function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""


class TestNamingVisitor(ast.NodeVisitor):
    """Checks test naming conventions."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check test function naming."""
        if node.name.startswith("test"):
            # Check for generic test names
            generic_patterns = [
                r"^test\d+$",  # test1, test2, etc.
                r"^test_test$",
                r"^test_$",
                r"^test_[a-z]$",  # test_a, test_b, etc.
            ]

            for pattern in generic_patterns:
                if re.match(pattern, node.name):
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Generic test name: '{node.name}' - use descriptive names",
                        code_snippet=f"def {node.name}():",
                    )
                    break

            # Check for test_ prefix without description
            if node.name == "test_":
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="Test name 'test_' needs a description",
                    code_snippet="def test_():",
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check test class naming."""
        if node.name.startswith("Test"):
            # Check for generic class names
            if node.name in ["Test", "Tests", "Testing"]:
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Generic test class name: '{node.name}' - use descriptive names",
                    code_snippet=f"class {node.name}:",
                )

        self.generic_visit(node)


class MissingTestsVisitor(ast.NodeVisitor):
    """Detects functions that might be missing tests."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.public_functions = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track public functions."""
        # Skip private functions and special methods
        if not node.name.startswith("_"):
            # Skip simple getters/setters
            if not self._is_simple_accessor(node):
                self.public_functions.append(node)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async public functions."""
        self.visit_FunctionDef(node)

    def finalize(self) -> None:
        """Report findings after visiting."""
        # Report if file has many untested functions
        if len(self.public_functions) > 3:
            self.result.add_failure(
                file_path=self.file_path,
                line=1,
                column=0,
                message=f"File has {len(self.public_functions)} public functions - consider adding tests",
                code_snippet=f"Functions: {', '.join(f.name for f in self.public_functions[:3])}...",
            )

    def _is_simple_accessor(self, node: ast.FunctionDef) -> bool:
        """Check if function is a simple getter/setter."""
        # Simple heuristic: function with one line that returns an attribute
        if len(node.body) == 1:
            stmt = node.body[0]
            if isinstance(stmt, ast.Return):
                if isinstance(stmt.value, ast.Attribute):
                    return True
                if isinstance(stmt.value, ast.Name):
                    return True
        return False
