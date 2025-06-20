---
description: Call this rule to update context files and commit the changes.
globs: 
alwaysApply: false
---
## TLDR
Update context files to reflect changes, update tasks.md based on test results, and make a commit following conventions.

## Instructions
1. **Context update**: Read again and if necessary update the three context files, ensuring they adhere to their defined structures:
   - `.cursor/memory-bank/context/projectBrief.md`: Update global vision if impacted. Max 200 lines. Sections: Vision, Objectives (3-7 points), Constraints, Stakeholders, Success Metrics, History and Context (optional).
   - `.cursor/memory-bank/context/activeContext.md`: Reflect current state after modifications. Max 200 lines. Focus on recent (2-4 weeks) info. Sections: Current Focus, Ongoing Issues, Recent Decisions, Next Steps, Important Notes, Recent Learnings (optional).
   - `.cursor/memory-bank/context/techContext.md`: Add/modify technical information if necessary. Sections: Development Platform, Console/Shell, Installation/Dependency Management, Technology Stack, Code Conventions, Server Architecture/Deployment, Testing/Quality, Known Issues/Solutions.
   - IMPORTANT: You should always read the context files, even if you think you remember them.

2. **Context cleanup**: Clean context and workflow files, maintaining structural integrity:
   - Remove obsolete or redundant information.
   - Condense overly detailed sections.
   - Ensure each file remains under 200 lines (especially `projectBrief.md` and `activeContext.md`).
   - Prioritize conciseness while maintaining clarity and all mandatory sections for `projectBrief.md`, `activeContext.md`, and `techContext.md` as defined in Step 1.

3. **Userbrief Archival Commenting**: Read `.cursor/memory-bank/userbrief.md` and `.cursor/memory-bank/context/activeContext.md`. For any archived task (🗄️) in `userbrief.md` that the agent "remembers" working on (based on its description being found in `activeContext.md`) and that does not already have an agent comment, the agent will append a specific, informative comment in French.
    *   <think>
        *   I need to read `userbrief.md` and `activeContext.md`.
        *   For each archived task (🗄️) in `userbrief.md` that doesn't have an agent comment (-> 🧠):
        *     I will extract the `archived_task_description`.
        *     I will then search `activeContext.md` for this `archived_task_description` (or its key identifying parts, e.g., the first 50 characters).
        *     Let `my_french_comment = ""`.
        *     If I find relevant information in `activeContext.md` about this task (e.g., its completion status, any problems encountered, or information/resources I needed for it):
        *       I will use my understanding to formulate a concise, informative comment **in French**, summarizing this information.
        *       This comment should be similar in style to the user's examples:
        *         - "tâche terminée, tous les tests passent mais il y a encore un problème avec xxx qui a été ajouté à la liste des tâches"
        *         - "J'ai besoin de la clé d'authentification together.ai présente dans le fichier .env pour pouvoir effectuer cette opération"
        *       This is where I generate the actual `my_french_comment` string.
        *     Else if I find the task mentioned in `activeContext.md` (e.g., `archived_task_description[:50]` is in `active_context_content`) but no *specific* details for a rich comment as described above, I will formulate a more general French comment indicating the task was processed, for example:
        *       `my_french_comment = "La tâche concernant \'" + archived_task_description[:30].replace("'", "\\'") + "...\' a été traitée."` (This is a fallback, I should try to be more specific if possible based on context).
        *
        *     If `my_french_comment` is not empty:
        *       I will append `" -> 🧠 " + my_french_comment` to the task line in `userbrief.md`.
        *       And I will ensure `userbrief.md` is updated with these changes using the `edit_file` tool, joining all (potentially modified) lines.
        *     If I don't find the task in `activeContext.md` or cannot generate a meaningful comment, I will make no change to that line.
        *   After checking all lines, if I made any changes to `userbrief.md` content, I will use the `edit_file` tool to write the modified content back to the file.
    *   </think>
    *   (Agent will execute the logic described in the think block using available tools like `read_file` and `edit_file`.)

4. **tasks.md update**: Update `.cursor/memory-bank/workflow/tasks.md` based on test results and task completion:
   - Identify tasks that were 🟡 IN_PROGRESS and are now completed (e.g., based on `activeContext.md` or if the `implementation` rule just finished a task).
   - Change their status emoji from 🟡 IN_PROGRESS to 🟢 DONE.

