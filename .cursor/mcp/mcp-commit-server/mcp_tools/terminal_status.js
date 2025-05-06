import * as StateManager from '../lib/state_manager.js';
import { readLastLogChars } from '../lib/logger.js';
import process from 'process'; // Needed for background status check

// Define character limit for status snapshot
const MAX_CHARS_STATUS = 1500;

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
    if (timeout > 300) {
        return { content: [{ type: "text", text: JSON.stringify({ error: "Timeout cannot exceed 300 seconds (5 minutes).", status_changed: false, terminals: [] }) }] };
    }

    let status_changed = false;
    const startTime = Date.now();
    let currentStates = StateManager.getState(); // Get initial state

    // Helper function to get formatted terminal list
    const getFormattedTerminals = async (states) => {
        const terminals = [];
        const prefix = '[Call get_terminal_output to consult previous characters !] ';
        for (const state of states) {
            let lastStdout = '';
            let lastStderr = '';

            // Read last N characters for status snapshot
            try {
                lastStdout = await readLastLogChars(state.stdout_log, MAX_CHARS_STATUS);
                if (lastStdout.length === MAX_CHARS_STATUS) {
                    lastStdout = prefix + lastStdout;
                }
            } catch (logReadErr) {
                console.error(`[GetStatus] Error reading last stdout chars for PID ${state.pid}:`, logReadErr);
            }
            try {
                lastStderr = await readLastLogChars(state.stderr_log, MAX_CHARS_STATUS);
                if (lastStderr.length === MAX_CHARS_STATUS) {
                    lastStderr = prefix + lastStderr;
                }
            } catch (logReadErr) {
                console.error(`[GetStatus] Error reading last stderr chars for PID ${state.pid}:`, logReadErr);
            }

            const last_output = `--- STDOUT (Last ${MAX_CHARS_STATUS} chars) ---\n${lastStdout}\n--- STDERR (Last ${MAX_CHARS_STATUS} chars) ---\n${lastStderr}`.trim();

            terminals.push({
                pid: state.pid,
                status: state.status,
                exit_code: state.exit_code,
                cwd: state.cwd ?? null,
                last_output: last_output // Renamed field or update description?
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
    const terminals = await getFormattedTerminals(currentStates);
    const response = { status_changed, terminals };

    return { content: [{ type: "text", text: JSON.stringify(response) }] };
}

export { }; // Add empty export to make it a module 