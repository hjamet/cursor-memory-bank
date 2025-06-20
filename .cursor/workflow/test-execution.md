---
description: Call this rule to execute unit tests and analyze the results
globs: 
alwaysApply: false
---
## TLDR
Execute unit tests, analyze results and document successes and failures in `.cursor/memory-bank/workflow/tests.md` using a new summary and failing-tests-only format.

## Instructions

1. **Test execution**: Launch tests for implemented features using MCP tools:
   - Determine the command needed to run the relevant test suite(s) (e.g., `npm test`, `pytest`, `node tests/my_test.js`).
   - Use `mcp_MyMCP_execute_command` to run the test command. Set an appropriate `timeout` if tests might take time.
   - Check the `exit_code` and captured `stdout`/`stderr` from the result to determine success or failure.
   - Note precise error messages from `stdout`/`stderr` if the exit code is non-zero.
   - After each tool call, write **(Test-execution - 1.[Test name] in progress...)**

2. **Results analysis**: Compare with previous tests
   - Read the `.cursor/memory-bank/workflow/tests.md` file if it exists to get previous counts and failing/skipped test details for evolution tracking.
   - Identify improvements or regressions based on the current execution's raw results.
   - After each tool call, write **(Test-execution - 2.[Analysis] in progress...)**

3. **Results documentation**: Update `.cursor/memory-bank/workflow/tests.md`
   - Create or overwrite the file.
   - Write the **Header Line** (e.g., `✅{total_passed} ❌{total_failed} ℹ️{total_skipped}`) based on the current test run.
   - For each test that failed or was skipped in the current run:
     - Append a line following the format: `- [❌/ℹ️] [Test Name]: [Failure/Skip Reason] - (Evolution: [note change from previous state if known])`.
   - Ensure the file adheres strictly to the **tests.md: New Format Definition** section above.

4. **Call next rule**
   - If at least one test improved without any regression → `context-update`
   - If no significant change → `context-update`
   - Otherwise, if at least one test regressed → `fix`

## Specifics

