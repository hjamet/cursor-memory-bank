# Active Context

## Current Status

- Fixed a `sed` command in `tests/test_curl_install.sh` (line 240) within the `test_mcp_json_absolute_path_no_jq` function.
- The goal was to correctly handle literal '\\n' characters when extracting a path from `mcp.json` without `jq`.
- The edit has been applied.