import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import { readLogChars, deleteLogFiles } from '../lib/logger.js';

// Define character limit for final output retrieval
const MAX_CHARS_STOP = 20000;

/**
 * MCP Tool handler for 'stop_terminal_command'.
 * Stops specified terminal processes and retrieves final NEW output (since last call) if requested.
 */
export async function handleStopTerminalCommand({ pids, lines = 0 /* If lines > 0, retrieve final chars */ }) {
    const results = [];

    for (const pid of pids) {
        const state = StateManager.findStateByPid(pid);
        let stdoutContent = '';
        let stderrContent = '';
        let stopStatus = '';

        // Only attempt to read logs if lines > 0 AND state exists
        if (lines > 0 && state) {
            const stdoutStartIndex = state.stdout_read_index ?? 0;
            const stderrStartIndex = state.stderr_read_index ?? 0;
            let newStdoutIndex = stdoutStartIndex;
            let newStderrIndex = stderrStartIndex;

            try {
                stdoutContent = await readLogChars(state.stdout_log, stdoutStartIndex, MAX_CHARS_STOP);
                newStdoutIndex = stdoutStartIndex + Buffer.byteLength(stdoutContent, 'utf8');
            } catch (logReadErr) {
                stdoutContent = `[Stdout Log Read Error: ${logReadErr.code || logReadErr.message}]`;
            }
            try {
                stderrContent = await readLogChars(state.stderr_log, stderrStartIndex, MAX_CHARS_STOP);
                newStderrIndex = stderrStartIndex + Buffer.byteLength(stderrContent, 'utf8');
            } catch (logReadErr) {
                stderrContent = `[Stderr Log Read Error: ${logReadErr.code || logReadErr.message}]`;
            }

            // Update state with new read indices *before* killing/cleanup (best effort)
            if (newStdoutIndex > stdoutStartIndex || newStderrIndex > stderrStartIndex) {
                StateManager.updateState(pid, {
                    stdout_read_index: newStdoutIndex,
                    stderr_read_index: newStderrIndex
                }).catch(err => console.error(`[StopCmd] Error updating final state indices for PID ${pid}:`, err));
            }
        } else if (lines > 0) {
            // State not found, cannot read logs
            stdoutContent = "[State not found for log reading]";
            stderrContent = "[State not found for log reading]";
        }

        // Attempt to kill the process
        try {
            stopStatus = await ProcessManager.killProcess(pid);
        } catch (killError) {
            stopStatus = `Error during kill attempt: ${killError.message}`;
            // Ensure state is still cleaned up even if kill fails
        }

        // Attempt to clean up state and log files
        try {
            await deleteLogFiles(pid); // Use logger's delete function
            await StateManager.removeStateByPid(pid);
            // Append success only if kill didn't report an error initially
            if (!stopStatus.startsWith('Error')) {
                stopStatus += " Log cleanup successful.";
            }
        } catch (cleanupError) {
            console.error(`[StopCmd] Error during cleanup for PID ${pid}:`, cleanupError);
            stopStatus += " Error during cleanup.";
        }

        results.push({
            pid: pid,
            status: stopStatus,
            stdout: stdoutContent, // Include content read (or error message)
            stderr: stderrContent
        });
    }

    return { content: [{ type: "text", text: JSON.stringify(results) }] };
}

export { }; // Add empty export to make it a module 