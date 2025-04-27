import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATE_FILE = path.join(__dirname, '../terminals_status.json');
let terminalStates = []; // In-memory cache of the state

/**
 * Loads the terminal state from the JSON file into the in-memory cache.
 * Initializes with an empty array if the file doesn't exist or is invalid.
 * Should be called once on server startup.
 */
export async function loadState() {
    try {
        const fileContent = await fs.readFile(STATE_FILE, 'utf8');
        const parsedState = JSON.parse(fileContent);
        if (Array.isArray(parsedState)) {
            terminalStates = parsedState;
            // console.log(`[StateManager] Loaded ${terminalStates.length} states from ${STATE_FILE}`);
        } else {
            console.error(`[StateManager] Invalid state file format in ${STATE_FILE}. Expected an array. Resetting state.`);
            terminalStates = [];
            await persistState(); // Write empty state back
        }
    } catch (error) {
        if (error.code === 'ENOENT') {
            // File doesn't exist, initialize empty state
            terminalStates = [];
            // console.log(`[StateManager] State file ${STATE_FILE} not found. Initializing empty state.`);
            await persistState(); // Create the file with empty state
        } else {
            console.error(`[StateManager] Error reading or parsing state file ${STATE_FILE}:`, error);
            terminalStates = []; // Reset state on other errors
            // Consider if we should attempt to write back the empty state here too
        }
    }
    return terminalStates;
}

/**
 * Writes the current in-memory terminal state cache to the JSON file.
 */
async function persistState() {
    try {
        const fileContent = JSON.stringify(terminalStates, null, 2); // Pretty print JSON
        await fs.writeFile(STATE_FILE, fileContent, 'utf8');
        // console.log(`[StateManager] Wrote ${terminalStates.length} states to ${STATE_FILE}`);
    } catch (error) {
        console.error(`[StateManager] Error writing state file ${STATE_FILE}:`, error);
        // Decide how to handle write errors - potentially critical
    }
}

/**
 * Returns the current in-memory state array.
 * Use this for reading the state after loadState has been called.
 */
export function getState() {
    return [...terminalStates]; // Return a copy
}

/**
 * Finds a terminal state entry by PID.
 * @param {number} pid The process ID.
 * @returns {object | undefined} The state entry or undefined if not found.
 */
export function findStateByPid(pid) {
    return terminalStates.find(s => s.pid === pid);
}

/**
 * Adds a new terminal state entry to the cache and persists it.
 * @param {object} newStateEntry The state entry to add.
 * @returns {Promise<void>}
 */
export async function addState(newStateEntry) {
    // Ensure no duplicate PID - though spawn should guarantee uniqueness for active processes
    if (findStateByPid(newStateEntry.pid)) {
        console.warn(`[StateManager] Attempted to add duplicate PID ${newStateEntry.pid}. Ignoring.`);
        return;
    }
    terminalStates.push(newStateEntry);
    persistState(); // Trigger persistence without waiting
}

/**
 * Updates an existing terminal state entry by PID.
 * @param {number} pid The PID of the state to update.
 * @param {object} updates An object containing the properties to update.
 * @returns {Promise<void>}
 */
export async function updateState(pid, updates) {
    const stateIndex = terminalStates.findIndex(s => s.pid === pid);
    if (stateIndex !== -1) {
        terminalStates[stateIndex] = { ...terminalStates[stateIndex], ...updates };
        await persistState();
    } else {
        console.warn(`[StateManager] Attempted to update non-existent PID ${pid}. Ignoring.`);
    }
}

/**
 * Removes a terminal state entry by PID from the cache and persists the change.
 * @param {number} pid The PID of the state to remove.
 * @returns {Promise<void>}
 */
export async function removeStateByPid(pid) {
    const initialLength = terminalStates.length;
    terminalStates = terminalStates.filter(s => s.pid !== pid);
    if (terminalStates.length < initialLength) {
        await persistState();
    } else {
        console.warn(`[StateManager] Attempted to remove non-existent PID ${pid}. Ignoring.`);
    }
}

/**
 * Removes multiple terminal state entries by PID.
 * @param {number[]} pids Array of PIDs to remove.
 * @returns {Promise<void>}
 */
export async function removeStatesByPids(pids) {
    const initialLength = terminalStates.length;
    const pidsSet = new Set(pids);
    terminalStates = terminalStates.filter(s => !pidsSet.has(s.pid));
    if (terminalStates.length < initialLength) {
        await persistState();
    }
}

/**
 * Finds the index of the first finished (Success, Failure, Stopped) terminal state.
 * Used for the reuse_terminal logic.
 * @returns {number} The index or -1 if no reusable terminal found.
 */
export function findReusableTerminalIndex() {
    return terminalStates.findIndex(state =>
        ['Success', 'Failure', 'Stopped', 'Terminated'].includes(state.status) // Added Terminated
    );
}

/**
 * Removes a terminal state by its index in the array.
 * Used internally for the reuse_terminal logic after finding the index.
 * @param {number} index The index to remove.
 * @returns {Promise<object | undefined>} The removed state object or undefined.
 */
export async function removeStateByIndex(index) {
    if (index >= 0 && index < terminalStates.length) {
        const removedState = terminalStates.splice(index, 1)[0];
        await persistState();
        return removedState;
    }
    return undefined;
} 