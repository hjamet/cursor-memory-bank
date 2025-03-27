#!/bin/bash

# Tests for the installation script

# Set up test environment
TEST_DIR="/tmp/cursor-memory-bank-test-$$"
TEST_RULES_DIR="$TEST_DIR/.cursor/rules"
TEST_DIST_DIR="$TEST_DIR/dist"
ORIGINAL_DIR="$(pwd)"
VERSION="1.0.0"

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
    
    # Create test directories
    mkdir -p "$TEST_RULES_DIR/custom/test"
    mkdir -p "$TEST_DIST_DIR/cursor-memory-bank-${VERSION}"
    
    # Create test custom rule
    echo "test rule" > "$TEST_RULES_DIR/custom/test/test.mdc"
    
    # Create test project structure
    mkdir -p "$TEST_DIST_DIR/cursor-memory-bank-${VERSION}/rules/custom/test"
    echo "test rule" > "$TEST_DIST_DIR/cursor-memory-bank-${VERSION}/rules/custom/test/test.mdc"
    
    # Create test archive
    cd "$TEST_DIST_DIR"
    tar -czf "v${VERSION}.tar.gz" "cursor-memory-bank-${VERSION}/"
    cd "$ORIGINAL_DIR"
}

cleanup() {
    log "Cleaning up test environment..."
    rm -rf "$TEST_DIR"
}

# Test functions
test_clean_install() {
    log "Testing clean installation..."
    
    # Set up test environment variables
    export TEST_MODE=1
    export TEST_RULES_DIR="$TEST_RULES_DIR"
    export TEST_DIST_DIR="$TEST_DIST_DIR"
    
    # Run installation script
    if ! ../install.sh --dir "$TEST_DIR"; then
        error "Clean installation failed"
    fi
    
    # Verify installation
    if [[ ! -f "$TEST_RULES_DIR/custom/test/test.mdc" ]]; then
        error "Rules were not installed correctly"
    fi
    
    log "Clean installation test passed"
}

test_backup_restore() {
    log "Testing backup and restore functionality..."
    
    # Create custom rules
    mkdir -p "$TEST_RULES_DIR/custom/user"
    echo "user rule" > "$TEST_RULES_DIR/custom/user/user.mdc"
    
    # Run installation script with backup
    export TEST_MODE=1
    export TEST_RULES_DIR="$TEST_RULES_DIR"
    export TEST_DIST_DIR="$TEST_DIST_DIR"
    
    if ! ../install.sh --dir "$TEST_DIR"; then
        error "Installation with backup failed"
    fi
    
    # Verify backup
    local backup_pattern="$TEST_DIR/.cursor/rules.bak-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]"
    if ! ls -d $backup_pattern > /dev/null 2>&1; then
        error "Backup was not created"
    fi
    
    # Verify custom rules preserved
    if [[ ! -f "$TEST_RULES_DIR/custom/user/user.mdc" ]]; then
        error "Custom rules were not preserved"
    fi
    
    log "Backup and restore test passed"
}

test_error_handling() {
    log "Testing error handling..."
    
    # Test invalid directory
    if ../install.sh --dir "/nonexistent" 2>/dev/null; then
        error "Installation should fail with invalid directory"
    fi
    
    # Test invalid archive
    echo "invalid" > "$TEST_DIST_DIR/v${VERSION}.tar.gz"
    if ../install.sh --dir "$TEST_DIR" 2>/dev/null; then
        error "Installation should fail with invalid archive"
    fi
    
    log "Error handling test passed"
}

# Run tests
trap cleanup EXIT

log "Starting tests..."
setup

test_clean_install
test_backup_restore
test_error_handling

log "All tests passed successfully!" 