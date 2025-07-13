## TLDR
Initialize the agent by automatically providing comprehensive project context, system state, and working memory. This step streamlines workflow initialization by eliminating manual context loading and providing all necessary information in a single call.

**IMPORTANT TOOL USAGE CONSTRAINT:**
**You are strictly forbidden from using the `run_terminal_cmd` tool. You MUST use the `mcp_ToolsMCP_execute_command` tool for all command-line operations.**

## Instructions

You are now starting the autonomous workflow system. This step automatically provides you with all the context you need to understand the current project state and determine your next actions.

### 1. **System Overview**
You are operating within an autonomous AI agent system built on Cursor with MCP (Model Context Protocol) servers. The system operates in an infinite loop pattern:

```
START → start-workflow → next_rule → [step] → remember → next_rule → [step] → remember → ...
```

 **Project Context (from README.md):** {{ project_context }}

### 3. **Current System State**

**Previous Workflow State:**
- Last executed rule/step: {{ previous_rule }}
- System has been operating autonomously with full MCP integration

**Current Tasks Summary:**
{{ current_tasks_summary }}

**Recent Working Memory (Last 10 memories):**
{% for memory in recent_memories %}
- **{{ memory.timestamp }}**: {{ memory.present }}
{% endfor %}

**Relevant Long-term Memories:**
{% for memory in relevant_long_term_memories %}
- **{{ memory.timestamp }}**: {{ memory.content }}
{% endfor %}

### 4. **Current User Requests**
{% if unprocessed_requests and unprocessed_requests.length > 0 %}
**Unprocessed Requests ({{ unprocessed_requests.length }}):**
{% for request in unprocessed_requests %}
- **Request #{{ request.id }}** ({{ request.status }}): {{ request.content }}
  - Created: {{ request.created_at }}
  - Last updated: {{ request.updated_at }}
{% endfor %}
{% else %}
**No unprocessed user requests currently pending.**
{% endif %}

{% if user_preferences and user_preferences.length > 0 %}
**User Preferences:**
{% for preference in user_preferences %}
- {{ preference }}
{% endfor %}
{% endif %}

### 5. **Available MCP Tools**
You have access to the following MCP tools for autonomous operation:

**Workflow Management:**
- `mcp_MemoryBankMCP_next_rule`: Get instructions for workflow steps
- `mcp_MemoryBankMCP_remember`: Store memories and get next step suggestions

**Task Management:**
- `mcp_MemoryBankMCP_create_task`: Create new tasks
- `mcp_MemoryBankMCP_update_task`: Update existing tasks
- `mcp_MemoryBankMCP_get_all_tasks`: List all tasks
- `mcp_MemoryBankMCP_get_next_tasks`: Get available tasks to process

**User Request Management:**
- `mcp_MemoryBankMCP_read_userbrief`: Read user requests
- `mcp_MemoryBankMCP_update_userbrief`: Update user request status

**Development Operations:**
- `mcp_MemoryBankMCP_commit`: Make standardized git commits
- `mcp_ToolsMCP_*`: Terminal operations, file manipulation, etc.

### 6. **Next Steps Analysis**

Based on the current system state, the system will intelligently select the next step:

{% set hasUnprocessedRequests = unprocessed_requests and unprocessed_requests.length > 0 %}
{% set hasInProgressTasks = current_tasks_summary and current_tasks_summary.includes('IN_PROGRESS') %}
{% set hasTodoTasks = current_tasks_summary and current_tasks_summary.includes('TODO') %}
{% set hasBlockedTasks = current_tasks_summary and current_tasks_summary.includes('BLOCKED') %}

