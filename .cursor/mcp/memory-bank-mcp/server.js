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
import { handleGetAllTasks } from './mcp_tools/get_all_tasks.js';

// Import commit tool handler
import { handleCommit } from './mcp_tools/commit.js';

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
            .describe('Number of archived entries to include in response (default: 3)')
    },
    handleReadUserbrief
);

server.tool(
    'update-userbrief',
    {
        action: z.enum(['mark_in_progress', 'mark_archived', 'add_comment']).describe('Action to perform on userbrief entry'),
        line_number: z.number().min(1).optional().describe('Line number of the entry to update (optional if auto-detecting current request)'),
        comment: z.string().optional().describe('Comment to add when archiving a task or adding notes'),
        auto_current: z.boolean().default(true).optional().describe('Automatically find and update the current unprocessed/in-progress request (default: true)')
    },
    handleUpdateUserbrief
);

// Register task management tools
server.tool(
    'create_task',
    {
        title: z.string().min(1).max(200).describe('Short descriptive title of the task'),
        short_description: z.string().min(1).max(500).describe('Brief one-sentence description of what needs to be done'),
        detailed_description: z.string().min(1).describe('Comprehensive description with implementation details'),
        dependencies: z.array(z.number().int().positive()).optional().default([]).describe('Array of task IDs that must be completed before this task'),
        status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe('Initial status of the task'),
        impacted_files: z.array(z.string()).optional().default([]).describe('List of files or rules affected by this task'),
        validation_criteria: z.string().optional().default('').describe('Clear criteria to determine when the task is successfully completed'),
        parent_id: z.number().int().positive().optional().describe('ID of parent task for sub-tasks'),
        priority: z.number().int().min(1).max(5).optional().default(3).describe('Priority level (1=highest, 5=lowest)')
    },
    handleCreateTask
);

server.tool(
    'update-task',
    {
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
    },
    handleUpdateTask
);

server.tool(
    'get_next_tasks',
    {
        limit: z.number().int().min(1).max(50).optional().default(10).describe('Maximum number of tasks to return'),
        include_completed: z.boolean().optional().default(false).describe('Include completed tasks in results'),
        include_blocked: z.boolean().optional().default(false).describe('Include blocked tasks in results'),
        status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Filter by specific status'),
        priority_filter: z.number().int().min(1).max(5).optional().describe('Filter by specific priority level')
    },
    handleGetNextTasks
);

server.tool(
    'get_all_tasks',
    {
        count: z.number().int().min(1).max(100).optional().default(10).describe('Number of tasks to return (default: 10)'),
        status_filter: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Filter by specific status'),
        priority_filter: z.number().int().min(1).max(5).optional().describe('Filter by specific priority level'),
        include_subtasks: z.boolean().optional().default(true).describe('Include sub-tasks in results'),
        include_dependencies: z.boolean().optional().default(true).describe('Include dependency information in response')
    },
    handleGetAllTasks
);

// Register commit tool
server.tool(
    'commit',
    {
        emoji: z.string().describe("Emoji to use in the commit message (e.g. :sparkles:)"),
        type: z.string().describe("Type of change (e.g. feat, fix, docs, style, refactor, test, chore)"),
        title: z.string().describe("Brief commit title"),
        description: z.string().describe("Detailed description of changes")
    },
    handleCommit
);

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