import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- State Persistence and Logging Setup --- START ---
const LOGS_DIR = path.join(__dirname, 'logs');
const STATE_FILE = path.join(__dirname, 'terminals_status.json');
let terminalStates = []; // In-memory store for terminal statuses

/**
 * Ensures the logs directory exists.
 */
function ensureLogsDirExists() {
    try {
        if (!fs.existsSync(LOGS_DIR)) {
            fs.mkdirSync(LOGS_DIR, { recursive: true });
            // console.log(`Created logs directory: ${LOGS_DIR}`); // Optional: for debugging
        }
    } catch (error) {
        console.error(`Error creating logs directory ${LOGS_DIR}:`, error);
        // Depending on severity, might want to exit: process.exit(1);
    }
}

/**
 * Reads the terminal state from the JSON file.
 * Initializes with an empty array if the file doesn't exist or is invalid.
 */
function loadTerminalState() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            const fileContent = fs.readFileSync(STATE_FILE, 'utf8');
            terminalStates = JSON.parse(fileContent);
            // Basic validation (check if it's an array)
            if (!Array.isArray(terminalStates)) {
                console.error(`Invalid state file format in ${STATE_FILE}. Expected an array. Resetting state.`);
                terminalStates = [];
            }
            // console.log(`Loaded terminal state from ${STATE_FILE}`); // Optional: for debugging
        } else {
            terminalStates = [];
            // console.log(`State file ${STATE_FILE} not found. Initializing empty state.`); // Optional
        }
    } catch (error) {
        console.error(`Error reading or parsing state file ${STATE_FILE}:`, error);
        terminalStates = []; // Reset state on error
    }
}

/**
 * Writes the current terminal state to the JSON file.
 * @param {Array} state The state array to write.
 */
function writeTerminalState(state) {
    try {
        const fileContent = JSON.stringify(state, null, 2); // Pretty print JSON
        fs.writeFileSync(STATE_FILE, fileContent, 'utf8');
        // console.log(`Wrote terminal state to ${STATE_FILE}`); // Optional: for debugging
    } catch (error) {
        console.error(`Error writing state file ${STATE_FILE}:`, error);
    }
}

// --- State Persistence and Logging Setup --- END ---

// --- Background Status Monitor --- START ---
let statusMonitorInterval = null;

/**
 * Checks the status of running processes and updates the state file.
 * This is a polling mechanism and mainly detects if a process previously marked
 * as 'Running' no longer exists. It doesn't reliably capture exit codes immediately.
 */
async function updateRunningProcessStatuses() {
    // console.log('Running status check...'); // Optional: for debugging
    let stateChanged = false;
    const currentStates = [...terminalStates]; // Work on a copy

    for (const state of currentStates) {
        if (state.status === 'Running') {
            try {
                // process.kill with signal 0 tests if the process exists
                const isRunning = process.kill(state.pid, 0);
                // If kill returns true, the process exists. We don't know if it *just* exited.
                // Polling isn't perfect for immediate exit detection.
            } catch (error) {
                // If error is ESRCH, the process doesn't exist anymore
                if (error.code === 'ESRCH') {
                    // console.log(`Process ${state.pid} (${state.command}) no longer running.`); // Optional
                    state.status = 'Stopped'; // Or potentially 'Failure', but we don't know exit code here
                    state.exit_code = state.exit_code ?? null; // Keep existing exit code if set by 'exit' event, else null
                    state.endTime = state.endTime ?? new Date().toISOString();
                    stateChanged = true;
                } else if (error.code === 'EPERM') {
                    // Process exists, but we lack permissions to send signals.
                    // Should not happen for child processes spawned by us, but log it.
                    console.warn(`Permission error checking status for PID ${state.pid}. Assuming it's still running.`);
                } else {
                    // Other unexpected error
                    console.error(`Error checking status for PID ${state.pid}:`, error);
                }
            }
        }
    }

    if (stateChanged) {
        // console.log('Detected status changes, writing state file.'); // Optional
        writeTerminalState(currentStates);
        terminalStates = currentStates; // Update in-memory state
    }
}
// --- Background Status Monitor --- END ---

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
    name: "InternalAsyncTerminal",
    version: "0.2.0",
    capabilities: {
        tools: {
            'commit': true,
            'execute_command': true,
            'get_terminal_status': true,
            'get_terminal_output': true,
            'stop_terminal_command': true
        }
    }
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

