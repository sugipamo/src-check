#!/usr/bin/env python3
"""src-check performance profiling script."""

import argparse
import cProfile
import pstats
import sys
from typing import Optional

from src_check.cli import main as cli_main


def profile_src_check(project_path: str, output_file: Optional[str] = None) -> None:
    """Profile src-check execution."""
    print(f"🔍 Profiling src-check on: {project_path}")

    # Create a profile
    profiler = cProfile.Profile()

    # Modify sys.argv to pass the project path
    original_argv = sys.argv
    sys.argv = ["src-check", project_path]

    try:
        # Run src-check under profiler
        profiler.enable()
        cli_main()
        profiler.disable()
    except SystemExit:
        # Ignore SystemExit from CLI
        pass
    finally:
        # Restore original argv
        sys.argv = original_argv

    # Save or print results
    if output_file:
        profiler.dump_stats(output_file)
        print(f"✅ Profile saved to: {output_file}")

        # Also print summary
        print("\n📊 Top 20 functions by cumulative time:")
        stats = pstats.Stats(profiler)
        stats.sort_stats("cumulative")
        stats.print_stats(20)
    else:
        # Print detailed stats
        stats = pstats.Stats(profiler)

        print("\n📊 Profile Statistics")
        print("=" * 80)

        # Sort by cumulative time
        print("\n🕐 Top 30 functions by cumulative time:")
        stats.sort_stats("cumulative")
        stats.print_stats(30)

        # Sort by total time
        print("\n⏱️  Top 30 functions by total time:")
        stats.sort_stats("time")
        stats.print_stats(30)

        # Show callers
        print("\n📞 Top function callers:")
        stats.print_callers(10)


def analyze_profile(profile_file: str) -> None:
    """Analyze a saved profile file."""
    print(f"📈 Analyzing profile: {profile_file}")

    stats = pstats.Stats(profile_file)

    # Basic info
    total_calls = stats.total_calls
    total_time = stats.total_tt

    print(f"\nTotal function calls: {total_calls:,}")
    print(f"Total execution time: {total_time:.2f} seconds")

    # Find bottlenecks
    print("\n🔥 Performance Bottlenecks (by cumulative time):")
    stats.sort_stats("cumulative")
    stats.print_stats(20)

    # Find hot spots
    print("\n🌡️  Hot Spots (by total time):")
    stats.sort_stats("time")
    stats.print_stats(20)

    # Analyze by module
    print("\n📦 Time by Module:")
    stats.sort_stats("cumulative")

    module_times = {}
    for func, (cc, nc, tt, ct, callers) in stats.stats.items():
        module = func[0].split("/")[-1] if "/" in func[0] else func[0]
        if module not in module_times:
            module_times[module] = 0
        module_times[module] += ct

    # Sort and print module times
    sorted_modules = sorted(module_times.items(), key=lambda x: x[1], reverse=True)
    for module, time in sorted_modules[:10]:
        percentage = (time / total_time) * 100
        print(f"  {module}: {time:.2f}s ({percentage:.1f}%)")


def main():
    """Main profiling entry point."""
    parser = argparse.ArgumentParser(description="Profile src-check performance")
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Path to project to analyze (default: current directory)",
    )
    parser.add_argument("--output", "-o", help="Save profile to file")
    parser.add_argument("--analyze", "-a", help="Analyze existing profile file")

    args = parser.parse_args()

    if args.analyze:
        analyze_profile(args.analyze)
    else:
        profile_src_check(args.project_path, args.output)


if __name__ == "__main__":
    main()
