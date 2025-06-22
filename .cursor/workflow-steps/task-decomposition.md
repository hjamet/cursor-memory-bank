## TLDR
Analyzes user requests, explores existing code, searches for additional information, retrieves high-level context, stores relevant vision elements, and decomposes requests into concrete tasks using the MCP task management tools.

## Instructions

1. **Request analysis**: Understand the user's request:
   - Analyze the user request provided by the MCP server.
   - Identify requested features or modifications.
   - Extract important keywords and concepts.

2. **Code analysis**: Identify concerned files and symbols:
   - Use `codebase_search` (up to 3 times) based on request keywords.
   - Optionally, use `tree` to visualize directory structure.
   - Strictly forbidden: listing folders/files, reading specific files, or using any other tool.

3. **Additional research**: Consult documentation and resources:
   - Use `mcp_Context7_*` tools for library documentation.
   - Use `mcp_brave-search_brave_web_search` for general research (max 5 searches).

4. **New tasks integration**: Create new tasks using MCP tools.
   - Decompose the user request into concrete tasks and sub-tasks.
   - Use `mcp_MemoryBankMCP_create_task` to create new tasks with appropriate details.

5. **Userbrief archiving**: Update the processed request via the MCP tool.
   - Call `mcp_MemoryBankMCP_update_userbrief` with `action: 'mark_archived'` and the `id` of the request being processed.

6. **Record state and determine next steps**: Use remember tool to record progress and get next steps.
   - Call `mcp_MemoryBankMCP_remember` to record the current state and analysis
   - The remember tool will indicate the appropriate next steps

## Specifics
- If you were called from consolidate-repo, consider the formulated request as the user request to analyze
- If the brief is empty without explicit request, consider current tasks as context for analysis
- Strict tool limits:
  - Phase 2 (Code analysis): only code base search (max 3) and tree
  - Phase 3 (Research): only mcp_Context7_* tools OR `mcp_brave-search_brave_web_search` (max 5 searches)
- Never mention planned modifications to context files (.cursor/memory-bank/* or .cursor/memory/*) unless creating a new vision note.
- Group similar tasks under common main task structures, even if apparently different.
- Favor detailed descriptions for each task item.
- Minimize dependencies between major tasks where possible.
- Use MCP tools for all task and userbrief management operations.

## Task Creation Guidelines

When creating tasks with `mcp_MemoryBankMCP_create_task`, use the following structure:
- **title**: Concise, actionable title
- **short_description**: Brief overview (1-500 characters)
- **detailed_description**: Comprehensive description with requirements, acceptance criteria, and technical details
- **priority**: 1-5 (5 being highest priority)
- **status**: Usually "TODO" for new tasks
- **dependencies**: Array of task IDs that must be completed first
- **impacted_files**: List of files that will be modified
- **validation_criteria**: Specific criteria for task completion

## Next Steps
- `implementation` - To begin implementing tasks
- `context-update` - If context needs updating
- `fix` - If issues are detected during analysis

## Example

# Task-decomposition: 1 - Request analysis
I begin by analyzing the user's request to properly understand their demand. **(Task-decomposition: 1 - Request analysis)**
[...request analysis...]
I identified the following key elements in the request: [...] **(Task-decomposition: 1 - Request analysis)**

# Task-decomposition: 2 - Code analysis
I begin by performing semantic searches to identify relevant files.
Let's perform a first semantic search: **(Task-decomposition: 2 - Code analysis)**
[...first semantic search...]
Let's perform a second semantic search: **(Task-decomposition: 2 - Code analysis)**
[...second semantic search...]
Let's visualize the directory structure to better understand the organization: **(Task-decomposition: 2 - Code analysis)**
[...tree command...]
I now better understand the code and relevant files. **(Task-decomposition: 2 - Code analysis)**

# Task-decomposition: 3 - Additional research
I need to understand how to use the 'some-obscure-library'. I will use the MCP Context7 tools for this. **(Task-decomposition: 3 - Additional research)**
[...calling `mcp_Context7_resolve-library-id` with libraryName="some-obscure-library"...]
[...calling `mcp_Context7_get-library-docs` with the resolved ID...]
Alternatively, I might search the web for general patterns related to [...]. **(Task-decomposition: 3 - Additional research)**
`mcp_brave-search_brave_web_search(...)`
**(Task-decomposition: 3 - Additional research)**

# Task-decomposition: 4 - New tasks integration
I decompose the main request into concrete tasks using the MCP task management tools. **(Task-decomposition: 4 - New tasks integration)**
[...calling `mcp_MemoryBankMCP_create_task` with appropriate parameters...]
**(Task-decomposition: 4 - New tasks integration)**

# Task-decomposition: 5 - Userbrief archiving
Now that the tasks have been created, I will update the userbrief to mark the request as processed. **(Task-decomposition: 5 - Userbrief archiving)**
[...calling `mcp_MemoryBankMCP_update_userbrief` with action: 'mark_archived'...]
**(Task-decomposition: 5 - Userbrief archiving)**

# Task-decomposition: 6 - Record state and determine next steps
I will now record the current state and let the remember tool indicate the next appropriate steps. **(Task-decomposition: 6 - Record state and determine next steps)**
[...calling `mcp_MemoryBankMCP_remember` with past, present, and future state...]
**(Task-decomposition: 6 - Record state and determine next steps)**