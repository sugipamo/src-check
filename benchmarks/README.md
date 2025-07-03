# src-check Performance Benchmarks

This directory contains performance benchmarking and profiling tools for src-check.

## 🚀 Quick Start

### Running Benchmarks

```bash
# Benchmark src-check on itself
python benchmarks/benchmark.py

# Benchmark specific projects
python benchmarks/benchmark.py --projects "Django:/path/to/django" "FastAPI:/path/to/fastapi"

# Save results to custom file
python benchmarks/benchmark.py --output results.json
```

### Profiling Performance

```bash
# Profile src-check on current directory
python benchmarks/profile.py

# Profile specific project
python benchmarks/profile.py /path/to/project

# Save profile for later analysis
python benchmarks/profile.py /path/to/project --output profile.stats

# Analyze saved profile
python benchmarks/profile.py --analyze profile.stats
```

## 📊 Benchmark Metrics

The benchmark script measures:
- **Execution time**: Total time to analyze the project
- **Memory usage**: Peak memory consumption during analysis
- **Throughput**: Files/second and lines/second processed
- **File statistics**: Total files and lines analyzed

## 🔍 Profiling Details

The profiling script provides:
- Function-level performance breakdown
- Cumulative vs. total time analysis
- Module-level time distribution
- Performance bottleneck identification

## 📈 Performance Goals

Based on our roadmap, the performance targets are:
- **v0.2.0**: Process 1000 lines in < 10 seconds
- **v0.4.0**: Process 1000 files in < 5 seconds
- **Memory**: < 500MB for large projects

## 🧪 Test Projects

Recommended test projects for benchmarking:
1. **Small**: src-check itself (~5K lines)
2. **Medium**: FastAPI (~10K lines)
3. **Large**: Django (~50K lines)
4. **Extra Large**: Pandas (~100K+ lines)

## 📝 Example Results

```json
{
  "name": "src-check",
  "execution_time": 3.45,
  "peak_memory_mb": 45.2,
  "file_count": 89,
  "line_count": 4532,
  "files_per_second": 25.8,
  "lines_per_second": 1313.6
}
```

## 🛠️ Optimization Workflow

1. Run benchmark to establish baseline
2. Profile to identify bottlenecks
3. Implement optimizations
4. Re-run benchmark to measure improvement
5. Document changes and results