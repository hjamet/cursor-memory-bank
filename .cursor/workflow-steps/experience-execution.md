
## TLDR
Execute potentially long-running commands (experiments, data processing, model training), iteratively monitor progress, analyze logs and results critically, and document outcomes.

## Instructions

1.  **Planning & Preparation**: Plan the command execution.
    *   `<think>`
        *   Identify the exact command(s) to execute based on the task context.
        *   Determine necessary arguments, input/output paths, and configurations.
        *   Estimate potential execution time.
        *   Consider if adjustments are needed for testing purposes (e.g., using a reduced dataset, fewer iterations) versus a full run.
        *   Consult relevant project files, documentation, or `techContext.md` if needed to confirm command details.
        *   Define expected outputs (files, database entries, log patterns).
        *   Outline the analysis steps needed for the results (including potential monitoring checkpoints).
        *</think>`
    *   Summarize the plan and the command(s) to be executed.
    *   **(Experience-Execution: 1 - Planning completed)**

2.  **Add Temporary Debug Logging**: Add temporary logging to help identify potential issues.
    *   `<think>`
        *   Identify the key files/scripts that will be executed or are central to the experiment.
        *   Determine appropriate logging points (e.g., function entry/exit, key variable values, error conditions).
        *   Choose logging method (e.g., print statements, logging library calls, debug flags).
        *   Plan where to add these temporary logs without disrupting core functionality.
        *</think>`
    *   Add temporary debug logging to relevant files to help monitor execution and identify potential issues.
    *   Document what logging was added and where for later removal.
    *   **(Experience-Execution: 2 - Temporary logging added)**

3.  **Initial Command Execution**: Start the command with a short timeout.
    *   Use the `mcp_MyMCP_execute_command` MCP tool.
    *   Provide the `command` string.
    *   Set a **fixed short timeout of 30 seconds (`timeout=30`)**. This is just to ensure the command starts without immediate errors.
    *   The tool returns the `pid` and initial status/output (potentially incomplete if timeout is reached). Record the `pid`.
    *   **(Experience-Execution: 3 - Initial execution initiated)**

4.  **Iterative Monitoring & Analysis**: Monitor the command's progress.
    *   Initialize `current_timeout = 15` (seconds).
    *   **Loop:** While the command identified by `pid` is still likely running (check status from previous iteration or assume running initially):
        *   Call `mcp_MyMCP_get_terminal_status` with the recorded `pid` and `timeout = current_timeout`. **IMPORTANT: `current_timeout` MUST NOT exceed 300 seconds (5 minutes).** If doubling the timeout would exceed 300, use 300 instead.
        *   `<think>`
            *   Analyze the status, exit code (if finished), and recent output returned by `get_terminal_status`.
            *   Does the output show expected progress? Are there new errors or warnings?
            *   Does the status indicate the command is still 'Running', 'Success', 'Failure', or 'Stopped'?
            *   **Anomaly Check:** Is there anything unexpected or strange in the output, even if not a clear error (e.g., unusually slow progress, strange log messages, unexpected file modifications suggested by logs)?
            *   **(Optional Investigation):** If anomalies are detected and warrant investigation *before* the command finishes, you MAY use `read_file` or `codebase_search` to check relevant source code or generated files *now* to understand the potential issue.
            *   **Decision:** Based on the analysis:
                *   **Stop Execution?** If a critical error is confirmed, or an anomaly is severe enough to halt -> Call `mcp_MyMCP_stop_terminal_command` with the `pid`, record the failure reason, **break the loop**, and prepare to go to Step 8 (Calling Next Rule, likely routing to `fix`).
                *   **Continue Monitoring?** If status is 'Running' and analysis shows normal progress or minor/investigated anomalies -> Double `current_timeout` (capping at 300s), **continue the loop**.
                *   **Finished?** If status is 'Success', 'Failure', or 'Stopped' -> Record the final state, **break the loop**, and proceed to Step 5 (Final Analysis).
            *</think>`
        *   **(Experience-Execution: 4 - Monitoring loop iteration completed)**

5.  **Final Result Analysis**: **Critically analyze** final logs **AND generated files**.
    *   Using the final status and complete output gathered (potentially from the last `get_terminal_status` or `stop_terminal_command` call):
    *   Examine the standard output and error streams for success indicators or error messages.
    *   **MANDATORY: Check for expected generated files** (defined in Step 1). Verify their existence.
    *   **MANDATORY: Critically analyze the CONTENT of key generated files** (e.g., result data, logs, configuration outputs). Use `read_file` if necessary.
        *   **Do NOT just check for existence or basic format.**
        *   **Look for:** Values within expected ranges, absence of errors in logs, correct structure/types, unusual patterns, consistency. Incorporate insights from any intermediate analysis done in Step 4's `<think>` blocks.
        *   Verify that their format and content **truly conform** to expectations (defined in Step 1).
    *   `<think>`
        *   Compare the final actual results (**including detailed file content analysis**) against the expected outcomes defined in the planning phase.
        *   Identify any discrepancies, errors, **anomalies**, unexpected results, or formatting issues found in the final console output OR the generated files.
        *   Determine if the execution was ultimately successful based on the **complete and CRITICAL analysis** (console and files).
        *   **Explicitly note any strange findings**, even if not technically an error according to initial expectations.
        *</think>`
    *   Summarize the **detailed critical analysis** findings, explicitly mentioning the state and **content assessment** of generated files and any anomalies found.
    *   **(Experience-Execution: 5 - Final Analysis completed)**

