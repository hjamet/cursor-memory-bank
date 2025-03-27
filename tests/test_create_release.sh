#!/bin/bash

# Tests for the release creation script

# Set up test environment
TEST_DIR="/tmp/cursor-memory-bank-test-$$"
TEST_RULES_DIR="$TEST_DIR/.cursor/rules"
TEST_DIST_DIR="$TEST_DIR/dist"
ORIGINAL_DIR="$(pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

setup() {
    log "Setting up test environment..."
    mkdir -p "$TEST_RULES_DIR/custom/test"
    mkdir -p "$TEST_DIST_DIR"
    echo "test rule" > "$TEST_RULES_DIR/custom/test/test.mdc"
}

cleanup() {
    log "Cleaning up test environment..."
    rm -rf "$TEST_DIR"
}

# Test functions
test_archive_creation() {
    log "Testing archive creation..."
    
    # Set up test environment variables
    export RULES_DIR="$TEST_RULES_DIR"
    export DIST_DIR="$TEST_DIST_DIR"
    
    # Run release script
    if ! ./scripts/create-release.sh; then
        error "Archive creation failed"
    fi
    
    # Verify archive exists
    if [[ ! -f "$TEST_DIST_DIR/rules.tar.gz" ]]; then
        error "Archive was not created"
    fi
    
    log "Archive creation test passed"
}

test_checksum_creation() {
    log "Testing checksum creation..."
    
    # Set up test environment variables
    export RULES_DIR="$TEST_RULES_DIR"
    export DIST_DIR="$TEST_DIST_DIR"
    
    # Run release script
    if ! ./scripts/create-release.sh; then
        error "Checksum creation failed"
    fi
    
    # Verify checksum exists
    if [[ ! -f "$TEST_DIST_DIR/rules.sha256" ]]; then
        error "Checksum file was not created"
    fi
    
    # Verify checksum is valid
    cd "$TEST_DIST_DIR"
    if ! sha256sum -c rules.sha256; then
        error "Checksum verification failed"
    fi
    cd "$ORIGINAL_DIR"
    
    log "Checksum creation test passed"
}

test_error_handling() {
    log "Testing error handling..."
    
    # Test with non-existent rules directory
    export RULES_DIR="/nonexistent"
    export DIST_DIR="$TEST_DIST_DIR"
    
    # Run script and capture output and return code
    ./scripts/create-release.sh > "$TEST_DIR/output.txt" 2>&1
    ret_code=$?
    
    if [[ $ret_code -eq 0 ]]; then
        error "Script should fail"
    fi
    if [[ $ret_code -ne 1 ]]; then
        error "Script should return error code 1, got $ret_code"
    fi
    if ! grep -q "Rules directory does not exist" "$TEST_DIR/output.txt"; then
        error "Script did not produce expected error message for non-existent rules directory"
    fi
    
    # Test with non-writable dist directory
    export RULES_DIR="$TEST_RULES_DIR"
    export DIST_DIR="/root/dist"
    
    # Run script and capture output and return code
    ./scripts/create-release.sh > "$TEST_DIR/output.txt" 2>&1
    ret_code=$?
    
    if [[ $ret_code -eq 0 ]]; then
        error "Script should fail"
    fi
    if [[ $ret_code -ne 1 ]]; then
        error "Script should return error code 1, got $ret_code"
    fi
    if ! grep -q "Cannot create distribution directory" "$TEST_DIR/output.txt"; then
        error "Script did not produce expected error message for non-writable directory"
    fi
    
    # Clean up output file
    rm -f "$TEST_DIR/output.txt"
    
    log "Error handling test passed"
}

# Run tests
trap cleanup EXIT

log "Starting tests..."
setup

test_archive_creation
test_checksum_creation
test_error_handling

log "All tests passed successfully!" 