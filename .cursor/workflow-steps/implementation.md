## TLDR

Methodically implement ONE SINGLE priority task with intelligent routing. **WARNING: Process only ONE SINGLE task per cycle.**

## Instructions

0.  **Implementation Counter Update**: AUTOMATICALLY increment the implementation step counter and check for README task triggers.

      * **AUTOMATIC CALL**: This step is handled automatically by the workflow system. The `implementation_count` counter is incremented with each call to this rule.
      * **README TASK GENERATION**: If the counter reaches a multiple of 10, a README update task will be automatically generated with priority 4.
      * **TRANSPARENCY**: This operation is transparent and does not interrupt the normal workflow.

## Available Context

**Automatic Next Task Integration**: The next priority task to work on is automatically provided in the workflow context as `current_task`. This eliminates the need for manual calls to `get_next_tasks`.

**Context Structure Available:**
- `current_task`: The highest priority available task with full details (id, title, description, status, priority, dependencies, etc.)
- `current_tasks_summary`: Summary of current task counts by status (TODO, IN_PROGRESS, BLOCKED, REVIEW, DONE)
- `system_analysis`: Analysis with recommended workflow step and system state evaluation
- `recent_memories`: Context from previous workflow steps to maintain continuity

**How to Use the Automatic Context:**
- **Task Selection**: Use `context.current_task` for the single task to process
- **Status Management**: The task may already be IN_PROGRESS if resumed from previous workflow cycle
- **Priority Validation**: The task selection algorithm automatically handles priority, dependencies, and availability
- **Workflow Continuity**: If `current_task` is null, no tasks are available and agent should route appropriately

1.  **Task analysis and status update**: Analyze THE task to implement (ONLY ONE) and immediately mark it as IN\_PROGRESS.

      * **Use Automatic Context**: The priority task is automatically provided in `context.current_task` - no manual tool calls needed.
      * **IMPORTANT**: It is THIS task and ONLY this task that you must process.
      * **MANDATORY TAGGING**: IMMEDIATELY mark the task as IN\_PROGRESS with `mcp_MemoryBankMCP_update_task`. This is a non-negotiable rule to maintain workflow integrity.
      * **EXCEPTION**: If a task is already marked as IN\_PROGRESS, skip this step and continue working with that task.
      * **No Available Tasks**: If `context.current_task` is null, no tasks are available and you should handle appropriately (e.g., route to context-update).

2.  **Evaluation and Intelligent Routing**: Evaluate the nature of the task to decide on the course of action.

      * **TASK ANALYSIS**: As a senior engineer, deeply analyze the title, description, and objectives of the task.
      * **ROUTING DECISION**:
          * **CASE 1: Pure Execution**: If you determine that the task requires **no code modification** and only consists of executing commands, running tests, performing validations, or generating reports, then the implementation phase is not necessary.
              * **ACTION**: Immediately call `mcp_MemoryBankMCP_next_rule` with `step_name: "experience-execution"`.
              * **RULE FINISHED**: The `implementation` rule stops here for this type of task.
          * **CASE 2: Development Required**: If the task involves any code modification (file creation, correction, refactoring, feature addition), continue with the development steps below (3-5).
      * **Guiding principle**: Trust your expert judgment to distinguish a "development" task from an "execution" task. Document your decision in your thoughts.

3.  **Context Analysis and Implementation Plan**: Analyze the existing code to understand its principles, practices, and conventions.

      * **Context research**: Perform up to 3 semantic searches (`codebase_search`).
      * **Research objectives**:
          * Identify reusable components, functions, or patterns.
          * Understand the current code conventions and adhere to them as much as possible.
          * Identify how the kind of task you have to implement has been handled in the past: reproduce the same approaches.
          * **Guiding principle**: You must not reinvent the wheel\! Go for the simplest solution. Modify the existing code as little as possible: it is certainly correct. Reuse existing code as much as possible.
      * **Synthesis**: You must finish this step by summarizing the identified principles, reusable components, and code conventions. Taking all these elements into account, you must establish an implementation plan.

4.  **Implementation** (former step 3): Implement the necessary modifications for THE single task, following the identified principles.

      * Use the appropriate tools (`edit_file`, `replace_content_between`, `grep_search`, etc.).
      * **ABSOLUTE FOCUS**: Concentrate solely on this task. Do not get distracted by other unplanned issues.

5.  **Record progress and determine next steps**: Record an honest self-assessment and transition automatically.

      * **MANDATORY**: Use `mcp_MemoryBankMCP_remember`.
      * **Critical Communication**: Use the `user_message` parameter of `remember` only to report a **critical** issue that requires the user's attention.
      * **AUTOMATIC TRANSITION**: The workflow automatically transitions to `experience-execution` for validation after remember.

