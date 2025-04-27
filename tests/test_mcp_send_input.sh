#!/bin/bash

# tests/test_mcp_send_input.sh

# Function to generate UUID (using PowerShell for Windows compatibility)
uuidgen_alt() {
    powershell -Command "[guid]::NewGuid().ToString()" | tr -d '\r'
}

# Configuration
MCP_SERVER_URL="${MCP_SERVER_URL:-http://localhost:8888}"
TEST_ID=$(uuidgen_alt | cut -c1-8)

# Temporary file for JSON payloads
# Adding PID to temp file name to avoid potential collisions if run in parallel (though unlikely here)
TEMP_JSON="mcp_request_temp_${TEST_ID}_$$.json"

# Variables for test state
TARGET_PID=""
FINAL_STATUS="FAIL"

# --- Helper Functions ---

# Function to generate MCP JSON request
# $1: Tool Name
# $2: Tool Arguments (JSON string)
mcp_json() {
    local tool_name="$1"
    local tool_args_json="$2"
    local request_id=$(uuidgen_alt)

    cat <<EOF
{
  "mcp_version": "1.0",
  "request_id": "${request_id}",
  "tool_name": "${tool_name}",
  "tool_arguments": ${tool_args_json}
}
EOF
}

# Function to call MCP tool via curl
# $1: Tool Name
# $2: Tool Arguments (JSON string)
call_mcp_tool() {
    local tool_name="$1"
    local tool_args_json="$2"
    local response

    # Create JSON payload
    mcp_json "${tool_name}" "${tool_args_json}" > "${TEMP_JSON}"
    if [ $? -ne 0 ]; then
        echo "[Error] Failed to write temp JSON file ${TEMP_JSON}" >&2
        return 1
    fi

    echo "[MCP Call] curl ... -d @${TEMP_JSON} ... (Tool: ${tool_name})"
    # Execute curl
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "@${TEMP_JSON}" "${MCP_SERVER_URL}")
    local curl_exit_code=$?

    # Clean up temp file immediately
    rm -f "${TEMP_JSON}"

    if [ ${curl_exit_code} -ne 0 ]; then
        echo "[Error] curl command failed with exit code ${curl_exit_code} for tool ${tool_name}" >&2
        return 1
    fi

    echo "[MCP Resp] Raw: ${response}"

    # Basic validation of response (check for error field, check for content)
    # Using jq for robust parsing
    if ! command -v jq &> /dev/null; then
        echo "[Warning] jq command not found. Skipping robust JSON validation." >&2
        # Simple string check for error (less reliable)
        if [[ "${response}" == *'"error"'* ]]; then
             echo "[Error] MCP response contains an error field (jq not found): ${response}" >&2
             return 1
        fi
        if [[ "${response}" != *'"content"'* ]] || [[ "${response}" != *'"type\": \"text\"'* ]]; then
            echo "[Error] MCP response format unexpected (jq not found): ${response}" >&2
            return 1
        fi
    else
        # Use jq
        if echo "${response}" | jq -e '.error' > /dev/null; then
            local error_msg=$(echo "${response}" | jq -r '.error.message // "Unknown MCP Error"')
            echo "[Error] MCP response contains error: ${error_msg}" >&2
            return 1
        fi
         if ! echo "${response}" | jq -e '.content[0].type == "text"' > /dev/null; then
             echo "[Error] MCP response format unexpected: ${response}" >&2
             return 1
         fi
    fi

    # Return the full JSON response for further processing
    echo "${response}"
    return 0
}

# Function to extract text content from MCP response
# $1: MCP Response JSON string
get_mcp_text_content() {
    local response_json="$1"
    if command -v jq &> /dev/null; then
        echo "${response_json}" | jq -r '.content[0].text'
    else
        echo "[Warning] jq not found. Cannot extract text content precisely." >&2
        # Attempt basic extraction (highly fragile)
        echo "${response_json}" | sed -n 's/.*"text": \"\(.*\)\"}.*/\1/p'
    fi
}

# --- Test Steps ---

echo "[Test Start] test_mcp_send_input.sh - ID: ${TEST_ID}"

