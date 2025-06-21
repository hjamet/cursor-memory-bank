# Active Context

## Current Focus
All tasks related to fixing the MCP workflow are complete. The root cause of the workflow failure was identified as an issue within the external `@modelcontextprotocol/sdk`, which swallows errors from tool handlers instead of propagating them as JSON-RPC errors. While our local code has been cleaned and made more robust, the core issue remains in the dependency.

## Current Implementation Context
-   **Task**: 41.1 - Log analysis and reproduction.
-   **Objective**: Find a reliable way to reproduce the "Unexpected token 'R'" error and the tool interruptions observed during the initial test.
-   **Hypothesis**: The issue is likely related to how the Node.js MCP server process communicates with the client over stdio. A non-JSON string (perhaps a debug `console.log`) might be corrupting the JSON-RPC stream. The error "Unexpected token 'R'" could come from the word "Rule" or "ReadUserbr" seen in the logs if it's not wrapped in a proper JSON object.
-   **Plan**:
    1.  Thoroughly examine the code for `next_rule.js` and `remember.js` for any `console.log` statements that could be printing raw strings to stdout.
    2.  Examine the test script `test_remember_next_rule.js`. It seems to spawn the server as a child process and communicate via stdin/stdout, which is a perfect environment to replicate the issue.
    3.  Run `test_remember_next_rule.js` to see if it fails and analyze its output.

## Recent Decisions
- Decided to stop trying to fix the error propagation issue in our local code as it's an external SDK problem.
- Documented the SDK issue in `techContext.md` and in a dedicated results file.
- Cleaned up potential error sources in our code (e.g., `console.warn` in `remember.js`).
- Made the server-side code more robust by wrapping all tool handlers in a `safeHandler`.

## Recent Implementation
**Task 41 Completion**: Diagnosed and documented the MCP workflow failure.
- **41.1 & 41.2**: Analyzed logs, reproduced a related error with an improved test script, and cleaned up local code.
- **41.3 & 41.4**: Concluded the investigation, identifying the external SDK as the root cause, and documented the findings thoroughly.

## Current Repository State
- **Branch**: Currently on `memory-bank-mcp`
- **MCP Servers**: Both MemoryBank and MyMCP fully operational and enhanced
- **Task Management**: Robust validation and filtering system implemented
- **Tool Schemas**: All enhanced with proper validation and comprehensive options

## Next Steps
- Commit the investigation results and code improvements.
- Decide on the next steps for the project, considering the identified limitation of the MCP SDK.

## Important Notes
- All MCP task management tools now have comprehensive validation
- Enhanced filtering capabilities improve task discovery and management
- Status transition validation ensures data integrity
- Dependency resolution logic improved for better task ordering

## Repository Technical State
- **Branch**: Currently on `memory-bank-mcp`
- **Userbrief System**: Fully migrated to `userbrief.json`
- **MCP Servers**: Both MemoryBank and MyMCP fully operational and tested
- **Tool Schemas**: All tool argument descriptions properly exported and functioning

# Active Implementation Context

## Current Task: #42 - Refactor Workflow: Rules to Steps & New Logic

I am starting the implementation of a major workflow refactoring. The goal is to move from an implicit, "rule-based" system to an explicit, "step-based" system.

### Key Objectives:
1.  **Terminology Change**: Globally replace "rule" with "step".
2.  **Tool Renaming**: Rename `next_rule` to `next_step`.
3.  **Logic Overhaul**:
    - The `next_step` tool will no longer decide the next step. It will require a `step_name` argument.
    - The `remember` tool will be enhanced to analyze the agent's state and return a list of `possible_next_steps`.
    - The agent's core logic will be: `remember` -> choose a step -> `next_step(chosen_step)`.
4.  **Process Cleanup**: Stop creating `results/` directories for documenting work.
5.  **Testing**: Update all tests to match the new workflow.

I will proceed by implementing the sub-tasks of #42 in order, starting with 42.1.

## Current Status
The agent has been working on refactoring the MCP workflow system (task #42) to replace "rules" with "steps" and improve tool stability. Several sub-tasks have been completed or are in progress, with some blocked due to tooling issues.

## Lost workflow
The user has just restarted the MCP server and requested testing and fixing any remaining issues. I was in the middle of implementing task #42 (comprehensive workflow refactoring) which involved:

- Renaming `next_rule` to `next_step` tool ✅ COMPLETED
- Updating `remember` tool to suggest next steps ✅ COMPLETED  
- Updating workflow files to use "step" terminology (PARTIALLY DONE)
- Removing results directory creation logic (PENDING)
- Updating test scripts (IN PROGRESS - renamed file, need to test)
- Enforcing mcp_MyMCP_* tools usage (PENDING)

Files recently modified:
- `.cursor/mcp/memory-bank-mcp/mcp_tools/next_step.js` (renamed from next_rule.js)
- `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js` (updated logic)
- `.cursor/mcp/memory-bank-mcp/server.js` (updated tool registration)
- `test_remember_next_step.js` (renamed and updated)
- Various workflow markdown files (partially updated)

The user wants me to test the restarted server and fix any remaining issues with the new MCP workflow system.