---
description: Call this step to implement the project's priority tasks.
globs: 
alwaysApply: false
---
## TLDR
Methodically implement tasks from a priority section, retrieve high-level context when needed, and document the process.

## Instructions

1. **Task analysis**: 
   -   Analyze the active tasks provided by the MCP server.
   -   Identify the priority task to work on (first "In Progress", then first "ToDo").

2. **Task implementation**: For each task in the section
   -   Display: `## Implementation - 2.number.[Section Name]: [Task Title]`
   -   Implement the solution for all sub-tasks in the current section
   -   After each tool call, write **(Implementation - 2.number.[Section Name]: [Task Title] in progress...)**

3. **Task update**: Update tasks.md
   -   Move section from "ToDo" to "In Progress" if necessary
   -   Mark individual tasks as in progress or completed as appropriate

4. **Calling the next step**: Mandatory call to `next_step`.

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
2.  **Check Status:** Call the `mcp_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the list of all running/completed commands, their `pid`, `status` (`Running`, `Success`, 'Failure', 'Stopped'), `exit_code`, and recent output. Providing a `timeout` waits for a status change.
3.  **Get Output:** Call the `mcp_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve the last N lines (default 100) of stdout/stderr for that process.
4.  **Stop & Cleanup:** Call the `mcp_stop_terminal_command` MCP tool with the target `pid` and an optional `lines` count to terminate a running command, retrieve its final output, and remove it from tracking.
This workflow allows managing long processes without blocking and retrieving intermediate/final results reliably.

- Always call the appropriate next step

## Next Steps
- `experience-execution`: If any testable feature created or modified (DEFAULT for testing approach)
- `context-update`: ONLY if non-testable changes (pure documentation, step edits, git operations, repo cleanup)

## Example

# Implementation: 1 - Task analysis
I begin by reading the tasks.md file to identify the highest priority section. **(Implementation: 1 - Task analysis)**
[...reading tasks.md file...]
**(Implementation: 1 - Task analysis)**

# Implementation: 2 - Active context update
I will update the active context to document what I will be working on. **(Implementation: 2 - Active context update)**
[...reading activeContext.md file...]
[...updating with relevant information for tasks to perform...]
[...adding information researched online...]
**(Implementation: 2 - Active context update)**

# Implementation: 3 - Task implementation
I will implement each task in the section following a methodical approach. **(Implementation: 3 - Task implementation)**

## Implementation - 3.1.Development: Script creation
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

I begin by creating the main script with the required functionalities. **(Implementation: 3.1 - Script creation)**
[...script implementation...]
**(Implementation - 3.1.Development: Script creation in progress...)**
[...implementation continuation...]
**(Implementation: 3.1 - Script creation)**

## Implementation - 3.2.Development: Documentation
I add the necessary documentation to explain how the script works. **(Implementation: 3.2 - Documentation)**
[...adding documentation...]
**(Implementation - 3.2.Development: Documentation in progress...)**
[...documentation finalization...]
**(Implementation: 3.2 - Documentation)**

# Implementation: 4 - Task update
I update the tasks.md file to reflect task progress. **(Implementation: 4 - Task update)**
[...updating tasks.md file...]
**(Implementation: 4 - Task update)**

# Implementation: 5 - Calling the next step
Since I created a new testable feature (the script), I must now call the `experience-execution` step.
The experience-execution step must be called to test the new feature. **(Implementation: 5 - Calling the next step)**

[...calling tool 'fetch_rules' with rule_names=["experience-execution"]...]

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following step, then the next, etc., without ever stopping -> It is completely autonomous.)