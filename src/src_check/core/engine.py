"""Analysis engine for running checkers on files and directories."""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from src_check.core.base import BaseChecker
from src_check.core.registry import registry
from src_check.models.check_result import CheckResult
from src_check.models.config import SrcCheckConfig

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """Engine for analyzing files and directories using multiple checkers."""

    def __init__(
        self,
        checkers: Union[List[str], List[BaseChecker]],
        config: Optional[SrcCheckConfig] = None,
    ):
        """Initialize the analysis engine.

        Args:
            checkers: List of checker names or checker instances to run
            config: Optional configuration object
        """
        self.checkers: List[BaseChecker] = []

        # Handle both string names and checker instances
        for checker in checkers:
            if isinstance(checker, str):
                # Get checker from registry
                checker_instance = registry.get_checker(checker)
                if checker_instance:
                    self.checkers.append(checker_instance)
                else:
                    logger.warning(f"Checker not found: {checker}")
            elif isinstance(checker, BaseChecker):
                self.checkers.append(checker)

        self.config = config or SrcCheckConfig()

    def analyze_file(self, file_path: Path) -> List[CheckResult]:
        """Analyze a single file with all checkers.

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of check results from all checkers
        """
        results: List[CheckResult] = []

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return results

        if not file_path.is_file():
            logger.warning(f"Not a file: {file_path}")
            return results

        # Parse the Python file
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            ast_tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return results

        # Run each checker
        for checker in self.checkers:
            try:
                # Try check_file method first (for mock compatibility)
                if hasattr(checker, "check_file"):
                    checker_result = checker.check_file(file_path)
                else:
                    checker_result = checker.check(ast_tree, str(file_path))

                if checker_result:
                    # Check if it's a single result or list
                    if isinstance(checker_result, list):
                        results.extend(checker_result)
                    else:
                        results.append(checker_result)
            except Exception as e:
                logger.error(
                    f"Error running {checker.name if hasattr(checker, 'name') else type(checker).__name__} on {file_path}: {e}"
                )

        return results

    def analyze_directory(
        self, dir_path: Path, recursive: bool = True
    ) -> Dict[str, List[CheckResult]]:
        """Analyze all Python files in a directory.

        Args:
            dir_path: Path to the directory to analyze
            recursive: Whether to analyze subdirectories

        Returns:
            Dictionary mapping file paths to their check results
        """
        results: Dict[str, List[CheckResult]] = {}

        if not dir_path.exists():
            logger.warning(f"Directory not found: {dir_path}")
            return results

        if not dir_path.is_dir():
            logger.warning(f"Not a directory: {dir_path}")
            return results

        # Find all Python files
        pattern = "**/*.py" if recursive else "*.py"
        python_files = list(dir_path.glob(pattern))

        # Apply exclusions from config
        excluded_files = self._get_excluded_files(python_files)
        files_to_check = [f for f in python_files if f not in excluded_files]

        logger.info(f"Found {len(files_to_check)} Python files to analyze")

        # Analyze each file
        for file_path in files_to_check:
            file_results = self.analyze_file(file_path)
            if file_results:
                results[str(file_path)] = file_results

        return results

    def _get_excluded_files(self, files: List[Path]) -> List[Path]:
        """Get list of files that should be excluded based on config.

        Args:
            files: List of all files

        Returns:
            List of files to exclude
        """
        excluded = []

        # Default exclusions
        default_exclude_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".env",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "dist",
            "build",
            "*.egg-info",
        ]

        for file in files:
            # Check if file matches any exclusion pattern
            file_str = str(file)
            for pattern in default_exclude_patterns:
                if pattern in file_str:
                    excluded.append(file)
                    break

        return excluded

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on exclusion patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored, False otherwise
        """
        # Default exclusions
        default_exclude_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            ".env",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            "dist",
            "build",
            ".egg-info",
            ".pyc",
            ".pyo",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in default_exclude_patterns)
