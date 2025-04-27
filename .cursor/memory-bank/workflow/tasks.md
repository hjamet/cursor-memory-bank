# ToDo

## 1. Debug MCP Server & Test Environment

1.1. [ ] **Diagnose MCP Server Accessibility**: Investigate why the MCP server (`server.js`) running via `node` is not accessible on `http://localhost:8888` or via STDIN/STDOUT communication from test scripts.
    - Description: Check server logs for startup errors. Verify the transport mechanism used (StdioServerTransport vs an HTTP one). Ensure no firewall/proxy interference. Attempt manual interaction if possible.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`, `.cursor/mcp.json`
    - Dependencies: Understanding of Node.js execution, MCP transports, local network configuration.
    - Validation: Successful manual connection to the running server (e.g., via `curl` if HTTP, or a simple Node.js client if STDIN/STDOUT).

1.2. [ ] **Fix `test_mcp_send_input` Execution**: Based on the diagnosis (Task 1.1), modify `tests/test_mcp_send_input.js` to correctly communicate with the MCP server (likely via STDIN/STDOUT) and validate the `send_terminal_input` tool.
    - Description: Refactor the test script to spawn `server.js`, write JSON requests to its stdin, parse JSON responses from its stdout (handling buffering/newlines), and execute the test logic (start `cat`, send input, check output, stop `cat`). Remove the unused bash script.
    - Files: `tests/test_mcp_send_input.js`, `.cursor/mcp/mcp-commit-server/server.js` (for reference)
    - Dependencies: Task 1.1, `child_process`, MCP JSON protocol.
    - Validation: Test script `tests/test_mcp_send_input.js` passes successfully.

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

1.1. [ ] **Add `send_terminal_input` MCP Tool**: Implement and **validate** a new tool in the MCP server (`server.js`) to send input to a running terminal process. **(Implementation added, Needs Test Validation)**
    - Description: Define a new tool `send_terminal_input`. Handler finds child process, writes input + `\n` to stdin. Validation requires successful execution of the corresponding test (Task 1.2).
    - Files: `.cursor/mcp/mcp-commit-server/server.js`, `tests/test_mcp_send_input.js`
    - Dependencies: Node.js `child_process`, Task 1.2.
    - Validation: `tests/test_mcp_send_input.js` passes.

# Done

## 1. Rule Modifications (Current Cycle)

1.1. [x] **Update `