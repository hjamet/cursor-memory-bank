import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming server.js is in .cursor/mcp/memory-bank-mcp/)
const projectRoot = path.resolve(__dirname, '../../..');

// Import userbrief tool handlers
import { handleReadUserbrief } from './mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief } from './mcp_tools/update_userbrief.js';

// Import task management tool handlers
import { handleCreateTask } from './mcp_tools/create_task.js';
import { handleUpdateTask } from './mcp_tools/update_task.js';
import { handleGetNextTasks } from './mcp_tools/get_next_tasks.js';
import { handleGetAllTasks, getAllTasksSchema } from './mcp_tools/get_all_tasks.js';

// Import commit tool handler
import { handleCommit, commitSchema } from './mcp_tools/commit.js';

// Import memory management tool handlers
import { handleReadMemory, readMemorySchema } from './mcp_tools/read_memory.js';
import { handleEditMemory, editMemorySchema } from './mcp_tools/edit_memory.js';

// Import remember tool
import { handleRemember, rememberSchema } from './mcp_tools/remember.js';

// Import next_rule tool
import { handleNextRule, nextRuleSchema } from './mcp_tools/next_rule.js';

// Create server instance
const server = new McpServer({
    name: 'memory-bank-mcp',
    version: '1.1.0'
});

// Register userbrief management tools
server.tool(
    'read-userbrief',
    {
        archived_count: z.number().min(0).max(10).default(3).optional()
            .describe('Number of archived entries to include in response. (optional, default: 3)')
    },
    handleReadUserbrief
);

server.tool(
    'update-userbrief',
    {
        action: z.enum(['mark_in_progress', 'mark_archived', 'add_comment'])
            .describe("Action to perform on the userbrief entry. (required)"),
        id: z.number().optional()
            .describe('ID of the request to update. If not provided, the tool targets the current active request. (optional)'),
        comment: z.string().optional()
            .describe("Comment to add to the request's history. Only used with 'add_comment' action. (optional)"),
    },
    handleUpdateUserbrief
);

// Register task management tools
server.tool(
    'create_task',
    {
        title: z.string().min(1).max(200).describe('Short descriptive title of the task. (required)'),
        short_description: z.string().min(1).max(500).describe('Brief one-sentence description of what needs to be done. (required)'),
        detailed_description: z.string().min(1).describe('Comprehensive description with implementation details. (required)'),
        dependencies: z.array(z.number().int().positive()).optional().default([]).describe('Array of task IDs that must be completed before this task. (optional, default: [])'),
        status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe("Initial status of the task. (optional, default: 'TODO')"),
        impacted_files: z.array(z.string()).optional().default([]).describe('List of files or rules affected by this task. (optional, default: [])'),
        validation_criteria: z.string().optional().default('').describe('Clear criteria to determine when the task is successfully completed. (optional)'),
        parent_id: z.number().int().positive().optional().describe('ID of a parent task if this is a sub-task. (optional)'),
        priority: z.number().int().min(1).max(5).optional().default(3).describe('Priority level from 1 (highest) to 5 (lowest). (optional, default: 3)')
    },
    handleCreateTask
);

server.tool(
    'update-task',
    {
        task_id: z.number().int().positive().describe('ID of the task to update. (required)'),
        title: z.string().min(1).max(200).optional().describe('Updated task title. (optional)'),
        short_description: z.string().min(1).max(500).optional().describe('Updated brief description. (optional)'),
        detailed_description: z.string().min(1).optional().describe('Updated detailed description. (optional)'),
        dependencies: z.array(z.number().int().positive()).optional().describe('Updated array of dependency task IDs. (optional)'),
        status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Updated task status. (optional)'),
        impacted_files: z.array(z.string()).optional().describe('Updated list of affected files. (optional)'),
        validation_criteria: z.string().optional().describe('Updated validation criteria. (optional)'),
        parent_id: z.number().int().positive().nullable().optional().describe('Updated parent task ID. Use null to remove the parent. (optional)'),
        priority: z.number().int().min(1).max(5).optional().describe('Updated priority level from 1 (highest) to 5 (lowest). (optional)')
    },
    handleUpdateTask
);

server.tool(
    'get_next_tasks',
    {
        limit: z.number().int().min(1).max(50).optional().default(10).describe('Maximum number of tasks to return. (optional, default: 10)'),
        include_completed: z.boolean().optional().default(false).describe('If true, include completed tasks in the results. (optional, default: false)'),
        include_blocked: z.boolean().optional().default(false).describe('If true, include blocked tasks in the results. (optional, default: false)'),
        status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Filter tasks by a specific status. (optional)'),
        priority_filter: z.number().int().min(1).max(5).optional().describe('Filter tasks by a specific priority level. (optional)')
    },
    handleGetNextTasks
);

server.tool('get_all_tasks', getAllTasksSchema, handleGetAllTasks);
server.tool('commit', commitSchema, handleCommit);
server.tool('read_memory', readMemorySchema, handleReadMemory);
server.tool('edit_memory', editMemorySchema, handleEditMemory);
server.tool('remember', rememberSchema, handleRemember);
server.tool('next_rule', nextRuleSchema, handleNextRule);

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
    process.exit(1);
}); 