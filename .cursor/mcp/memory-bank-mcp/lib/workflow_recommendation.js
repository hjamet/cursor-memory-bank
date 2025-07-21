/**
 * Centralized Workflow Recommendation System
 * Harmonizes recommendation logic between remember.js and next_rule.js
 * Provides consistent workflow decisions across the autonomous system
 */

import { readUserbrief } from './userbrief_manager.js';
import { readTasks } from './task_manager.js';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Load workflow mode from workflow_state.json
 * @returns {string} - The current workflow mode ('infinite' or 'task_by_task')
 */
async function loadWorkflowMode() {
    try {
        const workflowStateFile = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'workflow_state.json');
        const workflowStateData = await fs.readFile(workflowStateFile, 'utf8');
        const workflowState = JSON.parse(workflowStateData);
        return workflowState.mode || 'infinite'; // Default to infinite if mode is not specified
    } catch (error) {
        // If file doesn't exist or is corrupted, default to infinite mode
        return 'infinite';
    }
}

/**
 * Get possible next steps based on current system state
 * @param {string} lastStep - The previous workflow step
 * @returns {Promise<string[]>} Array of possible next steps
 */
export async function getPossibleNextSteps(lastStep = null) {
    let possibleSteps = new Set();

    try {
        const userbrief = await readUserbrief();
        if (userbrief && userbrief.requests && userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress')) {
            possibleSteps.add('task-decomposition');
        }

        const tasks = await readTasks();
        if (tasks && tasks.some(t => t.status === 'TODO' || t.status === 'IN_PROGRESS')) {
            possibleSteps.add('implementation');
            // Enhanced: After implementation, prioritize testing more strongly
            if (lastStep === 'implementation') {
                possibleSteps.add('experience-execution');
                // Also check if there are tasks in REVIEW status, which indicates recent implementation
                if (tasks.some(t => t.status === 'REVIEW')) {
                    possibleSteps.add('experience-execution');
                }
            }
        }

        // Add 'fix' as a possibility only if there are blocked tasks
        if (tasks && tasks.some(t => t.status === 'BLOCKED')) {
            possibleSteps.add('fix');
        }

        // Enhanced: Also recommend experience-execution if there are tasks in REVIEW status
        // This helps validate completed implementations
        if (tasks && tasks.some(t => t.status === 'REVIEW')) {
            possibleSteps.add('experience-execution');
        }

        // Default steps that are almost always possible
        possibleSteps.add('context-update');
        possibleSteps.add('system');

        if (possibleSteps.size === 0) {
            // Fallback to a safe default if no other steps are identified
            return ['context-update', 'system'];
        }

        return Array.from(possibleSteps);

    } catch (error) {
        // This can happen on first run if no context files exist.
        // In this case, the only valid next step is to start the process.
        if (error.code === 'ENOENT') {
            return ['START'];
        }
        // Fallback to a safe default
        return ['system'];
    }
}

/**
 * Get recommended next step with safety validation
 * @param {string} lastStep - The previous workflow step
 * @param {string[]} possibleSteps - Array of possible next steps
 * @param {Object[]} tasks - Optional tasks array (will be loaded if not provided)
 * @returns {Promise<string>} Recommended next step
 */
export async function getRecommendedNextStep(lastStep, possibleSteps, tasks = null) {
    // SAFETY FIRST: Determine the optimal next step based on workflow logic
    let recommendedStep = await getRecommendedStepLogic(lastStep, possibleSteps, tasks);

    // SAFETY VALIDATION: Check if the transition is safe
    try {
        // The safety system is removed, so this block is effectively removed.
        // The recommendation logic itself should handle safe transitions.
        // If a transition is blocked, the logic will return a safe fallback.
    } catch (error) {
        // If safety system fails, fallback to 'fix' or 'implementation' (never context-update)
        console.warn(`Workflow safety system error: ${error.message}`);
        if (possibleSteps.includes('fix')) {
            recommendedStep = 'fix';
        } else if (possibleSteps.includes('implementation')) {
            recommendedStep = 'implementation';
        } else {
            recommendedStep = possibleSteps[0] || 'fix';
        }
    }

    return recommendedStep;
}

/**
 * Core recommendation logic (unified version)
 * @param {string} lastStep - The previous workflow step
 * @param {string[]} possibleSteps - Array of possible next steps
 * @param {Object[]} tasks - Optional tasks array (will be loaded if not provided)
 * @returns {Promise<string>} Recommended next step
 */
