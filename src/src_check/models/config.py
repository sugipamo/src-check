"""
Configuration models for src-check.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml


@dataclass
class RuleConfig:
    """Configuration for a single rule/checker."""

    name: str
    enabled: bool = True
    severity_override: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleConfig":
        """Create RuleConfig from dictionary."""
        return cls(
            name=data.get("name", ""),
            enabled=data.get("enabled", True),
            severity_override=data.get("severity_override"),
            options=data.get("options", {}),
        )


@dataclass
class OutputConfig:
    """Configuration for output settings."""

    format: str = "text"  # text, json, markdown
    file: Optional[str] = None
    verbose: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OutputConfig":
        """Create OutputConfig from dictionary."""
        return cls(
            format=data.get("format", "text"),
            file=data.get("file"),
            verbose=data.get("verbose", False),
        )


@dataclass
class SrcCheckConfig:
    """Main configuration for src-check."""

    # Base configuration
    base_score: float = 100.0

    # Category weights for KPI scoring
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "code_quality": 0.25,
            "architecture_quality": 0.25,
            "test_quality": 0.25,
            "security_quality": 0.25,
        }
    )

    # Severity impacts on score
    severity_impacts: Dict[str, float] = field(
        default_factory=lambda: {
            "critical": -10.0,
            "high": -5.0,
            "medium": -3.0,
            "low": -1.0,
            "info": -0.5,
        }
    )

    # Rules configuration
    rules: List[RuleConfig] = field(default_factory=list)

    # Output configuration
    output: OutputConfig = field(default_factory=OutputConfig)

    # Exclusion patterns
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "**/__pycache__/**",
            "**/venv/**",
            "**/.venv/**",
            "**/.git/**",
            "**/node_modules/**",
            "**/.tox/**",
            "**/*.pyc",
            "**/*.pyo",
        ]
    )

    # File size limits
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # Performance settings
    parallel: bool = True
    max_workers: Optional[int] = None

    # Cache settings
    use_cache: bool = True
    cache_dir: str = ".src-check-cache"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SrcCheckConfig":
        """Create configuration from dictionary."""
        config = cls()

        # Base settings
        config.base_score = data.get("base_score", 100.0)

        # Weights
        if "weights" in data:
            config.weights.update(data["weights"])

        # Severity impacts
        if "severity_impacts" in data:
            config.severity_impacts.update(data["severity_impacts"])

        # Rules
        if "rules" in data:
            config.rules = [RuleConfig.from_dict(rule) for rule in data["rules"]]

        # Output
        if "output" in data:
            config.output = OutputConfig.from_dict(data["output"])

        # Exclusions
        if "exclude_patterns" in data:
            config.exclude_patterns = data["exclude_patterns"]

        # Limits
        config.max_file_size = data.get("max_file_size", config.max_file_size)

        # Performance
        config.parallel = data.get("parallel", True)
        config.max_workers = data.get("max_workers")

        # Cache
        config.use_cache = data.get("use_cache", True)
        config.cache_dir = data.get("cache_dir", ".src-check-cache")

        return config

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "SrcCheckConfig":
        """Load configuration from YAML file."""
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def load(cls, config_path: Optional[Union[str, Path]] = None) -> "SrcCheckConfig":
        """Load configuration with fallback strategy."""
        # If specific path provided, use it
        if config_path:
            if Path(config_path).exists():
                return cls.from_yaml(config_path)
            else:
                raise FileNotFoundError(f"Config file not found: {config_path}")

        # Search for config files in order
        search_paths = [
            Path.cwd() / ".src-check.yaml",
            Path.cwd() / ".src-check.yml",
            Path.cwd() / "src-check.yaml",
            Path.cwd() / "src-check.yml",
            Path.home() / ".src-check.yaml",
            Path.home() / ".config" / "src-check" / "config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return cls.from_yaml(path)

        # Return default config if no file found
        return cls()

    def get_enabled_rules(self) -> List[str]:
        """Get list of enabled rule names."""
        return [rule.name for rule in self.rules if rule.enabled]

    def get_rule_config(self, rule_name: str) -> Optional[RuleConfig]:
        """Get configuration for a specific rule."""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "base_score": self.base_score,
            "weights": self.weights,
            "severity_impacts": self.severity_impacts,
            "rules": [
                {
                    "name": rule.name,
                    "enabled": rule.enabled,
                    "severity_override": rule.severity_override,
                    "options": rule.options,
                }
                for rule in self.rules
            ],
            "output": {
                "format": self.output.format,
                "file": self.output.file,
                "verbose": self.output.verbose,
            },
            "exclude_patterns": self.exclude_patterns,
            "max_file_size": self.max_file_size,
            "parallel": self.parallel,
            "max_workers": self.max_workers,
            "use_cache": self.use_cache,
            "cache_dir": self.cache_dir,
        }

    def save(self, path: Union[str, Path]) -> None:
        """Save configuration to YAML file."""
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
