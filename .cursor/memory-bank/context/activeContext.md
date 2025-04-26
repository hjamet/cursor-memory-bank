# Active Context

## Current implementation context

- **Task:** Fix a failing test related to `install.sh`.
- **Constraint:** Do not modify the `install.sh` script itself.
- **Affected Files:** Likely one of `tests/test_install.sh`, `tests/test_curl_install.sh`, or `tests/test_git_install.sh`.
- **Goal:** Identify the specific failing test and correct the test script logic.

## Current Status

- **Task:** Fixed the failing `test_mcp_json_absolute_path_no_jq` test in `tests/test_curl_install.sh`.
- **Fixes:**
    - Corrected `--target` option to `--dir` when calling `install.sh`.
    - Modified the test to capture `stderr` instead of checking a non-existent log file.
    - Refined `awk`/`grep`/`sed` logic to correctly extract the server path from `mcp.json`.
- **Result:** All installation tests (`test_install.sh`, `test_curl_install.sh`, `test_git_install.sh`) are now passing.