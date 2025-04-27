# Active Context

## Current implementation context

- **Task Group:** Rule Enhancements (MCP Cleanup)
- **Current Tasks:**
    - 1.1 Add MCP Cleanup Step to `consolidate-repo` rule.
    - 1.2 Add Cleanup Note to `experience-execution` rule.
    - 1.3 Add Cleanup Note to `fix` rule.
- **Goal:** Enhance MCP terminal process cleanup by adding a dedicated step in `consolidate-repo` and reminder notes in other rules.
- **Details (Task 1.1):** Modify `consolidate-repo.mdc` Instructions to include a step calling `mcp_get_terminal_status` and then `mcp_stop_terminal_command` for finished terminals.
- **Details (Task 1.2 & 1.3):** Add a reminder sentence about using `mcp_stop_terminal_command` proactively to the Specifics section of `experience-execution.mdc` and `fix.mdc`.
- **Dependencies:** MCP tools (`mcp_get_terminal_status`, `mcp_stop_terminal_command`).

## Current Status

- Completed `consolidate-repo` rule execution: processed `userbrief.md`, verified file integrity, cleaned up MCP terminals, updated `.gitignore`.
- **Completed Task: Modify `stop_terminal_command` to accept a list of PIDs.**
    - Modified Zod schema and handler in `server.js`.
    - Added try/catch around tool registration and stream creation.
    - Updated test script (`tests/test_mcp_async_terminal.js`) to handle array arguments and parse results correctly.
- **Tests for `tests/test_mcp_async_terminal.js` now passing.**

## Recent Decisions

- Successfully diagnosed and fixed test failures related to MCP tool implementation and test script parsing.
- Added error handling to MCP server for robustness.

## Next Steps

- Process remaining tasks from `userbrief.md` / `tasks.md`.
- Current `userbrief.md` contains new requests added by the user:
    - Modify `context-update` rule to use MCP `commit` tool.
    - Add new MCP tool for sending input to a terminal.
- Proceed to `consolidate-repo` to process the new `userbrief.md` items.

## Important Notes

- Ensure the new step in `consolidate-repo.mdc` is placed appropriately within the existing instructions (e.g., after integrity verification, before evaluation).

## Lost workflow

- *This section is no longer relevant after successfully resuming the workflow via consolidate-repo.*

## MCP Tool Enhancement

- **Current Task:** Modify `mcp_MyMCP_stop_terminal_command` to accept a list of PIDs.
- **Goal:** Allow stopping multiple terminal processes with a single tool call.
- **Details:**
    - Modify the Zod schema for `stop_terminal_command` in `server.js` to accept `z.array(z.number().int())` for the `pid` parameter (renaming it to `pids` for clarity).
    - Update the handler function logic to iterate over the `pids` array.
    - For each PID, perform the existing stop/cleanup logic.
    - Collect results (status, stdout, stderr) for each PID and return them, perhaps as an array of result objects.
- **Files:** `.cursor/mcp/mcp-commit-server/server.js`
- **Dependencies:** Zod library, Node.js `child_process`, `fs`.
- **Considerations:** Error handling for individual PIDs (e.g., if one PID is not found or fails to stop). Return format for multiple results.

## MCP Test Failure Diagnosis

- **Current Task:** Add error handling to `server.tool()` registrations in `server.js` to diagnose test failure.
- **Goal:** Identify the root cause of the immediate exit (code 1, no output) of `tests/test_mcp_async_terminal.js` after modifications to `stop_terminal_command`.
- **Details:**
    - Wrap the `server.tool('stop_terminal_command', ...)` definition and potentially others in `server.js` with `try...catch` blocks.
    - Log any caught errors to `console.error` to make them visible, potentially allowing the server to start or providing diagnostic output.
- **Files:** `.cursor/mcp/mcp-commit-server/server.js`
- **Dependencies:** Node.js error handling.
- **Considerations:** Ensure error logging provides enough detail. Decide if only `stop_terminal_command` or all `server.tool` calls should be wrapped initially.