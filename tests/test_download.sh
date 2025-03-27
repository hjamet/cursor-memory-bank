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
export TEST_MODE=1
export TEST_RULES_DIR="$TEST_DIR/rules"

# Test files setup
SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIST_DIR="$TEST_DIR/dist"
TEST_RULES_ARCHIVE="$TEST_DIST_DIR/rules.tar.gz"
TEST_RULES_CHECKSUM="$TEST_DIST_DIR/rules.tar.gz.sha256"

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

    # Check if source files exist
    if [[ ! -f "$PROJECT_ROOT/dist/rules.tar.gz" ]]; then
        log_error "Test archive not found at $PROJECT_ROOT/dist/rules.tar.gz"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

    if [[ ! -f "$PROJECT_ROOT/dist/rules.tar.gz.sha256" ]]; then
        log_error "Test checksum not found at $PROJECT_ROOT/dist/rules.tar.gz.sha256"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

    # Copy test files
    log "Copying test files to $TEST_DIST_DIR"
    if ! cp "$PROJECT_ROOT/dist/rules.tar.gz" "$TEST_RULES_ARCHIVE"; then
        log_error "Failed to copy rules archive to $TEST_RULES_ARCHIVE"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

    if ! cp "$PROJECT_ROOT/dist/rules.tar.gz.sha256" "$TEST_RULES_CHECKSUM"; then
        log_error "Failed to copy rules checksum to $TEST_RULES_CHECKSUM"
        rm -rf "$TEST_DIR"  # Clean up if we fail
        return 1
    fi

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
    
    # Create test file
    local test_content="This is a test file for download verification"
    local test_file="$TEST_DIST_DIR/test_download.txt"
    echo "$test_content" > "$test_file"
    
    # Test download using file:// protocol
    if download_file "file://$test_file" "$TEST_DIR/downloaded.txt"; then
        # Verify content
        if [[ "$(cat "$TEST_DIR/downloaded.txt")" == "$test_content" ]]; then
            echo "✓ Download successful and content verified"
            return 0
        else
            echo "✗ Download succeeded but content mismatch"
            return 1
        fi
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
    
    # Create test archive and checksum
    local test_content="This is a test archive for integration testing"
    local archive_path="$TEST_DIST_DIR/$ARCHIVE_NAME"
    local checksum_path="$TEST_DIST_DIR/$ARCHIVE_NAME.sha256"
    
    # Create test archive
    echo "$test_content" > "$archive_path"
    
    # Generate checksum
    cd "$TEST_DIST_DIR"
    sha256sum "$ARCHIVE_NAME" > "$ARCHIVE_NAME.sha256"
    cd - > /dev/null
    
    # Test download and verify
    if download_and_verify "file://$archive_path" "$TEST_DIR"; then
        # Verify downloaded file exists
        if [[ -f "$TEST_DIR/$ARCHIVE_NAME" ]]; then
            # Verify content
            if [[ "$(cat "$TEST_DIR/$ARCHIVE_NAME")" == "$test_content" ]]; then
                echo "✓ Download and verify integration successful"
                return 0
            else
                echo "✗ Download succeeded but content mismatch"
                return 1
            fi
        else
            echo "✗ Download succeeded but file not found"
            return 1
        fi
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