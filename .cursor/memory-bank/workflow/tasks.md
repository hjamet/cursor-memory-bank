# ToDo


# In Progress

# Done

## 1. Pre-commit Hook Implementation [Done]
- [x] **1.1 Create Hook Script**: Create the pre-commit hook script.
  - *Description*: Write a Bash script (`.githooks/pre-commit`) that checks the line count of staged code files. Use `git diff --cached --name-only` to get staged files. Filter for extensions: `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php`, `.sh`. Use `wc -l` to count lines. If any file exceeds 500 lines, collect filenames, print the specified error message in English, and exit with a non-zero status.
  - *Impacted Files/Components*: `.githooks/pre-commit` (New file)
  - *Dependencies*: Git
  - *Validation Criteria*: The script correctly identifies oversized staged code files and blocks commits with the specified error message.

## 2. Installation Script Update [Done]
- [x] **2.1 Add Hook Installation**: Modify `install.sh` to install the hook.
  - *Description*: Add steps in `install.sh` to:
    1. Create the `$INSTALL_DIR/.githooks` directory if it doesn't exist.
    2. Copy the pre-commit script (created in task 1.1, assume it exists in the source repo at `.githooks/pre-commit`) to `$INSTALL_DIR/.githooks/pre-commit`.
    3. Make the copied script executable (`chmod +x`).
    4. Add a final `log` message instructing the user to run `git config core.hooksPath .githooks` in their repository to activate the hook.
  - *Impacted Files/Components*: `install.sh`, `.githooks/pre-commit` (from source)
  - *Dependencies*: Task 1.1 (pre-commit script available in source repo)
  - *Validation Criteria*: `install.sh` successfully copies the hook, makes it executable, creates the directory, and displays the user instruction message.

## 3. Rule Modification: `fix.mdc` [Done]
- [x] **3.1 Add Hook Error Handling**: Modify the `fix.mdc` rule to handle the pre-commit error.
  - *Description*: Using the rename-edit-rename workaround (`.mdc` -> `.md` -> edit -> `.mdc`), modify the `fix` rule. Identify where commits are attempted (likely using `mcp_MyMCP_commit` or potentially `run_terminal_cmd` in step 2.5). After the commit attempt, check the result/output for the specific error message: "Echec du commit. Les fichiers suivants font plus de 500 lignes et devraient être refactorisés...". If this error is detected:
    1. Parse the list of filenames from the error message.
    2. Read `.cursor/memory-bank/workflow/tasks.md`.
    3. For each oversized file, check if a corresponding refactoring task already exists in the "ToDo" or "In Progress" sections.
    4. If not, add a new task to the "ToDo" section (or highest priority) with:
       - Title: `Refactor oversized file: [filename]`
       - Description: `Refactor [filename] (currently over 500 lines) into smaller, logical sub-files each under 500 lines. CRITICAL: After each significant change during refactoring, run relevant tests (`pytest`, `npm test`, etc. for the affected module/component) to ensure no regressions are introduced.`
       - Impacted Files: `[filename]`, potentially new files.
       - Dependencies: None.
       - Validation: File(s) refactored, all related tests pass.
    5. Update `tasks.md` with the new task(s).
    6. Adjust the rule's flow: Instead of proceeding as if the fix was successful, potentially call `context-update` to save the new task list or directly call `implementation` if appropriate.
  - *Impacted Files/Components*: `.cursor/rules/fix.mdc`, `.cursor/memory-bank/workflow/tasks.md`
  - *Dependencies*: Task 1.1 (for the specific error message)
  - *Validation Criteria*: The `fix` rule correctly detects the line-count error, adds appropriate refactoring tasks to `tasks.md` if they don't exist, and adjusts its control flow.

