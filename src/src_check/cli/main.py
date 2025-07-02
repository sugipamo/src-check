#!/usr/bin/env python3
"""
Main CLI entry point for src-check.

Provides the primary command-line interface for code quality analysis
and KPI scoring.
"""

import argparse
import sys
from pathlib import Path
from typing import List


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


def main() -> None:
    """Main entry point for src-check CLI."""
    try:
        args = parse_args()

        # Validate paths
        paths = validate_paths(args.paths)

        if args.verbose:
            print("src-check v1.0.0")
            print(f"Analyzing paths: {[str(p) for p in paths]}")
            if args.config:
                print(f"Using config: {args.config}")

        # TODO: Implement actual analysis logic
        print("🔍 Starting code quality analysis...")
        print(f"📂 Analyzing {len(paths)} path(s)")

        if args.kpi_only:
            print("📊 KPI-only mode enabled")

        # Placeholder for now
        print("✅ Analysis complete! (placeholder)")
        print("📊 KPI Score: 75.0/100 (placeholder)")

        # Exit with appropriate code
        if args.threshold and 75.0 < args.threshold:
            print(f"❌ Quality score below threshold ({args.threshold})")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
