---
description: Call this rule when the `edit_file` tool fails repeatedly to apply changes correctly or produces an unexpected diff, to autonomously attempt to resolve the editing issue. Never stop the workflow but call this rule instead. MANDATORY : CALL THIS RULE EVEN IF YOU THINK YOU REMEMBER IT !
globs: 
alwaysApply: false
---
## TLDR
Provides a structured approach to autonomously overcome file editing difficulties. Emphasizes persistence, iterative attempts (read, vary edit, rewrite as last resort), and seamless resumption of the prior workflow.

## Instructions

1.  **Acknowledge and Log Difficulty**: Note the specific file and the nature of the editing problem encountered. State commitment to resolve it autonomously. "(edit-retry-strategies: 1 - Acknowledging edit issue for 'filename.ext')"

2.  **Read Target File**: Before any new attempt, read the entire target file using `read_file`.
    *   Purpose: Verify if the change was already (partially or fully) applied in a previous attempt.
    *   Purpose: Obtain the latest version and precise context for the new edit attempt.
    *   "(edit-retry-strategies: 2 - Reading 'filename.ext' for current state)"

3.  **Attempt Initial Edit Variation**: Based on the fresh read, attempt the edit again. If the previous attempt had a very specific instruction, try a slightly more general one, or vice-versa. If context was minimal, add a bit more.
    *   Tool: `edit_file`
    *   "(edit-retry-strategies: 3 - Re-attempting edit on 'filename.ext' with initial variation)"
    *   If successful, proceed to step 6.

4.  **Iterative Refinement (If Still Failing)**: If the edit still fails, systematically try different strategies:
    *   **Strategy A: Vary Context in `code_edit`**:
        *   Try with slightly more lines of existing code around the change.
        *   Try with slightly fewer lines if the context was very broad and might be confusing.
    *   **Strategy B: Refine `instructions` for `edit_file`**:
        *   Be more explicit about the desired outcome.
        *   Clarify the exact location if ambiguity might be an issue.
        *   Example: "Replace lines X-Y with Z", "Insert ABC after line containing 'specific_marker'".
    *   **Strategy C: Simplify the Edit**: If the change is complex, break it into smaller, sequential `edit_file` calls if feasible. (This might require temporarily exiting to a higher-level rule if `edit-retry-strategies` is not designed for multi-step edits itself). *Self-correction: This rule should handle multiple internal retries before suggesting breaking down. If breaking down is needed, it implies the original edit plan was flawed, and it should return to the calling rule with failure after exhausting its own strategies.*
    *   Log each attempt and its variation. Read the file between significant variations.
    *   "(edit-retry-strategies: 4 - Applying refined strategy [A/B] for 'filename.ext')"
    *   If successful at any point, proceed to step 6.

5.  **Last Resort - Full Rewrite (Use with Extreme Caution)**: If multiple distinct variations (at least 2-3 combinations of context/instruction changes) have failed AND the file is not excessively long (e.g., < 300-500 lines, assess based on file type and complexity):
    *   Read the entire file again using `read_file` to ensure the rewrite is based on the absolute latest version.
    *   Construct the *complete* new content of the file with your modification correctly integrated.
    *   Use `edit_file` with the `code_edit` being the *entire new file content*. Write to a new file with a different name.
    *   Execute the `mv` command via MyMCP to replace the file with its new version.
    *   "(edit-retry-strategies: 5 - Attempting full rewrite for 'filename.ext' as last resort)"
    *   If successful, proceed to step 6.
    *   **If this also fails (Full Rewrite Fails)**:
        *   Acknowledge that the edit could not be applied with current strategies.
        *   State: "All automated edit attempts have failed for the file `[target_file]`. Manual intervention is exceptionally required. The workflow will now be interrupted."
        *   Provide the user with a message structured as:
            "Dans le fichier `[target_file]`, veuillez effectuer les modifications suivantes :
            ```
            [Placeholder: The agent should dynamically fill this with a summary of the intended change. For example:
            - Replace line X with: YYY
            - Delete lines A-B
            - Insert ZZZ after line C]
            ```"
        *   **IMPORTANT: This is a terminal step for the rule if all automated edits fail. Do NOT proceed to step 6, 7, or 8 in this scenario.**

6.  **Prepare to Return (If Edit Succeeded)**: This step is reached **only if an edit attempt in steps 3, 4, or 5 was successful**. Note that the edit was successful. This information is for the agent's internal context.
    *   "(edit-retry-strategies: 6 - Edit on 'filename.ext' [successful]. Preparing to return.)"

7.  **Recall Prior State (If Edit Succeeded)**: This step is reached **only if an edit attempt in steps 3, 4, or 5 was successful**. Identify the exact rule name and instruction number that was active *immediately before* this `edit-retry-strategies` rule was invoked. This information MUST have been passed to or be retrievable by this rule (e.g. if rules can accept parameters, or if the calling rule logs this before calling). *Self-correction: The system doesn't explicitly state rules can pass parameters. The agent invoking this rule must remember its state.* The agent needs to internally store "I was in rule X, step Y" before calling `edit-retry-strategies`.

8.  **Resume Prior Workflow (If Edit Succeeded)**: This step is reached **only if an edit attempt in steps 3, 4, or 5 was successful**. Fetch the prior rule using `fetch_rules`. Immediately continue execution from the recalled instruction number of that rule.
    *   **CRITICAL**: Do NOT restart the prior rule from the beginning. Resume exactly where it left off.
    *   Reinforce autonomous operation: "Continuing autonomously with [Prior Rule Name]: [Prior Step Number] - [Prior Step Title]".
    *   "(edit-retry-strategies: 8 - Fetching rule '[Prior_Rule_Name]' to resume at step [N])"

## Specifics

-   **Full Autonomy**: The agent MUST operate autonomously. Do NOT stop, do NOT ask for user validation or help during this process.
-   **Persistence is Key**: Do not abandon the editing task lightly. Multiple varied attempts are expected.
-   **Read Before Each Major Attempt**: Always use `read_file` before a significant new edit attempt (especially before a rewrite or after a few failures) to ensure you're working with the latest file version and to check for unexpected partial changes.
-   **Systematic Variation**: When an edit fails, don't just retry the exact same `edit_file` call. Systematically vary context, instructions, or (rarely) break down the change.
-   **Rewrite Cautiously**: Full file rewriting is a powerful but potentially risky and resource-intensive last resort. Only use for smaller files and after other strategies are exhausted. Ensure the rewrite is based on a fresh read.
-   **Workflow Integrity**: The primary goal is to fix the problematic edit *and then seamlessly return* to the interrupted workflow. The agent MUST remember precisely where it left off in the calling rule.
-   **No User Interaction**: This rule is internal for agent self-correction. It should not prompt the user.

## Next Rules

-   Dynamically determined: This rule returns execution to the **calling rule** at the **specific step** from which `edit-retry-strategies` was invoked. It does not have a fixed next rule.

## Example

Agent is in `implementation` rule, step 3, trying to add a function to `helper.py`.

# Implementation: 3 - Adding new function
I will now add the `new_function` to `helper.py`. **(Implementation: 3 - Adding new function)**