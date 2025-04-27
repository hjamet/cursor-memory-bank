import { execa } from 'execa';
// import { spawn } from 'child_process'; // REVERTED
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';
// import os from 'os'; // No longer needed
// import fs from 'fs/promises'; // No longer needed

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const workspaceRoot = process.env.MCP_WORKSPACE_ROOT || path.resolve(__dirname, '../../../..'); // Go up one more level to get actual root
const MAX_BUFFER_SIZE = 10 * 1024 * 1024; // Global constant (10MB)

/**
 * Reads file content safely, returning empty string on ENOENT.
 * @param {string} filePath 
 * @returns {Promise<string>}
 */
async function readFileSafe(filePath) {
    try {
        return await fs.readFile(filePath, 'utf8');
    } catch (error) {
        if (error.code === 'ENOENT') {
            return ''; // File not found, return empty string
        } else {
            console.error(`[ProcessManager] Error reading temp file ${filePath}:`, error);
            return `[Error reading file: ${error.message}]`;
        }
    }
}

/**
 * Deletes a file safely, ignoring ENOENT errors.
 * @param {string} filePath 
 */
async function unlinkSafe(filePath) {
    try {
        await fs.unlink(filePath);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            console.error(`[ProcessManager] Error deleting temp file ${filePath}:`, error);
        }
    }
}

/**
 * Spawns a process, manages its state, and logs its output.
 * @param {string} command The command line to execute.
 * @returns {Promise<{pid: number, completionPromise: Promise}>} Promise resolving with initial info.
 */
export async function spawnProcess(command) {
    let child;
    let pid;
    let resolveCompletion;
    const completionPromise = new Promise(resolve => { resolveCompletion = resolve; });
    const startTime = new Date().toISOString();

    try {
        // Using execa with shell: true and default buffering as the final state
        const execaOptions = {
            shell: true, // Use shell for robustness, execa handles escaping
            stdio: 'pipe', // Required for execa to buffer output
            detached: true,
            cwd: workspaceRoot,
            reject: false, // Handle completion manually based on result
            env: { ...process.env, PYTHONUNBUFFERED: '1' } // Keep PYTHONUNBUFFERED just in case
        };
        Logger.logDebug(`[PID UNKNOWN YET] Spawning with execa (buffered, shell:true): Command: ${command}, Options: ${JSON.stringify(execaOptions)}`);
        child = execa(command, execaOptions);

        pid = child.pid;
        if (pid === undefined) {
            throw new Error('Failed to get PID from execa process.');
        }
        Logger.logDebug(`[PID ${pid}] Spawned successfully with execa (buffered, shell:true).`);

        const newStateEntry = {
            pid,
            command,
            cwd: execaOptions.cwd,
            status: 'Running',
            exit_code: null,
            stdout_log: null, // No external log files with buffered approach
            stderr_log: null,
            startTime,
            endTime: null,
        };
        StateManager.addState(newStateEntry).catch(e => console.error("Error adding initial state:", e));

        (async () => {
            let finalState = {};
            let result = null;
            try {
                result = await child;
                Logger.logDebug(`[PID ${pid}] execa completed. Exit Code: ${result.exitCode}, Signal: ${result.signal}`);

                const finalStatus = result.exitCode === 0 ? 'Success' : 'Failure';
                finalState = {
                    pid: pid,
                    command: command,
                    cwd: execaOptions.cwd,
                    startTime: startTime,
                    status: finalStatus,
                    exit_code: result.exitCode,
                    endTime: new Date().toISOString(),
                    stdout: result.stdout ?? '', // Use execa result stdout (might still be empty for Python)
                    stderr: result.stderr ?? '', // Use execa result stderr (might still be empty for Python)
                    stdout_log: null,
                    stderr_log: null,
                };

            } catch (error) {
                console.error(`[ProcessManager] Unexpected Error awaiting execa process ${pid}:`, error);
                Logger.logDebug(`[PID ${pid}] execa awaited promise failed unexpectedly: ${error.message}`);
                finalState = {
                    pid: pid,
                    command: command,
                    cwd: execaOptions.cwd,
                    startTime: startTime,
                    status: 'Failure',
                    exit_code: error.exitCode ?? null,
                    endTime: new Date().toISOString(),
                    stdout: error.stdout ?? '',
                    stderr: (error.stderr ?? '') + `\nExeca Error: ${error.message}`,
                    stdout_log: null,
                    stderr_log: null,
                };
            }

            // Final state update for persistence
            const finalUpdatePayload = {
                status: finalState.status,
                exit_code: finalState.exit_code,
                endTime: finalState.endTime,
                stdout_log: null,
                stderr_log: null,
            };
            StateManager.updateState(pid, finalUpdatePayload).catch(err => {
                console.error(`[ProcessManager] Background persistence error for PID ${pid} after execa completion:`, err);
            });

            Logger.logDebug(`[PID ${pid}] Resolving completion promise with final state (buffered, shell:true).`);
            resolveCompletion(finalState);
        })();

        return { pid, completionPromise };

    } catch (err) {
        console.error(`[ProcessManager] Error during execa setup for command "${command}":`, err);
        Logger.logDebug(`[PID UNKNOWN] Execa setup error details: ${JSON.stringify(err)}`);
        if (resolveCompletion) {
            const errorState = {
                pid: null, command: command, cwd: workspaceRoot, startTime: startTime,
                status: 'Failure', exit_code: null, endTime: new Date().toISOString(),
                stdout: '', stderr: `Execa Setup Error: ${err.message}`, stdout_log: null, stderr_log: null
            };
            resolveCompletion(errorState);
            Logger.logDebug(`[PID UNKNOWN] Resolved completion promise with setup error state.`);
        } else {
            Logger.logDebug(`[PID UNKNOWN] Setup error, but resolveCompletion was null.`);
        }
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