import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import * as Logger from '../lib/logger.js';

/**
 * MCP Tool handler for 'stop_terminal_command'.
 * Attempts to stop processes, retrieves final output, and cleans up state/logs.
 */
export async function handleStopTerminalCommand({ pids, lines = 100 }) {
    const results = [];

    for (const pid of pids) {
        let stdoutContent = `(Could not read stdout for PID ${pid})`;
        let stderrContent = `(Could not read stderr for PID ${pid})`;
        let finalStatus = `Processing PID ${pid}.`;

        const state = StateManager.findStateByPid(pid);

        if (!state) {
            finalStatus = `PID ${pid} not found in state.`;
            results.push({ pid, status: finalStatus, stdout: '', stderr: '' });
            continue;
        }

        // 1. Read final logs before attempting kill
        try {
            stdoutContent = await Logger.readLogLines(state.stdout_log, lines);
            stderrContent = await Logger.readLogLines(state.stderr_log, lines);
        } catch (readErr) {
            console.warn(`[StopCommand] Error reading logs for PID ${pid}:`, readErr);
            // Keep default error message for logs
        }

        // 2. Attempt termination using process manager
        const terminationMsg = await ProcessManager.killProcess(pid);

        // 3. Remove state entry using state manager
        await StateManager.removeStateByPid(pid);
        // Note: The killProcess relies on the process 'exit' handler (setup in spawnProcess)
        // to update the state to Success/Failure before it's removed here.
        // If killProcess is called before the exit event fires, the state might be removed while 'Running'.
        // This is acceptable as the process is being forcefully stopped.

        // 4. Delete log files
        let logCleanupMsg = 'Log cleanup successful.';
        try {
            await Logger.deleteLogFiles(state);
        } catch (logErr) {
            logCleanupMsg = 'Log cleanup failed.';
            console.warn(`[StopCommand] Error deleting logs for PID ${pid}:`, logErr);
        }

        // Combine status messages
        finalStatus = `${terminationMsg} ${logCleanupMsg}`;

        results.push({ pid, status: finalStatus, stdout: stdoutContent, stderr: stderrContent });
    }

    // Persist state changes made by removeStateByPid (already handled inside StateManager)

    // Return results for all processed PIDs
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
} 