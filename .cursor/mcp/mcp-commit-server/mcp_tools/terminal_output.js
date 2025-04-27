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

    // Prioritize reading captured initial output from state if process has finished
    if (['Success', 'Failure', 'Stopped', 'Terminated'].includes(state.status)) {
        // console.log(`[GetOutput] PID ${pid} finished (${state.status}). Returning captured state output.`);
        stdoutContent = state.initial_stdout || '';
        stderrContent = state.initial_stderr || '';
        // Optionally append recent log lines if needed, but primary source is captured state
        // stdoutContent += "\n--- Log File Tail ---\n" + await Logger.readLogLines(state.stdout_log, lines);
        // stderrContent += "\n--- Log File Tail ---\n" + await Logger.readLogLines(state.stderr_log, lines);
    } else {
        // Process is still running (or status unknown), read from log files
        // console.log(`[GetOutput] PID ${pid} running (${state.status}). Reading last ${lines} lines from logs.`);
        stdoutContent = await Logger.readLogLines(state.stdout_log, lines);
        stderrContent = await Logger.readLogLines(state.stderr_log, lines);
    }

    const response = {
        stdout: stdoutContent,
        stderr: stderrContent
    };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 