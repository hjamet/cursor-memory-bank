import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import * as Logger from '../lib/logger.js';

// Default timeout in milliseconds (10 seconds)
const DEFAULT_TIMEOUT_MS = 10000;

/**
 * MCP Tool handler for 'execute_command'.
 * Spawns a command, manages state, handles optional terminal reuse,
 * and returns immediately with full results if command finishes within timeout.
 */
export async function handleExecuteCommand({ command, reuse_terminal, timeout /* timeout is in seconds */ }) {
    // Handle terminal reuse: Find a finished terminal state index
    if (reuse_terminal) {
        const reusableIndex = StateManager.findReusableTerminalIndex();
        if (reusableIndex !== -1) {
            // Get the state before removing it
            const stateToClean = StateManager.getState()[reusableIndex];
            if (stateToClean) {
                // Remove state first
                await StateManager.removeStateByIndex(reusableIndex);
                // Then delete logs (best effort)
                await Logger.deleteLogFiles(stateToClean);
                // console.log(`[ExecuteCommand] Reused terminal slot from PID ${stateToClean.pid}`);
            }
        }
    }

    let pid;
    let stdout_log;
    let stderr_log;
    let completionPromise;
    let earlyResult = null;

    // Define timeout in milliseconds, using default if not provided or invalid
    const timeoutMs = (timeout && Number.isInteger(timeout) && timeout > 0) ? timeout * 1000 : DEFAULT_TIMEOUT_MS;

    try {
        // Spawn the process using the process manager
        // This now returns pid, log paths, and a completionPromise
        ({ pid, stdout_log, stderr_log, completionPromise } = await ProcessManager.spawnProcess(command));

        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('TIMEOUT')), timeoutMs); // Use specific error
        });

        try {
            // Wait for either the process to complete or the timeout
            await Promise.race([completionPromise, timeoutPromise]);

            // If we reach here, completionPromise resolved first (process finished)
            const finalState = await StateManager.getState(pid); // Get final state after handleClose finished
            if (!finalState) {
                // Should theoretically not happen if completionPromise resolved, but handle defensively
                throw new Error(`Process ${pid} finished but final state not found.`);
            }

            // Read the full logs
            let stdoutContent = '';
            let stderrContent = '';
            try {
                stdoutContent = await Logger.readLogLines(stdout_log, -1); // Read all lines
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stdout log for completed PID ${pid}:`, logErr.message);
            }
            try {
                stderrContent = await Logger.readLogLines(stderr_log, -1); // Read all lines
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stderr log for completed PID ${pid}:`, logErr.message);
            }

            earlyResult = {
                pid,
                cwd: finalState.cwd ?? null,
                status: finalState.status, // Should be Success or Failure
                exit_code: finalState.exit_code, // Should be the actual exit code
                stdout: stdoutContent,
                stderr: stderrContent
            };

        } catch (raceError) {
            // Check if the error was our specific timeout error
            if (raceError.message === 'TIMEOUT') {
                // Timeout occurred, process is still running (or finished after timeout began)
                // Return basic info, allowing background continuation
                // console.log(`[ExecuteCommand] Timeout reached for PID ${pid}. Process continues.`);
                const currentState = StateManager.findStateByPid(pid); // Get current (likely Running) state
                earlyResult = {
                    pid,
                    cwd: currentState?.cwd ?? null,
                    stdout: '',
                    stderr: '',
                    exit_code: null
                };
            } else {
                // Another error occurred (e.g., from completionPromise rejecting)
                throw raceError; // Re-throw original error
            }
        }

        // Return either the full early result or the basic PID info
        return { content: [{ type: "text", text: JSON.stringify(earlyResult) }] };

    } catch (error) {
        console.error('[ExecuteCommand] Error:', error);
        // If spawnProcess failed, pid might not be set
        // If Promise.race failed with non-timeout error, we might have a pid
        // Attempt to clean up state if PID exists and error happened after spawn
        if (pid) {
            try {
                // Update state to Failure if not already finalized by process_manager
                const state = StateManager.findStateByPid(pid);
                if (state && (state.status === 'Running' || !state.endTime)) {
                    await StateManager.updateState(pid, {
                        status: 'Failure',
                        exit_code: state.exit_code ?? null, // Keep code if handleExit set it
                        endTime: state.endTime ?? new Date().toISOString(),
                    });
                }
            } catch (stateErr) {
                console.error(`[ExecuteCommand] Error updating state after error for PID ${pid}:`, stateErr);
            }
        }
        throw new Error(`Failed to execute command: ${error.message}`);
    }
}

export { }; // Add empty export to make it a module 