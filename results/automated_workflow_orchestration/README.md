# Automated Workflow Orchestration

The MemoryBank MCP server has been updated to automate user request processing and workflow routing.

## Changes
- The `next_rule` tool can now be called without arguments. It will automatically determine the next rule to execute based on the state of `userbrief.md` and `tasks.md`.
- The `read_userbrief` tool now automatically marks new user requests as 'in_progress'.
- The `.md` rules have been simplified to use this new automated logic.

## How to use
Simply call the `mcp_MemoryBank_next_rule` tool without any arguments to let the server decide the next step in the workflow. 