"""Documentation quality checker."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from src_check.core.base import BaseChecker
from src_check.models.check_result import CheckResult, Severity


class DocstringVisitor(ast.NodeVisitor):
    """AST visitor to check documentation quality."""

    def __init__(self, filepath: Path):
        """Initialize the visitor.

        Args:
            filepath: Path to the file being checked
        """
        self.filepath = filepath
        self.issues: List[Tuple[int, str]] = []
        self.has_module_docstring = False

    def visit_Module(self, node: ast.Module) -> None:
        """Check module-level docstring."""
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        ):
            self.has_module_docstring = True
        elif node.body and ast.get_docstring(node):
            self.has_module_docstring = True
        else:
            self.issues.append((1, "Missing module docstring"))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function documentation."""
        self._check_function_doc(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function documentation."""
        self._check_function_doc(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class documentation."""
        docstring = ast.get_docstring(node)

        if not docstring:
            self.issues.append(
                (node.lineno, f"Missing docstring for class '{node.name}'")
            )

        self.generic_visit(node)

    def _check_function_doc(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Check function or method documentation.

        Args:
            node: The function node to check
        """
        # Skip private methods and dunder methods
        if node.name.startswith("_"):
            return

        docstring = ast.get_docstring(node)

        if not docstring:
            self.issues.append(
                (node.lineno, f"Missing docstring for function '{node.name}'")
            )
            return

        # Check docstring completeness
        self._check_docstring_completeness(node, docstring)

    def _check_docstring_completeness(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], docstring: str
    ) -> None:
        """Check if docstring is complete with all necessary sections.

        Args:
            node: The function node
            docstring: The function's docstring
        """
        # Get function signature info
        has_params = len(node.args.args) > 0 or node.args.vararg or node.args.kwarg
        has_return = node.returns is not None

        # Skip 'self' parameter for methods
        params = node.args.args
        if params and params[0].arg == "self":
            params = params[1:]
            has_params = len(params) > 0 or node.args.vararg or node.args.kwarg

        # Check for parameter documentation
        if has_params and params:
            if not self._has_param_documentation(docstring, params):
                self.issues.append(
                    (
                        node.lineno,
                        f"Function '{node.name}' has parameters but missing parameter documentation",
                    )
                )

        # Check for return documentation (skip None returns)
        if has_return and node.name != "__init__":
            # Skip if return type is None
            if node.returns:
                # Check for None in various forms
                if (
                    (hasattr(node.returns, "id") and node.returns.id == "None")
                    or (
                        isinstance(node.returns, ast.Constant)
                        and node.returns.value is None
                    )
                    or (
                        isinstance(node.returns, ast.NameConstant)
                        and node.returns.value is None
                    )
                ):
                    return
            if not self._has_return_documentation(docstring):
                self.issues.append(
                    (
                        node.lineno,
                        f"Function '{node.name}' has return type but missing return documentation",
                    )
                )

    def _has_param_documentation(self, docstring: str, params: List[ast.arg]) -> bool:
        """Check if docstring documents all parameters.

        Args:
            docstring: The docstring to check
            params: List of parameter nodes

        Returns:
            True if all parameters are documented
        """
        # Check for Args: section
        if "Args:" not in docstring and "Parameters:" not in docstring:
            return False

        # Simple check for parameter names in docstring
        for param in params:
            param_pattern = rf"\b{param.arg}\b.*:"
            if not re.search(param_pattern, docstring):
                return False

        return True

    def _has_return_documentation(self, docstring: str) -> bool:
        """Check if docstring documents return value.

        Args:
            docstring: The docstring to check

        Returns:
            True if return is documented
        """
        return "Returns:" in docstring or "Return:" in docstring


class DocumentationChecker(BaseChecker):
    """Check documentation quality and completeness."""

    @property
    def name(self) -> str:
        """Return checker name."""
        return "documentation"

    @property
    def description(self) -> str:
        """Return checker description."""
        return "Check documentation quality"

    @property
    def category(self) -> str:
        """Return checker category."""
        return "documentation"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check documentation quality in the file.

        Args:
            ast_tree: The parsed AST of the Python file
            file_path: Path to the file being checked

        Returns:
            Check result with documentation issues
        """
        result = self.create_result(title="Documentation Quality Check")
        result.severity = Severity.MEDIUM
        result.rule_id = "DOC001"

        filepath = Path(file_path)
        visitor = DocstringVisitor(filepath)
        visitor.visit(ast_tree)

        # Add all found issues to result
        for line, message in visitor.issues:
            result.add_failure(file_path=file_path, line=line, message=message)

        # Add fix policy if there are issues
        if not result.passed:
            result.fix_policy = """To fix documentation issues:
1. Add docstrings to all public modules, classes, and functions
2. Use Google-style or NumPy-style docstring format
3. Document all parameters with 'Args:' section
4. Document return values with 'Returns:' section
5. Include brief description of what the code does"""

            result.fix_example_code = '''def example_function(param1: str, param2: int) -> bool:
    """Check if string length exceeds threshold.
    
    Args:
        param1: The string to check
        param2: The length threshold
        
    Returns:
        True if string length exceeds threshold
    """
    return len(param1) > param2'''

        return result if not result.passed else None
