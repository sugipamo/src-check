"""Configuration loader for src-check."""

import json
import logging
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, cast

import yaml

# Remove unused import

logger = logging.getLogger(__name__)


class SrcCheckConfig:
    """Configuration for src-check."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize configuration from dictionary.

        Args:
            data: Configuration data
        """
        self.version = data.get("version", "1.0")
        self.exclude = data.get("exclude", [])
        self.include = data.get("include", ["**/*.py"])
        # Handle both dict and list formats for checkers
        checkers_data = data.get("checkers", {})
        if isinstance(checkers_data, list):
            self.checkers = checkers_data
        else:
            # If dict, extract enabled checkers
            self.checkers = [
                name
                for name, config in checkers_data.items()
                if config.get("enabled", True)
            ]
        self._checkers_config = checkers_data if isinstance(checkers_data, dict) else {}
        self.output_format = data.get("output_format", "text")
        self.fail_on_issues = data.get("fail_on_issues", True)
        self.severity_threshold = data.get("severity_threshold", "low")

        # Additional attributes expected by tests
        self.file_patterns = data.get("file_patterns", ["*.py"])
        self.ignore_patterns = data.get("ignore_patterns", self.exclude)
        self.max_file_size = data.get("max_file_size", 1048576)  # 1MB default
        self.parallel = data.get("parallel", False)
        self.cache_enabled = data.get("cache_enabled", False)

    def get_checker_config(self, checker_name: str) -> Dict[str, Any]:
        """Get configuration for a specific checker.

        Args:
            checker_name: Name of the checker

        Returns:
            Checker configuration dictionary
        """
        result = self._checkers_config.get(checker_name, {})
        return cast(Dict[str, Any], result)

    def is_checker_enabled(self, checker_name: str) -> bool:
        """Check if a checker is enabled.

        Args:
            checker_name: Name of the checker

        Returns:
            True if enabled, False otherwise
        """
        checker_config = self.get_checker_config(checker_name)
        return bool(checker_config.get("enabled", True))


class ConfigLoader:
    """Loader for src-check configuration files."""

    # Default configuration
    DEFAULT_CONFIG: ClassVar[Dict[str, Any]] = {
        "version": "1.0",
        "exclude": [
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/.venv/**",
            "**/venv/**",
            "**/env/**",
            "**/.env/**",
            "**/.mypy_cache/**",
            "**/.pytest_cache/**",
            "**/.tox/**",
            "**/dist/**",
            "**/build/**",
            "**/*.egg-info/**",
        ],
        "include": ["**/*.py"],
        "ignore_patterns": [
            "__pycache__",
            "*.pyc",
            ".git",
            ".venv",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
            ".eggs",
            "*.egg-info",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".coverage",
            "htmlcov",
            ".tox",
        ],
        "file_patterns": ["*.py"],
        "checkers": [
            "SecurityChecker",
            "CodeQualityChecker",
            "ArchitectureChecker",
            "TestQualityChecker",
            "DocumentationChecker",
            "TypeHintChecker",
            "PerformanceChecker",
            "DependencyChecker",
            "LicenseChecker",
            "DeprecationChecker",
        ],
        "output_format": "text",
        "fail_on_issues": False,
        "severity_threshold": "low",
        "max_file_size": 1048576,
        "parallel": False,
        "cache_enabled": False,
    }

    # Supported config file names
    CONFIG_FILENAMES: ClassVar[List[str]] = [
        ".src-check.yaml",
        ".src-check.yml",
        ".src-check.json",
        "src-check.yaml",
        "src-check.yml",
        "src-check.json",
        "pyproject.toml",  # Support for pyproject.toml
    ]

    def load_from_file(self, path: Path) -> SrcCheckConfig:
        """Load configuration from a file.

        Args:
            path: Path to the configuration file

        Returns:
            Configuration object

        Raises:
            ValueError: If file format is not supported
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        # Determine file type and load
        if path.suffix in [".yaml", ".yml"]:
            config_data = self._load_yaml(path)
        elif path.suffix == ".json":
            config_data = self._load_json(path)
        elif path.name == "pyproject.toml":
            config_data = self._load_pyproject_toml(path)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")

        # Merge with defaults
        merged_config = self._merge_with_defaults(config_data)

        return SrcCheckConfig(merged_config)

    def find_config_file(self, start_path: Path) -> Optional[Path]:
        """Find configuration file starting from a path and going up.

        Args:
            start_path: Path to start searching from

        Returns:
            Path to configuration file if found, None otherwise
        """
        current = start_path.resolve()

        # If it's a file, start from its parent
        if current.is_file():
            current = current.parent

        # Search up the directory tree
        while current != current.parent:
            for filename in self.CONFIG_FILENAMES:
                config_path = current / filename
                if config_path.exists():
                    logger.info(f"Found configuration file: {config_path}")
                    return config_path

            current = current.parent

        return None

    def load_default_config(self) -> SrcCheckConfig:
        """Load default configuration.

        Returns:
            Default configuration object
        """
        return SrcCheckConfig(self.DEFAULT_CONFIG.copy())

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        with open(path) as f:
            data: Dict[str, Any] = json.load(f)
            return data

    def _load_pyproject_toml(self, path: Path) -> Dict[str, Any]:
        """Load configuration from pyproject.toml."""
        try:
            import toml
        except ImportError:
            logger.warning("toml package not installed, cannot read pyproject.toml")
            return {}

        with open(path) as f:
            data = toml.load(f)

        # Extract src-check configuration
        tool_config = data.get("tool", {})
        src_check_config: Dict[str, Any] = tool_config.get("src-check", {})
        return src_check_config

    def _merge_with_defaults(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults.

        Args:
            config_data: User configuration data

        Returns:
            Merged configuration
        """
        # Start with defaults
        merged = self.DEFAULT_CONFIG.copy()

        # Update with user config
        for key, value in config_data.items():
            if key == "checkers" and isinstance(value, dict):
                # If user provides dict format, replace the default list format
                merged["checkers"] = value
            elif key == "exclude" and isinstance(value, list):
                # Extend exclude list
                existing_exclude = merged.get("exclude")
                if isinstance(existing_exclude, list):
                    existing_exclude.extend(value)
                else:
                    merged["exclude"] = value
            else:
                merged[key] = value

        return merged

    def load(self, config_path: Optional[str] = None) -> SrcCheckConfig:
        """Load configuration from file or defaults.

        Args:
            config_path: Optional path to configuration file

        Returns:
            Configuration object
        """
        if config_path:
            return self.load_from_file(Path(config_path))

        # Try to find config file in current directory
        config_file = self.find_config_file(Path.cwd())
        if config_file:
            return self.load_from_file(config_file)

        # Return default config
        return self.load_default_config()
