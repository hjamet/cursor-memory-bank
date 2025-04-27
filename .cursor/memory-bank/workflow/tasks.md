# ToDo

## 1. Rule Modifications

1.1. [ ] **Update `context-update` Rule**: Modify the rule to use the MCP `commit` tool (`mcp_MyMCP_commit`) instead of the `git commit -a` command for committing changes.
    - Description: Replace the `run_terminal_cmd` call for `git commit -a ...` with a call to `mcp_MyMCP_commit`, ensuring all necessary arguments (emoji, type, title, description) are passed correctly.
    - Files: `.cursor/rules/context-update.mdc`
    - Dependencies: `mcp_MyMCP_commit` tool.
    - Validation: The rule uses the MCP tool for commits, and commits are successful.

1.2. [ ] **Update `test-execution` Rule**: Modify the rule to primarily use MCP tools (`mcp_MyMCP_execute_command`, etc.) for executing test commands, similar to how `fix` and `experience-execution` were updated.
    - Description: Update the instructions and examples in the rule to demonstrate and recommend using the suite of MCP terminal tools for running tests.
    - Files: `.cursor/rules/test-execution.mdc`
    - Dependencies: MCP terminal tools.
    - Validation: The rule reflects the usage of MCP tools for test execution.

1.3. [ ] **Update `fix` Rule**: Modify the rule to remove the mention of the deprecated MCP `Debug` tool and suggest using temporary debug logging instead.
    - Description: Edit the rule's instructions/specifics to replace references to the MCP `Debug` tool with guidance on adding temporary logging statements (`console.log`, etc.) within the code being fixed and remembering to remove them afterward.
    - Files: `.cursor/rules/fix.mdc`
    - Dependencies: None.
    - Validation: The rule no longer mentions the MCP `Debug` tool and correctly suggests temporary logging.

1.4. [ ] **Remove `[200~` Terminal Error Mentions**: Identify all rule files (`.cursor/rules/*.mdc`) that mention the `[200~` terminal error (related to the old `run_terminal_cmd` tool) and remove those specific notes/warnings, as they are obsolete with the use of MCP tools.
    - Description: Search across all `.mdc` files in `.cursor/rules/` for references to the `[200~` bug or similar terminal execution warnings related to the old tool. Remove these specific sentences/paragraphs.
    - Files: `.cursor/rules/*.mdc` (Multiple files likely involved, e.g., `context-update.mdc`, `fix.mdc`, `experience-execution.mdc`, `implementation.mdc`)
    - Dependencies: None.
    - Validation: Rules no longer contain the outdated warnings about the `[200~` terminal bug.

## 2. MCP Server Enhancements

2.1. [ ] **Add `send_terminal_input` MCP Tool**: Implement a new tool in the MCP server (`server.js`) to send input to a running terminal process.
    - Description: Define a new tool `send_terminal_input` with schema `pid` (number), `input` (string), optional `timeout` (number). The handler should find the child process associated with the `pid` (potentially requires storing the `child` object in `terminalStates`), write the `input` string followed by `\n` to `child.stdin`. It needs a mechanism to capture subsequent stdout/stderr and potential exit code within the timeout, similar to `execute_command`'s response structure. Careful handling of stdin stream availability and potential errors is required.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: Node.js `child_process` (access to `child.stdin`), potentially modifying `terminalStates` structure.
    - Validation: Tool successfully sends input, captures output, handles timeout, and returns expected structure. Requires new tests.

## 3. Completed / Deferred

3.1. [x] **Modify `stop_terminal_command` MCP Tool**: Modify the tool to accept a list of PIDs.
    - Status: Completed and tested in previous steps.

# In Progress

## 1. Rule Modifications

1.1. [x] **Update `context-update` Rule**: Modify the rule to use the MCP `commit` tool (`mcp_MyMCP_commit`) instead of the `git commit -a` command for committing changes. (Verified already correct)
    - Description: Replace the `run_terminal_cmd` call for `git commit -a ...` with a call to `mcp_MyMCP_commit`, ensuring all necessary arguments (emoji, type, title, description) are passed correctly.
    - Files: `.cursor/rules/context-update.mdc`
    - Dependencies: `mcp_MyMCP_commit` tool.
    - Validation: The rule uses the MCP tool for commits, and commits are successful.

# Done

## 1. Rule Modifications (Current Cycle)

