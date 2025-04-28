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
import fkill from 'fkill'; // <-- ADDED: Import fkill
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
    const isVisible = process.argv.includes("--visible"); // Check for --visible flag
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
            // If --visible flag is passed AND on windows, show the window
            windowsHide: isVisible ? false : true,
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
 * Kills a process and its child processes using fkill.
 * @param {number} pid The process ID of the process to kill.
 * @returns {Promise<string>} Promise resolving with status message.
 */
export async function killProcess(pid) {
    // console.log(`[ProcessManager] Attempting to kill process tree for PID: ${pid}`);
    try {
        // Use fkill to kill the process and its children forcefully
        // force: true uses SIGKILL
        // tree: true attempts to kill the whole process tree (default on Windows, explicit here)
        await fkill(pid, { force: true, tree: true, ignoreCase: true });
        // console.log(`[ProcessManager] Process tree for PID ${pid} killed successfully via fkill.`);
        // Update state to 'Stopped' after successful kill attempt
        await StateManager.updateState(pid, {
            status: 'Stopped', // Indicate it was stopped externally
            endTime: new Date().toISOString(),
        }).catch(err => console.error(`[PID ${pid}] Error updating state after kill:`, err));
        return `Process tree for ${pid} terminated successfully (fkill).`;
    } catch (error) {
        // console.warn(`[ProcessManager] Error killing process tree for PID ${pid} via fkill:`, error);

        // Check specific fkill error types (it might throw custom errors or process.kill errors)
        // fkill throws if the process doesn't exist.
        if (error.message.includes('Process doesn\'t exist') || error.code === 'ESRCH') {
            // Update state if process was already gone
            await StateManager.updateState(pid, {
                status: 'Stopped', // Or 'Failure' if it should have been running? Stopped seems better.
                endTime: new Date().toISOString(),
                error: `Process ${pid} not found during kill attempt.`
            }).catch(err => console.error(`[PID ${pid}] Error updating state on kill error (not found):`, err));
            return `Process ${pid} not found or already exited.`;
        } else if (error.code === 'EPERM') {
            // Update state on permission error
            await StateManager.updateState(pid, {
                status: 'Failure', // Keep as Failure if kill failed due to perms
                error: `Permission error trying to kill process ${pid}.`
            }).catch(err => console.error(`[PID ${pid}] Error updating state on kill error (permission):`, err));
            return `Permission error trying to kill process ${pid}.`;
        } else {
            // Update state on other errors
            await StateManager.updateState(pid, {
                status: 'Failure', // Keep as Failure on unexpected kill errors
                error: `Unexpected error killing process ${pid}: ${error.message}`
            }).catch(err => console.error(`[PID ${pid}] Error updating state on kill error (other):`, err));
            return `Error killing process tree for ${pid}: ${error.message}`;
        }
    }
}

export { }; // Ensure it's treated as a module