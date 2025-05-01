import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { getDefaultCwd } from '../lib/process_manager.js'; // Import CWD helper

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
 * Stages all changes and performs a git commit in the auto-detected working directory.
 */
export async function handleCommit({ emoji, type, title, description }) {
    // --- Determine CWD and Repo Name --- 
    let cwd;
    let repoName = 'unknown repository';
    try {
        cwd = getDefaultCwd();
        // Validate CWD existence (basic check)
        if (!fs.existsSync(cwd)) {
            throw new Error(`Auto-detected CWD does not exist: ${cwd}`);
        }
        // Get repo name
        const { stdout: repoPathStdout } = await execAsync('git rev-parse --show-toplevel', { cwd });
        repoName = path.basename(repoPathStdout.trim());
    } catch (setupError) {
        console.error('[handleCommit] Error determining CWD or repo name:', setupError);
        throw new Error(`Failed to determine execution context: ${setupError.message}`);
    }
    // --- End CWD / Repo Name --- 

    // Build the commit title
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

        // Execute commit command in auto-detected CWD
        const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd });

        if (commitStderr) {
            if (commitStderr.includes('nothing to commit, working tree clean')) {
                return { content: [{ type: "text", text: `Nothing to commit in ${repoName}, working tree clean.` }] };
            }
            // Allow commits with non-fatal stderr (e.g., warnings from hooks?)
            if (!commitStdout && !commitStderr.toLowerCase().includes('error') && !commitStderr.toLowerCase().includes('failed')) {
                // Get committed files even if there's non-fatal stderr
                let committedFilesList = '';
                try {
                    const { stdout: diffStdout } = await execAsync('git diff-tree --no-commit-id --name-only -r HEAD', { cwd });
                    const committedFiles = diffStdout.trim().split('\n').filter(Boolean);
                    if (committedFiles.length > 0) {
                        committedFilesList = `\nFiles committed:\n- ${committedFiles.join('\n- ')}`;
                    }
                } catch (diffError) {
                    console.error('[handleCommit] Error getting diff-tree after commit with stderr:', diffError);
                }
                return { content: [{ type: "text", text: `Commit successful in ${repoName}: ${commitTitle} (with stderr: ${commitStderr.trim()})${committedFilesList}` }] };
            } else {
                throw new Error(`Git commit failed in ${repoName}. Stderr: ${commitStderr.trim()}`);
            }
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
        return { content: [{ type: "text", text: `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}` }] };
    } catch (error) {
        // Handle errors from execAsync (includes non-zero exit codes)
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Error:', error);
        throw new Error(`Git operation failed in ${repoName}: ${errorMessage.trim()}`);
    }
} 