import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import { getDefaultCwd } from '../lib/process_manager.js'; // Import CWD helper

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
        const { stdout: repoPathStdout } = await execa('git', ['rev-parse', '--show-toplevel'], { cwd });
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
        await execa('git', ['add', '.'], { cwd });

        const commitArgs = ['commit'];
        commitArgs.push('-m', commitTitle);
        if (description) {
            commitArgs.push('-m', description);
        }

        // Use reject: false to inspect exit code and stderr manually
        const { stdout: commitStdout, stderr: commitStderr, exitCode } = await execa('git', commitArgs, { cwd, reject: false });

        // Case 1: Nothing to commit (specific stderr message)
        if (exitCode === 1 && commitStderr && commitStderr.includes('nothing to commit, working tree clean')) {
            return { content: [{ type: "text", text: `Nothing to commit in ${repoName}, working tree clean.` }] };
        }

        // Case 2: Commit failed for other reasons (non-zero exit code OR fatal stderr keywords)
        if (exitCode !== 0 || (commitStderr && (commitStderr.toLowerCase().includes('fatal:') || commitStderr.toLowerCase().includes('error:') || commitStderr.toLowerCase().includes('failed to push')))) {
            // Construct more informative error
            let errMsg = `Git commit failed in ${repoName}. Exit Code: ${exitCode}.`;
            if (commitStderr) errMsg += ` Stderr: ${commitStderr.trim()}`;
            if (commitStdout) errMsg += ` Stdout: ${commitStdout.trim()}`;
            console.error('[handleCommit] Failure:', errMsg);
            throw new Error(errMsg);
        }

        // Case 3: Commit succeeded (exit code 0), potentially with non-fatal stderr (like hook warnings)
        let committedFilesList = '';
        try {
            const { stdout: diffStdout } = await execa('git', ['diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'], { cwd });
            const committedFiles = diffStdout.trim().split('\n').filter(Boolean);
            if (committedFiles.length > 0) {
                committedFilesList = `\nFiles committed:\n- ${committedFiles.join('\n- ')}`;
            }
        } catch (diffError) {
            console.error('[handleCommit] Error getting diff-tree after successful commit:', diffError);
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        let successMessage = `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}`;
        if (commitStderr) { // Append any stderr (like hook warnings)
            successMessage += `\n(Stderr: ${commitStderr.trim()})`
        }

        return { content: [{ type: "text", text: successMessage }] };
    } catch (error) {
        // Ensure error is an instance of Error for consistent message access
        const errorObj = error instanceof Error ? error : new Error(String(error));
        const errorMessage = errorObj.message || 'Unknown error during git operation';
        console.error('[handleCommit] Caught Error:', errorObj);
        // Rethrow but ensure it's always an Error object
        throw new Error(`Git operation failed in ${repoName}: ${errorMessage.trim()}`);
    }
} 