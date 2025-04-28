import * as StateManager from '../lib/state_manager.js';
// Import specific functions for clarity
import { readLogChars } from '../lib/logger.js';

// Define character limit
const MAX_CHARS_OUTPUT = 20000;

/**
 * MCP Tool handler for 'get_terminal_output'.
 * Retrieves NEW output (since last call) for a specific terminal process based on character count.
 */
export async function handleGetTerminalOutput({ pid /* lines parameter is deprecated/ignored */ }) {
    const state = StateManager.findStateByPid(pid);

    if (!state) {
        throw new Error(`Terminal process with PID ${pid} not found.`);
    }

    // Ensure read indices exist, default to 0 if somehow missing (e.g., older state files)
    const stdoutStartIndex = state.stdout_read_index ?? 0;
    const stderrStartIndex = state.stderr_read_index ?? 0;

    let newStdoutContent = '';
    let newStderrContent = '';
    let newStdoutIndex = stdoutStartIndex;
    let newStderrIndex = stderrStartIndex;

    try {
        newStdoutContent = await readLogChars(state.stdout_log, stdoutStartIndex, MAX_CHARS_OUTPUT);
        newStdoutIndex = stdoutStartIndex + Buffer.byteLength(newStdoutContent, 'utf8'); // Update index based on bytes read
    } catch (logReadErr) {
        console.error(`[GetOutput] Error reading stdout log chars for PID ${pid}:`, logReadErr);
    }

    try {
        newStderrContent = await readLogChars(state.stderr_log, stderrStartIndex, MAX_CHARS_OUTPUT);
        newStderrIndex = stderrStartIndex + Buffer.byteLength(newStderrContent, 'utf8'); // Update index based on bytes read
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

    const response = {
        pid: state.pid,
        cwd: state.cwd ?? null,
        stdout: newStdoutContent,
        stderr: newStderrContent
    };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 