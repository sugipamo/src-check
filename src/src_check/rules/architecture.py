"""
Architecture quality checkers.
"""

import ast
from collections import defaultdict
from typing import Optional, Set, List, Dict, Union

from src_check.core.base import BaseChecker
from src_check.models import CheckResult, Severity


class ArchitectureChecker(BaseChecker):
    """Checks for architectural issues and design problems."""

    @property
    def name(self) -> str:
        return "architecture"

    @property
    def description(self) -> str:
        return "Architecture and design quality"

    @property
    def category(self) -> str:
        return "architecture"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for architecture issues."""
        result = self.create_result()

        # Use multiple visitors for different architecture checks
        visitors = [
            CircularImportVisitor(file_path, result),
            LayerViolationVisitor(file_path, result),
            CouplingVisitor(file_path, result),
            GodClassVisitor(file_path, result),
        ]

        for visitor in visitors:
            visitor.visit(ast_tree)
            # Call finalize for visitors that need it
            if hasattr(visitor, "finalize"):
                visitor.finalize()

        # Set severity based on findings
        if result.failure_count > 0:
            # Circular imports are critical
            for failure in result.failure_locations:
                if "circular" in failure.message.lower():
                    result.severity = Severity.HIGH
                    break
            else:
                result.severity = Severity.MEDIUM

            # Add fix policy
            result.fix_policy = (
                "Architecture improvements:\n"
                "1. Break circular imports by introducing interfaces or moving shared code\n"
                "2. Follow layer architecture: UI → Business Logic → Data Access\n"
                "3. Reduce coupling between modules\n"
                "4. Split large classes into smaller, focused classes"
            )

            return result

        return None


class CircularImportVisitor(ast.NodeVisitor):
    """Detects potential circular imports."""

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.imports: Set[str] = set()
        self.deferred_imports: List[Union[ast.Import, ast.ImportFrom]] = []  # Imports inside functions/classes
        self.scope_depth = 0  # Track how deep we are in nested scopes

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track entering function scope."""
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track entering async function scope."""
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track entering class scope."""
        self.scope_depth += 1
        self.generic_visit(node)
        self.scope_depth -= 1

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        # Check if import is at module level
        if self._is_module_level():
            for alias in node.names:
                self.imports.add(alias.name)
        else:
            # Import inside function/class (deferred)
            self.deferred_imports.append(node)

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        if node.module:
            if self._is_module_level():
                self.imports.add(node.module)
            else:
                self.deferred_imports.append(node)

        self.generic_visit(node)

    def finalize(self) -> None:
        """Analyze imports after visiting."""
        # Check for deferred imports (potential circular import workaround)
        if self.deferred_imports:
            for import_node in self.deferred_imports:
                self.result.add_failure(
                    file_path=self.file_path,
                    line=import_node.lineno,
                    column=import_node.col_offset,
                    message="Import inside function/class may indicate circular dependency",
                    code_snippet="import inside function",
                )

    def _is_module_level(self) -> bool:
        """Check if we're at module level (not inside any function or class)."""
        return self.scope_depth == 0


class LayerViolationVisitor(ast.NodeVisitor):
    """Detects violations of layered architecture."""

    # Common layer patterns
    LAYER_PATTERNS = {
        "ui": ["ui", "view", "controller", "handler", "route"],
        "business": ["service", "business", "logic", "domain", "core"],
        "data": ["repository", "dao", "model", "entity", "database", "db"],
    }

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.current_layer = self._detect_layer(file_path)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check layer violations in imports."""
        if node.module and self.current_layer:
            imported_layer = self._detect_layer(node.module)

            if imported_layer and self._is_layer_violation(
                self.current_layer, imported_layer
            ):
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Layer violation: {self.current_layer} layer importing from {imported_layer} layer",
                    code_snippet=f"from {node.module} import ...",
                )

        self.generic_visit(node)

    def _detect_layer(self, path: str) -> Optional[str]:
        """Detect which layer a module belongs to."""
        path_lower = path.lower()

        for layer, patterns in self.LAYER_PATTERNS.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return layer

        return None

    def _is_layer_violation(self, from_layer: str, to_layer: str) -> bool:
        """Check if import violates layer architecture."""
        # UI can import from business and data
        # Business can import from data
        # Data should not import from UI or business

        violations = {"data": ["ui", "business"], "business": ["ui"], "ui": []}

        return to_layer in violations.get(from_layer, [])


class CouplingVisitor(ast.NodeVisitor):
    """Detects high coupling between modules."""

    MAX_IMPORTS_PER_MODULE = 10
    MAX_EXTERNAL_CALLS = 15

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.imports_count = 0
        self.external_calls: Dict[str, int] = defaultdict(int)

    def visit_Import(self, node: ast.Import) -> None:
        """Count imports."""
        self.imports_count += len(node.names)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Count from imports."""
        if node.module:
            self.imports_count += 1
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Count external calls."""
        # Track module.function calls
        if isinstance(node.value, ast.Name):
            self.external_calls[node.value.id] += 1

        self.generic_visit(node)

    def finalize(self) -> None:
        """Check metrics after visiting."""
        # Check import count
        if self.imports_count > self.MAX_IMPORTS_PER_MODULE:
            self.result.add_failure(
                file_path=self.file_path,
                line=1,
                column=0,
                message=f"High coupling: Too many imports ({self.imports_count} > {self.MAX_IMPORTS_PER_MODULE})",
                code_snippet=f"{self.imports_count} imports",
            )

        # Check external calls
        total_external_calls = sum(self.external_calls.values())
        if total_external_calls > self.MAX_EXTERNAL_CALLS:
            most_called = max(self.external_calls.items(), key=lambda x: x[1])
            self.result.add_failure(
                file_path=self.file_path,
                line=1,
                column=0,
                message=f"High coupling: Too many external calls ({total_external_calls} > {self.MAX_EXTERNAL_CALLS})",
                code_snippet=f"Most called: {most_called[0]} ({most_called[1]} times)",
            )


class GodClassVisitor(ast.NodeVisitor):
    """Detects god classes (classes that do too much)."""

    MAX_METHODS = 20
    MAX_ATTRIBUTES = 15
    MAX_LINES = 300

    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check for god classes."""
        methods = []
        attributes = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)

        # Calculate class size
        if hasattr(node, "end_lineno") and node.end_lineno is not None and node.lineno is not None:
            class_lines = node.end_lineno - node.lineno
        else:
            class_lines = 0

        # Check metrics
        issues = []

        if len(methods) > self.MAX_METHODS:
            issues.append(f"too many methods ({len(methods)} > {self.MAX_METHODS})")

        if len(attributes) > self.MAX_ATTRIBUTES:
            issues.append(
                f"too many attributes ({len(attributes)} > {self.MAX_ATTRIBUTES})"
            )

        if class_lines > self.MAX_LINES:
            issues.append(f"too many lines ({class_lines} > {self.MAX_LINES})")

        if issues:
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"God class '{node.name}': {', '.join(issues)}",
                code_snippet=f"class {node.name}: # {len(methods)} methods, {len(attributes)} attributes",
            )

        self.generic_visit(node)
