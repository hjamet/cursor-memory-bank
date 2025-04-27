import { execa } from 'execa';
// import { spawn } from 'child_process'; // REVERTED
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import fs from 'fs';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';
// No longer needed: import os from 'os';
// No longer needed: import fsPromises from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../..'); // Assuming lib/ is two levels down

/**
 * Spawns a process, manages its state, and logs its output.
 * @param {string} command The command line to execute.
 * @returns {Promise<{pid: number, completionPromise: Promise}>} Promise resolving with initial info.
 */
export async function spawnProcess(command) {
    let child;
    let pid;
    let stdoutLogPath;
    let stderrLogPath;
    let stdoutStream;
    let stderrStream;

    const startTime = new Date().toISOString();

    try {
        await Logger.ensureLogsDir();

        // Determine how to spawn based on the command string
        let executable;
        let args;
        let spawnOptions = {
            detached: true, // Keep detached for background potential
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: projectRoot,
            shell: false // Default to false now
        };

        // Specific handling for Git Bash on Windows
        const gitBashPath = "C:\\Program Files\\Git\\bin\\bash.exe"; // Use escaped backslashes
        if (process.platform === 'win32' && command.startsWith(`"${gitBashPath}"`)) {
            const match = command.match(/^"(.*?)"\s+-c\s+"(.*)"$/);
            if (match && match[1] === gitBashPath) {
                executable = gitBashPath;
                args = ['-c', match[2]]; // Pass the command string as an argument to -c
            } else {
                executable = command; // The whole string
                args = [];
                spawnOptions.shell = true; // Revert to shell: true for this case
            }
        } else {
            // Default behavior for other commands/platforms
            executable = command; // Assume command is the executable or handled by shell
            args = [];
            spawnOptions.shell = true; // Use shell: true for general commands
        }

        // Spawn the process - First attempt with configured options (potentially shell: false)
        try {
            child = spawn(executable, args, spawnOptions);
        } catch (spawnErr) {
            // If the first attempt failed (e.g., ENOENT with shell: false), try again with shell: true
            if (spawnOptions.shell === false && spawnErr.code === 'ENOENT') {
                spawnOptions.shell = true;
                executable = command; // Use the original full command string
                args = [];
                try {
                    child = spawn(executable, args, spawnOptions); // Retry with shell: true
                } catch (retryErr) {
                    throw retryErr; // Throw the error from the retry
                }
            } else {
                throw spawnErr;
            }
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

        // Pipe output to log files
        child.stdout.pipe(stdoutStream);
        child.stderr.pipe(stderrStream);

        // Add entry to state
        const newStateEntry = {
            pid,
            command,
            cwd: execaOptions.cwd,
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
                console.error(`[ProcessManager] Error during tentative state update on exit for PID ${pid}:`, stateErr);
            }
        };

        const handleClose = async (code, signal) => {
            if (finalUpdateDone) return; // Prevent duplicate updates
            finalUpdateDone = true;

            // console.log(`[ProcessManager] Process ${pid} received 'close' event with code: ${code}, signal: ${signal}`);
            // Exit code/status should ideally be set by handleExit, but recalculate for safety
            const finalExitCode = code ?? (signal ? 1 : 0);
            const finalStatus = (finalExitCode === 0) ? 'Success' : 'Failure';
            const finalEndTime = (await StateManager.getState(pid))?.endTime ?? new Date().toISOString(); // Use existing endTime if set by exit, else now

            // Ensure file streams are ended explicitly before waiting for 'finish'
            // It's possible 'close' fires before pipes automatically end the streams
            stdoutStream?.end();
            stderrStream?.end();

            // Wait for file write streams to finish
            const streamFinishPromises = [];
            if (stdoutStream) streamFinishPromises.push(new Promise(res => stdoutStream.once('finish', res).on('error', (e) => { console.error(`[ProcessManager] stdoutStream finish error for ${pid}:`, e); res(); }))); // Add error handlers
            if (stderrStream) streamFinishPromises.push(new Promise(res => stderrStream.once('finish', res).on('error', (e) => { console.error(`[ProcessManager] stderrStream finish error for ${pid}:`, e); res(); }))); // Add error handlers

            try {
                await Promise.all(streamFinishPromises);
                // console.log(`[ProcessManager] File streams finished for PID ${pid} after 'close' event.`);
            } catch (streamErr) {
                // This catch might be redundant if the error handlers within the promises resolve, but keep for safety.
                console.error(`[ProcessManager] Error waiting for file streams to finish for PID ${pid}:`, streamErr);
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
                console.error(`[ProcessManager] Error during final state update on 'close' for PID ${pid}:`, finalStateErr);
            }
        };

        const handleError = async (err) => {
            if (finalUpdateDone) return; // Prevent duplicate updates
            finalUpdateDone = true;

            console.error(`[ProcessManager] Error event for child process ${pid}:`, err);

            // Attempt to end streams immediately
            stdoutStream?.end();
            stderrStream?.end();

            // Update state to indicate failure due to an error event
            const errorEndTime = new Date().toISOString();
            try {
                await StateManager.updateState(pid, {
                    status: 'Failure',
                    exit_code: null, // Typically no exit code in 'error' event
                    endTime: errorEndTime,
                    // Store error message? Maybe in a separate field or stderr_log?
                    // Let's add it to a potential error field if we modify state manager
                });
                console.log(`[ProcessManager] Updated state to Failure for PID ${pid} due to 'error' event.`);
            } catch (stateErr) {
                console.error(`[ProcessManager] Error updating state after 'error' event for PID ${pid}:`, stateErr);
            }
        };

        // Register event handlers
        child.on('exit', handleExit);
        child.on('close', handleClose); // Use 'close' for finalization
        child.on('error', handleError);

        return {
            pid,
            exit_code: null,
            stdout_log: stdoutLogPath,
            stderr_log: stderrLogPath
        };
    } catch (err) {
        console.error(`[ProcessManager] Error during spawnProcess setup for command "${command}":`, err);
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
                console.error(`[ProcessManager] Error updating state after setup error for PID ${pid}:`, stateErr);
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
    // Find the execa child process instance associated with the PID?
    // This is tricky because we only store state, not the live child object.
    // Let's stick to process.kill for now, assuming execa doesn't fundamentally change PID behavior.
    // TODO: Revisit if execa provides a better way to manage/kill detached processes by PID.
    try {
        process.kill(pid, 0);
    } catch (e) {
        if (e.code === 'ESRCH') {
            // Process already exited or never existed
            return `Process ${pid} already exited before termination attempt.`;
        } else {
            // Other error (e.g., permissions)
            console.error(`[ProcessManager] Error checking process ${pid} existence:`, e);
            return `Error checking process ${pid}: ${e.message}.`;
        }
    }

    // Process exists, attempt graceful termination
    try {
        process.kill(pid, 'SIGTERM');
        // Wait a short period to see if it terminates
        await new Promise(resolve => setTimeout(resolve, 200)); // 200ms grace period

        // Check again if it exited
        try {
            process.kill(pid, 0);
            // Still running, force kill
            console.warn(`[ProcessManager] Process ${pid} did not exit after SIGTERM, sending SIGKILL.`);
            try {
                process.kill(pid, 'SIGKILL');
                return `Process ${pid} terminated forcefully (SIGKILL).`;
            } catch (killErr) {
                // Handle error during SIGKILL (e.g., process died just before)
                console.error(`[ProcessManager] Error sending SIGKILL to ${pid}:`, killErr);
                if (killErr.code === 'ESRCH') {
                    return `Process ${pid} exited during termination attempt.`;
                } else {
                    return `Error sending SIGKILL to ${pid}: ${killErr.message}.`;
                }
            }
        } catch (e) {
            if (e.code === 'ESRCH') {
                // Exited gracefully after SIGTERM
                return `Process ${pid} terminated gracefully (SIGTERM).`;
            } else {
                // Should not happen if first check passed, but handle defensively
                console.error(`[ProcessManager] Error re-checking process ${pid} after SIGTERM:`, e);
                return `Error confirming termination for ${pid}: ${e.message}.`;
            }
        }
    } catch (termErr) {
        // Handle error during SIGTERM (e.g., permissions)
        console.error(`[ProcessManager] Error sending SIGTERM to ${pid}:`, termErr);
        if (termErr.code === 'ESRCH') {
            return `Process ${pid} exited before termination signal could be sent.`;
        } else {
            return `Error sending SIGTERM to ${pid}: ${termErr.message}.`;
        }
    }
}