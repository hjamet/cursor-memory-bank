---
description: Call this rule to implement the project's priority tasks.
globs: 
alwaysApply: false
---
## TLDR
Methodically implement tasks from a priority section, retrieve high-level context when needed, and document the process.

## Instructions

1. **Analyze available context**:
   - Analyze the active tasks and context provided by the MCP server.
   - Identify the priority task to work on (first "In Progress", then first "ToDo").
   - If all tasks are completed, move to the next rule.

2. **Task implementation**: For each task in the section
   - Display: `## Implementation - 2.number.[Section Name]: [Task Title]`
   - **(Optional) High-Level Context Retrieval**: Use `codebase_search` targeting the `.cursor_memory` directory with keywords from the task to find relevant high-level vision or context notes that might inform the implementation.
   - Evaluate if the task is complex and requires in-depth reflection
   - If yes, use the think token: `<think>In-depth reflection using chain of thought, comparison of different implementation approaches, etc.</think>`
   - Briefly summarize the conclusions of the reflection if applicable
   - Implement the solution for all sub-tasks in the current section
   - After each tool call, write **(Implementation - 2.number.[Section Name]: [Task Title] in progress...)**

3. **Task update**: Update tasks.md
   - Move section from "ToDo" to "In Progress" if necessary
   - Mark individual tasks as in progress or completed as appropriate

4. **Calling the next rule**: Mandatory decision point after completing ALL sub-tasks
   - Based on the implementation completed in this rule:
     - IF any testable feature was created or modified (scripts, functions, executable code) → `experience-execution` (DEFAULT for testing approach)
     - ELSE IF only non-testable changes were made (documentation, rule edits, git operations, repo cleanup) → `context-update`

## Specifics

- The think token `<think></think>` must be used for each complex individual task
- In-depth reflection must be verbalized in the think token before implementation
- Using the think token allows reasoning according to the chain of thought method and comparing different approaches
- Implement one task at a time, in logical order
- Comment complex parts of the code
- A feature is "testable" if it involves creating/modifying a script or function
- To avoid losing the workflow, systematically write **(Implementation - 2.number.[Section Name]: [Task Title] in progress...)** between each step
- Complete ALL sub-tasks in the current section before proceeding to Step 4

**VERY IMPORTANT : Using the Advanced MCP Terminal Tools:**

For executing shell commands, ALWAYS USE MyMCP and NEVER USE the terminal tool for better control and monitoring:
1.  **Launch:** Call the `mcp_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds. It returns the `pid` and initial output/status after the timeout (default 15s) or command completion, whichever comes first. The command continues running in the background if the MCP timeout is reached. I STRONGLY encourage using short timeouts, even to the point of monitoring command execution with increasingly longer timeouts via `mcp_get_terminal_status`. The idea is to be as efficient as possible and to be able to interrupt commands with minimal issue or in the face of an unusually long wait.
2.  **Check Status:** Call the `mcp_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the list of all running/completed commands, their `pid`, `status` (`Running`, `Success`, `Failure`, `Stopped`), `exit_code`, and recent output. Providing a `timeout` waits for a status change.
3.  **Get Output:** Call the `mcp_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve the last N lines (default 100) of stdout/stderr for that process.
4.  **Stop & Cleanup:** Call the `mcp_stop_terminal_command` MCP tool with the target `pid` and an optional `lines` count to terminate a running command, retrieve its final output, and remove it from tracking.
This workflow allows managing long processes without blocking and retrieving intermediate/final results reliably.

- Always call the appropriate next rule

## Next Rules
- `experience-execution`: If any testable feature created or modified (DEFAULT for testing approach)
- `context-update`: ONLY if non-testable changes (pure documentation, rule edits, git operations, repo cleanup)

## Example

# Implementation: 1 - Analyze available context
I begin by analyzing the tasks provided by the server to identify the highest priority section. **(Implementation: 1 - Analyze available context)**
**(Implementation: 1 - Analyze available context)**

# Implementation: 2 - Task implementation
I will implement each task in the section following a methodical approach. **(Implementation: 2 - Task implementation)**

## Implementation - 2.1.Development: Script creation
*(Optional) I search for high-level context in `.cursor_memory` related to script patterns or goals: [...]*
`codebase_search(query='script creation goals patterns', target_directories=['.cursor/memory'])`
This task is complex and requires in-depth reflection.

<think>
To create this script, I have several architecture options:
1. A monolithic architecture where all logic is in a single file
2. A modular architecture with separation of concerns
3. An event-driven approach

Let's compare these approaches:
- Option 1: Simple to implement but difficult to maintain long-term
- Option 2: Better maintainability but initially more complex
- Option 3: Flexible but potentially over-optimized for this use case

I think option 2 is most appropriate as it offers a good balance between maintainability and initial complexity. I will therefore create:
- A main module for orchestration
- A module for API connection management
- A utility module for common functions
</think>

After reflection, I determined that the best approach is to use a modular architecture with separation of concerns.

I begin by creating the main script with the required functionalities. **(Implementation: 2.1 - Script creation)**
[...script implementation...]
**(Implementation - 2.1.Development: Script creation in progress...)**
[...implementation continuation...]
**(Implementation: 2.1 - Script creation)**

## Implementation - 2.2.Development: Documentation
*(Optional) I search for high-level context in `.cursor_memory` related to documentation standards or project vision: [...]*
`codebase_search(query='documentation standards vision', target_directories=['.cursor/memory'])`
I add the necessary documentation to explain how the script works. **(Implementation: 2.2 - Documentation)**
[...adding documentation...]
**(Implementation - 2.2.Development: Documentation in progress...)**
[...documentation finalization...]
**(Implementation: 2.2 - Documentation)**

# Implementation: 3 - Task update
I update the tasks.md file to reflect task progress. **(Implementation: 3 - Task update)**
[...updating tasks.md file...]
**(Implementation: 3 - Task update)**

# Implementation: 4 - Calling the next rule
Since I created a new testable feature (the script), I must now call the `experience-execution` rule.
The experience-execution rule must be called to test the new feature. **(Implementation: 4 - Calling the next rule)**

[...calling tool 'fetch_rules' with rule_names=["experience-execution"]...]

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)