# ToDo

# In Progress

# Done
- [x] Install `execa` library
- [x] Run `tests/test_mcp_async_terminal.js` to verify the fix (Fixed regression by implementing killProcess and reverting execa)
- [ ] **Investigate MCP `find` command issue**: Determine why `find ./ -type f -name '*.md'` executed via `mcp_MyMCP_execute_command` with Git Bash returns empty stdout on this Windows system.