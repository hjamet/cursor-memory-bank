import { z } from 'zod';
import { MCPServer } from '@cursor/mcp-core';
import { handleReadMemory, readMemorySchema } from './mcp_tools/read_memory.js';
import { handleEditMemory, editMemorySchema } from './mcp_tools/edit_memory.js';
import { handleRemember, rememberSchema } from './mcp_tools/remember.js';
import { handleNextRule, nextRuleSchema } from './mcp_tools/next_rule.js';
import { handleCommit, commitSchema } from './mcp_tools/commit.js';
import {
    handleCreateTask, createTaskSchema,
    handleUpdateTask, updateTaskSchema,
    handleGetAllTasks, getAllTasksSchema,
    handleGetNextTasks, getNextTasksSchema
} from './mcp_tools/task_management.js';
import {
    handleReadUserbrief, readUserbriefSchema,
    handleUpdateUserbrief, updateUserbriefSchema,
    handleAddUserbrief, addUserbriefSchema
} from './mcp_tools/userbrief_management.js';
import { StdioServerTransport } from '@cursor/mcp-core/transport.js';
import process from 'process';

// Create a new MCP server instance
const server = new MCPServer({
    name: 'MemoryBank',
    version: '1.2.0'
});

// Register the tools with the server
server.tool('read_memory', readMemorySchema, handleReadMemory);
server.tool('edit_memory', editMemorySchema, handleEditMemory);
server.tool('remember', rememberSchema, handleRemember);
server.tool('next_rule', nextRuleSchema, handleNextRule);
server.tool('commit', commitSchema, handleCommit);
server.tool('create_task', createTaskSchema, handleCreateTask);
server.tool('update_task', updateTaskSchema, handleUpdateTask);
server.tool('get_all_tasks', getAllTasksSchema, handleGetAllTasks);
server.tool('get_next_tasks', getNextTasksSchema, handleGetNextTasks);
server.tool('read_userbrief', readUserbriefSchema, handleReadUserbrief);
server.tool('update_userbrief', updateUserbriefSchema, handleUpdateUserbrief);
server.tool('add_userbrief', addUserbriefSchema, handleAddUserbrief);


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