# Test Results

*Comparison Date: YYYY-MM-DD*

## Successful Tests
- ✅ `test_install.sh`: Passed - Stable
- ✅ `test_curl_install.sh`: Passed - Stable
- ✅ `test_git_install.sh`: Passed - Stable
- ✅ `test_download.sh`: Passed - Stable
- ✅ `test_mcp_async_terminal.js`: Passed - Stable
- ✅ `test_consult_image.js`: Passed - Stable
- ✅ **FIXED** `test_execute_command_timeout_rejection.js`: Passed
  - **Evolution**: Was failing (regression with -32603 error), now fixed by correcting client.callTool params structure.

## Tests with Warnings
- None

## Failed Tests
- ❌ `test_get_terminal_status_timeout_rejection.js`: Failed (Regression)
  - **Error**: `McpError: MCP error -32603: [[{"code":"invalid_type","expected":"string","received":"undefined","path":[      "params",      "name"    ],"message":"Required"  }]]`
  - **Evolution**: Was passing after SDK usage fix, now failing. Server expects 'name' in tool params. (Likely needs same client.callTool fix)
- ❌ `test_stop_command_tree_kill.js`: Failed (Regression)
  - **Error**: `McpError: MCP error -32603: [[{"code":"invalid_type","expected":"string","received":"undefined","path":[      "params",      "name"    ],"message":"Required"  }]]`
  - **Evolution**: Was passing after SDK usage fix, now failing. Server expects 'name' in tool params. (Likely needs same client.callTool fix)

## Known Issues / Manual Tests
- ℹ️ **`test_git_install.sh` Auto-Config Path**: Although the test passes, the automatic `git config core.hooksPath` logic added to `install.sh` was not verified in a true Git repository context by the test suite. Manual verification recommended.