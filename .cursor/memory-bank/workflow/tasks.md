# ToDo

## 2. Rule Modification: `experience-execution.mdc`
- [ ] **2.1 Enhance Critical Analysis**: Modify the `experience-execution.mdc` rule to emphasize deeper analysis of results.
    - *Description*: Strengthen the instructions related to analyzing the *content* of files produced by experiments, not just relying on logs (stdout/stderr). Emphasize a *critical* perspective, looking for anything unusual or unexpected. Follow the rename-edit-rename workaround.
    - *Impacted Files/Components*: `.cursor/rules/custom/experience-execution.mdc`
    - *Dependencies*: None
    - *Validation Criteria*: The rule text explicitly instructs the agent to perform detailed, critical analysis of experiment output files.
- [ ] **2.2 Add Anomaly Investigation Trigger**: Modify `experience-execution.mdc` to handle strange results.
    - *Description*: Add logic to the rule: if the critical analysis (Task 2.1) reveals strange or anomalous results that are not clear bugs, the rule should conclude by calling `request-analysis` instead of its usual next rule. The purpose of calling `request-analysis` should be explicitly stated: to create a new task in `tasks.md` aimed at investigating these anomalies. Follow the rename-edit-rename workaround.
    - *Impacted Files/Components*: `.cursor/rules/custom/experience-execution.mdc`
    - *Dependencies*: 2.1
    - *Validation Criteria*: The rule contains logic to check for anomalies and, if found, calls `request-analysis` with the goal of creating an investigation task.

# Done

## 1. Rule Modification: `architect.mdc`
- [x] **1.1 Simplify and Enforce Context Reading**: Modify the `architect.mdc` rule.
    - *Description*: Simplify the rule's instructions. Add a new mandatory first step that requires the agent to read all context files (`.cursor/memory-bank/context/projectBrief.md`, `.cursor/memory-bank/context/activeContext.md`, `.cursor/memory-bank/context/techContext.md`) using the file reader tool at the beginning of every user request interaction. Follow the rename-edit-rename workaround.
    - *Impacted Files/Components*: `.cursor/rules/custom/architect.mdc` (Actual path: `.cursor/rules/architect.mdc`)
    - *Dependencies*: None
    - *Validation Criteria*: The updated `architect.mdc` rule contains a simplified structure and explicitly mandates reading the three context files as its first action.