import { execa } from 'execa';
import { spawn } from 'child_process';
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import fs from 'fs';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';
import { Buffer } from 'node:buffer'; // Import Buffer for Base64
import os from 'os'; // Import os for platform check
// No longer needed: import fsPromises from 'fs/promises';

// --- ADDED: Parse server startup args for default CWD ---
let serverDefaultCwd = null;
const cwdIndex = process.argv.indexOf('--cwd');
if (cwdIndex > -1 && process.argv[cwdIndex + 1]) {
    serverDefaultCwd = path.resolve(process.argv[cwdIndex + 1]); // Resolve to absolute path
} else {
}

// Helper to escape double quotes for bash -c "..."
const escapeDoubleQuotesForBash = (str) => {
    return str.replace(/"/g, '\\"');
};

// Helper to escape quotes for bash -c "..." - NO LONGER NEEDED?
// const escapeQuotesForBash = (str) => {
//   // Escape backslashes first, then double quotes, then single quotes
//   return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/'/g, "\\'");
// };

// Get the directory name of the current module (optional, might not be needed anymore)
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// --- REMOVED old projectRoot calculation ---
// // Determine project root (assuming server.js is in .cursor/mcp/mcp-commit-server/)
// const projectRoot = path.resolve(__dirname, '../../../../');

// --- ADDED: Determine CWD from environment or process ---
// const userWorkspaceCwd = process.env.CURSOR_WORKSPACE_ROOT || process.cwd();
// console.log(`[ProcessManager] Using CWD: ${userWorkspaceCwd}`); // Optional debug log

/**
 * Helper function to clean up resources associated with a process.
 * @param {number} pid Process ID.
 * @param {fs.WriteStream} stdoutStream Stream for stdout log.
 * @param {fs.WriteStream} stderrStream Stream for stderr log.
 * @param {ChildProcess} child The child process object.
 */
async function cleanupProcessResources(pid, stdoutStream, stderrStream, child) {
    // console.log(`[ProcessManager] Cleaning up resources for PID ${pid}...`);
    // Close file streams safely
    stdoutStream?.end();
    stderrStream?.end();

    // Remove all listeners from the child process to prevent memory leaks
    // Especially important if the process object might persist for a bit
    child?.removeAllListeners();

    // Optional: Add a small delay if needed for system resource release?
    // await new Promise(resolve => setTimeout(resolve, 10));
}

/**
 * Spawns a new process, manages its state, and handles logging.
 * Returns an object containing the pid, log file paths, and a completion promise.
 * @param {string} command The command to execute.
 * @param {string | undefined | null} explicitWorkingDirectory Optional explicit CWD from the tool call.
 * @returns {Promise<object>} Promise resolving to { pid, stdout_log, stderr_log, completionPromise, cleanupPromise }
 */
export async function spawnProcess(command, explicitWorkingDirectory) {
    // Ensure logs directory exists for this specific execution
    const logsDir = await Logger.ensureLogsDir();
    if (!logsDir) {
        // Log the error and prevent proceeding if logsDir is null
        const errorMsg = 'Failed to ensure logs directory exists. Cannot proceed.';
        console.error(`[ProcessManager] ${errorMsg}`);
        throw new Error(errorMsg);
    }

    // --- Determine Shell, Args, Options, and CWD FIRST ---
    let shell, args, spawnOptions;
    const initialCommand = command; // Store original command for state
    // PRIORITIZE: Explicit CWD > Server --cwd Arg > Env Var > Server process.cwd()
    const executionCwd = explicitWorkingDirectory || serverDefaultCwd || process.env.CURSOR_WORKSPACE_ROOT || process.cwd();
    // Debug log for chosen CWD
    // console.log(`[ProcessManager] Spawning process in CWD: ${executionCwd}`);

    if (os.platform() === 'win32') {
        shell = 'C:\\\\Program Files\\\\Git\\\\bin\\\\bash.exe';

        // Convert CWD to Git Bash format (e.g., C:\\Users\\Jamet -> /c/Users/Jamet)
        // CORRECTED: Use match and lowercase group, ensure single slash
        let bashCwd = executionCwd.replace(/^([A-Za-z]):\\/, (match, drive) => `/${drive.toLowerCase()}/`);
        bashCwd = bashCwd.replace(/\\\\/g, '/'); // Convert backslashes

        // Prepend cd command to the actual command for Windows + Git Bash
        // Escape the path properly for the bash shell
        const escapedBashCwd = bashCwd.replace(/([\\\'\"])/g, '\\\\$1'); // Minimal escape for cd
        const fullCommand = `cd "${escapedBashCwd}" && ${command}`;

        // Escape the *entire* command string for the outer shell/Node spawn
        const base64Command = Buffer.from(fullCommand).toString('base64');
        args = ['-c', `eval $(echo ${base64Command} | base64 --decode)`];
        spawnOptions = {
            stdio: ['ignore', 'pipe', 'pipe'],
            detached: false,
            shell: false,
            windowsHide: true,
        };
    } else { // macOS, Linux, etc.
        shell = '/bin/bash';
        args = ['-c', command];
        spawnOptions = {
            stdio: ['ignore', 'pipe', 'pipe'],
            detached: false,
            shell: false,
            cwd: executionCwd
        };
    }

    // --- Spawn the process ---
    const child = spawn(shell, args, spawnOptions);

    // --- Get PID AFTER spawning ---
    const pid = child.pid;
    if (pid === undefined) {
        // Should not happen if spawn itself doesn't throw
        throw new Error('Failed to get PID from spawned process.');
    }

    // --- Setup Logging and State using the obtained PID ---
    const stdout_log = path.join(logsDir, `${pid}_stdout.log`);
    const stderr_log = path.join(logsDir, `${pid}_stderr.log`);
    const stdout_stream = fs.createWriteStream(stdout_log, { flags: 'a' });
    const stderr_stream = fs.createWriteStream(stderr_log, { flags: 'a' });

    // Add initial state entry NOW that we have the PID
    await StateManager.addState({
        pid,
        command: initialCommand,
        status: 'Running',
        exit_code: null,
        stdout_log,
        stderr_log,
        startTime: new Date().toISOString(),
        endTime: null,
        cwd: executionCwd
    });

    // Log streams immediately
    child.stdout.pipe(stdout_stream);
    child.stderr.pipe(stderr_stream);

    // --- Promise Handling for Completion and Cleanup ---

    // Promise that resolves/rejects when the process exits
    const completionPromise = new Promise((resolve, reject) => {
        child.on('error', (error) => {
            // console.error(`[PID ${pid}] Spawn Error:`, error); // Optional
            // State updated in 'exit' handler or here if exit doesn't fire
            StateManager.updateState(pid, {
                status: 'Failure',
                endTime: new Date().toISOString(),
                error: error.message // Store error message
            }).catch(err => console.error(`[PID ${pid}] Error updating state on spawn error:`, err));
            reject(error); // Reject completionPromise on spawn error
        });

        child.on('exit', (code, signal) => {
            // console.log(`[PID ${pid}] Exited with code: ${code}, signal: ${signal}`); // Optional
            // State updated here
            StateManager.updateState(pid, {
                status: (code === 0) ? 'Success' : 'Failure',
                exit_code: code,
                endTime: new Date().toISOString(),
                signal: signal // Store signal if present
            }).then(() => {
                // Resolve completionPromise *after* state update
                resolve({ code, signal });
            }).catch(err => {
                console.error(`[PID ${pid}] Error updating state on exit:`, err);
                // Resolve anyway? Or reject? Let's resolve but log error.
                resolve({ code, signal });
            });
        });
    });

    // Promise that resolves when log streams are closed
    const cleanupPromise = new Promise((resolve) => {
        let stdoutClosed = false;
        let stderrClosed = false;

        const checkClose = () => {
            if (stdoutClosed && stderrClosed) {
                // console.log(`[PID ${pid}] Log streams closed.`); // Optional
                resolve(); // Resolve cleanupPromise when both streams are closed
            }
        };

        stdout_stream.on('close', () => {
            stdoutClosed = true;
            checkClose();
        });
        stderr_stream.on('close', () => {
            stderrClosed = true;
            checkClose();
        });

        // Handle stream errors (e.g., write errors)
        stdout_stream.on('error', (err) => {
            console.error(`[PID ${pid}] Stdout stream error:`, err);
            stdoutClosed = true; // Consider it closed on error too
            checkClose();
        });
        stderr_stream.on('error', (err) => {
            console.error(`[PID ${pid}] Stderr stream error:`, err);
            stderrClosed = true; // Consider it closed on error too
            checkClose();
        });

        // Ensure streams eventually close after process exit
        completionPromise.finally(() => {
            // Use process.nextTick to ensure exit handlers run first
            process.nextTick(() => {
                if (!stdout_stream.destroyed) stdout_stream.end();
                if (!stderr_stream.destroyed) stderr_stream.end();
            });
        });
    });

    return { pid, stdout_log, stderr_log, completionPromise, cleanupPromise };
}

/**
 * Kills a process managed by execa.
 * @param {number} pid The process ID of the process to kill.
 * @returns {Promise<string>} Promise resolving with status message.
 */
export async function killProcess(pid) {
    // We need to use OS-level kill.
    // console.log(`[ProcessManager] Attempting to kill PID: ${pid}`);
    try {
        // Check if process exists first (0 signal)
        process.kill(pid, 0);

        // Attempt graceful termination first
        process.kill(pid, 'SIGTERM');
        // Wait a short period to see if it terminates
        await new Promise(resolve => setTimeout(resolve, 200)); // 200ms grace period

        // Check again if it exited
        try {
            process.kill(pid, 0);
            // Still running, force kill
            // console.warn(`[ProcessManager] Process ${pid} did not exit after SIGTERM, sending SIGKILL.`);
            process.kill(pid, 'SIGKILL');
            await new Promise(resolve => setTimeout(resolve, 100)); // Short wait after SIGKILL
        } catch (e) {
            if (e.code === 'ESRCH') {
                // Process already exited after SIGTERM
                // console.log(`[ProcessManager] Process ${pid} exited after SIGTERM.`);
                return `Process ${pid} terminated successfully (SIGTERM).`;
            } else {
                throw e; // Other error checking after SIGTERM
            }
        }
        // Check one last time after SIGKILL
        try {
            process.kill(pid, 0);
            // console.error(`[ProcessManager] Process ${pid} did NOT exit after SIGKILL!`);
            return `Process ${pid} failed to terminate after SIGKILL.`;
        } catch (e) {
            if (e.code === 'ESRCH') {
                // console.log(`[ProcessManager] Process ${pid} exited after SIGKILL.`);
                return `Process ${pid} terminated successfully (SIGKILL).`;
            } else {
                throw e; // Other error checking after SIGKILL
            }
        }

    } catch (error) {
        if (error.code === 'ESRCH') {
            // console.warn(`[ProcessManager] Process ${pid} not found or already exited when trying to kill.`);
            return `Process ${pid} not found or already exited.`;
        } else if (error.code === 'EPERM') {
            // console.error(`[ProcessManager] Permission error trying to kill process ${pid}.`);
            return `Permission error trying to kill process ${pid}.`;
        } else {
            // console.error(`[ProcessManager] Unexpected error killing process ${pid}:`, error);
            return `Error killing process ${pid}: ${error.message}`;
        }
    }
}

export { }; // Ensure it's treated as a module