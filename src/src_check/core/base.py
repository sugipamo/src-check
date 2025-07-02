"""
Base class for all checkers.
"""

import ast
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src_check.models import CheckResult


class BaseChecker(ABC):
    """Abstract base class for all quality checkers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the checker."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the checker does."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Category of the checker (security, code_quality, architecture, test)."""
        pass
    
    @abstractmethod
    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """
        Perform the check on the given AST.
        
        Args:
            ast_tree: The parsed AST of the Python file
            file_path: Path to the file being checked
            
        Returns:
            CheckResult with findings, or None if no issues found
        """
        pass
    
    def is_excluded(self, file_path: str, exclude_patterns: list) -> bool:
        """
        Check if the file should be excluded from checking.
        
        Args:
            file_path: Path to check
            exclude_patterns: List of glob patterns to exclude
            
        Returns:
            True if file should be excluded
        """
        path = Path(file_path)
        for pattern in exclude_patterns:
            if path.match(pattern):
                return True
        return False
    
    def create_result(self, title: str = None) -> CheckResult:
        """
        Create a CheckResult with default values from the checker.
        
        Args:
            title: Optional custom title, defaults to checker description
            
        Returns:
            Empty CheckResult ready to be populated
        """
        return CheckResult(
            title=title or self.description,
            checker_name=self.name,
            category=self.category
        )