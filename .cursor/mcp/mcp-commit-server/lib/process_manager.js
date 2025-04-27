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
const workspaceRoot = process.env.MCP_WORKSPACE_ROOT || path.resolve(__dirname, '../../../..'); // Go up one more level to get actual root
const MAX_BUFFER_SIZE = 10 * 1024 * 1024; // Global constant (10MB)

/**
 * Check if a command is a Python command.
 * @param {string} command The command to check
 * @returns {boolean} True if it's a Python command
 */
function isPythonCommand(command) {
    return command.trim().startsWith('python') || command.trim().startsWith('"python') ||
        command.trim().startsWith("'python") || command.trim().startsWith('py ');
}

/**
 * Create a wrapped Python command that redirects output to files.
 * @param {string} command The original Python command
 * @param {string} stdoutFile The path to the stdout file
 * @param {string} stderrFile The path to the stderr file
 * @returns {string} The wrapped command
 */
function createPythonWrapper(command, stdoutFile, stderrFile) {
    // For Python commands, we'll create a wrapper that ensures output redirection
    const escapedStdoutFile = stdoutFile.replace(/\\/g, '\\\\');
    const escapedStderrFile = stderrFile.replace(/\\/g, '\\\\');

    // Extract the python command and its arguments
    const parts = command.match(/^(["']?python(?:\s+|-)?(?:\.exe)?["']?)\s*(.*)$/i);
    if (!parts) {
        // Fallback if our regex didn't match
        return `${command} > "${stdoutFile}" 2> "${stderrFile}"`;
    }

    const pythonCmd = parts[1];
    const pythonArgs = parts[2];

    // Create a Python wrapper that ensures output capture
    return `${pythonCmd} -c "
import sys, subprocess, os

# Create the files to ensure they exist
with open('${escapedStdoutFile}', 'w') as f: pass
with open('${escapedStderrFile}', 'w') as f: pass

# Run the original command and capture its output
try:
    cmd = ${JSON.stringify(pythonArgs)}
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proc.communicate()
    
    # Write output to files
    with open('${escapedStdoutFile}', 'w') as f:
        f.write(stdout)
    with open('${escapedStderrFile}', 'w') as f:
        f.write(stderr)
    
    # Exit with the same code
    sys.exit(proc.returncode)
except Exception as e:
    with open('${escapedStderrFile}', 'w') as f:
        f.write(f'Error in wrapper: {str(e)}')
    sys.exit(1)
"`;
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

    // For Python commands, set up temporary files for output capture
    let stdoutFile = null;
    let stderrFile = null;
    let isPython = isPythonCommand(command);
    let wrappedCommand = command;

    if (isPython) {
        // Create unique filenames for this process
        const randomId = Math.random().toString(36).substring(2, 15);
        stdoutFile = path.join(workspaceRoot, `.tmp_stdout_${randomId}.txt`);
        stderrFile = path.join(workspaceRoot, `.tmp_stderr_${randomId}.txt`);

        // Create a wrapped command that ensures output capture
        wrappedCommand = createPythonWrapper(command, stdoutFile, stderrFile);
        Logger.logDebug(`[PID UNKNOWN YET] Using Python wrapper for command: ${command}`);
        Logger.logDebug(`[PID UNKNOWN YET] Wrapped command: ${wrappedCommand}`);
    }

    try {
        const execaOptions = {
            shell: true,
            stdio: 'pipe',
            detached: true,
            cwd: workspaceRoot,
            reject: false // Handle completion manually based on result
        };

        Logger.logDebug(`[PID UNKNOWN YET] Spawning with execa: Command: ${wrappedCommand}, Options: ${JSON.stringify(execaOptions)}`);
        child = execa(wrappedCommand, execaOptions);

        pid = child.pid;
        if (pid === undefined) {
            throw new Error('Failed to get PID from execa process.');
        }
        Logger.logDebug(`[PID ${pid}] Spawned successfully with execa.`);

        const newStateEntry = {
            pid,
            command,
            cwd: execaOptions.cwd,
            status: 'Running',
            exit_code: null,
            stdout_log: null,
            stderr_log: null,
            startTime,
            endTime: null,
        };
        StateManager.addState(newStateEntry).catch(e => console.error("Error adding initial state:", e));

        (async () => {
            let finalState = {};
            let result = null; // To store result outside try block
            try {
                result = await child;
                Logger.logDebug(`[PID ${pid}] execa completed. Exit Code: ${result.exitCode}, Signal: ${result.signal}`);

                let stdout = result.stdout || '';
                let stderr = result.stderr || '';

                // If we used the Python wrapper, read from the temporary files
                if (isPython && stdoutFile && stderrFile) {
                    try {
                        if (fs.existsSync(stdoutFile)) {
                            stdout = fs.readFileSync(stdoutFile, 'utf8');
                            Logger.logDebug(`[PID ${pid}] Read ${stdout.length} bytes from stdout file`);
                            // Clean up
                            fs.unlinkSync(stdoutFile);
                        }

                        if (fs.existsSync(stderrFile)) {
                            stderr = fs.readFileSync(stderrFile, 'utf8');
                            Logger.logDebug(`[PID ${pid}] Read ${stderr.length} bytes from stderr file`);
                            // Clean up
                            fs.unlinkSync(stderrFile);
                        }
                    } catch (fileErr) {
                        console.error(`[ProcessManager] Error reading output files for PID ${pid}:`, fileErr);
                        stderr += `\nError reading output files: ${fileErr.message}`;
                    }
                }

                const finalStatus = result.exitCode === 0 ? 'Success' : 'Failure';
                finalState = {
                    pid: pid,
                    command: command,
                    cwd: execaOptions.cwd,
                    startTime: startTime,
                    status: finalStatus,
                    exit_code: result.exitCode,
                    endTime: new Date().toISOString(),
                    stdout: stdout,
                    stderr: stderr,
                    stdout_log: null, stderr_log: null,
                };

            } catch (error) {
                // Should not happen with reject: false unless execa setup fails catastrophically
                console.error(`[ProcessManager] Unexpected Error awaiting execa process ${pid}:`, error);
                Logger.logDebug(`[PID ${pid}] execa awaited promise failed unexpectedly: ${error.message}`);

                let stdout = error.stdout || '';
                let stderr = (error.stderr || '') + `\nExeca Error: ${error.message}`;

                // If we used the Python wrapper, try to read from the temporary files, even in case of error
                if (isPython && stdoutFile && stderrFile) {
                    try {
                        if (fs.existsSync(stdoutFile)) {
                            stdout = fs.readFileSync(stdoutFile, 'utf8');
                            // Clean up
                            fs.unlinkSync(stdoutFile);
                        }

                        if (fs.existsSync(stderrFile)) {
                            stderr = fs.readFileSync(stderrFile, 'utf8');
                            // Clean up
                            fs.unlinkSync(stderrFile);
                        }
                    } catch (fileErr) {
                        console.error(`[ProcessManager] Error reading output files for PID ${pid} after execution error:`, fileErr);
                        stderr += `\nError reading output files after execution error: ${fileErr.message}`;
                    }
                }

                finalState = {
                    pid: pid,
                    command: command,
                    cwd: execaOptions.cwd,
                    startTime: startTime,
                    status: 'Failure',
                    exit_code: error.exitCode ?? null,
                    endTime: new Date().toISOString(),
                    stdout: stdout,
                    stderr: stderr,
                    stdout_log: null, stderr_log: null,
                };
            } finally {
                // Ensure we clean up temp files in all cases
                if (isPython) {
                    try {
                        if (stdoutFile && fs.existsSync(stdoutFile)) {
                            fs.unlinkSync(stdoutFile);
                        }
                        if (stderrFile && fs.existsSync(stderrFile)) {
                            fs.unlinkSync(stderrFile);
                        }
                    } catch (cleanupErr) {
                        console.error(`[ProcessManager] Error cleaning up temporary files for PID ${pid}:`, cleanupErr);
                    }
                }
            }

            // Final state update for persistence
            const finalUpdatePayload = {
                status: finalState.status,
                exit_code: finalState.exit_code,
                endTime: finalState.endTime,
                stdout: finalState.stdout,
                stderr: finalState.stderr,
                stdout_log: null, stderr_log: null,
            };
            StateManager.updateState(pid, finalUpdatePayload).catch(err => {
                console.error(`[ProcessManager] Background persistence error for PID ${pid} after execa completion:`, err);
            });

            Logger.logDebug(`[PID ${pid}] Resolving completion promise with final state.`);
            resolveCompletion(finalState);
        })();

        return { pid, completionPromise };

    } catch (err) {
        console.error(`[ProcessManager] Error during execa setup for command "${command}":`, err);
        Logger.logDebug(`[PID UNKNOWN] Execa setup error details: ${JSON.stringify(err)}`);

        // Clean up temp files if we created them but failed to start the process
        if (isPython) {
            try {
                if (stdoutFile && fs.existsSync(stdoutFile)) {
                    fs.unlinkSync(stdoutFile);
                }
                if (stderrFile && fs.existsSync(stderrFile)) {
                    fs.unlinkSync(stderrFile);
                }
            } catch (cleanupErr) {
                console.error('[ProcessManager] Error cleaning up temporary files after setup failure:', cleanupErr);
            }
        }

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