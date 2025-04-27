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

## Recent Decisions

- Decomposed the new user request into three tasks in `tasks.md`.

## Next Steps

1. Implement Task 1.1 (Modify `consolidate-repo.mdc`).
2. Implement Task 1.2 (Modify `experience-execution.mdc`).
3. Implement Task 1.3 (Modify `fix.mdc`).
4. Update `tasks.md`.
5. Proceed to the next rule (likely `context-update` as these are documentation/rule changes).

## Important Notes

- Ensure the new step in `consolidate-repo.mdc` is placed appropriately within the existing instructions (e.g., after integrity verification, before evaluation).

## Lost workflow

- **Reason:** Interrupted by user with new tasks in `userbrief.md` and attachment of `workflow-perdu.mdc`.
- **Last Action:** Completed modifications to `consolidate-repo.mdc` and `experience-execution.mdc` to add MCP cleanup steps (Tasks 1.1 and 1.2 of 'Rule Enhancements'). Task 1.3 (Modify `fix.mdc`) was not started.
- **Issue:** Examples within the modified rules might not accurately reflect the added cleanup steps.
- **Files Concerned:** `.cursor/memory-bank/userbrief.md`, `.cursor/rules/consolidate-repo.mdc`, `.cursor/rules/experience-execution.mdc`.
- **Next:** Need to re-evaluate `userbrief.md` using the standard workflow, likely starting from `consolidate-repo`.