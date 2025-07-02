"""
Code quality checkers.
"""

import ast
import re
from typing import Optional, Dict, Set, Union, Tuple

from src_check.core.base import BaseChecker
from src_check.models import CheckResult, Severity


class CodeQualityChecker(BaseChecker):
    """Checks for code quality issues and best practices."""

    @property
    def name(self) -> str:
        return "code_quality"

    @property
    def description(self) -> str:
        return "Code quality and best practices"

    @property
    def category(self) -> str:
        return "code_quality"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for code quality issues."""
        result = self.create_result()

        # Use multiple visitors for different quality checks
        visitors = [
            NamingConventionVisitor(file_path, result),
            PrintStatementVisitor(file_path, result),
            ComplexityVisitor(file_path, result),
            UnusedImportsVisitor(file_path, result),
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
                "Code quality improvements:\n"
                "1. Follow PEP 8 naming conventions (snake_case for functions/variables)\n"
                "2. Replace print statements with proper logging\n"
                "3. Reduce function complexity by extracting smaller functions\n"
                "4. Remove unused imports to keep code clean"
            )

            return result

        return None


class NamingConventionVisitor(ast.NodeVisitor):
    """Checks for PEP 8 naming conventions."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function naming."""
        # Skip visit_* methods (AST visitor pattern)
        if node.name.startswith("visit_"):
            self.generic_visit(node)
            return

        if not self._is_snake_case(node.name) and not node.name.startswith("_"):
            # Allow dunder methods
            if not (node.name.startswith("__") and node.name.endswith("__")):
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Function '{node.name}' should use snake_case naming",
                    code_snippet=f"def {node.name}(...)",
                )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function naming."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class naming."""
        if not self._is_pascal_case(node.name):
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Class '{node.name}' should use PascalCase naming",
                code_snippet=f"class {node.name}:",
            )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Check variable naming for constants."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check if it looks like a constant (all uppercase)
                if target.id.isupper() and not self._is_constant_case(target.id):
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Constant '{target.id}' should use UPPER_SNAKE_CASE",
                        code_snippet=f"{target.id} = ...",
                    )
                # Check regular variables
                elif not target.id.isupper() and not self._is_snake_case(target.id):
                    # Allow single letter variables and private variables
                    if len(target.id) > 1 and not target.id.startswith("_"):
                        self.result.add_failure(
                            file_path=self.file_path,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Variable '{target.id}' should use snake_case naming",
                            code_snippet=f"{target.id} = ...",
                        )

        self.generic_visit(node)

    def _is_snake_case(self, name: str) -> bool:
        """Check if name is in snake_case."""
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))

    def _is_pascal_case(self, name: str) -> bool:
        """Check if name is in PascalCase."""
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    def _is_constant_case(self, name: str) -> bool:
        """Check if name is in CONSTANT_CASE."""
        return bool(re.match(r"^[A-Z][A-Z0-9_]*$", name))


class PrintStatementVisitor(ast.NodeVisitor):
    """Detects print statements that should use logging."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.in_main = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track if we're in a main function."""
        old_in_main = self.in_main
        if node.name == "main" or node.name == "__main__":
            self.in_main = True

        self.generic_visit(node)
        self.in_main = old_in_main

    def visit_Call(self, node: ast.Call) -> None:
        """Check for print function calls."""
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # Allow prints in main or scripts
            if not self.in_main:
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="Use logging instead of print statements",
                    code_snippet="print(...)",
                )

        self.generic_visit(node)


class ComplexityVisitor(ast.NodeVisitor):
    """Checks for overly complex functions."""

    MAX_COMPLEXITY = 10  # McCabe complexity threshold

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function complexity."""
        complexity = self._calculate_complexity(node)

        if complexity > self.MAX_COMPLEXITY:
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Function '{node.name}' is too complex (complexity: {complexity}, max: {self.MAX_COMPLEXITY})",
                code_snippet=f"def {node.name}(...)",
            )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function complexity."""
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate McCabe cyclomatic complexity."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and' or 'or' adds a branch
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity


class UnusedImportsVisitor(ast.NodeVisitor):
    """Detects unused imports."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.imports: Dict[str, Tuple[int, int, str]] = {}  # name -> (line, col, full_name)
        self.used_names: Set[str] = set()
        self._analyzed = False  # Flag to prevent duplicate analysis

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = (node.lineno, node.col_offset, alias.name)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if name != "*":  # Ignore star imports
                full_name = f"{node.module}.{alias.name}" if node.module else alias.name
                self.imports[name] = (node.lineno, node.col_offset, full_name)

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Track name usage."""
        self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Track attribute usage."""
        # Get the root name
        root: Union[ast.expr, ast.AST] = node
        while isinstance(root, ast.Attribute):
            root = root.value
        if isinstance(root, ast.Name):
            self.used_names.add(root.id)

        self.generic_visit(node)

    def finalize(self) -> None:
        """Check for unused imports (call after visiting)."""
        if self._analyzed:
            return  # Prevent duplicate analysis

        self._analyzed = True

        # Check for unused imports
        for name, (line, col, full_name) in self.imports.items():
            if name not in self.used_names:
                # Common exceptions
                if name not in ["__future__", "__all__"] and not name.startswith("_"):
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=line,
                        column=col,
                        message=f"Unused import: {full_name}",
                        code_snippet=f"import {full_name}",
                    )
