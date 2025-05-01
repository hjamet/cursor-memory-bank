---
description: Call this rule to analyze and correct test errors via an iterative execution-correction loop
globs: 
alwaysApply: false
---

## TLDR
Analyze test errors and fix them through an iterative execution-correction loop until all tests pass or truly complex issues (requiring major refactoring or showing no progress after 3 attempts) are identified and handed over to `request-analysis`. Retrieve high-level context when needed.

## Instructions

1.  **Error identification**: Analyze and catalog test errors
    *   Read `.cursor/memory-bank/workflow/tests.md` to understand test results
    *   Establish a precise list of failing tests to address and their error messages
    *   Write **(Fix: 1 - Error identification completed)** after this step

2.  **Correction loop**: For each failing test, iterate until fixed or handed over
    *   **2.1 Marking**: Always indicate **(Fix: 2 - Correction loop - [Test name] - Iteration [number])**
    *   **2.2 Analysis**:
        *   **(Optional) High-Level Context Retrieval**: Use `codebase_search` targeting the `.cursor_memory` directory with keywords from the error/test to find relevant high-level vision or context notes that might inform the fix.
        *   Examine files involved in the error and identify the cause. Use `<think></think>` for complex analysis. Don't hesitate either to use the codebase search tool !
        *   **(Optional but recommended) Regression Check**: If the error seems like a regression (a feature that worked previously is now broken), use `mcp_MyMCP_execute_command` to consult the Git history (`git log -p -- <file_path>`) for the relevant files to understand recent changes that might have introduced the bug. Consider reading or restoring previous versions if helpful.
        *   **Consider adding temporary logging** (e.g., `console.log`, `print` statements) directly into the code to understand the flow and variable states leading to the error, especially if:
            - You are unsure about the fix after initial analysis.
            - This is the 3rd iteration for this test without clear progress.
            - The test logic or the code under test seems particularly complex.
        *   **Remember to remove temporary logs** after the issue is resolved.
    *   **2.3 Research**: If needed, use `mcp_brave-search_brave_web_search` to find solutions for specific errors
    *   **2.4 Implementation**: Make the correction and document the changes
    *   **2.5 Test**: Execute ONLY the specific test currently being fixed using `mcp_MyMCP_execute_command` (determine the correct command, e.g., `pytest tests/test_module.py::test_function`) and analyze the result:
        *   If test passes :
            * **2.5.1 Update tests.md**: If the test passes, update the `.cursor/memory-bank/workflow/tests.md` file to reflect the new status of the test. Write **(Fix: 2 - Correction loop - [Test name] - Implementation [number] completed)** after this step.
            * **2.5.2 Quick commit**: Call the MCP tool named "Commit".
              - Use `type` = "fix"
              - Use `emoji` = ":wrench:"
              - Construct `title` = "fix([Test name]): Quick fix"
              - Construct `description` = "Applied quick fix for [Test name] after successful test run."
              - Provide these arguments to the MCP "Commit" tool. It handles staging automatically.
            * **(Situational) Consider Vision Note**: If the fix reveals a misunderstanding or needed clarification of high-level project goals/vision relevant to the error, consider suggesting the user add a note to `.cursor_memory` or asking for clarification, but do *not* create notes directly in the `fix` rule.
            * **2.5.3 Continue**: Move to the next failing test in the list and repeat the loop from step 2.1.
        *   If test fails but shows progress → Continue loop with new iteration for the *same* test.
        *   If **truly complex correction** (after 3 attempts *without any progress* OR requires *major* refactoring / a completely new implementation approach):
            *   Mark the test as **(Fix: 2 - Correction loop - [Test name] - Handing over to request-analysis)**
            *   Call the `request-analysis` rule, providing the problem description, context, and the need for a new approach.

