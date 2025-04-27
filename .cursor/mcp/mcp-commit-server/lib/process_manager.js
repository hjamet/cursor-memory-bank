import { spawn } from 'child_process';
// import { execa } from 'execa'; // REVERTED
import path from 'path';
import process from 'process';
import { fileURLToPath } from 'url';
import * as StateManager from './state_manager.js';
import * as Logger from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
// const projectRoot = path.resolve(__dirname, '../../..'); // Assuming lib/ is two levels down
// Use the workspace root passed via environment variable or a sensible default
const workspaceRoot = process.env.MCP_WORKSPACE_ROOT || path.resolve(__dirname, '../../../..'); // Go up one more level to get actual root

/**
 * Spawns a process, manages its state, and logs its output.
 * @param {string} command The command line to execute.
 * @returns {Promise<{pid: number, exit_code: number | null, stdout_log: string, stderr_log: string}>} Promise resolving with initial info, or rejecting on immediate spawn error.
 */
export async function spawnProcess(command) {
    let child;
    let pid;
    let stdoutBuffer = ''; // Buffer pour stdout
    let stderrBuffer = ''; // Buffer pour stderr
    let resolveCompletion;
    const completionPromise = new Promise(resolve => { resolveCompletion = resolve; });
    let capturedExitCode = null;
    const startTime = new Date().toISOString();

    try {
        // Determine how to spawn based on the command string
        let executable;
        let args;
        let spawnOptions = {
            detached: true,
            stdio: ['ignore', 'pipe', 'pipe'],
            cwd: workspaceRoot,
            // Force shell: false par défaut, sauf cas spécifiques
            shell: false
        };

        // Specific handling for Git Bash on Windows
        const gitBashPath = "C:\\Program Files\\Git\\bin\\bash.exe"; // Use escaped backslashes
        if (process.platform === 'win32' && command.startsWith(`"${gitBashPath}"`)) {
            const match = command.match(/^"(.*?)"\s+-c\s+"(.*)"$/);
            if (match && match[1] === gitBashPath) {
                executable = gitBashPath;
                args = ['-c', match[2]]; // Pass the command string as an argument to -c
            } else {
                executable = command; // The whole string
                args = [];
                spawnOptions.shell = true; // Revert to shell: true for this case
            }
        } else if (process.platform === 'win32') {
            // Sur Windows, pour commandes générales, utiliser cmd /c explicitement avec shell: false
            executable = 'cmd.exe';
            args = ['/c', command]; // Passe toute la commande à /c
            spawnOptions.shell = false; // Assurer shell: false
        } else {
            // Pour les autres OS (ou si on veut un vrai shell interactif plus tard)
            executable = command; // Ou peut-être /bin/sh ?
            args = [];
            spawnOptions.shell = true; // Revenir à shell: true pour non-Windows par défaut ?
        }

        // Spawn the process
        try {
            Logger.logDebug(`[PID ${pid}] Spawning: Executable: ${executable}, Args: [${args.join(', ')}], Options: ${JSON.stringify(spawnOptions)}`);
            child = spawn(executable, args, spawnOptions);
        } catch (spawnErr) {
            Logger.logDebug(`[PID ${pid}] Spawn initial failed: ${spawnErr.message}`);
            // Pas de retry automatique avec shell: true si on force shell: false
            throw spawnErr;
        }

        pid = child.pid;
        if (pid === undefined) {
            throw new Error('Failed to get PID for spawned process.');
        }

        // Supprimer création et piping vers streams/fichiers logs
        /*
        const streams = Logger.createLogStreams(pid);
        stdoutLogPath = streams.stdoutLogPath;
        stderrLogPath = streams.stderrLogPath;
        stdoutStream = streams.stdoutStream;
        stderrStream = streams.stderrStream;
        child.stdout.pipe(stdoutStream);
        child.stderr.pipe(stderrStream);
        */
        const MAX_BUFFER_SIZE = 10 * 1024 * 1024; // Limite de 10MB par buffer (ajustable)

        // Capturer stdout en mémoire
        child.stdout.on('data', (data) => {
            const dataStr = data.toString();
            Logger.logDebug(`[PID ${pid}] stdout DATA event. Length: ${dataStr.length}`);
            if (stdoutBuffer.length < MAX_BUFFER_SIZE) {
                stdoutBuffer += dataStr;
                if (stdoutBuffer.length > MAX_BUFFER_SIZE) {
                    stdoutBuffer = stdoutBuffer.substring(0, MAX_BUFFER_SIZE) + '\n[Output Truncated]\n';
                }
            } // Sinon, ignorer les données supplémentaires
        });

        // Capturer stderr en mémoire
        child.stderr.on('data', (data) => {
            const dataStr = data.toString();
            Logger.logDebug(`[PID ${pid}] stderr DATA event. Length: ${dataStr.length}`);
            if (stderrBuffer.length < MAX_BUFFER_SIZE) {
                stderrBuffer += dataStr;
                if (stderrBuffer.length > MAX_BUFFER_SIZE) {
                    stderrBuffer = stderrBuffer.substring(0, MAX_BUFFER_SIZE) + '\n[Output Truncated]\n';
                }
            } // Sinon, ignorer les données supplémentaires
        });

        // Add entry to state (sans log paths)
        const newStateEntry = {
            pid,
            command,
            cwd: spawnOptions.cwd,
            status: 'Running',
            exit_code: null,
            stdout_log: null, // Pas de fichier log
            stderr_log: null, // Pas de fichier log
            startTime,
            endTime: null,
        };
        // Utiliser addState qui n'attend pas persist
        StateManager.addState(newStateEntry).catch(e => console.error("Error adding initial state:", e));

        // --- Process Event Handling ---
        let finalUpdateDone = false;

        const handleExit = async (code, signal) => {
            capturedExitCode = code ?? (signal ? 1 : 0);
            Logger.logDebug(`[PID ${pid}] EXIT event. Stored code: ${capturedExitCode}`);
            const status = (capturedExitCode === 0) ? 'Success' : 'Failure';
            const endTime = new Date().toISOString();
            // Mise à jour initiale pour statut/code/temps (n'attend pas persist)
            StateManager.updateState(pid, { status: status, exit_code: capturedExitCode, endTime: endTime })
                .catch(e => console.error("Error updating state on exit:", e));
        };

        const handleClose = async (code, signal) => {
            Logger.logDebug(`[PID ${pid}] CLOSE event. Using stored code: ${capturedExitCode}.`);
            if (finalUpdateDone) { return; }
            finalUpdateDone = true;

            // Construire l'état final avec les buffers mémoire
            const stateToResolve = {
                // Lire les infos non volatiles de l'état si besoin
                // mais construire l'essentiel directement
                pid: pid,
                command: command,
                cwd: spawnOptions.cwd,
                startTime: startTime,
                // Fin
                status: (capturedExitCode === 0) ? 'Success' : 'Failure',
                exit_code: capturedExitCode,
                endTime: new Date().toISOString(),
                stdout: stdoutBuffer, // Utiliser le buffer stdout
                stderr: stderrBuffer, // Utiliser le buffer stderr
                stdout_log: null,
                stderr_log: null,
            };

            // Mettre à jour l'état final pour la persistance (sans logs)
            const finalUpdatePayload = {
                status: stateToResolve.status,
                exit_code: stateToResolve.exit_code,
                endTime: stateToResolve.endTime,
                stdout_log: null,
                stderr_log: null,
            };
            StateManager.updateState(pid, finalUpdatePayload).catch(err => {
                console.error(`[ProcessManager] Background persistence error for PID ${pid} in handleClose:`, err);
            });

            if (resolveCompletion) resolveCompletion(stateToResolve);
        };

        const handleError = async (err) => {
            Logger.logDebug(`[PID ${pid}] ERROR event. Error: ${err.message}`);
            if (finalUpdateDone) { return; }
            finalUpdateDone = true;
            console.error(`[ProcessManager] Error event for child process ${pid}:`, err);

            const errorEndTime = new Date().toISOString();
            // Mise à jour pour persistance
            StateManager.updateState(pid, { status: 'Failure', exit_code: null, endTime: errorEndTime, stdout_log: null, stderr_log: null })
                .catch(e => console.error("Error updating state on error:", e));

            // Construire état à résoudre
            const stateToResolveOnError = {
                pid: pid,
                command: command,
                cwd: spawnOptions.cwd,
                startTime: startTime,
                status: 'Failure',
                exit_code: null,
                endTime: errorEndTime,
                stdout: stdoutBuffer, // Inclure ce qui a été bufferisé
                stderr: stderrBuffer + (stderrBuffer ? '\n' : '') + `Process Error: ${err.message}`, // Ajouter l'erreur
                stdout_log: null,
                stderr_log: null,
            };

            if (resolveCompletion) resolveCompletion(stateToResolveOnError);
        };

        // Register event handlers
        child.on('exit', handleExit);
        child.on('close', handleClose);
        child.on('error', handleError);

        // Retourner seulement PID et promesse
        return { pid, completionPromise };
    } catch (err) {
        console.error(`[ProcessManager] Error during spawnProcess setup for command "${command}":`, err);
        // Pas de streams à fermer ici
        // Tenter maj état si PID existe ?
        if (pid) {
            try {
                await StateManager.updateState(pid, {
                    status: 'Failure',
                    exit_code: null,
                    endTime: new Date().toISOString(),
                    stdout_log: null,
                    stderr_log: null
                });
            } catch (stateErr) { }
        }
        throw err;
    }
}

