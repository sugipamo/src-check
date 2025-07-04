#!/usr/bin/env python3
"""src-check performance benchmark script."""

import argparse
import json
import os
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List

# import psutil  # Optional for memory tracking


class BenchmarkRunner:
    """Run performance benchmarks for src-check."""

    def __init__(self, output_file: str = "benchmark_results.json"):
        self.output_file = output_file
        self.results: List[Dict[str, Any]] = []

    def run_benchmark(self, project_path: str, name: str) -> Dict[str, Any]:
        """Run benchmark for a single project."""
        print(f"\n📊 Benchmarking {name}...")

        # Start memory tracking
        tracemalloc.start()

        # Record start metrics
        start_time = time.time()

        # Run src-check
        cmd = [sys.executable, "-m", "src_check.cli.main", project_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
        except Exception as e:
            success = False
            output = ""
            error = str(e)

        # Record end metrics
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Calculate metrics
        execution_time = end_time - start_time
        peak_memory = peak / 1024 / 1024  # MB

        # Count files
        file_count = sum(1 for _ in Path(project_path).rglob("*.py"))

        # Count lines
        line_count = 0
        for py_file in Path(project_path).rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    line_count += len(f.readlines())
            except:
                pass

        result = {
            "name": name,
            "project_path": project_path,
            "success": success,
            "execution_time": round(execution_time, 2),
            "peak_memory_mb": round(peak_memory, 2),
            "file_count": file_count,
            "line_count": line_count,
            "files_per_second": (
                round(file_count / execution_time, 2) if execution_time > 0 else 0
            ),
            "lines_per_second": (
                round(line_count / execution_time, 2) if execution_time > 0 else 0
            ),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(f"✅ Completed in {execution_time:.2f}s")
        print(f"   Files: {file_count}, Lines: {line_count}")
        print(
            f"   Speed: {result['files_per_second']:.2f} files/s, {result['lines_per_second']:.2f} lines/s"
        )
        print(f"   Memory: {peak_memory:.2f} MB peak")

        return result

    def run_all_benchmarks(self, projects: List[Dict[str, str]]) -> None:
        """Run benchmarks for all projects."""
        print("🚀 Starting src-check benchmark suite")
        print("=" * 50)

        for project in projects:
            result = self.run_benchmark(project["path"], project["name"])
            self.results.append(result)

        # Save results
        with open(self.output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print benchmark summary."""
        print("\n" + "=" * 50)
        print("📈 Benchmark Summary")
        print("=" * 50)

        total_files = sum(r["file_count"] for r in self.results)
        total_lines = sum(r["line_count"] for r in self.results)
        total_time = sum(r["execution_time"] for r in self.results)
        avg_memory = sum(r["peak_memory_mb"] for r in self.results) / len(self.results)

        print(f"Total files processed: {total_files}")
        print(f"Total lines processed: {total_lines}")
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Average peak memory: {avg_memory:.2f} MB")
        print(
            f"Overall throughput: {total_files/total_time:.2f} files/s, {total_lines/total_time:.2f} lines/s"
        )

        print("\nPer-project results:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(
                f"{status} {result['name']}: {result['execution_time']:.2f}s, "
                f"{result['file_count']} files, {result['peak_memory_mb']:.2f} MB"
            )


def main():
    """Main benchmark entry point."""
    parser = argparse.ArgumentParser(description="Run src-check performance benchmarks")
    parser.add_argument(
        "--projects", nargs="+", help="Project paths to benchmark (format: name:path)"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results (default: benchmark_results.json)",
    )

    args = parser.parse_args()

    # Default projects if none specified
    if not args.projects:
        # Use src-check itself as a test project
        projects = [{"name": "src-check", "path": "."}]
    else:
        projects = []
        for project in args.projects:
            if ":" in project:
                name, path = project.split(":", 1)
            else:
                name = os.path.basename(project)
                path = project
            projects.append({"name": name, "path": path})

    runner = BenchmarkRunner(args.output)
    runner.run_all_benchmarks(projects)


if __name__ == "__main__":
    main()
