import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';
import crypto from 'crypto';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- State Persistence and Logging Setup --- START ---
const LOGS_DIR = path.join(__dirname, 'logs');
const STATE_FILE = path.join(__dirname, 'terminals_status.json');
let terminalStates = []; // In-memory store for terminal statuses
const activeProcesses = new Map(); // In-memory map to store active child_process objects {pid: child}

/**
 * Ensures the logs directory exists.
 */
function ensureLogsDirExists() {
    try {
        if (!fs.existsSync(LOGS_DIR)) {
            fs.mkdirSync(LOGS_DIR, { recursive: true });
            // console.error(`Created logs directory: ${LOGS_DIR}`); // Optional: for debugging
        }
    } catch (error) {
        console.error(`Error creating/accessing logs directory ${LOGS_DIR}:`, error);
        // Rethrow or handle critical error? For now, log and continue.
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
            // console.error(`Loaded terminal state from ${STATE_FILE}`); // Optional: for debugging
        } else {
            terminalStates = [];
            // console.error(`State file ${STATE_FILE} not found. Initializing empty state.`); // Optional
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
        // console.error(`Wrote terminal state to ${STATE_FILE}`); // Optional: for debugging
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
    // console.error('Running status check...'); // Optional: for debugging
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
                    // console.error(`Process ${state.pid} (${state.command}) no longer running.`); // Optional
                    state.status = 'Stopped'; // Or potentially 'Failure', but we don't know exit code here
                    state.exit_code = state.exit_code ?? null; // Keep existing exit code if set by 'exit' event, else null
                    state.endTime = state.endTime ?? new Date().toISOString();
                    stateChanged = true;
                } else if (error.code === 'EPERM') {
                    // Process exists, but we lack permissions to send signals.
                    // Should not happen for child processes spawned by us, but log it.
                    console.error(`Permission error checking status for PID ${state.pid}. Assuming it's still running.`); // Changed log to error
                } else {
                    // Other unexpected error
                    console.error(`Error checking status for PID ${state.pid}:`, error);
                }
            }
        }
    }

    if (stateChanged) {
        // console.error('Detected status changes, writing state file.'); // Optional
        writeTerminalState(currentStates);
        terminalStates = currentStates; // Update in-memory state
    }
}
// --- Background Status Monitor --- END ---

// --- Internal Helper Functions --- START ---

/**
 * Internal helper to clean up state for a given PID.
 * Removes from activeProcesses, terminalStates, and deletes logs.
 * Does NOT write the state file; caller should do that.
 * @param {number} pid The PID to clean up.
 * @returns {Promise<boolean>} True if cleanup was attempted (state found), false otherwise.
 */
async function _cleanupTerminalState(pid) {
    // console.error(`[MyMCP DEBUG] _cleanupTerminalState called for PID: ${pid}`); // Optional debug
    const stateIndex = terminalStates.findIndex(s => s.pid === pid);
    if (stateIndex === -1) {
        console.error(`[MyMCP ERROR] _cleanupTerminalState: PID ${pid} not found in terminalStates.`);
        activeProcesses.delete(pid); // Attempt removal from map anyway
        return false; // State not found
    }

    const state = terminalStates[stateIndex];
    let deleteFailed = false;

    // 1. Remove from active processes map
    activeProcesses.delete(pid);
    // console.error(`[MyMCP DEBUG] _cleanupTerminalState: Removed PID ${pid} from activeProcesses map.`); // Optional debug

    // 2. Remove from state array
    terminalStates.splice(stateIndex, 1);

    // 3. Delete log file (best effort)
    try {
        if (state.logFile && fs.existsSync(state.logFile)) {
            fs.unlinkSync(state.logFile);
            // console.error(`[MyMCP DEBUG] _cleanupTerminalState: Deleted log file ${state.logFile}`); // Optional debug
        } else if (state.logFile) {
            // console.error(`[MyMCP DEBUG] _cleanupTerminalState: Log file ${state.logFile} not found for deletion.`); // Optional debug
        }
    } catch (unlinkErr) {
        console.error(`[MyMCP ERROR] _cleanupTerminalState: Could not delete log file ${state.logFile} for PID ${pid}:`, unlinkErr);
        deleteFailed = true;
    }

    // console.error(`[MyMCP DEBUG] _cleanupTerminalState completed for PID: ${pid}. Log delete failed: ${deleteFailed}`); // Optional debug
    return true; // Indicate cleanup was performed
}

