"""
Security-related quality checkers.
"""

import ast
import re
from typing import Optional, Set

from src_check.core.base import BaseChecker
from src_check.models import CheckResult, Severity


class SecurityChecker(BaseChecker):
    """Checks for security vulnerabilities and bad practices."""
    
    @property
    def name(self) -> str:
        return "security"
    
    @property
    def description(self) -> str:
        return "Security vulnerability detection"
    
    @property
    def category(self) -> str:
        return "security"
    
    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for security issues in the AST."""
        result = self.create_result()
        
        # Use multiple visitors for different security checks
        visitors = [
            HardcodedSecretsVisitor(file_path, result),
            DangerousFunctionsVisitor(file_path, result),
            SQLInjectionVisitor(file_path, result),
            PickleUsageVisitor(file_path, result),
        ]
        
        for visitor in visitors:
            visitor.visit(ast_tree)
        
        # Set severity based on findings
        if result.failure_count > 0:
            # If any critical issues found, set to critical
            for failure in result.failure_locations:
                if "password" in failure.message.lower() or "secret" in failure.message.lower():
                    result.severity = Severity.CRITICAL
                    break
                elif "eval" in failure.message.lower() or "exec" in failure.message.lower():
                    result.severity = Severity.HIGH
                elif result.severity != Severity.HIGH:
                    result.severity = Severity.MEDIUM
            
            # Add fix policy
            result.fix_policy = (
                "Security issues should be addressed immediately:\n"
                "1. Never hardcode secrets - use environment variables or secure vaults\n"
                "2. Avoid dangerous functions like eval() and exec()\n"
                "3. Use parameterized queries to prevent SQL injection\n"
                "4. Avoid pickle for untrusted data - use JSON instead"
            )
            
            return result
        
        return None


class HardcodedSecretsVisitor(ast.NodeVisitor):
    """Detects hardcoded secrets and credentials."""
    
    SECRET_PATTERNS = [
        'password', 'passwd', 'pwd', 'secret', 'token',
        'api_key', 'apikey', 'access_key', 'private_key',
        'auth', 'credential', 'mysql_pwd', 'postgres_pwd'
    ]
    
    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Check assignments for hardcoded secrets."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                
                # Skip common metadata fields
                if target.id in ['__author__', '__email__', '__version__', '__license__']:
                    continue
                    
                # Check if variable name suggests a secret
                for pattern in self.SECRET_PATTERNS:
                    if pattern in var_name:
                        # Check if value is a string literal
                        if isinstance(node.value, (ast.Str, ast.Constant)):
                            value = node.value.s if isinstance(node.value, ast.Str) else node.value.value
                            if isinstance(value, str) and value and not value.startswith('${'):
                                self.result.add_failure(
                                    file_path=self.file_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message=f"Hardcoded secret found: {target.id}",
                                    code_snippet=f"{target.id} = '<hidden>'"
                                )
                        break
        
        self.generic_visit(node)
    
    def visit_Dict(self, node: ast.Dict) -> None:
        """Check dictionary literals for secrets."""
        for key, value in zip(node.keys, node.values):
            if isinstance(key, (ast.Str, ast.Constant)):
                key_str = key.s if isinstance(key, ast.Str) else key.value
                if isinstance(key_str, str):
                    key_lower = key_str.lower()
                    
                    for pattern in self.SECRET_PATTERNS:
                        if pattern in key_lower:
                            if isinstance(value, (ast.Str, ast.Constant)):
                                val = value.s if isinstance(value, ast.Str) else value.value
                                if isinstance(val, str) and val and not val.startswith('${'):
                                    self.result.add_failure(
                                        file_path=self.file_path,
                                        line=key.lineno,
                                        column=key.col_offset,
                                        message=f"Hardcoded secret in dictionary: {key_str}",
                                        code_snippet=f'"{key_str}": "<hidden>"'
                                    )
                            break
        
        self.generic_visit(node)


class DangerousFunctionsVisitor(ast.NodeVisitor):
    """Detects usage of dangerous functions."""
    
    DANGEROUS_FUNCTIONS = {
        'eval': 'Can execute arbitrary code',
        'exec': 'Can execute arbitrary code',
        'compile': 'Can compile and execute arbitrary code',
        '__import__': 'Dynamic imports can be dangerous',
        'input': 'In Python 2, input() evaluates the input',
        'os.system': 'Can execute shell commands',
        'subprocess.call': 'Prefer subprocess.run with shell=False',
        'subprocess.Popen': 'Ensure shell=False'
    }
    
    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for dangerous functions."""
        func_name = self._get_function_name(node.func)
        
        if func_name in self.DANGEROUS_FUNCTIONS:
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Dangerous function '{func_name}': {self.DANGEROUS_FUNCTIONS[func_name]}",
                code_snippet=ast.unparse(node) if hasattr(ast, 'unparse') else func_name
            )
        
        # Check for subprocess with shell=True
        if func_name in ['subprocess.call', 'subprocess.run', 'subprocess.Popen']:
            for keyword in node.keywords:
                if keyword.arg == 'shell' and self._is_true(keyword.value):
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Dangerous: {func_name} with shell=True",
                        code_snippet="shell=True"
                    )
        
        self.generic_visit(node)
    
    def _get_function_name(self, node) -> str:
        """Extract function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return ''
    
    def _is_true(self, node) -> bool:
        """Check if a node represents True."""
        if isinstance(node, ast.Constant):
            return node.value is True
        elif isinstance(node, ast.NameConstant):
            return node.value is True
        return False


class SQLInjectionVisitor(ast.NodeVisitor):
    """Detects potential SQL injection vulnerabilities."""
    
    SQL_PATTERNS = [
        r'SELECT.*FROM',
        r'INSERT.*INTO',
        r'UPDATE.*SET',
        r'DELETE.*FROM',
        r'DROP.*TABLE',
        r'CREATE.*TABLE'
    ]
    
    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.sql_re = re.compile('|'.join(self.SQL_PATTERNS), re.IGNORECASE)
    
    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Check string concatenation/formatting for SQL."""
        if isinstance(node.op, (ast.Add, ast.Mod)):
            # Check if left side contains SQL
            left_str = self._extract_string(node.left)
            if left_str and self.sql_re.search(left_str):
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message="Potential SQL injection: String concatenation with SQL",
                    code_snippet="SQL + user_input"
                )
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check string format calls with SQL."""
        func_name = self._get_function_name(node.func)
        
        if func_name in ['str.format', 'format'] or func_name.endswith('.format'):
            # Check if any argument contains SQL
            for arg in node.args:
                sql_str = self._extract_string(arg)
                if sql_str and self.sql_re.search(sql_str):
                    self.result.add_failure(
                        file_path=self.file_path,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Potential SQL injection: format() with SQL",
                        code_snippet="sql.format(user_input)"
                    )
                    break
        
        self.generic_visit(node)
    
    def _extract_string(self, node) -> Optional[str]:
        """Extract string value from AST node."""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None
    
    def _get_function_name(self, node) -> str:
        """Extract function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{node.value.__class__.__name__}.{node.attr}"
        return ''


