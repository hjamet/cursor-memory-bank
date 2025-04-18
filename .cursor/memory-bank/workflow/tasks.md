# In Progress

## 1. Cleanup
[ x ] **1.1 Delete `workflow-propositions.md` file.**
    - Description: User has reviewed the proposals and requested deletion of the file.
    - Impacted Files: `.cursor/memory-bank/workflow/workflow-propositions.md`
    - Dependencies: None
    - Validation: Verify file deletion using `ls` or `find`.

# ToDo

## 2. Integrate `terminal-mcp` Server
2.1 [ ] **Modify `implementation` rule for `terminal-mcp`:**
    - Description: Update the `implementation.mdc` rule to use `mcp_terminal-mcp_start-process` for potentially long-running commands executed during task implementation (e.g., build steps, complex scripts). Store the returned `processId`. Add logic to check process status/output using `mcp_terminal-mcp_get-process-output` before proceeding or in a subsequent step.
    - Impacted Files: `.cursor/rules/implementation.mdc`
    - Dependencies: None
    - Validation: Review `implementation.mdc` to confirm usage of `terminal-mcp` tools and asynchronous handling.
2.2 [ ] **Modify `test-execution` rule for `terminal-mcp`:**
    - Description: Update the `test-execution.mdc` rule to use `mcp_terminal-mcp_start-process` for running the test suite. Store the returned `processId`. Add logic to check process status/output using `mcp_terminal-mcp_get-process-output` to get test results.
    - Impacted Files: `.cursor/rules/test-execution.mdc`
    - Dependencies: None
    - Validation: Review `test-execution.mdc` to confirm usage of `terminal-mcp` tools and asynchronous handling of test results.
2.3 [ ] **Update Command Execution Notes:**
    - Description: Modify the "Command Execution Note" section in the specifics of `implementation.mdc` and `test-execution.mdc` to mention the use of `terminal-mcp` for long-running commands and the need to check output asynchronously.
    - Impacted Files: `.cursor/rules/implementation.mdc`, `.cursor/rules/test-execution.mdc`
    - Dependencies: 2.1, 2.2
    - Validation: Review the specifics section in both rules to ensure the note about `terminal-mcp` is present and accurate.

## 12. Cleanup Temporary Files
12.1. [ ] **Clean the tmp directory**: Remove the temporary test directories.
- Actions:
  1. Add `tmp/` to `.gitignore`.
  2. Implement a mechanism (e.g., in tests or a separate script) to clean the `tmp/` directory regularly or after tests.
- Fichiers: `.gitignore`, `tests/*`
- Dépendances: Aucune
- Validation: The `tmp/` directory is cleaned appropriately. 

# Done

## 1. Cleanup
[ x ] **1.1 Delete `workflow-propositions.md` file.**

## 13. Workflow Improvement Proposals
[ x ] **13.1 Analyze current workflow and identify areas for thoughtful improvement.**
[ x ] **13.2 Document thoughtful workflow improvement proposals.** 