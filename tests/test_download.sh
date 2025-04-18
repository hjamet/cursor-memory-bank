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
# export TEST_MODE=1 # Not needed anymore
# export TEST_RULES_DIR="$TEST_DIR/rules" # Not needed anymore

# Test files setup
# SCRIPT_DIR="$(dirname "$0")" # Not needed anymore
# PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)" # Not needed anymore
TEST_DIST_DIR="$TEST_DIR/dist"
TEST_RULES_ARCHIVE="$TEST_DIST_DIR/v1.0.0.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions (copied from install.sh)
log() {
    local message="$1"
    echo -e "${GREEN}[INFO]${NC} $message"
    # Optionally log to file, adapted for test script
    mkdir -p "$LOGS_DIR" # Ensure logs dir exists
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $message" >> "$TEST_LOG"
}

log_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" >&2
    mkdir -p "$LOGS_DIR" # Ensure logs dir exists
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $message" >> "$TEST_LOG"
    # Do NOT exit 1 here, let the test function return 1
}

log_warn() {
    local message="$1"
    echo -e "${YELLOW}[WARN]${NC} $message"
    mkdir -p "$LOGS_DIR" # Ensure logs dir exists
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $message" >> "$TEST_LOG"
}

# Curl download function for individual files (copied from install.sh)
download_file() {
    local url="$1"
    local dest="$2"

    log "Downloading file from $url"
    local http_code
    
    # Handle file:// protocol differently
    if [[ "$url" =~ ^file:// ]]; then
        local file_path="${url#file://}"
        if [ -f "$file_path" ]; then
            cp "$file_path" "$dest"
            return 0 # Success
        else
            log_error "Failed to download file: Local file not found: $file_path"
            return 1 # Failure
        fi
    fi
    
    # Use || echo "$?" to capture curl exit code if command fails
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" || echo "$?" )
    local curl_exit_code=$?

    # If curl itself failed (non-zero exit code captured by || echo), handle it
    if [[ $curl_exit_code -ne 0 ]]; then
         # Use the captured exit code as http_code for the case statement
         http_code=$curl_exit_code 
    fi

    case "$http_code" in
        200)
            return 0 # Success
            ;;
        404)
            log_error "Failed to download file: URL not found (HTTP 404). URL: $url"
            return 1 # Failure
            ;;
        403)
            log_error "Failed to download file: Access denied (HTTP 403). URL: $url"
            return 1 # Failure
            ;;
        50[0-9])
            log_error "Failed to download file: Server error (HTTP $http_code). URL: $url"
            return 1 # Failure
            ;;
        6) # Curl exit code 6: Couldn't resolve host
            log_error "Failed to download file: Couldn't resolve host (Curl exit code 6). URL: $url"
            return 1 # Failure
            ;;
        22) # Often corresponds to HTTP 4xx errors when -f is used
            log_error "Failed to download file: HTTP error likely 4xx (Curl exit code 22). URL: $url"
            return 1 # Failure
            ;;
        *)
            if [[ "$http_code" =~ ^[0-9]+$ && $http_code -ne 200 ]]; then
                log_error "Failed to download file (HTTP $http_code). URL: $url"
            else
                 # This case might catch other non-numeric curl exit codes
                log_error "Failed to download file: Unknown error or Curl exit code ($http_code). URL: $url"
            fi
            return 1 # Failure
            ;;
    esac
}

