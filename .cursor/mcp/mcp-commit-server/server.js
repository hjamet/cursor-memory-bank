import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Helper function to escape shell arguments safely
// Escapes double quotes, dollar signs, backticks, and backslashes
const escapeShellArg = (arg) => {
    if (arg === null || arg === undefined) {
        return '';
    }
    // 1. Replace backslash with double backslash
    // 2. Replace dollar sign with backslash-dollar sign
    // 3. Replace double quote with backslash-double quote
    // 4. Replace backtick with backslash-backtick
    return arg
        .replace(/\\/g, '\\\\')
        .replace(/\$/g, '\\$')
        .replace(/"/g, '\\"')
        .replace(/`/g, '\\`');
};

// Define the input schema for the commit tool using Zod
const commitInputSchema = z.object({
    emoji: z.string().min(1, { message: 'Emoji is required' }),
    type: z.string().min(1, { message: 'Commit type is required (e.g., feat, fix)' }),
    title: z.string().min(1, { message: 'Commit title is required' }),
    description: z.string().optional(),
});

// Create an MCP server instance
const server = new McpServer({
    // No transport here
    name: "InternalGitCommit", // Added a name for clarity
    version: "0.1.2",         // Incremented version for schema change
    logLevel: 'info',         // Use 'debug' for more verbose logging if needed
});

// Define the commit tool
server.tool({
    name: 'commit',
    description: 'Stages all changes and creates a git commit with a conventional message format including title and optional description.',
    inputSchema: commitInputSchema,
    run: async (input) => {
        const { emoji, type, title, description } = input;
        const commitTitle = `${emoji} ${type}: ${title}`;

        try {
            // Stage all changes
            server.log('info', 'Running git add .');
            const { stdout: addStdout, stderr: addStderr } = await execAsync('git add .');
            if (addStderr) {
                server.log('warn', `Git add stderr: ${addStderr}`);
            }
            server.log('info', `Git add stdout: ${addStdout || '(no stdout)'}`);

            // Escape title and description
            const escapedCommitTitle = escapeShellArg(commitTitle);
            const escapedDescription = description ? escapeShellArg(description) : '';

            // Construct the commit command
            let commitCommand = `git commit -m "${escapedCommitTitle}"`;
            if (escapedDescription) {
                // Add a second -m flag for the description
                commitCommand += ` -m "${escapedDescription}"`;
            }

            server.log('info', `Running: ${commitCommand}`);
            const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand);

            if (commitStderr) {
                server.log('warn', `Git commit stderr: ${commitStderr}`);
                if (commitStderr.includes('nothing to commit, working tree clean')) {
                    return 'Nothing to commit, working tree clean.';
                }
                if (!commitStdout && !commitStderr.toLowerCase().includes('error') && !commitStderr.toLowerCase().includes('failed')) {
                    server.log('info', 'Git commit stderr detected, but assuming success based on context (no explicit "error" or "failed" found).');
                    // Return success message even with non-fatal stderr
                    return `Commit successful: ${commitTitle}`;
                } else { // Removed the specific check for .includes('error') to be more general
                    // Throw an error if stderr indicates a real problem or if stdout is missing without a clean exit indication
                    throw new Error(`Git commit failed. Stderr: ${commitStderr.trim()}`);
                }
            }
            server.log('info', `Git commit stdout: ${commitStdout || '(no stdout)'}`);

            // Return the primary commit title in the success message
            return `Commit successful: ${commitTitle}`;
        } catch (error) {
            server.log('error', 'Error during git commit process:', error);
            const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
            throw new Error(`Git operation failed: ${errorMessage.trim()}`);
        }
    },
});

// Create the transport and connect the server
async function startServer() {
    try {
        const transport = new StdioServerTransport();
        // Log *before* connecting, as connect might alter server state/methods
        server.log('info', 'MCP Commit Server attempting to connect via StdioTransport...');
        await server.connect(transport);
        // Log after connect might be problematic, log before instead.
        // server.log('info', 'MCP Commit Server connected via StdioTransport'); 
        console.log('[INFO] MCP Commit Server connection established.'); // Use console.log for post-connect status
    } catch (error) {
        console.error("Failed to start MCP Commit Server:", error);
        process.exit(1);
    }
}

// Start the server
startServer();
// console.log('MCP Commit Server started inside .cursor/mcp'); // Old message replaced by connect log 