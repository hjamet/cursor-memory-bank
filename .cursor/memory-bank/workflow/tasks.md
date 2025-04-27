# ToDo

(No tasks remaining in ToDo for now)

# Done

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

