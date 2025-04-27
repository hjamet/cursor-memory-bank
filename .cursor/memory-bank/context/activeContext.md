# Active Context

## Current Goal
Fix stdout/stderr capture issues in MCP command execution (Task 1.1).

## Current implementation context
- **High Priority Task**: Fix MCP Stdout/Stderr Capture (Task 1.1).
- **Problem**: Stdout/stderr from commands (Python, cmd, Git Bash) run via `mcp_MyMCP_execute_command` is inconsistently captured on Windows.
- **Analysis**: The issue likely stems from buffering, shell interactions (`shell: true`), or stream closing/flushing race conditions within `process_manager.js`. The current method pipes streams to log files, which are then read.
- **Potential Solutions**:
    - Refine `spawn` options in `process_manager.js`: Experiment with `shell: false` more consistently.
    - Implement direct Git Bash invocation for bash commands: `C:\\Program Files\\Git\\bin\\bash.exe -c \"...\"` using `shell: false`.
    - Improve stream handling: Ensure streams are fully flushed before the `close` event completes. Consider alternative capturing methods if piping to files remains problematic.
- **Testing**: Validate with specific Python (`-u`), cmd, and Git Bash commands, checking both stdout and stderr via `mcp_MyMCP_get_terminal_output`.

## Key Files Involved
- `.cursor/mcp/mcp-commit-server/lib/process_manager.js` (Main focus for modifications)
- `.cursor/mcp/mcp-commit-server/lib/logger.js` (Review stream creation/reading logic)
- `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_execution.js` (Calls `process_manager.spawnProcess`)
- `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_output.js` (Reads logs)
- `.cursor/memory-bank/context/activeContext.md`
- `.cursor/memory-bank/workflow/tasks.md`

## Next Steps
- Read `process_manager.js` and `logger.js`.
- Modify `process_manager.js` to implement potential solutions (e.g., refined shell handling, Git Bash invocation).
- Test iteratively using `mcp_MyMCP_execute_command` and `mcp_MyMCP_get_terminal_output`.