// --- Background Status Monitor --- START (Placeholder)
// TODO: Implement in Task 1.2
// --- Background Status Monitor --- END ---

// --- New MCP Tools --- START ---

/**
 * @typedef {object} ExecuteCommandResult
 * @property {number} pid - The process ID of the spawned command.
 * @property {string} stdout - The stdout captured during the initial wait period.
 * @property {string} stderr - The stderr captured during the initial wait period.
 * @property {number | null} exit_code - The exit code if the command completed within the timeout, otherwise null.
 */

server.tool(
    'execute_command',
    {
        command: z.string().describe("The command line to execute."),
        reuse_terminal: z.boolean().optional().default(true).describe("If true (default), attempts to clean up one finished terminal state before spawning a new process. Otherwise, always spawns without cleanup."),
        timeout: z.number().int().optional().default(15).describe("Maximum time in seconds to wait for the command to complete before returning. The command continues in the background if timeout is reached.")
    },
    /**
     * Executes a command asynchronously in a detached process.
     * @param {object} params
     * @param {string} params.command
     * @param {boolean} params.reuse_terminal
     * @param {number} params.timeout
     * @returns {Promise<ExecuteCommandResult>}
     */
    async ({ command, reuse_terminal, timeout }) => {
        // <<< DEBUG LOGGING START >>>
        // console.log(`[MyMCP DEBUG] execute_command handler START - Command: ${command}, Timeout: ${timeout}, Reuse: ${reuse_terminal}`);
        // <<< DEBUG LOGGING END >>>

        // --- Terminal Reuse Logic --- START ---
        if (reuse_terminal) {
            const reusableTerminalIndex = terminalStates.findIndex(state =>
                ['Success', 'Failure', 'Stopped'].includes(state.status)
            );

            if (reusableTerminalIndex !== -1) {
                const stateToClean = terminalStates[reusableTerminalIndex];
                // console.log(`[MyMCP DEBUG] Reusing terminal slot from PID ${stateToClean.pid} (Status: ${stateToClean.status})`);

                // Remove from state array first
                terminalStates.splice(reusableTerminalIndex, 1);
                writeTerminalState(terminalStates);

                // Delete log files (best effort)
                try {
                    if (fs.existsSync(stateToClean.stdout_log)) {
                        fs.unlinkSync(stateToClean.stdout_log);
                    }
                } catch (unlinkErr) {
                    console.warn(`[MyMCP DEBUG] Could not delete reused stdout log ${stateToClean.stdout_log}:`, unlinkErr);
                }
                try {
                    if (fs.existsSync(stateToClean.stderr_log)) {
                        fs.unlinkSync(stateToClean.stderr_log);
                    }
                } catch (unlinkErr) {
                    console.warn(`[MyMCP DEBUG] Could not delete reused stderr log ${stateToClean.stderr_log}:`, unlinkErr);
                }
            }
        }
        // --- Terminal Reuse Logic --- END ---

        // Note: reuse_terminal logic *description* needs update (it's being implemented now).
        let child;
        let pid;
        let stdoutLogPath;
        let stderrLogPath;
        let stdoutStream;
        let stderrStream;
        let stateEntryIndex = -1;
        let initialStdout = '';
        let initialStderr = '';

        const startTime = new Date().toISOString();

        // Temporary listeners for initial output capture
        const stdoutListener = (data) => { initialStdout += data.toString(); };
        const stderrListener = (data) => { initialStderr += data.toString(); };

        try {
            // Spawn the process
            // Use shell: true to handle complex commands more easily, like pipelines or env vars
            child = spawn(command, [], {
                shell: true,
                detached: true, // Allows parent to exit independently
                stdio: ['ignore', 'pipe', 'pipe'], // Ignore stdin, pipe stdout/stderr
                cwd: projectRoot // Execute in project root by default
            });

            pid = child.pid;
            if (pid === undefined) {
                throw new Error('Failed to get PID for spawned process.');
            }

            // Create log file streams
            stdoutLogPath = path.join(LOGS_DIR, `${pid}.stdout.log`);
            stderrLogPath = path.join(LOGS_DIR, `${pid}.stderr.log`);
            stdoutStream = fs.createWriteStream(stdoutLogPath, { flags: 'a' });
            stderrStream = fs.createWriteStream(stderrLogPath, { flags: 'a' });

            // Pipe output to log files
            child.stdout.pipe(stdoutStream);
            child.stderr.pipe(stderrStream);

            // Attach temporary listeners for initial output
            child.stdout.on('data', stdoutListener);
            child.stderr.on('data', stderrListener);

            // Add entry to state
            const newStateEntry = {
                pid,
                command,
                status: 'Running',
                exit_code: null,
                stdout_log: stdoutLogPath,
                stderr_log: stderrLogPath,
                startTime,
                endTime: null
            };
            terminalStates.push(newStateEntry);
            stateEntryIndex = terminalStates.length - 1; // Keep track of the index
            writeTerminalState(terminalStates);

            // console.log(`Spawned process ${pid} for command: ${command}`); // Optional debug

            let exitCode = null;
            let processExited = false;

            // Promise that resolves when the process exits
            const exitPromise = new Promise((resolve) => {
                child.on('exit', (code, signal) => {
                    // console.log(`Process ${pid} exited with code: ${code}, signal: ${signal}`); // Optional debug
                    processExited = true;
                    exitCode = code ?? (signal ? 1 : 0); // Simplistic: non-null code or signal implies non-zero exit
                    const endTime = new Date().toISOString();

                    // Update state
                    if (stateEntryIndex !== -1) {
                        terminalStates[stateEntryIndex].status = (exitCode === 0) ? 'Success' : 'Failure';
                        terminalStates[stateEntryIndex].exit_code = exitCode;
                        terminalStates[stateEntryIndex].endTime = endTime;
                        writeTerminalState(terminalStates);
                    }

                    // Clean up streams and listeners
                    child.stdout?.removeListener('data', stdoutListener);
                    child.stderr?.removeListener('data', stderrListener);
                    stdoutStream.end();
                    stderrStream.end();

                    resolve('exited');
                });

                // Handle spawn errors (e.g., command not found)
                child.on('error', (err) => {
                    console.error(`Error spawning process ${pid} (${command}):`, err);
                    processExited = true; // Treat spawn error as an exit
                    exitCode = 1; // Indicate failure
                    const endTime = new Date().toISOString();

                    // Update state
                    if (stateEntryIndex !== -1) {
                        terminalStates[stateEntryIndex].status = 'Failure';
                        terminalStates[stateEntryIndex].exit_code = exitCode;
                        terminalStates[stateEntryIndex].endTime = endTime;
                        // Attempt to add error message to stderr log if possible
                        try {
                            fs.appendFileSync(stderrLogPath, `\n[MCP Server Spawn Error]: ${err.message}\n`);
                        } catch (logErr) { /* Ignore logging error */ }
                        writeTerminalState(terminalStates);
                    }

                    // Clean up streams and listeners
                    child.stdout?.removeListener('data', stdoutListener);
                    child.stderr?.removeListener('data', stderrListener);
                    try { stdoutStream.end(); } catch { /* ignore */ }
                    try { stderrStream.end(); } catch { /* ignore */ }

                    // Resolve the exit promise to prevent timeout waiting indefinitely
                    // but pass the error to the outer catch block
                    resolve(new Error(`Spawn failed: ${err.message}`));
                });
            });

            // Promise that resolves on timeout
            const timeoutPromise = new Promise((resolve) => {
                setTimeout(() => resolve('timeout'), timeout * 1000);
            });

            // Wait for exit or timeout
            const result = await Promise.race([exitPromise, timeoutPromise]);

            if (result instanceof Error) {
                throw result; // Rethrow spawn error
            }

            // If timeout occurred, clean up initial listeners and unref
            if (result === 'timeout') {
                // console.log(`Process ${pid} timed out after ${timeout}s.`); // Optional debug
                child.stdout?.removeListener('data', stdoutListener);
                child.stderr?.removeListener('data', stderrListener);
                child.unref(); // Allow parent to exit if this was the only ref
            }

            // <<< DEBUG LOGGING START >>>
            const response = {
                pid,
                stdout: initialStdout,
                stderr: initialStderr,
                exit_code: (result === 'timeout' || processExited === false) ? null : exitCode // Return null if timed out or not exited yet
            };
            // console.log(`[MyMCP DEBUG] execute_command handler RETURNING - Response: ${JSON.stringify(response)}`);
            // Wrap the response in the format expected by the calling tool
            // return { content: [{ type: "json", json: response }] }; // Try type: "json"
            // return response; // Return raw JSON object
            return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Use text type like commit
            // <<< DEBUG LOGGING END >>>

        } catch (error) {
            // <<< DEBUG LOGGING START >>>
            // console.error('[MyMCP DEBUG] execute_command handler ERROR:', error);
            // <<< DEBUG LOGGING END >>>
            console.error('[mcp_execute_command] Error:', error);
            // Ensure state is marked as failed if an error occurred after state entry was added
            if (pid && stateEntryIndex !== -1 && terminalStates[stateEntryIndex]?.status === 'Running') {
                terminalStates[stateEntryIndex].status = 'Failure';
                terminalStates[stateEntryIndex].exit_code = 1; // Generic failure code
                terminalStates[stateEntryIndex].endTime = new Date().toISOString();
                writeTerminalState(terminalStates);
            }
            // Clean up listeners and streams on error
            child?.stdout?.removeListener('data', stdoutListener);
            child?.stderr?.removeListener('data', stderrListener);
            try { stdoutStream?.end(); } catch { /* ignore */ }
            try { stderrStream?.end(); } catch { /* ignore */ }

            throw new Error(`Failed to execute command: ${error.message}`);
        }
    }
);

