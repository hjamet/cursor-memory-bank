# Active Context

## Current Goal
Completed implementation and testing of character-based log truncation and retrieval for MCP terminal tools.

## Summary of Fix
- Added `stdout_read_index` and `stderr_read_index` to process state in `process_manager.js`.
- Implemented `readLogChars` and `readLastLogChars` in `logger.js` using `fs.promises`.
- Updated MCP tool handlers (`terminal_execution.js`, `terminal_output.js`, `terminal_status.js`, `terminal_stop.js`) to use the new logger functions, respect character limits (3000/20000), and manage read indices.
- Successfully tested via ad-hoc Python script execution using MCP tools, verifying correct handling of:
    - Immediate command completion within timeout (full output).
    - Command timeout (partial output).
    - Subsequent calls retrieving only new output.
    - Status snapshot showing last N characters.

## Current implementation context
N/A - Implementation and testing complete for this cycle.

## Previous Context (Preserved)
- Fixed `consult_image` MCP tool (previously crashed on large images).
    - Used `sharp` library for server-side image resizing/compression before base64 encoding.
- Strengthened `experience-execution` rule analysis.
- Modified `experience-execution` rule error handling.
- Verified `mcp_MyMCP_stop_terminal_command`.
- Debugged `MODULE_NOT_FOUND` error with `mcp-commit-server`.