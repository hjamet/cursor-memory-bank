## TLDR
Gracefully terminates the autonomous workflow when no active tasks or user requests are pending, specifically designed for task-by-task mode.

**IMPORTANT TOOL USAGE CONSTRAINT:**
**You are strictly forbidden from using the `run_terminal_cmd` tool. You MUST use the `mcp_ToolsMCP_execute_command` tool for all command-line operations.**

## Instructions

### When to Use This Rule

This rule should be called **ONLY** in the following specific scenario:
- **Workflow Mode**: `task_by_task` (workflow infini disabled)
- **Previous Step**: Coming from `context-update` 
- **System State**: No active TODO or IN_PROGRESS tasks and no unprocessed user requests
- **Purpose**: Provide a clean stopping point for controlled workflow execution

### Automatic Transition Logic

The `context-update` step should automatically transition to `workflow-complete` when:
1. **Mode Check**: `workflow_state.mode === "task_by_task"`
2. **Idle State**: All tasks are DONE/APPROVED/REVIEW and no new user requests exist
3. **Clean State**: System is in a stable, complete state ready for pause

### Implementation Steps

1.  **Final Memory Record**
    -   Call `mcp_MemoryBankMCP_remember` to record the final state.
    -   **PAST**: "I was in the context-update step and detected an idle state with workflow mode set to task-by-task."
    -   **PRESENT**: "I have confirmed that all tasks are complete and there are no new user requests. The workflow is configured for task-by-task mode, so I am now transitioning to a controlled stop."
    -   **FUTURE**: "I will wait for new user requests or tasks. The autonomous workflow is now paused until the user provides new instructions or switches back to infinite mode."

### Integration with Workflow Control

This rule works in coordination with the Streamlit interface workflow toggle:
- **Infinite Mode** (🟢): Agent continues automatically, never calls workflow-complete
- **Task-by-Task Mode** (🔴): Agent stops at workflow-complete after completing current cycle

The agent status indicator in the Streamlit sidebar will show:
- 🟢 **Actif** when the agent is running (any step except workflow-complete)
- 🔴 **Inactif** when the agent has reached workflow-complete or stopped

## CRITICAL
-   Do NOT call `mcp_MemoryBankMCP_next_rule`.
-   This rule is the designated end of the autonomous workflow loop.
-   Only use this rule when coming from `context-update` with `mode: "task_by_task"`
-   In infinite mode, `context-update` should NEVER transition to workflow-complete

## Example
# Workflow Complete: 1 - Record Final State and Inform User
All tasks are complete and no new requests are pending. The workflow is configured for task-by-task mode, so I am now pausing the autonomous workflow. The agent status indicator will show as inactive until new instructions are provided. **(Workflow Complete: 1 - Record Final State and Inform User)**
[...calling `mcp_MemoryBankMCP_remember` with the final state...]
**(Workflow Complete: 1 - Record Final State and Inform User)** 