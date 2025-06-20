import { z } from 'zod';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { handleReadMemory } from './mcp_tools/read_memory.js';
import { handleEditMemory } from './mcp_tools/edit_memory.js';
import { handleRemember } from './mcp_tools/remember.js';
import { handleNextRule } from './mcp_tools/next_rule.js';
import { handleCommit } from './mcp_tools/commit.js';
import { handleCreateTask } from './mcp_tools/create_task.js';
import { handleUpdateTask } from './mcp_tools/update_task.js';
import { handleGetAllTasks } from './mcp_tools/get_all_tasks.js';
import { handleGetNextTasks } from './mcp_tools/get_next_tasks.js';
import { handleReadUserbrief } from './mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief } from './mcp_tools/update_userbrief.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import process from 'process';

// Create a new MCP server instance
const server = new McpServer({
    name: 'MemoryBank',
    version: '1.2.0'
});

// Register the tools with the server
server.tool('read_memory', {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext'])
        .describe('Name of context file to read (activeContext, projectBrief, techContext)')
}, handleReadMemory);

server.tool('edit_memory', {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext'])
        .describe('Name of context file to edit (activeContext, projectBrief, techContext)'),
    content: z.string().describe('New content to completely replace existing content')
}, handleEditMemory);

server.tool('remember', {
    past: z.string().describe("A description of what the agent originally planned to do."),
    present: z.string().describe("A description of what the agent actually did, any problems encountered, and decisions made."),
    future: z.string().describe("A description of what the agent plans to do next."),
    long_term_memory: z.string().optional().describe("Critical project information to be stored persistently (e.g., database schemas, architectural decisions). If provided, this will overwrite any existing long-term memory."),
}, handleRemember);

server.tool('next_rule', {
    rule_name: z.string().optional().describe("The name of the rule to execute next (without the .md extension). If not provided, the server will decide the next rule."),
}, handleNextRule);

server.tool('commit', {
    emoji: z.string().describe("Emoji to use in the commit message (e.g. :sparkles:)"),
    type: z.string().describe("Type of change (e.g. feat, fix, docs, style, refactor, test, chore)"),
    title: z.string().describe("Brief commit title"),
    description: z.string().describe("Detailed description of changes")
}, handleCommit);

server.tool('create_task', {
    title: z.string().min(1).max(200).describe('Short descriptive title of the task'),
    short_description: z.string().min(1).max(500).describe('Brief one-sentence description of what needs to be done'),
    detailed_description: z.string().min(1).describe('Comprehensive description with implementation details'),
    dependencies: z.array(z.number().int().positive()).optional().default([]).describe('Array of task IDs that must be completed before this task'),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe('Initial status of the task'),
    impacted_files: z.array(z.string()).optional().default([]).describe('List of files or rules affected by this task'),
    validation_criteria: z.string().optional().default('').describe('Clear criteria to determine when the task is successfully completed'),
    parent_id: z.number().int().positive().optional().describe('ID of parent task for sub-tasks'),
    priority: z.number().int().min(1).max(5).optional().default(3).describe('Priority level (1=highest, 5=lowest)')
}, handleCreateTask);

server.tool('update_task', {
    task_id: z.number().int().positive().describe('ID of the task to update'),
    title: z.string().min(1).max(200).optional().describe('Updated task title'),
    short_description: z.string().min(1).max(500).optional().describe('Updated brief description'),
    detailed_description: z.string().min(1).optional().describe('Updated detailed description'),
    dependencies: z.array(z.number().int().positive()).optional().describe('Updated array of dependency task IDs'),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Updated task status'),
    impacted_files: z.array(z.string()).optional().describe('Updated list of affected files'),
    validation_criteria: z.string().optional().describe('Updated validation criteria'),
    parent_id: z.number().int().positive().nullable().optional().describe('Updated parent task ID (null to remove parent)'),
    priority: z.number().int().min(1).max(5).optional().describe('Updated priority level (1=highest, 5=lowest)')
}, handleUpdateTask);

server.tool('get_all_tasks', {
    count: z.number().int().min(1).max(100).optional().default(10).describe('Number of tasks to return (default: 10)'),
    status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Filter by specific status'),
    priority_filter: z.number().int().min(1).max(5).optional().describe('Filter by specific priority level'),
    include_subtasks: z.boolean().optional().default(true).describe('Include sub-tasks in results'),
    include_dependencies: z.boolean().optional().default(true).describe('Include dependency information in response')
}, handleGetAllTasks);

server.tool('get_next_tasks', {
    limit: z.number().int().min(1).max(50).optional().default(10).describe('Maximum number of tasks to return'),
    include_completed: z.boolean().optional().default(false).describe('Include completed tasks in results'),
    include_blocked: z.boolean().optional().default(false).describe('Include blocked tasks in results'),
    status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Filter by specific status'),
    priority_filter: z.number().int().min(1).max(5).optional().describe('Filter by specific priority level')
}, handleGetNextTasks);

server.tool('read_userbrief', {
    archived_count: z.number().min(0).max(10).default(3).optional()
        .describe('Number of archived entries to include in response (default: 3)')
}, handleReadUserbrief);

server.tool('update_userbrief', {
    action: z.enum(['mark_archived', 'add_comment', 'mark_pinned'])
        .describe("Action to perform on the userbrief entry. Can be either 'mark_archived', 'add_comment', or 'mark_pinned'."),
    id: z.number().optional()
        .describe('ID of the request to update. If not provided, targets the current active request.'),
    comment: z.string().optional()
        .describe('Comment to add to the request history.'),
}, handleUpdateUserbrief);


// Start the server
async function startServer() {
    try {
        // Initialize server transport
        const transport = new StdioServerTransport();

        // Connect server to transport
        await server.connect(transport);

    } catch (error) {
        console.error('[MemoryBankMCP] Failed to start server:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    process.exit(0);
});

process.on('SIGTERM', () => {
    process.exit(0);
});

// Start the server
startServer().catch(error => {
    console.error('[MemoryBankMCP] Server startup error:', error);
}); 