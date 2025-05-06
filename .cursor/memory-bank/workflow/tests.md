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
  - **Evolution**: Was failing due to SDK import/usage, now fixed and passes.

## Tests with Warnings
- None

## Failed Tests
- ❌ **NEW** `test_get_terminal_status_timeout_rejection.js`: Failed
  - **Error**: `ERR_PACKAGE_PATH_NOT_EXPORTED: No "exports" main defined in ... @modelcontextprotocol/sdk/package.json`
  - **Evolution**: New test, failing (likely same SDK import/usage issue as previously fixed test).
- ❌ **NEW** `test_stop_command_tree_kill.js`: Failed
  - **Error**: `ERR_PACKAGE_PATH_NOT_EXPORTED: No "exports" main defined in ... @modelcontextprotocol/sdk/package.json`
  - **Evolution**: New test, failing (likely same SDK import/usage issue as previously fixed test).

## Known Issues / Manual Tests
- ℹ️ **`test_git_install.sh` Auto-Config Path**: Although the test passes, the automatic `git config core.hooksPath` logic added to `install.sh` was not verified in a true Git repository context by the test suite. Manual verification recommended.