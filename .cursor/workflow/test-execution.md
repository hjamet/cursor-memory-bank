---
description: Call this step to execute unit tests and analyze the results
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

4. **Call next step**
   - If at least one test improved without any regression → `context-update`
   - If no significant change → `context-update`
   - Otherwise, if at least one test regressed → `fix`

## Specifics

- Execute all available tests, not just new ones
- Do not attempt to fix errors (that's the role of the `fix` step)
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

2.  **Failing/Skipped Test Lines (Optional, one per test)**:
    *   `- [❌/ℹ️] [Test Name]: [Failure/Skip Reason] - (Evolution: [note])`
    *   `[Test Name]` is the full, unique identifier of the test.
    *   `[Failure/Skip Reason]` is the relevant error message or skip reason.
    *   `(Evolution: [note])` is a mandatory parenthesized note indicating the change from the last run. Examples:
        *   `(Evolution: new failure)`
        *   `(Evolution: same error)`
        *   `(Evolution: new regression)`
        *   `(Evolution: still skipped)`
        *   `(Evolution: error changed)`

- **Only** failing (❌) or skipped (ℹ️) tests are listed. Passed tests (✅) are only represented in the header count.

## Next Steps
- `fix` - if test regressions are detected
- `context-update` - if no regressions or no significant changes
- `implementation` - should not be called directly, `context-update` will handle this.

## Example

# Test-execution: 1 - Test execution
I will execute the main test suite to validate the latest changes. **(Test-execution: 1 - Test execution)**
[...calling `mcp_MyMCP_execute_command` with `npm test`...]
**(Test-execution - 1.npm_test in progress...)**
[...analysis of test results from stdout/stderr...]
**(Test-execution: 1 - Test execution)**

# Test-execution: 2 - Results analysis
I will now compare the results with the previous test run. **(Test-execution: 2 - Results analysis)**
[...reading old tests.md...]
[...comparison logic...]
**(Test-execution: 2 - Results analysis)**

# Test-execution: 3 - Results documentation
I will now document the results in the `tests.md` file using the new format. **(Test-execution: 3 - Results documentation)**
[...writing to tests.md...]
**(Test-execution: 3 - Results documentation)**

# Test-execution: 4 - Call next step
Based on the results, one test has regressed. I must now call the `fix` step.
The `fix` step must be called to address the test regression. **(Test-execution: 4 - Call next step)**

[...] (The workflow must continue uninterrupted)