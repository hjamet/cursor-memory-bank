# Active Context

## Current implementation context

- **Task Group:** MCP Server Enhancements
- **Current Task:** 2.1 Add `send_terminal_input` MCP Tool
- **Goal:** Implement a new MCP tool in `server.js` to allow sending string input (followed by newline) to the standard input of a specified running terminal process managed by the MCP server.
- **Details:**
    - Define a new tool `send_terminal_input` with parameters: `pid` (integer), `input` (string), optional `timeout` (integer, e.g., 5 seconds).
    - The handler needs to locate the `child` process object associated with the `pid` (this likely requires modifying the `terminalStates` structure or a separate map to store `child` objects).
    - Write `input + '\n'` to `child.stdin`.
    - Implement logic to capture subsequent stdout/stderr and potentially the exit code if the input causes the process to finish within the `timeout` period.
    - Return a structure similar to `execute_command` (status, stdout, stderr, exit_code).
    - Handle potential errors: PID not found, `stdin` not writable, process already closed, timeout exceeded.
- **Files:** `.cursor/mcp/mcp-commit-server/server.js`
- **Dependencies:** Node.js `child_process`, modification of `terminalStates` or equivalent mapping.

## Current Status

- **Completed Task 1.4: Remove `[200~` Terminal Error Mentions.**
    - Searched rule files (`.cursor/rules/*.mdc`) for the obsolete warning.
    - Edited `consolidate-repo.mdc`, `context-update.mdc`, `experience-execution.mdc`, and `implementation.mdc` to remove the warning.
- Completed `consolidate-repo` rule execution.
- Completed Task 3.1: Modify `stop_terminal_command` to accept a list of PIDs.
- Tests for `tests/test_mcp_async_terminal.js` are passing.

## Recent Decisions

- Successfully removed obsolete terminal warnings from relevant rule files.
- Successfully diagnosed and fixed test failures related to previous MCP tool modifications.

## Next Steps

- Implement Task 2.1: Add `send_terminal_input` MCP Tool.
- Once Task 2.1 is implemented, create necessary tests.
- Proceed according to the `implementation` rule workflow.

## Important Notes

- The implementation of `send_terminal_input` requires careful handling of the `child_process` object and its `stdin` stream.
- Need to decide how to store and retrieve the `child` object for the given PID.