# Test Results

*Comparison Date: YYYY-MM-DD*

## Successful Tests
- ✅ `test_install.sh`: Passed - Stable
- ✅ `test_curl_install.sh`: Passed - Stable
- ✅ `test_git_install.sh`: Passed - Stable
- ✅ `test_download.sh`: Passed - Stable
- ✅ `test_mcp_async_terminal.js`: Passed - Stable
- ✅ `test_consult_image.js`: Passed - Stable
- ✅ `tests/mcp_server_tests/test_execute_command_timeout_rejection.js`: Passed
  - **Evolution**: Was failing due to `__dirname` error after move, now fixed.
- ✅ **FIXED** `test_get_terminal_status_timeout_rejection.js`: Passed
  - **Evolution**: Was failing (regression with -32603 error), now fixed by correcting client.callTool params structure.
- ✅ **FIXED** `test_stop_command_tree_kill.js`: Passed
  - **Evolution**: Was failing due to SDK usage and script path issues, now fixed. Tree killing appears functional.

## Tests with Warnings
- None

## Failed Tests
- None

## Known Issues / Manual Tests
- ℹ️ **`test_git_install.sh` Auto-Config Path**: Although the test passes, the automatic `git config core.hooksPath` logic added to `install.sh` was not verified in a true Git repository context by the test suite. Manual verification recommended.