import * as StateManager from '../lib/state_manager.js';
import * as ProcessManager from '../lib/process_manager.js';
import * as Logger from '../lib/logger.js';

/**
 * MCP Tool handler for 'execute_command'.
 * Spawns a command, manages state, and handles optional terminal reuse.
 */
export async function handleExecuteCommand({ command, reuse_terminal, timeout /* timeout is currently unused but part of sig */ }) {
    // Handle terminal reuse: Find a finished terminal state index
    if (reuse_terminal) {
        const reusableIndex = StateManager.findReusableTerminalIndex();
        if (reusableIndex !== -1) {
            // Get the state before removing it
            const stateToClean = StateManager.getState()[reusableIndex];
            if (stateToClean) {
                // Remove state first
                await StateManager.removeStateByIndex(reusableIndex);
                // Then delete logs (best effort)
                await Logger.deleteLogFiles(stateToClean);
                // console.log(`[ExecuteCommand] Reused terminal slot from PID ${stateToClean.pid}`);
            }
        }
    }

    try {
        // Spawn the process using the process manager
        const { pid, stdout_log, stderr_log } = await ProcessManager.spawnProcess(command);

        // Original server had timeout logic to return early while process continues.
        // This simplified version doesn't wait or return early based on timeout.
        // It just returns the PID immediately.
        // The *actual* status/output is retrieved via get_terminal_status/output.
        // The `timeout` parameter from the MCP definition is effectively ignored here.

        const response = {
            pid,
            stdout: '', // Per original logic, stdout/stderr are not returned here
            stderr: '', // They are retrieved via get_terminal_output
            exit_code: null // Exit code is unknown at this point
        };

        return { content: [{ type: "text", text: JSON.stringify(response) }] };

    } catch (error) {
        console.error('[ExecuteCommand] Error:', error);
        // Ensure error is propagated correctly
        throw new Error(`Failed to execute command: ${error.message}`);
    }
}

export { }; // Add empty export to make it a module 