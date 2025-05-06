# TO DO

### Priority Tasks


# IN PROGRESS
*No tasks currently in progress here.*

# DONE

2.  **Enhance MCP Server Testing**
    *   [x] **2.1 Create Python Helper Script for Interruption Test**
        *   **Description**: Create a simple Python script (e.g., `temp_python_script.py` at the project root or in `tests/mcp_server_tests/helper_scripts/`) that runs for a noticeable duration (e.g., sleeps, writes to a file periodically) and can indicate whether it terminated gracefully or was killed.
        *   **Impacted Files/Components**: `tests/mcp_server_tests/helper_scripts/temp_python_script.py` (New file).
        *   **Dependencies**: Task 1.1 (for location).
        *   **Validation**: Python script is created and functions as expected when run manually.
    *   [x] **2.2 Implement Python Script Execution/Interruption Test**
        *   **Description**: Create a new test script (e.g., `tests/mcp_server_tests/test_python_interrupt.js`) that uses the MCP server's `execute_command` to run the Python helper script and `stop_terminal_command` to terminate it. The test should verify that the Python script (and any child processes, if applicable) is properly terminated by `tree-kill`.
        *   **Impacted Files/Components**: `tests/mcp_server_tests/test_python_interrupt.js` (New file).
        *   **Dependencies**: Task 1.4 (for SDK setup), Task 2.1.
        *   **Validation**: The new test script successfully executes the Python script, stops it, and verifies termination of the entire process tree.
    *   [x] **2.3 Test Long Timeout Behavior (Valid Timeout)**
        *   **Description**: Create or modify an existing test to use a *valid* long timeout (e.g., 20-30 seconds, less than 300s) with a long-running command (like `sleep 25` or the `persistent_child.sh`). Verify that `execute_command` initially returns a 'Running' status, and the process can be subsequently queried or stopped. (The existing `test_execute_command_timeout_rejection.js` tests *invalid* timeouts > 300s).
        *   **Impacted Files/Components**: `tests/mcp_server_tests/test_execute_command_long_timeout.js` (New or modified existing test).
        *   **Dependencies**: Task 1.4.
        *   **Validation**: Test confirms `execute_command` handles valid long timeouts correctly, allowing for asynchronous operation and status checks/stops.

1.  **Refactor Test File Locations**
    *   [x] **1.1 Create New Test Directory Structure**
        *   **Description**: Create a new directory `tests/mcp_server_tests/` and a subdirectory `tests/mcp_server_tests/helper_scripts/` at the project root to house MCP server-specific tests, aligning with standard project structure.
        *   **Impacted Files/Components**: File system (new directories).
        *   **Dependencies**: None.
        *   **Validation**: Directories `tests/mcp_server_tests/` and `tests/mcp_server_tests/helper_scripts/` are created successfully.
    *   [x] **1.2 Move Existing MCP Server Tests**
        *   **Description**: Move the existing test files (`test_execute_command_timeout_rejection.js`, `test_get_terminal_status_timeout_rejection.js`, `test_stop_command_tree_kill.js`) from `.cursor/mcp/mcp-commit-server/tests/` to the new `tests/mcp_server_tests/` directory.
        *   **Impacted Files/Components**:
            *   `.cursor/mcp/mcp-commit-server/tests/test_execute_command_timeout_rejection.js` (Moved)
            *   `.cursor/mcp/mcp-commit-server/tests/test_get_terminal_status_timeout_rejection.js` (Moved)
            *   `.cursor/mcp/mcp-commit-server/tests/test_stop_command_tree_kill.js` (Moved)
            *   `tests/mcp_server_tests/` (Receives files)
        *   **Dependencies**: Task 1.1.
        *   **Validation**: Files are successfully moved to the new location. The old directory `.cursor/mcp/mcp-commit-server/tests/` (excluding `helper_scripts` for now) should be empty or removed.
    *   [x] **1.3 Move Existing Helper Scripts**
        *   **Description**: Move the existing helper script directory `.cursor/mcp/mcp-commit-server/tests/helper_scripts/` (and its contents like `persistent_child.sh`) to the new `tests/mcp_server_tests/helper_scripts/` directory.
        *   **Impacted Files/Components**:
            *   `.cursor/mcp/mcp-commit-server/tests/helper_scripts/` (Moved)
            *   `tests/mcp_server_tests/helper_scripts/` (Receives directory)
        *   **Dependencies**: Task 1.1.
        *   **Validation**: Directory and its contents are successfully moved. The old path `.cursor/mcp/mcp-commit-server/tests/helper_scripts/` is removed.
    *   [x] **1.4 Update Paths in Moved Test Scripts**
        *   **Description**: Review and update any internal paths within the moved test scripts. This primarily includes the `StdioClientTransport` CWD and server script path (e.g., `args: ['../../.cursor/mcp/mcp-commit-server/server.js']`, `cwd: projectRoot`) and paths to helper scripts.
        *   **Impacted Files/Components**:
            *   `tests/mcp_server_tests/test_execute_command_timeout_rejection.js`
            *   `tests/mcp_server_tests/test_get_terminal_status_timeout_rejection.js`
            *   `tests/mcp_server_tests/test_stop_command_tree_kill.js`
        *   **Dependencies**: Task 1.2, 1.3.
        *   **Validation**: All moved tests pass successfully after path updates.

2.  **Process Tree Killing Implementation**
    *   [x] **2.1 Add `tree-kill` Dependency**
        *   **Description**: Add the `tree-kill` npm package as a dependency to the MCP server project.
        *   **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/package.json`
        *   **Validation**: `tree-kill` added to `package.json` and `npm install` run successfully in the correct directory.

    *   [x] **2.2 Create `process_killer.js` Utility**
        *   **Description**: Create a new utility file `lib/util/process_killer.js` within the MCP server's source. This file will export a function, e.g., `killProcessTree(pid, callback)`, which uses the `tree-kill` library to terminate the process with the given PID and all its descendants. It should use a strong signal like `SIGKILL` to ensure termination.
        *   **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/lib/util/process_killer.js` (New file)
        *   **Validation**: File created with `killProcessTree` function using `tree-kill`.

    *   [x] **2.3 Implement `handleStopCommand` with Tree Killing**
        *   **Description**: Modify the `handleStopTerminalCommand` function in `mcp_tools/terminal_stop.js`. Replace the current call to `ProcessManager.killProcess(pid)` with a call to the new `killProcessTree(pid, (err) => { ... })` from `process_killer.js`. Inside the callback, update the process state in `StateManager` (e.g., mark as 'Killed', remove state, update `endTime`) and handle any errors from `tree-kill`.
        *   **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_stop.js`
        *   **Validation**: `handleStopCommand` modified to use `killProcessTree` and update `StateManager`.

1.  **MCP Server Core Enhancements**
    *   [x] **1.1 Implement Timeout Limits for MCP Tools**
        *   **Description**: Modify `execute_command` and `get_terminal_status` tools in the MCP server. Implement a 5-minute (300 seconds) maximum timeout. If the user-specified timeout exceeds this, the MCP should return an error without executing/processing. Update the Zod schema and description for the `timeout` argument in `server.js` to reflect this limit. Enforce this check at the beginning of the respective handler functions (`handleExecuteCommand`, `handleGetTerminalStatus`).
        *   **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/server.js`, `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_execution.js`, `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_status.js`.
        *   **Validation**: MCP server operational, timeout descriptions updated in `server.js`. Timeout logic added to handlers.

    *   [x] **1.2 Update Process Spawning for Detached Execution (Windows)**
        *   **Description**: Modify the `spawnProcess` function in `lib/process_manager.js` for Windows environments. Ensure `detached: true` and `shell: false` in `spawnOptions`, and call `child.unref()`.
        *   **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`.
        *   **Validation**: `detached: true` and `child.unref()` implemented for Windows in `process_manager.js`.

## 2. Enhance MCP Commit Tool [Done]
- [x] **2.1 Add `bypass_hooks` Argument**: Modify the `mcp_MyMCP_commit` tool to support bypassing hooks.

## 3. Update Test Workflow & Documentation [Done]
- [x] **3.1 Modify `