/**
 * Reads the last N lines of a file.
 * @param {string} filePath Path to the file.
 * @param {number} lineCount Maximum number of lines to read.
 * @returns {string} Last N lines or empty string if file not found/error.
 */
function readLastLogLines(filePath, lineCount) {
    try {
        if (!fs.existsSync(filePath)) {
            return '';
        }
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split(/\r?\n/).filter(line => line.length > 0);
        const lastLines = lines.slice(-lineCount);
        return lastLines.join('\n');
    } catch (error) {
        // Log error but return empty string for robustness
        console.error(`Error reading log file ${filePath}:`, error);
        return '';
    }
}

/**
 * @typedef {object} TerminalStatus
 * @property {number} pid - The process ID.
 * @property {string} status - The current status ('Running', 'Success', 'Failure', 'Stopped', 'Terminated').
 * @property {number | null} exit_code - The exit code if completed.
 * @property {string} last_output - The last ~10 lines combined from stdout/stderr logs.
 */

/**
 * @typedef {object} GetTerminalStatusResult
 * @property {boolean} status_changed - True if the status of a running process changed during the wait period.
 * @property {Array<TerminalStatus>} terminals - List of all tracked terminals.
 */

server.tool(
    'get_terminal_status',
    {
        timeout: z.number().int().optional().default(0).describe("Maximum time in seconds to wait for any running process status to change before returning. 0 means return immediately.")
    },
    /**
     * Retrieves the status of all tracked terminal processes.
     * @param {object} params
     * @param {number} params.timeout
     * @returns {Promise<GetTerminalStatusResult>}
     */
    async ({ timeout }) => {
        // <<< DEBUG LOGGING START >>>
        // console.log(`[MyMCP DEBUG] get_terminal_status handler START - Timeout: ${timeout}`);
        // <<< DEBUG LOGGING END >>>

        let status_changed = false;
        const startTime = Date.now();

        // Store initial statuses of running processes if waiting
        const initialRunningStatuses = new Map();
        if (timeout > 0) {
            terminalStates.forEach(state => {
                if (state.status === 'Running') {
                    initialRunningStatuses.set(state.pid, state.status);
                }
            });
            // Trigger an immediate update check
            await updateRunningProcessStatuses();
        }

        // Polling loop if timeout is specified
        while (timeout > 0 && (Date.now() - startTime) < (timeout * 1000)) {
            let changed = false;
            for (const state of terminalStates) {
                if (initialRunningStatuses.has(state.pid) && state.status !== 'Running') {
                    changed = true;
                    break;
                }
            }

            if (changed) {
                status_changed = true;
                break; // Exit loop as soon as a change is detected
            }

            // Wait a short interval before checking again
            await new Promise(resolve => setTimeout(resolve, 200)); // Poll every 200ms
        }

        // Format the final output
        const terminals = terminalStates.map(state => {
            const lastStdout = readLastLogLines(state.stdout_log, 10);
            const lastStderr = readLastLogLines(state.stderr_log, 10);
            // Simple combination, could be interleaved by timestamp if needed
            const last_output = `--- STDOUT ---\n${lastStdout}\n--- STDERR ---\n${lastStderr}`;

            return {
                pid: state.pid,
                status: state.status,
                exit_code: state.exit_code,
                last_output: last_output.trim()
            };
        });

        // <<< DEBUG LOGGING START >>>
        const response = { status_changed, terminals };
        // console.log(`[MyMCP DEBUG] get_terminal_status handler RETURNING - Response: ${JSON.stringify(response)}`);
        // return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Correct format
        // return { content: [{ type: "json", json: response }] }; // Try type: "json"
        return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Use text type like commit
        // <<< DEBUG LOGGING END >>>
    }
);

