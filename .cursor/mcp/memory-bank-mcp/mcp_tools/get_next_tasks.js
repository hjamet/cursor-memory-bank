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

/**
 * Handles the get_next_tasks tool call
 * Returns available tasks (tasks with no pending dependencies)
 * 
 * @param {Object} params - Tool parameters
 * @param {number} [params.limit=10] - Maximum number of tasks to return
 * @param {boolean} [params.include_completed=false] - Include completed tasks
 * @param {boolean} [params.include_blocked=false] - Include blocked tasks
 * @param {string} [params.status_filter] - Filter by specific status
 * @param {number} [params.priority_filter] - Filter by specific priority
 * @returns {Object} Tool response with available tasks
 */
export async function handleGetNextTasks(params) {
    try {
        const {
            limit = 10,
            include_completed = false,
            include_blocked = false,
            status_filter,
            priority_filter
        } = params;

        console.log(`[GetNextTasks] Retrieving next available tasks (limit: ${limit})`);

        const allTasks = await readTasks();

        // First, create a map for quick lookups
        const taskMap = new Map(allTasks.map(task => [task.id, task]));

        // Determine available tasks
        let availableTasks = allTasks.filter(task => {
            if (!include_completed && task.status === 'DONE') return false;
            if (!include_blocked && task.status === 'BLOCKED') return false;
            if (task.dependencies.length === 0) return true;

            return task.dependencies.every(depId => {
                const depTask = taskMap.get(depId);
                return !depTask || depTask.status === 'DONE';
            });
        });

        // Apply additional filters if specified
        if (status_filter) {
            availableTasks = availableTasks.filter(task => task.status === status_filter);
        }

        if (priority_filter) {
            availableTasks = availableTasks.filter(task => task.priority === priority_filter);
        }

        // Sort by priority
        availableTasks.sort((a, b) => (a.priority || 3) - (b.priority || 3));

        // Apply limit after filtering
        const paginatedTasks = availableTasks.slice(0, limit);

        // Enhance tasks with dependency information
        const enhancedTasks = paginatedTasks.map(task => {
            const dependencyDetails = task.dependencies.map(depId => {
                const depTask = taskMap.get(depId);
                return depTask ? {
                    id: depTask.id,
                    title: depTask.title,
                    status: depTask.status
                } : {
                    id: depId,
                    title: 'Unknown Task',
                    status: 'NOT_FOUND'
                };
            });

            return {
                id: task.id,
                title: task.title,
                short_description: task.short_description,
                status: task.status,
                priority: task.priority,
                dependencies: task.dependencies,
                dependency_details: dependencyDetails,
                is_available: dependencyDetails.every(dep => dep.status === 'DONE' || dep.status === 'NOT_FOUND'),
                parent_id: task.parent_id,
                created_date: task.created_date,
                updated_date: task.updated_date
            };
        });

        // Generate statistics
        const statistics = {
            total_tasks: allTasks.length,
            available_tasks_count: availableTasks.length, // Total available before pagination
            tasks_returned: enhancedTasks.length,
            status_breakdown: allTasks.reduce((acc, task) => {
                acc[task.status] = (acc[task.status] || 0) + 1;
                return acc;
            }, {}),
            filters_applied: {
                status_filter: status_filter || null,
                priority_filter: priority_filter || null,
                include_completed,
                include_blocked
            }
        };

        const response = {
            status: 'success',
            message: `Found ${enhancedTasks.length} available tasks`,
            available_tasks: enhancedTasks,
            statistics,
            query_info: {
                limit_requested: limit,
                filters_applied: Object.keys(params).filter(key => key !== 'limit').length,
                total_available: availableTasks.length
            }
        };

        console.log(`[GetNextTasks] Returning ${enhancedTasks.length} available tasks`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[GetNextTasks] Error:', error);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error retrieving next tasks: ${error.message}`,
                    available_tasks: [],
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message
                    }
                }, null, 2)
            }]
        };
    }
} 