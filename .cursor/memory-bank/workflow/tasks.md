# ToDo

## 1. Debug MCP Server & Test Environment

1.1. [BLOCKED] **Diagnose MCP Server Accessibility / Stdio Communication**: Root cause identified as test script using HTTP instead of stdio. Test script `test_mcp_send_input.js` refactored for stdio.
    - Description: Test script needs verification, but blocked by MCP command execution output issues.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`, `tests/test_mcp_send_input.js`
    - Dependencies: MCP Tooling (`mcp_MyMCP_execute_command` output capture).
    - Validation: Requires seeing output from `node ./tests/test_mcp_send_input.js`.

1.2. [BLOCKED] **Fix `test_mcp_send_input` Execution**: Script refactored for stdio communication, `uuid` dependency removed. CWD issue in server potentially fixed.
    - Description: Further debugging requires visibility into test script output via `mcp_MyMCP_execute_command`.
    - Files: `tests/test_mcp_send_input.js`, `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: Task 1.1, MCP Tooling (`mcp_MyMCP_execute_command` output capture).
    - Validation: Test script `tests/test_mcp_send_input.js` passes successfully (Requires visible output).

1.3. [ ] **Delete Obsolete Test Script**: Remove the unused bash script `tests/test_mcp_send_input.sh`.
    - Description: Use the appropriate tool/command to delete the file.
    - Files: `tests/test_mcp_send_input.sh`
    - Dependencies: None.
    - Validation: File is successfully deleted.

## 2. General Rule Improvement

2.1. [ ] **Ensure Rules Use MCP Tools**: Review all rule files (`.cursor/rules/*.mdc`) to confirm they exclusively recommend and use MCP tools (`mcp_MyMCP_*`) for terminal commands, replacing any remaining references to `run_terminal_cmd`.
    - Description: Grep/search through all `.mdc` files for `run_terminal_cmd`. Verify rules like `context-update` (mentioned in userbrief) and others use the correct MCP tools in instructions and examples. Update where necessary.
    - Files: `.cursor/rules/*.mdc` (Potentially all rule files)
    - Dependencies: MCP Terminal Tools (`mcp_MyMCP_execute_command`, etc.).
    - Validation: All rules consistently use MCP tools for command execution examples/instructions.

# In Progress

## 1. Rule Modifications

## 2. MCP Server Enhancements

1.1. [BLOCKED] **Add `send_terminal_input` MCP Tool**: Implementation added to `server.js`, `uuid` dependency removed. CWD possibly fixed. **Needs Test Validation.**
    - Description: Validation blocked by inability to run/debug test script `tests/test_mcp_send_input.js` due to MCP command execution output issues.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`, `tests/test_mcp_send_input.js`
    - Dependencies: Tasks 1.1, 1.2, MCP Tooling.
    - Validation: `tests/test_mcp_send_input.js` passes (Requires visible output).

# Done

## 1. Rule Modifications (Current Cycle)

1.1. [x] **Update `