// --- Internal Helper Functions --- END ---

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
    version: "0.2.1",
    capabilities: {
        tools: {
            'commit': true,
            'execute_command': true,
            'get_terminal_status': true,
            'get_terminal_output': true,
            'stop_terminal_command': true,
            'send_terminal_input': true
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
        // console.error(`[MyMCP DEBUG] execute_command handler START - Command: ${command}, Timeout: ${timeout}, Reuse: ${reuse_terminal}`);
        // <<< DEBUG LOGGING END >>>

        // Task 1.1: Implement reuse_terminal logic - Cleanup ONE finished process
        if (reuse_terminal) {
            try {
                const stateToRemove = terminalStates.find(s => s.status === 'Success' || s.status === 'Failure' || s.status === 'Stopped');
                if (stateToRemove) {
                    console.error(`[MyMCP DEBUG] Reusing terminal: Found finished process PID ${stateToRemove.pid} to clean up.`); // Optional debug log
                    const cleanupSuccess = await _cleanupTerminalState(stateToRemove.pid);
                    if (cleanupSuccess) {
                        writeTerminalState(terminalStates); // Write state after successful cleanup
                        console.error(`[MyMCP DEBUG] Reusing terminal: State for PID ${stateToRemove.pid} cleaned up and state written.`); // Optional debug log
                    } else {
                        console.error(`[MyMCP DEBUG] Reusing terminal: _cleanupTerminalState reported failure for PID ${stateToRemove.pid}.`); // Optional debug log
                    }
                } else {
                    // console.error('[MyMCP DEBUG] Reusing terminal: No finished process found to clean up.'); // Optional debug log
                }
            } catch (cleanupError) {
                console.error('[MyMCP ERROR] Error during reuse_terminal cleanup call:', cleanupError);
                // Don't prevent execution, just log the cleanup error
            }
        }
        // Task 1.1: End

        const commandId = crypto.randomUUID(); // Use crypto.randomUUID()
        const logFileName = `cmd_${commandId}_pid_${process.pid}.log`; // Include server PID for potential multi-server scenarios
        const logFilePath = path.join(LOGS_DIR, logFileName);
        let childPid = null;
        let initialStdout = '';
        let initialStderr = '';
        let exitCode = null;
        let processError = null;
        let signal = null;
        let commandStartTime = new Date().toISOString();
        let commandEndTime = null;

        // Create write stream for logging
        const logStream = fs.createWriteStream(logFilePath, { flags: 'a' });
        logStream.write(`--- Log Start: ${commandStartTime} ---\n`);
        logStream.write(`Command: ${command}\n`);
        logStream.write(`Timeout Setting: ${timeout}s\n`);

        // Timeout promise
        let timeoutId = null;
        const timeoutPromise = new Promise((_, reject) => {
            timeoutId = setTimeout(() => {
                // console.error(`[MyMCP DEBUG] Command PID ${childPid}: Timeout (${timeout}s) reached.`); // Optional debug
                reject(new Error(`Timeout reached after ${timeout} seconds`)); // Indicate timeout specifically
            }, timeout * 1000);
        });

        // Process execution promise
        const processPromise = new Promise((resolve, reject) => {
            try {
                // Spawn the process
                // Use shell: true for convenience (handles path, complex commands), but be mindful of security.
                // Consider shell: false and parsing command/args for more control if needed.
                // Use 'detached: true' so child can outlive parent if needed (though we manage lifetime)
                const child = spawn(command, [], {
                    shell: true,
                    detached: true,
                    stdio: ['pipe', 'pipe', 'pipe'], // Ensure we pipe stdio
                    cwd: projectRoot // Set CWD to project root
                });
                childPid = child.pid;

                // --- Process State Tracking --- START ---
                const newState = {
                    pid: childPid,
                    command: command,
                    status: 'Running', // Initial status
                    startTime: commandStartTime,
                    endTime: null,
                    exit_code: null,
                    signal: null,
                    logFile: logFilePath // Store log file path
                };
                terminalStates.push(newState);
                writeTerminalState(terminalStates); // Persist state immediately
                // <<< INTEGRATION: Store active child process object >>>
                activeProcesses.set(childPid, child);
                // console.error(`[MyMCP DEBUG] Added PID ${childPid} to activeProcesses map.`); // Optional debug
                // <<< END INTEGRATION >>>
                // --- Process State Tracking --- END ---

                // Log PID immediately
                logStream.write(`PID: ${childPid}\n`);
                logStream.write(`--- Output Start ---\n`);

                // Handlers for stdout/stderr data
                const stdoutListener = (data) => {
                    const dataStr = data.toString();
                    initialStdout += dataStr;
                    logStream.write(dataStr); // Log incrementally
                };
                const stderrListener = (data) => {
                    const dataStr = data.toString();
                    initialStderr += dataStr;
                    logStream.write(`[STDERR] ${dataStr}`); // Log incrementally, marked
                };

                child.stdout.on('data', stdoutListener);
                child.stderr.on('data', stderrListener);

                // Handlers for process exit and error
                child.on('exit', (code, sig) => {
                    commandEndTime = new Date().toISOString();
                    // console.error(`[MyMCP DEBUG] Process PID ${childPid} exited. Code: ${code}, Signal: ${sig}`); // Optional debug
                    exitCode = code;
                    signal = sig;
                    clearTimeout(timeoutId); // Clear timeout if process finishes first

                    // --- Process State Update (Exit) --- START ---
                    const stateIndex = terminalStates.findIndex(s => s.pid === childPid);
                    if (stateIndex !== -1) {
                        terminalStates[stateIndex].status = (code === 0) ? 'Success' : 'Failure';
                        terminalStates[stateIndex].endTime = commandEndTime;
                        terminalStates[stateIndex].exit_code = exitCode;
                        terminalStates[stateIndex].signal = signal;
                        writeTerminalState(terminalStates); // Update state file
                    } else {
                        console.error(`[MyMCP ERROR] Could not find state for exited PID ${childPid} to update.`);
                    }
                    // <<< INTEGRATION: Remove from active map on exit >>>
                    activeProcesses.delete(childPid);
                    // console.error(`[MyMCP DEBUG] Removed PID ${childPid} from activeProcesses map on exit.`); // Optional debug
                    // <<< END INTEGRATION >>>
                    // --- Process State Update (Exit) --- END ---

                    // Final log entry
                    logStream.write(`\n--- Output End ---\n`);
                    logStream.write(`Exit Code: ${exitCode}, Signal: ${signal}, End Time: ${commandEndTime}\n`);
                    logStream.end(() => resolve({ initialStdout, initialStderr, exitCode })); // Resolve after log stream finishes
                });

                child.on('error', (err) => {
                    commandEndTime = new Date().toISOString();
                    console.error(`[MyMCP ERROR] Failed to start or spawn process PID ${childPid}:`, err); // Log the detailed error
                    processError = err;
                    clearTimeout(timeoutId);

                    // --- Process State Update (Error) --- START ---
                    const stateIndex = terminalStates.findIndex(s => s.pid === childPid);
                    if (stateIndex !== -1) {
                        terminalStates[stateIndex].status = 'Failure';
                        terminalStates[stateIndex].endTime = commandEndTime;
                        terminalStates[stateIndex].exit_code = null; // No exit code in this case
                        terminalStates[stateIndex].signal = null;
                        // Add error message? Maybe not directly in state.
                        writeTerminalState(terminalStates); // Update state file
                    } else {
                        // This might happen if error occurs before state is added?
                        console.error(`[MyMCP ERROR] Could not find state for errored PID ${childPid} to update.`);
                    }
                    // <<< INTEGRATION: Remove from active map on error >>>
                    activeProcesses.delete(childPid);
                    // console.error(`[MyMCP DEBUG] Removed PID ${childPid} from activeProcesses map on error.`); // Optional debug
                    // <<< END INTEGRATION >>>
                    // --- Process State Update (Error) --- END ---

                    // Log error and reject
                    logStream.write(`\n--- ERROR: ${err.message} ---\nEnd Time: ${commandEndTime}\n`);
                    logStream.end(() => reject(err)); // Reject after log stream finishes
                });

            } catch (spawnError) {
                // Catch synchronous errors during spawn itself
                commandEndTime = new Date().toISOString();
                console.error('[MyMCP ERROR] Synchronous spawn error:', spawnError);
                processError = spawnError;
                clearTimeout(timeoutId); // Ensure timeout is cleared
                logStream.write(`\n--- SPAWN ERROR: ${spawnError.message} ---\nEnd Time: ${commandEndTime}\n`);
                logStream.end(() => reject(spawnError)); // Reject after log stream finishes
            }
        });

        try {
            // Wait for either the process to finish or the timeout
            const result = await Promise.race([processPromise, timeoutPromise]);

            // Process finished within timeout
            // console.error(`[MyMCP DEBUG] Process PID ${childPid} finished within timeout. Exit code: ${result.exitCode}`); // Optional debug
            return {
                content: [{
                    type: "text",
                    text: JSON.stringify({
                        pid: childPid,
                        stdout: result.initialStdout,
                        stderr: result.initialStderr,
                        exit_code: result.exitCode // Will be null if timeout occurred but process finished *during* timeout handling
                    })
                }]
            };

        } catch (error) {
            // This block catches errors from processPromise (spawn/runtime errors) OR timeoutPromise
            if (error.message.startsWith('Timeout reached')) {
                // Timeout occurred, process is still running in the background
                // console.error(`[MyMCP DEBUG] Process PID ${childPid} timed out. Returning PID and initial output.`); // Optional debug
                return {
                    content: [{
                        type: "text",
                        text: JSON.stringify({
                            pid: childPid,
                            stdout: initialStdout, // Return whatever was captured so far
                            stderr: initialStderr,
                            exit_code: null // Indicate timeout by null exit code
                        })
                    }]
                };
            } else {
                // Process failed (spawn error or runtime error)
                console.error(`[MyMCP ERROR] Process PID ${childPid || 'unknown'} failed:`, error);
                throw new Error(`Command execution failed for PID ${childPid || 'unknown'}: ${error.message}`);
            }
        } finally {
            // Clean up listeners? Node.js usually handles this on process end, but explicit removal can be safer.
            // However, removing listeners before the 'exit' or 'error' event fires can cause missed events.
            // Let Node.js handle cleanup for now unless issues arise.
            // Ensure log stream is closed if it hasn't been already (e.g., if timeout occurred before exit/error)
            if (!logStream.destroyed) {
                logStream.end();
            }
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
        if (!filePath) {
            // console.warn('readLastLogLines called with null or undefined filePath.');
            return ''; // Return empty string if no log path is provided
        }
        if (!fs.existsSync(filePath)) {
            return '';
        }
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split(/\r?\n/).filter(line => line.length > 0);
        const lastLines = lines.slice(-lineCount);
        return lastLines.join('\n');
    } catch (error) {
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
        // console.error(`[MyMCP DEBUG] get_terminal_status handler START - Timeout: ${timeout}`);
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

        // Format the final output (Read from single logFile)
        const terminals = terminalStates.map(state => {
            const last_output = readLastLogLines(state.logFile, 10); // Use logFile
            return {
                pid: state.pid,
                status: state.status,
                exit_code: state.exit_code,
                last_output: last_output.trim()
            };
        });
        const response = { status_changed, terminals };
        return { content: [{ type: "text", text: JSON.stringify(response) }] };
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
        // Read from single log file, try to split conceptually?
        // For simplicity, return the whole log content as 'stdout'.
        const logContent = readLastLogLines(state.logFile, lines); // Use logFile
        const response = {
            stdout: logContent,
            stderr: "(Combined in stdout)" // Indicate stderr is mixed in
        };
        return { content: [{ type: "text", text: JSON.stringify(response) }] };
    }
);

/**
 * @typedef {object} StopTerminalCommandResult
 * @property {number} pid - The PID this result corresponds to.
 * @property {string} status - Message indicating the outcome of the stop and cleanup attempt for this PID.
 * @property {string} stdout - The last N lines of stdout log before termination attempt.
 * @property {string} stderr - The last N lines of stderr log before termination attempt.
 */

// Add try-catch around the tool definition
try {
    server.tool(
        'stop_terminal_command',
        {
            pids: z.array(z.number().int()).describe("An array of PIDs of the terminal processes to stop."),
            lines: z.number().int().optional().describe("The maximum number of lines to retrieve from the end of each log before stopping.")
        },
        /**
        * Attempts to stop multiple terminal processes and cleans up their state and logs.
        * @param {object} params
        * @param {number[]} params.pids - Array of PIDs to stop.
        * @param {number} params.lines
        * @returns {Promise<{ content: Array<{ type: string, text: string }> }>} - Returns an object containing a 'content' array where each element wraps a JSON string result for one PID.
        */
        async ({ pids, lines }) => {
            // console.error(`[MyMCP DEBUG] stop_terminal_command handler START - PIDs: ${pids.join(', ')}`); // Optional debug
            const results = [];
            const pidsToCleanup = []; // Store PIDs that need state cleanup
            let stateChanged = false;

            for (const pid of pids) {
                // --- Stage 1: Attempt Termination & Log Retrieval (Mostly unchanged) ---
                const state = terminalStates.find(s => s.pid === pid);
                if (!state) {
                    results.push({ pid, status: 'PID not found in managed state.', stdout: '', stderr: '' });
                    continue;
                }
                if (state.status !== 'Running') {
                    results.push({ pid, status: `Process not running (Status: ${state.status}). Cleanup will be attempted.`, stdout: '', stderr: '' });
                    pidsToCleanup.push(pid); // Mark for cleanup even if not running
                    continue;
                }

                let finalStdout = '';
                let finalStderr = '';
                let terminationStatus = 'Termination initiated.';
                // let cleanupStatus = '(Cleanup pending)'; // // Removed - Cleanup happens after loop

                // Fetch last lines before terminating
                try {
                    const lineCount = lines ?? 50;
                    if (state.logFile && fs.existsSync(state.logFile)) {
                        const logResult = await readLastLogLines(state.logFile, lineCount);
                        finalStdout = logResult.stdout;
                        finalStderr = logResult.stderr;
                    } else {
                        finalStdout = '(Log file missing or not specified)';
                        finalStderr = '';
                    }
                } catch (readErr) {
                    console.error(`Error reading final log lines for PID ${pid} before termination:`, readErr);
                    finalStdout = finalStdout || `(Error reading stdout: ${readErr.message})`;
                    finalStderr = finalStderr || `(Error reading stderr: ${readErr.message})`;
                }

                // Attempt termination (SIGTERM first, then SIGKILL)
                try {
                    // // Removed activeProcesses.delete(pid) here - moved to _cleanupTerminalState

                    process.kill(pid, 'SIGTERM');
                    await new Promise(resolve => setTimeout(resolve, 200));
                    try {
                        process.kill(pid, 0);
                        try {
                            process.kill(pid, 'SIGKILL');
                            terminationStatus = 'SIGTERM sent, followed by SIGKILL.';
                        } catch (sigkillError) {
                            if (sigkillError.code === 'ESRCH') {
                                terminationStatus = 'Process likely terminated after SIGTERM (before SIGKILL needed).';
                            } else {
                                console.error(`[MyMCP ERROR] SIGKILL error for PID ${pid}:`, sigkillError);
                                throw sigkillError;
                            }
                        }
                    } catch (checkError) {
                        if (checkError.code === 'ESRCH') {
                            terminationStatus = 'Process likely terminated after SIGTERM.';
                        } else {
                            console.error(`[MyMCP ERROR] Error checking process ${pid} after SIGTERM:`, checkError);
                            throw checkError;
                        }
                    }
                } catch (error) {
                    // // Removed activeProcesses.delete(pid) here - moved to _cleanupTerminalState
                    if (error.code === 'ESRCH') {
                        terminationStatus = 'Process already exited before termination attempt.';
                    } else {
                        console.error(`Error sending termination signal to PID ${pid}:`, error);
                        terminationStatus = `Error during termination: ${error.message}`;
                        // killError = error; // // Removed - Not used
                    }
                }
                // --- End Stage 1 ---

                pidsToCleanup.push(pid); // Mark PID for cleanup in Stage 2
                results.push({ pid, status: terminationStatus, stdout: finalStdout, stderr: finalStderr });

            } // End of loop through PIDs

            // --- Stage 2: Perform Cleanup --- 
            let overallCleanupStatus = 'Cleanup successful.';
            if (pidsToCleanup.length > 0) {
                console.error(`[MyMCP DEBUG] stop_terminal_command: Entering cleanup stage for PIDs: ${pidsToCleanup.join(', ')}`); // Optional debug
            }

            for (const pid of pidsToCleanup) {
                let cleanupSuccess = false;
                let cleanupMessage = 'Cleanup attempted.';
                try {
                    cleanupSuccess = await _cleanupTerminalState(pid);
                    if (cleanupSuccess) {
                        stateChanged = true;
                        cleanupMessage = 'Cleanup successful.';
                    } else {
                        cleanupMessage = 'Cleanup failed (state not found).';
                        overallCleanupStatus = 'Cleanup finished with errors (state not found for some PIDs).';
                    }
                } catch (cleanupError) {
                    console.error(`Error during cleanup stage for PID ${pid}:`, cleanupError);
                    cleanupMessage = `Cleanup failed: ${cleanupError.message}`;
                    overallCleanupStatus = 'Cleanup finished with errors.'; // Mark overall status
                    stateChanged = true; // State might have been partially changed before error
                }

                // Update the result status for this PID to reflect the cleanup outcome
                const resultIndex = results.findIndex(r => r.pid === pid);
                if (resultIndex !== -1) {
                    // Append cleanup status to existing termination status
                    results[resultIndex].status = `${results[resultIndex].status} ${cleanupMessage}`;
                } else {
                    // If PID wasn't in results (e.g., not found initially), add a cleanup-only entry?
                    // Or ignore, as it wasn't found in the first place.
                    console.error(`[MyMCP ERROR] PID ${pid} marked for cleanup but not found in results array.`);
                }
            }

            // Persist the final state after all cleanups
            if (stateChanged) {
                try {
                    writeTerminalState(terminalStates);
                    console.error(`[MyMCP DEBUG] stop_terminal_command: Wrote final terminal state after cleanup.`); // Optional debug
                } catch (writeError) {
                    console.error('Error writing final terminal state after cleanup:', writeError);
                    overallCleanupStatus = 'Cleanup completed but failed to write final state.';
                }
            }

            // Log overall cleanup status if issues occurred
            if (overallCleanupStatus !== 'Cleanup successful.') {
                console.error(`Overall cleanup status: ${overallCleanupStatus}`);
            }

            // Format expected by the tool - return an array of result objects
            return { content: [{ type: "text", text: JSON.stringify(results) }] };
        }
    );
} catch (toolRegistrationError) {
    // Log the error during tool registration
    console.error(`!!!!!!!!!! FAILED TO REGISTER TOOL 'stop_terminal_command' !!!!!!!!!!`);
    console.error(toolRegistrationError);
    // Optionally re-throw or exit if registration failure is fatal
    // process.exit(1); // Or handle more gracefully depending on server design
}

// --- New MCP Tools --- END ---

// --- send_terminal_input Tool --- START ---
server.tool(
    'send_terminal_input',
    {
        pid: z.number().int().describe("The PID of the running process to send input to."),
        input: z.string().describe("The string to send to the process's standard input.")
    },
    async ({ pid, input }) => {
        // console.error(`[MyMCP DEBUG] send_terminal_input handler START - PID: ${pid}, Input length: ${input.length}`);
        const childProcess = activeProcesses.get(pid);
        const processState = terminalStates.find(state => state.pid === pid);

        if (!childProcess || !processState) {
            throw new Error(`Process with PID ${pid} not found or not managed by this server.`);
        }

        if (processState.status !== 'Running') {
            throw new Error(`Process with PID ${pid} is not currently running (Status: ${processState.status}). Cannot send input.`);
        }

        // Check if stdin exists and is writable
        if (!childProcess.stdin || !childProcess.stdin.writable || childProcess.stdin.destroyed) {
            console.error(`[MyMCP ERROR] Stdin not available or writable for PID ${pid}. Writable: ${childProcess.stdin?.writable}, Destroyed: ${childProcess.stdin?.destroyed}`);
            throw new Error(`Standard input for process PID ${pid} is not available or writable.`);
        }

        try {
            const inputToSend = input + '\n'; // Append newline crucial for many interactive programs
            const writeSuccess = childProcess.stdin.write(inputToSend);
            if (!writeSuccess) {
                console.error(`[MyMCP WARN] High water mark reached for stdin buffer of PID ${pid}. Input might be buffered.`); // Changed log to error
                // Application should ideally handle backpressure, but for now we just warn.
            }
            // console.error(`[MyMCP DEBUG] Successfully wrote input to PID ${pid}. Write success: ${writeSuccess}`);
            return { content: [{ type: "text", text: `Successfully sent input to process PID ${pid}.` }] };
        } catch (error) {
            // Catch errors like EPIPE if the process closed stdin unexpectedly
            console.error(`[MyMCP ERROR] Error writing input to PID ${pid}:`, error);
            throw new Error(`Failed to write input to process PID ${pid}: ${error.message}`);
        }
    }
);
// --- send_terminal_input Tool --- END ---

// Create the transport and connect the server
async function startServer() {
    ensureLogsDirExists(); // Ensure logs directory exists before starting
    loadTerminalState();   // Load initial state from file
    console.error(`[MyMCP Server] Initial state loaded. ${terminalStates.length} states found.`); // Changed log to error

    // Start the background status monitor
    if (statusMonitorInterval) {
        clearInterval(statusMonitorInterval); // Clear existing interval if any
    }
    statusMonitorInterval = setInterval(updateRunningProcessStatuses, 30000); // Check less frequently (30s)
    console.error('[MyMCP Server] Background status monitor interval set.'); // Changed log to error

    try {
        console.error('[MyMCP Server] Creating StdioServerTransport...'); // Changed log to error
        const transport = new StdioServerTransport();
        console.error('[MyMCP Server] StdioServerTransport created. Connecting server...'); // Changed log to error
        await server.connect(transport);
        console.error('[MyMCP Server] Server connected successfully via stdio.'); // If this logs, connection worked // Changed log to error
    } catch (error) {
        // Keep console.error for fatal startup errors ONLY
        console.error("!!!!!!!!!! [MyMCP Server] FAILED TO CONNECT TRANSPORT !!!!!!!!!!");
        console.error("Failed to start MCP Commit Server:", error);
        process.exit(1);
    }
}

// Start the server
console.error('[MyMCP Server] Starting server...'); // Changed log to error
startServer(); 