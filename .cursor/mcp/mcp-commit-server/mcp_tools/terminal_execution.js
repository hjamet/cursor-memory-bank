import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import * as Logger from '../lib/logger.js';

/**
 * MCP Tool handler for 'execute_command'.
 * Spawns a command, manages state, and handles optional terminal reuse.
 * If command finishes within timeout, returns full output and final state.
 * Otherwise, returns initial state and PID for later polling.
 */
export async function handleExecuteCommand({ command, reuse_terminal, timeout = 15 /* default 15s */ }) {
    // Handle terminal reuse
    if (reuse_terminal) {
        const reusableIndex = StateManager.findReusableTerminalIndex();
        if (reusableIndex !== -1) {
            const stateToClean = StateManager.getState()[reusableIndex];
            if (stateToClean) {
                await StateManager.removeStateByIndex(reusableIndex);
                await Logger.deleteLogFiles(stateToClean);
            }
        }
    }

    let pid;
    try {
        // Spawn process and get pid & completion promise
        const { pid: processPid, completionPromise } = await ProcessManager.spawnProcess(command);
        pid = processPid; // Assign pid for potential error logging

        // Create a timeout promise
        let timeoutId;
        const timeoutPromise = new Promise((_, reject) => {
            timeoutId = setTimeout(() => reject(new Error('Timeout')), timeout * 1000);
        });

        let processCompleted = false;
        let resolvedState = null; // Variable to hold the state passed by the promise
        try {
            // Wait for either the process to complete or the timeout
            resolvedState = await Promise.race([completionPromise, timeoutPromise]);
            // If we reach here, completionPromise resolved first
            processCompleted = true;
            Logger.logDebug(`[PID ${pid}] Promise.race: completionPromise won.`);
        } catch (error) {
            // If we reach here, timeoutPromise rejected first (or completionPromise had an error)
            if (error.message === 'Timeout') {
                processCompleted = false;
                Logger.logDebug(`[PID ${pid}] Promise.race: timeoutPromise won.`);
            } else {
                // Unexpected error from completionPromise?
                Logger.logDebug(`[PID ${pid}] Promise.race: completionPromise failed with error: ${error.message}`);
                throw error;
            }
        } finally {
            // Crucial: Clear the timeout timer regardless of outcome
            clearTimeout(timeoutId);
        }

        // Construct response based on completion status
        // Use resolvedState if process completed, otherwise fetch current state for timeout case
        const stateToUse = processCompleted ? resolvedState : StateManager.findStateByPid(pid);

        if (!stateToUse) {
            // This shouldn't happen if spawn succeeded and promise resolved/state fetched
            throw new Error(`Failed to find state for PID ${pid}.`);
        }

        let response;
        if (processCompleted) {
            // Process finished: Use the final state passed by the promise, which now includes logs

            response = {
                pid: stateToUse.pid,
                cwd: stateToUse.cwd ?? null,
                status: stateToUse.status,
                exit_code: stateToUse.exit_code,
                stdout: stateToUse.stdout ?? '', // Get logs from resolved state
                stderr: stateToUse.stderr ?? '', // Get logs from resolved state
            };
        } else {
            // Timeout occurred: Return current state (likely 'Running')
            response = {
                pid: pid,
                cwd: stateToUse.cwd ?? null,
                status: stateToUse.status ?? 'Running', // Default to Running if state is weird
                exit_code: null,
                stdout: '',
                stderr: ''
            };
        }

        return { content: [{ type: "text", text: JSON.stringify(response) }] };

    } catch (error) {
        console.error(`[ExecuteCommand] Error processing command "${command}" (PID: ${pid ?? 'N/A'}):`, error);
        throw new Error(`Failed to execute command: ${error.message}`);
    }
}

export { }; // Add empty export to make it a module 