class PickleUsageVisitor(ast.NodeVisitor):
    """Detects usage of pickle module."""
    
    def __init__(self, file_path: str, result: CheckResult):
        self.file_path = file_path
        self.result = result
        self.has_pickle_import = False
    
    def visit_Import(self, node: ast.Import) -> None:
        """Check for pickle imports."""
        for alias in node.names:
            if alias.name in ['pickle', 'cPickle']:
                self.has_pickle_import = True
                self.result.add_failure(
                    file_path=self.file_path,
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Security risk: {alias.name} can execute arbitrary code during deserialization",
                    code_snippet=f"import {alias.name}"
                )
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for pickle imports."""
        if node.module in ['pickle', 'cPickle']:
            self.has_pickle_import = True
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message=f"Security risk: {node.module} can execute arbitrary code during deserialization",
                code_snippet=f"from {node.module} import ..."
            )
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Check for pickle.loads() calls."""
        func_name = self._get_function_name(node.func)
        
        if self.has_pickle_import and func_name in ['pickle.loads', 'pickle.load', 
                                                     'cPickle.loads', 'cPickle.load']:
            self.result.add_failure(
                file_path=self.file_path,
                line=node.lineno,
                column=node.col_offset,
                message="Critical: Unpickling untrusted data can execute arbitrary code",
                code_snippet=func_name
            )
        
        self.generic_visit(node)
    
    def _get_function_name(self, node) -> str:
        """Extract function name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
        return ''