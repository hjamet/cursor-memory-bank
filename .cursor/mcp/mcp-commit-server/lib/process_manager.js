import { execa } from 'execa';
import { spawn } from 'child_process';
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import fs from 'fs';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';
import { Buffer } from 'node:buffer'; // Import Buffer for Base64
// No longer needed: import os from 'os';
// No longer needed: import fsPromises from 'fs/promises';

// Helper to escape double quotes for bash -c "..."
const escapeDoubleQuotesForBash = (str) => {
    return str.replace(/"/g, '\\"');
};

// Helper to escape quotes for bash -c "..." - NO LONGER NEEDED?
// const escapeQuotesForBash = (str) => {
//   // Escape backslashes first, then double quotes, then single quotes
//   return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/'/g, "\\'");
// };

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// Restore global projectRoot calculation - CORRECTED
const projectRoot = path.resolve(__dirname, '../../../../'); // Go up 4 levels

/**
 * Spawns a process, manages its state, and logs its output.
 * @param {string} command The command line to execute.
 * @returns {Promise<{pid: number, completionPromise: Promise, cleanupPromise: Promise}>} Promise resolving with initial info.
 */
export async function spawnProcess(command) {
    let child;
    let pid;
    let stdoutLogPath;
    let stderrLogPath;
    let stdoutStream;
    let stderrStream;
    let cleanupResolve;
    const cleanupPromise = new Promise(resolve => { cleanupResolve = resolve; });
    let finalUpdateDone = false; // Flag to prevent duplicate final updates

    const startTime = new Date().toISOString();

    try {
        await Logger.ensureLogsDir();

        // Determine how to spawn based on the command string
        let executable;
        let args;
        // Get CWD of the current Node process (MCP Server) - REVERT THIS
        // const currentProcessCwd = process.cwd();
        let spawnOptions = {
            detached: true,
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: projectRoot, // Use the calculated projectRoot again
            shell: false
        };

        const gitBashPath = "C:\\Program Files\\Git\\bin\\bash.exe";

        if (process.platform === 'win32') {
            executable = gitBashPath;
            // Encode the command in Base64 to avoid complex escaping
            const base64Command = Buffer.from(command).toString('base64');
            // Construct bash command to decode and execute using eval
            const bashCommand = `eval $(echo '${base64Command}' | base64 -d)`;
            args = ['-c', bashCommand];
            spawnOptions.shell = false; // Ensure shell is false for direct bash execution
        } else {
            // Non-Windows: Use default shell for compatibility
            executable = command; // Let the default shell handle it
            args = [];
            spawnOptions.shell = true;
        }

        // --- DEBUG LOGGING START ---
        // console.log(`[ProcessManager] Using server process CWD: ${currentProcessCwd}`); // Removed debug log
        // console.log(`[ProcessManager] Effective spawnOptions.cwd: ${spawnOptions.cwd}`); // Removed debug log
        // --- DEBUG LOGGING END ---

        // Spawn the process
        try {
            child = spawn(executable, args, spawnOptions);
        } catch (spawnErr) {
            // No need for shell: true fallback anymore on Windows
            // console.error(`[ProcessManager] Initial spawn failed: ${spawnErr.message}. Code: ${spawnErr.code}`); // Keep commented out
            throw spawnErr; // Re-throw error if direct bash spawn fails
        }

        pid = child.pid;
        if (pid === undefined) {
            // Clean up streams if they were somehow created before PID assignment failed
            stdoutStream?.end();
            stderrStream?.end();
            throw new Error('Failed to get PID for spawned process.');
        }

        // Create log streams
        const streams = Logger.createLogStreams(pid);
        stdoutLogPath = streams.stdoutLogPath;
        stderrLogPath = streams.stderrLogPath;
        stdoutStream = streams.stdoutStream;
        stderrStream = streams.stderrStream;

        // Create a promise that resolves/rejects when the process finishes
        const completionPromise = new Promise((resolve, reject) => {
            child.once('close', (code, signal) => resolve({ code, signal }));
            child.once('error', reject);
            // We don't need to explicitly handle 'exit' here as 'close' guarantees finality
        });

        // Capture output using event listeners
        let stdoutData = ''; // Potentially buffer small amounts for immediate return?
        let stderrData = '';
        let pendingWrites = 0;
        let writePromiseResolve = null;
        let writePromise = new Promise(resolve => { writePromiseResolve = resolve; });

        const handleData = async (streamType, logPath, data) => {
            pendingWrites++;
            try {
                await Logger.appendLog(logPath, data);
            } finally {
                pendingWrites--;
                if (pendingWrites === 0 && writePromiseResolve) {
                    // If this was the last pending write after close was initiated,
                    // resolve the promise we wait for in handleClose.
                    writePromiseResolve();
                    writePromiseResolve = null; // Prevent resolving multiple times
                }
            }
        };

        child.stdout.on('data', (data) => {
            //stdoutData += data.toString(); // Optional: buffer recent data
            handleData('stdout', stdoutLogPath, data).catch(err => {
                // console.error(`[ProcessManager] Error handling stdout data for PID ${pid}:`, err);
            });
        });

        child.stderr.on('data', (data) => {
            //stderrData += data.toString(); // Optional: buffer recent data
            handleData('stderr', stderrLogPath, data).catch(err => {
                // console.error(`[ProcessManager] Error handling stderr data for PID ${pid}:`, err);
            });
        });

        // Ensure streams associated with the child process are closed when it exits
        // Note: 'end' might fire before 'close'
        child.stdout.on('end', () => {
            // console.log(`[ProcessManager] child.stdout received 'end' for PID ${pid}`);
            stdoutStream?.end(); // Close the underlying file stream
        });
        child.stderr.on('end', () => {
            // console.log(`[ProcessManager] child.stderr received 'end' for PID ${pid}`);
            stderrStream?.end(); // Close the underlying file stream
        });

        // Add entry to state
        const newStateEntry = {
            pid,
            command,
            cwd: spawnOptions.cwd, // Store the actual CWD used (projectRoot)
            status: 'Running',
            exit_code: null,
            stdout_log: stdoutLogPath,
            stderr_log: stderrLogPath,
            startTime,
            endTime: null,
        };
        await StateManager.addState(newStateEntry);

        // --- Process Event Handling ---

        // Flag to prevent duplicate final updates if 'close' and 'error' both fire near simultaneously
        let finalUpdateDone = false;

        const handleExit = async (code, signal) => {
            // console.log(`[ProcessManager] Process ${pid} received 'exit' event with code: ${code}, signal: ${signal}`);
            const exitCode = code ?? (signal ? 1 : 0); // Assign exit code based on signal if code is null
            const status = (exitCode === 0) ? 'Success' : 'Failure';
            const endTime = new Date().toISOString(); // Capture potential end time on exit

            // Update status immediately on exit, but don't mark as fully ended yet
            try {
                await StateManager.updateState(pid, {
                    status: status, // Set tentative status
                    exit_code: exitCode,
                    endTime: endTime, // Update end time tentatively
                });
                // console.log(`[ProcessManager] Updated tentative state for PID ${pid} on exit: Status=${status}, Code=${exitCode}`);
            } catch (stateErr) {
                // console.error(`[ProcessManager] Error during tentative state update on exit for PID ${pid}:`, stateErr);
            }
        };

        const handleClose = async (code, signal) => {
            if (finalUpdateDone) return; // Prevent duplicate updates
            finalUpdateDone = true;

            // Exit code/status should ideally be set by handleExit, but recalculate for safety
            const finalExitCode = code ?? (signal ? 1 : 0);
            const finalStatus = (finalExitCode === 0) ? 'Success' : 'Failure';
            const finalEndTime = (await StateManager.getState(pid))?.endTime ?? new Date().toISOString(); // Use existing endTime if set by exit, else now

            // Wait for file write streams to finish (if they haven't already)
            // and wait for any pending async writes from handleData to complete.
            // console.log(`[ProcessManager] Waiting for streams/writes to finish for PID ${pid}...`);
            const streamFinishPromises = [];
            // Only wait for streams if they exist and aren't already closed/finished
            if (stdoutStream && !stdoutStream.destroyed) streamFinishPromises.push(new Promise((res, rej) => {
                stdoutStream.once('finish', res);
                stdoutStream.once('error', rej);
            }));
            if (stderrStream && !stderrStream.destroyed) streamFinishPromises.push(new Promise((res, rej) => {
                stderrStream.once('finish', res);
                stderrStream.once('error', rej);
            }));

            // Add promise to wait for pending async writes
            if (pendingWrites > 0) {
                // console.log(`[ProcessManager] Waiting for ${pendingWrites} pending writes for PID ${pid}`);
                streamFinishPromises.push(writePromise);
            } else {
                // If no pending writes, resolve the promise immediately in case handleClose was called first
                if (writePromiseResolve) writePromiseResolve();
            }

            try {
                await Promise.all(streamFinishPromises);
                // console.log(`[ProcessManager] File streams/writes finished for PID ${pid} after 'close' event.`);
            } catch (streamErr) {
                // This catch might be redundant if the error handlers within the promises resolve, but keep for safety.
                // console.error(`[ProcessManager] Error waiting for file streams to finish for PID ${pid}:`, streamErr);
            }

            // Final state update after streams are confirmed closed
            try {
                await StateManager.updateState(pid, {
                    status: finalStatus, // Confirm final status
                    exit_code: finalExitCode, // Confirm final exit code
                    endTime: finalEndTime, // Confirm final end time
                    // Read log files here if needed, or let get_terminal_output handle it
                });
                // console.log(`[ProcessManager] Updated final state for PID ${pid} after 'close': Status=${finalStatus}, Code=${finalExitCode}`);
            } catch (finalStateErr) {
                // console.error(`[ProcessManager] Error during final state update on 'close' for PID ${pid}:`, finalStateErr);
            }
            cleanupResolve({ status: finalStatus, code: finalExitCode }); // Resolve cleanup *after* state update
        };

        const handleError = async (err) => {
            if (finalUpdateDone) return; // Prevent duplicate updates
            finalUpdateDone = true;

            // console.error(`[ProcessManager] Error event for child process ${pid}:`, err);

            // Attempt to end streams immediately
            stdoutStream?.end();
            stderrStream?.end();

            // Update state to indicate failure due to an error event
            const errorEndTime = new Date().toISOString();
            let stateUpdateError = null;
            try {
                await StateManager.updateState(pid, {
                    status: 'Failure',
                    exit_code: null, // Typically no exit code in 'error' event
                    endTime: errorEndTime,
                    // Store error message? Maybe in a separate field or stderr_log?
                    // Let's add it to a potential error field if we modify state manager
                });
                // console.log(`[ProcessManager] Updated state to Failure for PID ${pid} due to 'error' event.`);
            } catch (stateErr) {
                stateUpdateError = stateErr;
            }
            // Resolve cleanupPromise *after* state update attempt
            cleanupResolve({ status: 'Failure', code: null, error: stateUpdateError || err });
        };

        // Register event handlers
        child.on('exit', handleExit);
        child.on('close', handleClose); // Use 'close' for finalization
        child.on('error', handleError);

        return {
            pid,
            exit_code: null, // This is initial, final code comes from completionPromise/state
            stdout_log: stdoutLogPath,
            stderr_log: stderrLogPath,
            completionPromise, // Return the promise
            cleanupPromise     // Resolves after state/logs are finalized
        };
    } catch (err) {
        // console.error(`[ProcessManager] Error during spawnProcess setup for command "${command}":`, err);
        // Ensure streams are closed if they were opened during a failed setup
        stdoutStream?.end();
        stderrStream?.end();

        // If PID was assigned before error, try to update state to Failure
        // This handles errors between PID assignment and returning the promise
        if (pid && !finalUpdateDone) { // Check finalUpdateDone here too
            try {
                await StateManager.updateState(pid, {
                    status: 'Failure',
                    exit_code: null,
                    endTime: new Date().toISOString(),
                    // Maybe add error info here too
                });
            } catch (stateErr) {
                // console.error(`[ProcessManager] Error updating state after setup error for PID ${pid}:`, stateErr);
            }
        }
        // Re-throw the error to the caller (e.g., terminal_execution.js)
        throw err;
    }
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