---
description: Call this rule to analyze the user's request in detail and situate it in relation to the project objectives.
globs: 
alwaysApply: false
---
## TLDR
Analyzes user requests, explores existing code, searches for additional information, retrieves high-level context, stores relevant vision elements, and decomposes requests into concrete tasks organized in `.cursor/memory-bank/workflow/tasks.md` using an emoji-based status system.

## Instructions

1. **Request analysis**: Understand the user's request:
   - Analyze the user request provided by the MCP server.
   - Identify requested features or modifications.
   - Extract important keywords and concepts.

2. **Code analysis**: Identify concerned files and symbols:
   - Use `codebase_search` (up to 3 times) based on request keywords.
   - Optionally, use `tree` to visualize directory structure.
   - Strictly forbidden: listing folders/files, reading specific files, or using any other tool.

3. **Additional research**: Consult documentation and resources:
   - Use `mcp_Context7_*` tools for library documentation.
   - Use `mcp_brave-search_brave_web_search` for general research (max 5 searches).

4. **New tasks integration**: Structure new tasks in `tasks.md`.
   - Decompose the user request into concrete tasks and sub-tasks.
   - Add them to `tasks.md` using the `⚪️ TODO` emoji and the defined structure.

5. **Userbrief archiving**: Update the processed request via the MCP tool.
   - Call `mcp_MemoryBank_update-userbrief` with `action: 'mark_archived'` and the `id` of the request being processed.

6. **Call next rule**: Mandatory call to `implementation`.

## Specifics
- If you were called from consolidate-repo, consider the formulated request as the user request to analyze
- If the brief is empty without explicit request, consider tasks.md content as request
- Strict tool limits:
  - Phase 2 (Code analysis): only code base search (max 3) and tree
  - Phase 3 (Research): only mcp_Context7_* tools OR `mcp_brave-search_brave_web_search` (max 5 searches)
