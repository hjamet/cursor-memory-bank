/**
 * Workflow Safety Manager
 * Implements safety mechanisms for the automated workflow system
 * Prevents infinite loops and validates workflow transitions
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Safety configuration
const SAFETY_CONFIG = {
    MAX_CONSECUTIVE_TRANSITIONS: 10,
    MAX_EXPERIENCE_EXECUTION_ATTEMPTS: 3,
    COOLDOWN_PERIOD_MS: 60000, // 1 minute
    WORKFLOW_STATE_FILE: path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_safety.json')
};

/**
 * Initialize or load workflow safety state
 */
async function loadSafetyState() {
    try {
        const data = await fs.readFile(SAFETY_CONFIG.WORKFLOW_STATE_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        // File doesn't exist or is corrupted, return default state
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
 * Save workflow safety state
 */
async function saveSafetyState(state) {
    try {
        // Ensure directory exists
        const dir = path.dirname(SAFETY_CONFIG.WORKFLOW_STATE_FILE);
        await fs.mkdir(dir, { recursive: true });

        await fs.writeFile(SAFETY_CONFIG.WORKFLOW_STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
    } catch (error) {
        console.warn(`Could not save workflow safety state: ${error.message}`);
    }
}

/**
 * Record a workflow transition
 */
async function recordTransition(fromStep, toStep) {
    const state = await loadSafetyState();
    const timestamp = new Date().toISOString();

    // Add to transition history (keep last 20)
    state.transition_history.unshift({
        from: fromStep,
        to: toStep,
        timestamp: timestamp
    });

    if (state.transition_history.length > 20) {
        state.transition_history = state.transition_history.slice(0, 20);
    }

    // Update consecutive transition counter
    state.consecutive_transitions++;

    // Track specific transitions
    if (toStep === 'experience-execution') {
        state.experience_execution_attempts++;
        state.last_experience_execution = timestamp;
    }

    if (toStep === 'implementation') {
        state.last_implementation = timestamp;
    }

    // Reset experience-execution attempts if we move away from testing cycle
    if (fromStep === 'experience-execution' && !['fix', 'implementation'].includes(toStep)) {
        state.experience_execution_attempts = 0;
    }

    await saveSafetyState(state);
    return state;
}

/**
 * Check if workflow transition is safe
 */
async function validateTransition(fromStep, toStep) {
    const state = await loadSafetyState();
    const now = new Date();

    // Emergency brake check
    if (state.emergency_brake_active) {
        return {
            allowed: false,
            reason: 'Emergency brake is active. Manual intervention required.',
            recommendation: 'context-update'
        };
    }

    // Check for too many consecutive transitions
    if (state.consecutive_transitions >= SAFETY_CONFIG.MAX_CONSECUTIVE_TRANSITIONS) {
        // Activate emergency brake
        state.emergency_brake_active = true;
        await saveSafetyState(state);

        return {
            allowed: false,
            reason: `Too many consecutive transitions (${state.consecutive_transitions}). Activating emergency brake.`,
            recommendation: 'context-update'
        };
    }

    // Prevent experience-execution loops
    if (toStep === 'experience-execution') {
        // Check cooldown period
        if (state.last_experience_execution) {
            const lastExecution = new Date(state.last_experience_execution);
            const timeSinceLastExecution = now - lastExecution;

            if (timeSinceLastExecution < SAFETY_CONFIG.COOLDOWN_PERIOD_MS) {
                return {
                    allowed: false,
                    reason: `Experience-execution cooldown active. Last execution: ${state.last_experience_execution}`,
                    recommendation: 'context-update'
                };
            }
        }

        // Check attempt limit
        if (state.experience_execution_attempts >= SAFETY_CONFIG.MAX_EXPERIENCE_EXECUTION_ATTEMPTS) {
            return {
                allowed: false,
                reason: `Too many experience-execution attempts (${state.experience_execution_attempts}). Task may need manual review.`,
                recommendation: 'fix'
            };
        }
    }

    // Prevent direct experience-execution → experience-execution transitions
    if (fromStep === 'experience-execution' && toStep === 'experience-execution') {
        return {
            allowed: false,
            reason: 'Direct experience-execution → experience-execution transition is forbidden.',
            recommendation: 'fix'
        };
    }

    // Check for rapid implementation → experience-execution cycles
    if (fromStep === 'implementation' && toStep === 'experience-execution') {
        const recentTransitions = state.transition_history.slice(0, 6); // Last 6 transitions
        const cyclePattern = recentTransitions.filter(t =>
            (t.from === 'implementation' && t.to === 'experience-execution') ||
            (t.from === 'experience-execution' && t.to === 'fix') ||
            (t.from === 'fix' && t.to === 'implementation')
        );

        if (cyclePattern.length >= 4) {
            return {
                allowed: false,
                reason: 'Detected implementation → experience-execution → fix cycle. Breaking cycle.',
                recommendation: 'context-update'
            };
        }
    }

    // All checks passed
    return {
        allowed: true,
        reason: 'Transition validated successfully.',
        recommendation: toStep
    };
}

/**
 * Reset workflow safety state (for manual intervention)
 */
async function resetSafetyState() {
    const defaultState = {
        transition_history: [],
        experience_execution_attempts: 0,
        last_experience_execution: null,
        last_implementation: null,
        consecutive_transitions: 0,
        emergency_brake_active: false
    };

    await saveSafetyState(defaultState);
    return defaultState;
}

/**
 * Get current safety status
 */
async function getSafetyStatus() {
    const state = await loadSafetyState();

    return {
        emergency_brake_active: state.emergency_brake_active,
        consecutive_transitions: state.consecutive_transitions,
        experience_execution_attempts: state.experience_execution_attempts,
        last_experience_execution: state.last_experience_execution,
        recent_transitions: state.transition_history.slice(0, 5)
    };
}

/**
 * Reset consecutive transition counter (call when workflow completes a full cycle)
 */
async function resetTransitionCounter() {
    const state = await loadSafetyState();
    state.consecutive_transitions = 0;
    await saveSafetyState(state);
}

export {
    recordTransition,
    validateTransition,
    resetSafetyState,
    getSafetyStatus,
    resetTransitionCounter,
    SAFETY_CONFIG
}; 