6.  **Documentation**: Document results.
    *   Create or update a dedicated documentation file (e.g., `results/[timestamp_or_name]/README.md`).
    *   Content Requirements: Command, parameters, summary of results (from Step 5), conclusions, links to generated files.
    *   Ensure discoverability.
    *   **(Experience-Execution: 6 - Documentation updated)**

7.  **Remove Temporary Debug Logging**: Clean up temporary logging if execution was successful.
    *   `<think>`
        *   Review the final analysis from Step 5.
        *   Was the execution ultimately successful without major issues that would require calling `fix`?
        *   If successful, proceed to remove the temporary logging added in Step 2.
        *   If there were issues that will lead to calling `fix`, keep the logging for debugging purposes.
        *</think>`
    *   **IF** the final analysis indicates success and no call to `fix` will be made:
        *   Remove the temporary debug logging that was added in Step 2.
        *   Restore files to their original state without the temporary logging.
    *   **ELSE** (if issues detected that will lead to `fix`):
        *   Keep the temporary logging in place to aid in debugging.
    *   **(Experience-Execution: 7 - Temporary logging cleanup completed)**

8.  **MCP Terminal Cleanup**: Ensure the executed command's resources are released (if not already stopped).
    *   `<think>`
        *   Identify the `pid` of the command executed.
        *   Check its final status from Step 4 or 5. If it was explicitly stopped or finished and cleaned up, this step might be skipped. Otherwise, proceed.
        *</think>`
    *   Call `mcp_get_terminal_status` one last time if needed to confirm state.
    *   Call `mcp_stop_terminal_command` with the correct `pid` to ensure termination and cleanup if it wasn't already confirmed stopped/completed and cleaned.
    *   **(Experience-Execution: 8 - MCP cleanup performed)**

9. **Commit changes**: Make a commit with the modifications using the MCP tool:
   - Determine the appropriate `emoji`, `type`, and `title` based on the experiment performed and documented.
   - **Construct a detailed `description`**: This description is CRITICAL and must be a comprehensive markdown-formatted text. Refer to the "Format for Detailed Commit Description" section in the `context-update.mdc` rule. It should summarize the experiment, parameters, results, analysis, observations, and a conclusion.
   - Call the `mcp_MyMCP_commit` tool with these arguments (`emoji`, `type`, `title`, `description`).
   - The tool handles staging automatically (equivalent to `git add .` or `git commit -a`).

