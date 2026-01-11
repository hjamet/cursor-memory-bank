import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Calculate dynamic path relative to the MCP server location
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'tasks.json');

/**
 * Centralized task statistics calculator
 * This module provides a single source of truth for task statistics
 * to prevent inconsistencies across different tools and contexts.
 */

/**
 * Status definitions with their semantic meanings
 */
export const TASK_STATUSES = {
    TODO: 'TODO',
    IN_PROGRESS: 'IN_PROGRESS',
    BLOCKED: 'BLOCKED',
    REVIEW: 'REVIEW',
    DONE: 'DONE',
    APPROVED: 'APPROVED'
};

/**
 * Status categories for consistent filtering
 */
export const STATUS_CATEGORIES = {
    ACTIVE: ['TODO', 'IN_PROGRESS', 'BLOCKED'],
    COMPLETED: ['DONE', 'APPROVED'],
    PENDING_REVIEW: ['REVIEW'],
    ALL: ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REVIEW', 'DONE', 'APPROVED']
};

/**
 * Read tasks from the canonical tasks.json file
 * @returns {Promise<Array>} Array of task objects
 */
async function readTasks() {
    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return [];
        }
        throw error;
    }
}

/**
 * Calculate comprehensive task statistics with validation
 * @param {Array} tasks - Array of task objects (optional, will read from file if not provided)
 * @returns {Promise<Object>} Comprehensive statistics object
 */
export async function calculateTaskStatistics(tasks = null) {
    const allTasks = tasks || await readTasks();

    // Validate task data integrity
    const validationResults = validateTaskData(allTasks);
    if (validationResults.hasErrors) {
        console.warn('[TaskStatistics] Data integrity issues detected:', validationResults.errors);
    }

    // Calculate status breakdown
    const statusBreakdown = {};
    for (const status of STATUS_CATEGORIES.ALL) {
        statusBreakdown[status] = allTasks.filter(task => task.status === status).length;
    }

    // Calculate category totals
    const categoryTotals = {
        active: STATUS_CATEGORIES.ACTIVE.reduce((sum, status) => sum + statusBreakdown[status], 0),
        completed: STATUS_CATEGORIES.COMPLETED.reduce((sum, status) => sum + statusBreakdown[status], 0),
        pending_review: STATUS_CATEGORIES.PENDING_REVIEW.reduce((sum, status) => sum + statusBreakdown[status], 0),
        total: allTasks.length
    };

    // Calculate priority breakdown
    const priorityBreakdown = {};
    for (let i = 1; i <= 5; i++) {
        priorityBreakdown[`Priority ${i}`] = allTasks.filter(task => (task.priority || 3) === i).length;
    }

    // Calculate task types
    const taskTypes = {
        main_tasks: allTasks.filter(task => !task.parent_id).length,
        subtasks: allTasks.filter(task => task.parent_id).length
    };

    // Calculate dependency analysis
    const dependencyAnalysis = {
        tasks_with_dependencies: allTasks.filter(task => task.dependencies && task.dependencies.length > 0).length,
        tasks_without_dependencies: allTasks.filter(task => !task.dependencies || task.dependencies.length === 0).length
    };

    // Generate timestamp for cache invalidation
    const timestamp = new Date().toISOString();

    return {
        timestamp,
        total_tasks: allTasks.length,
        status_breakdown: statusBreakdown,
        category_totals: categoryTotals,
        priority_breakdown: priorityBreakdown,
        task_types: taskTypes,
        dependency_analysis: dependencyAnalysis,
        validation_results: validationResults,
        // Legacy format for backward compatibility
        current_tasks_summary: `Tasks: ${statusBreakdown.TODO} TODO, ${statusBreakdown.IN_PROGRESS} IN_PROGRESS, ${statusBreakdown.BLOCKED} BLOCKED, ${statusBreakdown.REVIEW} REVIEW, ${statusBreakdown.DONE} DONE`
    };
}

/**
 * Get filtered tasks by category
 * @param {string} category - Category name from STATUS_CATEGORIES
 * @param {Array} tasks - Array of task objects (optional)
 * @returns {Promise<Array>} Filtered tasks
 */
export async function getTasksByCategory(category, tasks = null) {
    const allTasks = tasks || await readTasks();

    if (!STATUS_CATEGORIES[category]) {
        throw new Error(`Invalid category: ${category}. Valid categories: ${Object.keys(STATUS_CATEGORIES).join(', ')}`);
    }

    const allowedStatuses = STATUS_CATEGORIES[category];
    return allTasks.filter(task => allowedStatuses.includes(task.status));
}

/**
 * Validate task data integrity
 * @param {Array} tasks - Array of task objects
 * @returns {Object} Validation results
 */
function validateTaskData(tasks) {
    const errors = [];
    const warnings = [];

    // Check for duplicate IDs
    const ids = tasks.map(task => task.id);
    const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
        errors.push(`Duplicate task IDs found: ${[...new Set(duplicateIds)].join(', ')}`);
    }

    // Check for invalid statuses
    const validStatuses = STATUS_CATEGORIES.ALL;
    const invalidStatuses = tasks.filter(task => !validStatuses.includes(task.status));
    if (invalidStatuses.length > 0) {
        errors.push(`Tasks with invalid status: ${invalidStatuses.map(t => `${t.id}:${t.status}`).join(', ')}`);
    }

    // Check for missing required fields
    const requiredFields = ['id', 'title', 'status'];
    const tasksWithMissingFields = tasks.filter(task =>
        requiredFields.some(field => task[field] === undefined || task[field] === null)
    );
    if (tasksWithMissingFields.length > 0) {
        errors.push(`Tasks with missing required fields: ${tasksWithMissingFields.map(t => t.id || 'unknown').join(', ')}`);
    }

    // Check for orphaned dependencies
    const allIds = new Set(ids);
    const orphanedDependencies = [];
    tasks.forEach(task => {
        if (task.dependencies) {
            task.dependencies.forEach(depId => {
                if (!allIds.has(depId)) {
                    orphanedDependencies.push(`Task ${task.id} depends on non-existent task ${depId}`);
                }
            });
        }
    });
    if (orphanedDependencies.length > 0) {
        warnings.push(`Orphaned dependencies: ${orphanedDependencies.join(', ')}`);
    }

    return {
        hasErrors: errors.length > 0,
        hasWarnings: warnings.length > 0,
        errors,
        warnings,
        total_tasks_validated: tasks.length
    };
}

/**
 * Get consistent task summary string
 * @param {Object} statistics - Statistics object from calculateTaskStatistics
 * @returns {string} Formatted summary string
 */
export function formatTaskSummary(statistics) {
    const { status_breakdown } = statistics;
    return `Tasks: ${status_breakdown.TODO} TODO, ${status_breakdown.IN_PROGRESS} IN_PROGRESS, ${status_breakdown.BLOCKED} BLOCKED, ${status_breakdown.REVIEW} REVIEW, ${status_breakdown.DONE} DONE`;
}

/**
 * Export the tasks file path for consistency
 */
export { TASKS_FILE_PATH }; 