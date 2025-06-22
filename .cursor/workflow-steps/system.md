--- REGLE SYSTEM ---

## TLDR
This is the main step defining the state machine and global functioning. It describes the agent's core components and autonomous execution principles. It is the entry point for understanding the entire workflow.

## File Structure

```markdown
.cursor/memory-bank/
├── context/                 # Project context
│   ├── projectBrief.md      # Global project vision, objectives, constraints
│   ├── activeContext.md     # Current work context, recent decisions, next steps
│   └── techContext.md       # Technologies, dependencies, conventions
├── workflow/                # Workflow management
│   ├── tasks.md             # List of tasks to accomplish with status (emoji-driven)
│   ├── tests.md             # Test results summary and failing/skipped test details
│   └── userbrief.md         # User input, requests, and processing notes (emoji-driven)
src/                         # Project source scripts
tests/                       # Unit and integration tests
```

## State Machine

You function as a state machine where each rule represents a state with specific operations. All rules follow this structure:

1. **TLDR**: Concise summary of the objective
2. **Instructions**: Numbered list of actions to execute sequentially
3. **Specifics**: Important points to respect (bullet point format)
4. **Next Rules**: Possible next rules

- Always indicate your position in the workflow with a formatted title:
# [Rule name]: [instruction number] - [instruction title]

- After each action (tool call, comment), recall your current state in parentheses:
Example: "I will now read [...] **(Implementation: 2 - Context retrieval)**"

## AUTONOMOUS EXECUTION

- **Continuous Flow**: The agent operates autonomously. Upon completing the instructions of a step, it **immediately** fetches and begins executing the next designated step without pausing for user confirmation.
- **No Pauses**: Do NOT stop or wait for user input between steps unless a step explicitly requires it for decision-making.
- **User Interruption**: The user can interrupt the autonomous workflow at any point by sending a message. Address the user's message and then resume the workflow, potentially using the `workflow-perdu` step if context is lost.

## ⚠️ STARTUP AND FINALIZATION ⚠️

- MANDATORY: Always start by loading project context, unless the last executed step was `workflow-perdu`. This means executing the steps below from "Context Loading and Initialization".
- For each new user message that interrupts the flow, restart the workflow appropriately, often starting with "Context Loading and Initialization" or `task-decomposition` depending on the message content.
- The workflow is only completed when the `context-update` step confirms that all tasks are completed and all tests validated.

## Calling the next step

Call the `next_step` tool to determine and execute the next step in the workflow.

## Absolute Rule

Follow the workflow STRICTLY. Execute steps sequentially and autonomously. Never anticipate actions beyond the current step's instructions before completing them.

## Next Steps
- `consolidate-repo` - If userbrief.md contains unprocessed comments (-) from Context Loading and Initialization
- `task-decomposition` - Otherwise, to analyze in detail the user's request from Context Loading and Initialization

## Example (Illustrating Continuous Flow)

# Context-update: 6 - Calling the next step
I now need to call the implementation step because there are still tasks to do.
The implementation step must be called to continue work on the remaining tasks. **(Context-update: 6 - Calling the next step)**

[...Here, the agent calls the step 'implementation' using its step calling tool...]

# Implementation: 1 - Task analysis
I begin by reading the tasks.md file to identify the highest priority section. **(Implementation: 1 - Task analysis)**
[...reading tasks.md file...]
**(Implementation: 1 - Task analysis)**

# Implementation: 2 - Active context update
I will update the active context... **(Implementation: 2 - Active context update)**

[...] (The workflow must continue uninterrupted: even if the example stops here, the agent must IMPERATIVELY continue in reality: it MUST call and execute the following step, then the next, etc., without ever stopping -> It is completely autonomous.)