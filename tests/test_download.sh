#!/bin/bash

# Test Download Functionality
#
# This file contains tests for the download and verification functionality.
#
# Prerequisites:
# - curl installed
# - sha256sum installed
# - Internet connection
#
# Execution:
# ./test_download.sh
#
# Expected Results:
# - All download tests pass
# - All checksum verification tests pass
# - All error cases are handled properly

# Setup test environment
TEST_DIR="/tmp/cursor-test-$$"
LOGS_DIR="$TEST_DIR/logs"
TEST_LOG="$LOGS_DIR/test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log() {
    local message="$1"
    echo -e "${GREEN}[INFO]${NC} $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $message" >> "$TEST_LOG"
}

log_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $message" >> "$TEST_LOG"
}

log_warn() {
    local message="$1"
    echo -e "${YELLOW}[WARN]${NC} $message"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $message" >> "$TEST_LOG"
}

setup() {
    mkdir -p "$LOGS_DIR"
    log "Created test environment at $TEST_DIR"
}

teardown() {
    if [[ -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
        log "Cleaned up test environment"
    fi
}

# Source the main script
SCRIPT_DIR="$(dirname "$0")"
INSTALL_SCRIPT="$SCRIPT_DIR/../install.sh"

if [[ ! -f "$INSTALL_SCRIPT" ]]; then
    log_error "Installation script not found at $INSTALL_SCRIPT"
    exit 1
fi

if ! source "$INSTALL_SCRIPT"; then
    log_error "Failed to source $INSTALL_SCRIPT"
    exit 1
fi

log "Successfully sourced installation script"

# Setup
MOCK_SERVER="https://example.com"
MOCK_FILE="test.txt"
MOCK_CHECKSUM="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Empty file checksum

# Test Cases
test_download_file_success() {
    echo "Testing successful file download..."
    if download_file "https://raw.githubusercontent.com/lopilo24/cursor-memory-bank/main/README.md" "$TEST_DIR/README.md"; then
        echo "✓ Download successful"
        return 0
    else
        echo "✗ Download failed"
        return 1
    fi
}

test_download_file_invalid_url() {
    echo "Testing download with invalid URL..."
    if ! download_file "https://invalid.example.com/nonexistent" "$TEST_DIR/invalid.txt" 2>/dev/null; then
        echo "✓ Invalid URL handled correctly"
        return 0
    else
        echo "✗ Invalid URL not handled"
        return 1
    fi
}

test_verify_checksum_success() {
    echo "Testing successful checksum verification..."
    echo -n "" > "$TEST_DIR/empty.txt"
    echo "$MOCK_CHECKSUM  empty.txt" > "$TEST_DIR/checksum.sha256"
    cd "$TEST_DIR"
    if verify_checksum "empty.txt" "checksum.sha256"; then
        echo "✓ Checksum verification successful"
        cd - > /dev/null
        return 0
    else
        echo "✗ Checksum verification failed"
        cd - > /dev/null
        return 1
    fi
}

test_verify_checksum_failure() {
    echo "Testing checksum verification failure..."
    echo "modified" > "$TEST_DIR/modified.txt"
    echo "$MOCK_CHECKSUM  modified.txt" > "$TEST_DIR/checksum.sha256"
    cd "$TEST_DIR"
    if ! verify_checksum "modified.txt" "checksum.sha256" 2>/dev/null; then
        echo "✓ Invalid checksum detected"
        cd - > /dev/null
        return 0
    else
        echo "✗ Invalid checksum not detected"
        cd - > /dev/null
        return 1
    fi
}

test_download_and_verify_integration() {
    echo "Testing download and verify integration..."
    if download_and_verify "$DOWNLOAD_URL" "$TEST_DIR"; then
        echo "✓ Download and verify integration successful"
        return 0
    else
        echo "✗ Download and verify integration failed"
        return 1
    fi
}

# Run Tests
run_tests() {
    local failures=0

    setup

    # Run individual test cases
    test_download_file_success || ((failures++))
    test_download_file_invalid_url || ((failures++))
    test_verify_checksum_success || ((failures++))
    test_verify_checksum_failure || ((failures++))
    test_download_and_verify_integration || ((failures++))

    teardown

    echo
    echo "Test Summary:"
    echo "-------------"
    echo "Total tests: 5"
    echo "Failures: $failures"
    echo "-------------"

    if [[ -f "$TEST_LOG" ]]; then
        echo "Test log available at: $TEST_LOG"
    fi

    return $failures
}

# Set up cleanup on exit
trap teardown EXIT

# Execute tests if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_tests
fi 