async function getRecommendedStepLogic(lastStep, possibleSteps, tasks = null) {
    // CRITICAL: Check workflow mode for task-by-task stopping logic
    const workflowMode = await loadWorkflowMode();

    // In task-by-task mode, check if we should stop at context-update
    if (workflowMode === 'task_by_task') {
        // Load userbrief and tasks to determine if we should continue or stop
        let userbrief, tasksData;
        try {
            userbrief = await readUserbrief();
            tasksData = tasks || await readTasks();
        } catch (error) {
            // If we can't load data, default to continuing with available steps
            userbrief = { requests: [] };
            tasksData = [];
        }

        // Check the specific conditions for stopping in task-by-task mode:
        // 1. No unprocessed user requests (all should be archived)
        // 2. No active tasks (TODO, IN_PROGRESS, BLOCKED)
        // 3. We are at a natural stopping point

        const hasUnprocessedRequests = userbrief && userbrief.requests &&
            userbrief.requests.some(r => r.status === 'new' || r.status === 'in_progress');

        const hasActiveTasks = tasksData && tasksData.some(t =>
            t.status === 'TODO' || t.status === 'IN_PROGRESS' || t.status === 'BLOCKED');

        // If we have no pending work and we're being asked for context-update, allow stopping
        if (!hasUnprocessedRequests && !hasActiveTasks && possibleSteps.includes('context-update')) {
            return 'context-update'; // This will trigger the stopping logic in remember.js
        }
    }

    // CRITICAL FIX: Prevent context-update loops
    // Rule: context-update can NEVER be followed by context-update (except in task-by-task stopping case)
    if (lastStep === 'context-update') {
        // Coming from context-update, we need to determine the next step based on system state

        // Load tasks if not provided
        if (!tasks) {
            try {
                tasks = await readTasks();
            } catch (error) {
                // If we can't load tasks, force implementation or task-decomposition
                if (possibleSteps.includes('task-decomposition')) {
                    return 'task-decomposition';
                }
                if (possibleSteps.includes('implementation')) {
                    return 'implementation';
                }
                // Ultimate fallback - but avoid context-update
                return possibleSteps.find(step => step !== 'context-update') || 'implementation';
            }
        }

        // Check for unprocessed requests first (highest priority)
        if (possibleSteps.includes('task-decomposition')) {
            return 'task-decomposition';
        }

        // Check for active tasks (implementation or blocked)
        if (possibleSteps.includes('implementation')) {
            return 'implementation';
        }

        // Check for blocked tasks that need fixing
        if (possibleSteps.includes('fix')) {
            return 'fix';
        }

        // Check for tasks that need validation
        if (possibleSteps.includes('experience-execution')) {
            return 'experience-execution';
        }

        // If we reach here, either the system is idle or we have no valid transitions
        // NEVER return context-update to prevent loops
        return possibleSteps.find(step => step !== 'context-update') || 'implementation';
    }

    // CRITICAL FIX: Prevent experience-execution loops
    // Rule: experience-execution can NEVER be followed by experience-execution
    if (lastStep === 'experience-execution') {
        // If coming from experience-execution, we need to determine the next step based on task status

        // Load tasks if not provided
        if (!tasks) {
            try {
                tasks = await readTasks();
            } catch (error) {
                // If we can't load tasks, default to context-update
                return 'context-update';
            }
        }

        // Find the current task (assuming it's the one that was being worked on)
        // Look for tasks that are IN_PROGRESS or recently moved to REVIEW
        const currentTask = tasks && tasks.find(t => t.status === 'IN_PROGRESS');

        if (currentTask) {
            // Task is still IN_PROGRESS, meaning experience-execution failed or was interrupted.
            // Give priority to implementation to allow the agent to continue its work.
            return 'implementation';
        } else {
            // No IN_PROGRESS task found, meaning the task was likely completed
            // Check for new user requests first (highest priority)
            if (possibleSteps.includes('task-decomposition')) {
                return 'task-decomposition';
            }
            // Otherwise, default to context-update
            return 'context-update';
        }
    }

    // ENHANCED WORKFLOW AUTOMATION: Mandatory implementation → experience-execution
    // This implements the core requirement of automated workflow
    if (lastStep === 'implementation' && possibleSteps.includes('experience-execution')) {
        // Load tasks if not provided to check for completed implementations
        if (!tasks) {
            try {
                tasks = await readTasks();
            } catch (error) {
                // If we can't load tasks, fallback to standard logic
                return getStandardRecommendation(possibleSteps);
            }
        }

        // Check if there are recently completed tasks that need testing
        const recentlyCompletedTasks = tasks && tasks.filter(t =>
            t.status === 'REVIEW' &&
            t.updated_date &&
            new Date(t.updated_date) > new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
        );

        // MANDATORY TRANSITION: Always go to experience-execution after implementation
        // Exception: Only skip if there are critical blocking issues
        const hasBlockedTasks = tasks && tasks.some(t => t.status === 'BLOCKED');
        const hasUserRequests = possibleSteps.includes('task-decomposition');

        // Skip experience-execution only in exceptional cases
        if (hasBlockedTasks && !recentlyCompletedTasks?.length) {
            return 'fix'; // Address blocking issues first
        } else if (hasUserRequests && !recentlyCompletedTasks?.length) {
            return 'task-decomposition'; // Process urgent user requests
        } else {
            // MANDATORY: Go to experience-execution to test the implementation
            return 'experience-execution';
        }
    }

    // For all other cases, use the standard recommendation logic
    return getStandardRecommendation(possibleSteps);
}