3.  **Calling the next rule (only if loop completed without handover)**: Determine the next step based on results *if and only if* step 2.5 did not trigger a handover to `request-analysis`.
    *   `<think>`
        *   **Determine Invocation Context:** How was the `fix` rule invoked?
        *   Read `.cursor/memory-bank/context/activeContext.md`. Look for sections indicating the source of the problem (e.g., `## Test Execution Failure`, `## Experience Execution Anomaly`, `## User Reported Issue`).
        *   Set `invoked_by_test_failure = true` if the context clearly indicates this rule was called due to a failed automated test reported in `tests.md` (typically by `test-execution`).
        *   Set `invoked_by_test_failure = false` if the context indicates the issue came from another source (e.g., `experience-execution` analysis, user input) and likely lacks specific test coverage.
        *   If context is unclear, default to `invoked_by_test_failure = true` for safety (prioritizing running existing tests).
        *</think>`
    *   **Decision Logic:**
        *   First check for unprocessed comments in `.cursor/memory-bank/userbrief.md`.
            *   If unprocessed comments exist → call `consolidate-repo`.
        *   ELSE IF `invoked_by_test_failure == false`:
            *   Call `test-implementation`, instructing it to create a test case for the specific behavior/scenario that was just fixed to prevent regression.
        *   ELSE (i.e., `invoked_by_test_failure == true` or context unclear):
            *   Assuming all initially identified failing tests were addressed in the loop, call `test-execution` for final verification of the fixes against the existing test suite.
    *   Write **(Fix: 3 - Calling the next rule)**

## Specifics

-   The `<think></think>` token must be used for each complex correction requiring in-depth analysis
-   You should examinate the files you know related to the problem but you should also use the codebase search tool in case you are missing something.
-   For debugging, consider adding temporary logging (e.g., `console.log` statements) within the code to inspect values and control flow. Remember to remove these logs afterwards.
-   NEVER execute all tests, but ONLY the specific test you are currently fixing
-   Running the complete test suite is exclusively the responsibility of the `test-execution` rule
-   Document ONLY errors related to:
    *   API changes in libraries
    *   Non-intuitive framework behaviors
    *   Updates that modify existing functionalities
-   CRUCIAL: To avoid losing workflow tracking, ALWAYS indicate the current test and iteration

**Using the Advanced MCP Terminal Tools:**

For executing shell commands, prefer the advanced MCP terminal tools for better control and monitoring:
1.  **Launch:** Call the `mcp_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds. It returns the `pid` and initial output/status after the timeout (default 15s) or command completion, whichever comes first. The command continues running in the background if the MCP timeout is reached.
2.  **Check Status:** Call the `mcp_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the list of all running/completed commands, their `pid`, `status` (`Running`, `Success`, `Failure`, `Stopped`), `exit_code`, and recent output. Providing a `timeout` waits for a status change.
3.  **Get Output:** Call the `mcp_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve the last N lines (default 100) of stdout/stderr for that process.
4.  **Stop & Cleanup:** Call the `mcp_stop_terminal_command` MCP tool with the target `pid` and an optional `lines` count to terminate a running command, retrieve its final output, and remove it from tracking.
This workflow allows managing long processes without blocking and retrieving intermediate/final results reliably.

## Next Rules
-   `consolidate-repo` - If loop completes and unprocessed comments exist
-   `test-execution` - If loop completes and the fix was for issues identified by existing automated tests.
-   `test-implementation` - If loop completes and the fix was for issues NOT identified by existing automated tests (to add regression test).
-   `request-analysis` - Called directly from step 2.5 for truly complex issues, terminating this rule's execution.

## Example

[...fetching rule `fix`...] # Use your rule-calling tool to call the rule, then apply it.

# Fix: 1 - Error identification
I begin by reading the tests.md file to understand test errors. **(Fix: 1 - Error identification)**
[...reading .cursor/memory-bank/workflow/tests.md file...]

I've identified the following failing tests:
1.  TestUserAuthentication.test_login_with_invalid_token - TypeError: Object of type bytes is not JSON serializable
2.  TestDataProcessing.test_large_file_processing - MemoryError: Unable to allocate memory for operation
3.  TestAPIConnection.test_retry_mechanism - AssertionError: Expected 3 retry attempts, got 0
**(Fix: 1 - Error identification completed)**

