## TLDR
Gracefully terminates the autonomous workflow when no active tasks or user requests are pending.

## Instructions

1.  **Final Memory Record**
    -   Call `mcp_MemoryBankMCP_remember` to record the final state.
    -   **PAST**: "I was in the context-update step and detected an idle state."
    -   **PRESENT**: "I have confirmed that all tasks are complete and there are no new user requests. I am now transitioning to an idle state."
    -   **FUTURE**: "I will wait for new user requests or tasks. The autonomous workflow is now paused."

## CRITICAL
-   Do NOT call `mcp_MemoryBankMCP_next_rule`.
-   This rule is the designated end of the autonomous workflow loop.

## Example
# Workflow Complete: 1 - Record Final State and Inform User
All tasks are complete and no new requests are pending. The autonomous workflow is now paused. I will wait for new instructions. **(Workflow Complete: 1 - Record Final State and Inform User)**
[...calling `mcp_MemoryBankMCP_remember` with the final state...]\
**(Workflow Complete: 1 - Record Final State and Inform User)** 