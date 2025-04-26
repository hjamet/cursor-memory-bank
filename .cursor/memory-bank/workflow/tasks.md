# In Progress

## 3. Repository Cleanup


# Done

## [Task Group - e.g., Rules, Installation, Cleanup]
[x] **Create `new-chat` Rule**:
    - Description: Create a new rule `.cursor/rules/new-chat.mdc` allowing users to trigger a state save (summary, current rule name) to `activeContext.md` using a specific `<SYSTEM>` block, preparing for a clean restart in a new chat session. The rule must also define the agent's behavior for resuming from this saved state.
    - Files: `.cursor/rules/new-chat.mdc`

[x] **Replace ⬜ Emoji in Rules**:
    - Description: Replace the white square emoji (⬜) with a hyphen (-) in all rule files referencing it for userbrief.md processing status.
    - Files: `.cursor/rules/context-loading.mdc`, `.cursor/rules/context-update.mdc`, `.cursor/rules/consolidate-repo.mdc`, `.cursor/rules/architect.mdc`, `.cursor/rules/templates/userbrief-template.mdc`

[x] **Cleanup Test Logs**:
    - Description: Review the `.log` files in the `tests/` directory (`exit_codes.log`, `test_*.log`). Decide whether to delete them or add them to `.gitignore`.
    - Files: `tests/*.log`, `.gitignore`

[x] **General Repository Cleanup Review**:
    - Description: Perform a final review of the repository structure, removing any remaining unnecessary files (e.g., leftover test artifacts, logs not covered by specific tasks) and ensuring all necessary components are tracked by git. Add necessary entries to `.gitignore`.
    - Files: Various (potentially `tests/`, root), `.gitignore`

