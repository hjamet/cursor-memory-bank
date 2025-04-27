import * as StateManager from '../lib/state_manager.js';
import * as Logger from '../lib/logger.js';

/**
 * MCP Tool handler for 'get_terminal_output'.
 * Retrieves output for a specific terminal process.
 */
export async function handleGetTerminalOutput({ pid, lines = 100 }) {
    const state = StateManager.findStateByPid(pid);

    if (!state) {
        throw new Error(`Terminal process with PID ${pid} not found.`);
    }

    let stdoutContent = '';
    let stderrContent = '';

    // Always read from log files to avoid timing issues with state updates
    // console.log(`[GetOutput] PID ${pid} (${state.status}). Reading last ${lines} lines from logs.`);
    try {
        stdoutContent = await Logger.readLogLines(state.stdout_log, lines);
    } catch (logReadErr) {
        console.error(`[GetOutput] Error reading stdout log for PID ${pid}:`, logReadErr);
        // Keep stdoutContent empty or consider a specific error message
    }
    try {
        stderrContent = await Logger.readLogLines(state.stderr_log, lines);
    } catch (logReadErr) {
        console.error(`[GetOutput] Error reading stderr log for PID ${pid}:`, logReadErr);
        // Keep stderrContent empty or consider a specific error message
    }

    const response = {
        stdout: stdoutContent,
        stderr: stderrContent
    };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 