1.1. [x] **Update `context-update` Rule**: Modify the rule to use the MCP `commit` tool (`mcp_MyMCP_commit`) instead of the `git commit -a` command for committing changes. (Verified already correct)
    - Description: Replace the `run_terminal_cmd` call for `git commit -a ...` with a call to `mcp_MyMCP_commit`, ensuring all necessary arguments (emoji, type, title, description) are passed correctly.
    - Files: `.cursor/rules/context-update.mdc`
    - Dependencies: `mcp_MyMCP_commit` tool.
    - Validation: The rule uses the MCP tool for commits, and commits are successful.

# Blocked

(Old blocked tasks removed for clarity)

## 1. MCP Server Enhancements (Current Cycle)

1.1. [x] **Implement `reuse_terminal` Logic**: Modify the `mcp_execute_command` handler. If `reuse_terminal` is true, find an inactive terminal (status `Success`, `Failure`, or `Stopped`), clean up its state entry and log files, then proceed with spawning the new command.
    - Actions: Add check for inactive terminals at the start of the handler. Implement cleanup logic (remove state, delete logs, update state file). Ensure this runs only if `reuse_terminal` is true.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: Requires `terminalStates` access, file system access (`fs.unlinkSync`), existing state update functions.
    - Validation: When calling `mcp_execute_command` repeatedly with `reuse_terminal: true`, inactive entries in `terminalStates` are cleared, and log files are deleted.

1.2. [x] **Decrease Status Update Interval**: Change the background status check interval from 5 seconds to 1 second for faster updates.
    - Actions: Modify the `setInterval` call in the `startServer` function.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: None.
    - Validation: The interval in `setInterval(updateRunningProcessStatuses, ...)` is set to `1000`.

## 1. MCP Server Enhancements (Previous Cycle)

1.1. [x] **Set Default CWD for `mcp_execute_command`**: Modify the MCP server script to ensure commands executed via `mcp_execute_command` run in the project's root directory by default.
    - Actions: Add `cwd: projectRoot` to the options object passed to `child_process.spawn` within the `execute_command` handler.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: None (requires `projectRoot` variable to be defined, which it is).
    - Validation: Commands like `git status` run via `mcp_execute_command` operate on the project root without needing `cwd` explicitly set.

## 2. Rule Updates (Previous Cycle)

2.1. [x] **Update Rules to Recommend MCP Terminal Tools**: Modify specified rules to recommend using the new MCP terminal tools (`mcp_execute_command`, etc.) over the standard terminal tool.
    - Actions: Add the provided explanatory paragraph about MCP tool usage to the specified rule files.
    - Files: `.cursor/rules/experience-execution.mdc`, `.cursor/rules/fix.mdc`, `.cursor/rules/implementation.mdc`.
    - Dependencies: None.
    - Validation: The rules contain the updated paragraph recommending MCP terminal tools.

## 1. Enhance MCP Commit Server with Async Terminal Execution
1.1. [x] **Setup State Persistence & Logging**: Initialize the `terminals_status.json` file structure and the `logs/` directory. Implement functions to read/write the JSON state file safely (handling potential concurrent access if necessary) and ensure the server reads the state on startup.
    - Description: Create the mechanism for storing and retrieving the status of tracked terminal processes persistently. Ensure log directory exists.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`, create `.cursor/mcp/mcp-commit-server/terminals_status.json`, create `.cursor/mcp/mcp-commit-server/logs/` directory.
    - Dependencies: None.
    - Validation: Server correctly initializes/reads `terminals_status.json` on start, functions for atomic read/write exist, log directory is created.

1.2. [x] **Implement Background Status Monitor**: Create a `setInterval` based background task within `server.js` that runs approximately every 5 seconds.
    - Description: This task should read `terminals_status.json`, iterate through processes marked as 'Running', check their actual OS status (using `process.kill(pid, 0)` or similar cross-platform check), update their status (`Success`, `Failure` with exit code, `Stopped` if PID disappeared), and rewrite the `terminals_status.json` file with the updated information.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`.
    - Dependencies: Task 1.1 (state persistence functions).
    - Validation: Background task correctly identifies completed/disappeared processes and updates `terminals_status.json`.

