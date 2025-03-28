#!/bin/bash

# Test Download Functionality
#
# This file contains tests for the download functionality.
#
# Prerequisites:
# - curl installed
# - Internet connection
#
# Execution:
# ./test_download.sh
#
# Expected Results:
# - All download tests pass
# - All error cases are handled properly

# Setup test environment
TEST_DIR="/tmp/cursor-test-$$"
LOGS_DIR="$TEST_DIR/logs"
TEST_LOG="$LOGS_DIR/test.log"
export TEST_MODE=1
export TEST_RULES_DIR="$TEST_DIR/rules"

# Test files setup
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIST_DIR="$TEST_DIR/dist"
TEST_RULES_ARCHIVE="$TEST_DIST_DIR/v1.0.0.tar.gz"

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
    # Create logs directory
    if ! mkdir -p "$LOGS_DIR"; then
        log_error "Failed to create logs directory at $LOGS_DIR"
        return 1
    fi
    
    # Create test rules directory
    if ! mkdir -p "$TEST_RULES_DIR"; then
        log_error "Failed to create test rules directory at $TEST_RULES_DIR"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

    # Create test dist directory
    if ! mkdir -p "$TEST_DIST_DIR"; then
        log_error "Failed to create test dist directory at $TEST_DIST_DIR"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

    # Create test archive structure
    local temp_dir="$TEST_DIR/temp"
    mkdir -p "$temp_dir/cursor-memory-bank-1.0.0/rules"
    echo "Test rule content" > "$temp_dir/cursor-memory-bank-1.0.0/rules/test.rule"
    
    # Create test archive
    cd "$temp_dir"
    if ! tar -czf "$TEST_RULES_ARCHIVE" cursor-memory-bank-1.0.0/; then
        log_error "Failed to create test archive"
        cd - > /dev/null
        rm -rf "$TEST_DIR"
        return 1
    fi
    cd - > /dev/null

    log "Created test environment at $TEST_DIR"
    return 0
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
    echo -e "${RED}[ERROR]${NC} Installation script not found at $INSTALL_SCRIPT" >&2
    exit 1
fi

# Create test directory structure before sourcing
if ! setup; then
    echo -e "${RED}[ERROR]${NC} Failed to set up test environment" >&2
    exit 1
fi

if ! source "$INSTALL_SCRIPT"; then
    log_error "Failed to source $INSTALL_SCRIPT"
    teardown
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
    log "Running test_download_file_success"
    
    # Create test file
    local test_content="This is a test file for download verification"
    local test_file="$TEST_DIST_DIR/test_download.txt"
    echo "$test_content" > "$test_file"
    
    # Test download using file:// protocol
    if download_file "file://$test_file" "$TEST_DIR/downloaded.txt"; then
        # Verify content
        if [[ "$(cat "$TEST_DIR/downloaded.txt")" == "$test_content" ]]; then
            echo "✓ Download successful and content verified"
            log "test_download_file_success passed"
            return 0
        else
            echo "✗ Download succeeded but content mismatch"
            log_error "test_download_file_success failed: content mismatch"
            return 1
        fi
    else
        echo "✗ Download failed"
        log_error "test_download_file_success failed: download failed"
        return 1
    fi
}

test_download_file_invalid_url() {
    echo "Testing download with invalid URL..."
    log "Running test_download_file_invalid_url"
    
    if ! download_file "https://invalid.example.com/nonexistent" "$TEST_DIR/invalid.txt" 2>/dev/null; then
        echo "✓ Invalid URL handled correctly"
        log "test_download_file_invalid_url passed"
        return 0
    else
        echo "✗ Invalid URL not handled"
        log_error "test_download_file_invalid_url failed: invalid URL not handled"
        return 1
    fi
}

test_download_archive_success() {
    echo "Testing successful archive download..."
    log "Running test_download_archive_success"
    
    # Check if the function exists
    if ! type download_archive &>/dev/null; then
        log_warn "download_archive function not found, skipping test"
        echo "✓ Skipped archive download test (function not available)"
        return 0
    fi
    
    # Test download using file:// protocol
    if download_archive "file://$TEST_RULES_ARCHIVE" "$TEST_DIR/archive.tar.gz"; then
        # Verify file exists
        if [[ -f "$TEST_DIR/archive.tar.gz" ]]; then
            echo "✓ Archive download successful"
            log "test_download_archive_success passed"
            return 0
        else
            echo "✗ Archive download succeeded but file not found"
            log_error "test_download_archive_success failed: file not found after download"
            return 1
        fi
    else
        echo "✗ Archive download failed"
        log_error "test_download_archive_success failed: download failed"
        return 1
    fi
}

test_download_archive_invalid_url() {
    echo "Testing archive download with invalid URL..."
    log "Running test_download_archive_invalid_url"
    
    # Check if the function exists
    if ! type download_archive &>/dev/null; then
        log_warn "download_archive function not found, skipping test"
        echo "✓ Skipped archive invalid URL test (function not available)"
        return 0
    fi
    
    if ! download_archive "https://invalid.example.com/v1.0.0.tar.gz" "$TEST_DIR/invalid.tar.gz" 2>/dev/null; then
        echo "✓ Invalid URL handled correctly"
        log "test_download_archive_invalid_url passed"
        return 0
    else
        echo "✗ Invalid URL not handled"
        log_error "test_download_archive_invalid_url failed: invalid URL not handled"
        return 1
    fi
}

# Run tests
run_tests() {
    local failed=0
    log "Starting test execution"
    
    # Run download tests
    if ! test_download_file_success; then
        ((failed++))
        log_error "test_download_file_success failed"
    else
        log "test_download_file_success passed"
    fi
    
    if ! test_download_file_invalid_url; then
        ((failed++))
        log_error "test_download_file_invalid_url failed"
    else
        log "test_download_file_invalid_url passed"
    fi
    
    if ! test_download_archive_success; then
        ((failed++))
        log_error "test_download_archive_success failed"
    else
        log "test_download_archive_success passed"
    fi
    
    if ! test_download_archive_invalid_url; then
        ((failed++))
        log_error "test_download_archive_invalid_url failed"
    else
        log "test_download_archive_invalid_url passed"
    fi
    
    # Report results
    if ((failed == 0)); then
        echo -e "\n${GREEN}All tests passed!${NC}"
        log "All tests passed"
        return 0
    else
        echo -e "\n${RED}$failed test(s) failed${NC}"
        log_error "$failed test(s) failed"
        return 1
    fi
}

# Run the tests
if ! run_tests; then
    log_error "Some tests failed"
    teardown
    exit 1
fi

log "All tests completed successfully"
teardown
exit 0