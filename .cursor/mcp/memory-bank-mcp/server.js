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
import { handleReadUserbrief, readUserbriefSchema } from './mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief, updateUserbriefSchema } from './mcp_tools/update_userbrief.js';

// Import task management tool handlers
import { handleCreateTask, createTaskSchema } from './mcp_tools/create_task.js';
import { handleUpdateTask, updateTaskSchema } from './mcp_tools/update_task.js';
import { handleGetNextTasks, getNextTasksSchema } from './mcp_tools/get_next_tasks.js';
import { handleGetAllTasks, getAllTasksSchema } from './mcp_tools/get_all_tasks.js';

// Create server instance
const server = new McpServer({
    name: 'memory-bank-mcp',
    version: '1.1.0'
});

// Register userbrief management tools
server.tool('read-userbrief', readUserbriefSchema, handleReadUserbrief);
server.tool('update-userbrief', updateUserbriefSchema, handleUpdateUserbrief);

// Register task management tools
server.tool('create_task', createTaskSchema, handleCreateTask);
server.tool('update-task', updateTaskSchema, handleUpdateTask);
server.tool('get_next_tasks', getNextTasksSchema, handleGetNextTasks);
server.tool('get_all_tasks', getAllTasksSchema, handleGetAllTasks);

// Start the server
async function startServer() {
    try {
        console.log('[MemoryBankMCP] Starting Memory Bank MCP Server v1.1.0');
        console.log('[MemoryBankMCP] Project root:', projectRoot);

        // Initialize server transport
        const transport = new StdioServerTransport();

        // Connect server to transport
        await server.connect(transport);

        console.log('[MemoryBankMCP] Server started successfully');
        console.log('[MemoryBankMCP] Available tools:');
        console.log('  - read-userbrief: Read userbrief.md and return unprocessed requests');
        console.log('  - update-userbrief: Update userbrief.md entry status and add comments');
        console.log('  - create_task: Create new tasks with auto-generated IDs');
        console.log('  - update-task: Update existing tasks by ID');
        console.log('  - get_next_tasks: Get available tasks with no pending dependencies');
        console.log('  - get_all_tasks: Get tasks with priority ordering');

    } catch (error) {
        console.error('[MemoryBankMCP] Failed to start server:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('[MemoryBankMCP] Shutting down server...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('[MemoryBankMCP] Shutting down server...');
    process.exit(0);
});

// Start the server
startServer().catch(error => {
    console.error('[MemoryBankMCP] Server startup error:', error);
    process.exit(1);
}); 