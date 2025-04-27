# Active Context

## Current implementation context

- **Task Group:** Rule Enhancements (MCP Cleanup)
- **Current Tasks:**
    - 1.1 Add MCP Cleanup Step to `consolidate-repo` rule.
    - 1.2 Add Cleanup Note to `experience-execution` rule.
    - 1.3 Add Cleanup Note to `fix` rule.
- **Goal:** Enhance MCP terminal process cleanup by adding a dedicated step in `consolidate-repo` and reminder notes in other rules.
- **Details (Task 1.1):** Modify `consolidate-repo.mdc` Instructions to include a step calling `mcp_get_terminal_status` and then `mcp_stop_terminal_command` for finished terminals.
- **Details (Task 1.2 & 1.3):** Add a reminder sentence about using `mcp_stop_terminal_command` proactively to the Specifics section of `experience-execution.mdc` and `fix.mdc`.
- **Dependencies:** MCP tools (`mcp_get_terminal_status`, `mcp_stop_terminal_command`).

## Current Status

- Previous MCP server enhancements are complete.
- Focus is now on modifying rules to improve MCP terminal cleanup procedures.
- Completed `consolidate-repo` rule execution: processed `userbrief.md`, verified file integrity, cleaned up MCP terminals, updated `.gitignore`.

## Recent Decisions

- Decomposed the new user request into three tasks in `tasks.md`.

## Next Steps

1. Implement Task 1.1 (Modify `consolidate-repo.mdc`).  - *This task was done before the workflow interruption, but not committed. Need to re-verify/re-apply if needed.* 
2. Implement Task 1.2 (Modify `experience-execution.mdc`). - *This task was done before the workflow interruption, but not committed. Need to re-verify/re-apply if needed.*
3. Implement Task 1.3 (Modify `fix.mdc`).
4. Update `tasks.md`.
5. Proceed to the next rule (likely `implementation` to continue with Task 1.3).

## Important Notes

- Ensure the new step in `consolidate-repo.mdc` is placed appropriately within the existing instructions (e.g., after integrity verification, before evaluation).

## Lost workflow

- *This section is no longer relevant after successfully resuming the workflow via consolidate-repo.*