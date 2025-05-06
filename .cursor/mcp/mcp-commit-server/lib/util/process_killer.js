import kill from 'tree-kill'; // ESM import style
import os from 'os';

/**
 * Kills a process tree.
 * @param {number} pid The process ID of the root process to kill.
 * @param {(error?: Error) => void} callback Callback function. Called with an error if kill fails, otherwise undefined.
 */
export function killProcessTree(pid, callback) {
    if (typeof pid !== 'number' || pid <= 0) {
        // console.error('[ProcessKiller] Invalid PID provided for killProcessTree:', pid);
        if (callback) callback(new Error('Invalid PID provided.'));
        return;
    }

    // tree-kill uses 'SIGTERM' by default on POSIX and 'taskkill /F /T' on Windows.
    // 'SIGKILL' can be specified for POSIX.
    // For Windows, tree-kill already uses a forceful method (taskkill /F /T), so providing no signal is fine.
    // For POSIX, SIGKILL is more forceful than the default SIGTERM.
    const signal = os.platform() === 'win32' ? undefined : 'SIGKILL';

    // console.log(`[ProcessKiller] Attempting to kill process tree for PID: ${pid} with signal: ${signal || 'default (taskkill /F /T for Win)'}`);
    kill(pid, signal, (err) => {
        if (err) {
            // console.error(`[ProcessKiller] Error killing process tree for PID ${pid}:`, err);
            if (callback) callback(err);
        } else {
            // console.log(`[ProcessKiller] Successfully sent kill signal to process tree for PID: ${pid}`);
            if (callback) callback();
        }
    });
}

// Ensure it's treated as a module if no other exports are present, though `export function` makes it a module.
// export {}; // This might not be strictly necessary if there's already an export like `export function`. 