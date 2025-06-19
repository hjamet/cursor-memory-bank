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

// Import tool handlers
import { handleReadUserbrief, readUserbriefSchema } from './mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief, updateUserbriefSchema } from './mcp_tools/update_userbrief.js';

// Create server instance
const server = new McpServer({
    name: 'memory-bank-mcp',
    version: '1.0.0'
});

// Register tools
server.tool('read-userbrief', 'Read userbrief.md and return current unprocessed or in-progress request', readUserbriefSchema, handleReadUserbrief);
server.tool('update-userbrief', 'Update userbrief.md entry status (mark in-progress, archived, or add comments)', updateUserbriefSchema, handleUpdateUserbrief);

// Handle server startup
async function main() {
    console.log('[MemoryBankMCP] Server started successfully.');

    // Create transport for stdio communication
    const transport = new StdioServerTransport();

    // Connect server to transport
    await server.connect(transport);

    console.log('[MemoryBankMCP] Connected to transport. Ready to handle requests.');
}

// Handle process signals
process.on('SIGINT', () => {
    console.log('[MemoryBankMCP] Received SIGINT, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('[MemoryBankMCP] Received SIGTERM, shutting down gracefully...');
    process.exit(0);
});

// Start the server
main().catch((error) => {
    console.error('[MemoryBankMCP] Server error:', error);
    process.exit(1);
}); 