/**
 * Kills a process.
 * @param {number} pid The process ID of the process to kill.
 * @returns {Promise<string>} Promise that resolves with a status message when the kill attempt is done.
 */
export async function killProcess(pid) {
    try {
        // Check if process exists using signal 0
        process.kill(pid, 0);
    } catch (e) {
        if (e.code === 'ESRCH') {
            // Process already exited or never existed
            return `Process ${pid} already exited before termination attempt.`;
        } else {
            // Other error (e.g., permissions)
            console.error(`[ProcessManager] Error checking process ${pid} existence:`, e);
            return `Error checking process ${pid}: ${e.message}.`;
        }
    }

    // Process exists, attempt graceful termination
    try {
        process.kill(pid, 'SIGTERM');
        // Wait a short period to see if it terminates
        await new Promise(resolve => setTimeout(resolve, 200)); // 200ms grace period

        // Check again if it exited
        try {
            process.kill(pid, 0);
            // Still running, force kill
            console.warn(`[ProcessManager] Process ${pid} did not exit after SIGTERM, sending SIGKILL.`);
            try {
                process.kill(pid, 'SIGKILL');
                return `Process ${pid} terminated forcefully (SIGKILL).`;
            } catch (killErr) {
                // Handle error during SIGKILL (e.g., process died just before)
                console.error(`[ProcessManager] Error sending SIGKILL to ${pid}:`, killErr);
                if (killErr.code === 'ESRCH') {
                    return `Process ${pid} exited during termination attempt.`;
                } else {
                    return `Error sending SIGKILL to ${pid}: ${killErr.message}.`;
                }
            }
        } catch (e) {
            if (e.code === 'ESRCH') {
                // Exited gracefully after SIGTERM
                return `Process ${pid} terminated gracefully (SIGTERM).`;
            } else {
                // Should not happen if first check passed, but handle defensively
                console.error(`[ProcessManager] Error re-checking process ${pid} after SIGTERM:`, e);
                return `Error confirming termination for ${pid}: ${e.message}.`;
            }
        }
    } catch (termErr) {
        // Handle error during SIGTERM (e.g., permissions)
        console.error(`[ProcessManager] Error sending SIGTERM to ${pid}:`, termErr);
        if (termErr.code === 'ESRCH') {
            return `Process ${pid} exited before termination signal could be sent.`;
        } else {
            return `Error sending SIGTERM to ${pid}: ${termErr.message}.`;
        }
    }
}