5. **Commit changes**: Make a commit with the modifications using the MCP tool:
   - Determine the appropriate `emoji`, `type`, and `title` based on the changes made during the preceding rules.
   - **Construct a detailed `description`**: This description is CRITICAL and must be a comprehensive markdown-formatted text. Refer to the "Format for Detailed Commit Description" section below. It should summarize all work done, tests performed, observations, and a conclusion.
   - Call the `mcp_MyMCP_commit` tool with these arguments (`emoji`, `type`, `title`, `description`).
   - The tool handles staging automatically (equivalent to `git add .` or `git commit -a`).

6. **File integrity verification**: Look for structural problems:
   - Read the `.cursor/memory-bank/userbrief.md` file.
   - Use the MCP command execution tool via Git Bash to list all markdown files: `mcp_MyMCP_execute_command(command = "\"C:\\Program Files\\Git\\bin\\bash.exe\" -c \"find . -type f -name '*.md'\"")`
   - Analyze results to identify:
     - File duplicates
     - Misplaced files
     - Unnecessary temporary files
     - Files with incorrect names
   - If structural problems are identified OR if the `.cursor/memory-bank/userbrief.md` file contains unprocessed comments (marked with - symbol in the # User input section), call the `consolidate-repo` rule
   - Otherwise, continue with the next step: 7. **Call the next rule**

7. **Call the next rule**: Mandatory call to the next rule if the workflow is not complete:
   - Read the `.cursor/memory-bank/workflow/test.md` file
     - IF at least one test fails, call the `fix` rule
     - ELSE IF structural problems were identified OR if the `.cursor/memory-bank/userbrief.md` file contains unprocessed comments (marked with - symbol in the # User input section), call the `consolidate-repo` rule
     - ELSE, check `.cursor/memory-bank/workflow/tasks.md` for any tasks marked with 🟡 IN_PROGRESS or ⚪️ TODO emojis.
       - IF yes (tasks still active), call the `implementation` rule
       - ELSE (no 🟡 or ⚪️ tasks found, meaning all are 🟢 DONE, 🔴 BLOCKED, or 🔵 REVIEW), indicate that the workflow is complete.

## Specifics
- IMPORTANT: You should always read the context files, even if you think you remember them. It is a good way for you to keep a big picture in mind while staying focused on the details of what you are doing.
- Mark tasks as 🟢 DONE only if all associated tests pass and the work for that task is fully completed.
- Use conventional commit format by adding an emoji to describe the operation performed
- Systematically delete old history entries that are no longer relevant
- NEVER end without either explicitly calling a next rule or explicitly indicating that the workflow is complete
- The workflow must NEVER be considered complete if there are remaining tasks with 🟡 IN_PROGRESS or ⚪️ TODO emojis OR if there is at least one failing test (marked ❌) or with warning (marked ⚠️)
- For the commit, use the `mcp_MyMCP_commit` tool, which handles staging automatically.
- If all tasks are complete (meaning there are NO MORE tasks with 🟡 IN_PROGRESS or ⚪️ TODO emojis in the `tasks.md` file) AND all tests pass (ALL marked ✅), then:
   - Present a clear and concise synthesis of the work done
   - Summarize implemented features and resolved issues
   - Explicitly indicate that the workflow is successfully completed
   - Explicitly state: "The workflow is complete, no next rule to call."
- If the workflow is not complete, call the appropriate next rule

## Format for Detailed Commit Description
The `description` argument for the `mcp_MyMCP_commit` tool must be a detailed markdown-formatted string. It serves as a comprehensive record of the work performed. Structure it like a mini-article with the following sections:

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
    *   Learned about a new API feature in Y that could be useful for future tasks.

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

## Next Rules
- `consolidate-repo` - If file structure problems are detected or unprocessed comments exist in userbrief.md
- `fix` - If at least one test fails
- `implementation` - If at least one task is still in progress or to do and no test fails

## Example

# Context-update: 1 - Context update
I begin by updating the context files to reflect changes. **(Context-update: 1 - Context update)**
[...updating projectBrief.md file...]
**(Context-update: 1 - Context update)**
[...updating activeContext.md file...]
**(Context-update: 1 - Context update)**
[...updating techContext.md file...]
**(Context-update: 1 - Context update)**

# Context-update: 2 - Context cleanup
I clean up context files by removing obsolete information. **(Context-update: 2 - Context cleanup)**
[...cleaning up context files...]
**(Context-update: 2 - Context cleanup)**

# Context-update: 3 - Userbrief Archival Commenting
I will now check `userbrief.md` for archived tasks and add specific French comments if I remember working on them and relevant information is found in `activeContext.md`. **(Context-update: 3 - Userbrief Archival Commenting)**
<think>
The agent reads `.cursor/memory-bank/userbrief.md` and `.cursor/memory-bank/context/activeContext.md`.
For each archived task (starting with "🗄️ - ") in `userbrief.md` that does not already have an agent comment ("-> 🧠"):
1. It extracts the archived task description.
2. It searches for this description (or key parts of it) in `activeContext.md`.
3. If it finds relevant information (status, issues, needs), it formulates a concise and informative comment **in French**. For example, if `activeContext.md` states "Task 'Fix bug X' completed, but issue with Y", the comment could be "Tâche 'Corriger le bug X' terminée, mais un souci persiste avec Y.".
4. If it finds the task in `activeContext.md` but no specific details, it formulates a more general French comment, like "La tâche concernant 'Corriger le bug X...' a été traitée.".
5. It appends the generated comment to the task line in `userbrief.md` (e.g., "🗄️ - Fix display bug on homepage -> 🧠 Tâche corrigée, mais un souci d'alignement subsiste sur mobile.").
If changes are made, the agent saves `userbrief.md` using file manipulation tools.
</think>
[...agent performs actions described in the think block using available file tools...]
**(Context-update: 3 - Userbrief Archival Commenting)**

# Context-update: 4 - Updating tasks.md file
I update the tasks.md file by changing the status of completed tasks from 🟡 IN_PROGRESS to 🟢 DONE. **(Context-update: 4 - Updating tasks.md file)**
[...updating tasks.md file...]
**(Context-update: 4 - Updating tasks.md file)**

# Context-update: 5 - Making a commit
I prepare and make a commit with the changes made using the MCP commit tool. **(Context-update: 5 - Making a commit)**
<think>
To construct the commit message, I need to determine:
1.  `emoji` and `type`: Based on the overall nature of the changes (e.g., :sparkles: feat, :bug: fix).
2.  `title`: A concise summary of the changes.
3.  `description`: This needs to be very detailed, following the new markdown format. I will need to synthesize information from `activeContext.md`, possibly `projectBrief.md`, `tasks.md` (for what was planned), and `tests.md` (for test results) to fill in:
    *   `### Changes Made`: What code/files were altered? What was the specific change?
    *   `### Testing Performed`: How was it tested? What were the results?
    *   `### Observations & Learnings`: Any notable points during the process?
    *   `### Conclusion`: Overall summary and impact.
This requires gathering and structuring a lot of information.
</think>
[...gathering information and constructing the detailed emoji, type, title, and multi-section markdown description...]\
[...calling tool `mcp_MyMCP_commit` with appropriate arguments, including the detailed markdown description...]\
**(Context-update: 5 - Making a commit)**

# Context-update: 6 - File integrity verification
I now check the integrity of project files using the MCP command execution tool via Git Bash. **(Context-update: 6 - File integrity verification)**
[...calling tool `mcp_MyMCP_execute_command` with command="\"C:\\Program Files\\Git\\bin\\bash.exe\" -c \"find . -type f -name '*.md'\""...]
[...analyzing command results...]\nI have not identified structural problems in the files. I will now check the content of the `userbrief.md` file. **(Context-update: 6 - File integrity verification)**
[...checking .cursor/memory-bank/userbrief.md file...]
I don't see new tasks or advice to process. I will therefore proceed to the next step.
**(Context-update: 6 - File integrity verification)**

# Context-update: 7 - Calling the next rule
I now check the tests and remaining tasks (looking for 🟡 or ⚪️ emojis) to determine which rule to call. **(Context-update: 7 - Calling the next rule)**
[...checking tests and tasks...]
I see there are tasks with 🟡 or ⚪️ emojis and all tests pass. I will therefore call the `implementation` rule. **(Context-update: 7 - Calling the next rule)**

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)