1.3. [x] **Implement `mcp_execute_command` Endpoint**: Add the new API endpoint using `child_process.spawn`.
    - Description: Implement the `mcp_execute_command` tool. Use `child_process.spawn` with `detached: true` and `stdio: ['ignore', log_stdout_stream, log_stderr_stream]`. Redirect stdout/stderr to `logs/<pid>.stdout.log` and `logs/<pid>.stderr.log`. Implement terminal reuse logic if specified. Add the new process entry to `terminals_status.json`. Handle the initial `timeout` wait and return the specified JSON structure. Ensure JSDoc comments are added.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`.
    - Dependencies: Task 1.1 (state persistence functions), understanding of `child_process.spawn` and file stream redirection.
    - Validation: Endpoint spawns command, redirects output, updates state, handles timeout correctly, and returns the correct JSON structure. Reuse logic works.

1.4. [x] **Implement `mcp_get_terminal_status` Endpoint**: Add the new API endpoint to retrieve status.
    - Description: Implement the `mcp_get_terminal_status` tool. Read `terminals_status.json`. Implement the optional `timeout` logic to wait for status changes (leveraging the background monitor from Task 1.2). Format the output according to the specified JSON structure, including tailing the last ~10 lines from log files for each entry.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`.
    - Dependencies: Task 1.1, Task 1.2.
    - Validation: Endpoint returns the correct status information, handles the optional timeout wait, and correctly tails log files.

1.5. [x] **Implement `mcp_get_terminal_output` Endpoint**: Add the new API endpoint to retrieve full logs.
    - Description: Implement the `mcp_get_terminal_output` tool. Read the specified number of lines (default 100) from the `.stdout.log` and `.stderr.log` files for the given PID. Return the specified JSON structure.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`.
    - Dependencies: Task 1.3 (log file creation).
    - Validation: Endpoint correctly reads and returns the specified number of lines from the correct log files.

1.6. [x] **Implement `mcp_stop_terminal_command` Endpoint**: Add the new API endpoint to stop processes.
    - Description: Implement the `mcp_stop_terminal_command` tool. Read the last specified lines from log files. Attempt to terminate the process using `process.kill(pid, 'SIGTERM')` and then `process.kill(pid, 'SIGKILL')` if necessary. Remove the process entry from `terminals_status.json` and delete the associated log files. Return the specified JSON structure indicating status and final output.
    - Files: `.cursor/mcp/mcp-commit-server/server.js`.
    - Dependencies: Task 1.1, Task 1.3.
    - Validation: Endpoint correctly attempts termination, cleans up state file and logs, and returns the specified JSON structure.

# Blocked

## 1. MyMCP Tool Investigation

### 1.1 Investigate Local MyMCP Server (`mcp-commit-server/server.js`) Failure
- **Status**: Blocked
- **Description**: MyMCP tools (`execute_command`, `get_terminal_status`) fail consistently ("Error: no result from tool"). Investigation confirmed MyMCP uses the local `.cursor/mcp/mcp-commit-server/server.js` script (via `mcp.json`). Code review of `server.js` revealed no obvious errors. Added debug logs to `server.js`, but the logs were not visible when calling tools via MCP, preventing further diagnosis. The root cause might be in the MCP communication layer, Node.js environment interaction, or SDK.
- **Impacted Files/Components**: `.cursor/mcp/mcp-commit-server/server.js`, `.cursor/mcp.json`, MCP SDK/Transport, Node.js environment.
- **Dependencies**: A working method to debug MCP server scripts launched via `mcp.json` or resolution of the underlying issue.
- **Validation Criteria**: Successful execution of MyMCP tools OR identification of the root cause.
- **Next Step**: Requires external help or different debugging approach (e.g., checking Cursor logs if possible, simplifying `server.js` further).

## 1. Rule Enhancements

1.1. [ ] **Add MCP Cleanup Step to `consolidate-repo`**: Modify the `consolidate-repo.mdc` rule to include a new instruction step for cleaning up completed MCP terminals.
    - Actions: Define the step logic: call `mcp_get_terminal_status`, identify finished terminals (`Success`, `Failure`, `Stopped`), call `mcp_stop_terminal_command` for each PID.
    - Files: `.cursor/rules/consolidate-repo.mdc`
    - Dependencies: MCP tools (`mcp_get_terminal_status`, `mcp_stop_terminal_command`).
    - Validation: The `consolidate-repo.mdc` rule includes the new cleanup step in its Instructions section.

1.2. [ ] **Add Cleanup Note to `experience-execution`**: Add a brief note to the `experience-execution.mdc` rule reminding the agent to proactively use `mcp_stop_terminal_command`.
    - Actions: Add a sentence like "Remember to call `mcp_stop_terminal_command` for terminals once results are analyzed and they are no longer needed." to the Specifics section.
    - Files: `.cursor/rules/experience-execution.mdc`
    - Dependencies: None.
    - Validation: The rule contains the reminder note.

1.3. [ ] **Add Cleanup Note to `fix`**: Add a brief note to the `fix.mdc` rule reminding the agent to proactively use `mcp_stop_terminal_command`.
    - Actions: Add a similar reminder sentence to the Specifics section.
    - Files: `.cursor/rules/fix.mdc`
    - Dependencies: None.
    - Validation: The rule contains the reminder note.

