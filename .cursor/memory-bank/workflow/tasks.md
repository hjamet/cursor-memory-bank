# ToDo

## 1. Rule Modifications [In Progress]
- [x] **1.1 Modify `userbrief-template.mdc`**: Add an "Archives" section to the template.
    - *Description*: Edit the template file to include a new top-level markdown section `# Archives`.
    - *Impacted Files/Components*: `.cursor/rules/templates/userbrief-template.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: The file `.cursor/rules/templates/userbrief-template.mdc` contains the `# Archives` section.
- [x] **1.2 Modify `consolidate-repo.mdc` Rule**: Update the rule to move tasks from 'User Input' to 'Processing' with ⏳ emoji.
    - *Description*: Apply the rename-edit-rename procedure (`.mdc` -> `.md` -> edit -> `.mdc`). Edit the rule instructions and specifics to reflect that its purpose is to mark input tasks with ⏳ and move them to the 'Processing' section, removing logic related to ✅ or archive emojis.
    - *Impacted Files/Components*: `.cursor/rules/consolidate-repo.mdc`
    - *Dependencies*: 1.1 (implicitly uses the template structure)
    - *Validation Criteria*: The rule `consolidate-repo.mdc` correctly describes the input -> processing (⏳) step.
- [x] **1.3 Modify `task-decomposition.mdc` Rule**: Update the rule to handle processing (⏳) to archives (🗄️) transition.
    - *Description*: Apply the rename-edit-rename procedure. Modify Step 2 to only identify ⏳ tasks in 'Processing'. Modify Step 4 to include these ⏳ tasks when adding to `tasks.md`. Add a new Step 5 to move these tasks from 'Processing' to 'Archives' (🗄️) in `userbrief.md` *after* they have been added to `tasks.md`. Add a specific constraint forbidding the move to Archives if `tasks.md` integration failed.
    - *Impacted Files/Components*: `.cursor/rules/task-decomposition.mdc`
    - *Dependencies*: 1.1, 1.2
    - *Validation Criteria*: The rule `task-decomposition.mdc` correctly describes the processing (⏳) -> `tasks.md` -> archives (🗄️) logic.

# Done

## 1. Rule Modifications
- [x] **1.1 Modify `userbrief-template.mdc`**: Add an "Archives" section to the template.
    - *Description*: Edit the template file to include a new top-level markdown section `# Archives`.
    - *Impacted Files/Components*: `.cursor/rules/templates/userbrief-template.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: The file `.cursor/rules/templates/userbrief-template.mdc` contains the `# Archives` section.
- [x] **1.2 Modify `consolidate-repo.mdc` Rule**: Update the rule to move tasks from 'User Input' to 'Processing' with ⏳ emoji.
    - *Description*: Apply the rename-edit-rename procedure (`.mdc` -> `.md` -> edit -> `.mdc`). Edit the rule instructions and specifics to reflect that its purpose is to mark input tasks with ⏳ and move them to the 'Processing' section, removing logic related to ✅ or archive emojis.
    - *Impacted Files/Components*: `.cursor/rules/consolidate-repo.mdc`
    - *Dependencies*: 1.1 (implicitly uses the template structure)
    - *Validation Criteria*: The rule `consolidate-repo.mdc` correctly describes the input -> processing (⏳) step.
- [x] **1.3 Modify `task-decomposition.mdc` Rule**: Update the rule to handle processing (⏳) to archives (🗄️) transition.
    - *Description*: Apply the rename-edit-rename procedure. Modify Step 2 to only identify ⏳ tasks in 'Processing'. Modify Step 4 to include these ⏳ tasks when adding to `tasks.md`. Add a new Step 5 to move these tasks from 'Processing' to 'Archives' (🗄️) in `userbrief.md` *after* they have been added to `tasks.md`. Add a specific constraint forbidding the move to Archives if `tasks.md` integration failed.
    - *Impacted Files/Components*: `.cursor/rules/task-decomposition.mdc`
    - *Dependencies*: 1.1, 1.2
    - *Validation Criteria*: The rule `task-decomposition.mdc` correctly describes the processing (⏳) -> `tasks.md` -> archives (🗄️) logic.

