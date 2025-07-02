"""
Tests for PerformanceChecker.
"""

import ast

from src_check.rules.performance import PerformanceChecker


class TestPerformanceChecker:
    """Test cases for PerformanceChecker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = PerformanceChecker()

    def test_string_concatenation_in_loop(self):
        """Test detection of string concatenation in loops."""
        code = """
result = ""
for i in range(100):
    result += str(i)  # Inefficient
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert len(result.failure_locations) >= 1
        assert any("PERF003" in issue.message for issue in result.failure_locations)

    def test_string_concatenation_with_augassign(self):
        """Test detection of += string concatenation in loops."""
        code = """
result = ""
for line in lines:
    result += line + "\\n"  # Inefficient
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF003" in issue.message for issue in result.failure_locations)

    def test_function_call_in_loop_range(self):
        """Test detection of function calls in loop range."""
        code = """
for i in range(calculate_limit()):  # Called every iteration?
    process(i)
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF001" in issue.message for issue in result.failure_locations)

    def test_len_in_range_is_ok(self):
        """Test that len() in range is not flagged."""
        code = """
for i in range(len(items)):  # This is OK
    print(items[i])
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        # Should not flag len() in range
        if result:
            assert not any(
                "PERF001" in issue.message for issue in result.failure_locations
            )

    def test_function_call_in_while_condition(self):
        """Test detection of function calls in while conditions."""
        code = """
while get_status() == "running":  # Called every iteration
    process()
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF002" in issue.message for issue in result.failure_locations)

    def test_unnecessary_type_conversion(self):
        """Test detection of unnecessary type conversions."""
        code = """
data = list(list(items))  # Redundant conversion
data2 = list(tuple(items))  # Also redundant
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF005" in issue.message for issue in result.failure_locations)

    def test_loop_invariant_computation(self):
        """Test detection of loop-invariant computations."""
        code = """
for i in range(100):
    constant_value = expensive_function()  # Doesn't depend on i
    result = i * constant_value
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF007" in issue.message for issue in result.failure_locations)

    def test_loop_invariant_function_calls(self):
        """Test detection of loop-invariant function calls."""
        code = """
for item in items:
    if item > len(reference_list):  # len() called every iteration
        process(item)
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF006" in issue.message for issue in result.failure_locations)

    def test_deeply_nested_comprehensions(self):
        """Test detection of deeply nested comprehensions."""
        code = """
result = [[[x*y*z for z in range(10)] for y in range(10)] for x in range(10)]
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert any("PERF004" in issue.message for issue in result.failure_locations)

    def test_list_comprehension_is_good(self):
        """Test that simple list comprehensions are not flagged."""
        code = """
# Good: List comprehension instead of loop
result = [x * 2 for x in range(100) if x % 2 == 0]
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        # Simple list comprehensions should not be flagged
        if result:
            assert not any(
                "PERF004" in issue.message for issue in result.failure_locations
            )

    def test_efficient_string_join(self):
        """Test that efficient string joining is not flagged."""
        code = """
# Good: Using join
parts = []
for i in range(100):
    parts.append(str(i))
result = "".join(parts)
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        # Efficient pattern should not be flagged for string concatenation
        if result:
            assert not any(
                "PERF003" in issue.message for issue in result.failure_locations
            )

    def test_no_issues_in_clean_code(self):
        """Test that clean code produces no issues."""
        code = '''
def efficient_function(data):
    """Process data efficiently."""
    # Pre-compute constants
    data_length = len(data)
    threshold = calculate_threshold()
    
    # Use list comprehension
    results = [process(item) for item in data if item > threshold]
    
    # Efficient string building
    output_parts = []
    for result in results:
        output_parts.append(format_result(result))
    
    return "\\n".join(output_parts)
'''
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        # Clean code should have no performance issues
        assert result is None or len(result.failure_locations) == 0

    def test_multiple_issues_in_bad_code(self):
        """Test detection of multiple performance issues."""
        code = """
def bad_performance(items):
    result = ""
    for i in range(len(get_items())):  # Function call in range
        item = items[i]
        result += str(item)  # String concatenation in loop
        
        # Loop invariant
        constant = expensive_calculation()
        value = item * constant
        
    # Unnecessary conversion
    return list(list(result))
"""
        tree = ast.parse(code)
        result = self.checker.check(tree, "test.py")

        assert result is not None
        assert len(result.failure_locations) >= 3  # At least 3 different issues

        # Check for different issue types
        messages = [issue.message for issue in result.failure_locations]
        assert any("PERF001" in msg for msg in messages)  # Function in range
        assert any("PERF003" in msg for msg in messages)  # String concatenation
        assert any("PERF007" in msg for msg in messages)  # Loop invariant
