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
                // console.error(`[Logger] Error creating logs directory ${LOGS_DIR}:`, mkdirError);
                // Decide if this is fatal - For now, suppress error output to avoid MCP interference
            }
        } else {
            // console.error(`[Logger] Error accessing logs directory ${LOGS_DIR}:`, error);
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
 * Appends data to a log file asynchronously.
 * @param {string} logPath Path to the log file.
 * @param {string | Buffer} data Data to append.
 * @returns {Promise<void>}
 */
export async function appendLog(logPath, data) {
    if (!logPath) return; // Do nothing if log path is invalid
    try {
        await fs.appendFile(logPath, data);
    } catch (error) {
        // console.error(`[Logger] Error appending to log file ${logPath}:`, error);
        // Decide how critical this is - maybe throw? For now, suppress error output
    }
}

/**
 * Reads the last N lines of a log file asynchronously.
 * @param {string} logPath Path to the log file.
 * @param {number} lineCount Maximum number of lines to read.
 * @returns {Promise<string>} Last N lines or empty string if file not found/error.
 */
export async function readLogLines(logPath, lineCount) {
    try {
        const content = await fs.readFile(logPath, 'utf8');
        const lines = content.split(/\r?\n/).filter(line => line.length > 0);
        const lastLines = lines.slice(-lineCount);
        return lastLines.join('\n');
    } catch (error) {
        if (error.code === 'ENOENT') {
            return ''; // File not found is not necessarily an error here
        }
        // console.error(`[Logger] Error reading log file ${logPath}:`, error);
        return ''; // Return empty on other errors
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
                    // console.warn(`[Logger] Could not delete stdout log ${stdoutLogPath}:`, err);
                }
            })
        );
    }

    if (stderrLogPath) {
        deletePromises.push(
            fs.unlink(stderrLogPath).catch(err => {
                if (err.code !== 'ENOENT') { // Ignore if file doesn't exist
                    // console.warn(`[Logger] Could not delete stderr log ${stderrLogPath}:`, err);
                }
            })
        );
    }

    await Promise.all(deletePromises);
} 