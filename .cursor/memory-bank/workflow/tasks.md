# TO DO

### Priority Tasks

*   None

### Secondary Tasks

*   None

## DONE

*   ~~**Improve Async Terminal Test Diagnostics**~~:
    - [x] **1.1 Implement File Logging in Test**: Modified `tests/test_mcp_async_terminal.js` to write logs to `./test_mcp_async_terminal.log`.
    - [x] **1.2 Modify Fix Rule**: Updated `.cursor/rules/fix.mdc` to read log file.
*   ~~**Automate git hook config**: Modified install.sh to automatically run \`git config core.hooksPath .githooks\` if in a git repo.~~ (Commit: [...placeholder...])
*   ~~**Make Hook Non-Blocking**: Modified .githooks/pre-commit to print warnings for oversized files but always exit 0.~~ (Commit: [...placeholder...])
*   ~~**Revert Commit Tool Argument**: Modified commit.js to remove the bypass_hooks argument and associated --no-verify logic.~~ (Commit: [...placeholder...])
*   ~~**Test Automation:** Verify `mcp_MyMCP_commit` interaction with pre-commit hook (blocking & bypass).~~ (Automated test successful)
*   ~~Update pre-commit hook message to mention bypass.~~ (Commit: `feat: Update hook msg & verify commit tool bypass`)
*   ~~Update `README.md` with commit tool verification steps.~~ (Commit: `feat: Update hook msg & verify commit tool bypass`)
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
*   **Debug MCP Async Terminal Test Regression**: `tests/test_mcp_async_terminal.js` fails (Exit Code 1, no output) when run via `mcp_MyMCP_execute_command`. Issue seems related to MCP tool's output capture with complex Node.js scripts involving child processes and stdio manipulation. Requires manual investigation or potential MCP tool enhancement.
    - *Attempted*: Analysis, test simplification, fix attempts.
    - *Status*: Unresolved.

# In Progress

*   None

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
- [x] **3.1 Modify `