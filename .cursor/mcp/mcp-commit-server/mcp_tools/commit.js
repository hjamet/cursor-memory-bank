import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { getDefaultCwd } from '../lib/process_manager.js';

// Promisify exec
const execAsync = promisify(exec);

// Helper function to escape shell arguments safely
const escapeShellArg = (arg) => {
    if (arg === null || arg === undefined) {
        return '';
    }
    // Basic escaping for common shell metacharacters within double quotes
    return arg
        .replace(/\\/g, '\\\\') // \ -> \\
        .replace(/\$/g, '\\$')  // $ -> \$
        .replace(/"/g, '\\"')  // " -> \"
        .replace(/`/g, '\\`'); // ` -> \`
};

/**
 * MCP Tool handler for 'commit'.
 * Stages all changes and performs a git commit in the auto-detected working directory.
 * Handles non-blocking hook warnings correctly by checking exit code first.
 */
export async function handleCommit({ emoji, type, title, description }) {
    // --- Determine CWD and Repo Name --- 
    let cwd;
    let repoName = 'unknown repository';
    try {
        cwd = getDefaultCwd();
        if (!fs.existsSync(cwd)) {
            throw new Error(`Auto-detected CWD does not exist: ${cwd}`);
        }
        const { stdout: repoPathStdout } = await execAsync('git rev-parse --show-toplevel', { cwd });
        repoName = path.basename(repoPathStdout.trim());
    } catch (setupError) {
        console.error('[handleCommit] Error determining CWD or repo name:', setupError);
        throw new Error(`Failed to determine execution context: ${setupError.message}`);
    }
    // --- End CWD / Repo Name --- 

    const commitTitle = `${emoji} ${type}: ${title}`;

    try {
        // Stage all changes - Execute in auto-detected CWD
        await execAsync('git add .', { cwd });

        // Escape title and description
        const escapedCommitTitle = escapeShellArg(commitTitle);
        const escapedDescription = description ? escapeShellArg(description) : '';

        // Construct the commit command
        let commitCommand = `git commit -m "${escapedCommitTitle}"`;
        if (escapedDescription) {
            commitCommand += ` -m "${escapedDescription}"`;
        }

        // Execute commit command
        // execAsync will throw an error (caught below) if git commit exits non-zero
        const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd });

        // --- If execAsync resolved, commit succeeded (exit code 0) --- 

        // Check stderr specifically for "nothing to commit"
        if (commitStderr && commitStderr.includes('nothing to commit, working tree clean')) {
            return { content: [{ type: "text", text: `Nothing to commit in ${repoName}, working tree clean.` }] };
        }

        // Success - Get committed files
        let committedFilesList = '';
        try {
            const { stdout: diffStdout } = await execAsync('git diff-tree --no-commit-id --name-only -r HEAD', { cwd });
            const committedFiles = diffStdout.trim().split('\n').filter(Boolean);
            if (committedFiles.length > 0) {
                committedFilesList = `\nFiles committed:\n- ${committedFiles.join('\n- ')}`;
            }
        } catch (diffError) {
            console.error('[handleCommit] Error getting diff-tree after successful commit:', diffError);
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        // Construct success message, include stderr if it exists (as warning/info)
        let successMessage = `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}`;
        if (commitStderr) {
            successMessage += `\nCommit Warnings/Info (stderr):\n${commitStderr.trim()}`;
        }
        return { content: [{ type: "text", text: successMessage }] };

    } catch (error) {
        // --- If execAsync rejected, commit failed (non-zero exit code) --- 
        // The error object from execAsync usually contains stdout/stderr
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Git operation failed:', error);
        // Check specifically for 'nothing to commit' within the error output as well, just in case
        if (errorMessage.includes('nothing to commit, working tree clean')) {
            return { content: [{ type: "text", text: `Nothing to commit in ${repoName}, working tree clean.` }] };
        }
        throw new Error(`Git operation failed in ${repoName}: ${errorMessage.trim()}`);
    }
} 