# Fix: 2 - Correction loop - TestUserAuthentication.test_login_with_invalid_token - Iteration 1
**(Fix: 2 - Correction loop - TestUserAuthentication.test_login_with_invalid_token - Iteration 1)**

## 2.1 Marking
**(Fix: 2 - Correction loop - TestUserAuthentication.test_login_with_invalid_token - Iteration 1)**

## 2.2 Analysis
*(Optional) I search for high-level context in `.cursor_memory` related to authentication logic: [...]*
`codebase_search(query='authentication vision', target_directories=['.cursor/memory'])`
[...examining authentication code files...]

<think>
The error occurs because we're trying to JSON serialize a bytes object. Decoding to 'utf-8' before serialization should work.
</think>

## 2.3 Research
*I search the web for information on JSON serializing bytes objects.*
`mcp_brave-search_brave_web_search(query='python json serialize bytes error')`

## 2.4 Implementation
[...modifying the authentication code to decode bytes before JSON serialization...]
**(Fix: 2 - Correction loop - TestUserAuthentication.test_login_with_invalid_token - Implementation 1 completed)**

## 2.5 Test
[...determining command for specific test, e.g., `pytest tests/auth_tests.py::TestUserAuthentication::test_login_with_invalid_token`...]
[...calling `mcp_MyMCP_execute_command` with the specific test command...]
**(Fix: 2 - Correction loop - TestUserAuthentication.test_login_with_invalid_token - Test execution 1)**

Great! The test now passes. 
*(Situational) The error was simple, no need to reflect on high-level vision.*
Moving to the next failing test.

# Fix: 2 - Correction loop - TestDataProcessing.test_large_file_processing - Iteration 1
**(Fix: 2 - Correction loop - TestDataProcessing.test_large_file_processing - Iteration 1)**

## 2.1 Marking
**(Fix: 2 - Correction loop - TestDataProcessing.test_large_file_processing - Iteration 1)**

## 2.2 Analysis
[...examining data processing code...]
<think>
MemoryError indicates loading the whole file. A streaming approach is likely needed.
</think>

## 2.3 Research
*I search the web for Python techniques for processing large files efficiently.*
`mcp_brave-search_brave_web_search(query='python streaming large file processing memory efficient')`

## 2.4 Implementation
[...modifying the processor to use a basic streaming approach...]

## 2.3 Research
*I search the web for resolving Python NameErrors.*
`mcp_brave-search_brave_web_search(query='python NameError: name process_chunk is not defined')`

## 2.4 Implementation
[...implementing the missing function...]

## 2.3 Research
*I search the web again for advanced large file processing patterns.*
`mcp_brave-search_brave_web_search(query='python advanced large file processing memory management')`

## 2.4 Implementation
[...No further implementation attempt...]

## 2.5 Test
The test failed on the previous iteration, and analysis confirms it needs major refactoring beyond simple iteration.
**(Fix: 2 - Correction loop - TestDataProcessing.test_large_file_processing - Handing over to request-analysis)**

Calling `request-analysis` to handle the complex task of implementing efficient large file processing.
[Provide context: Problem="MemoryError during large file processing requires major refactoring (streaming/chunking insufficient)", Files=[...], Analysis="Initial attempts failed, needs new architectural approach."]

[...Here, the agent calls the rule 'request-analysis' using its rule calling tool...]

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)

**(Alternative Scenario in Step 3)**

# Fix: 3 - Calling the next rule (Scenario: Fix for non-test issue)
<think>
Determine Invocation Context: Reading activeContext.md... Found section '## Experience Execution Anomaly' detailing the issue fixed. This wasn't from tests.md.
Set invoked_by_test_failure = false.
</think>
Decision Logic:
Checking userbrief.md... No unprocessed comments.
invoked_by_test_failure is false.
Calling `test-implementation` to create a regression test for the specific behavior fixed.
**(Fix: 3 - Calling the next rule)**
[...calling tool 'fetch_rules' with rule_names=["test-implementation"]...]


