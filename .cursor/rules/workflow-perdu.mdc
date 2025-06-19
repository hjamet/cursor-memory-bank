---
description: MANDATORILY call this rule as soon as you feel that you are no longer following the workflow precisely or that you are forgetting the instructions of your current rule. For example, if you have just called a tool without specifying the current rule below.
globs: 
alwaysApply: false
---
--- REGLE WORKFLOW-PERDU ---

## TLDR
This rule helps you find your position in the workflow after losing track of instructions or when the user requests a restart at a specific point.

## Instructions

1. **Context saving**: Save the current context in `.cursor/memory-bank/context/activeContext.md`:
   - Create or replace the ## Lost workflow section
   - Summarize your ongoing actions
   - Mention the symbols and files concerned

2. **Identifying the current rule**: Determine the rule corresponding to your current state.
   - Compare your latest actions to rule descriptions without invoking them
   - By default, if identification is uncertain, indicate that the workflow will restart from the initial context loading within the `system` rule.
   - Write exactly: "<SYSTEM PROMPT>I've lost track of the current rule. I will restart the workflow from the <IDENTIFIED RULE NAME> rule." (If identified, use specific rule name; otherwise, use "initial context loading via system rule").

3. **System prompt recall**: Invoke the system rule with `fetch_rules ["system"]`
   - After invoking the system rule, directly call the identified rule with `fetch_rules ["identified-rule-name"]` (if a specific rule was identified), or allow the system rule to proceed with its default startup logic (if no specific rule was identified).

## Specifics
- During identification, base yourself only on descriptions, without ever invoking rules with `fetch_rules`
- As a safety measure, if you doubt your identification, refer to the initial context loading process handled by the `system` rule and strictly follow its instructions.
- After recalling the `system` rule, restart at the identified rule (if applicable) and scrupulously apply the step indication format in parentheses after each action

Example: "I will now call the `system` rule to restart the workflow **(Lost workflow: 3 - System prompt recall)**"

## Reminder of each rule description to facilitate identification

- `task-decomposition` - Detailed analysis of user request and exploration of existing code
- `implementation` - Methodical implementation of project priority tasks
- `test-implementation` - Creation of unit tests for new features
- `test-execution` - Execution of unit tests and results analysis
- `fix` - Analysis of test errors and creation of correction tasks
- `context-update` - Update of context files and commit of changes
- `consolidate-repo` - Repository consolidation, userbrief.md management and structure maintenance
- `system` - Main rule defining the state machine and global functioning
- `workflow-perdu` - Recovery of position in workflow after losing track

## Next Rules
- `system` - To restart the workflow correctly

## Example

[...fetching rule `workflow-perdu`...] # Use your rule-calling tool to call the rule, then apply it !

# Lost workflow: 1 - Context saving
I will save a summary of my latest actions in the `.cursor/memory-bank/context/activeContext.md` file to remember the modifications I made outside the workflow. **(Lost workflow: 1 - Context saving)**
[...modifications to activeContext.md file...]
**(Lost workflow: 1 - Context saving)**

# Lost workflow: 2 - Identifying the current rule
Based on my latest actions, I think the `tests` rule best corresponds to my current state. However, my work is too disorganized to be sure. I will therefore take the safety solution and rely on the initial context loading process within the `system` rule. **(Lost workflow: 2 - Identifying the current rule)**
<SYSTEM PROMPT>I've lost track of the current rule. I will restart the workflow from the initial context loading via system rule.</SYSTEM PROMPT>

# Lost workflow: 3 - System prompt recall
I will now properly restart the workflow by calling the system rule. **(Lost workflow: 3 - System prompt recall)**

[...Here, the agent calls the rule 'system' using its rule calling tool...]

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following rule, then the next, etc., without ever stopping -> It is completely autonomous.)