import * as StateManager from '../lib/state_manager.js';
// import * as ProcessManager from '../lib/process_manager.js'; // No longer using ProcessManager.killProcess
import { killProcessTree } from '../lib/util/process_killer.js';
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
        let stopStatus = ''; // Initialize stopStatus

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

            if (newStdoutIndex > stdoutStartIndex || newStderrIndex > stderrStartIndex) {
                StateManager.updateState(pid, {
                    stdout_read_index: newStdoutIndex,
                    stderr_read_index: newStderrIndex
                }).catch(err => console.error(`[StopCmd] Error updating final state indices for PID ${pid}:`, err));
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