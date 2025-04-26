import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define the project root relative to the server script's location
const projectRoot = path.resolve(__dirname, '../../..');

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

// Create an MCP server instance
const server = new McpServer({
    name: "InternalGitCommit",
    version: "0.1.9", // Incremented version for CWD fix
    capabilities: { tools: {} } // Explicitly declare capabilities
});

// Define the commit tool following EXACTLY the example structure
server.tool(
    'commit',
    // Define schema directly in the call as individual properties, not using z.object()
    {
        emoji: z.string().describe("Emoji to use in the commit message (e.g. :sparkles:)"),
        type: z.string().describe("Type of change (e.g. feat, fix, docs, style, refactor, test, chore)"),
        title: z.string().describe("Brief commit title"),
        description: z.string().optional().describe("Optional detailed description of changes")
    },
    async ({ emoji, type, title, description }) => {
        // Build the commit title
        const commitTitle = `${emoji} ${type}: ${title}`;

        try {
            // Stage all changes - Execute in project root
            const { stdout: addStdout, stderr: addStderr } = await execAsync('git add .', { cwd: projectRoot });

            // Escape title and description
            const escapedCommitTitle = escapeShellArg(commitTitle);
            const escapedDescription = description ? escapeShellArg(description) : '';

            // Construct the commit command
            let commitCommand = `git commit -m "${escapedCommitTitle}"`;
            if (escapedDescription) {
                // Add a second -m flag for the description
                commitCommand += ` -m "${escapedDescription}"`;
            }

            // Execute commit command in project root
            const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd: projectRoot });

            if (commitStderr) {
                if (commitStderr.includes('nothing to commit, working tree clean')) {
                    return { content: [{ type: "text", text: 'Nothing to commit, working tree clean.' }] };
                }

                if (!commitStdout && !commitStderr.toLowerCase().includes('error') && !commitStderr.toLowerCase().includes('failed')) {
                    // Return success message even with non-fatal stderr
                    return { content: [{ type: "text", text: `Commit successful: ${commitTitle}` }] };
                } else {
                    // Throw an error if stderr indicates a real problem
                    throw new Error(`Git commit failed. Stderr: ${commitStderr.trim()}`);
                }
            }

            // Return the primary commit title in the success message
            return { content: [{ type: "text", text: `Commit successful: ${commitTitle}` }] };
        } catch (error) {
            const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
            throw new Error(`Git operation failed: ${errorMessage.trim()}`);
        }
    }
);

// Create the transport and connect the server
async function startServer() {
    try {
        const transport = new StdioServerTransport();
        await server.connect(transport);
    } catch (error) {
        // Keep console.error for fatal startup errors ONLY
        console.error("Failed to start MCP Commit Server:", error);
        process.exit(1);
    }
}

// Start the server
startServer(); 