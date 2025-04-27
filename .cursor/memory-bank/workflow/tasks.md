# Done

## 2. Refactor Execution Rule & Update Implementation Rule
- [x] **Rename Rule File**: Renamed `execution.mdc` to `experience-execution.mdc`.
- [x] **Update Rule Content**: Updated `experience-execution.mdc` (no background, std examples, internal refs).
- [x] **Update Rule Frontmatter**: Attempted to update `experience-execution.mdc` frontmatter (skipped).
- [x] **Modify Implementation Rule**: Updated `implementation.mdc` to call `experience-execution`.

## 1. Workflow Enhancement
1.1. [x] **Modify `fix` Rule Debugging Strategy**: Updated rule to use logs/temp scripts instead of MCP Debug.
1.2. [x] **Strengthen MCP Memory Usage in `fix` Rule**: Emphasized memory lookup/storage.
1.3. [x] **Strengthen MCP Memory Usage in `implementation` Rule**: Emphasized memory lookup/storage.
1.4. [x] **Strengthen MCP Memory Usage in `request-analysis` Rule**: Emphasized memory lookup/storage.

## 1. Enhance Architect Rule Memory Usage
1.1. [x] **Define Memory Strategy**: Define and document within `architect.mdc` how the architect agent should store user vision, preferences, and directives using MCP Memory.
    - Actions: Add a new section or subsection detailing entity types (e.g., `ProjectVision`, `UserPreference`, `ArchitectDirective`), relations (e.g., `CONTAINS`, `SPECIFIES`), and observation content structure. Recommend using a main `ProjectVision` entity as an entry point.
    - Files: `.cursor/rules/architect.mdc`
    - Dependencies: None
    - Validation: Verify the rule clearly instructs the architect agent on *how* and *what* to store in MCP Memory, including organization principles.

1.2. [x] **Integrate Memory Storage**: Update existing sections (like Communication avec l'Utilisateur) in `architect.mdc` to explicitly instruct the agent to use `mcp_Memory_add_observations` (or similar) when receiving relevant vision/preference information from the user.
    - Actions: Modify relevant instruction steps to include mandatory calls to MCP Memory tools for storing user input.
    - Files: `.cursor/rules/architect.mdc`
    - Dependencies: Task 1.1
    - Validation: Check that the rule mandates memory storage for user vision/preferences.

## 2. Implement Architect Verification Workflow
2.1. [x] **Define Verification Workflow**: Define and add a new major section to `architect.mdc` outlining the step-by-step iterative verification process.
    - Actions: Create a new H2 section (e.g., `## Verification Workflow`). Detail the loop: 1. Query MCP Memory for a specific vision/preference element. 2. Analyze project state (code files, `tasks.md`, context files) to check conformity. 3. Document findings (conformant, deviant, planned in tasks). 4. Repeat for next memory element. Specify tools to use (MCP search, file reading, semantic search).
    - Files: `.cursor/rules/architect.mdc`
    - Dependencies: Task 1.1 (relies on stored memory)
    - Validation: Verify the rule contains a clear, detailed, iterative verification workflow.

2.2. [x] **Update Architect Example**: Modify the example usage section in `architect.mdc` to illustrate both the enhanced memory storage and the new verification workflow.
    - Actions: Add example snippets showing how the architect agent should store information and perform a verification step.
    - Files: `.cursor/rules/architect.mdc`
    - Dependencies: Task 1.2, Task 2.1
    - Validation: Verify the example accurately reflects the new memory and verification instructions.

# In Progress

(No tasks currently in progress)

# ToDo

(No tasks remaining in ToDo for now)