- [x] **Consolidate-Repo Check**: Verified file integrity and performed terminal cleanup (no issues found).
- [x] **Implement Character-Based MCP Log Handling**: Refactored MCP terminal tools to use character counts instead of lines for output retrieval.
    - *Description*: Implemented character-based reading (`readLogChars`, `readLastLogChars`) in `logger.js`. Added read index tracking (`stdout_read_index`, `stderr_read_index`) to process state. Modified `handleExecuteCommand`, `handleGetTerminalOutput`, `handleGetTerminalStatus`, `handleStopTerminalCommand` to use new functions, respect character limits (3000/20000), and update indices to return only new output.
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, `.cursor/mcp/mcp-commit-server/lib/logger.js`, `.cursor/mcp/mcp-commit-server/mcp_tools/*.js`
    - *Validation*: Verified correct behavior via ad-hoc Python script tests covering completion, timeout, incremental output retrieval, and status snapshot cases.
- [x] **Fix MCP Stdout/Stderr Capture**: Resolve the issue where stdout and stderr are not consistently captured for commands executed via `mcp_MyMCP_execute_command` on Windows (using Git Bash). **Solution**: Always execute via `bash -c \"eval $(echo '<base64_command>' | base64 -d)\"` on Windows.
    - *Description*: Output is sometimes missing or incomplete despite the command executing. Investigate buffering, shell interactions, stream closing logic, and the user's suggestion of directly invoking Git Bash (`C:\\Program Files\\Git\\bin\\bash.exe -c \"...\"`).
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, potentially `.cursor/mcp/mcp-commit-server/lib/logger.js`.
    - *Dependencies*: None.
    - *Validation Criteria*: Running test commands like `python -u -c \"import sys; print('stdout test'); print('stderr test', file=sys.stderr)\"`, `cmd /c \"echo cmd_stdout && echo cmd_stderr >&2\"`, and `git status` via `mcp_MyMCP_execute_command` successfully captures both stdout and stderr, verified using `mcp_MyMCP_get_terminal_output`.
- [x] **Investigate Python Output Capture**: Verified that Python stdout/stderr/exit_code are correctly captured by the current implementation (universal Git Bash execution). (Previously Task 2.1)
- [x] **Enhance `mcp_execute_command`**: Implemented immediate return of full results (stdout/stderr/exit_code) if command finishes before timeout. (Previously Task 3.1)
- [x] **Implement Immediate Return for `execute_command`**: Modified MCP server (`terminal_execution.js`, `process_manager.js`, `server.js`) so `execute_command` waits for completion up to a timeout (default 10s). If completed early, returns full result (stdout/stderr/exit_code); otherwise, returns PID for background execution. (From userbrief.md)
- [x] **Add `cwd` to MCP Terminal Responses**: Modify MCP server tools (`execute_command`, `get_terminal_status`, `get_terminal_output`) to include the effective `cwd` (Current Working Directory) of the process in their responses.
- [x] Install `execa` library
- [x] Run `tests/test_mcp_async_terminal.js` to verify the fix (Fixed regression by implementing killProcess and reverting execa)
- [x] **Investigate MCP `find` command issue**: Determine why `find ./ -type f -name \\'*.md\\'` executed via `mcp_MyMCP_execute_command` with Git Bash returns empty stdout on this Windows system. (Fixed by explicit spawn `shell:false` + removing console logs)

## 2. Tool Testing
- [x] **2.1 Test `consult_image` tool**: Manually invoke the `consult_image` MCP tool using the image provided.
    - *Description*: Use the image located at `tests/assets/image.png` to test the `mcp_MyMCP_consult_image` tool. This task originates from `userbrief.md`.
    - *Impacted Files/Components*: `tests/assets/image.png`, `mcp_MyMCP_consult_image` tool.
    - *Dependencies*: None
    - *Validation Criteria*: Successful execution of `mcp_MyMCP_consult_image` with the specified image, returning expected output (e.g., base64 representation).