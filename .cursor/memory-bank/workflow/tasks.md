# TO DO

### Priority Tasks

*   None

### Secondary Tasks

*   None

## DONE

*   ~~**Test Automation:** Verify `mcp_MyMCP_commit` interaction with pre-commit hook (blocking & bypass).~~ (Automated test successful)
*   ~~Update pre-commit hook message to mention bypass.~~ (Current changes)
*   ~~Update `README.md` with commit tool verification steps.~~ (Current changes)
*   ~~Enhance `mcp_MyMCP_commit` tool: Add `bypass_hooks` argument.~~ (Commit: `chore: Enhance pre-commit tests...`)
*   ~~Refactor `tests.md` to new format.~~ (Commit: `chore: Enhance pre-commit tests...`)
*   ~~Modify `test-execution.mdc` rule for new `tests.md` format.~~ (Commit: `chore: Enhance pre-commit tests...`)
*   ~~Add hook installation check to `tests/test_install.sh`.~~ (Commit: `chore: Enhance pre-commit tests...`)
*   ~~Add manual verification steps for hook message to `README.md`.~~ (Commit: `chore: Enhance pre-commit tests...`)
*   ~~Create pre-commit hook script (`.githooks/pre-commit`).~~ (Commit: `feat: Add pre-commit hook...`)
*   ~~Update `install.sh` to install hook.~~ (Commit: `feat: Add pre-commit hook...`)
*   ~~Modify `fix.mdc` to handle hook failure.~~ (Commit: `feat: Add pre-commit hook...`)
*   ~~Modify `context-update.mdc` to handle hook failure.~~ (Commit: `feat: Add pre-commit hook...`)
*   ~~Temp: Debug install.sh Curl/No-JQ Failure~~ 
*   ~~Testing Pre-commit Hook~~ 
*   ~~Enhance MCP Commit Tool~~ 
*   ~~Update Test Workflow & Documentation~~ 
*   ~~UserBrief Modifications (Aug 7, 2024)~~ 


## BACKLOG

*   Monitor `test_curl_install.sh` failure (Expected 404 until hook is merged to main/master).

# In Progress


# Done

## Temp: Debug install.sh Curl/No-JQ Failure [Done]
- [x] **1.1 Analyze Failure**: Determine why `install.sh --use-curl` (when jq is not in PATH) exits with code 1, even after fixing 404 handling and `cp` issues.
- [x] **1.2 Implement Fix**: Correct the logic in `install.sh`.

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