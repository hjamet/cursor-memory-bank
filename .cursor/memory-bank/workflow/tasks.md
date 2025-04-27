# ToDo

# In Progress


# Done

## 1. Refactor MCP Command Server

1.1. [x] **Create Directory Structure and Files**
    - Description: Create the necessary directories (`.cursor/mcp/mcp-commit-server/mcp_tools`, `.cursor/mcp/mcp-commit-server/lib`) and empty JavaScript files (using ESM syntax) as outlined in the analysis tree.
    - Files:
        - `.cursor/mcp/mcp-commit-server/mcp_tools/commit.js`
        - `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_execution.js`
        - `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_status.js`
        - `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_output.js`
        - `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_stop.js`
        - `.cursor/mcp/mcp-commit-server/lib/state_manager.js`
        - `.cursor/mcp/mcp-commit-server/lib/process_manager.js`
        - `.cursor/mcp/mcp-commit-server/lib/logger.js`
    - Dependencies: None.
    - Validation: All specified directories and empty `.js` files exist.

1.2. [x] **Implement Library Modules**
    - Description: Implement the core logic for managing state, processes, and logging.
        - `state_manager.js`: Move logic for reading/writing `terminals_status.json` from `server.js`. Export functions like `loadState`, `writeState`, `findState`, `updateState`, `removeState`.
        - `logger.js`: Move logic for writing to log files in `./logs/` from `server.js`. Export functions for logging stdout/stderr, potentially handling log rotation or cleanup.
        - `process_manager.js`: Implement robust process spawning using `child_process.spawn`. Focus on reliable stdout/stderr capture (accumulating data, handling `close`/`exit`/`error` events, potentially using Promises). Export functions like `spawnProcess`, `killProcess`.
    - Files: `lib/state_manager.js`, `lib/logger.js`, `lib/process_manager.js`, `server.js` (for source code).
    - Dependencies: Task 1.1.
    - Validation: Modules export the required functions. Process manager handles basic spawning and event listening.

1.3. [x] **Implement MCP Tool Modules**
    - Description: Move the implementation logic for each MCP tool from the monolithic `server.js` into its corresponding module file. Ensure each module imports necessary functions from the `lib` modules and correctly implements the tool logic while adhering *exactly* to the existing MCP tool signature (parameters, return format).
    - Files: `mcp_tools/commit.js`, `mcp_tools/terminal_execution.js`, `mcp_tools/terminal_status.js`, `mcp_tools/terminal_output.js`, `mcp_tools/terminal_stop.js`, `server.js` (for source code), `lib/*` (for imports).
    - Dependencies: Task 1.1, Task 1.2.
    - Validation: Each tool module exports a handler function. Logic is moved from `server.js`.

1.4. [x] **Refactor Main Server Entry Point**
    - Description: Modify the main `server.js` file to import the tool handlers from the `mcp_tools/` directory and register them with the `McpServer` instance. Remove the now-extracted logic for tools, state management, logging, and process handling. Keep server setup, transport connection, and tool registration logic.
    - Files: `server.js`, `mcp_tools/*` (for imports).
    - Dependencies: Task 1.1, Task 1.2, Task 1.3.
    - Validation: `server.js` is significantly smaller, imports tool handlers, and registers them correctly.

## 2. Verification

2.1. [x] **Run Existing Tests**
    - Description: Execute the existing test suite (`tests/test_mcp_async_terminal.js`) using `run_terminal_cmd` (e.g., `node tests/test_mcp_async_terminal.js`). Ensure all tests pass with the refactored server implementation.
    - Files: `tests/test_mcp_async_terminal.js`, all files from section 1.
    - Dependencies: Section 1 (all tasks).
    - Validation: Test suite executes and reports all tests passed.