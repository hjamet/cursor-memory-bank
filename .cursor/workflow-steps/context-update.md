## TLDR
Performs advanced repository maintenance by cleaning temporary files, rewriting core context files for clarity, and committing the changes to ensure a clean and up-to-date project state.

## Instructions

1.  **Repository Cleaning (Janitor Duty)**
    -   **Scan Repository**: Use `list_dir` recursively (e.g., `list_dir -R .`) to get a full overview of the repository's file structure.
    -   **Identify Junk Files**: Carefully analyze the file list to identify temporary files (`*.tmp`, `*.bak`, `*.swp`), misplaced build artifacts, or other unnecessary files.
    -   **Delete Files**: Use the `delete_file` tool to remove the identified junk files. Exercise caution to avoid deleting important files. Log your reasoning for each deletion in your memory.

2.  **Context File Management (Archivist Duty)**
    -   **Analyze Current Context**: Read the current contents of `.cursor/memory-bank/context/techContext.md` and `.cursor/memory-bank/context/projectBrief.md`.
    -   **Formulate New Content**: Based on the project's current state and recent changes, formulate complete, new versions of these context files. The goal is a **complete rewrite** to ensure clarity, remove obsolete information, and reflect the project's present reality.
    -   **Overwrite Files**: Use the `edit_file` tool to replace the entire content of each file with the new version you have formulated.

3.  **Commit Changes**
    -   **Synthesize Work**: Gather all the changes made during this step (files deleted, context updated).
    -   **Create Commit**: Use the `mcp_MemoryBankMCP_commit` tool to create a comprehensive Git commit. Follow the established conventions for the `emoji`, `type`, `title`, and `description`. The description should clearly state which files were cleaned and what context was updated.

4.  **Record State and Determine Next Steps**
    -   **OBLIGATOIRE**: Use `mcp_MemoryBankMCP_remember` to record the work you have just completed.
    -   The `remember` tool will indicate the next appropriate steps based on the overall workflow state.

## Specifics
-   This rule is a maintenance step. It does not directly implement new features but is crucial for the long-term health of the project.
-   Be conservative when deleting files. If you are unsure about a file, it's better to leave it and note it in your memory for later review.
-   The context file rewrites should be comprehensive. Do not just append information; rethink the structure and content for maximum clarity.

## Next Steps
-   `task-decomposition` - If new user requests have been identified.
-   `implementation` - If there are pending tasks to be worked on.
-   `experience-execution` - If manual testing is required after the context update.

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