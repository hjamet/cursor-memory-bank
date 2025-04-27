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

1.2. [ ] **Update `test-execution` Rule**: Modify the rule to primarily use MCP tools (`mcp_MyMCP_execute_command`, etc.) for executing test commands, similar to how `fix` and `experience-execution` were updated.
    - Description: Update the instructions and examples in the rule to demonstrate and recommend using the suite of MCP terminal tools for running tests.
    - Files: `.cursor/rules/test-execution.mdc`
    - Dependencies: MCP terminal tools.
    - Validation: The rule reflects the usage of MCP tools for test execution.

# Done

## 1. Rule Modifications (Current Cycle)

1.1. [x] **Update `context-update` Rule**: Modify the rule to use the MCP `commit` tool (`mcp_MyMCP_commit`) instead of the `git commit -a` command for committing changes. (Verified already correct)
    - Description: Replace the `run_terminal_cmd` call for `git commit -a ...` with a call to `mcp_MyMCP_commit`, ensuring all necessary arguments (emoji, type, title, description) are passed correctly.
    - Files: `.cursor/rules/context-update.mdc`
    - Dependencies: `mcp_MyMCP_commit` tool.
    - Validation: The rule uses the MCP tool for commits, and commits are successful.

1.2. [x] **Update `test-execution` Rule**: Modify the rule to primarily use MCP tools (`mcp_MyMCP_execute_command`, etc.) for executing test commands, similar to how `fix` and `experience-execution` were updated.
    - Description: Update the instructions and examples in the rule to demonstrate and recommend using the suite of MCP terminal tools for running tests.
    - Files: `.cursor/rules/test-execution.mdc`
    - Dependencies: MCP terminal tools.
    - Validation: The rule reflects the usage of MCP tools for test execution.

1.3. [x] **Update `fix` Rule**: Modify the rule to remove the mention of the deprecated MCP `Debug` tool and suggest using temporary debug logging instead.
    - Description: Edit the rule's instructions/specifics to replace references to the MCP `Debug` tool with guidance on adding temporary logging statements (`console.log`, etc.) within the code being fixed and remembering to remove them afterward.
    - Files: `.cursor/rules/fix.mdc`
    - Dependencies: None.
    - Validation: The rule no longer mentions the MCP `Debug` tool and correctly suggests temporary logging.

## 2. MCP Server Enhancements (Current Cycle)

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
    - Validation: Background task correctly identifies completed/disappeared processes and updates `