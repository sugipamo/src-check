#!/bin/bash
# Quick publish script for src-check v0.2.0
# This script helps to quickly publish to TestPyPI and PyPI

set -e

echo "🚀 src-check v0.2.0 Quick Publish Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Check for required tools
if ! command -v twine &> /dev/null; then
    echo "❌ Error: twine is not installed. Run: pip install twine"
    exit 1
fi

# Check for dist files
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "❌ Error: No distribution files found in dist/"
    echo "Run: python -m build"
    exit 1
fi

# Function to publish to TestPyPI
publish_testpypi() {
    echo "📦 Publishing to TestPyPI..."
    if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
        echo "❌ Error: TWINE_USERNAME and TWINE_PASSWORD must be set"
        echo "Example:"
        echo "  export TWINE_USERNAME=__token__"
        echo "  export TWINE_PASSWORD=pypi-<your-token>"
        return 1
    fi
    
    twine upload --repository testpypi dist/*
    echo "✅ Published to TestPyPI!"
    echo "View at: https://test.pypi.org/project/src-check/0.2.0/"
}

# Function to test installation from TestPyPI
test_install() {
    echo "🧪 Testing installation from TestPyPI..."
    # Create temporary venv
    temp_dir=$(mktemp -d)
    python -m venv "$temp_dir/venv"
    source "$temp_dir/venv/bin/activate"
    
    # Install from TestPyPI
    pip install -i https://test.pypi.org/simple/ src-check==0.2.0
    
    # Test commands
    src-check --version
    src-check --help
    
    # Cleanup
    deactivate
    rm -rf "$temp_dir"
    
    echo "✅ Installation test passed!"
}

# Function to publish to PyPI
publish_pypi() {
    echo "📦 Publishing to PyPI..."
    if [ -z "$TWINE_USERNAME" ] || [ -z "$TWINE_PASSWORD" ]; then
        echo "❌ Error: TWINE_USERNAME and TWINE_PASSWORD must be set"
        echo "Note: You need a different token for PyPI"
        return 1
    fi
    
    twine upload dist/*
    echo "✅ Published to PyPI!"
    echo "View at: https://pypi.org/project/src-check/0.2.0/"
}

# Main menu
echo "What would you like to do?"
echo "1) Publish to TestPyPI"
echo "2) Test installation from TestPyPI"
echo "3) Publish to PyPI (production)"
echo "4) Full workflow (TestPyPI → Test → PyPI)"
echo "5) Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        publish_testpypi
        ;;
    2)
        test_install
        ;;
    3)
        read -p "⚠️  Are you sure you want to publish to production PyPI? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            publish_pypi
        else
            echo "Cancelled."
        fi
        ;;
    4)
        publish_testpypi && \
        test_install && \
        read -p "Continue to PyPI? (yes/no): " confirm && \
        [ "$confirm" = "yes" ] && publish_pypi
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac