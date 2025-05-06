# TO DO

### Priority Tasks

*No current priority tasks here, moved to In Progress or Done.*

# IN PROGRESS
*No tasks currently in progress here.*

# DONE

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

## BACKLOG

*   Monitor `test_curl_install.sh` failure (Expected 404 until hook is merged to main/master).
*   **Debug MCP Async Terminal Test Regression**: `tests/test_mcp_async_terminal.js` fails (Exit Code 1, no output) when run via `mcp_MyMCP_execute_command`. Issue seems related to MCP tool's output capture with complex Node.js scripts involving child processes and stdio manipulation. Requires manual investigation or potential MCP tool enhancement.
    - *Attempted*: Analysis, test simplification, fix attempts.
    - *Status*: Unresolved.

## DONE
(Retaining recent DONE items for context, older ones can be further pruned if needed)
*   **Improve Async Terminal Test Diagnostics**:
    - [x] **1.1 Implement File Logging in Test**: Modified `tests/test_mcp_async_terminal.js` to write logs to `./test_mcp_async_terminal.log`.
    - [x] **1.2 Modify Fix Rule**: Updated `.cursor/rules/fix.mdc` to read log file.
*   **Rule & Script Modifications**
    *   [x] **1.1 Enhance `fix` Rule**: Added Git history check suggestion and updated example in `.cursor/rules/fix.mdc`.
    *   [x] **1.2 Improve `install.sh` Robustness**: Added pre-install cleanup (`rm -rf .cursor/mcp`) in `install.sh`.
    *   [x] **1.3 Simplify `architect` Rule**: Refactored `.cursor/rules/architect.mdc` to Markdown, removed status command, added mandatory context/git log sequence, and enforced French output.

## Temp: Debug install.sh Curl/No-JQ Failure [Done]
- [x] **1.1 Analyze Failure**: Determine why `install.sh --use-curl` (when jq is not in PATH) exits with code 1, even after fixing 404 handling and `cp` issues.
- [x] **1.2 Implement Fix**: Correct the logic in `install.sh`.

## 1. Testing Pre-commit Hook [Done]
- [x] **1.1 Test Hook Installation**: Enhance `tests/test_install.sh` to verify hook installation.
- [x] **1.2 Verify Hook Failure Message (Manual/Documentation)**: Verify or document how to verify the pre-commit hook failure message.

## 2. Enhance MCP Commit Tool [Done]
- [x] **2.1 Add `bypass_hooks` Argument**: Modify the `mcp_MyMCP_commit` tool to support bypassing hooks.

## 3. Update Test Workflow & Documentation [Done]
- [x] **3.1 Modify `