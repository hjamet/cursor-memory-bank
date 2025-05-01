# ToDo

## Temp: Debug install.sh Curl/No-JQ Failure [In Progress]
- [x] **1.1 Analyze Failure**: Determine why `install.sh --use-curl` (when jq is not in PATH) exits with code 1, even after fixing 404 handling and `cp` issues.
- [x] **1.2 Implement Fix**: Correct the logic in `install.sh`.

# In Progress


# Done

## 1. Testing Pre-commit Hook [Done]
- [x] **1.1 Test Hook Installation**: Enhance `tests/test_install.sh` to verify hook installation.
- [x] **1.2 Verify Hook Failure Message (Manual/Documentation)**: Verify or document how to verify the pre-commit hook failure message.

## 2. Enhance MCP Commit Tool [Done]
- [x] **2.1 Add `bypass_hooks` Argument**: Modify the `mcp_MyMCP_commit` tool to support bypassing hooks.

## 3. Update Test Workflow & Documentation [Done]
- [x] **3.1 Modify `test-execution.mdc`**: Update rule instructions for `tests.md` format.
- [x] **3.2 Refactor `tests.md`**: Rewrite the existing test results file.

## UserBrief Modifications (Aug 7, 2024)
- [x] **Modify `execute_command`