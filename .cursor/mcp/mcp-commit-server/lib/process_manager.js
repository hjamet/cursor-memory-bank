import { spawn } from 'child_process';
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
    let child;
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

        // Basic shell detection (can be improved)
        // For now, replicating the core idea from server.js - use shell: true by default
        // TODO: Refine shell/argument parsing if needed, maybe move into a separate utility
        let useShell = true;
        let executable = command;
        let args = [];
        const spawnOptions = {
            detached: true, // Keep detached for background potential
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: projectRoot,
            shell: useShell
        };

        // Spawn the process
        // console.warn(`[ProcessManager] Spawning: '${command}' with options: ${JSON.stringify(spawnOptions)}`);
        if (useShell) {
            child = spawn(command, [], spawnOptions);
        } else {
            child = spawn(executable, args, spawnOptions);
        }

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
                exit_code: null, // Or maybe 1?
                endTime: new Date().toISOString(),
                initial_stderr: initialStderr + `\nSpawn/Runtime Error: ${err.message}` // Append error
            });
        };

        child.on('exit', handleExit);
        child.on('error', handleError);

        // Detach? The original had detached: true and unref() on timeout.
        // For now, let's not unref automatically. The caller can decide.
        // child.unref(); // Example: if we wanted to allow parent to exit

        // Return minimal info immediately
        return {
            pid,
            stdout_log: stdoutLogPath,
            stderr_log: stderrLogPath,
        };

    } catch (error) {
        console.error('[ProcessManager] Error spawning process:', error);
        // Clean up potentially created streams if error happened after creation
        stdoutStream?.end();
        stderrStream?.end();
        // Don't try to update state as PID might not exist
        throw new Error(`Failed to spawn process: ${error.message}`);
    }
}

/**
 * Sends a termination signal to a process.
 * Attempts SIGTERM first, then SIGKILL after a short delay if the process still exists.
 * @param {number} pid The process ID to kill.
 * @returns {Promise<string>} A status message indicating the outcome.
 */
export async function killProcess(pid) {
    let terminationStatus = `Attempting to terminate PID ${pid}.`;
    try {
        process.kill(pid, 'SIGTERM');
        terminationStatus = `Sent SIGTERM to PID ${pid}.`;
        // Wait briefly to allow graceful shutdown
        await new Promise(resolve => setTimeout(resolve, 200));

        // Check if process still exists
        try {
            process.kill(pid, 0); // Check if process exists
            // Process still exists, send SIGKILL
            try {
                process.kill(pid, 'SIGKILL');
                terminationStatus = `Sent SIGTERM, then SIGKILL to PID ${pid}.`;
            } catch (sigkillError) {
                if (sigkillError.code === 'ESRCH') {
                    terminationStatus = `Sent SIGTERM to PID ${pid}; process exited before SIGKILL.`;
                } else {
                    throw sigkillError; // Rethrow unexpected SIGKILL error
                }
            }
        } catch (checkError) {
            if (checkError.code === 'ESRCH') {
                terminationStatus = `Sent SIGTERM to PID ${pid}; process confirmed exited.`;
            } else {
                throw checkError; // Rethrow unexpected check error
            }
        }
    } catch (error) {
        if (error.code === 'ESRCH') {
            terminationStatus = `Process PID ${pid} already exited before termination attempt.`;
        } else if (error.code === 'EPERM') {
            console.error(`[ProcessManager] Permission error sending signal to PID ${pid}.`);
            terminationStatus = `Permission error trying to terminate PID ${pid}.`;
        } else {
            console.error(`[ProcessManager] Error sending termination signal to PID ${pid}:`, error);
            terminationStatus = `Error during termination attempt for PID ${pid}: ${error.message}`;
        }
    }
    // Note: This function only attempts to kill. State update happens in exit handler.
    // Consider if state should be updated to 'Terminated'/'Stopped' here immediately?
    // For now, rely on the exit handler triggered by the kill signal.
    return terminationStatus;
} 