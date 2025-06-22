
## TLDR
Analyzes test errors from `tests.md`, iteratively attempts corrections, and validates fixes. This step is a focused debugging loop designed to resolve specific, identified test failures.

## Instructions

1.  **Error Identification**: Analyze `.cursor/memory-bank/workflow/tests.md` to identify all failing tests (marked with ❌). List them and their error messages. This forms the worklist for this step.

2.  **Correction Loop**: For EACH failing test identified in Step 1, perform the following cycle:
    *   **2.1. Code Analysis**: Analyze the source code related to the failing test. Use `read_file` and `codebase_search` to understand the context of the error.
    *   **2.2. Propose Correction**: Formulate a fix for the bug. This may involve logic changes, dependency updates, or configuration adjustments.
    *   **2.3. Apply Correction**: Use `edit_file` to apply the fix to the relevant file(s).
    *   **2.4. Single Test Execution**: Re-run **only the single failing test** that was just addressed. Use `mcp_MyMCP_execute_command` with the specific test command (e.g., `pytest tests/test_user.py::test_login_failure`).
    *   **2.5. Verification**: Analyze the result of the single-test run.
        *   **If it passes**, move to the next failing test in the list from Step 1.
        *   **If it still fails**, re-enter the loop at 2.1 for the *same* test, but try a different correction. Limit attempts per test to 3.
        *   **If after 3 attempts the test still fails**, mark the associated task as 🔴 BLOCKED in `tasks.md`, add a comment explaining why, and call `task-decomposition` to re-evaluate the problem. This terminates the current `fix` step execution.

3.  **Calling the next step (only if loop completed without handover)**: Determine the next step based on results *if and only if* step 2.5 did not trigger a handover to `task-decomposition`.
    *   `<think>`
        *   **Determine Invocation Context:** How was the `fix` step invoked?
        *   Read `.cursor/memory-bank/context/activeContext.md`. Look for sections indicating the source of the problem (e.g., `## Test Execution Failure`, `## Experience Execution Anomaly`, `## User Reported Issue`).
        *   Set `invoked_by_test_failure = true` if the context clearly indicates this step was called due to a failed automated test reported in `tests.md` (typically by `test-execution`).
        *   Set `invoked_by_test_failure = false` if the context indicates the issue came from another source (e.g., `experience-execution` analysis, user input) and likely lacks specific test coverage.
        *   If context is unclear, default to `invoked_by_test_failure = true` for safety (prioritizing running existing tests).
        *</think>`
    *   **Decision Logic:**
        * IF `invoked_by_test_failure == false`:
            *   Call `test-implementation`, instructing it to create a test case for the specific behavior/scenario that was just fixed to prevent regression.
        *   ELSE (i.e., `invoked_by_test_failure == true` or context unclear):
            *   Assuming all initially identified failing tests were addressed in the loop, call `test-execution` for final verification of the fixes against the existing test suite.
    *   Write **(Fix: 3 - Calling the next step)**

## Specifics

-   The `<think></think>` token must be used for each complex correction requiring in-depth analysis
-   You should examinate the files you know related to the problem but you should also use the codebase search tool in case you are missing something.

## **Using the Advanced MCP Terminal Tools:**

For executing shell commands (including tests), prefer the advanced MCP terminal tools for better control and monitoring:
1.  **Launch:** Call the `mcp_MyMCP_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds. It returns the `pid` and initial output/status after the timeout (default 15s) or command completion, whichever comes first. The command continues running in the background if the MCP timeout is reached.
2.  **Check Status:** Call the `mcp_MyMCP_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the list of all running/completed commands, their `pid`, `status` (`Running`, `Success`, `Failure`, `Stopped`), `exit_code`, and recent output. Providing a `timeout` waits for a status change.
3.  **Get Output:** Call the `mcp_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve the last N lines (default 100) of stdout/stderr for that process.
4.  **Stop & Cleanup:** Call the `mcp_stop_terminal_command` MCP tool with the target `pid` and an optional `lines` count to terminate a running command, retrieve its final output, and remove it from tracking.
This workflow allows managing long processes without blocking and retrieving intermediate/final results reliably.