- Execute all available tests, not just new ones
- Do not attempt to fix errors (that's the role of the `fix` rule)
- An "improvement" means a previously failing test now passes or a warning is resolved
- A "regression" means a previously successful test now fails or generates a warning
- To avoid losing the workflow, systematically write **(Test-execution - [number].[Name] in progress...)** between each step
- The file `.cursor\memory-bank\workflow\tests.md` should not exceed 250 lines: it should not be a history log, but simply the current state of the tests, with their evolution compared to the last execution indicated in parentheses. If there are errors, they can be described. There should be no dates or timestamps.

## tests.md: New Format Definition

The `.cursor/memory-bank/workflow/tests.md` file is now section-less and follows a specific format:

1.  **Header Line (Mandatory First Line)**:
    *   `✅{nbr_success} ❌{nbr_fails} ℹ️{nbr_skip}`
    *   Example: `✅17 ❌2 ℹ️1`
    *   This line provides an at-a-glance summary of all tests executed.

2.  **List of Failing/Skipped Tests (Optional, only if fails/skips > 0)**:
    *   If there are failing (❌) or skipped (ℹ️) tests, they are listed below the header line.
    *   **Successful tests (✅) are NOT listed individually.**
    *   Each failing/skipped test item starts with its emoji, followed by its name, a colon, a detailed description of the failure (or reason for skipping), and optionally, progress notes or evolution since the last run.
    *   Format for each item:
        *   `- ❌ [Test Name]: [Detailed explanation of the failure, including error messages if concise] - (Evolution: [e.g., new failure, same error, regression from ✅])`
        *   `- ℹ️ [Test Name]: [Reason for skipping] - (Evolution: [e.g., still skipped, newly skipped])`
    *   Example:
        ```markdown
        ✅17 ❌2 ℹ️1
        - ❌ TestUserAuthentication.test_login_with_invalid_token: TypeError: Object of type bytes is not JSON serializable - (Evolution: new failure)
        - ❌ TestAPIConnection.test_retry_mechanism: AssertionError: Expected 3 retry attempts, got 0 - (Evolution: same error as last run)
        - ℹ️ TestDataProcessing.test_large_file_processing_new_dataset: Skipped due to missing large dataset file - (Evolution: still skipped)
        ```

**Key Principles (adapted from former `tests-template.mdc`):**
*   **Clarity**: Precise descriptions for failures/skips.
*   **Emojis**: Use ✅, ❌, ℹ️ consistently.
*   **Evolution**: Optionally note if the status is an improvement, regression, or unchanged for failing/skipped tests.
*   **Detail for Failures**: Include concise error messages if helpful.
*   **Conciseness**: The file should be kept brief by only detailing problematic tests.

## **Using the Advanced MCP Terminal Tools:**

For executing shell commands (including tests), prefer the advanced MCP terminal tools for better control and monitoring:
1.  **Launch:** Call the `mcp_MyMCP_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds. It returns the `pid` and initial output/status after the timeout (default 15s) or command completion, whichever comes first. The command continues running in the background if the MCP timeout is reached.
2.  **Check Status:** Call the `mcp_MyMCP_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the list of all running/completed commands, their `pid`, `status` (`Running`, `Success`, `Failure`, `Stopped`), `exit_code`, and recent output. Providing a `timeout` waits for a status change.
3.  **Get Output:** Call the `mcp_MyMCP_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve the last N lines (default 100) of stdout/stderr for that process.
4.  **Stop & Cleanup:** Call the `mcp_MyMCP_stop_terminal_command` MCP tool with the target `pids` (array) and an optional `lines` count to terminate running commands, retrieve their final output, and remove them from tracking.
This workflow allows managing long processes without blocking and retrieving intermediate/final results reliably.

- Never skip calling the next rule

## Next Rules
- `fix` - If at least one test regressed
- `context-update` - If at least one test improved or no significant change (and no regression)

## Example

# Test-execution: 1 - Test execution
I begin by executing the unit tests using the MCP tools. **(Test-execution: 1 - Test execution)**
[...determining test command, e.g., "npm test"...]
[...calling `mcp_MyMCP_execute_command` with command="npm test", timeout=180...]
[...checking result exit_code and stderr/stdout...]
**(Test-execution: 1 - Test execution)**

# Test-execution: 2 - Results analysis
I compare the results with previous tests. I read the old `tests.md` (if it exists) to see if TestA, TestB, TestC had different statuses. **(Test-execution: 2 - Results analysis)**
[...reading old tests.md file... Assume TestA was ✅, TestB was ❌ (same error), TestC was ℹ️ (same reason).
**(Test-execution - 2.Comparison in progress...)**
[...results comparison: TestA regressed. TestB same. TestC same.
**(Test-execution: 2 - Results analysis)**

# Test-execution: 3 - Results documentation
I update the tests.md file with new results, following the new format. **(Test-execution: 3 - Results documentation)**
```json
// ... tool_code: print(default_api.edit_file(target_file=".cursor/memory-bank/workflow/tests.md", code_edit=\'\'\'
✅17 ❌2 ℹ️1
- ❌ TestA: Null Pointer - (Evolution: regression from ✅)
- ❌ TestB: Timeout - (Evolution: same error)
- ℹ️ TestC: Manual skip - (Evolution: still skipped)
\'\'\', instructions="Update tests.md with current results in new format.")) ...
```
**(Test-execution: 3 - Results documentation)**

# Test-execution: 4 - Call next rule
I must now call the appropriate rule based on test results. **(Test-execution: 4 - Call next rule)**
[...analysis of improvements and regressions...]
I note that [description of test status changes]. I will therefore call the [fix/context-update] rule because we have two tests that have progressed and no regression. **(Test-execution: 4 - Call next rule)**

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)