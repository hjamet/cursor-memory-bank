#!/bin/bash

# Ensure tmp directory is clean
rm -rf tmp/
mkdir -p tmp/

# Source the main install script to test its functions
# Determine the script's directory
SCRIPT_DIR=$(cd $(dirname $0) && pwd)

# Source the main install script
# Assuming install.sh is in the parent directory
source "$SCRIPT_DIR/../install.sh"

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
    log "Testing clean installation including MCP server setup..."
    
    # Create dummy MCP server files for the test
    local mcp_server_test_dir="$TEST_DIR/.cursor/mcp/mcp-commit-server"
    mkdir -p "$mcp_server_test_dir"
    echo '{ "name": "dummy-mcp-server-test" }' > "$mcp_server_test_dir/package.json"
    
    # Set up test environment variables
    export TEST_MODE=1 # Potentially used by install.sh? Keep for safety.
    export TEST_RULES_DIR="$TEST_RULES_DIR"
    export TEST_DIST_DIR="$TEST_DIST_DIR"
    
    # Run installation script using absolute path and capture output
    local install_script="$(cd "$(dirname "$0")/.." && pwd)/install.sh"
    if [[ ! -f "$install_script" ]]; then
        error "Installation script not found at $install_script"
        return 1
    fi
    
    local install_output
    install_output=$(bash "$install_script" --dir "$TEST_DIR" 2>&1)
    local install_status=$?
    
    log "Installation script output:\n$install_output"
    
    if [[ $install_status -ne 0 ]]; then
        error "Clean installation failed (Exit code: $install_status)"
        return 1
    fi
    
    # Verify core rules installation
    if [[ ! -d "$TEST_RULES_DIR" ]]; then
        error "Rules directory was not created"
        return 1
    fi

    # Verify pre-commit hook installation
    local hook_file="$TEST_DIR/.githooks/pre-commit"
    if [[ ! -f "$hook_file" ]]; then
        error "Pre-commit hook file was not created at $hook_file"
        return 1
    fi
    if [[ ! -x "$hook_file" ]]; then
        error "Pre-commit hook file is not executable at $hook_file"
        return 1
    fi
    log "Pre-commit hook installed and executable."
    
    # Verify MCP server dependency installation was attempted
    if ! echo "$install_output" | grep -q "Installing Internal MCP Commit Server dependencies"; then
        error "MCP server dependency installation step was not logged"
        return 1
    fi
    
    # Verify it handled npm presence (or lack thereof) gracefully 
    # Check for either success message or warning about npm missing
    if ! echo "$install_output" | grep -q "Internal MCP Commit Server dependencies installed." && ! echo "$install_output" | grep -q "npm not found"; then
       error "MCP server dependency installation did not log expected success or npm warning message"
       return 1
    fi
    
    log "Clean installation test passed"
    return 0
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
    
    local install_script="$(cd "$(dirname "$0")/.." && pwd)/install.sh"
    if [[ ! -f "$install_script" ]]; then
        error "Installation script not found at $install_script"
        return 1
    fi
    
    if ! bash "$install_script" --dir "$TEST_DIR" --backup; then
        error "Installation with backup failed"
        return 1
    fi
    
    # Verify backup
    local backup_pattern="$TEST_DIR/.cursor/rules.bak-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]"
    if ! ls -d $backup_pattern > /dev/null 2>&1; then
        error "Backup was not created"
        return 1
    fi
    
    # Verify custom rules preserved
    if [[ ! -f "$TEST_RULES_DIR/custom/user/user.mdc" ]]; then
        error "Custom rules were not preserved"
        return 1
    fi
    
    log "Backup and restore test passed"
    return 0
}

test_error_handling() {
    log "Testing error handling..."
    
    local install_script="$(cd "$(dirname "$0")/.." && pwd)/install.sh"
    if [[ ! -f "$install_script" ]]; then
        error "Installation script not found at $install_script"
        return 1
    fi
    
    # Test invalid directory
    if ! bash "$install_script" --dir "/nonexistent" 2>/dev/null; then
        log "OK: Failed on invalid directory as expected."
    else
        error "Installation should fail with invalid directory"
        return 1
    fi
    
    # Test installation with force option to an invalid GitHub repo (using the API)
    export REPO_URL="https://github.com/invalid-user/invalid-repo.git"
    export API_URL="https://api.github.com/repos/invalid-user/invalid-repo/commits/master"
    if ! bash "$install_script" --dir "$TEST_DIR" --force --use-curl 2>/dev/null; then
        log "OK: Failed on invalid repository (using curl) as expected."
    else
        error "Installation should fail with invalid repository (using curl)"
        return 1
    fi
    
    log "Error handling test passed"
    return 0
}

# Run tests
trap cleanup EXIT

log "Starting tests..."
setup

test_clean_install
test_backup_restore
test_error_handling

log "All tests passed successfully!" 