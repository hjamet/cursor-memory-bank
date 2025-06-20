import { z } from 'zod';
import { taskManager } from '../lib/task_manager.js';

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

        // Get available tasks using TaskManager
        const options = {
            limit,
            includeCompleted: include_completed,
            includeBlocked: include_blocked
        };

        let availableTasks = taskManager.getNextTasks(options);

        // Apply additional filters if specified
        if (status_filter) {
            availableTasks = availableTasks.filter(task => task.status === status_filter);
        }

        if (priority_filter) {
            availableTasks = availableTasks.filter(task => task.priority === priority_filter);
        }

        // Apply limit after filtering
        availableTasks = availableTasks.slice(0, limit);

        // Enhance tasks with dependency information
        const enhancedTasks = availableTasks.map(task => {
            const dependencyDetails = task.dependencies.map(depId => {
                const depTask = taskManager.getTaskById(depId);
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
        const allTasks = taskManager.getAllTasks();
        const statistics = {
            total_tasks: allTasks.length,
            available_tasks: enhancedTasks.length,
            tasks_returned: enhancedTasks.length,
            status_breakdown: {
                TODO: allTasks.filter(t => t.status === 'TODO').length,
                IN_PROGRESS: allTasks.filter(t => t.status === 'IN_PROGRESS').length,
                DONE: allTasks.filter(t => t.status === 'DONE').length,
                BLOCKED: allTasks.filter(t => t.status === 'BLOCKED').length,
                REVIEW: allTasks.filter(t => t.status === 'REVIEW').length
            },
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
                filters_applied: Object.keys(params).length - 1, // Exclude limit
                total_available: enhancedTasks.length
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