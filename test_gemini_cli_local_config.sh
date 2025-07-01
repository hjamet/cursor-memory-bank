#!/bin/bash
echo "--- DEBUG: Script started ---"

# Test script for validating the local Gemini CLI configuration fix in install.sh

# --- Setup ---
# Source the main install script to get access to its functions
echo "--- DEBUG: Sourcing ./install.sh ---"
source ./install.sh
echo "--- DEBUG: Sourcing complete ---"

# --- Test Environment ---
TEST_DIR="test_gemini_local_config_env"
GLOBAL_GEMINI_DIR="$HOME/.gemini"
GLOBAL_SETTINGS_FILE="$GLOBAL_GEMINI_DIR/settings.json"
FAKE_GLOBAL_CONTENT='{"apiKey": "global_api_key_should_not_be_touched"}'

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper Functions ---
assert_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}SUCCESS: $1${NC}"
    else
        echo -e "${RED}FAILURE: $1${NC}"
        cleanup
        exit 1
    fi
}

assert_failure() {
    if [ $? -ne 0 ]; then
        echo -e "${GREEN}SUCCESS (expected failure): $1${NC}"
    else
        echo -e "${RED}FAILURE (unexpected success): $1${NC}"
        cleanup
        exit 1
    fi
}

cleanup() {
    echo "--- Cleaning up test environment ---"
    rm -rf "$TEST_DIR"
    # Restore original global config if it existed, otherwise remove our fake one
    if [ -n "$BACKUP_GLOBAL_CONFIG" ]; then
        mv "$GLOBAL_SETTINGS_FILE.bak" "$GLOBAL_SETTINGS_FILE"
    else
        rm -f "$GLOBAL_SETTINGS_FILE"
        rmdir "$GLOBAL_GEMINI_DIR" 2>/dev/null
    fi
    echo "Cleanup complete."
}

# --- Main Test Logic ---
echo "--- Starting Test: Gemini CLI Local Configuration ---"

# 1. Prepare environment
cleanup > /dev/null 2>&1 # Clean up any previous failed runs
mkdir -p "$TEST_DIR"
assert_success "Created test directory: $TEST_DIR"

# Create dummy server scripts required by the function
touch "$TEST_DIR/server.js"
touch "$TEST_DIR/memory_bank_mcp.js"
assert_success "Created dummy MCP server scripts"

# 2. Prepare fake global configuration to test non-destruction
if [ -f "$GLOBAL_SETTINGS_FILE" ]; then
    mv "$GLOBAL_SETTINGS_FILE" "$GLOBAL_SETTINGS_FILE.bak"
    BACKUP_GLOBAL_CONFIG=true
fi
mkdir -p "$GLOBAL_GEMINI_DIR"
echo "$FAKE_GLOBAL_CONTENT" > "$GLOBAL_SETTINGS_FILE"
assert_success "Created fake global settings file to ensure it's not modified"

# 3. Run the function to be tested
echo "--- Calling configure_gemini_cli_mcp() ---"
configure_gemini_cli_mcp "$TEST_DIR" "./server.js" "./memory_bank_mcp.js"
assert_success "configure_gemini_cli_mcp() executed without script errors"
echo "---------------------------------------------"

# 4. Verify results
LOCAL_SETTINGS_FILE="$TEST_DIR/.gemini/settings.json"

# 4.1. Check that the local settings file was created
if [ -f "$LOCAL_SETTINGS_FILE" ]; then
    echo -e "${GREEN}SUCCESS: Local settings file was created at $LOCAL_SETTINGS_FILE${NC}"
else
    echo -e "${RED}FAILURE: Local settings file was NOT created.${NC}"
    cleanup
    exit 1
fi

# 4.2. Check that the local settings file contains MCP configuration
if grep -q '"mcpServers"' "$LOCAL_SETTINGS_FILE" && grep -q '"MyMCP"' "$LOCAL_SETTINGS_FILE" && grep -q '"MemoryBankMCP"' "$LOCAL_SETTINGS_FILE"; then
    echo -e "${GREEN}SUCCESS: Local settings file contains the correct MCP server configuration.${NC}"
else
    echo -e "${RED}FAILURE: Local settings file does NOT contain expected MCP configuration.${NC}"
    cleanup
    exit 1
fi

# 4.3. Check that the global settings file was NOT modified
if [ "$(cat "$GLOBAL_SETTINGS_FILE")" == "$FAKE_GLOBAL_CONTENT" ]; then
    echo -e "${GREEN}SUCCESS: Global settings file was not modified.${NC}"
else
    echo -e "${RED}FAILURE: Global settings file was MODIFIED!${NC}"
    echo "Expected content: $FAKE_GLOBAL_CONTENT"
    echo "Actual content: $(cat "$GLOBAL_SETTINGS_FILE")"
    cleanup
    exit 1
fi

# 4.4. Check if local settings file is valid JSON
if command -v jq >/dev/null 2>&1; then
    if jq -e . "$LOCAL_SETTINGS_FILE" > /dev/null; then
        echo -e "${GREEN}SUCCESS: Local settings file is valid JSON.${NC}"
    else
        echo -e "${RED}FAILURE: Local settings file is NOT valid JSON.${NC}"
        cleanup
        exit 1
    fi
else
    echo "Skipping JSON validation: jq is not installed."
fi


# --- Final Cleanup ---
cleanup
echo "--- All tests passed successfully! ---"
exit 0 