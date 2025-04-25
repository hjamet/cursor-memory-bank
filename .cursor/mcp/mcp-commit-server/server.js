import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Define the input schema for the commit tool using Zod
const commitInputSchema = z.object({
    emoji: z.string().min(1, { message: 'Emoji is required' }),
    type: z.string().min(1, { message: 'Commit type is required (e.g., feat, fix)' }),
    message: z.string().min(1, { message: 'Commit message is required' }),
});

// Create an MCP server instance
const server = new McpServer({
    // No transport here
    name: "InternalGitCommit", // Added a name for clarity
    version: "0.1.1",         // Incremented version
    logLevel: 'info',         // Use 'debug' for more verbose logging if needed
});

// Define the commit tool
server.tool({
    name: 'commit',
    description: 'Stages all changes and creates a git commit with a conventional message format.',
    inputSchema: commitInputSchema,
    run: async (input) => {
        const { emoji, type, message } = input;
        const commitMessage = `${emoji} ${type}: ${message}`;

        try {
            // Stage all changes
            console.log('Running git add .');
            const { stdout: addStdout, stderr: addStderr } = await execAsync('git add .');
            if (addStderr) {
                console.warn(`Git add stderr: ${addStderr}`);
            }
            console.log(`Git add stdout: ${addStdout || '(no stdout)'}`);

            // Commit changes
            // Escape the commit message to handle special characters (quotes, dollar signs, backticks)
            const escapedCommitMessage = commitMessage
                .replace(/"/g, '\"') // Escape double quotes
                .replace(/\$/g, '\\$') // Escape dollar signs
                .replace(/`/g, '\`'); // Escape backticks

            const commitCommand = `git commit -m "${escapedCommitMessage}"`;
            console.log(`Running: ${commitCommand}`);
            const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand);

            if (commitStderr) {
                console.warn(`Git commit stderr: ${commitStderr}`);
                // Check for common non-error messages in stderr
                if (commitStderr.includes('nothing to commit, working tree clean')) {
                    return 'Nothing to commit, working tree clean.';
                }
                // Otherwise, assume stderr might indicate success despite warnings
            }
            console.log(`Git commit stdout: ${commitStdout || '(no stdout)'}`);

            return `Commit successful: ${commitMessage}`;
        } catch (error) {
            console.error('Error during git commit process:', error);
            const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
            // Provide a clearer error message back to the MCP client
            throw new Error(`Git operation failed: ${errorMessage.trim()}`);
        }
    },
});

// Create the transport and connect the server
async function startServer() {
    try {
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.log('MCP Commit Server connected via StdioTransport');
    } catch (error) {
        console.error("Failed to start MCP Commit Server:", error);
        process.exit(1);
    }
}

// Start the server
startServer();
// console.log('MCP Commit Server started inside .cursor/mcp'); // Old message replaced by connect log 