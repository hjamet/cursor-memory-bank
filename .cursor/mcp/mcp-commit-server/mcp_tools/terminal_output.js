import * as StateManager from '../lib/state_manager.js';
// Import specific functions for clarity
import { readLogChars, readLastLogChars } from '../lib/logger.js';

// Define character limit
const MAX_CHARS_OUTPUT = 20000;

/**
 * MCP Tool handler for 'get_terminal_output'.
 * Retrieves output for a specific terminal process.
 * If from_beginning is true, reads all output from the start.
 * If from_beginning is false (default), reads only NEW output since last call.
 */
export async function handleGetTerminalOutput({ pid, from_beginning = false /* lines parameter is deprecated/ignored */ }) {
    const state = StateManager.findStateByPid(pid);

    if (!state) {
        throw new Error(`Terminal process with PID ${pid} not found.`);
    }

    let stdoutContent = '';
    let stderrContent = '';

    if (from_beginning) {
        // Read all output from the beginning (like get_terminal_status does)
        try {
            stdoutContent = await readLastLogChars(state.stdout_log, Number.MAX_SAFE_INTEGER);
        } catch (logReadErr) {
            console.error(`[GetOutput] Error reading full stdout log for PID ${pid}:`, logReadErr);
        }

        try {
            stderrContent = await readLastLogChars(state.stderr_log, Number.MAX_SAFE_INTEGER);
        } catch (logReadErr) {
            console.error(`[GetOutput] Error reading full stderr log for PID ${pid}:`, logReadErr);
        }
    } else {
        // Original behavior: read only new content since last call
        // Ensure read indices exist, default to 0 if somehow missing (e.g., older state files)
        const stdoutStartIndex = state.stdout_read_index ?? 0;
        const stderrStartIndex = state.stderr_read_index ?? 0;

        let newStdoutIndex = stdoutStartIndex;
        let newStderrIndex = stderrStartIndex;

        try {
            stdoutContent = await readLogChars(state.stdout_log, stdoutStartIndex, MAX_CHARS_OUTPUT);
            newStdoutIndex = stdoutStartIndex + Buffer.byteLength(stdoutContent, 'utf8'); // Update index based on bytes read
        } catch (logReadErr) {
            console.error(`[GetOutput] Error reading stdout log chars for PID ${pid}:`, logReadErr);
        }

        try {
            stderrContent = await readLogChars(state.stderr_log, stderrStartIndex, MAX_CHARS_OUTPUT);
            newStderrIndex = stderrStartIndex + Buffer.byteLength(stderrContent, 'utf8'); // Update index based on bytes read
        } catch (logReadErr) {
            console.error(`[GetOutput] Error reading stderr log chars for PID ${pid}:`, logReadErr);
        }

        // Update state with new read indices *asynchronously* (don't wait)
        if (newStdoutIndex > stdoutStartIndex || newStderrIndex > stderrStartIndex) {
            StateManager.updateState(pid, {
                stdout_read_index: newStdoutIndex,
                stderr_read_index: newStderrIndex
            }).catch(err => console.error(`[GetOutput] Error updating state indices for PID ${pid}:`, err));
        }
    }

    const response = {
        pid: state.pid,
        cwd: state.cwd ?? null,
        stdout: stdoutContent,
        stderr: stderrContent
    };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 