## 4. Rule Modification: `context-update.mdc` [Done]
- [x] **4.1 Add Hook Error Handling**: Modify the `context-update.mdc` rule similarly to `fix.mdc`.
  - *Description*: Using the rename-edit-rename workaround, modify the `context-update` rule. In step 4 ("Commit changes"), after the `mcp_MyMCP_commit` call, check the result/output for the specific pre-commit error message. If detected, perform the same actions as described in Task 3.1 (parse files, read tasks.md, check for existing tasks, add new refactoring tasks if needed, update tasks.md). Adjust the rule's flow: Instead of proceeding to step 5, call the `implementation` rule to address the newly added refactoring tasks.
  - *Impacted Files/Components*: `.cursor/rules/context-update.mdc`, `.cursor/memory-bank/workflow/tasks.md`
  - *Dependencies*: Task 1.1, Task 3.1
  - *Validation Criteria*: The `context-update` rule correctly detects the line-count error during its commit step, adds appropriate refactoring tasks to `tasks.md` if they don't exist, and calls `implementation`.

# Done

## UserBrief Modifications (Aug 7, 2024)
- [x] **Modify `execute_command` MCP Tool**: Changed `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_execution.js`. Set `MAX_CHARS_EXEC_PARTIAL` to 1500. Used `readLastLogChars` for pre-timeout completion. Added prefix `[Call get_terminal_output...]` if output length equals 1500 in both pre-timeout and timeout scenarios.
- [x] **Modify `get_terminal_status` MCP Tool**: Changed `.cursor/mcp/mcp-commit-server/mcp_tools/terminal_status.js`. Set `MAX_CHARS_STATUS` to 1500. Added prefix `[Call get_terminal_output...]` to `lastStdout` or `lastStderr` within `getFormattedTerminals` if length equals 1500, before combining into `last_output`.

## 1. Modify `commit` MCP Tool [Done]
- [x] **1.1 Implement Auto-CWD and Repo Name Reporting**: Refactor `.cursor/mcp/mcp-commit-server/mcp_tools/commit.js`, `server.js`, and `lib/process_manager.js`.
    - *Description*: Remove explicit `working_directory` argument. Implement automatic CWD detection (server default -> env var -> process.cwd). Add `git rev-parse --show-toplevel` execution after commit to get repo name. Include repo name and committed file list in the success message.
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/mcp_tools/commit.js`, `.cursor/mcp/mcp-commit-server/server.js`, `.cursor/mcp/mcp-commit-server/lib/process_manager.js`
    - *Dependencies*: Node.js, Git
    - *Validation Criteria*: `commit` tool automatically detects CWD, executes git commands correctly, and reports repo name and committed files on success.

## 2. Enhance `fix.mdc`: Add Regression Test Trigger [Done]
- [x] **1.1 Modify `fix.mdc` Final Step**: Add logic to conditionally call `test-implementation`.
    - *Description*: Update the final step ("Calling the next rule") in `fix.mdc`. Add a decision point: If the `fix` rule was invoked for an issue *not* originating from a failed automated test (e.g., called by `experience-execution`, user input, or other rules detecting non-test-covered problems), then the rule should conclude by calling `test-implementation`. The call to `test-implementation` should clearly state the goal: create a new test to cover the specific scenario that was just fixed, preventing regression. If the fix *was* for an automated test failure, the original logic for choosing the next rule should apply. Use the rename-edit-rename workaround.
    - *Impacted Files/Components*: `.cursor/rules/fix.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: The final step in `fix.mdc` includes logic to check the invocation context/reason and correctly calls `test-implementation` with the appropriate goal when the fix was for a non-test-covered issue.

## 1. Refactor `experience-execution.mdc`: Command Execution & Monitoring [In Progress]
- [x] **1.1 Modify Initial Execution (Step 2)**: Change Step 2 to always use `mcp_MyMCP_execute_command` with a fixed short timeout (e.g., 30 seconds).
    - *Description*: Update the instruction text in Step 2 to mandate the use of `mcp_MyMCP_execute_command` and specify a short initial timeout (30s). Remove mentions of long timeouts in this step.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: Step 2 text reflects the use of a short, fixed timeout (30s) for the initial command execution.
- [x] **1.2 Implement Monitoring Loop (New Step 2.5 / Modify Step 3)**: Add a new step or modify Step 3 to implement the iterative monitoring loop.
    - *Description*: Introduce logic after the initial execution (Step 2) to repeatedly call `