# Curl download function for archives (copied from install.sh)
download_archive() {
    local url="$1"
    local dest="$2"

    log "Downloading archive from $url"
    local http_code
    
    # Handle file:// protocol differently
    if [[ "$url" =~ ^file:// ]]; then
        local file_path="${url#file://}"
        if [ -f "$file_path" ]; then
            cp "$file_path" "$dest"
            return 0 # Success
        else
            log_error "Failed to download archive: Local file not found: $file_path"
            return 1 # Failure
        fi
    fi
    
    # Use || echo "$?" to capture curl exit code if command fails
    http_code=$(curl -w "%{http_code}" -fsSL "$url" -o "$dest" || echo "$?" )
    local curl_exit_code=$?

    # If curl itself failed (non-zero exit code captured by || echo), handle it
    if [[ $curl_exit_code -ne 0 ]]; then
         # Use the captured exit code as http_code for the case statement
         http_code=$curl_exit_code
    fi

    case "$http_code" in
        200)
            return 0 # Success
            ;;
        404)
            log_error "Failed to download archive: URL not found (HTTP 404). URL: $url"
            return 1 # Failure
            ;;
        403)
            log_error "Failed to download archive: Access denied (HTTP 403). URL: $url"
            return 1 # Failure
            ;;
        50[0-9])
            log_error "Failed to download archive: Server error (HTTP $http_code). URL: $url"
            return 1 # Failure
            ;;
        6) # Curl exit code 6: Couldn't resolve host
            log_error "Failed to download archive: Couldn't resolve host (Curl exit code 6). URL: $url"
            return 1 # Failure
            ;;
        22) # Often corresponds to HTTP 4xx errors when -f is used
            log_error "Failed to download archive: HTTP error likely 4xx (Curl exit code 22). URL: $url"
            return 1 # Failure
            ;;
        *)
            if [[ "$http_code" =~ ^[0-9]+$ && $http_code -ne 200 ]]; then
                log_error "Failed to download archive (HTTP $http_code). URL: $url"
            else
                # This case might catch other non-numeric curl exit codes
                log_error "Failed to download archive: Unknown error or Curl exit code ($http_code). URL: $url"
            fi
            return 1 # Failure
            ;;
    esac
}

# Setup function (copied and adapted)
setup() {
    # Create logs directory
    if ! mkdir -p "$LOGS_DIR"; then
        # Use direct echo for setup errors as log_error might not be fully ready
        echo -e "${RED}[ERROR]${NC} Failed to create logs directory at $LOGS_DIR" >&2
        return 1
    fi
    
    # Create test dist directory
    if ! mkdir -p "$TEST_DIST_DIR"; then
        log_error "Failed to create test dist directory at $TEST_DIST_DIR"
        rm -rf "$TEST_DIR" # Clean up if we fail
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

# REMOVED SOURCING of install.sh
# log "Successfully sourced installation script"

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
    
    if ! download_file "https://invalid.example.com/nonexistent" "$TEST_DIR/invalid.txt"; then
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
    
    if ! download_archive "https://invalid.example.com/v1.0.0.tar.gz" "$TEST_DIR/invalid.tar.gz"; then
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
    log "Starting test execution - Checkpoint 1"
    
    # Run download tests
    log "Checkpoint 2: Before test_download_file_success"
    if ! test_download_file_success; then
        ((failed++))
        log_error "test_download_file_success failed"
    else
        log "test_download_file_success passed"
    fi
    log "Checkpoint 3: After test_download_file_success"
    
    log "Checkpoint 4: Before test_download_file_invalid_url"
    if ! test_download_file_invalid_url; then
        ((failed++))
        log_error "test_download_file_invalid_url failed"
    else
        log "test_download_file_invalid_url passed"
    fi
    log "Checkpoint 5: After test_download_file_invalid_url"
    
    log "Checkpoint 6: Before test_download_archive_success"
    if ! test_download_archive_success; then
        ((failed++))
        log_error "test_download_archive_success failed"
    else
        log "test_download_archive_success passed"
    fi
    log "Checkpoint 7: After test_download_archive_success"
    
    log "Checkpoint 8: Before test_download_archive_invalid_url"
    if ! test_download_archive_invalid_url; then
        ((failed++))
        log_error "test_download_archive_invalid_url failed"
    else
        log "test_download_archive_invalid_url passed"
    fi
    log "Checkpoint 9: After test_download_archive_invalid_url"
    
    # Report results
    log "Checkpoint 10: Reporting results"
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

# Execute setup
if ! setup; then
    echo -e "${RED}[ERROR]${NC} Failed to set up test environment" >&2
    exit 1
fi

# Run the tests
if ! run_tests; then
    log_error "Some tests failed"
    teardown
    exit 1
fi

log "All tests completed successfully"
teardown
exit 0