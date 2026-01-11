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

// Zod schema for the commit tool
export const commitSchema = {
    emoji: z.string().describe("Emoji to use in the commit message (e.g. :sparkles:)"),
    type: z.string().describe("Type of change (e.g. feat, fix, docs, style, refactor, test, chore)"),
    title: z.string().describe("Brief commit title"),
    description: z.string().describe("Detailed description of changes")
};

/**
 * Determines the appropriate CWD based on server args, env vars, or process CWD.
 * Adapted from ToolsMCP's process_manager.js getDefaultCwd function.
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

/**
 * Gets modified files from git (staged and unstaged changes)
 * @param {string} cwd - Working directory to run git commands in
 * @returns {Promise<Array>} Array of modified file paths
 */
async function getModifiedFiles(cwd) {
    try {
        // Get staged files
        const stagedResult = await execAsync('git diff --cached --name-only', { cwd });
        const stagedFiles = stagedResult.stdout.trim() ? stagedResult.stdout.trim().split('\n') : [];

        // Get unstaged modified files
        const unstagedResult = await execAsync('git diff --name-only', { cwd });
        const unstagedFiles = unstagedResult.stdout.trim() ? unstagedResult.stdout.trim().split('\n') : [];

        // Get untracked files
        const untrackedResult = await execAsync('git ls-files --others --exclude-standard', { cwd });
        const untrackedFiles = untrackedResult.stdout.trim() ? untrackedResult.stdout.trim().split('\n') : [];

        // Combine and deduplicate
        const allFiles = [...new Set([...stagedFiles, ...unstagedFiles, ...untrackedFiles])];

        return allFiles.filter(file => file && file.trim() !== '');
    } catch (error) {
        console.error('[getModifiedFiles] Error getting modified files:', error.message);
        return [];
    }
}

/**
 * Scans only modified files to identify oversized code files (>500 lines)
 * @param {string} cwd - Working directory 
 * @returns {Promise<Array>} Array of file analysis objects with properties: file, lines, oversized, extension
 */
async function scanModifiedCodeFiles(cwd) {
    const results = [];
    const MAX_LINES = 500;

    // Supported file extensions
    const SUPPORTED_EXTENSIONS = ['.py', '.js', '.tex', '.html', '.css', '.sh'];

    try {
        // Get only modified files instead of scanning all files
        const modifiedFiles = await getModifiedFiles(cwd);

        for (const relativePath of modifiedFiles) {
            // Check if file has a supported extension
            const hasValidExtension = SUPPORTED_EXTENSIONS.some(ext => relativePath.endsWith(ext));

            if (hasValidExtension) {
                // Skip install.sh from this repository
                if (relativePath === 'install.sh' || relativePath.endsWith('/install.sh')) {
                    continue;
                }

                const fullPath = path.join(cwd, relativePath);

                try {
                    // Check if file exists (might be deleted)
                    if (fs.existsSync(fullPath)) {
                        const content = fs.readFileSync(fullPath, 'utf8');
                        const lineCount = content.split('\n').length;

                        results.push({
                            file: relativePath,
                            lines: lineCount,
                            oversized: lineCount > MAX_LINES,
                            extension: path.extname(relativePath).toLowerCase()
                        });
                    }
                } catch (fileError) {
                    // Skip files that can't be read
                    console.error(`[scanModifiedCodeFiles] Error reading file ${fullPath}:`, fileError.message);
                }
            }
        }
    } catch (error) {
        console.error('[scanModifiedCodeFiles] Error scanning modified files:', error.message);
    }

    return results;
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

/**
 * MCP Tool handler for 'commit'.
 * Stages all changes, performs a git commit, and reports oversized files.
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
        throw new Error(`Failed to determine execution context: ${setupError.message}`);
    }

    const commitTitle = `${emoji} ${type}: ${title}`;

    // --- Scan modified code files before commit ---
    let codeScanResults = [];
    try {
        codeScanResults = await scanModifiedCodeFiles(cwd);
    } catch (scanError) {
        console.error('[handleCommit] Error scanning modified code files:', scanError.message);
        // Continue with commit even if scan fails
    }

    try {
        // Stage all changes
        await execAsync('git add .', { cwd });

        // Escape title
        const escapedCommitTitle = escapeShellArg(commitTitle);

        // Construct the commit command
        let commitCommand = `git commit -m "${escapedCommitTitle}"`;

        // Handle multi-line description by adding multiple -m flags
        if (description && description.trim() !== '') {
            const paragraphs = description.split('\n');
            for (const paragraph of paragraphs) {
                if (paragraph.trim() !== '') {
                    const escapedParagraph = escapeShellArg(paragraph);
                    commitCommand += ` -m "${escapedParagraph}"`;
                }
            }
        }

        // Execute commit command
        const { stdout: commitStdout, stderr: commitStderr } = await execAsync(commitCommand, { cwd });

        // Check stderr specifically for "nothing to commit"
        if (commitStderr && commitStderr.includes('nothing to commit, working tree clean')) {
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        status: 'success',
                        message: `Nothing to commit in ${repoName}, working tree clean.`
                    }, null, 2)
                }]
            };
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
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        // Construct success message
        let successMessage = `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}`;
        if (commitStderr) {
            successMessage += `\nCommit Warnings/Info (stderr):\n${commitStderr.trim()}`;
        }

        // Report oversized files if any
        const oversizedFiles = codeScanResults.filter(file => file.oversized);
        if (oversizedFiles.length > 0) {
            successMessage += `\n\n⚠️  ATTENTION: Files with more than 500 lines detected:`;
            oversizedFiles.forEach(file => {
                const fileType = path.extname(file.file).replace('.', '').toUpperCase();
                successMessage += `\n  • ${file.file} (${fileType}): ${file.lines} lines (${file.lines - 500} over limit)`;
            });
            successMessage += `\n\nPlease consider refactoring these files to improve maintainability.`;
            successMessage += `\nThe agent should mention these oversized files to the user for potential refactoring.`;
        }

        // Add recent git log output
        try {
            const now = new Date();
            const formattedDate = now.toISOString().replace('T', ' ').substring(0, 19);
            const datePrefix = `  Current time: ${formattedDate}\n`;

            const gitLogCommand = 'git log -n 5 --pretty=format:"%C(auto)%h %Cgreen[%an] %Cblue%cd%Creset — %s%n%b" --date=format:"%Y-%m-%d %H:%M:%S" | cat';
            const { stdout: gitLogStdout } = await execAsync(gitLogCommand, { cwd });

            if (gitLogStdout && gitLogStdout.trim() !== '') {
                successMessage += `\n\n--- Recent Activity (Last 5 Commits) ---\n${datePrefix}${gitLogStdout.trim()}`;
            }
        } catch (logCmdError) {
            successMessage += '\n\n(Failed to retrieve recent git log output)';
        }

        return {
            content: [{
                type: "text",
                text: JSON.stringify({
                    status: 'success',
                    message: successMessage,
                    oversized_files: oversizedFiles.map(file => ({
                        file: file.file,
                        lines: file.lines,
                        extension: file.extension,
                        excess_lines: file.lines - 500
                    }))
                }, null, 2)
            }]
        };

    } catch (error) {
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';

        // Check for 'nothing to commit' in error message
        if (errorMessage.includes('nothing to commit, working tree clean')) {
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        status: 'success',
                        message: `Nothing to commit in ${repoName}, working tree clean.`
                    }, null, 2)
                }]
            };
        }

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Git operation failed: ${error.message}`
                }, null, 2)
            }]
        };
    }
} 