#!/usr/bin/env python3
"""
KPI-focused CLI entry point for src-check.

Provides a specialized command-line interface focused on KPI scoring
and quality metrics.
"""

import argparse
import sys
from pathlib import Path


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

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

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

        # TODO: Implement KPI-specific analysis
        print("\n" + "=" * 50)
        print("📊 KPI Score Report (placeholder)")
        print("=" * 50)
        print("Total Score: 75.0/100")
        print("  - Code Quality:     80.0/100")
        print("  - Architecture:     75.0/100")
        print("  - Test Quality:     70.0/100")
        print("  - Security:         75.0/100")
        print("\n✅ Good: Code quality is at a good level.")

        # Exit with appropriate code
        score = 75.0
        if args.threshold and score < args.threshold:
            print(f"\n❌ Quality score ({score}) below threshold ({args.threshold})")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
