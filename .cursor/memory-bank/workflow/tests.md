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
- ✅ `tests/mcp_server_tests/test_get_terminal_status_timeout_rejection.js`: Passed
  - **Evolution**: Previously marked as FIXED, assumed failed due to `__dirname` error after move, now confirmed fixed and passing.
- ✅ `tests/mcp_server_tests/test_stop_command_tree_kill.js`: Passed
  - **Evolution**: Was failing due to `__dirname` and then script path issues after move, now fixed.
- ✅ `tests/mcp_server_tests/test_python_interrupt.js`: Passed (New)
  - **Evolution**: New test for Python script execution and interruption via tree-kill.
- ✅ `tests/mcp_server_tests/test_execute_command_long_timeout.js`: Passed (New)
  - **Evolution**: New test for `execute_command` with long-running commands and valid shorter timeouts. Validated with `sleep` command after `persistent_child.sh` proved problematic.
- ✅ `tests/mcp_server_tests/test_take_webpage_screenshot.js`: Passed (New)
  - **Evolution**: New test for the `take_webpage_screenshot` MCP tool. Validated with `http://httpbin.org/html`.

## Tests with Warnings
- None

## Failed Tests
- None

## Known Issues / Manual Tests
- ℹ️ **`test_git_install.sh` Auto-Config Path**: Although the test passes, the automatic `git config core.hooksPath` logic added to `install.sh` was not verified in a true Git repository context by the test suite. Manual verification recommended.