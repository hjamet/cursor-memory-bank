import { z } from 'zod';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { handleReadMemory } from './mcp_tools/read_memory.js';
import { handleEditMemory } from './mcp_tools/edit_memory.js';
import { handleRemember } from './mcp_tools/remember.js';
import handleNextStep, { nextStepSchema } from './mcp_tools/next_step.js';
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

// Helper function to wrap handlers with error catching
function safeHandler(handler) {
    return async (args, a, b) => {
        try {
            return await handler(args, a, b);
        } catch (error) {
            // Re-throwing the error should be handled by the MCP SDK to create a proper JSON-RPC error response.
            throw new Error(error.message);
        }
    };
}

// Register the tools with the server
server.tool('read_memory', {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext'])
}, safeHandler(handleReadMemory));

server.tool('edit_memory', {
    context_file: z.enum(['activeContext', 'projectBrief', 'techContext']),
    content: z.string()
}, safeHandler(handleEditMemory));

server.tool('remember', {
    past: z.string(),
    present: z.string(),
    future: z.string(),
    long_term_memory: z.string().optional(),
}, safeHandler(handleRemember));

server.tool('next_step', nextStepSchema, safeHandler(handleNextStep));

server.tool('commit', {
    emoji: z.string(),
    type: z.string(),
    title: z.string(),
    description: z.string()
}, safeHandler(handleCommit));

server.tool('create_task', {
    title: z.string().min(1).max(200),
    short_description: z.string().min(1).max(500),
    detailed_description: z.string().min(1),
    dependencies: z.array(z.number().int().positive()).optional().default([]),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO'),
    impacted_files: z.array(z.string()).optional().default([]),
    validation_criteria: z.string().optional().default(''),
    parent_id: z.number().int().positive().optional(),
    priority: z.number().int().min(1).max(5).optional().default(3)
}, safeHandler(handleCreateTask));

server.tool('update_task', {
    task_id: z.number().int().positive(),
    title: z.string().min(1).max(200).optional(),
    short_description: z.string().min(1).max(500).optional(),
    detailed_description: z.string().min(1).optional(),
    dependencies: z.array(z.number().int().positive()).optional(),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional(),
    impacted_files: z.array(z.string()).optional(),
    validation_criteria: z.string().optional(),
    parent_id: z.number().int().positive().nullable().optional(),
    priority: z.number().int().min(1).max(5).optional()
}, safeHandler(handleUpdateTask));

server.tool('get_all_tasks', {
    count: z.number().int().min(1).max(100).optional().default(10),
    status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional(),
    priority_filter: z.number().int().min(1).max(5).optional(),
    include_subtasks: z.boolean().optional().default(true),
    include_dependencies: z.boolean().optional().default(true)
}, safeHandler(handleGetAllTasks));

server.tool('get_next_tasks', {
    limit: z.number().int().min(1).max(50).optional().default(10),
    include_completed: z.boolean().optional().default(false),
    include_blocked: z.boolean().optional().default(false),
    status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional(),
    priority_filter: z.number().int().min(1).max(5).optional()
}, safeHandler(handleGetNextTasks));

server.tool('read_userbrief', {
    archived_count: z.number().min(0).max(10).default(3).optional()
}, safeHandler(handleReadUserbrief));

server.tool('update_userbrief', {
    action: z.enum(['mark_archived', 'add_comment', 'mark_pinned']),
    id: z.number().optional(),
    comment: z.string().optional(),
}, safeHandler(handleUpdateUserbrief));


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