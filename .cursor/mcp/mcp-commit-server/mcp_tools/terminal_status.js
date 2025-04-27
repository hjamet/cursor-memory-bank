import * as StateManager from '../lib/state_manager.js';
// import * as Logger from '../lib/logger.js'; // Logger no longer needed here
import process from 'process'; // Needed for background status check

// TODO: Re-implement or remove the background status monitor (updateRunningProcessStatuses)
// The original server had a background timer (`setInterval(updateRunningProcessStatuses, 1000);`)
// that periodically checked if running processes (via `process.kill(pid, 0)`) still existed
// and updated their state to 'Stopped' if they didn't (error code ESRCH).
// This was a polling mechanism and not perfectly reliable for immediate exit detection.
// The current `process_manager.js` relies on the 'exit' event handler for accurate status updates.
// We need to decide if the less reliable polling is still desired/needed as a fallback.
// For now, the timeout logic in this handler will *not* rely on the background monitor.

/**
 * MCP Tool handler for 'get_terminal_status'.
 * Retrieves status of tracked terminals, optionally waiting for changes.
 */
export async function handleGetTerminalStatus({ timeout = 0 }) {
    let status_changed = false;
    const startTime = Date.now();
    let currentStates = StateManager.getState(); // Get initial state

    // Helper function to get formatted terminal list
    const getFormattedTerminals = (states) => { // Made synchronous
        const terminals = [];
        for (const state of states) {
            // Log reading removed as log files no longer exist
            /* 
            const lastStdout = await Logger.readLogLines(state.stdout_log, 10);
            const lastStderr = await Logger.readLogLines(state.stderr_log, 10);
            const last_output = `--- STDOUT ---\n${lastStdout}\n--- STDERR ---\n${lastStderr}`.trim();
            */
            const last_output = "[Output not available via get_terminal_status]"; // Placeholder

            terminals.push({
                pid: state.pid,
                status: state.status,
                exit_code: state.exit_code,
                cwd: state.cwd ?? null,
                last_output: last_output
            });
        }
        return terminals;
    };

    // If timeout > 0, wait for a status change for any running process
    if (timeout > 0) {
        const initialRunningPids = new Set(
            currentStates.filter(s => s.status === 'Running').map(s => s.pid)
        );

        if (initialRunningPids.size > 0) {
            while ((Date.now() - startTime) < (timeout * 1000)) {
                currentStates = StateManager.getState(); // Re-fetch current state
                let changed = false;
                for (const pid of initialRunningPids) {
                    const currentState = currentStates.find(s => s.pid === pid);
                    // If a process that was initially running is no longer running or missing
                    if (!currentState || currentState.status !== 'Running') {
                        changed = true;
                        break;
                    }
                }

                if (changed) {
                    status_changed = true;
                    break; // Exit loop as soon as a change is detected
                }

                // Wait a short interval before checking again
                await new Promise(resolve => setTimeout(resolve, 200)); // Poll every 200ms
            }
        }
    }

    // Format the final output based on the latest state fetched
    const terminals = getFormattedTerminals(currentStates); // Call synchronous helper
    const response = { status_changed, terminals };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 