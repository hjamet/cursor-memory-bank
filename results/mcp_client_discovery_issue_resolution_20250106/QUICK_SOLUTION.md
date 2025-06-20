# Quick Solution: MCP Tool Not Appearing in Cursor

## Problem
New MCP tool not showing up in Cursor's available tools list despite proper server configuration.

## Solution
**Restart Cursor completely**

### Steps:
1. **Close Cursor**: Exit the application entirely
2. **Restart Cursor**: Launch the application again  
3. **Open Workspace**: Navigate back to your project
4. **Verify**: Check if the tool now appears in the available tools list

### Expected Result:
The missing tool should now appear with the correct naming pattern: `mcp_[ServerName]_[ToolName]`

## Why This Happens
Cursor caches MCP tool lists for performance. When tools are added to existing servers, the cache isn't automatically refreshed until the application restarts.

## Alternative Solutions (if restart doesn't work)
1. Reload the workspace
2. Check MCP server configuration in `.cursor/mcp.json`
3. Restart MCP servers manually
4. Verify tool registration in server code

## Prevention
- Add new tools before initial MCP server deployment when possible
- Always document restart requirements when distributing MCP server updates
- Test tool discovery in fresh Cursor sessions

---
**Quick Fix:** Just restart Cursor! 🔄 