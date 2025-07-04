"""Unit tests for the FileContextAnalyzer."""

from src_check.context import FileType
from src_check.context.analyzer import FileContextAnalyzer
from src_check.models.config import SrcCheckConfig


class TestFileContextAnalyzer:
    """Test cases for FileContextAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FileContextAnalyzer()

    def test_classify_production_file(self):
        """Test classification of production code files."""
        test_cases = [
            "src/main.py",
            "app/models/user.py",
            "lib/utils.py",
            "myproject/core/engine.py",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.PRODUCTION

    def test_classify_example_files(self):
        """Test classification of example/demo files."""
        test_cases = [
            "examples/basic_usage.py",
            "demo/sample_app.py",
            "docs/example/quickstart.py",
            "tutorials/lesson1.py",
            "samples/hello_world.py",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.EXAMPLE

    def test_classify_test_files(self):
        """Test classification of test files."""
        test_cases = [
            "tests/test_main.py",
            "test_utils.py",
            "spec/test_user_spec.py",
            "tests/unit/test_analyzer.py",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.TEST

    def test_classify_config_files(self):
        """Test classification of configuration files."""
        test_cases = [
            "config.py",
            "settings.py",
            "setup.py",
            "pyproject.toml",
            ".github/workflows/ci.yml",
            "requirements.txt",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.CONFIG

    def test_classify_documentation_files(self):
        """Test classification of documentation files."""
        test_cases = [
            "README.md",
            "CHANGELOG.rst",
            "docs/guide.txt",
            "CONTRIBUTING.md",
            "LICENSE",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.DOCUMENTATION

    def test_classify_generated_files(self):
        """Test classification of generated files."""
        test_cases = [
            "build/lib/module.py",
            "dist/package.py",
            "__pycache__/module.cpython-39.pyc",
            "generated/api_client.py",
            ".egg-info/PKG-INFO",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.GENERATED

    def test_classify_vendor_files(self):
        """Test classification of vendor/third-party files."""
        test_cases = [
            "vendor/requests/api.py",
            "third_party/django/core.py",
            "external/libs/utils.py",
            "dependencies/numpy/array.py",
        ]

        for path in test_cases:
            assert self.analyzer.classify_file(path) == FileType.VENDOR

    def test_severity_multipliers(self):
        """Test severity multipliers for different file types."""
        assert self.analyzer.get_severity_multiplier(FileType.PRODUCTION) == 1.0
        assert self.analyzer.get_severity_multiplier(FileType.TEST) == 0.7
        assert self.analyzer.get_severity_multiplier(FileType.EXAMPLE) == 0.3
        assert self.analyzer.get_severity_multiplier(FileType.CONFIG) == 0.8
        assert self.analyzer.get_severity_multiplier(FileType.DOCUMENTATION) == 0.2
        assert self.analyzer.get_severity_multiplier(FileType.GENERATED) == 0.0
        assert self.analyzer.get_severity_multiplier(FileType.VENDOR) == 0.0

    def test_should_check_file(self):
        """Test file checking decisions."""
        # Should check these files
        assert self.analyzer.should_check_file("src/main.py") is True
        assert self.analyzer.should_check_file("tests/test_main.py") is True
        assert self.analyzer.should_check_file("examples/demo.py") is True

        # Should not check these files
        assert self.analyzer.should_check_file("build/lib/module.py") is False
        assert self.analyzer.should_check_file("vendor/lib.py") is False
        assert self.analyzer.should_check_file("__pycache__/module.pyc") is False

    def test_custom_patterns(self):
        """Test custom pattern configuration."""
        config = SrcCheckConfig()
        # Create a custom config with additional attributes
        setattr(config, "context", {
            "example_patterns": ["playground", "sandbox"],
        })

        analyzer = FileContextAnalyzer(config)

        # Test custom patterns work
        assert analyzer.classify_file("playground/test.py") == FileType.EXAMPLE
        assert analyzer.classify_file("sandbox/experiment.py") == FileType.EXAMPLE

        # Test default patterns still work
        assert analyzer.classify_file("examples/demo.py") == FileType.EXAMPLE

    def test_get_context_rules(self):
        """Test context-specific rule retrieval."""
        # Example files should have relaxed rules
        example_rules = self.analyzer.get_context_rules(FileType.EXAMPLE)
        assert example_rules["print_statements"]["severity"] == "warning"
        assert example_rules["complexity"]["threshold_multiplier"] == 2.0

        # Test files should have specific rules
        test_rules = self.analyzer.get_context_rules(FileType.TEST)
        assert test_rules["print_statements"]["enabled"] is False
        assert test_rules["test_quality"]["strict"] is True

        # Config files should have some rules disabled
        config_rules = self.analyzer.get_context_rules(FileType.CONFIG)
        assert config_rules["type_hints"]["enabled"] is False
        assert config_rules["docstrings"]["enabled"] is False

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        test_cases = [
            ("Examples/demo.py", FileType.EXAMPLE),
            ("TESTS/test_main.py", FileType.TEST),
            ("Demo/Sample.py", FileType.EXAMPLE),
            ("BUILD/output.py", FileType.GENERATED),
        ]

        for path, expected_type in test_cases:
            assert self.analyzer.classify_file(path) == expected_type
