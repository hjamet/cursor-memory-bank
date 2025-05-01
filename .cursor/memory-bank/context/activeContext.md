# Active Context

## Current implementation context
- **Goal**: Debug why `install.sh --use-curl` exits with code 1 when jq is not in PATH.
- **Task**: 
    1.1 Analyze `install.sh` (curl path) to find the exact command causing the exit.
    1.2 Fix the logic in `install.sh`.
- **Context**: The failure occurs during the `test_mcp_json_absolute_path_no_jq` step of `test_curl_install.sh`. Previous fixes addressed 404 handling and file copying, but the exit persists. It might be during download attempts for `mcp.json`, the pre-commit hook, or `server.js`.
- **Attention**: Focus on the `install_rules` function's curl path when `jq` is missing.

## Summary of Recent Changes
- Called `test-execution` -> `fix` (multiple iterations fixing `test_curl_install.sh` and `test_install.sh`) -> `test-execution` -> `fix` -> `request-analysis` -> `implementation`.
- Modified `install.sh` (download_file 404 handling, cp command).
- Modified `tests/test_curl_install.sh` (set +e wrapper, --use-curl flag).
- Modified `tests/test_install.sh` (set +e wrapper, removed --use-curl).
- Committed fixes for test interactions.
- Last `test-execution` run failed on `test_curl_install.sh`.
- `fix` rule handed over to `request-analysis` after 4 attempts.
- `request-analysis` identified the need for targeted debugging of `install.sh`.
