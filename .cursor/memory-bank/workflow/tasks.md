# ToDo

# In Progress

# Done

## 1. MCP Server Enhancement
- [x] **1.1 Implement Process Tree Killing**: Modify the `killProcess` function in the MCP server to terminate the entire process tree (parent and children) associated with a given PID.
    - *Description*: The current `process.kill` only terminates the parent. Research and implement a cross-platform solution, potentially using the `fkill` npm package.
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, `.cursor/mcp/mcp-commit-server/package.json` (add dependency).
    - *Dependencies*: None (external library `fkill` to be added).
    - *Validation Criteria*: A test case involving starting a parent process (e.g., bash script) that spawns a child process (e.g., python script `sleep(30)`), then stopping the parent PID via `mcp_MyMCP_stop_terminal_command`, should result in both parent and child processes being terminated (verified via OS tools like `tasklist` or `ps`).

## 2. Rule Enhancement
- [x] **2.1 Update experience-execution Rule**: Modify the `experience-execution.mdc` rule to incorporate an incremental timeout strategy for monitoring long-running commands.
    - *Description*: The rule should guide the agent to initially check command status/output with a short timeout (e.g., 20 seconds) using `mcp_MyMCP_get_terminal_status` or `mcp_MyMCP_get_terminal_output`, then progressively increase the timeout for subsequent checks, ensuring no single timeout exceeds ~5 minutes.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`.
    - *Dependencies*: None.
    - *Validation Criteria*: Manual review of the updated rule instructions to ensure they clearly describe the incremental timeout strategy.