/**
 * @typedef {object} GetTerminalOutputResult
 * @property {string} stdout - The last N lines of stdout log.
 * @property {string} stderr - The last N lines of stderr log.
 */

server.tool(
    'get_terminal_output',
    {
        pid: z.number().int().describe("The PID of the terminal process to get output from."),
        lines: z.number().int().optional().default(100).describe("The maximum number of lines to retrieve from the end of each log (stdout, stderr).")
    },
    /**
     * Retrieves the last N lines of output logs for a specific terminal process.
     * @param {object} params
     * @param {number} params.pid
     * @param {number} params.lines
     * @returns {Promise<GetTerminalOutputResult>}
     */
    async ({ pid, lines }) => {
        const state = terminalStates.find(s => s.pid === pid);

        if (!state) {
            throw new Error(`Terminal process with PID ${pid} not found.`);
        }

        const stdoutContent = readLastLogLines(state.stdout_log, lines);
        const stderrContent = readLastLogLines(state.stderr_log, lines);

        // Format expected by the tool
        const response = {
            stdout: stdoutContent,
            stderr: stderrContent
        };
        // return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Incorrect format
        // --- TEMPORARY DEBUG --- 
        // return { content: [{ type: "text", text: `Stdout length: ${stdoutContent.length}` }] };
        // return { content: [{ type: "json", json: response }] }; // Try type: "json"
        // return response; // Return raw JSON object
        return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Use text type like commit
    }
);

