"""Context awareness module for src-check.

This module provides functionality to identify file types and contexts,
allowing for appropriate rule application based on file purpose.
"""

from enum import Enum, auto
from typing import Set


class FileType(Enum):
    """Enumeration of file types for context-aware checking."""
    
    PRODUCTION = auto()  # Production code
    EXAMPLE = auto()     # Example/demo code
    TEST = auto()        # Test code
    CONFIG = auto()      # Configuration files
    DOCUMENTATION = auto()  # Documentation files
    GENERATED = auto()   # Generated code
    VENDOR = auto()      # Third-party/vendor code


# Common patterns for identifying file types
EXAMPLE_PATTERNS: Set[str] = {
    "example", "examples", 
    "demo", "demos",
    "sample", "samples",
    "tutorial", "tutorials",
    "snippet", "snippets",
    "playground",
    "sandbox",
}

TEST_PATTERNS: Set[str] = {
    "test", "tests",
    "spec", "specs", 
    "__pycache__",
    "pytest_cache",
    ".pytest_cache",
}

CONFIG_PATTERNS: Set[str] = {
    "config", "configs",
    "conf",
    "settings",
    ".github",
    ".vscode",
}

GENERATED_PATTERNS: Set[str] = {
    "generated",
    "gen",
    "build",
    "dist",
    "__pycache__",
    ".egg-info",
    "node_modules",
}

VENDOR_PATTERNS: Set[str] = {
    "vendor",
    "vendors", 
    "third_party",
    "third-party",
    "external",
    "libs",  # Changed from "lib" to "libs" to avoid false positives
    "dependencies",
}


__all__ = [
    "FileType",
    "EXAMPLE_PATTERNS",
    "TEST_PATTERNS", 
    "CONFIG_PATTERNS",
    "GENERATED_PATTERNS",
    "VENDOR_PATTERNS",
]