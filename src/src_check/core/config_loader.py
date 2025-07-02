"""Configuration loader for src-check."""

import json
import logging
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

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
        self.checkers = data.get("checkers", {})
        self.output_format = data.get("output_format", "text")
        self.fail_on_issues = data.get("fail_on_issues", True)
        self.severity_threshold = data.get("severity_threshold", "low")

    def get_checker_config(self, checker_name: str) -> Dict[str, Any]:
        """Get configuration for a specific checker.

        Args:
            checker_name: Name of the checker

        Returns:
            Checker configuration dictionary
        """
        return self.checkers.get(checker_name, {})  # type: ignore

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
        "checkers": {
            "SecurityChecker": {"enabled": True, "severity_threshold": "medium"},
            "CodeQualityChecker": {"enabled": True, "max_complexity": 10},
            "ArchitectureChecker": {"enabled": True},
            "TestQualityChecker": {"enabled": True, "min_coverage": 80},
        },
        "output_format": "text",
        "fail_on_issues": True,
        "severity_threshold": "low",
    }

    # Supported config file names
    CONFIG_FILENAMES: ClassVar[list[str]] = [
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
                # Merge checker configs
                merged_checkers = merged.get("checkers", {})
                if isinstance(merged_checkers, dict):
                    merged_checkers = merged_checkers.copy()
                    merged_checkers.update(value)
                    merged["checkers"] = merged_checkers
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
