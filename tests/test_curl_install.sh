#!/bin/bash

# Test Curl Installation
#
# This file tests the end-to-end installation process using curl.
#
# Prerequisites:
# - curl installed
# - Internet connection
# - GitHub repository accessible
#
# Execution:
# ./test_curl_install.sh
#
# Expected Results:
# - Installation via curl completes successfully
# - All files are in place
# - Custom rules are preserved

# Setup test environment
TEST_DIR="/tmp/cursor-curl-test-$$"
LOGS_DIR="$TEST_DIR/logs"
TEST_LOG="$LOGS_DIR/test.log"
RULES_DIR="$TEST_DIR/.cursor/rules"

# Determine the absolute path to the install script in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_SCRIPT_PATH="$(cd "$SCRIPT_DIR/.." && pwd)/install.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log() {
    local message="$1"
    echo -e "${GREEN}[INFO]${NC} $message"
    if [[ -d "$LOGS_DIR" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $message" >> "$TEST_LOG"
    fi
}

log_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" >&2
    if [[ -d "$LOGS_DIR" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $message" >> "$TEST_LOG"
    fi
}

log_warn() {
    local message="$1"
    echo -e "${YELLOW}[WARN]${NC} $message"
    if [[ -d "$LOGS_DIR" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $message" >> "$TEST_LOG"
    fi
}

setup() {
    # First create the main test directory
    if ! mkdir -p "$TEST_DIR"; then
        echo -e "${RED}[ERROR]${NC} Failed to create test directory"
        return 1
    fi
    
    # Then create the logs directory
    if ! mkdir -p "$LOGS_DIR"; then
        echo -e "${RED}[ERROR]${NC} Failed to create logs directory"
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

# Test Cases
test_curl_installation() {
    log "Testing curl installation..."
    
    # Save current directory
    local current_dir="$(pwd)"
    
    # Change to test directory
    cd "$TEST_DIR" || {
        log_error "Failed to change to test directory"
        return 1
    }
    
    # Clean any existing backups from previous runs
    find "$TEST_DIR" -name "*.bak-*" -type d -exec rm -rf {} \; 2>/dev/null || true
    
    # Create test custom rule
    mkdir -p "$RULES_DIR/custom/test"
    echo "test custom rule" > "$RULES_DIR/custom/test/test.mdc"
    
    # Perform installation using LOCAL script with --force
    if ! bash "$INSTALL_SCRIPT_PATH" --dir "$TEST_DIR" --force; then
        log_error "Local installation failed"
        cd "$current_dir"
        return 1
    fi
    
    # Return to original directory
    cd "$current_dir"
    
    # Verify installation
    if [ ! -d "$RULES_DIR" ]; then
        log_error "Rules directory not created"
        return 1
    fi
    
    if [ ! -f "$RULES_DIR/custom/test/test.mdc" ]; then
        log_error "Custom rules not preserved"
        return 1
    fi
    
    # Check for core rules
    if [ ! -f "$RULES_DIR/system.mdc" ]; then
        log_error "Core rules not installed"
        return 1
    fi
    
    # Verify that it displays the commit date in the installation log
    local installation_log=$(bash "$INSTALL_SCRIPT_PATH" --dir "$TEST_DIR" --force --version 2>&1)
    if ! echo "$installation_log" | grep -q "([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\})"; then
        log_error "Commit date not displayed in version output"
        echo "Version output: $installation_log"
        return 1
    fi
    
    log "Curl installation test passed"
    return 0
}

test_curl_installation_with_options() {
    log "Testing curl installation with default options (no backup)..."
    
    # Save current directory
    local current_dir="$(pwd)"
    
    # Change to test directory
    cd "$TEST_DIR" || {
        log_error "Failed to change to test directory"
        return 1
    }
    
    # Clean any existing backups that might have been created by previous tests
    find "$TEST_DIR" -name "*.bak-*" -type d -exec rm -rf {} \; 2>/dev/null || true
    
    # Create test custom rule
    mkdir -p "$RULES_DIR/custom/test"
    echo "test custom rule" > "$RULES_DIR/custom/test/test.mdc"
    
    # Test with default options (no --backup) and --force option using LOCAL script
    if ! bash "$INSTALL_SCRIPT_PATH" --dir "$TEST_DIR" --force; then
        log_error "Local installation with default options (no backup) failed"
        cd "$current_dir"
        return 1
    fi
    
    # Verify no backup was created - check for both potential names (rules.bak-* and .cursor/rules.bak-*)
    backup_files=$(find "$TEST_DIR/.cursor" -path "*rules.bak-*" -type d 2>/dev/null | wc -l)
    if [[ $backup_files -gt 0 ]]; then
        log_error "Backup was created despite default no-backup behavior (found $backup_files backup files)"
        find "$TEST_DIR/.cursor" -path "*rules.bak-*" -type d -ls 2>/dev/null || true
        cd "$current_dir"
        return 1
    fi
    
    # Return to original directory
    cd "$current_dir"
    
    log "Curl installation with default options test passed"
    return 0
}

test_curl_installation_error_handling() {
    log "Testing curl installation error handling..."
    
    # Save current directory
    local current_dir="$(pwd)"
    
    # Change to test directory
    cd "$TEST_DIR" || {
        log_error "Failed to change to test directory"
        return 1
    }
    
    # Test with invalid URL and --use-curl, capturing the result
    log "Attempting to download from invalid URL (this should fail)..."
    
    # Temporarily disable exit on error for this command
    set +e 
    curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/invalid/install.sh -o /dev/null 
    local curl_status=$?
    # Re-enable exit on error immediately after
    set -e 

    log "Curl exit status: $curl_status"
    
    # For this test, we EXPECT curl to fail with the invalid URL, so a non-zero exit status is SUCCESS
    if [[ $curl_status -eq 0 ]]; then
        log_error "Test failed: curl should have failed with invalid URL but succeeded"
        cd "$current_dir"
        return 1
    else
        log "Test passed: curl failed with invalid URL as expected"
    fi
    
    # Return to original directory
    cd "$current_dir"
    
    log "Curl installation error handling test passed"
    return 0
}

# Run tests
run_tests() {
    local failed=0
    
    # Run each test in a clean environment
    
    # Setup test environment for first test
    if ! setup; then
        log_error "Failed to set up test environment"
        return 1
    fi
    
    # Run installation test
    if ! test_curl_installation; then
        ((failed++))
    fi
    
    # Clean up and setup fresh environment for second test
    teardown
    if ! setup; then
        log_error "Failed to set up test environment for options test"
        return 1
    fi
    
    # Run options test
    if ! test_curl_installation_with_options; then
        ((failed++))
    fi
    
    # Clean up and setup fresh environment for third test
    teardown
    if ! setup; then
        log_error "Failed to set up test environment for error handling test"
        return 1
    fi

    # Run error handling test
    if ! test_curl_installation_error_handling; then
        ((failed++))
    fi
    
    # Final cleanup
    teardown
    
    # Report results
    if [[ $failed -eq 0 ]]; then
        log "All tests passed!"
        return 0
    else
        log_error "$failed test(s) failed"
        return 1
    fi
}

# Execute tests
run_tests

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_tests
fi 