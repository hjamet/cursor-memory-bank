# Active Context

## Current implementation context

- **Objective**: Resolve issues with async terminal MCP tools.
- **Last Task**: Fixed regression in `tests/test_mcp_async_terminal.js` caused by failed `execa` refactoring.
- **Actions Taken**:
    - Attempted refactor of `process_manager.js` to use `execa` failed due to test timeouts/incompatibility.
    - Reverted `process_manager.js` to use `child_process.spawn`.
    - Modified `tests/test_mcp_async_terminal.js` commands to use `node -e "process.exit()"` for reliability.
    - Identified and fixed missing `killProcess` implementation in `process_manager.js`.
- **Files/Symbols involved**: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, `tests/test_mcp_async_terminal.js`, `.cursor/memory-bank/workflow/tests.md`, `.cursor/memory-bank/workflow/tasks.md`.
- **Current State**: Tests related to async terminal pass. Refactoring task (`execa`) abandoned for now.
- **Next Step**: Update tasks.md and commit changes.

## Current Status

- Workflow started, `context-loading`, `request-analysis`, and `task-decomposition` completed.
- Ready to begin implementation based on tasks in `tasks.md` (Section 1).

## Recent Decisions

- Confirmed use of ES Modules (ESM) for the refactored code based on existing `server.js` and Node.js best practices.
- Prioritize reliable output capture in `process_manager.js` by handling stream events correctly.

## Next Steps

- Implement tasks from Section 1 of `tasks.md`, starting with 1.1 (Create Directory Structure and Files).

## Important Notes

- Adhere strictly to existing MCP tool signatures.
- Use `run_terminal_cmd` (not the MCP tool) for running tests (`tests/test_mcp_async_terminal.js`) until refactoring is complete and verified.

## Task List Context
- **Reference File:** `.cursor/memory-bank/workflow/tasks.md` (Section 1 & 2)

## Code Implementation Context
- **Files to Create/Modify:** See "Files/Modules Involved" above.
- **Key Functions/Classes:** `McpServer` (from `@modelcontextprotocol/sdk`), `spawn` (from `node:child_process`), `fs` module functions, ESM `import`/`export`.

## Test Context
- **Last Test Execution:** N/A for this task.
- **Relevant Tests:** `tests/test_mcp_async_terminal.js` (to be run in Task 2.1).

## Documentation Context
- **Relevant Files:** Node.js `child_process` documentation.
- **Key Concepts:** MCP Server, Node.js Streams, ESM Modules, Asynchronous Programming.