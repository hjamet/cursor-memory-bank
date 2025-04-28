import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
// Import specific logger functions
import { readLogChars, deleteLogFiles } from '../lib/logger.js';

// Default timeout in milliseconds (10 seconds)
const DEFAULT_TIMEOUT_MS = 10000;
// Character limit for partial output on timeout
const MAX_CHARS_EXEC_PARTIAL = 3000;

/**
 * MCP Tool handler for 'execute_command'.
 * Spawns a command, manages state, handles optional terminal reuse,
 * and returns immediately with full results if command finishes within timeout.
 * Retrieves NEW characters on timeout, or ALL characters on completion.
 */
export async function handleExecuteCommand({ command, working_directory, reuse_terminal, timeout /* timeout is in seconds */ }) {

    // Handle terminal reuse: Find a finished terminal state index
    if (reuse_terminal) {
        const reusableIndex = StateManager.findReusableTerminalIndex();
        if (reusableIndex !== -1) {
            const stateToClean = StateManager.getState()[reusableIndex];
            if (stateToClean) {
                await StateManager.removeStateByIndex(reusableIndex);
                await deleteLogFiles(stateToClean); // Use imported function
            }
        }
    }

    let pid;
    let stdout_log;
    let stderr_log;
    let completionPromise;
    let cleanupPromise;
    let result = null;

    const timeoutMs = (timeout && Number.isInteger(timeout) && timeout > 0) ? timeout * 1000 : DEFAULT_TIMEOUT_MS;

    try {
        ({ pid, stdout_log, stderr_log, completionPromise, cleanupPromise } = await ProcessManager.spawnProcess(command, working_directory));

        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('TIMEOUT')), timeoutMs);
        });

        try {
            const completionResult = await Promise.race([completionPromise, timeoutPromise]);

            // --- Process Finished Before Timeout --- 
            await cleanupPromise;
            const { code: finalExitCode, signal } = completionResult;
            const finalStatus = (finalExitCode === 0) ? 'Success' : 'Failure';
            const state = StateManager.findStateByPid(pid);

            let stdoutContent = '';
            let stderrContent = '';

            // Read the *entire* log content using char reader
            try {
                // Read all chars from start index 0
                stdoutContent = await readLogChars(stdout_log, 0, Number.MAX_SAFE_INTEGER);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading full stdout log for completed PID ${pid}:`, logErr.message);
            }
            try {
                stderrContent = await readLogChars(stderr_log, 0, Number.MAX_SAFE_INTEGER);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading full stderr log for completed PID ${pid}:`, logErr.message);
            }

            result = {
                pid,
                cwd: state?.cwd ?? null,
                status: finalStatus,
                exit_code: finalExitCode,
                stdout: typeof stdoutContent === 'string' ? stdoutContent : '',
                stderr: typeof stderrContent === 'string' ? stderrContent : ''
            };
            // No index update needed for completed process

        } catch (raceError) {
            if (raceError.message === 'TIMEOUT') {
                // --- Timeout Occurred --- 
                const currentState = StateManager.findStateByPid(pid);

                // Ensure read indices exist
                const stdoutStartIndex = currentState?.stdout_read_index ?? 0;
                const stderrStartIndex = currentState?.stderr_read_index ?? 0;
                let newStdoutContent = '';
                let newStderrContent = '';
                let newStdoutIndex = stdoutStartIndex;
                let newStderrIndex = stderrStartIndex;

                // Read *new* partial logs using char reader
                try {
                    newStdoutContent = await readLogChars(stdout_log, stdoutStartIndex, MAX_CHARS_EXEC_PARTIAL);
                    newStdoutIndex = stdoutStartIndex + Buffer.byteLength(newStdoutContent, 'utf8');
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading partial stdout log for running PID ${pid}:`, logErr.message);
                }
                try {
                    newStderrContent = await readLogChars(stderr_log, stderrStartIndex, MAX_CHARS_EXEC_PARTIAL);
                    newStderrIndex = stderrStartIndex + Buffer.byteLength(newStderrContent, 'utf8');
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading partial stderr log for running PID ${pid}:`, logErr.message);
                }

                // Update state with new read indices *asynchronously*
                if (newStdoutIndex > stdoutStartIndex || newStderrIndex > stderrStartIndex) {
                    StateManager.updateState(pid, {
                        stdout_read_index: newStdoutIndex,
                        stderr_read_index: newStderrIndex
                    }).catch(err => console.error(`[ExecuteCommand] Error updating state indices on timeout for PID ${pid}:`, err));
                }

                result = {
                    pid,
                    cwd: currentState?.cwd ?? null,
                    status: currentState?.status ?? 'Running',
                    exit_code: null,
                    stdout: typeof newStdoutContent === 'string' ? newStdoutContent : '',
                    stderr: typeof newStderrContent === 'string' ? newStderrContent : ''
                };
            } else {
                // --- Another Error Occurred --- 
                // (Error handling logic remains mostly the same, reading full stderr at the end)
                const cleanupResult = await cleanupPromise;
                const errorState = await StateManager.findStateByPid(pid); // Fetch state by PID

                let stderrReadContent = '';
                try {
                    // Read full stderr log using char reader on error
                    stderrReadContent = await readLogChars(stderr_log, 0, Number.MAX_SAFE_INTEGER);
                } catch (logErr) { /* Ignore log read error here */ }

                let combinedStderr = (cleanupResult?.error || raceError)?.message || 'Unknown error';
                if (typeof stderrReadContent === 'string' && stderrReadContent.length > 0) {
                    combinedStderr += "\n--- STDERR LOG ---\n" + stderrReadContent;
                }

                result = {
                    pid,
                    cwd: errorState?.cwd ?? null,
                    status: errorState?.status ?? 'Failure',
                    exit_code: errorState?.exit_code,
                    stdout: '',
                    stderr: typeof combinedStderr === 'string' ? combinedStderr : ''
                };
            }
        }

        return { content: [{ type: "text", text: JSON.stringify(result) }] };

    } catch (error) {
        // (Top-level error handling remains the same)
        console.error('[ExecuteCommand] Top-level Error:', error);
        if (pid) {
            try {
                const state = StateManager.findStateByPid(pid);
                if (state && (state.status === 'Running' || !state.endTime)) {
                    await StateManager.updateState(pid, {
                        status: 'Failure',
                        exit_code: state.exit_code ?? null,
                        endTime: state.endTime ?? new Date().toISOString(),
                    });
                }
            } catch (stateErr) {
                console.error(`[ExecuteCommand] Error updating state after top-level error for PID ${pid}:`, stateErr);
            }
        }
        const errorResult = {
            pid: pid || null,
            cwd: null,
            status: 'Failure',
            exit_code: null,
            stdout: '',
            stderr: `Failed to execute command: ${error.message}`
        };
        return { content: [{ type: "text", text: JSON.stringify(errorResult) }] };
    }
}

export { }; // Add empty export to make it a module