import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';
import { z } from 'zod';
import { handleCreateTask } from './create_task.js';

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

/**
 * Recursively scans directory for Python files and counts their lines
 * @param {string} dirPath - Directory to scan
 * @param {string} rootPath - Root path for relative file paths
 * @returns {Array} Array of objects with file info: {file, lines, oversized}
 */
function scanPythonFiles(dirPath, rootPath = dirPath) {
    const results = [];
    const MAX_LINES = 500;

    try {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dirPath, entry.name);

            if (entry.isDirectory()) {
                // Skip common directories that shouldn't be scanned
                const skipDirs = ['node_modules', '.git', '__pycache__', '.venv', 'venv', '.env'];
                if (!skipDirs.includes(entry.name)) {
                    results.push(...scanPythonFiles(fullPath, rootPath));
                }
            } else if (entry.isFile() && entry.name.endsWith('.py')) {
                try {
                    const content = fs.readFileSync(fullPath, 'utf8');
                    const lineCount = content.split('\n').length;
                    const relativePath = path.relative(rootPath, fullPath);

                    results.push({
                        file: relativePath,
                        lines: lineCount,
                        oversized: lineCount > MAX_LINES
                    });
                } catch (fileError) {
                    // Skip files that can't be read
                    console.error(`[scanPythonFiles] Error reading file ${fullPath}:`, fileError.message);
                }
            }
        }
    } catch (dirError) {
        // Skip directories that can't be read
        console.error(`[scanPythonFiles] Error reading directory ${dirPath}:`, dirError.message);
    }

    return results;
}

/**
 * Creates actual refactoring tasks for oversized Python files
 * @param {Array} oversizedFiles - Array of file objects that are oversized
 * @returns {Promise<Array>} Array of created task objects or error results
 */
async function createRefactoringTasks(oversizedFiles) {
    const createdTasks = [];

    for (const fileInfo of oversizedFiles) {
        try {
            // Determine priority based on file size
            let priority = 3; // Default priority
            if (fileInfo.lines > 1500) {
                priority = 5; // Very high priority for extremely large files
            } else if (fileInfo.lines > 1000) {
                priority = 4; // High priority for very large files
            }

            // Create task parameters
            const taskParams = {
                title: `Refactoriser ${fileInfo.file} - Réduire la taille du fichier`,
                short_description: `Décomposer le fichier Python ${fileInfo.file} (${fileInfo.lines} lignes) en modules plus petits pour améliorer la maintenabilité.`,
                detailed_description: `Le fichier ${fileInfo.file} contient actuellement ${fileInfo.lines} lignes, ce qui dépasse largement la limite recommandée de 500 lignes.

**Analyse du fichier :**
- Taille actuelle : ${fileInfo.lines} lignes
- Dépassement : ${fileInfo.lines - 500} lignes au-dessus de la limite
- Ratio : ${Math.round((fileInfo.lines / 500) * 100) / 100}x la taille recommandée

**Objectifs de refactoring :**
- Réduire la taille à moins de 500 lignes par module
- Améliorer la lisibilité et la maintenabilité
- Faciliter les tests unitaires
- Réduire la complexité cognitive

**Approches recommandées :**
${fileInfo.lines > 1000 ?
                        `- **Décomposition critique requise** - Ce fichier nécessite une refactorisation majeure
- Extraire les classes principales en modules séparés
- Séparer les fonctions utilitaires en modules dédiés
- Créer des sous-packages si nécessaire` :
                        `- Extraire les fonctions logiquement liées en modules séparés
- Identifier et isoler les responsabilités distinctes
- Créer des interfaces claires entre les modules`}

**Critères d'acceptation :**
- Aucun module ne doit dépasser 500 lignes
- Les fonctionnalités existantes doivent être préservées
- Les tests doivent continuer à passer
- La documentation doit être mise à jour`,
                priority: priority,
                dependencies: [], // No dependencies for refactoring tasks
                status: 'TODO',
                impacted_files: [fileInfo.file],
                validation_criteria: `La tâche est terminée quand :
1. Le fichier ${fileInfo.file} a été décomposé en modules de moins de 500 lignes chacun
2. Toutes les fonctionnalités existantes sont préservées
3. Les tests unitaires passent sans modification
4. La documentation est mise à jour pour refléter la nouvelle structure
5. Les imports et dépendances sont correctement ajustés
6. Le code suit les conventions de style établies`
            };

            // Create the task using the existing MCP API
            const result = await handleCreateTask(taskParams);

            // Parse the result to get task info
            const resultData = JSON.parse(result.content[0].text);

            if (resultData.status === 'success') {
                createdTasks.push({
                    file: fileInfo.file,
                    task_id: resultData.created_task.id,
                    title: resultData.created_task.title,
                    priority: priority,
                    status: 'created'
                });
            } else {
                createdTasks.push({
                    file: fileInfo.file,
                    error: resultData.message,
                    status: 'failed'
                });
            }
        } catch (error) {
            createdTasks.push({
                file: fileInfo.file,
                error: error.message,
                status: 'failed'
            });
        }
    }

    return createdTasks;
}

/**
 * Generates task recommendations for oversized Python files (legacy function for backward compatibility)
 * @param {Array} oversizedFiles - Array of file objects that are oversized
 * @returns {Array} Array of task recommendation objects
 */
