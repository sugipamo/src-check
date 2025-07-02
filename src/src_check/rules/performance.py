"""
Performance checker implementation.
"""

import ast
from typing import Dict, List, Optional

from src_check.core.base import BaseChecker
from src_check.models import CheckResult, FailureLocation


class PerformanceChecker(BaseChecker):
    """Check for performance issues in Python code."""

    @property
    def name(self) -> str:
        return "performance"

    @property
    def description(self) -> str:
        return "Detect performance bottlenecks and inefficient code patterns"

    @property
    def category(self) -> str:
        return "performance"

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for performance issues in the code."""
        result = self.create_result()
        visitor = PerformanceVisitor(file_path)
        visitor.visit(ast_tree)

        for issue in visitor.issues:
            result.failure_locations.append(issue)

        return result if result.failure_locations else None


class PerformanceVisitor(ast.NodeVisitor):
    """AST visitor to detect performance issues."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues: List[FailureLocation] = []
        self.current_function: Optional[str] = None
        self.loop_depth = 0
        self.loop_invariants: Dict[int, List[ast.AST]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track current async function context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_For(self, node: ast.For) -> None:
        """Check for performance issues in loops."""
        self.loop_depth += 1

        # Check for loop invariants
        self._check_loop_invariants(node)

        # Check for string concatenation in loops
        self._check_string_concatenation_in_loop(node)

        # Check for repeated function calls in loop condition
        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
            and node.iter.args
            and isinstance(node.iter.args[0], ast.Call)
            and (
                (
                    isinstance(node.iter.args[0].func, ast.Name)
                    and node.iter.args[0].func.id == "len"
                    and node.iter.args[0].args
                    and isinstance(node.iter.args[0].args[0], ast.Call)
                )
                or not (
                    isinstance(node.iter.args[0].func, ast.Name)
                    and node.iter.args[0].func.id == "len"
                )
            )
        ):
                self.issues.append(
                    FailureLocation(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="[PERF001] Function call in loop range may be evaluated multiple times. Consider storing the result in a variable before the loop",
                    )
                )

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        """Check for performance issues in while loops."""
        self.loop_depth += 1

        # Check for function calls in while condition
        if isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Call):
            self.issues.append(
                FailureLocation(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="[PERF002] Function call in while condition is evaluated on each iteration. Consider caching the result if it doesn't change",
                )
            )

        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Check for inefficient augmented assignments in loops."""
        if (
            self.loop_depth > 0
            and isinstance(node.op, ast.Add)
            and (
                (
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "str"
                )
                or (
                    isinstance(node.value, (ast.Constant, ast.BinOp))
                    and self._is_string_type(node.value)
                )
            )
        ):
                self.issues.append(
                    FailureLocation(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="[PERF003] String concatenation in loop is inefficient. Use list.append() and ''.join() instead",
                    )
                )

        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Check for inefficient string concatenation."""
        if (
            self.loop_depth > 0
            and isinstance(node.op, ast.Add)
            and (self._is_string_type(node.left) or self._is_string_type(node.right))
        ):
            self.issues.append(
                FailureLocation(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="[PERF003] String concatenation in loop is inefficient. Use list.append() and ''.join() instead",
                )
            )

        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Check list comprehensions (usually good for performance)."""
        # List comprehensions are generally good, but check for nested ones
        nested_count = sum(
            1
            for n in ast.walk(node)
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp))
        )
        if nested_count > 2:
            self.issues.append(
                FailureLocation(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="[PERF004] Deeply nested comprehensions may hurt readability and performance. Consider breaking into multiple steps",
                )
            )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for performance issues in function calls."""
        # Check for repeated list() conversions
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "list"
            and node.args
            and isinstance(node.args[0], ast.Call)
        ):
            inner_call = node.args[0]
            if isinstance(inner_call.func, ast.Name) and inner_call.func.id in [
                "list",
                "tuple",
            ]:
                self.issues.append(
                    FailureLocation(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"[PERF005] Unnecessary type conversion: list({inner_call.func.id}(...)) is redundant",
                    )
                )

        # Check for global function calls in tight loops
        if (
            self.loop_depth > 0
            and isinstance(node.func, ast.Name)
            and node.func.id in ["len", "sum", "max", "min"]
            and self._is_loop_invariant(node)
        ):
            self.issues.append(
                FailureLocation(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"[PERF006] Loop-invariant call to {node.func.id}() could be moved outside the loop. Consider computing this value before the loop",
                )
            )

        self.generic_visit(node)

    def _check_loop_invariants(self, node: ast.For) -> None:
        """Check for computations that could be moved outside the loop."""
        # This is a simplified check - a full implementation would be more complex
        for stmt in node.body:
            if (
                isinstance(stmt, ast.Assign)
                and not self._uses_loop_variable(stmt.value, node.target)
                and isinstance(stmt.value, (ast.BinOp, ast.Call))
            ):
                        self.issues.append(
                            FailureLocation(
                                file_path=self.file_path,
                                line=stmt.lineno,
                                column=stmt.col_offset,
                                message="[PERF007] Loop-invariant computation could be moved outside the loop. This value doesn't change during loop iterations",
                            )
                        )

    def _check_string_concatenation_in_loop(self, node: ast.For) -> None:
        """Check for string concatenation patterns in loops."""
        for stmt in ast.walk(node):
            if (
                isinstance(stmt, ast.AugAssign) 
                and isinstance(stmt.op, ast.Add)
                and isinstance(stmt.target, ast.Name)
            ):
                    # This is a heuristic - we can't always know the type
                    # but we can check for common patterns
                    for parent_stmt in node.body:
                        if (
                            isinstance(parent_stmt, ast.Assign)
                            and any(
                                isinstance(t, ast.Name) and t.id == stmt.target.id
                                for t in parent_stmt.targets
                            )
                            and isinstance(parent_stmt.value, ast.Constant)
                            and isinstance(parent_stmt.value.value, str)
                        ):
                            self.issues.append(
                                FailureLocation(
                                    file_path=self.file_path,
                                    line=stmt.lineno,
                                    column=stmt.col_offset,
                                    message="[PERF008] String concatenation with += in loop is inefficient. Use list.append() and ''.join() for better performance",
                                )
                            )

    def _is_string_type(self, node: ast.AST) -> bool:
        """Heuristic to check if a node is likely a string."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "str":
                return True
        if isinstance(node, ast.JoinedStr):  # f-string
            return True
        return False

    def _uses_loop_variable(self, node: ast.AST, loop_var: ast.AST) -> bool:
        """Check if an expression uses the loop variable."""
        if isinstance(loop_var, ast.Name):
            loop_var_name = loop_var.id
        elif isinstance(loop_var, ast.Tuple):
            loop_var_names = [n.id for n in loop_var.elts if isinstance(n, ast.Name)]
        else:
            return False

        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                if (isinstance(loop_var, ast.Name) and child.id == loop_var_name) or (
                    isinstance(loop_var, ast.Tuple) and child.id in loop_var_names
                ):
                    return True

        return False

    def _is_loop_invariant(self, node: ast.Call) -> bool:
        """Simple check if a function call might be loop-invariant."""
        # This is a heuristic - check if all arguments are constants or
        # variables that don't appear to be modified in the loop
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                continue
            elif isinstance(arg, ast.Name):
                # In a real implementation, we'd track if this variable
                # is modified in the loop
                continue
            else:
                return False
        return True
