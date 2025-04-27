import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

// Promisify exec
const execAsync = promisify(exec);

// Determine project root (assuming this file is in .cursor/mcp/mcp-commit-server/mcp_tools/)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../..');

// Helper function to escape shell arguments safely (copied from original server.js)
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

/**
 * MCP Tool handler for 'commit'.
 * Stages all changes and performs a git commit.
 */
export async function handleCommit({ emoji, type, title, description }) {
    // Build the commit title
    const commitTitle = `${emoji} ${type}: ${title}`;

    try {
        // Stage all changes - Execute in project root
        // Note: Using execAsync here as it's simpler for short-lived git commands.
        // Could potentially be replaced with spawnProcess from process_manager if needed,
        // but git commands are generally quick and exec handles them well.
        await execAsync('git add .', { cwd: projectRoot });

        // Escape title and description
        const escapedCommitTitle = escapeShellArg(commitTitle);
        const escapedDescription = description ? escapeShellArg(description) : '';

        // Construct the commit command
        let commitCommand = `git commit -m "${escapedCommitTitle}"`;
        if (escapedDescription) {
            commitCommand += ` -m "${escapedDescription}"`;
        }

        // Execute commit command
        const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd: projectRoot });

        if (commitStderr) {
            if (commitStderr.includes('nothing to commit, working tree clean')) {
                return { content: [{ type: "text", text: 'Nothing to commit, working tree clean.' }] };
            }
            // Allow commits with non-fatal stderr (e.g., warnings from hooks?)
            if (!commitStdout && !commitStderr.toLowerCase().includes('error') && !commitStderr.toLowerCase().includes('failed')) {
                return { content: [{ type: "text", text: `Commit successful: ${commitTitle} (with stderr: ${commitStderr.trim()})` }] };
            } else {
                throw new Error(`Git commit failed. Stderr: ${commitStderr.trim()}`);
            }
        }

        // Success
        return { content: [{ type: "text", text: `Commit successful: ${commitTitle}` }] };
    } catch (error) {
        // Handle errors from execAsync (includes non-zero exit codes)
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Error:', error);
        throw new Error(`Git operation failed: ${errorMessage.trim()}`);
    }
} 