- Never mention planned modifications to context files (.cursor/memory-bank/* or .cursor/memory/*) unless creating a new vision note.
- Group similar tasks under common main task structures, even if apparently different.
- Favor detailed descriptions for each task item.
- Minimize dependencies between major tasks where possible.
- IMPORTANT: Do not add new tasks to `userbrief.md`.
- IMPORTANT: Crucially, NEVER archive an item in `userbrief.md` (Step 8) if its corresponding task(s) were NOT successfully added to `.cursor/memory-bank/workflow/tasks.md` in Step 7.
- IMPORTANT: Only process items marked with ⏳ in `userbrief.md`. Never process items marked with other emojis or even simple "-".

## tasks.md: New Format Definition

The `.cursor/memory-bank/workflow/tasks.md` file no longer uses H1/H2 section titles (e.g., `# In Progress`, `# ToDo`). It is a flat list of task items, each starting with an emoji indicating its status. This rule (`task-decomposition`) is primarily responsible for creating new tasks (usually with ⚪️) and structuring them.

**Emoji Legend & Handling by `task-decomposition`:**
*   `⚪️ TODO`: For new tasks or sub-tasks. This rule will primarily add tasks with this emoji.
*   `🟡 IN_PROGRESS`: Tasks currently being worked on (status set by `implementation` or `context-update` rules).
*   `🟢 DONE`: Completed tasks (status set by `implementation` or `context-update` rules).
*   `🔴 BLOCKED`: Tasks that cannot proceed.
*   `🔵 REVIEW`: Tasks awaiting review.

**Task Item Structure:**
Each task, regardless of status, should generally follow this structure:
```markdown
[EMOJI] **[Concise Title - Main Task or Sub-Task Numbering, e.g., 1. or 1.1]**
    *   **Description**: [Detailed explanation of what needs to be done.]
    *   **Impacted Rules/Files**: [List of rules or files affected by this task.]
    *   **Dependencies**: [List of other tasks this one depends on, if any. Use task numbers if available.]
    *   **Validation**: [Clear criteria to determine when the task is successfully completed.]
```
- Main tasks can be numbered (e.g., `⚪️ **1. Main Task Title**`).
- Sub-tasks should be indented and can use sub-numbering (e.g., `    *   ⚪️ **1.1. Sub-Task Title**`).
- The `---` separator can be used to visually group related sets of tasks if helpful, but is not structurally mandatory.

## Next Rules
- `implementation` - To begin implementing tasks.

## Example

# Task-decomposition: 1 - Request analysis
I begin by analyzing the user's request to properly understand their demand. **(Task-decomposition: 1 - Request analysis)**
[...request analysis...]
I identified the following key elements in the request: [...] **(Task-decomposition: 1 - Request analysis)**
*I search for existing high-level context notes related to these keywords in `.cursor_memory`.*
`codebase_search(query='...', target_directories=['.cursor/memory'])`
*If the user stated a new high-level vision element like 'The UI should feel modern and clean', I create a note:*
`edit_file(target_file='.cursor/memory/ui_vision_modern_clean.md', code_edit='The user wants a modern and clean UI.', instructions='Create new vision note.')`
**(Task-decomposition: 1 - Request analysis)**

# Task-decomposition: 2 - Code analysis
I begin by performing semantic searches to identify relevant files.
Let's perform a first semantic search: **(Task-decomposition: 2 - Code analysis)**
[...first semantic search...]
Let's perform a second semantic search: **(Task-decomposition: 2 - Code analysis)**
[...second semantic search...]
Let's visualize the directory structure to better understand the organization: **(Task-decomposition: 2 - Code analysis)**
[...tree command...]
I now better understand the code and relevant files. **(Task-decomposition: 2 - Code analysis)**

# Task-decomposition: 3 - Additional research
I need to understand how to use the 'some-obscure-library'. I will use the MCP Context7 tools for this. **(Task-decomposition: 3 - Additional research)**
[...calling `mcp_Context7_resolve-library-id` with libraryName="some-obscure-library"...]
[...calling `mcp_Context7_get-library-docs` with the resolved ID...]
Alternatively, I might search the web for general patterns related to [...]. **(Task-decomposition: 3 - Additional research)**
`mcp_brave-search_brave_web_search(...)`
**(Task-decomposition: 3 - Additional research)**

# Task-decomposition: 4 - Analyze available context
I begin by analyzing the tasks and user requests provided by the server. **(Task-decomposition: 4 - Analyze available context)**
I identified several items marked with ⏳. I will prepare them for integration into `tasks.md` in step 6.
**(Task-decomposition: 4 - Analyze available context)**

# Task-decomposition: 5 - Completed tasks archival/removal
The tasks X, Y, and Z are marked as 🟢 DONE aren't linked to our current focus. I will remove them from `tasks.md` to keep it clean and relevant. **
**(Task-decomposition: 5 - Completed tasks archival/removal)**

# Task-decomposition: 6 - New tasks integration
I decompose the main request and the identified ⏳ userbrief items into concrete tasks in `tasks.md`, using the new emoji-based format. **(Task-decomposition: 6 - New tasks integration)**
```json
// ... tool_code: print(default_api.edit_file(target_file=".cursor/memory-bank/workflow/tasks.md", code_edit=\'\'\'
// ... existing tasks ...
⚪️ **3. New Main Task from Request**
    *   **Description**: [Detailed description of the new main task based on the original user request or active context.]
    *   **Impacted Rules/Files**: [List relevant files/rules.]
    *   **Dependencies**: [List dependencies.]
    *   **Validation**: [Define validation criteria.]

⚪️ **4. Task from Userbrief Item 1**
    *   **Description**: [Description based on the ⏳ userbrief item.]
    *   **Impacted Rules/Files**: [files/rules.]
    *   **Dependencies**: [dependencies.]
    *   **Validation**: [validation criteria.]
    *   **Sub-Tasks**:
        *   ⚪️ **4.1. Sub-task for Userbrief Item 1**
            *   **Description**: [Detailed sub-task description.]
            *   **Impacted Rules/Files**: [files/rules.]
            *   **Dependencies**: [dependencies.]
            *   **Validation**: [validation criteria.]
\'\'\')) ...
```
**(Task-decomposition: 6 - New tasks integration)**

# Task-decomposition: 7 - Userbrief archiving
Now that the tasks from userbrief have been integrated into `tasks.md`, I will ensure the original items in `userbrief.md` are updated from ⏳ to 🗄️. **(Task-decomposition: 7 - Userbrief archiving)**
// ... tool_code to modify userbrief.md ...
**(Task-decomposition: 7 - Userbrief archiving)**

# Task-decomposition: 8 - Call next rule
I must now call the `implementation` rule to begin work on the newly structured tasks.
The `implementation` rule must be called to begin implementing the tasks. **(Task-decomposition: 8 - Call next rule)**
// ... tool_code: print(default_api.fetch_rules(rule_names=["implementation"])) ...

[...] (The workflow must continue uninterrupted)