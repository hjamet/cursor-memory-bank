# Active Context

## Summary of Recent Changes
- Modified `commit` MCP tool (`commit.js`, `server.js`) to accept `working_directory` argument and report committed files.
- Updated rule system (`request-analysis`, `fix`, `implementation`, `experience-execution`, `architect`):
    - Replaced Memory MCP with a file-based system using markdown notes in `.cursor/memory` for high-level vision/preferences.
    - Replaced generic web search tool with `mcp_brave-search_brave_web_search`.
    - Created `.cursor/memory` directory.
    - Used rename-edit-rename workflow (with `mcp_MyMCP_execute_command`) for rule modification.
