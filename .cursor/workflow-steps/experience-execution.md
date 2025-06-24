## TLDR
Quickly test the recent changes manually. If the test is successful, commit the changes. If it fails, prepare to fix the issues.

## Instructions

1.  **Execute Manual Test**:
    - `<think>`
        - Based on the last implemented task, what is the most direct way to validate the changes?
        - What is the expected outcome of a successful test?
        - What would a failure look like?
    `</think>`
    - Perform the manual test. This could involve running a command, interacting with a UI, or checking a file's content.
    - Clearly state whether the test was a **SUCCESS** or a **FAILURE**.

2.  **Report Outcome & Next Steps**:

    - **If the test was a SUCCESS**:
        - `<think>`
            - Formulate a clear and concise commit message that follows conventions. The message should summarize the changes that were just validated.
            - What is the correct emoji, type, title, and description for the commit?
        `</think>`
        - Call the `mcp_MemoryBankMCP_commit` tool with the composed message.
        - `<think>`
            - Now that the work is committed, what is the next logical step?
            - Are there more `TODO` tasks waiting? If so, the next step is `implementation`.
            - If no tasks are left, `context-update` is appropriate to finalize the session.
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to record the successful test and set the future step.

    - **If the test was a FAILURE**:
        - `<think>`
            - What was the exact nature of the failure?
            - What are the likely causes?
            - What information is crucial for the `fix` step?
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to document the failure and set the future step to `fix`.

## Specifics
- This rule is for quick, targeted manual validation, not exhaustive testing.
- The outcome must be a clear binary choice: SUCCESS or FAILURE.
- A commit is mandatory after a successful test.
- The `remember` tool is used to transition to the next logical step (`implementation`, `context-update`, or `fix`).

## Next Steps
- `fix` - If the manual test failed.
- `implementation` - If the test was successful and there are more tasks to be done.
- `context-update` - If the test was successful and it's a good time to sync the project state.

## Example (Successful Test)

# Experience-Execution: 1 - Execute Manual Test
<think> I just implemented the JWT token generation in `auth.js`. I will run the associated test file `auth.test.js` to see if it passes and generates a token as expected. </think>
I will run the tests for the new authentication module.
`npm test -- src/auth/auth.test.js`
The test command finished successfully with all tests passing. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> The change adds the JWT feature. A good commit message would be `feat(auth): Implement JWT generation`. I'll use the ✨ emoji. The description will detail the new endpoint. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '✨', type: 'feat', title: 'feat(auth): Implement JWT generation', description: '- Added /login endpoint to generate JWT...']
<think> The commit was successful. I see there is another task in my TODO list to implement user permissions. The next step should be `implementation`. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested JWT generation", PRESENT: "Changes committed", FUTURE: "Proceed to the next task in `implementation`."...]

## Example (Failed Test)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored the database connection pool. I'll try to start the server, which should now connect to the database immediately. </think>
I will attempt to start the server.
`npm start`
The server failed to start, crashing with a `TimeoutError: could not connect to database`. The outcome is a **FAILURE**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> The server can't connect to the database after my refactoring. It's likely an issue with the new connection string or pooling options. I need to investigate this in the `fix` step. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Tested the new DB connection logic by starting the server.", PRESENT: "The server failed to start with a connection timeout.", FUTURE: "Switch to the `fix` workflow to debug the database connection."...]
