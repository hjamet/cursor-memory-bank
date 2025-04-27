# ToDo


# Done
- [x] **Fix MCP Stdout/Stderr Capture**: Resolve the issue where stdout and stderr are not consistently captured for commands executed via `mcp_MyMCP_execute_command` on Windows (using Git Bash). **Solution**: Always execute via `bash -c \"eval $(echo '<base64_command>' | base64 -d)\"` on Windows.
    - *Description*: Output is sometimes missing or incomplete despite the command executing. Investigate buffering, shell interactions, stream closing logic, and the user's suggestion of directly invoking Git Bash (`C:\\Program Files\\Git\\bin\\bash.exe -c \"...\"`).
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, potentially `.cursor/mcp/mcp-commit-server/lib/logger.js`.
    - *Dependencies*: None.
    - *Validation Criteria*: Running test commands like `python -u -c \"import sys; print('stdout test'); print('stderr test', file=sys.stderr)\"`, `cmd /c \"echo cmd_stdout && echo cmd_stderr >&2\"`, and `git status` via `mcp_MyMCP_execute_command` successfully captures both stdout and stderr, verified using `mcp_MyMCP_get_terminal_output`.
- [x] **Investigate Python Output Capture**: Verified that Python stdout/stderr/exit_code are correctly captured by the current implementation (universal Git Bash execution). (Previously Task 2.1)
- [x] **Enhance `mcp_execute_command`**: Implemented immediate return of full results (stdout/stderr/exit_code) if command finishes before timeout. (Previously Task 3.1)
- [x] **Implement Immediate Return for `execute_command`**: Modified MCP server (`terminal_execution.js`, `process_manager.js`, `server.js`) so `execute_command` waits for completion up to a timeout (default 10s). If completed early, returns full result (stdout/stderr/exit_code); otherwise, returns PID for background execution. (From userbrief.md)
- [x] **Add `cwd` to MCP Terminal Responses**: Modify MCP server tools (`execute_command`, `get_terminal_status`, `get_terminal_output`) to include the effective `cwd` (Current Working Directory) of the process in their responses.
- [x] Install `execa` library
- [x] Run `tests/test_mcp_async_terminal.js` to verify the fix (Fixed regression by implementing killProcess and reverting execa)
- [x] **Investigate MCP `find` command issue**: Determine why `find ./ -type f -name \\'*.md\\'` executed via `mcp_MyMCP_execute_command` with Git Bash returns empty stdout on this Windows system. (Fixed by explicit spawn `shell:false` + removing console logs)