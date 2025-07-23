## TLDR
End the workflow when no more tasks or user requests are available. This rule provides a graceful stopping point for autonomous workflows regardless of workflow mode.

## Instructions

The autonomous workflow has reached a natural completion point. All tasks are complete, all user requests have been processed, and there is no further work to be done.

### 1. **Workflow Completion Status**

You have successfully completed all assigned work:
- All tasks are in "DONE" or "APPROVED" status
- All user requests have been processed and archived
- No pending work remains

### 2. **Summary Preparation**

Before concluding, prepare a summary of what was accomplished:
- List the main tasks that were completed
- Highlight any significant achievements or discoveries
- Note any important information for future reference

### 3. **Graceful Termination**

The workflow is now complete. You should:
1. Provide a clear summary of accomplishments
2. Indicate that the workflow has completed successfully
3. Stop execution without calling `next_rule`

**IMPORTANT**: This is the only workflow step where stopping is explicitly allowed and required. Do NOT call `mcp_MemoryBankMCP_next_rule` or `remember` from this step.

## Next Steps

None - the workflow is complete. 