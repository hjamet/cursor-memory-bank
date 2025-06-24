import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';
import { z } from 'zod';

// Promisify exec
const execAsync = promisify(exec);

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming server.js is in .cursor/mcp/memory-bank-mcp/)
const projectRoot = path.resolve(__dirname, '../../..');

/**
 * Determines the appropriate CWD based on server args, env vars, or process CWD.
 * Adapted from MyMCP's process_manager.js getDefaultCwd function.
 * @returns {string} The determined CWD.
 */
function getDefaultCwd() {
    // Parse server startup args for default CWD
    let serverDefaultCwd = null;
    const cwdIndex = process.argv.indexOf('--cwd');
    if (cwdIndex > -1 && process.argv[cwdIndex + 1]) {
        serverDefaultCwd = path.resolve(process.argv[cwdIndex + 1]);
    }

    // PRIORITIZE: Server --cwd Arg > Env Var > Server process.cwd()
    return serverDefaultCwd || process.env.CURSOR_WORKSPACE_ROOT || process.cwd();
}

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

// Zod schema for the commit tool
export const commitSchema = {
    emoji: z.string().describe("Emoji to use in the commit message (e.g. :sparkles:)"),
    type: z.string().describe("Type of change (e.g. feat, fix, docs, style, refactor, test, chore)"),
    title: z.string().describe("Brief commit title"),
    description: z.string().describe("Detailed description of changes")
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
        // Debug logging removed to prevent JSON-RPC pollution
        // console.error('[handleCommit] Error determining CWD or repo name:', setupError);
        throw new Error(`Failed to determine execution context: ${setupError.message}`);
    }
    // --- End CWD / Repo Name --- 

    const commitTitle = `${emoji} ${type}: ${title}`;

    try {
        // Stage all changes - Execute in auto-detected CWD
        await execAsync('git add .', { cwd });

        // Escape title
        const escapedCommitTitle = escapeShellArg(commitTitle);

        // Construct the commit command
        let commitCommand = `git commit -m "${escapedCommitTitle}"`;

        // Handle multi-line description by adding multiple -m flags
        if (description && description.trim() !== '') {
            const paragraphs = description.split('\n');
            for (const paragraph of paragraphs) {
                if (paragraph.trim() !== '') { // Avoid adding -m for empty lines
                    const escapedParagraph = escapeShellArg(paragraph);
                    commitCommand += ` -m "${escapedParagraph}"`;
                }
            }
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
            // Debug logging removed to prevent JSON-RPC pollution
            // console.error('[handleCommit] Error getting diff-tree after successful commit:', diffError);
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        // Construct success message, include stderr if it exists (as warning/info)
        let successMessage = `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}`;
        if (commitStderr) {
            successMessage += `\nCommit Warnings/Info (stderr):\n${commitStderr.trim()}`;
        }

        // Add recent git log output as requested by user
        try {
            // 1. Get current date/time in JavaScript and format it
            const now = new Date();
            const year = now.getFullYear();
            const month = (now.getMonth() + 1).toString().padStart(2, '0');
            const day = now.getDate().toString().padStart(2, '0');
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            const formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            const datePrefix = `  Heure actuelle : ${formattedDate}\n`;

            // 2. Define the git log command (without the echo part)
            const gitLogOnlyCommand = 'git log -n 5 --pretty=format:"%C(auto)%h %Cgreen[%an] %Cblue%cd%Creset — %s%n%b" --date=format:"%Y-%m-%d %H:%M:%S" | cat';

            // 3. Execute the git log command
            const { stdout: gitLogStdout } = await execAsync(gitLogOnlyCommand, { cwd, shell: "C:\\Program Files\\Git\\bin\\bash.exe" });

            // 4. Prepend date and append git log to successMessage
            if (gitLogStdout && gitLogStdout.trim() !== '') {
                successMessage += `\n\n--- Recent Activity (Last 5 Commits) ---\n${datePrefix}${gitLogStdout.trim()}`;
            }
        } catch (logCmdError) {
            // Debug logging removed to prevent JSON-RPC pollution
            // console.error('[handleCommit] Error executing git log command:', logCmdError);
            successMessage += '\n\n(Failed to retrieve recent git log output)';
        }

        return { content: [{ type: "text", text: successMessage }] };

    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.error('[handleCommit] Git operation failed:', error);

        // --- If execAsync rejected, commit failed (non-zero exit code) --- 
        // The error object from execAsync usually contains stdout/stderr
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Git operation failed:', error);
        // Check specifically for 'nothing to commit' within the error output as well, just in case
        if (errorMessage.includes('nothing to commit, working tree clean')) {
            return { content: [{ type: "text", text: `Nothing to commit in ${repoName}, working tree clean.` }] };
        }
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({ status: 'error', message: `Git operation failed: ${error.message}` }, null, 2)
            }]
        };
    } finally {
        // console.error('[handleCommit] Git operation failed:', error);
    }
} 