## Next Steps
-   `consolidate-repo` - If loop completes and unprocessed comments exist
-   `test-execution` - If loop completes and the fix was for issues identified by existing automated tests.
-   `test-implementation` - If loop completes and the fix was for issues NOT identified by existing automated tests (to add regression test).
-   `task-decomposition` - Called directly from step 2.5 for truly complex issues, terminating this step's execution.

## Example

[...fetching step `fix`...] # Use your step-calling tool to call the step, then apply it.

# Fix: 1 - Error identification
I begin by reading the tests.md file to understand test errors. **(Fix: 1 - Error identification)**
[...reading .cursor/memory-bank/workflow/tests.md file, assuming new format, e.g.:
✅15 ❌3 ℹ️0
- ❌ TestUserAuthentication.test_login_with_invalid_token: TypeError: Object of type bytes is not JSON serializable - (Evolution: new failure)
- ❌ TestDataProcessing.test_large_file_processing: MemoryError: Unable to allocate memory for operation - (Evolution: same error)
- ❌ TestAPIConnection.test_retry_mechanism: AssertionError: Expected 3 retry attempts, got 0 - (Evolution: new regression)
...]

I've identified the following failing tests from `tests.md`:
1.  TestUserAuthentication.test_login_with_invalid_token - TypeError: Object of type bytes is not JSON serializable
2.  TestDataProcessing.test_large_file_processing - MemoryError: Unable to allocate memory for operation
3.  TestAPIConnection.test_retry_mechanism - AssertionError: Expected 3 retry attempts, got 0

I will now start the correction loop for these three tests. **(Fix: 1 - Error identification)**

# Fix: 2 - Correction loop

## Fix - 2.1: Correcting TestUserAuthentication.test_login_with_invalid_token

### Fix - 2.1.1: Code analysis
I'll analyze `TestUserAuthentication.py` and the related authentication logic to find the source of the `TypeError`. **(Fix: 2.1.1 - Code analysis)**
[... `read_file` on relevant python files ...]
[... `codebase_search` for `login_with_invalid_token` ...]
**(Fix: 2.1.1 - Code analysis)**

### Fix - 2.1.2: Propose correction
<think>The error suggests a JSON serialization issue. It's likely that a response object is not being correctly encoded to JSON before being returned. I will ensure the response is explicitly serialized using `json.dumps()`.</think>
**(Fix: 2.1.2 - Propose correction)**

### Fix - 2.1.3: Apply correction
I will now apply the fix to `auth_handler.py`. **(Fix: 2.1.3 - Apply correction)**
[... `edit_file` to add `json.dumps()` to the return statement ...]
**(Fix: 2.1.3 - Apply correction)**

### Fix - 2.1.4: Single test execution
I'll re-run just the failing test to verify the fix. **(Fix: 2.1.4 - Single test execution)**
[... `mcp_MyMCP_execute_command` with `pytest tests/test_authentication.py::TestUserAuthentication::test_login_with_invalid_token` ...]
**(Fix: 2.1.4 - Single test execution)**

### Fix - 2.1.5: Verification
The test passed. I'll move on to the next error. **(Fix: 2.1.5 - Verification)**

## Fix - 2.2: Correcting TestDataProcessing.test_large_file_processing
[...]

# Fix: 3 - Calling the next step
<think>
invoked_by_test_failure = true because I was fixing errors from tests.md.
</think>
Decision Logic:
invoked_by_test_failure is true.
Calling `test-execution` to verify all fixes and check for regressions.
**(Fix: 3 - Calling the next step)**
[...calling tool 'fetch_rules' with rule_names=["test-execution"]...]


