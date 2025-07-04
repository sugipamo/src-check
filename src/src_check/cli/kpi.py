#!/usr/bin/env python3
"""
KPI-focused CLI entry point for src-check.

Provides a specialized command-line interface focused on KPI scoring
and quality metrics.
"""

import argparse
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for KPI mode."""
    parser = argparse.ArgumentParser(
        description="src-check KPI - Focused code quality scoring", prog="src-check-kpi"
    )

    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to analyze (default: current directory)",
        default=["."],
    )

    parser.add_argument(
        "--config", "-c", type=str, help="Path to KPI configuration file"
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
        "--categories",
        nargs="+",
        choices=["code", "architecture", "test", "security"],
        help="Specific categories to analyze",
    )

    parser.add_argument(
        "--history", action="store_true", help="Show historical KPI trends"
    )

    parser.add_argument(
        "--checkers",
        nargs="+",
        help="Specific checkers to use",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")

    return parser.parse_args()


def main() -> None:
    """Main entry point for KPI-focused analysis."""
    try:
        args = parse_args()

        # Validate paths
        paths = []
        for path_str in args.paths:
            path = Path(path_str)
            if not path.exists():
                print(f"Error: Path '{path}' does not exist", file=sys.stderr)
                sys.exit(3)
            paths.append(path)

        print("📊 KPI Analysis Mode")
        print(f"📂 Analyzing {len(paths)} path(s)")

        if args.categories:
            print(f"🎯 Focus categories: {', '.join(args.categories)}")

        if args.history:
            print("📈 Historical analysis enabled")

        # Import here to avoid circular imports
        from src_check.core.config_loader import ConfigLoader
        from src_check.core.engine import AnalysisEngine
        from src_check.core.kpi_calculator import KPICalculator
        from src_check.core.registry import PluginRegistry as CheckerRegistry
        from src_check.formatters.json import JsonFormatter
        from src_check.formatters.markdown import MarkdownFormatter
        from src_check.formatters.text import TextFormatter

        def get_formatter(format_type: str) -> Any:
            """Get the appropriate formatter based on format type."""
            formatters = {
                "text": TextFormatter(),
                "json": JsonFormatter(),
                "markdown": MarkdownFormatter(),
            }
            return formatters.get(format_type, TextFormatter())

        # Load configuration
        config_loader = ConfigLoader()
        config = config_loader.load(args.config)

        # Get enabled checkers
        registry = CheckerRegistry()
        checkers = []

        # Filter by categories if specified
        for checker in registry.get_all_checkers():
            checker_name = checker.__class__.__name__
            if config.is_checker_enabled(checker_name):
                # Filter by categories if specified
                if args.categories:
                    # Map checker to categories
                    category_map = {
                        "SecurityChecker": "security",
                        "CodeQualityChecker": "code",
                        "ArchitectureChecker": "architecture",
                        "TestQualityChecker": "test",
                        "TypeHintChecker": "code",
                        "PerformanceChecker": "code",
                        "DependencyChecker": "architecture",
                        "DocumentationChecker": "code",
                        "LicenseChecker": "security",
                        "DeprecationChecker": "code",
                    }
                    checker_category = category_map.get(checker_name, "code")
                    if checker_category in args.categories:
                        checkers.append(checker)
                else:
                    checkers.append(checker)

        if args.verbose:
            print(f"📋 Enabled checkers: {[c.name for c in checkers]}")

        # Create analysis engine
        engine = AnalysisEngine(checkers)

        # Analyze paths
        all_results = {}
        for path in paths:
            if args.verbose:
                print(f"🔍 Analyzing {path}...")
            if path.is_file():
                file_results = engine.analyze_file(path)
                if file_results:
                    all_results[str(path)] = file_results
            else:
                dir_results = engine.analyze_directory(path)
                all_results.update(dir_results)

        # Calculate KPI score
        calculator = KPICalculator()
        kpi_score = calculator.calculate_project_score(all_results)

        # Format and output results
        formatter = get_formatter(args.format)
        output = formatter.format_kpi_report(kpi_score, all_results)

        # Output results
        if args.output:
            Path(args.output).write_text(output)
            print(f"✅ Report saved to {args.output}")
        else:
            print(output)

        # Exit with appropriate code
        score = getattr(
            kpi_score, "total_score", getattr(kpi_score, "overall_score", 0.0)
        )
        if args.threshold and score < args.threshold:
            print(
                f"\n❌ Quality score ({score:.1f}) below threshold ({args.threshold})"
            )
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
