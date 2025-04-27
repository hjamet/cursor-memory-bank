# ToDo
- [ ] **Investigate Python Output Capture**: Determine why stdout/stderr from Python processes are not captured by the MCP server on Windows, despite successful execution (exit code 0) and multiple implementation attempts (spawn, execa, shell options). Output capture works for non-Python commands like `echo`. (Status: Blocked - Environment Issue Suspected)

# In Progress

# Done
- [x] **Enhance `mcp_execute_command`**: Modify MCP server to return full stdout/stderr directly in the response if the command completes within the default timeout (e.g., 15s), avoiding the need for separate `get_terminal_output` calls for short commands.
- [x] **Add `cwd` to MCP Terminal Responses**: Modify MCP server tools (`execute_command`, `get_terminal_status`, `get_terminal_output`) to include the effective `cwd` (Current Working Directory) of the process in their responses.
- [x] Install `execa` library
- [x] Run `tests/test_mcp_async_terminal.js` to verify the fix (Fixed regression by implementing killProcess and reverting execa)
- [x] **Investigate MCP `find` command issue**: Determine why `find ./ -type f -name '*.md'` executed via `mcp_MyMCP_execute_command` with Git Bash returns empty stdout on this Windows system. (Fixed by explicit spawn `shell:false` + removing console logs)