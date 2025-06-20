---
description: Rule to consolidate the repository, manage userbrief.md, and maintain a clean project structure
globs: 
alwaysApply: false
---
## TLDR
Consolidates user requests from a section-less, emoji-driven `userbrief.md`, manages item statuses (🆕, ⏳, 📌), and verifies memory file integrity.

## Instructions

1. **Process `userbrief.md` Items**: Analyze and update item statuses:
   - Read all lines from `.cursor/memory-bank/userbrief.md`.
   - Iterate through the lines:
     - If a line starts with `🆕 - ` or `- ` (treat as new input):
       - **Select only the first such unprocessed item per rule execution.** (To maintain focused processing).
       - Analyze its content to determine if it's an actionable task or a preference/directive.
       - If it's a task: Change the line to start with `⏳ - `.
       - If it's a preference: Change the line to start with `📌 - `.
       - Re-write the `userbrief.md` file with this single change.
       - **Stop processing further items in this rule execution.** Subsequent 🆕 items will be handled in later calls to this rule.
     - Lines starting with ⏳, 📌, or 🗄️ are generally left unchanged by this step of this rule (they are managed by their current status or by other rules like `task-decomposition`).

2. **Evaluation of user requests & Next Rule**: Decide next workflow step:
   - Re-read `.cursor/memory-bank/userbrief.md`.
   - IF any line now starts with `⏳ - ` (indicating a task was just marked for processing by this rule in step 1 OR was already pending from a previous run):
     - Extract the content of the first such `⏳` item.
     - Formulate this as the user request to be analyzed.
     - Call `task-decomposition` rule to process this specific request (which will then likely lead to `task-decomposition`).
   - ELSE (no ⏳ items found, meaning no new tasks were identified or are pending from `userbrief.md`):
     - Call `context-update` rule to continue the general workflow (e.g., check for structural issues if this rule was called for that purpose, or proceed if it was a routine check).

## Specifics

- This rule now focuses on processing one `🆕` user input item from `userbrief.md` at a time.
- It changes `🆕` to `⏳` (for tasks) or `📌` (for preferences).
- The `task-decomposition` rule is responsible for processing `⏳` items and changing them to `🗄️`.
- Avoid directly modifying the content of user requests; only update the leading emoji.

## Repository Structure (for reference)
```
.cursor/memory-bank/  
├── context/                 # Project context  
│   ├── projectBrief.md      # Project global vision  
│   ├── activeContext.md     # Current work context  
│   └── techContext.md       # Technologies and dependencies  
├── workflow/                # Workflow management  
│   ├── tasks.md             # List of tasks to accomplish
│   └── tests.md             # Test results tracking
src/                         # Project source scripts  
tests/                       # Unit and integration tests  
```

## userbrief.md: New Format Definition

The `.cursor/memory-bank/userbrief.md` file no longer uses H1 section titles (e.g., `# User Input`, `# Processing`). It is a flat list of items, each starting with an emoji indicating its status or type. This rule (`consolidate-repo`) is primarily responsible for processing new user inputs (🆕) and categorizing them.

**Emoji Legend & Handling by `consolidate-repo`:**
*   `🆕 - [User's original request or idea]`
    *   Represents raw user input. Users should ideally prefix new requests with `🆕 -` or just `- ` (which this rule will treat as 🆕).
    *   This rule identifies these items.
    *   If it's a task-like request, this rule changes 🆕 to ⏳.
    *   If it's a preference/directive, this rule changes 🆕 to 📌.
*   `⏳ - [Task identified, awaiting decomposition by task-decomposition rule]`
    *   This rule changes 🆕 to ⏳ for actionable tasks.
    *   The `task-decomposition` rule will later process these ⏳ items.
*   `📌 - [User preference or long-term directive to be retained]`
    *   This rule changes 🆕 to 📌 for preferences.
    *   These items are generally preserved unless explicitly changed by the user.
*   `🗄️ - [Request archived by task-decomposition after being added to tasks.md]`
    *   This rule does NOT create or directly manage 🗄️ items. They are an outcome of the `task-decomposition` rule.

**Key Principles (from former `userbrief-template.mdc`):**
*   **Persistence**: The `userbrief.md` file should generally not be emptied by the agent; only the user should clear its content.
*   **Status Updates**: When changing status, only the leading emoji should be modified by the agent, not the content of the request/preference itself unless explicitly instructed.
*   **Conciseness**: The file should be kept as concise as possible without losing information.
*   **User Input**: Users can add new items by prefixing with `🆕 - ` or just `- `.


## Next Rules

- `task-decomposition` - If a `🆕` item was converted to `⏳` (or an existing `⏳` item is found), to analyze this specific task.
- `context-update` - If no `🆕` items were processed into `⏳` tasks (e.g., only preferences found, or no new input).

## Example

# Consolidate-repo: 1 - Process `userbrief.md` Items
I begin by reading `.cursor/memory-bank/userbrief.md` to find new user inputs (starting with `🆕 - ` or `- `). **(Consolidate-repo: 1 - Process `userbrief.md` Items)**
[...reading `userbrief.md`... Assume it contains:
- `- Add a new feature X.
- Make the UI blue.
`]
I found the first new item: `- Add a new feature X.` This appears to be a task. I will change its prefix to `⏳ - `.
[...editing `userbrief.md` to become:
`⏳ - Add a new feature X.
- Make the UI blue.
` ...]
**(Consolidate-repo: 1 - Process `userbrief.md` Items)**

# Consolidate-repo: 2 - Integrity verification
(Assuming no integrity issues for this example path)
I'm now verifying the integrity of memory files. **(Consolidate-repo: 2 - Integrity verification)**
[...MCP find command...]
No integrity issues found.
**(Consolidate-repo: 2 - Integrity verification)**

# Consolidate-repo: 3 - Direct Cleanup
No cleanup needed. **(Consolidate-repo: 3 - Direct Cleanup)**

# Consolidate-repo: 4 - MCP Terminal Cleanup
No terminal commands were used that require cleanup in this path. **(Consolidate-repo: 4 - MCP Terminal Cleanup)**

# Consolidate-repo: 5 - Evaluation of user requests & Next Rule
I re-read `userbrief.md`. It now contains `⏳ - Add a new feature X.`. **(Consolidate-repo: 5 - Evaluation of user requests & Next Rule)**
I found a task marked `⏳`. I will formulate "Add a new feature X" as the request and call `task-decomposition`.
**(Consolidate-repo: 5 - Evaluation of user requests & Next Rule)**

[...Calling `task-decomposition` rule...]

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)  