import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs'; // Added for directory check

// Promisify exec
const execAsync = promisify(exec);

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
 * Stages all changes and performs a git commit in the specified working directory.
 */
export async function handleCommit({ emoji, type, title, description, working_directory }) {
    // Validate working_directory
    if (!working_directory) {
        throw new Error('Missing required argument: working_directory');
    }
    try {
        // Basic check: Does the directory exist?
        // Note: fs.promises.stat would be more robust for permissions etc., but fs.existsSync is simpler for now.
        if (!fs.existsSync(working_directory)) {
            throw new Error(`Invalid working_directory: Path does not exist - ${working_directory}`);
        }
        // Could add further checks like fs.lstatSync(working_directory).isDirectory()
    } catch (err) {
        throw new Error(`Error accessing working_directory "${working_directory}": ${err.message}`);
    }

    // Build the commit title
    const commitTitle = `${emoji} ${type}: ${title}`;

    try {
        // Stage all changes - Execute in provided working directory
        await execAsync('git add .', { cwd: working_directory });

        // Escape title and description
        const escapedCommitTitle = escapeShellArg(commitTitle);
        const escapedDescription = description ? escapeShellArg(description) : '';

        // Construct the commit command
        let commitCommand = `git commit -m "${escapedCommitTitle}"`;
        if (escapedDescription) {
            commitCommand += ` -m "${escapedDescription}"`;
        }

        // Execute commit command in provided working directory
        const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd: working_directory });

        if (commitStderr) {
            if (commitStderr.includes('nothing to commit, working tree clean')) {
                return { content: [{ type: "text", text: 'Nothing to commit, working tree clean.' }] };
            }
            // Allow commits with non-fatal stderr (e.g., warnings from hooks?)
            if (!commitStdout && !commitStderr.toLowerCase().includes('error') && !commitStderr.toLowerCase().includes('failed')) {
                // Get committed files even if there's non-fatal stderr
                let committedFilesList = '';
                try {
                    const { stdout: diffStdout } = await execAsync('git diff-tree --no-commit-id --name-only -r HEAD', { cwd: working_directory });
                    const committedFiles = diffStdout.trim().split('\n').filter(Boolean);
                    if (committedFiles.length > 0) {
                        committedFilesList = `\nFiles committed:\n- ${committedFiles.join('\n- ')}`;
                    }
                } catch (diffError) {
                    console.error('[handleCommit] Error getting diff-tree after commit with stderr:', diffError);
                    // Don't fail the whole commit, just log the diff error
                }
                return { content: [{ type: "text", text: `Commit successful: ${commitTitle} (with stderr: ${commitStderr.trim()})${committedFilesList}` }] };
            } else {
                throw new Error(`Git commit failed. Stderr: ${commitStderr.trim()}`);
            }
        }

        // Success - Get committed files
        let committedFilesList = '';
        try {
            const { stdout: diffStdout } = await execAsync('git diff-tree --no-commit-id --name-only -r HEAD', { cwd: working_directory });
            const committedFiles = diffStdout.trim().split('\n').filter(Boolean);
            if (committedFiles.length > 0) {
                committedFilesList = `\nFiles committed:\n- ${committedFiles.join('\n- ')}`;
            }
        } catch (diffError) {
            console.error('[handleCommit] Error getting diff-tree after successful commit:', diffError);
            // Don't fail the commit if diff-tree fails, just log the error and return base message
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        return { content: [{ type: "text", text: `Commit successful: ${commitTitle}${committedFilesList}` }] };
    } catch (error) {
        // Handle errors from execAsync (includes non-zero exit codes)
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Error:', error);
        throw new Error(`Git operation failed: ${errorMessage.trim()}`);
    }
} 