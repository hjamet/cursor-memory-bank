import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to workflow state file
const WORKFLOW_STATE_FILE = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_state.json');

/**
 * Default workflow state structure
 */
const DEFAULT_WORKFLOW_STATE = {
    version: "1.0.0",
    implementation_count: 0,
    last_readme_task_at: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
};

/**
 * Load workflow state from file
 * @returns {Promise<Object>} Workflow state object
 */
async function loadWorkflowState() {
    try {
        const data = await fs.readFile(WORKFLOW_STATE_FILE, 'utf8');
        const state = JSON.parse(data);

        // Ensure all required fields exist (migration safety)
        return {
            ...DEFAULT_WORKFLOW_STATE,
            ...state
        };
    } catch (error) {
        if (error.code === 'ENOENT') {
            // File doesn't exist, return default state
            return { ...DEFAULT_WORKFLOW_STATE };
        }
        // File exists but is corrupted, log warning and return default
        console.warn(`Workflow state file corrupted, using defaults: ${error.message}`);
        return { ...DEFAULT_WORKFLOW_STATE };
    }
}

/**
 * Save workflow state to file atomically
 * @param {Object} state - Workflow state object
 * @returns {Promise<void>}
 */
async function saveWorkflowState(state) {
    try {
        // Ensure directory exists
        const dir = path.dirname(WORKFLOW_STATE_FILE);
        await fs.mkdir(dir, { recursive: true });

        // Update timestamp
        const updatedState = {
            ...state,
            updated_at: new Date().toISOString()
        };

        // Write atomically
        await fs.writeFile(WORKFLOW_STATE_FILE, JSON.stringify(updatedState, null, 2), 'utf8');
    } catch (error) {
        throw new Error(`Failed to save workflow state: ${error.message}`);
    }
}

/**
 * Increment implementation counter and check for README task trigger
 * @returns {Promise<Object>} Result with counter value and trigger status
 */
async function incrementImplementationCount() {
    const state = await loadWorkflowState();

    // Increment counter
    state.implementation_count++;

    // Check if we need to trigger README task generation
    const shouldTriggerReadmeTask = (state.implementation_count % 10 === 0) &&
        (state.last_readme_task_at !== state.implementation_count);

    // Save updated state
    await saveWorkflowState(state);

    return {
        count: state.implementation_count,
        shouldTriggerReadmeTask,
        triggerReason: shouldTriggerReadmeTask ? `Every 10 implementations (current: ${state.implementation_count})` : null
    };
}

/**
 * Mark that a README task was generated at the current count
 * @returns {Promise<void>}
 */
async function markReadmeTaskGenerated() {
    const state = await loadWorkflowState();
    state.last_readme_task_at = state.implementation_count;
    await saveWorkflowState(state);
}

/**
 * Get current workflow state (read-only)
 * @returns {Promise<Object>} Current workflow state
 */
async function getWorkflowState() {
    return await loadWorkflowState();
}

/**
 * Reset implementation counter (for maintenance/testing)
 * @returns {Promise<void>}
 */
async function resetImplementationCount() {
    const state = await loadWorkflowState();
    state.implementation_count = 0;
    state.last_readme_task_at = 0;
    await saveWorkflowState(state);
}

export {
    loadWorkflowState,
    saveWorkflowState,
    incrementImplementationCount,
    markReadmeTaskGenerated,
    getWorkflowState,
    resetImplementationCount,
    WORKFLOW_STATE_FILE
}; 