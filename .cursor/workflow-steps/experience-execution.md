## TLDR
Quickly test the recent changes manually. If the test is successful, commit the changes. If it fails, prepare to fix the issues. If you are interrupted, handle it gracefully.

## Instructions

1.  **Execute Manual Test**:
    - `<think>`
        - Based on the last implemented task, what is the most direct way to validate the changes?
        - What is the expected outcome of a successful test?
        - What would a failure look like?
    `</think>`
    - Perform the manual test. This could involve running a command, interacting with a UI, or checking a file's content.
    - Clearly state whether the test was a **SUCCESS**, a **FAILURE**, or if you were **INTERRUPTED**.

2.  **Report Outcome & Next Steps**:

    - **If the test was a SUCCESS**:
        - `<think>`
            - The test succeeded. The associated task is now complete. I must mark it as 'REVIEW'.
        `</think>`
        - **Call `mcp_MemoryBankMCP_update_task` to set the status of the related task to `REVIEW`.**
        - `<think>`
            - Formulate a clear and concise commit message that follows conventions. The message should summarize the changes that were just validated.
            - What is the correct emoji, type, title, and description for the commit?
        `</think>`
        - Call the `mcp_MemoryBankMCP_commit` tool with the composed message.
        - `<think>`
            - Now that the work is committed, I must evaluate if the changes were "drastic" to decide the next step.
            - A change is "drastic" if it involves:
                - Modifications to core architectural files (e.g., workflow rules, MCP server logic).
                - A large number of files being changed at once.
                - The completion of a major feature or epic.
            - Based on my last commit, were the changes drastic?
            - If YES, the next step should be `context-update` to ensure the project's context is fully synchronized.
            - If NO, and there are more tasks, the next step is `implementation`.
            - If NO, and there are no more tasks, `context-update` is still appropriate.
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to record the successful test and set the future step based on the evaluation above. **Utiliser l'argument `user_message` pour communiquer un résumé clair du succès de l'expérience à l'utilisateur, en incluant les résultats clés ou les métriques pertinentes (ex: "Expérience réussie: le test `npm test` a retourné 10/10 tests passés.").**

    - **If the test was a FAILURE**:
        - `<think>`
            - What was the exact nature of the failure?
            - What are the likely causes?
            - What information is crucial for the `fix` step?
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to document the failure and set the future step to `fix`. **Utiliser l'argument `user_message` pour communiquer un résumé clair de l'échec de l'expérience à l'utilisateur, en incluant les messages d'erreur ou observations pertinentes (ex: "Expérience échouée: la commande `npm start` a retourné une erreur `TimeoutError`.").**

    - **If you were INTERRUPTED**:
        - `<think>`
            - What was I trying to do when I was interrupted?
            - If I was trying to update a task's status (e.g., to 'APPROVED'), I should handle this to avoid a loop.
        `</think>`
        - If the interruption occurred during a task status update, change the task's status to **BLOCKED** using `mcp_MemoryBankMCP_update_task`. Add a comment explaining that the approval was interrupted by the user.
        - Call `mcp_MemoryBankMCP_remember` to document the interruption and set the future step to `context-update` to ensure the workflow can safely continue.

## Specifics
- This rule is for quick, targeted manual validation, not exhaustive testing.
- The outcome must be a clear choice: SUCCESS, FAILURE, or INTERRUPTED.
- A commit is mandatory after a successful test.
- The `remember` tool is used to transition to the next logical step.

## Next Steps
- `fix` - If the manual test failed.
- `implementation` - If the test was successful and the change was not drastic, and there are more tasks.
- `context-update` - If the test was successful and the change was drastic, or if no tasks are left, or if the process was interrupted.

## Example (Successful Test, Minor Change)

# Experience-Execution: 1 - Execute Manual Test
<think> I just implemented the JWT token generation in `auth.js`. I will run the associated test file `auth.test.js` to see if it passes and generates a token as expected. </think>
I will run the tests for the new authentication module.
`npm test -- src/auth/auth.test.js`
The test command finished successfully with all tests passing. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think>The test for task #42 succeeded. I will mark it as 'REVIEW'.</think>
[...calling `mcp_MemoryBankMCP_update_task` with task_id: 42, status: 'REVIEW'...]
<think> The change adds the JWT feature. A good commit message would be `feat(auth): Implement JWT generation`. I'll use the ✨ emoji. The description will detail the new endpoint. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '✨', type: 'feat', title: 'feat(auth): Implement JWT generation', description: '- Added /login endpoint to generate JWT...']
<think> The commit was successful. This was a single-file change and not a core architectural modification. The change was not drastic. I see other tasks are pending. The next step should be `implementation`. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested JWT generation", PRESENT: "Changes committed, task marked for review.", FUTURE: "Proceed to the next task in `implementation`.", user_message: "Expérience réussie : Les tests pour la génération JWT sont tous passés (12/12)." ...]

## Example (Successful Test, Drastic Change)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored three workflow rules (`.md` files) to streamline the agent's decision-making. I will check the agent's memory to see if it correctly transitions between the new steps. </think>
I will check the agent's memory logs.
`cat .cursor/memory-bank/agent_memory.json`
The logs show the agent correctly followed the new workflow path. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think>The test for the workflow refactoring (task #43) succeeded. I will mark it as 'REVIEW'.</think>
[...calling `mcp_MemoryBankMCP_update_task` with task_id: 43, status: 'REVIEW'...]
<think> The changes affected multiple core workflow files. This is a drastic architectural change. The commit message should reflect this. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '♻️', type: 'refactor', title: 'refactor(workflow): Streamline agent decision logic', description: '- Refactored experience-execution.md and implementation.md...']
<think> The commit was successful. Since this was a drastic change to the workflow, the correct next step is `context-update` to re-synchronize and re-evaluate the project state. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested the refactored workflow", PRESENT: "Drastic changes committed, task marked for review", FUTURE: "Proceed to `context-update` for project re-synchronization.", user_message: "Expérience réussie : Le remaniement des règles de workflow a été validé. L'agent suit correctement le nouveau flux."...]

## Example (Failed Test)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored the database connection pool. I'll try to start the server, which should now connect to the database immediately. </think>
I will attempt to start the server.
`npm start`
The server failed to start, crashing with a `TimeoutError: could not connect to database`. The outcome is a **FAILURE**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> The server can't connect to the database after my refactoring. It's likely an issue with the new connection string or pooling options. I need to investigate this in the `fix` step. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Tested the new DB connection logic by starting the server.", PRESENT: "The server failed to start with a connection timeout.", FUTURE: "Switch to the `fix` workflow to debug the database connection.", user_message: "Expérience échouée : Le serveur n'a pas pu démarrer et a retourné une erreur `TimeoutError: could not connect to database`."...]
