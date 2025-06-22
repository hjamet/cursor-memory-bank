import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';

// Use the absolute path that we know works
const TASKS_FILE_PATH = 'C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\memory-bank\\streamlit_app\\tasks.json';

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
        console.log(`[GetAllTasks] Retrieving all non-completed tasks.`);

        let allTasks = await readTasks();

        // Filter out completed tasks
        let filteredTasks = allTasks.filter(task => task.status !== 'DONE');

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
                    const depTask = allTasks.find(t => t.id === depId);
                    return depTask
                        ? { id: depTask.id, title: depTask.title, status: depTask.status }
                        : { id: depId, title: 'Unknown Task', status: 'NOT_FOUND' };
                });
                baseTask.dependency_details = dependencyDetails;
                baseTask.all_dependencies_completed = dependencyDetails.every(
                    dep => dep.status === 'DONE' || dep.status === 'NOT_FOUND'
                );
            }

            // Add parent information if it's a subtask
            if (task.parent_id) {
                const parentTask = allTasks.find(t => t.id === task.parent_id);
                baseTask.parent_info = parentTask
                    ? { id: parentTask.id, title: parentTask.title, status: parentTask.status }
                    : { id: task.parent_id, title: 'Unknown Parent', status: 'NOT_FOUND' };
            }

            // Add subtask information if it's a parent task
            const subtasks = allTasks.filter(t => t.parent_id === task.id);
            if (subtasks.length > 0) {
                baseTask.subtasks = subtasks.map(sub => ({ id: sub.id, title: sub.title, status: sub.status }));
                baseTask.subtask_count = subtasks.length;
                baseTask.completed_subtasks = subtasks.filter(st => st.status === 'DONE').length;
            }

            return baseTask;
        });

        // Generate comprehensive statistics from the full unfiltered list
        const statistics = {
            total_tasks: allTasks.length,
            tasks_returned: enhancedTasks.length,
            status_breakdown: allTasks.reduce((acc, task) => {
                acc[task.status] = (acc[task.status] || 0) + 1;
                return acc;
            }, {}),
            priority_breakdown: allTasks.reduce((acc, task) => {
                const priority = `Priority ${task.priority}`;
                acc[priority] = (acc[priority] || 0) + 1;
                return acc;
            }, {}),
            task_types: {
                main_tasks: allTasks.filter(t => !t.parent_id).length,
                subtasks: allTasks.filter(t => t.parent_id).length
            },
            filters_applied: {
                status_filter: "Excludes DONE tasks",
                priority_filter: null,
                include_subtasks: true,
                include_dependencies: true
            }
        };

        const response = {
            status: 'success',
            message: `Retrieved ${enhancedTasks.length} non-completed tasks in priority order`,
            tasks: enhancedTasks,
            statistics,
            query_info: {
                count_returned: enhancedTasks.length,
                priority_order: 'IN_PROGRESS → TODO → BLOCKED → REVIEW (excludes DONE)',
                filters_applied: "Excludes completed tasks only"
            }
        };

        console.log(`[GetAllTasks] Returning ${enhancedTasks.length} tasks in priority order`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[GetAllTasks] Error:', error);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error retrieving tasks: ${error.message}`,
                    tasks: [],
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message
                    }
                }, null, 2)
            }]
        };
    }
} 