## Specifics - STRICT RULES

  - **RULE \#1**: Work on ONE SINGLE task at a time - NEVER multiple tasks in sequence
  - **RULE \#2**: THE task to be processed is the one provided in `context.current_task` - no others
  - **RULE \#3**: IMMEDIATELY MARK the task as IN\_PROGRESS in step 1 - NO EXCEPTIONS
  - **RULE \#4**: APPLY INTELLIGENT ROUTING in step 2 - analyze the task type and route if necessary
  - **RULE \#5**: MANDATORILY end with `mcp_MemoryBankMCP_remember` to maintain the workflow
  - **RULE \#6**: Do not arbitrarily decide to process other tasks "while you're at it"
  - **RULE \#7**: If a task seems related to others, process ONLY the priority task returned by the tool
  - **RULE \#8**: Sub-tasks are allowed ONLY if they are an integral part of the main task
  - **RULE \#9**: NEVER mark a task as REVIEW - this is the responsibility of experience-execution
  - Use MCP tools for all task management
  - Respect established code conventions
  - Test modifications locally if possible
  - Document important decisions in memories

## Next Steps - WORKFLOW AUTOMATION ACTIVE

⚠️ **AUTOMATIC TRANSITION ACTIVATED** ⚠️

**CRITICAL RULE**: After each completed implementation, the workflow **AUTOMATICALLY** transitions to `experience-execution` for validation. This transition is **MANDATORY** and is part of the system's quality architecture.

**Automatic transitions**:

  - `implementation` → `experience-execution` (AUTOMATIC - after a code implementation)
  - `implementation` → `experience-execution` (DIRECT - for pure execution tasks routed in step 2)
  - `experience-execution` → Determined by test results

**Rare exceptions** (handled automatically by the system):

  - Presence of critical BLOCKED tasks
  - Urgent user requests without recently completed tasks

**Possible manual steps**:

  - `context-update` - To finalize and commit changes
  - `fix` - If problems are detected during implementation
  - `task-decomposition` - If new user requests arrive

## Example - SINGLE TASK WORKFLOW (Careful and efficient Mindset)

# Implementation: 1 - Task analysis and status update

I start by analyzing THE task to implement (ONLY ONE) and immediately mark it as IN\_PROGRESS.
**Use Automatic Context**: The priority task is automatically provided in `context.current_task`.
I have identified THE priority task: {{ current\_tasks\_summary }}; Since I have no other task in progress, I will mark it as IN\_PROGRESS.
**MANDATORY TAGGING**: I immediately mark this task as IN\_PROGRESS.
[...MANDATORY call to mcp\_MemoryBankMCP\_update\_task to mark the task IN\_PROGRESS...]
**FOCUS**: I will process ONLY this task.

# Implementation: 2 - Evaluation and Intelligent Routing

I evaluate the nature of the task to decide on the course of action.
\<think\>The task "{{ context.current\_task.title }}" asks to "{{ context.current\_task.short\_description }}". After analysis, I will determine if a code modification is necessary.

  - **CASE 1 - Pure Execution**: The task asks to run tests and generate a report. No line of code will be changed. I will therefore route to experience-execution.
  - **CASE 2 - Development Required**: The task asks to fix a bug in function X. This requires modifying the code. I will therefore continue with the implementation.
    My decision is: [CASE 1 or CASE 2]

\</think\>

  - **ROUTING DECISION - CASE 1**: This task only requires execution. I am routing it to `experience-execution`.
    [...call to mcp\_MemoryBankMCP\_next\_rule with step\_name: "experience-execution"...]
    **WORKFLOW FINISHED**
  - **ROUTING DECISION - CASE 2**: This task requires development. I am continuing with steps 3-5.

# Implementation: 3 - Context Analysis and Implementation Plan

I search the codebase to find reusable components and code conventions.
[...call to `codebase_search` (up to 3 times)...]
**Analysis and Plan**:
[...synthesis of identified principles, reusable components, and code conventions...]

# Implementation: 4 - Implementation

I now proceed with the implementation of the modifications for THE single task, following my plan.
[...implementation of changes...]

# Implementation: 5 - Record progress and determine next steps

I will now record an honest self-assessment.
[...MANDATORY call to mcp\_MemoryBankMCP\_remember, using `user_message` ONLY if a critical problem has been discovered...]
**WORKFLOW**: Remember will determine the next step (automatically experience-execution).