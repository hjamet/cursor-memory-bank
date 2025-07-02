import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { calculateTaskStatistics, getTasksByCategory, STATUS_CATEGORIES } from '../lib/task_statistics.js';

// Calculate dynamic path relative to the MCP server location
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'streamlit_app', 'tasks.json');

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

const STATUS_ORDER = {
    'IN_PROGRESS': 1,
    'TODO': 2,
    'BLOCKED': 3,
    'REVIEW': 4,
    'DONE': 5,
};

/**
 * Handles the get_all_tasks tool call
 * Returns all tasks except completed ones, with priority ordering: in_progress, todo, blocked, review
 * 
 * @param {Object} params - Tool parameters (no parameters needed)
 * @returns {Object} Tool response with all non-completed tasks
 */
export async function handleGetAllTasks(params) {
    try {
        const { status, priority, search, sort_by = 'priority' } = params || {};

        const tasksData = await readTasks();

        // Use centralized filtering logic - exclude completed tasks
        const activeAndReviewTasks = await getTasksByCategory('ACTIVE', tasksData);
        const pendingReviewTasks = await getTasksByCategory('PENDING_REVIEW', tasksData);
        let filteredTasks = [...activeAndReviewTasks, ...pendingReviewTasks];

        // Sort tasks by status order, then priority
        filteredTasks.sort((a, b) => {
            const statusA = STATUS_ORDER[a.status] || 99;
            const statusB = STATUS_ORDER[b.status] || 99;
            if (statusA !== statusB) {
                return statusA - statusB;
            }
            return (b.priority || 3) - (a.priority || 3); // Higher priority first
        });

        // Use all filtered tasks (no pagination)
        const paginatedTasks = filteredTasks;

        // Enhance tasks with additional information
        const enhancedTasks = paginatedTasks.map(task => {
            const baseTask = { ...task };

            // Always add dependency information
            if (task.dependencies && task.dependencies.length > 0) {
                const dependencyDetails = task.dependencies.map(depId => {
                    const depTask = tasksData.find(t => t.id === depId);
                    return depTask
                        ? { id: depTask.id, title: depTask.title, status: depTask.status }
                        : { id: depId, title: 'Unknown Task', status: 'NOT_FOUND' };
                });
                baseTask.dependency_details = dependencyDetails;
                baseTask.all_dependencies_completed = dependencyDetails.every(
                    dep => dep.status === 'DONE' || dep.status === 'APPROVED' || dep.status === 'REVIEW' || dep.status === 'NOT_FOUND'
                );
            }

            // Add parent information if it's a subtask
            if (task.parent_id) {
                const parentTask = tasksData.find(t => t.id === task.parent_id);
                baseTask.parent_info = parentTask
                    ? { id: parentTask.id, title: parentTask.title, status: parentTask.status }
                    : { id: task.parent_id, title: 'Unknown Parent', status: 'NOT_FOUND' };
            }

            // Add subtask information if it's a parent task
            const subtasks = tasksData.filter(t => t.parent_id === task.id);
            if (subtasks.length > 0) {
                baseTask.subtasks = subtasks.map(sub => ({ id: sub.id, title: sub.title, status: sub.status }));
                baseTask.subtask_count = subtasks.length;
                baseTask.completed_subtasks = subtasks.filter(st => st.status === 'DONE' || st.status === 'APPROVED' || st.status === 'REVIEW').length;
            }

            return baseTask;
        });

        // Use centralized statistics calculation
        const centralizedStats = await calculateTaskStatistics(tasksData);

        // Generate comprehensive statistics with validation results
        const statistics = {
            total_tasks: centralizedStats.total_tasks,
            tasks_returned: enhancedTasks.length,
            status_breakdown: centralizedStats.status_breakdown,
            category_totals: centralizedStats.category_totals,
            priority_breakdown: centralizedStats.priority_breakdown,
            task_types: centralizedStats.task_types,
            dependency_analysis: centralizedStats.dependency_analysis,
            filters_applied: {
                status_filter: "Excludes DONE and APPROVED tasks (completed)",
                priority_filter: null,
                include_subtasks: true,
                include_dependencies: true
            },
            data_validation: {
                has_integrity_issues: centralizedStats.validation_results.hasErrors || centralizedStats.validation_results.hasWarnings,
                validation_errors: centralizedStats.validation_results.errors,
                validation_warnings: centralizedStats.validation_results.warnings
            },
            timestamp: centralizedStats.timestamp
        };

        const response = {
            status: 'success',
            message: `Retrieved ${enhancedTasks.length} non-completed tasks in priority order`,
            workflow_reminder: "IMPORTANT: You are in a workflow. Process ONLY ONE task at a time. After completing this task, you MUST call remember() to continue the workflow.",
            tasks: enhancedTasks,
            statistics,
            query_info: {
                count_returned: enhancedTasks.length,
                priority_order: 'IN_PROGRESS → TODO → BLOCKED → REVIEW (excludes DONE & APPROVED)',
                filters_applied: "Excludes completed tasks (DONE, APPROVED)",
                data_integrity_status: statistics.data_validation.has_integrity_issues ? 'ISSUES_DETECTED' : 'VALIDATED'
            }
        };

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error retrieving tasks: ${error.message}`,
                    tasks: [],
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message,
                        timestamp: new Date().toISOString()
                    }
                }, null, 2)
            }]
        };
    }
} 