10.  **Calling the next rule**: Decide the next step based on final analysis.
    *   `<think>`
        *   Review the final critical analysis summary from Step 5.
        *   Did the analysis explicitly note any anomalies or strange findings?
        *   Did the analysis conclude the execution failed or results were non-conformant (based on Step 5)?
        *   Should stable behaviors be "frozen" with tests based on the successful execution?
        *</think>`
    *   **Decision Logic:**
        *   IF final analysis (Step 5) detected problems, errors, or non-conformity → call `fix`, providing context.
        *   ELSE IF final analysis (Step 5) explicitly noted **anomalies or strange findings** (even if the execution technically succeeded) → call `task-decomposition`, instructing it to create a new task to investigate these specific anomalies.
        *   ELSE IF execution was successful AND there are stable behaviors that should be "frozen" with tests (behaviors unlikely to change) → call `test-implementation`.
        *   ELSE (execution successful, no anomalies noted, no need to freeze behaviors) → call `context-update`.
    *   **(Experience-Execution: 10 - Calling next rule)**

## Specifics
-   This rule uses iterative monitoring for potentially long commands.
-   Step 2 uses a **fixed 30s timeout** for initial execution check.
-   Step 3 uses `mcp_MyMCP_get_terminal_status` with **increasing timeouts, capped at 300s (5 minutes) per call**.
-   Critical analysis (Step 5) of logs AND file content is mandatory.
-   Use `<think>` blocks for planning, monitoring analysis, cleanup checks, and final rule decision.
-   Documentation (Step 6) is mandatory.

## Next Rules
-   `context-update` - If execution was successful and NO anomalies were noted in final analysis.
-   `fix` - If execution failed or results were non-conformant in final analysis.
-   `task-decomposition` - If execution succeeded BUT anomalies/strange results were noted during final critical analysis.

## Example (Conceptual)

# Experience-Execution: 1 - Planning & Preparation
<think> Plan: Run `long_script.py`. Expect ~10 mins. Output: `output.log`, `results.csv`. Log should end with 'Success'. CSV needs 3 columns. Monitor progress via log messages. </think>
**(Experience-Execution: 1 - Planning completed)**

# Experience-Execution: 2 - Add Temporary Debug Logging
<think> Temporary logging added to help monitor execution and identify potential issues. </think>
**(Experience-Execution: 2 - Temporary logging added)**

# Experience-Execution: 3 - Initial Command Execution
Executing `long_script.py` with 30s timeout.
[...calling `mcp_MyMCP_execute_command` with command="long_script.py", timeout=30... returns pid=67890]
**(Experience-Execution: 3 - Initial execution initiated)**

# Experience-Execution: 4 - Iterative Monitoring & Analysis
(Iteration 1) Checking status for pid=67890 with timeout=15s.
[...calling `mcp_MyMCP_get_terminal_status` with pid=67890, timeout=15...]
<think> Status: Running. Output shows initial setup logs, looks normal. Continue. </think>
(Iteration 2) Checking status for pid=67890 with timeout=30s.
[...calling `mcp_MyMCP_get_terminal_status` with pid=67890, timeout=30...]
<think> Status: Running. Output shows 'Processing batch 10/100'. Looks slow? Anomaly: maybe. Let's check the code briefly. `read_file('long_script.py')`. Hmm, batch size seems normal. Continue monitoring for now. </think>
(Iteration 3) Checking status for pid=67890 with timeout=60s.
[...calling `mcp_MyMCP_get_terminal_status` with pid=67890, timeout=60...]
<think> Status: Running. Output shows 'Processing batch 50/100'. Still seems ok. </think>
... (Loop continues with increasing timeouts up to 300s) ...
(Iteration N) Checking status for pid=67890 with timeout=300s.
[...calling `mcp_MyMCP_get_terminal_status` with pid=67890, timeout=300...]
<think> Status: Success. Exit code 0. Final logs look good. Proceed to final analysis. </think>
**(Experience-Execution: 4 - Monitoring loop iteration completed)**

# Experience-Execution: 5 - Final Result Analysis
<think> Final status was Success. Log file `output.log` contains 'Success'. `results.csv` exists. Read `results.csv`. Content check: 3 columns, data looks reasonable. No anomalies noted in final check. </think>
Analysis: Execution successful and results conform.
**(Experience-Execution: 5 - Final Analysis completed)**

# Experience-Execution: 6 - Documentation
[...updating docs, e.g., writing results/long_script_run_1/README.md...]
**(Experience-Execution: 6 - Documentation updated)**

# Experience-Execution: 7 - Remove Temporary Debug Logging
<think> Temporary logging removed as execution was successful. </think>
**(Experience-Execution: 7 - Temporary logging cleanup completed)**

# Experience-Execution: 8 - MCP Terminal Cleanup
<think> Command finished with Success. Cleanup likely handled by MCP status check. Double check status. </think>
[...optional call to `mcp_get_terminal_status`...]
[...optional call to `mcp_stop_terminal_command` if needed...]
**(Experience-Execution: 8 - MCP cleanup performed)**

# Experience-Execution: 9 - Making a commit
I prepare and make a commit with the changes made (experiment results, documentation) using the MCP commit tool. **(Experience-Execution: 9 - Making a commit)**
<think>
To construct the commit message for an experiment:
1.  `emoji` and `type`: Likely :test: `test` or :wrench: `chore` if it's about the experimental setup/results, or :sparkles: `feat` if the experiment itself *is* the new feature.
2.  `title`: A concise summary, e.g., "Experiment: `long_script.py` execution and analysis".
3.  `description`: This needs to be very detailed, following the standard markdown format (see `context-update.mdc` rule). I will need to synthesize information from:
    *   Step 1 (Planning & Preparation): Command, parameters.
    *   Step 5 (Final Result Analysis): Summary of results, critical analysis of generated files, anomalies.
    *   Step 6 (Documentation): Link to or summary of the documentation.
    *   Overall observations and a strong conclusion about the experiment's outcome.
This requires pulling together all findings from the rule's execution.
</think>
[...gathering information from previous steps and constructing the detailed emoji, type, title, and multi-section markdown description for the experiment commit...]
[...calling tool `mcp_MyMCP_commit` with appropriate arguments...]
**(Experience-Execution: 9 - Making a commit)**

# Experience-Execution: 10 - Calling the next rule
<think> Final analysis showed success and no anomalies. </think>
Calling `context-update`.
**(Experience-Execution: 10 - Calling next rule)**
[...calling tool 'fetch_rules' with rule_names=["context-update"]...]

### Important note on command execution

When executing commands using the `mcp_MyMCP_execute_command` tool, make sure that the command is correctly formatted.