/**
 * Standard recommendation logic (priority-based)
 * @param {string[]} possibleSteps - Array of possible next steps
 * @returns {string} Recommended next step
 */
function getStandardRecommendation(possibleSteps) {
    // Prioritize task-decomposition for new user requests (highest priority)
    if (possibleSteps.includes('task-decomposition')) {
        return 'task-decomposition';
    }

    // Prioritize fix for critical issues (only if there are blocked tasks)
    if (possibleSteps.includes('fix')) {
        return 'fix';
    }

    // Then implementation for pending work
    if (possibleSteps.includes('implementation')) {
        return 'implementation';
    }

    // Experience-execution for testing/validation
    if (possibleSteps.includes('experience-execution')) {
        return 'experience-execution';
    }

    // Context-update ONLY if nothing else is possible (idle/end)
    if (possibleSteps.includes('context-update') && possibleSteps.length === 1) {
        return 'context-update';
    }

    // Ultimate fallback
    return possibleSteps[0] || 'fix';
}

/**
 * Analyze system state to determine optimal next workflow step
 * Unified version that combines both simple state analysis and contextual logic
 * @param {Object} context - System context including tasks and requests
 * @returns {Promise<Object>} Analysis result with recommended step and reasoning
 */
export async function analyzeSystemState(context) {
    // Load fresh task data
    let tasks;
    try {
        tasks = await readTasks();
    } catch (error) {
        tasks = [];
    }

    // Count tasks by status
    const taskCounts = {
        TODO: tasks.filter(t => t.status === 'TODO').length,
        IN_PROGRESS: tasks.filter(t => t.status === 'IN_PROGRESS').length,
        BLOCKED: tasks.filter(t => t.status === 'BLOCKED').length,
        REVIEW: tasks.filter(t => t.status === 'REVIEW').length,
        DONE: tasks.filter(t => t.status === 'DONE').length
    };

    // Check for unprocessed requests
    const unprocessedRequests = context.unprocessed_requests || [];
    const hasUnprocessedRequests = unprocessedRequests.length > 0;
    const hasActionableTasks = taskCounts.TODO > 0 || taskCounts.IN_PROGRESS > 0 || taskCounts.BLOCKED > 0 || taskCounts.REVIEW > 0;

    // Use unified recommendation logic
    const possibleSteps = await getPossibleNextSteps(context.previous_rule);
    const recommendedStep = await getRecommendedNextStep(context.previous_rule, possibleSteps, tasks);

    // Generate reasoning based on the recommendation
    let reasoning = 'Default system analysis and planning';

    if (hasUnprocessedRequests && recommendedStep === 'task-decomposition') {
        reasoning = `${unprocessedRequests.length} unprocessed user requests need to be converted to tasks`;
    } else if (taskCounts.IN_PROGRESS > 0 && recommendedStep === 'implementation') {
        reasoning = `${taskCounts.IN_PROGRESS} tasks currently in progress need completion`;
    } else if (taskCounts.BLOCKED > 0 && recommendedStep === 'fix') {
        reasoning = `${taskCounts.BLOCKED} blocked tasks need resolution`;
    } else if (taskCounts.TODO > 0 && recommendedStep === 'implementation') {
        reasoning = `${taskCounts.TODO} TODO tasks ready for execution`;
    } else if (taskCounts.REVIEW > 0 && recommendedStep === 'experience-execution') {
        reasoning = `${taskCounts.REVIEW} tasks need review and testing`;
    } else if (!hasActionableTasks && !hasUnprocessedRequests) {
        reasoning = 'All tasks are done and no new requests. The workflow can stop.';
    } else if (recommendedStep === 'experience-execution') {
        reasoning = 'Implementation completed, mandatory testing required';
    } else if (recommendedStep === 'context-update') {
        reasoning = 'Context refresh or workflow safety intervention required';
    }

    return {
        recommendedStep,
        reasoning,
        systemState: {
            taskCounts,
            unprocessedRequestCount: unprocessedRequests.length,
            totalTasks: tasks.length
        }
    };
} 