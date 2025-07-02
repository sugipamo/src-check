#!/usr/bin/env python3
"""
Main CLI entry point for src-check.

Provides the primary command-line interface for code quality analysis
and KPI scoring.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from src_check.core.config_loader import ConfigLoader
from src_check.core.engine import AnalysisEngine
from src_check.core.kpi_calculator import KPICalculator
from src_check.core.registry import registry
from src_check.formatters.json import JsonFormatter
from src_check.formatters.markdown import MarkdownFormatter
from src_check.formatters.text import TextFormatter


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="src-check - Python code quality analysis with KPI scoring",
        prog="src-check",
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to analyze (default: current directory)",
        default=["."],
    )

    parser.add_argument(
        "--config", "-c", type=str, help="Path to configuration file (.yaml/.json)"
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument("--output", "-o", type=str, help="Output file path")

    parser.add_argument(
        "--threshold", type=float, help="Quality threshold (0-100) for exit code"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument("--kpi-only", action="store_true", help="Run KPI scoring only")

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    return parser.parse_args()


def validate_paths(paths: List[str]) -> List[Path]:
    """Validate and convert string paths to Path objects."""
    validated_paths = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Error: Path '{path}' does not exist", file=sys.stderr)
            sys.exit(3)
        validated_paths.append(path)
    return validated_paths


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def get_formatter(format_type: str):
    """Get the appropriate formatter based on format type."""
    formatters = {
        "text": TextFormatter(),
        "json": JsonFormatter(),
        "markdown": MarkdownFormatter(),
    }
    return formatters.get(format_type, TextFormatter())


def main() -> None:
    """Main entry point for src-check CLI."""
    try:
        args = parse_args()

        # Setup logging
        setup_logging(args.verbose)

        # Validate paths
        paths = validate_paths(args.paths)

        if args.verbose:
            print("src-check v1.0.0")
            print(f"Analyzing paths: {[str(p) for p in paths]}")
            if args.config:
                print(f"Using config: {args.config}")

        # Load configuration
        config_loader = ConfigLoader()
        if args.config:
            config_path = Path(args.config)
            config = config_loader.load_from_file(config_path)
        else:
            # Try to find config file
            config_path = config_loader.find_config_file(Path.cwd())
            if config_path:
                config = config_loader.load_from_file(config_path)
            else:
                config = config_loader.load_default_config()

        # Discover and register plugins
        print("🔍 Starting code quality analysis...")
        registry.discover_plugins()

        # Get enabled checkers
        checkers = []
        for checker in registry.get_all_checkers():
            if config.is_checker_enabled(checker.__class__.__name__):
                checkers.append(checker)

        if args.verbose:
            print(f"📋 Enabled checkers: {[c.name for c in checkers]}")

        # Create analysis engine
        engine = AnalysisEngine(checkers)

        # Analyze paths
        all_results = {}
        for path in paths:
            print(f"📂 Analyzing {path}...")
            if path.is_file():
                results = engine.analyze_file(path)
                if results:
                    all_results[str(path)] = results
            else:
                results = engine.analyze_directory(path)
                all_results.update(results)

        # Calculate KPI score
        calculator = KPICalculator()
        kpi_score = calculator.calculate_project_score(all_results)

        # Format and output results
        formatter = get_formatter(args.format)
        output = formatter.format(all_results, kpi_score)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"✅ Results written to {args.output}")
        else:
            print(output)

        # Exit with appropriate code
        if args.threshold and kpi_score.overall_score < args.threshold:
            print(
                f"\n❌ Quality score {kpi_score.overall_score:.1f} below threshold ({args.threshold})"
            )
            sys.exit(1)

        # Exit with error if critical issues and fail_on_issues is true
        if config.fail_on_issues and kpi_score.critical_issues > 0:
            print(f"\n❌ Found {kpi_score.critical_issues} critical issues")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
