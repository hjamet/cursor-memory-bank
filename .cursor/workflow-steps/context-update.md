
## TLDR
Analyzes the provided context, updates context files, manages task statuses, and makes a commit following conventions. This step does not create any result files.

## Instructions
1. **Analyze available context**: 
   - Analyze the full context provided by the MCP server, including `projectBrief.md`, `techContext.md`, recent memories, and current tasks.
   - Read the userbrief to check for new user requests and preferences.

2. **Context update**: Update the context files if necessary.
   - Based on the analysis, determine if any context files need updates to reflect the latest changes.
   - If so, formulate the new content for the required files (`projectBrief.md`, `techContext.md`).
   - Use the `remember` tool to record the current state and learnings.

3. **Context cleanup**: 
   - When formulating new content, ensure it is concise, removes obsolete information, and maintains structural integrity.

4. **Tasks update**: Mark completed tasks as `DONE` using the `update_task` tool.

5. **Userbrief processing**: Check for new user requests and update their status if needed.
   - Use `read_userbrief` to get current requests
   - Process any new requests by updating their status or adding comments
   - Use `update_userbrief` to mark requests as processed

6. **Commit changes**: Make a commit with the modifications using the `commit` tool.
   - Determine the appropriate `emoji`, `type`, and `title`.
   - Construct a detailed `description`.

7. **Record state and determine next steps**: Use remember tool to record progress and get next steps.
   - Call `mcp_MemoryBankMCP_remember` to record the current state and context updates
   - The remember tool will indicate the appropriate next steps

## Specifics
- This step now operates on the assumption that all necessary context is provided by the MCP server at runtime, removing the need for direct file reads.
- The agent's responsibility is to analyze the provided context and formulate the *content* for any required updates.
- Mark tasks as 🟢 DONE only if all associated tests pass and the work for that task is fully completed.
- Use conventional commit format by adding an emoji to describe the operation performed
- Systematically delete old history entries that are no longer relevant
- NEVER end without either explicitly calling a next step or explicitly indicating that the workflow is complete
- The workflow must NEVER be considered complete if there are remaining tasks with 🟡 IN_PROGRESS or ⚪️ TODO emojis OR if there is at least one failing test (marked ❌) or with warning (marked ⚠️)
- For the commit, use the `mcp_MemoryBankMCP_commit` tool, which handles staging automatically.
- If all tasks are complete (meaning there are NO MORE tasks with 🟡 IN_PROGRESS or ⚪️ TODO emojis according to MCP task tools) AND all tests pass (ALL marked ✅), then:
   - Present a clear and concise synthesis of the work done
   - Summarize implemented features and resolved issues
   - Explicitly indicate that the workflow is successfully completed
   - Explicitly state: "The workflow is complete, no next step to call."
- If the workflow is not complete, call the appropriate next step

## Format for Detailed Commit Description
The `description` argument for the `mcp_MemoryBankMCP_commit` tool must be a detailed markdown-formatted string. It serves as a comprehensive record of the work performed. Structure it like a mini-article with the following sections:

```markdown
### Changes Made
*   Detailed bullet point list of all modifications.
*   Be specific: mention file names, functions changed, new features added, bugs fixed.
*   Example:
    *   Modified `src/moduleA/logic.py` to handle edge case X by adding a new validation step.
    *   Created new component `src/components/NewWidget.jsx` for displaying user data.
    *   Refactored `utils/helper.js` for improved performance by optimizing the `calculateValue` function.

### Testing Performed
*   Describe how the changes were tested.
*   Mention specific test scenarios, manual testing steps, or automated tests run.
*   If applicable, include results (e.g., "All 5 new unit tests for `logic.py` passed.").
*   Example:
    *   Manually tested the new widget with various user inputs (empty, long strings, special characters).
    *   Ran the full test suite (`npm test`), all 125 tests passed.
    *   Verified the fix for bug #123 by reproducing the original issue and confirming it's resolved.

### Observations & Learnings
*   Note any interesting observations, challenges encountered, or learnings during the development and testing process.
*   This could include unexpected behaviors, performance insights, or alternative approaches considered.
*   Example:
    *   Observed that the `calculateValue` optimization also reduced memory usage by 10%.
    *   Encountered an issue with library X's compatibility, requiring a workaround (describe briefly).
    *   Learned about a new API feature in Y that could be useful for future steps.

### Conclusion
*   Provide an overall summary of the work completed and its outcome.
*   State the impact of the changes (e.g., "This resolves critical bug #123 and improves system stability.").
*   Reiterate any key discoveries or insights.
*   Example:
    *   The implementation of the new user data widget is now complete and meets all specified requirements. This feature enhances user experience by providing a clear and interactive way to view their information. The refactoring of `calculateValue` has yielded significant performance gains.
```

**Emoji and Type Reference (for `title`):**
- :sparkles: `feat`: A new feature
- :bug: `fix`: A bug fix
- :memo: `docs`: Documentation only changes
- :recycle: `refactor`: A code change that neither fixes a bug nor adds a feature
- :white_check_mark: `test`: Adding missing tests or correcting existing tests
- :wrench: `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation
- :art: `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- :zap: `perf`: A code change that improves performance
- :construction: `wip`: Work in progress (use sparingly, prefer complete changes)
- :package: `build`: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- :construction_worker: `ci`: Changes to CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
- :rewind: `revert`: Reverts a previous commit

## Next Steps
- `task-decomposition` - If new user requests are found in userbrief
- `fix` - If issues are detected during analysis
- `implementation` - If tasks are still in progress or to do
- `experience-execution` - If implementation is complete and manual testing is needed
- `start-workflow` - If workflow is complete and ready for next iteration

## Example

# Context-update: 1 - Analyze available context
I begin by analyzing all the context provided by the server. **(Context-update: 1 - Analyze available context)**
**(Context-update: 1 - Analyze available context)**

# Context-update: 2 & 3 - Context update and cleanup
I will formulate new content for context files if needed, ensuring they are clean and concise. **(Context-update: 2 & 3 - Context update and cleanup)**
**(Context-update: 2 & 3 - Context update and cleanup)**

# Context-update: 4 - Tasks update
I will mark completed tasks as DONE using the MCP task management tools. **(Context-update: 4 - Tasks update)**
[...calling `mcp_MemoryBankMCP_update_task` for completed tasks...]
**(Context-update: 4 - Tasks update)**

# Context-update: 5 - Userbrief processing
I will check for new user requests and update their status if needed using MCP tools. **(Context-update: 5 - Userbrief processing)**
[...calling `mcp_MemoryBankMCP_read_userbrief` and `mcp_MemoryBankMCP_update_userbrief` as needed...]
**(Context-update: 5 - Userbrief processing)**

# Context-update: 6 - Making a commit
I prepare and make a commit with the changes made using the MCP commit tool. **(Context-update: 6 - Making a commit)**
<think>
To construct the commit message, I will synthesize information from the provided context (activeContext, projectBrief, tasks, tests) to fill in the detailed markdown description for the `mcp_MemoryBankMCP_commit` tool.
</think>
[...gathering information from provided context and constructing the commit arguments...]\
[...calling tool `mcp_MemoryBankMCP_commit`...]\
**(Context-update: 6 - Making a commit)**

# Context-update: 7 - Record state and determine next steps
I will now record the current state and let the remember tool determine the next appropriate steps. **(Context-update: 7 - Record state and determine next steps)**
[...calling `mcp_MemoryBankMCP_remember` with current state and context updates...]
**(Context-update: 7 - Record state and determine next steps)**