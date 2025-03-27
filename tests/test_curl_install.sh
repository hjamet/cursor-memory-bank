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
    # Create only the logs directory
    if ! mkdir -p "$LOGS_DIR"; then
        log_error "Failed to create logs directory"
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
    
    # Create test custom rule
    mkdir -p "$RULES_DIR/custom/test"
    echo "test custom rule" > "$RULES_DIR/custom/test/test.mdc"
    
    # Perform curl installation with --force
    if ! curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/main/install.sh | bash -s -- --force; then
        log_error "Curl installation failed"
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
    if [ ! -f "$RULES_DIR/core.mdc" ]; then
        log_error "Core rules not installed"
        return 1
    fi
    
    log "Curl installation test passed"
    return 0
}

test_curl_installation_with_options() {
    log "Testing curl installation with options..."
    
    # Save current directory
    local current_dir="$(pwd)"
    
    # Change to test directory
    cd "$TEST_DIR" || {
        log_error "Failed to change to test directory"
        return 1
    }
    
    # Create test custom rule
    mkdir -p "$RULES_DIR/custom/test"
    echo "test custom rule" > "$RULES_DIR/custom/test/test.mdc"
    
    # Test with --no-backup and --force options
    if ! curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/main/install.sh | bash -s -- --no-backup --force; then
        log_error "Curl installation with --no-backup failed"
        cd "$current_dir"
        return 1
    fi
    
    # Verify no backup was created
    if ls -d "$RULES_DIR".bak-* &>/dev/null; then
        log_error "Backup was created despite --no-backup option"
        cd "$current_dir"
        return 1
    fi
    
    # Return to original directory
    cd "$current_dir"
    
    log "Curl installation with options test passed"
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
    
    # Test with invalid URL
    if curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/invalid/install.sh | bash &>/dev/null; then
        log_error "Installation should fail with invalid URL"
        cd "$current_dir"
        return 1
    fi
    
    # Return to original directory
    cd "$current_dir"
    
    log "Curl installation error handling test passed"
    return 0
}

# Run tests
run_tests() {
    local failed=0
    
    # Setup test environment
    if ! setup; then
        log_error "Failed to set up test environment"
        return 1
    fi
    
    # Run installation tests
    if ! test_curl_installation; then
        ((failed++))
    fi
    
    if ! test_curl_installation_with_options; then
        ((failed++))
    fi
    
    if ! test_curl_installation_error_handling; then
        ((failed++))
    fi
    
    # Report results
    if ((failed == 0)); then
        echo -e "\n${GREEN}All curl installation tests passed!${NC}"
        return 0
    else
        echo -e "\n${RED}$failed test(s) failed${NC}"
        return 1
    fi
}

# Cleanup on exit
trap teardown EXIT

# Run the tests
if ! run_tests; then
    log_error "Some tests failed"
    exit 1
fi

log "All tests completed successfully"
exit 0 