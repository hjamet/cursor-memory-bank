import { spawn } from 'child_process';
// import { execa } from 'execa'; // REVERTED
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../..'); // Assuming lib/ is two levels down

/**
 * Spawns a process, manages its state, and logs its output.
 * @param {string} command The command line to execute.
 * @returns {Promise<{pid: number, exit_code: number | null, stdout_log: string, stderr_log: string}>} Promise resolving with initial info, or rejecting on immediate spawn error.
 */
export async function spawnProcess(command) {
    let child; // REVERTED from childProcess
    let pid;
    let stdoutLogPath;
    let stderrLogPath;
    let stdoutStream;
    let stderrStream;
    let initialStdout = '';
    let initialStderr = '';

    const startTime = new Date().toISOString();

    // Listeners to capture initial output
    const stdoutListener = (data) => { initialStdout += data.toString(); };
    const stderrListener = (data) => { initialStderr += data.toString(); };

    try {
        await Logger.ensureLogsDir();

        // Revert to original logic: Always use shell: true for now
        let useShell = true;
        const spawnOptions = {
            detached: true, // Keep detached for background potential
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: projectRoot,
            shell: useShell
        };

        // Spawn the process
        // console.warn(`[ProcessManager] Spawning: '${command}' with options: ${JSON.stringify(spawnOptions)}`);
        // Always use the simple spawn with the command string when shell: true
        child = spawn(command, [], spawnOptions); // REVERTED from execa

        pid = child.pid;
        if (pid === undefined) {
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

        // Capture initial output in memory as well (for potential immediate return? Or just for state?)
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
            endTime: null,
            initial_stdout: '', // Will be updated on exit
            initial_stderr: ''  // Will be updated on exit
        };
        await StateManager.addState(newStateEntry);

        // --- Process Event Handling --- 
        const handleExit = async (code, signal) => {
            // console.log(`[ProcessManager] Process ${pid} exited with code: ${code}, signal: ${signal}`);
            const exitCode = code ?? (signal ? 1 : 0); // Assign exit code based on signal if code is null
            const status = (exitCode === 0) ? 'Success' : 'Failure';
            const endTime = new Date().toISOString(); // Capture end time immediately

            // Log details to stderr for debugging
            // console.error(`[FIX_LOG] handleExit PID: ${pid}, code: ${code}, signal: ${signal}, calculatedExitCode: ${exitCode}, calculatedStatus: ${status}`);

            // --- Immediate Status Update ---
            try {
                await StateManager.updateState(pid, {
                    status: status,
                    exit_code: exitCode,
                    // Keep endTime null for now, update later after streams
                });
                // console.log(`[ProcessManager] Updated initial state for PID ${pid} to ${status}`);
            } catch (stateErr) {
                console.error(`[ProcessManager] Error during initial state update for PID ${pid}:`, stateErr);
                // Decide how to handle this - maybe try again later? For now, log and continue.
            }
            // --- End Immediate Status Update ---

            // Clean up data listeners immediately
            child.stdout?.removeListener('data', stdoutListener);
            child.stderr?.removeListener('data', stderrListener);

            // Wait for streams to finish writing
            const streamEndPromises = [];
            if (child.stdout) streamEndPromises.push(new Promise(res => child.stdout.once('end', res)));
            if (child.stderr) streamEndPromises.push(new Promise(res => child.stderr.once('end', res)));

            const streamFinishPromises = [];
            if (stdoutStream) streamFinishPromises.push(new Promise(res => stdoutStream.once('finish', res)));
            if (stderrStream) streamFinishPromises.push(new Promise(res => stderrStream.once('finish', res)));

            // Ensure streams are ended to trigger 'finish'
            stdoutStream?.end();
            stderrStream?.end();

            // HACK: Add a small delay to allow potentially buffered shell output to flush to logs
            await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms

            try {
                await Promise.all(streamEndPromises);
                await Promise.all(streamFinishPromises);
                // console.log(`[ProcessManager] Streams finished for PID ${pid}`);
            } catch (streamErr) {
                console.error(`[ProcessManager] Error waiting for streams to end/finish for PID ${pid}:`, streamErr);
            }

            // Update state AGAIN with final details AFTER streams are done
            try {
                await StateManager.updateState(pid, {
                    // status and exit_code already set
                    endTime: endTime, // Now set the final end time
                    initial_stdout: initialStdout, // Save captured output
                    initial_stderr: initialStderr
                });
                // console.log(`[ProcessManager] Updated final state details for PID ${pid}`);
            } catch (finalStateErr) {
                console.error(`[ProcessManager] Error during final state update for PID ${pid}:`, finalStateErr);
            }
        };

        const handleError = async (err) => {
            console.error(`[ProcessManager] Error in child process ${pid}:`, err);
            // Clean up listeners immediately
            child.stdout?.removeListener('data', stdoutListener);
            child.stderr?.removeListener('data', stderrListener);
            // Attempt to end streams
            stdoutStream?.end();
            stderrStream?.end();
            // Update state to Failure on spawn error
            await StateManager.updateState(pid, {
                status: 'Failure',
                exit_code: null, // Revert to original null
                endTime: new Date().toISOString(),
                initial_stderr: `${initialStderr}\nSpawn/Runtime Error: ${err.message}` // Append error
            });
        };

        child.on('exit', handleExit);
        child.on('error', handleError);

        return {
            pid,
            exit_code: null,
            stdout_log: stdoutLogPath,
            stderr_log: stderrLogPath
        };
    } catch (err) {
        console.error(`[ProcessManager] Error during spawnProcess:`, err);
        // If PID was assigned, try to update state to Failure
        if (pid) {
            try {
                await StateManager.updateState(pid, {
                    status: 'Failure',
                    exit_code: null,
                    endTime: new Date().toISOString(),
                    initial_stderr: `Setup Error: ${err.message}`
                });
            } catch (stateErr) {
                console.error(`[ProcessManager] Error updating state after setup error for PID ${pid}:`, stateErr);
            }
        }
        // Close streams if they were opened
        stdoutStream?.end();
        stderrStream?.end();
        // Re-throw the error
        throw err;
    }
}

/**
 * Kills a process.
 * @param {number} pid The process ID of the process to kill.
 * @returns {Promise<string>} Promise that resolves with a status message when the kill attempt is done.
 */
export async function killProcess(pid) {
    try {
        // Check if process exists using signal 0
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