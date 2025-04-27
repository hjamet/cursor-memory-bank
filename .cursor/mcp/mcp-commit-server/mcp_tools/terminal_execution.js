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
    let cleanupPromise;
    let result = null;

    // Define timeout in milliseconds, using default if not provided or invalid
    const timeoutMs = (timeout && Number.isInteger(timeout) && timeout > 0) ? timeout * 1000 : DEFAULT_TIMEOUT_MS;

    try {
        // Spawn the process using the process manager
        // This now returns pid, log paths, and a completionPromise
        ({ pid, stdout_log, stderr_log, completionPromise, cleanupPromise } = await ProcessManager.spawnProcess(command));

        // Create a timeout promise
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('TIMEOUT')), timeoutMs); // Use specific error
        });

        try {
            // Wait for either the process to complete or the timeout
            await Promise.race([completionPromise, timeoutPromise]);

            // --- Process Finished Before Timeout --- 
            // completionPromise resolved first

            // Explicitly wait for cleanup (state/log finalization) to complete
            await cleanupPromise;

            const finalState = await StateManager.getState(pid); // Get final state after handleClose finished
            if (!finalState) {
                throw new Error(`Process ${pid} finished but final state not found after cleanup.`);
            }

            // *** INCREASED DELAY before reading logs ***
            await new Promise(resolve => setTimeout(resolve, 150)); // 150ms delay

            // Initialize variables OUTSIDE try blocks
            let stdoutContent = '';
            let stderrContent = '';

            // Read the full logs
            try {
                stdoutContent = await Logger.readLogLines(stdout_log, -1);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stdout log (after delay) for completed PID ${pid}:`, logErr.message);
            }
            try {
                stderrContent = await Logger.readLogLines(stderr_log, -1);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stderr log (after delay) for completed PID ${pid}:`, logErr.message);
            }

            // Construct result using logs read *after* delay and final state from *after*
            result = {
                pid,
                cwd: finalState.cwd ?? null,
                status: finalState.status,
                exit_code: finalState.exit_code,
                stdout: typeof stdoutContent === 'string' ? stdoutContent : '', // Ensure string
                stderr: typeof stderrContent === 'string' ? stderrContent : ''  // Ensure string
            };

        } catch (raceError) {
            // Check if the error was our specific timeout error
            if (raceError.message === 'TIMEOUT') {
                // Timeout occurred, process is still running (or finished after timeout began)
                // console.log(`[ExecuteCommand] Timeout reached for PID ${pid}. Process continues.`);
                const currentState = StateManager.findStateByPid(pid); // Get current (likely Running) state

                // Initialize variables OUTSIDE try blocks
                let partialStdout = '';
                let partialStderr = '';

                // Read the CURRENT (partial) logs
                try {
                    partialStdout = await Logger.readLogLines(stdout_log, -1); // Read all available lines
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading partial stdout log for running PID ${pid}:`, logErr.message);
                }
                try {
                    partialStderr = await Logger.readLogLines(stderr_log, -1); // Read all available lines
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading partial stderr log for running PID ${pid}:`, logErr.message);
                }

                result = {
                    pid,
                    cwd: currentState?.cwd ?? null,
                    status: currentState?.status ?? 'Running',
                    exit_code: null,
                    stdout: typeof partialStdout === 'string' ? partialStdout : '', // Ensure string
                    stderr: typeof partialStderr === 'string' ? partialStderr : ''  // Ensure string
                };
            } else {
                // Another error occurred (e.g., from completionPromise rejecting)
                // Wait for cleanup to potentially capture the error state
                const cleanupResult = await cleanupPromise;
                const errorState = await StateManager.getState(pid);

                // Initialize variable OUTSIDE try block
                let stderrReadContent = '';
                try {
                    stderrReadContent = await Logger.readLogLines(stderr_log, -1);
                } catch (logErr) { }

                let combinedStderr = (cleanupResult?.error || raceError)?.message || 'Unknown error';
                if (typeof stderrReadContent === 'string' && stderrReadContent.length > 0) {
                    combinedStderr += "\n--- STDERR LOG ---\n" + stderrReadContent;
                }


                result = {
                    pid,
                    cwd: errorState?.cwd ?? null,
                    status: errorState?.status ?? 'Failure',
                    exit_code: errorState?.exit_code,
                    stdout: '', // Keep empty on error for now
                    stderr: typeof combinedStderr === 'string' ? combinedStderr : '' // Ensure string
                };
            }
        }

        // Return the constructed result (full on completion, partial on timeout, error info on error)
        return { content: [{ type: "text", text: JSON.stringify(result) }] };

    } catch (error) {
        console.error('[ExecuteCommand] Top-level Error:', error);
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
                console.error(`[ExecuteCommand] Error updating state after top-level error for PID ${pid}:`, stateErr);
            }
        }
        // Return an error structure consistent with other results if possible
        const errorResult = {
            pid: pid || null,
            cwd: null,
            status: 'Failure',
            exit_code: null,
            stdout: '',
            stderr: `Failed to execute command: ${error.message}`
        };
        return { content: [{ type: "text", text: JSON.stringify(errorResult) }] };
        // Or rethrow? Let's return a structured error.
        // throw new Error(`Failed to execute command: ${error.message}`);
    }
}

export { }; // Add empty export to make it a module 