/**
 * @typedef {object} StopTerminalCommandResult
 * @property {string} status - Message indicating the outcome of the stop and cleanup attempt.
 * @property {string} stdout - The last N lines of stdout log before termination attempt.
 * @property {string} stderr - The last N lines of stderr log before termination attempt.
 */

server.tool(
    'stop_terminal_command',
    {
        pid: z.number().int().describe("The PID of the terminal process to stop."),
        lines: z.number().int().optional().default(100).describe("The maximum number of lines to retrieve from the end of each log before stopping.")
    },
    /**
    * Attempts to stop a terminal process and cleans up its state and logs.
    * @param {object} params
    * @param {number} params.pid
    * @param {number} params.lines
    * @returns {Promise<StopTerminalCommandResult>}
    */
    async ({ pid, lines }) => {
        const stateIndex = terminalStates.findIndex(s => s.pid === pid);

        if (stateIndex === -1) {
            throw new Error(`Terminal process with PID ${pid} not found in state.`);
        }

        const state = terminalStates[stateIndex];

        // 1. Read final logs before attempting kill
        const finalStdout = readLastLogLines(state.stdout_log, lines);
        const finalStderr = readLastLogLines(state.stderr_log, lines);

        let terminationStatus = 'Termination signal sent.';
        let killError = null;

        // 2. Attempt termination (SIGTERM first, then SIGKILL)
        try {
            // console.log(`Attempting SIGTERM for PID ${pid}`); // Optional debug
            process.kill(pid, 'SIGTERM');
            // Wait briefly to see if SIGTERM worked before potentially sending SIGKILL
            await new Promise(resolve => setTimeout(resolve, 200));
            // Check if it's still running
            try {
                process.kill(pid, 0);
                // Still running, try SIGKILL
                try {
                    // console.log(`Process ${pid} still running, attempting SIGKILL`); // Optional debug
                    process.kill(pid, 'SIGKILL');
                    terminationStatus = 'SIGTERM sent, followed by SIGKILL.';
                } catch (sigkillError) {
                    if (sigkillError.code === 'ESRCH') {
                        terminationStatus = 'Process likely terminated after SIGTERM.';
                    } else {
                        throw sigkillError; // Re-throw unexpected SIGKILL error
                    }
                }
            } catch (checkError) {
                if (checkError.code === 'ESRCH') {
                    terminationStatus = 'Process already exited before/after SIGTERM.';
                } else {
                    throw checkError; // Re-throw unexpected check error
                }
            }
        } catch (error) {
            if (error.code === 'ESRCH') {
                terminationStatus = 'Process already exited before termination attempt.';
            } else {
                console.error(`Error sending termination signal to PID ${pid}:`, error);
                terminationStatus = `Error during termination: ${error.message}`;
                killError = error; // Store error to potentially indicate cleanup issues
            }
        }

        // 3. Cleanup state and logs regardless of kill outcome
        let cleanupStatus = 'Cleanup initiated.';
        try {
            // Remove from state array
            terminalStates.splice(stateIndex, 1);
            writeTerminalState(terminalStates);

            // Delete log files
            try {
                if (fs.existsSync(state.stdout_log)) fs.unlinkSync(state.stdout_log);
            } catch (unlinkErr) {
                console.warn(`Could not delete stdout log ${state.stdout_log}:`, unlinkErr);
                cleanupStatus += ' (stdout log deletion failed)';
            }
            try {
                if (fs.existsSync(state.stderr_log)) fs.unlinkSync(state.stderr_log);
            } catch (unlinkErr) {
                console.warn(`Could not delete stderr log ${state.stderr_log}:`, unlinkErr);
                cleanupStatus += ' (stderr log deletion failed)';
            }
            cleanupStatus = 'Cleanup successful.'; // Assume success if no errors thrown
        } catch (cleanupError) {
            console.error(`Error during cleanup for PID ${pid}:`, cleanupError);
            cleanupStatus = `Cleanup failed: ${cleanupError.message}`;
        }

        // Format expected by the tool
        const response = {
            status: `${terminationStatus} ${cleanupStatus}`,
            stdout: finalStdout,
            stderr: finalStderr
        };
        // return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Correct format
        // return { content: [{ type: "json", json: response }] }; // Try type: "json"
        // return response; // Return raw JSON object
        return { content: [{ type: "text", text: JSON.stringify(response) }] }; // Use text type like commit
    }
);

// --- New MCP Tools --- END ---

// Create the transport and connect the server
async function startServer() {
    ensureLogsDirExists(); // Ensure logs directory exists before starting
    loadTerminalState();   // Load initial state from file

    // Start the background status monitor
    if (statusMonitorInterval) {
        clearInterval(statusMonitorInterval); // Clear existing interval if any
    }
    statusMonitorInterval = setInterval(updateRunningProcessStatuses, 1000); // Check every 1 second

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