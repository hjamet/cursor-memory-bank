import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
// Import specific logger functions
import { readLogLines, deleteLogFiles } from '../lib/logger.js';

// Default timeout in milliseconds (10 seconds)
const DEFAULT_TIMEOUT_MS = 10000;

// Define maximum lines for output retrieval
const MAX_RUNNING_PROCESSES = 10; // Limit concurrent processes

/**
 * MCP Tool handler for 'execute_command'.
 * Spawns a command, manages state, handles optional terminal reuse,
 * and returns immediately with full results if command finishes within timeout.
 * Returns the last N lines of output based on lines_to_read parameter.
 */
export async function handleExecuteCommand({ command, working_directory, reuse_terminal, timeout, lines_to_read = 300 }) {
    if (timeout > 300) {
        const errorResult = {
            pid: null,
            cwd: working_directory || null,
            status: 'Failure',
            exit_code: null,
            stdout: '',
            stderr: 'Error: Timeout cannot exceed 300 seconds (5 minutes).'
        };
        return { content: [{ type: "text", text: JSON.stringify(errorResult) }] };
    }

    // Handle terminal reuse: Find a finished terminal state index
    if (reuse_terminal) {
        const reusableIndex = StateManager.findReusableTerminalIndex();
        if (reusableIndex !== -1) {
            const stateToClean = StateManager.getState()[reusableIndex];
            if (stateToClean) {
                await StateManager.removeStateByIndex(reusableIndex);
                await deleteLogFiles(stateToClean);
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

            // Read the last N lines from both logs
            try {
                stdoutContent = await readLogLines(stdout_log, lines_to_read);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stdout log for completed PID ${pid}:`, logErr.message);
            }
            try {
                stderrContent = await readLogLines(stderr_log, lines_to_read);
            } catch (logErr) {
                console.warn(`[ExecuteCommand] Error reading stderr log for completed PID ${pid}:`, logErr.message);
            }

            result = {
                pid,
                cwd: state?.cwd ?? null,
                status: finalStatus,
                exit_code: finalExitCode,
                stdout: typeof stdoutContent === 'string' ? stdoutContent : '',
                stderr: typeof stderrContent === 'string' ? stderrContent : ''
            };

        } catch (raceError) {
            if (raceError.message === 'TIMEOUT') {
                // --- Timeout Occurred --- 
                const currentState = StateManager.findStateByPid(pid);

                let stdoutContent = '';
                let stderrContent = '';

                // Read the last N lines from both logs for running process
                try {
                    stdoutContent = await readLogLines(stdout_log, lines_to_read);
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading stdout log for running PID ${pid}:`, logErr.message);
                }
                try {
                    stderrContent = await readLogLines(stderr_log, lines_to_read);
                } catch (logErr) {
                    console.warn(`[ExecuteCommand] Error reading stderr log for running PID ${pid}:`, logErr.message);
                }

                result = {
                    pid,
                    cwd: currentState?.cwd ?? null,
                    status: currentState?.status ?? 'Running',
                    exit_code: null,
                    stdout: typeof stdoutContent === 'string' ? stdoutContent : '',
                    stderr: typeof stderrContent === 'string' ? stderrContent : ''
                };
            } else {
                // --- Another Error Occurred --- 
                const cleanupResult = await cleanupPromise;
                const errorState = await StateManager.findStateByPid(pid);

                let stderrContent = '';
                try {
                    // Read stderr log for error case
                    stderrContent = await readLogLines(stderr_log, lines_to_read);
                } catch (logErr) { /* Ignore log read error here */ }

                let combinedStderr = (cleanupResult?.error || raceError)?.message || 'Unknown error';
                if (typeof stderrContent === 'string' && stderrContent.length > 0) {
                    combinedStderr += "\n--- STDERR LOG ---\n" + stderrContent;
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