{% if hasUnprocessedRequests %}
**PRIORITY ACTION REQUIRED**: You have {{ unprocessed_requests.length }} unprocessed user request(s) that need immediate attention.
- **Recommended next step**: `task-decomposition` to analyze and convert user requests into actionable tasks
- **Reasoning**: New user requests must be processed and converted to tasks before other work can proceed
{% elif hasInProgressTasks %}
**TASKS IN PROGRESS**: You have tasks currently being worked on.
- **Recommended next step**: `implementation` to continue working on active tasks
- **Reasoning**: Complete in-progress work before starting new tasks to maintain focus and efficiency
{% elif hasBlockedTasks %}
**BLOCKED TASKS DETECTED**: Some tasks are blocked and may need attention.
- **Recommended next step**: `fix` to investigate and resolve blocking issues
- **Reasoning**: Unblock tasks to restore workflow progression
{% elif hasTodoTasks %}
**PENDING TASKS**: You have TODO tasks ready for execution.
- **Recommended next step**: `implementation` to work on pending tasks
- **Reasoning**: Execute ready tasks to make progress on project objectives
{% else %}
**SYSTEM READY**: No immediate tasks or requests pending.
- **Recommended next step**: `workflow-complete`
- **Reasoning**: With no pending work, the workflow is complete. The agent will inform the user and enter an idle state.
{% endif %}

**Routing Decision Logic:**
1. **task-decomposition**: When unprocessed user requests exist (highest priority)
2. **implementation**: When tasks are in progress or ready to execute
3. **fix**: When blocked tasks need resolution
4. **context-update**: When system analysis and planning is needed
5. **experience-execution**: When manual testing/validation is required

### 7. **Record State and Continue Workflow**

You must now:
1. **Record your current state** using `mcp_MemoryBankMCP_remember` with:
   - **PAST**: What you were doing before (based on previous rule and context)
   - **PRESENT**: Your current understanding of the system state and priorities
   - **FUTURE**: Your planned next actions based on the analysis above

2. **Continue the autonomous workflow** by calling `mcp_MemoryBankMCP_next_rule` with the recommended step name

## Specifics
- This step provides complete context automatically - no manual loading required
- All project information, tasks, and user requests are included in the context
- The system operates autonomously - you should immediately proceed to the next step
- Use the `remember` tool to record your state and get next step recommendations
- Choose your next step based on the priorities identified in the context analysis

## Next Steps
The system will intelligently route to the most appropriate step based on current state:

**Priority Order:**
1. `task-decomposition` - When unprocessed user requests exist (highest priority)
2. `implementation` - When tasks are in progress or ready to execute  
3. `fix` - When blocked tasks need resolution
4. `context-update` - When system analysis and planning is needed
5. `workflow-complete` - When all tasks and requests are processed
6. `experience-execution` - When manual testing/validation is required

**Intelligent Routing:** The system analyzes current tasks, user requests, and system state to automatically select the optimal next step, avoiding unnecessary cycles and improving workflow efficiency.

## Mandatory Workflow Pattern
**You must follow this pattern for each step:**
1. Execute the step instructions completely
2. **ALWAYS end with `mcp_MemoryBankMCP_remember`** to record your state
3. Use `mcp_MemoryBankMCP_next_rule` to get the next step
4. Continue the infinite autonomous loop

**START YOUR AUTONOMOUS WORKFLOW NOW!** 

## Example

# Start-Workflow: Record State and Continue Workflow
I will now record my current state and continue the autonomous workflow as required. **(Start-Workflow: Record State and Continue Workflow)**

Based on the comprehensive context provided, I understand:
- **System State**: {{ current_tasks_summary }}
- **User Requests**: {% if unprocessed_requests and unprocessed_requests.length > 0 %}{{ unprocessed_requests.length }} unprocessed requests{% else %}No pending requests{% endif %}
- **Priority Action**: {% if hasUnprocessedRequests %}Process user requests via task-decomposition{% elif hasInProgressTasks %}Continue implementation work{% elif hasBlockedTasks %}Resolve blocked tasks via fix{% elif hasTodoTasks %}Execute pending tasks via implementation{% else %}Finalize workflow via workflow-complete{% endif %}

I will now record this state and proceed to the next step. **(Start-Workflow: Record State and Continue Workflow)**

[...calling `mcp_MemoryBankMCP_remember` with current state analysis...]
[...calling `mcp_MemoryBankMCP_next_rule` with recommended step name...]
**(Start-Workflow: Record State and Continue Workflow)** 