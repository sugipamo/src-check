"""File context analyzer for src-check.

This module provides the FileContextAnalyzer class that determines the type
and context of files to enable appropriate rule application.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from src_check.context import (
    CONFIG_PATTERNS,
    EXAMPLE_PATTERNS,
    GENERATED_PATTERNS,
    TEST_PATTERNS,
    VENDOR_PATTERNS,
    FileType,
)
from src_check.models.config import SrcCheckConfig


class FileContextAnalyzer:
    """Analyzes file context to determine appropriate rule application."""

    def __init__(self, config: Optional[SrcCheckConfig] = None):
        """Initialize the file context analyzer.

        Args:
            config: Configuration object with custom patterns and rules
        """
        self.config = config or SrcCheckConfig()
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[FileType, List[re.Pattern]]:
        """Compile regex patterns for efficient matching.

        Returns:
            Dictionary mapping file types to compiled regex patterns
        """
        patterns = {}

        # Get custom patterns from config if available
        custom_patterns = getattr(self.config, "file_context", {})

        # Compile example patterns
        example_pats = EXAMPLE_PATTERNS.copy()
        if "example_patterns" in custom_patterns:
            example_pats.update(custom_patterns["example_patterns"])
        patterns[FileType.EXAMPLE] = [
            re.compile(rf"(?:^|/)(?:{pat})(?:/|$)", re.IGNORECASE)
            for pat in example_pats
        ]

        # Compile test patterns
        test_pats = TEST_PATTERNS.copy()
        if "test_patterns" in custom_patterns:
            test_pats.update(custom_patterns["test_patterns"])
        patterns[FileType.TEST] = [
            re.compile(rf"(?:^|/)(?:{pat})(?:/|$)", re.IGNORECASE) for pat in test_pats
        ]
        # Also match files starting with test_
        patterns[FileType.TEST].append(
            re.compile(r"(?:^|/)test_[^/]+\.py$", re.IGNORECASE)
        )

        # Compile config patterns
        patterns[FileType.CONFIG] = [
            re.compile(rf"(?:^|/)(?:{pat})(?:/|$)", re.IGNORECASE)
            for pat in CONFIG_PATTERNS
        ]

        # Compile generated patterns
        patterns[FileType.GENERATED] = [
            re.compile(rf"(?:^|/)(?:{pat})(?:/|$)", re.IGNORECASE)
            for pat in GENERATED_PATTERNS
        ]

        # Compile vendor patterns
        patterns[FileType.VENDOR] = [
            re.compile(rf"(?:^|/)(?:{pat})(?:/|$)", re.IGNORECASE)
            for pat in VENDOR_PATTERNS
        ]

        return patterns

    def classify_file(self, file_path: Union[str, Path]) -> FileType:
        """Classify a file based on its path and context.

        Args:
            file_path: Path to the file to classify

        Returns:
            FileType enum indicating the file's classification
        """
        path = Path(file_path)
        path_str = str(path)

        # Check for generated code first (highest priority)
        if self._matches_patterns(path_str, FileType.GENERATED):
            return FileType.GENERATED

        # Check for vendor/third-party code
        if self._matches_patterns(path_str, FileType.VENDOR):
            return FileType.VENDOR

        # Check for test code
        if self._matches_patterns(path_str, FileType.TEST):
            return FileType.TEST

        # Check for example/demo code
        if self._matches_patterns(path_str, FileType.EXAMPLE):
            return FileType.EXAMPLE

        # Check for config files
        if self._is_config_file(path):
            return FileType.CONFIG

        # Check for documentation
        if self._is_documentation_file(path):
            return FileType.DOCUMENTATION

        # Default to production code
        return FileType.PRODUCTION

    def _matches_patterns(self, path_str: str, file_type: FileType) -> bool:
        """Check if a path matches any pattern for a given file type.

        Args:
            path_str: String representation of the file path
            file_type: The file type to check patterns for

        Returns:
            True if the path matches any pattern
        """
        if file_type not in self._compiled_patterns:
            return False

        return any(
            pattern.search(path_str) for pattern in self._compiled_patterns[file_type]
        )

    def _is_config_file(self, path: Path) -> bool:
        """Check if a file is a configuration file.

        Args:
            path: Path object to check

        Returns:
            True if the file is a configuration file
        """
        config_extensions = {
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".json",
            ".xml",
            ".env",
            ".properties",
        }

        config_names = {
            "setup.py",
            "setup.cfg",
            "pyproject.toml",
            "requirements.txt",
            "requirements.in",
            "Pipfile",
            "Pipfile.lock",
            "poetry.lock",
            "Makefile",
            "Dockerfile",
            ".gitignore",
            ".dockerignore",
            ".editorconfig",
        }

        # Check if filename starts with config or settings
        if path.stem.lower() in ["config", "settings"]:
            return True

        return (
            path.suffix.lower() in config_extensions
            or path.name in config_names
            or self._matches_patterns(str(path), FileType.CONFIG)
        )

    def _is_documentation_file(self, path: Path) -> bool:
        """Check if a file is documentation.

        Args:
            path: Path object to check

        Returns:
            True if the file is documentation
        """
        doc_extensions = {".md", ".rst", ".txt", ".adoc", ".org"}
        doc_patterns = {"readme", "changelog", "contributing", "license"}

        return path.suffix.lower() in doc_extensions or any(
            pat in path.name.lower() for pat in doc_patterns
        )

    def get_severity_multiplier(self, file_type: FileType) -> float:
        """Get severity multiplier for a given file type.

        Args:
            file_type: The type of file

        Returns:
            Multiplier to apply to issue severity (0.0 to 1.0)
        """
        severity_map = {
            FileType.PRODUCTION: 1.0,
            FileType.TEST: 0.7,
            FileType.EXAMPLE: 0.3,
            FileType.CONFIG: 0.8,
            FileType.DOCUMENTATION: 0.2,
            FileType.GENERATED: 0.0,  # Ignore generated files
            FileType.VENDOR: 0.0,  # Ignore vendor files
        }

        # Check for custom severity settings in config
        if hasattr(self.config, "context_severity"):
            custom_severity = self.config.context_severity.get(file_type.name)
            if custom_severity is not None:
                return float(custom_severity)

        return float(severity_map.get(file_type, 1.0))

    def should_check_file(self, file_path: Union[str, Path]) -> bool:
        """Determine if a file should be checked.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be checked
        """
        file_type = self.classify_file(file_path)

        # Never check generated or vendor files
        if file_type in (FileType.GENERATED, FileType.VENDOR):
            return False

        # Check custom exclusions from config
        if hasattr(self.config, "exclude_file_types"):
            if file_type.name in self.config.exclude_file_types:
                return False

        return True

    def get_context_rules(self, file_type: FileType) -> Dict[str, dict]:
        """Get context-specific rules for a file type.

        Args:
            file_type: The type of file

        Returns:
            Dictionary of rule adjustments for the file type
        """
        # Default rule adjustments by file type
        default_rules = {
            FileType.EXAMPLE: {
                "print_statements": {"enabled": True, "severity": "warning"},
                "hardcoded_values": {"enabled": True, "severity": "info"},
                "complexity": {"threshold_multiplier": 2.0},
                "coupling": {"threshold_multiplier": 2.0},
            },
            FileType.TEST: {
                "print_statements": {"enabled": False},
                "hardcoded_values": {"enabled": False},
                "test_quality": {"enabled": True, "strict": True},
            },
            FileType.CONFIG: {
                "type_hints": {"enabled": False},
                "docstrings": {"enabled": False},
                "complexity": {"enabled": False},
            },
            FileType.DOCUMENTATION: {
                # Most rules disabled for docs
                "all": {"enabled": False},
            },
        }

        rules: Dict[str, dict] = dict(default_rules.get(file_type, {}))

        # Merge with custom rules from config
        if hasattr(self.config, "context_rules"):
            custom_rules = self.config.context_rules.get(file_type.name, {})
            if isinstance(custom_rules, dict):
                rules.update(custom_rules)

        return rules
