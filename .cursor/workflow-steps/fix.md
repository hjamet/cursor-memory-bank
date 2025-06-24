## TLDR
Analyzes and fixes identified issues through iterative debugging, using MCP tools for task management and terminal operations. This step is a focused debugging loop designed to resolve specific problems.

## Instructions

1. **Error Identification**: Analyze the current context to identify issues that need fixing.
   - Use `mcp_MemoryBankMCP_get_all_tasks` to identify tasks with BLOCKED or failed status
   - Review recent memories for error reports or issues
   - Identify the specific problems that need to be addressed

2. **Correction Loop**: For EACH identified issue, perform the following cycle:
   - **2.1. Code Analysis**: Analyze the source code related to the issue. Use `read_file` and `codebase_search` to understand the context of the error.
   - **2.2. Propose Correction**: Formulate a fix for the bug. This may involve logic changes, dependency updates, or configuration adjustments.
   - **2.3. Apply Correction**: Use `edit_file` to apply the fix to the relevant file(s).
   - **2.4. Test Execution**: Re-run relevant tests or validation. Use `mcp_ToolsMCP_execute_command` with appropriate test commands.
   - **2.5. Verification**: Analyze the result of the test run.
     - **If it passes**, move to the next issue in the list from Step 1.
     - **If it still fails**, re-enter the loop at 2.1 for the *same* issue, but try a different correction. Limit attempts per issue to 3.
     - **If after 3 attempts the issue still persists**, mark the associated task as BLOCKED using `mcp_MemoryBankMCP_update_task`, add a comment explaining why, and proceed to the next issue.

3. **Record progress and determine next steps**: Use remember tool to record fixes and get next steps.
   - Call `mcp_MemoryBankMCP_remember` to record the current state and fixes applied
   - The remember tool will indicate the appropriate next steps

## Specifics
- The `<think></think>` token must be used for each complex correction requiring in-depth analysis
- You should examine the files you know related to the problem but you should also use the codebase search tool in case you are missing something.
- Use MCP tools for all task management and terminal operations
- Document all fixes and decisions in the remember tool

## Using the Advanced MCP Terminal Tools

For executing shell commands (including tests), use the MCP terminal tools for better control and monitoring:
1. **Launch:** Call the `mcp_ToolsMCP_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds.
2. **Check Status:** Call the `mcp_ToolsMCP_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the status of running/completed commands.
3. **Get Output:** Call the `mcp_ToolsMCP_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve output.
4. **Stop & Cleanup:** Call the `mcp_ToolsMCP_stop_terminal_command` MCP tool with the target `pid` to terminate a running command.

## Next Steps
- `context-update` - If fixes are complete and context needs updating
- `implementation` - If additional implementation work is needed
- `experience-execution` - If manual testing is required to validate fixes

## Example

# Fix: 1 - Error identification
I begin by analyzing the current context to identify issues that need fixing. **(Fix: 1 - Error identification)**
[...calling mcp_MemoryBankMCP_get_all_tasks to identify BLOCKED tasks...]
[...reviewing recent memories for error reports...]

I've identified the following issues:
1. Task #X is BLOCKED due to compilation error
2. Recent memory indicates database connection issue
3. User reported authentication problem

I will now start the correction loop for these issues. **(Fix: 1 - Error identification)**

# Fix: 2 - Correction loop

## Fix - 2.1: Correcting Task #X compilation error

### Fix - 2.1.1: Code analysis
I'll analyze the relevant source files to find the source of the compilation error. **(Fix: 2.1.1 - Code analysis)**
[... `read_file` on relevant files ...]
[... `codebase_search` for error patterns ...]
**(Fix: 2.1.1 - Code analysis)**

### Fix - 2.1.2: Propose correction
<think>The error suggests a missing import statement. I will add the required import to resolve the compilation issue.</think>
**(Fix: 2.1.2 - Propose correction)**

### Fix - 2.1.3: Apply correction
I will now apply the fix to the source file. **(Fix: 2.1.3 - Apply correction)**
[... `edit_file` to add missing import ...]
**(Fix: 2.1.3 - Apply correction)**

### Fix - 2.1.4: Test execution
I'll test the fix by running the compilation. **(Fix: 2.1.4 - Test execution)**
[... `mcp_ToolsMCP_execute_command` with compilation command ...]
**(Fix: 2.1.4 - Test execution)**

### Fix - 2.1.5: Verification
The compilation succeeded. I'll update the task status and move on to the next issue. **(Fix: 2.1.5 - Verification)**
[... `mcp_MemoryBankMCP_update_task` to unblock the task ...]

# Fix: 3 - Record progress and determine next steps
I will now record the fixes applied and determine the next appropriate steps. **(Fix: 3 - Record progress and determine next steps)**
[...calling `mcp_MemoryBankMCP_remember` with details of fixes applied...]
**(Fix: 3 - Record progress and determine next steps)**


