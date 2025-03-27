#!/bin/bash

# Test suite for the Cursor Memory Bank installation script
# This file contains tests for the installation script functionality

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
setup() {
    # Create temporary test directory
    TEST_DIR=$(mktemp -d)
    cp install.sh "$TEST_DIR/"
    cd "$TEST_DIR" || exit 1
}

teardown() {
    # Clean up test directory
    cd - > /dev/null || exit 1
    rm -rf "$TEST_DIR"
}

assert() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $1${NC}"
        ((TESTS_FAILED++))
    fi
    ((TESTS_RUN++))
}

# Test cases
test_help_flag() {
    echo "Testing help flag..."
    ./install.sh --help | grep -q "Usage:"
    assert "Help flag should display usage information"
}

test_version_flag() {
    echo "Testing version flag..."
    ./install.sh --version | grep -q "v[0-9]"
    assert "Version flag should display version information"
}

test_invalid_option() {
    echo "Testing invalid option..."
    ./install.sh --invalid 2>&1 | grep -q "ERROR"
    assert "Invalid option should display error"
}

test_directory_option() {
    echo "Testing directory option..."
    mkdir -p test_install
    ./install.sh --dir test_install
    [ -d "test_install/.cursor" ]
    assert "Directory option should create rules in specified directory"
}

# Run tests
echo "Running installation script tests..."
setup

test_help_flag
test_version_flag
test_invalid_option
test_directory_option

teardown

# Print summary
echo "Test Summary:"
echo "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"

# Exit with failure if any tests failed
[ $TESTS_FAILED -eq 0 ] 