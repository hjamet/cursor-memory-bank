import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import * as Logger from '../lib/logger.js';

/**
 * MCP Tool handler for 'stop_terminal_command'.
 * Stops specified terminal processes and retrieves final output if requested.
 */
export async function handleStopTerminalCommand({ pids, lines = 0 /* Default to 0 lines = don't read logs */ }) {
    const results = [];

    for (const pid of pids) {
        const state = StateManager.findStateByPid(pid);
        let stdoutContent = '';
        let stderrContent = '';
        let stopStatus = '';

        // Only attempt to read logs if lines > 0 AND log paths exist
        if (lines > 0 && state) {
            try {
                // Check if log paths are actually strings before reading
                if (typeof state.stdout_log === 'string') {
                    stdoutContent = await Logger.readLogLines(state.stdout_log, lines);
                } else {
                    stdoutContent = "[Log path not available]";
                }
            } catch (logReadErr) {
                stdoutContent = `[Stdout Log Read Error: ${logReadErr.code || logReadErr.message}]`;
            }
            try {
                if (typeof state.stderr_log === 'string') {
                    stderrContent = await Logger.readLogLines(state.stderr_log, lines);
                } else {
                    stderrContent = "[Log path not available]";
                }
            } catch (logReadErr) {
                stderrContent = `[Stderr Log Read Error: ${logReadErr.code || logReadErr.message}]`;
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
        }

        // Attempt to clean up state and potentially log files (if they ever existed)
        try {
            // Even if logs weren't used, try deleting based on PID just in case
            await Logger.deleteLogFiles(pid);
            await StateManager.removeStateByPid(pid);
            stopStatus += " Log cleanup successful.";
        } catch (cleanupError) {
            stopStatus += " Error during cleanup.";
        }

        results.push({
            pid: pid,
            status: stopStatus,
            stdout: stdoutContent, // Include content (or error) if reading was attempted
            stderr: stderrContent
        });
    }

    return { content: [{ type: "text", text: JSON.stringify(results) }] };
}

export { }; // Add empty export to make it a module 