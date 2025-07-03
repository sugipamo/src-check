#!/usr/bin/env python3
"""
Show current project metrics.
"""

import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


def count_lines(file_path: Path) -> Tuple[int, int, int]:
    """Count total lines, code lines, and comment lines."""
    with open(file_path, encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    blank = sum(1 for line in lines if not line.strip())
    comment = sum(1 for line in lines if line.strip().startswith('#'))
    code = total - blank - comment
    
    return total, code, comment


def analyze_complexity(file_path: Path) -> List[Tuple[str, int]]:
    """Analyze cyclomatic complexity of functions."""
    with open(file_path, encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except Exception:
        return []
    
    complexities = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
                elif isinstance(child, ast.ExceptHandler):
                    complexity += 1
            
            if complexity > 5:  # Only show complex functions
                complexities.append((node.name, complexity))
    
    return complexities


def get_test_coverage() -> float:
    """Get test coverage percentage."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', '--cov=src_check', '--cov-report=', '-q'],
            capture_output=True,
            text=True
        )
        
        # Parse coverage from output
        for line in result.stdout.split('\n'):
            if 'TOTAL' in line:
                parts = line.split()
                if len(parts) >= 4:
                    return float(parts[-1].rstrip('%'))
    except Exception:
        pass
    
    return 0.0


def count_checkers() -> Dict[str, int]:
    """Count implemented checkers."""
    checkers = {
        'security': 0,
        'code_quality': 0,
        'architecture': 0,
        'test_quality': 0,
        'total': 0
    }
    
    rules_dir = Path('src/src_check/rules')
    if rules_dir.exists():
        for file in rules_dir.glob('*.py'):
            if file.name != '__init__.py':
                checkers['total'] += 1
                category = file.stem
                if category in checkers:
                    checkers[category] = 1
    
    return checkers


def main():
    """Show project metrics."""
    print("=" * 60)
    print("📊 src-check Project Metrics")
    print("=" * 60)
    
    # Code statistics
    print("\n📈 Code Statistics:")
    src_dir = Path('src/src_check')
    total_lines = 0
    total_code = 0
    total_comments = 0
    file_count = 0
    
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            lines, code, comments = count_lines(py_file)
            total_lines += lines
            total_code += code
            total_comments += comments
            file_count += 1
    
    print(f"  Python files: {file_count}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Code lines: {total_code:,}")
    print(f"  Comment lines: {total_comments:,}")
    print(f"  Comment ratio: {total_comments/total_code*100:.1f}%")
    
    # Test coverage
    print("\n🧪 Test Coverage:")
    coverage = get_test_coverage()
    print(f"  Overall: {coverage:.1f}%")
    print("  Target: 70%")
    print(f"  Status: {'✅ PASS' if coverage >= 70 else '❌ FAIL'}")
    
    # Complexity analysis
    print("\n🔍 Code Complexity (functions > 5):")
    complex_functions = []
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            complexities = analyze_complexity(py_file)
            for func_name, complexity in complexities:
                complex_functions.append((py_file.relative_to(src_dir), func_name, complexity))
    
    complex_functions.sort(key=lambda x: x[2], reverse=True)
    for file_path, func_name, complexity in complex_functions[:10]:
        print(f"  {file_path}::{func_name} - {complexity}")
    
    # Feature completion
    print("\n✅ Feature Completion:")
    checkers = count_checkers()
    print(f"  Checkers: {checkers['total']}/20 ({checkers['total']/20*100:.0f}%)")
    print(f"    - Security: {'✅' if checkers['security'] else '⬜'}")
    print(f"    - Code Quality: {'✅' if checkers['code_quality'] else '⬜'}")
    print(f"    - Architecture: {'✅' if checkers['architecture'] else '⬜'}")
    print(f"    - Test Quality: {'✅' if checkers['test_quality'] else '⬜'}")
    
    # Documentation
    print("\n📚 Documentation:")
    docs = {
        'README.md': Path('README.md').exists(),
        'requirements-specification.md': Path('requirements-specification.md').exists(),
        'security-migration-plan.md': Path('security-migration-plan.md').exists(),
        'development-cycle.md': Path('development-cycle.md').exists(),
    }
    
    doc_count = sum(1 for exists in docs.values() if exists)
    print(f"  Core docs: {doc_count}/{len(docs)} ({doc_count/len(docs)*100:.0f}%)")
    for doc, exists in docs.items():
        print(f"    - {doc}: {'✅' if exists else '⬜'}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()