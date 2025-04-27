import fs from 'fs/promises';
import fsSync from 'fs'; // For createWriteStream sync
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const LOGS_DIR = path.join(__dirname, '../logs');

/**
 * Ensures the logs directory exists.
 * Creates it recursively if it doesn't.
 * @returns {Promise<void>}
 */
export async function ensureLogsDir() {
    try {
        await fs.access(LOGS_DIR);
    } catch (error) {
        if (error.code === 'ENOENT') {
            try {
                await fs.mkdir(LOGS_DIR, { recursive: true });
                // console.log(`[Logger] Created logs directory: ${LOGS_DIR}`);
            } catch (mkdirError) {
                console.error(`[Logger] Error creating logs directory ${LOGS_DIR}:`, mkdirError);
                // Decide if this is fatal
            }
        } else {
            console.error(`[Logger] Error accessing logs directory ${LOGS_DIR}:`, error);
        }
    }
}

/**
 * Creates write streams for stdout and stderr logs for a given PID.
 * Assumes logs directory exists (call ensureLogsDir first).
 * @param {number} pid The process ID.
 * @returns {{stdoutLogPath: string, stderrLogPath: string, stdoutStream: fsSync.WriteStream, stderrStream: fsSync.WriteStream}}
 */
export function createLogStreams(pid) {
    const stdoutLogPath = path.join(LOGS_DIR, `${pid}.stdout.log`);
    const stderrLogPath = path.join(LOGS_DIR, `${pid}.stderr.log`);
    // Using sync version as it's part of the synchronous setup before spawn returns
    const stdoutStream = fsSync.createWriteStream(stdoutLogPath, { flags: 'a' });
    const stderrStream = fsSync.createWriteStream(stderrLogPath, { flags: 'a' });
    return { stdoutLogPath, stderrLogPath, stdoutStream, stderrStream };
}

/**
 * Reads the last N lines of a log file asynchronously.
 * If lineCount <= 0, reads the entire file.
 * @param {string} logPath Path to the log file.
 * @param {number} lineCount Maximum number of lines to read (or <= 0 for all).
 * @returns {Promise<string>} Last N lines, full content, or explicit error string if file not found/error.
 */
export async function readLogLines(logPath, lineCount) {
    try {
        const content = await fs.readFile(logPath, 'utf8');
        if (lineCount === undefined || lineCount === null || lineCount <= 0) {
            return content; // Return full content if lineCount is invalid or non-positive
        }
        // Proceed with reading last N lines
        const lines = content.split(/\r?\n/).filter(line => line.length > 0);
        const lastLines = lines.slice(-lineCount);
        return lastLines.join('\n');
    } catch (error) {
        if (error.code === 'ENOENT') {
            return ''; // File not found is not necessarily an error here
        }
        console.error(`[Logger] Error reading log file ${logPath}:`, error);
        return `[Log Read Error: ${error.code || error.message}]`; // Return explicit error string
    }
}

/**
 * Deletes log files associated with a given state entry or PID.
 * @param {object|number} stateOrPid A state object containing log paths or just a PID.
 * @returns {Promise<void>}
 */
export async function deleteLogFiles(stateOrPid) {
    let stdoutLogPath = null;
    let stderrLogPath = null;

    if (typeof stateOrPid === 'number') {
        stdoutLogPath = path.join(LOGS_DIR, `${stateOrPid}.stdout.log`);
        stderrLogPath = path.join(LOGS_DIR, `${stateOrPid}.stderr.log`);
    } else if (typeof stateOrPid === 'object' && stateOrPid !== null) {
        stdoutLogPath = stateOrPid.stdout_log;
        stderrLogPath = stateOrPid.stderr_log;
    }

    const deletePromises = [];

    if (stdoutLogPath) {
        deletePromises.push(
            fs.unlink(stdoutLogPath).catch(err => {
                if (err.code !== 'ENOENT') { // Ignore if file doesn't exist
                    console.warn(`[Logger] Could not delete stdout log ${stdoutLogPath}:`, err);
                }
            })
        );
    }

    if (stderrLogPath) {
        deletePromises.push(
            fs.unlink(stderrLogPath).catch(err => {
                if (err.code !== 'ENOENT') { // Ignore if file doesn't exist
                    console.warn(`[Logger] Could not delete stderr log ${stderrLogPath}:`, err);
                }
            })
        );
    }

    await Promise.all(deletePromises);
}

// --- Debug Logging --- 
const DEBUG_LOG_FILE = path.join(__dirname, '../server_debug.log');
let debugLogStream = null;

function ensureDebugLogStream() {
    if (!debugLogStream) {
        try {
            // Use append flag 'a'
            debugLogStream = fsSync.createWriteStream(DEBUG_LOG_FILE, { flags: 'a' });
            debugLogStream.on('error', (err) => {
                console.error('[Logger] Error writing to debug log:', err);
                debugLogStream = null; // Reset stream on error
            });
        } catch (err) {
            console.error('[Logger] Failed to create debug log stream:', err);
        }
    }
}

/**
 * Logs a debug message to the server_debug.log file.
 * @param {string} message 
 */
export function logDebug(message) {
    ensureDebugLogStream();
    if (debugLogStream) {
        const timestamp = new Date().toISOString();
        debugLogStream.write(`${timestamp} - ${message}\n`);
    } else {
        // Fallback to console if stream failed
        console.error(`[Debug Log Fallback] ${message}`);
    }
}

// Ensure the stream is created on module load
ensureDebugLogStream(); 