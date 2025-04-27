# Active Context

## Current Goal
Implement Task 1: Enhance `mcp_execute_command` to return full stdout/stderr directly if command finishes within timeout.

## Current implementation context
- **Task**: Enhance `mcp_execute_command` for immediate output.
- **Requirement**: Modify the `execute_command` MCP tool handler (`terminal_execution.js`) so that if the spawned command finishes (successfully or with failure) before the specified `timeout` parameter expires, the handler waits for the process to complete, reads the final stdout/stderr logs, and returns these directly in the initial response, along with the final exit code and status. If the timeout *is* reached before completion, it should return the current status (likely 'Running') and null exit code as it does now, letting the user poll later.
- **Implementation Plan**:
    1.  Modify `handleExecuteCommand` in `terminal_execution.js`.
    2.  After calling `ProcessManager.spawnProcess`, instead of returning immediately, start a loop or use a promise-based mechanism to wait for the process associated with the returned `pid` to complete *or* for the `timeout` (provided as an argument to the tool) to expire.
    3.  Inside the loop/wait:
        - Periodically check the process state using `StateManager.findStateByPid(pid)`.
        - If state shows `status` is 'Success' or 'Failure', break the loop/resolve the promise.
        - If `Date.now()` exceeds `startTime + (timeout * 1000)`, break/resolve.
        - Use a small delay (e.g., `await new Promise(res => setTimeout(res, 100))`) between checks.
    4.  After the loop/wait finishes:
        - Check if the process completed (status is Success/Failure).
        - If yes: 
            - Retrieve the final state (`exit_code`, `status`, `cwd`, log paths) from `StateManager`.
            - Read the full stdout/stderr logs using `Logger.readLogLines` (perhaps with a large line count or modified to read all lines).
            - Construct the response object including `pid`, `cwd`, final `exit_code`, final `status`, full `stdout`, and full `stderr`.
        - If no (timeout expired): 
            - Retrieve the current state (likely 'Running', null `exit_code`).
            - Construct the response object with `pid`, `cwd`, current `status`, null `exit_code`, and empty/null `stdout`/`stderr` (as it does currently).
    5.  Return the constructed response.
- **Considerations**:
    - Need to handle potential errors during state/log retrieval carefully.
    - The `timeout` parameter in `execute_command` becomes significant.
    - This changes the tool's behavior: it might block for up to `timeout` seconds waiting for completion.

## Key Files Involved
- `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_execution.js`
- `.cursor/mcp/mcp-commit-server/lib/process_manager.js` (May need inspection, but perhaps no changes)
- `.cursor/mcp/mcp-commit-server/lib/state_manager.js` 
- `.cursor/mcp/mcp-commit-server/lib/logger.js` (May need modification for reading full logs)
- `.cursor/memory-bank/context/activeContext.md`
- `.cursor/memory-bank/workflow/tasks.md`

## Next Steps
- Implement the waiting logic and conditional response construction in `handleExecuteCommand` (`terminal_execution.js`).
- Potentially adapt `Logger.readLogLines` to read full file content.