# Trap errors and cleanup
trap 'echo "[Error] Test failed at line $LINENO"; FINAL_STATUS="FAIL"; exit 1' ERR
trap ' [ -n "${TARGET_PID}" ] && echo "[Cleanup] Stopping PID ${TARGET_PID}..." && call_mcp_tool "stop_terminal_command" "{ \"pids\": [${TARGET_PID}], \"lines\": 5 }" > /dev/null; rm -f "${TEMP_JSON}"; echo "[Test End] test_mcp_send_input.sh - ID: ${TEST_ID} - Status: ${FINAL_STATUS}" ' EXIT

# 1. Start target command ('cat')
echo "[${TEST_ID}] Step 1: Starting target command ('cat')..."
TARGET_COMMAND='cat' # Assuming cat is in PATH for the server
EXEC_ARGS="{ \"command\": \"${TARGET_COMMAND}\", \"timeout\": 5 }"
EXEC_RESPONSE=$(call_mcp_tool "execute_command" "${EXEC_ARGS}")
EXEC_RESULT_TEXT=$(get_mcp_text_content "${EXEC_RESPONSE}")

TARGET_PID=$(echo "${EXEC_RESULT_TEXT}" | jq -r '.pid // empty')
EXEC_EXIT_CODE=$(echo "${EXEC_RESULT_TEXT}" | jq -r '.exit_code // "null"')

if [ -z "${TARGET_PID}" ]; then
    echo "[Error] Failed to get PID from execute_command. Response: ${EXEC_RESULT_TEXT}" >&2
    exit 1
fi
echo "[${TEST_ID}] Step 1: Target command started with PID: ${TARGET_PID}. Initial exit_code=${EXEC_EXIT_CODE}"
if [ "${EXEC_EXIT_CODE}" != "null" ]; then
    echo "[Error] 'cat' command exited immediately with code ${EXEC_EXIT_CODE}. Stderr might be in server logs." >&2
    exit 1
fi

sleep 1 # Wait briefly

# 2. Send input line
INPUT_LINE="Test line from ${TEST_ID}"
echo "[${TEST_ID}] Step 2: Sending input ('${INPUT_LINE}')..."
SEND_ARGS="{ \"pid\": ${TARGET_PID}, \"input\": \"${INPUT_LINE}\" }"
SEND_RESPONSE=$(call_mcp_tool "send_terminal_input" "${SEND_ARGS}")
SEND_RESULT_TEXT=$(get_mcp_text_content "${SEND_RESPONSE}")
echo "[${TEST_ID}] Step 2: Response: ${SEND_RESULT_TEXT}"
if [[ "${SEND_RESULT_TEXT}" != *"Input sent to PID"* ]]; then
    echo "[Error] send_terminal_input did not confirm sending. Response: ${SEND_RESULT_TEXT}" >&2
    exit 1
fi

sleep 1.5 # Wait for cat to process/echo

# 3. Check output
echo "[${TEST_ID}] Step 3: Checking output..."
GET_OUTPUT_ARGS="{ \"pid\": ${TARGET_PID}, \"lines\": 20 }"
OUTPUT_RESPONSE=$(call_mcp_tool "get_terminal_output" "${GET_OUTPUT_ARGS}")
OUTPUT_RESULT_TEXT=$(get_mcp_text_content "${OUTPUT_RESPONSE}")

COMBINED_OUTPUT=$(echo "${OUTPUT_RESULT_TEXT}" | jq -r '.stdout // empty')
echo "[${TEST_ID}] Step 3: Combined output: ${COMBINED_OUTPUT}" # Use jq -r for raw string

# Check if the sent line appears in the output
if [[ "${COMBINED_OUTPUT}" != *"${INPUT_LINE}"* ]]; then
    echo "[Error] Expected output to contain '${INPUT_LINE}', but got: '${COMBINED_OUTPUT}'" >&2
    exit 1
fi
echo "[${TEST_ID}] Step 3: Input line found in output successfully."

FINAL_STATUS="PASS"
echo "[Success] Test steps completed successfully."

# Cleanup is handled by EXIT trap
exit 0 