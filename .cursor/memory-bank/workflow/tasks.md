# ToDo

# In Progress

# Done

## 2. General Rule Improvement

2.1. [x] **Ensure Rules Use MCP Tools**: Reviewed all rule files (`.cursor/rules/*.mdc`) to confirm they exclusively recommend and use MCP tools (`mcp_MyMCP_*`) for terminal commands, replacing any remaining references to `run_terminal_cmd`.
    - Description: Grep/search through all `.mdc` files for `run_terminal_cmd`. Verified rules like `context-update` (mentioned in userbrief) and others use the correct MCP tools in instructions and examples. Updated where necessary.
    - Files: `.cursor/rules/*.mdc` (Potentially all rule files)
    - Dependencies: MCP Terminal Tools (`mcp_MyMCP_execute_command`, etc.).
    - Validation: All rules consistently use MCP tools for command execution examples/instructions.