function generateTaskRecommendations(oversizedFiles) {
    return oversizedFiles.map(fileInfo => ({
        type: 'refactor_task',
        title: `Refactoriser le fichier Python ${fileInfo.file}`,
        description: `Le fichier ${fileInfo.file} contient ${fileInfo.lines} lignes (limite: 500). Il devrait être décomposé en plusieurs modules plus petits pour améliorer la maintenabilité et la lisibilité du code.`,
        file: fileInfo.file,
        current_lines: fileInfo.lines,
        target_lines: 500,
        priority: fileInfo.lines > 1000 ? 'high' : 'medium',
        suggested_approach: fileInfo.lines > 1000
            ? `Décomposition critique requise - ce fichier est ${Math.round(fileInfo.lines / 500)} fois plus grand que la limite recommandée`
            : `Décomposition recommandée - séparer en modules logiques distincts`
    }));
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
 * Stages all changes, performs a git commit, and scans Python files for size violations.
 * Returns structured information about oversized files and task recommendations.
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

    // --- Scan Python files before commit ---
    let pythonScanResults = [];
    let taskRecommendations = [];
    let createdTasks = [];
    try {
        pythonScanResults = scanPythonFiles(cwd);
        const oversizedFiles = pythonScanResults.filter(file => file.oversized);
        if (oversizedFiles.length > 0) {
            // Generate legacy recommendations for backward compatibility
            taskRecommendations = generateTaskRecommendations(oversizedFiles);

            // Create actual refactoring tasks automatically
            createdTasks = await createRefactoringTasks(oversizedFiles);
        }
    } catch (scanError) {
        console.error('[handleCommit] Error scanning Python files:', scanError.message);
        // Continue with commit even if scan fails
    }

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
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        status: 'success',
                        message: `Nothing to commit in ${repoName}, working tree clean.`,
                        python_scan: {
                            total_files: pythonScanResults.length,
                            oversized_files: pythonScanResults.filter(f => f.oversized).length,
                            files_scanned: pythonScanResults,
                            task_recommendations: taskRecommendations,
                            tasks_created: createdTasks,
                            automatic_task_creation: createdTasks.length > 0
                        }
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
            // Debug logging removed to prevent JSON-RPC pollution
            // console.error('[handleCommit] Error getting diff-tree after successful commit:', diffError);
            committedFilesList = '\n(Could not retrieve list of committed files)';
        }

        // Construct success message, include stderr if it exists (as warning/info)
        let successMessage = `Commit successful in ${repoName}: ${commitTitle}${committedFilesList}`;
        if (commitStderr) {
            successMessage += `\nCommit Warnings/Info (stderr):\n${commitStderr.trim()}`;
        }

        // Add information about automatically created refactoring tasks
        if (createdTasks.length > 0) {
            const successfulTasks = createdTasks.filter(task => task.status === 'created');
            const failedTasks = createdTasks.filter(task => task.status === 'failed');

            successMessage += `\n\n--- Automatic Task Creation ---`;
            successMessage += `\nDetected ${pythonScanResults.filter(f => f.oversized).length} oversized Python file(s) and automatically created refactoring tasks:`;

            if (successfulTasks.length > 0) {
                successMessage += `\n\n✅ Successfully created ${successfulTasks.length} refactoring task(s):`;
                successfulTasks.forEach(task => {
                    successMessage += `\n  • Task #${task.task_id}: ${task.title} (Priority: ${task.priority})`;
                });
            }

            if (failedTasks.length > 0) {
                successMessage += `\n\n❌ Failed to create ${failedTasks.length} task(s):`;
                failedTasks.forEach(task => {
                    successMessage += `\n  • ${task.file}: ${task.error}`;
                });
            }

            successMessage += `\n\nThese tasks are now available in the Streamlit interface for implementation when convenient.`;
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

        // Return structured response with Python scan results
        return {
            content: [{
                type: "text",
                text: JSON.stringify({
                    status: 'success',
                    message: successMessage,
                    python_scan: {
                        total_files: pythonScanResults.length,
                        oversized_files: pythonScanResults.filter(f => f.oversized).length,
                        files_scanned: pythonScanResults,
                        task_recommendations: taskRecommendations,
                        tasks_created: createdTasks,
                        automatic_task_creation: createdTasks.length > 0
                    }
                }, null, 2)
            }]
        };

    } catch (error) {
        // Debug logging removed to prevent JSON-RPC pollution
        // console.error('[handleCommit] Git operation failed:', error);

        // --- If execAsync rejected, commit failed (non-zero exit code) --- 
        // The error object from execAsync usually contains stdout/stderr
        const errorMessage = error.stderr || error.stdout || error.message || 'Unknown error during git operation';
        console.error('[handleCommit] Git operation failed:', error);
        // Check specifically for 'nothing to commit' within the error output as well, just in case
        if (errorMessage.includes('nothing to commit, working tree clean')) {
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        status: 'success',
                        message: `Nothing to commit in ${repoName}, working tree clean.`,
                        python_scan: {
                            total_files: pythonScanResults.length,
                            oversized_files: pythonScanResults.filter(f => f.oversized).length,
                            files_scanned: pythonScanResults,
                            task_recommendations: taskRecommendations,
                            tasks_created: createdTasks,
                            automatic_task_creation: createdTasks.length > 0
                        }
                    }, null, 2)
                }]
            };
        }
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Git operation failed: ${error.message}`,
                    python_scan: {
                        total_files: pythonScanResults.length,
                        oversized_files: pythonScanResults.filter(f => f.oversized).length,
                        files_scanned: pythonScanResults,
                        task_recommendations: taskRecommendations,
                        tasks_created: createdTasks,
                        automatic_task_creation: createdTasks.length > 0
                    }
                }, null, 2)
            }]
        };
    } finally {
        // console.error('[handleCommit] Git operation failed:', error);
    }
} 