import * as StateManager from '../lib/state_manager.js';
// Import specific functions for clarity
import { readLogLines } from '../lib/logger.js';

/**
 * MCP Tool handler for 'get_terminal_output'.
 * Retrieves the last N lines of output for a specific terminal process.
 */
export async function handleGetTerminalOutput({ pid, lines_to_read = 300 }) {
    const state = StateManager.findStateByPid(pid);

    if (!state) {
        throw new Error(`Terminal process with PID ${pid} not found.`);
    }

    let stdoutContent = '';
    let stderrContent = '';

    // Read the last N lines from both stdout and stderr logs
    try {
        stdoutContent = await readLogLines(state.stdout_log, lines_to_read);
    } catch (logReadErr) {
        console.error(`[GetOutput] Error reading stdout log for PID ${pid}:`, logReadErr);
    }

    try {
        stderrContent = await readLogLines(state.stderr_log, lines_to_read);
    } catch (logReadErr) {
        console.error(`[GetOutput] Error reading stderr log for PID ${pid}:`, logReadErr);
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