"""Type hint quality checker."""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from src_check.core.base import BaseChecker
from src_check.models.check_result import CheckResult, Severity


class TypeHintVisitor(ast.NodeVisitor):
    """AST visitor to check type hint quality."""

    def __init__(self, filepath: Path):
        """Initialize the visitor.

        Args:
            filepath: Path to the file being checked
        """
        self.filepath = filepath
        self.issues: List[Tuple[int, str]] = []
        self.generic_types = {
            "dict",
            "list",
            "set",
            "tuple",
            "Dict",
            "List",
            "Set",
            "Tuple",
        }

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function type hints."""
        self._check_function_type_hints(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function type hints."""
        self._check_function_type_hints(node)
        self.generic_visit(node)

    def _check_function_type_hints(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Check type hints for a function.

        Args:
            node: The function node to check
        """
        # Skip private methods and special methods
        if node.name.startswith("_") and node.name != "__init__":
            return

        # Get function signature info
        args = node.args

        # Check parameters (skip 'self' and 'cls')
        params_to_check = []
        if args.args:
            skip_first = False
            if args.args[0].arg in ("self", "cls"):
                skip_first = True
            params_to_check = args.args[1:] if skip_first else args.args

        # Check parameter type hints
        for param in params_to_check:
            if param.annotation is None:
                self.issues.append(
                    (
                        node.lineno,
                        f"Function '{node.name}' parameter '{param.arg}' missing type hint",
                    )
                )

        # Check return type hint (except for __init__)
        if node.name != "__init__" and node.returns is None:
            self.issues.append(
                (node.lineno, f"Function '{node.name}' missing return type hint")
            )

        # Check for generic types without parameters
        self._check_generic_types(node)

    def _check_generic_types(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> None:
        """Check for generic types that should have type parameters.

        Args:
            node: The function node to check
        """
        # Check parameter annotations
        for arg in node.args.args:
            if arg.annotation:
                self._check_annotation(
                    arg.annotation, node.lineno, f"parameter '{arg.arg}'"
                )

        # Check return annotation
        if node.returns:
            self._check_annotation(node.returns, node.lineno, "return type")

    def _check_annotation(
        self, annotation: ast.expr, lineno: int, context: str
    ) -> None:
        """Check if annotation uses generic types without parameters.

        Args:
            annotation: The annotation to check
            lineno: Line number for error reporting
            context: Context description (e.g., "parameter 'x'")
        """
        if isinstance(annotation, ast.Name) and annotation.id in self.generic_types:
            self.issues.append(
                (
                    lineno,
                    f"Generic type '{annotation.id}' used without type parameters in {context}",
                )
            )


class TypeHintChecker(BaseChecker):
    """Check type hint quality and completeness."""

    @property
    def name(self) -> str:
        """Return checker name."""
        return "type_hints"

    @property
    def description(self) -> str:
        """Return checker description."""
        return "Check type hint quality"

    @property
    def category(self) -> str:
        """Return checker category."""
        return "type_safety"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check type hint quality in the file.

        Args:
            ast_tree: The parsed AST of the Python file
            file_path: Path to the file being checked

        Returns:
            Check result with type hint issues
        """
        result = self.create_result(title="Type Hint Quality Check")
        result.severity = Severity.MEDIUM
        result.rule_id = "TYPE001"

        filepath = Path(file_path)
        visitor = TypeHintVisitor(filepath)
        visitor.visit(ast_tree)

        # Add all found issues to result
        for line, message in visitor.issues:
            result.add_failure(file_path=file_path, line=line, message=message)

        # Add fix policy if there are issues
        if not result.passed:
            result.fix_policy = """To fix type hint issues:
1. Add type hints to all public function parameters
2. Add return type hints to all public functions
3. Use specific generic types (e.g., List[str] instead of list)
4. Import typing module for complex types
5. Consider using Optional for nullable parameters"""

            result.fix_example_code = '''from typing import List, Optional, Dict

def process_data(items: List[str], config: Optional[Dict[str, str]] = None) -> List[str]:
    """Process list of items with optional config.
    
    Args:
        items: List of items to process
        config: Optional configuration dict
        
    Returns:
        Processed list of items
    """
    if config:
        # Apply configuration
        pass
    return [item.upper() for item in items]'''

        return result if not result.passed else None
