import { z } from 'zod';
import { taskManager } from '../lib/task_manager.js';

/**
 * Handles the get_all_tasks tool call
 * Returns tasks with priority ordering: in_progress, todo, blocked, review, done
 * 
 * @param {Object} params - Tool parameters
 * @param {number} [params.count=10] - Number of tasks to return
 * @param {string} [params.status_filter] - Filter by specific status
 * @param {number} [params.priority_filter] - Filter by specific priority
 * @param {boolean} [params.include_subtasks=true] - Include sub-tasks
 * @param {boolean} [params.include_dependencies=true] - Include dependency info
 * @returns {Object} Tool response with prioritized tasks
 */
export async function handleGetAllTasks(params) {
    try {
        const {
            count = 10,
            status_filter,
            priority_filter,
            include_subtasks = true,
            include_dependencies = true
        } = params;

        console.log(`[GetAllTasks] Retrieving ${count} tasks with priority ordering`);

        // Get all tasks using TaskManager with priority sorting
        const options = {
            limit: count
        };

        // Apply status filter if specified
        if (status_filter) {
            options.status = status_filter;
        }

        let allTasks = taskManager.getAllTasks(options);

        // Apply additional filters
        if (priority_filter) {
            allTasks = allTasks.filter(task => task.priority === priority_filter);
        }

        if (!include_subtasks) {
            allTasks = allTasks.filter(task => task.parent_id === null);
        }

        // Apply count limit after filtering
        allTasks = allTasks.slice(0, count);

        // Enhance tasks with additional information
        const enhancedTasks = allTasks.map(task => {
            const baseTask = {
                id: task.id,
                title: task.title,
                short_description: task.short_description,
                status: task.status,
                priority: task.priority,
                parent_id: task.parent_id,
                created_date: task.created_date,
                updated_date: task.updated_date
            };

            // Add dependency information if requested
            if (include_dependencies) {
                const dependencyDetails = task.dependencies.map(depId => {
                    const depTask = taskManager.getTaskById(depId);
                    return depTask ? {
                        id: depTask.id,
                        title: depTask.title,
                        status: depTask.status,
                        short_description: depTask.short_description
                    } : {
                        id: depId,
                        title: 'Unknown Task',
                        status: 'NOT_FOUND',
                        short_description: 'Task not found in system'
                    };
                });

                baseTask.dependencies = task.dependencies;
                baseTask.dependency_details = dependencyDetails;
                baseTask.all_dependencies_completed = dependencyDetails.every(dep =>
                    dep.status === 'DONE' || dep.status === 'NOT_FOUND'
                );
            }

            // Add parent information if it's a subtask
            if (task.parent_id) {
                const parentTask = taskManager.getTaskById(task.parent_id);
                baseTask.parent_info = parentTask ? {
                    id: parentTask.id,
                    title: parentTask.title,
                    status: parentTask.status
                } : {
                    id: task.parent_id,
                    title: 'Unknown Parent',
                    status: 'NOT_FOUND'
                };
            }

            // Add subtask information if it's a parent task
            const subtasks = taskManager.getAllTasks({ parent_id: task.id });
            if (subtasks.length > 0) {
                baseTask.subtasks = subtasks.map(subtask => ({
                    id: subtask.id,
                    title: subtask.title,
                    status: subtask.status,
                    short_description: subtask.short_description
                }));
                baseTask.subtask_count = subtasks.length;
                baseTask.completed_subtasks = subtasks.filter(st => st.status === 'DONE').length;
            }

            return baseTask;
        });

        // Generate comprehensive statistics
        const allTasksForStats = taskManager.getAllTasks();
        const statistics = {
            total_tasks: allTasksForStats.length,
            tasks_returned: enhancedTasks.length,
            status_breakdown: {
                TODO: allTasksForStats.filter(t => t.status === 'TODO').length,
                IN_PROGRESS: allTasksForStats.filter(t => t.status === 'IN_PROGRESS').length,
                DONE: allTasksForStats.filter(t => t.status === 'DONE').length,
                BLOCKED: allTasksForStats.filter(t => t.status === 'BLOCKED').length,
                REVIEW: allTasksForStats.filter(t => t.status === 'REVIEW').length
            },
            priority_breakdown: {
                'Priority 1 (Highest)': allTasksForStats.filter(t => t.priority === 1).length,
                'Priority 2': allTasksForStats.filter(t => t.priority === 2).length,
                'Priority 3 (Medium)': allTasksForStats.filter(t => t.priority === 3).length,
                'Priority 4': allTasksForStats.filter(t => t.priority === 4).length,
                'Priority 5 (Lowest)': allTasksForStats.filter(t => t.priority === 5).length
            },
            task_types: {
                main_tasks: allTasksForStats.filter(t => t.parent_id === null).length,
                subtasks: allTasksForStats.filter(t => t.parent_id !== null).length
            },
            filters_applied: {
                status_filter: status_filter || null,
                priority_filter: priority_filter || null,
                include_subtasks,
                include_dependencies
            }
        };

        const response = {
            status: 'success',
            message: `Retrieved ${enhancedTasks.length} tasks in priority order`,
            tasks: enhancedTasks,
            statistics,
            query_info: {
                count_requested: count,
                count_returned: enhancedTasks.length,
                priority_order: 'IN_PROGRESS → TODO → BLOCKED → REVIEW → DONE',
                filters_applied: Object.keys(params).filter(key => key !== 'count').length
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