import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Constants for workflow safety
const MAX_CONSECUTIVE_TRANSITIONS = 50;
const MAX_EXPERIENCE_EXECUTION_ATTEMPTS = 3;
const EXPERIENCE_EXECUTION_COOLDOWN = 60000; // 1 minute in milliseconds

/**
 * Get the path to the workflow safety JSON file
 * @returns {string} Path to workflow_safety.json
 */
function getWorkflowSafetyPath() {
    return path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_safety.json');
}

/**
 * Load the current workflow safety state
 * @returns {Promise<Object>} Workflow safety state
 */
async function loadWorkflowSafetyState() {
    try {
        const safetyPath = getWorkflowSafetyPath();
        const data = await fs.readFile(safetyPath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        // Return default state if file doesn't exist
        return {
            transition_history: [],
            experience_execution_attempts: 0,
            last_experience_execution: null,
            last_implementation: null,
            consecutive_transitions: 0,
            emergency_brake_active: false
        };
    }
}

/**
 * Save the workflow safety state
 * @param {Object} state - The state to save
 * @returns {Promise<void>}
 */
async function saveWorkflowSafetyState(state) {
    try {
        const safetyPath = getWorkflowSafetyPath();
        await fs.writeFile(safetyPath, JSON.stringify(state, null, 2));
    } catch (error) {
        // console.error('Error saving workflow safety state:', error); // Commented to prevent JSON-RPC pollution
    }
}

/**
 * Reset the transition counter to 0
 * This function is called after productive workflow cycles
 * @returns {Promise<void>}
 */
export async function resetTransitionCounter() {
    try {
        const state = await loadWorkflowSafetyState();
        state.consecutive_transitions = 0;
        state.emergency_brake_active = false;
        await saveWorkflowSafetyState(state);
        // console.log('Workflow safety: Transition counter reset to 0'); // Commented to prevent JSON-RPC pollution
    } catch (error) {
        // console.error('Error resetting transition counter:', error); // Commented to prevent JSON-RPC pollution
    }
}

/**
 * Increment the transition counter and check safety limits
 * @param {string} fromStep - Previous workflow step
 * @param {string} toStep - Next workflow step
 * @returns {Promise<Object>} Safety check result
 */
export async function incrementTransitionCounter(fromStep, toStep) {
    try {
        const state = await loadWorkflowSafetyState();

        // Add to transition history
        state.transition_history.unshift({
            from: fromStep,
            to: toStep,
            timestamp: new Date().toISOString()
        });

        // Keep only last 50 transitions
        if (state.transition_history.length > 50) {
            state.transition_history = state.transition_history.slice(0, 50);
        }

        // Increment consecutive transitions
        state.consecutive_transitions++;

        // Check for emergency brake condition
        if (state.consecutive_transitions >= MAX_CONSECUTIVE_TRANSITIONS) {
            state.emergency_brake_active = true;
        }

        await saveWorkflowSafetyState(state);

        return {
            safetyState: state,
            emergencyBrakeTriggered: state.emergency_brake_active,
            consecutiveTransitions: state.consecutive_transitions,
            maxTransitions: MAX_CONSECUTIVE_TRANSITIONS
        };
    } catch (error) {
        // console.error('Error incrementing transition counter:', error); // Commented to prevent JSON-RPC pollution
        return { count: 0, emergency_brake_active: false };
    }
}

/**
 * Check if experience-execution is in cooldown
 * @returns {Promise<boolean>} True if in cooldown
 */
export async function isExperienceExecutionInCooldown() {
    try {
        const state = await loadWorkflowSafetyState();
        if (!state.last_experience_execution) {
            return false;
        }

        const lastExecutionTime = new Date(state.last_experience_execution).getTime();
        const now = Date.now();
        const timeSinceLastExecution = now - lastExecutionTime;

        return timeSinceLastExecution < EXPERIENCE_EXECUTION_COOLDOWN;
    } catch (error) {
        // console.error('Error checking experience-execution cooldown:', error); // Commented to prevent JSON-RPC pollution
        return false; // Assume no cooldown if we can't read state
    }
}

/**
 * Record an experience-execution attempt
 * @returns {Promise<Object>} Updated state
 */
export async function recordExperienceExecutionAttempt() {
    try {
        const state = await loadWorkflowSafetyState();
        state.experience_execution_attempts++;
        state.last_experience_execution = new Date().toISOString();
        await saveWorkflowSafetyState(state);

        return {
            attempts: state.experience_execution_attempts,
            maxAttempts: MAX_EXPERIENCE_EXECUTION_ATTEMPTS,
            limitReached: state.experience_execution_attempts >= MAX_EXPERIENCE_EXECUTION_ATTEMPTS
        };
    } catch (error) {
        // console.error('Error recording experience-execution attempt:', error); // Commented to prevent JSON-RPC pollution
        return {
            attempts: 0,
            maxAttempts: MAX_EXPERIENCE_EXECUTION_ATTEMPTS,
            limitReached: false
        };
    }
}

/**
 * Reset the safety state completely (emergency function)
 * @returns {Promise<void>}
 */
export async function resetSafetyState() {
    try {
        const defaultState = {
            transition_history: [],
            experience_execution_attempts: 0,
            last_experience_execution: null,
            last_implementation: null,
            consecutive_transitions: 0,
            emergency_brake_active: false
        };

        await saveWorkflowSafetyState(defaultState);
        // console.log('Workflow safety: Complete safety state reset'); // Commented to prevent JSON-RPC pollution
    } catch (error) {
        // console.error('Error resetting safety state:', error); // Commented to prevent JSON-RPC pollution
    }
}

/**
 * Get the current safety status
 * @returns {Promise<Object>} Current safety status
 */
export async function getSafetyStatus() {
    try {
        const state = await loadWorkflowSafetyState();
        const isInCooldown = await isExperienceExecutionInCooldown();

        return {
            consecutiveTransitions: state.consecutive_transitions,
            maxConsecutiveTransitions: MAX_CONSECUTIVE_TRANSITIONS,
            emergencyBrakeActive: state.emergency_brake_active,
            experienceExecutionAttempts: state.experience_execution_attempts,
            maxExperienceExecutionAttempts: MAX_EXPERIENCE_EXECUTION_ATTEMPTS,
            isExperienceExecutionInCooldown: isInCooldown,
            lastExperienceExecution: state.last_experience_execution,
            lastImplementation: state.last_implementation
        };
    } catch (error) {
        // console.error('Error getting safety status:', error); // Commented to prevent JSON-RPC pollution
        return null;
    }
} 