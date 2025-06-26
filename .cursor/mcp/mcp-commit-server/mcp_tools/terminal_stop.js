import * as StateManager from '../lib/state_manager.js';
// import * as ProcessManager from '../lib/process_manager.js'; // No longer using ProcessManager.killProcess
import { killProcessTree } from '../lib/util/process_killer.js';
import { readLogLines, deleteLogFiles } from '../lib/logger.js';

/**
 * MCP Tool handler for 'stop_terminal_command'.
 * Stops specified terminal processes and retrieves final output if requested.
 */
export async function handleStopTerminalCommand({ pids, lines = 0 /* If lines > 0, retrieve final lines */ }) {
    const results = [];

    for (const pid of pids) {
        const state = StateManager.findStateByPid(pid);
        let stdoutContent = '';
        let stderrContent = '';
        let stopStatus = ''; // Initialize stopStatus

        // Only attempt to read logs if lines > 0 AND state exists
        if (lines > 0 && state) {
            try {
                stdoutContent = await readLogLines(state.stdout_log, lines);
            } catch (logReadErr) {
                stdoutContent = `[Stdout Log Read Error: ${logReadErr.code || logReadErr.message}]`;
            }
            try {
                stderrContent = await readLogLines(state.stderr_log, lines);
            } catch (logReadErr) {
                stderrContent = `[Stderr Log Read Error: ${logReadErr.code || logReadErr.message}]`;
            }
        } else if (lines > 0) {
            stdoutContent = "[State not found for log reading]";
            stderrContent = "[State not found for log reading]";
        }

        // Attempt to kill the process tree
        await new Promise((resolveKill) => {
            killProcessTree(pid, (killError) => {
                if (killError) {
                    // console.error(`[StopCmd] killProcessTree failed for PID ${pid}:`, killError);
                    stopStatus = `Error during tree kill for PID ${pid}: ${killError.message}.`;
                } else {
                    // console.log(`[StopCmd] killProcessTree signal sent for PID ${pid}.`);
                    stopStatus = `Process tree kill signal sent for PID ${pid}.`;
                }
                resolveKill();
            });
        });

        // Attempt to clean up state and log files
        try {
            // Ensure state exists before trying to use its properties for log deletion if deleteLogFiles needs it
            // However, based on previous search, deleteLogFiles(pid) was used.
            await deleteLogFiles(pid);
            await StateManager.removeStateByPid(pid);
            stopStatus += " State and log cleanup attempted."; // Append this regardless of kill success, as cleanup is always tried.
        } catch (cleanupError) {
            // console.error(`[StopCmd] Error during cleanup for PID ${pid}:`, cleanupError);
            stopStatus += ` Error during cleanup: ${cleanupError.message}.`;
        }

        results.push({
            pid: pid,
            status: stopStatus,
            stdout: stdoutContent,
            stderr: stderrContent
        });
    }

    return { content: [{ type: "text", text: JSON.stringify(results) }] };
}

export { }; // Add empty export to make it a module 