import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Calculate dynamic path relative to the MCP server location
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', '..', 'memory-bank', 'workflow', 'tasks.json');

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

async function writeTasks(tasks) {
    await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
}

/**
 * Checks if all dependencies of a task are completed (DONE, REVIEW, or APPROVED)
 * @param {Object} task - Task to check
 * @param {Array} allTasks - All tasks in the system
 * @returns {boolean} True if all dependencies are completed
 */
function areAllDependenciesCompleted(task, allTasks) {
    if (!task.dependencies || task.dependencies.length === 0) {
        return true;
    }

    const taskMap = new Map(allTasks.map(t => [t.id, t]));

    return task.dependencies.every(depId => {
        const depTask = taskMap.get(depId);
        return depTask && (depTask.status === 'DONE' || depTask.status === 'REVIEW' || depTask.status === 'APPROVED');
    });
}

/**
 * Finds and unblocks tasks that were waiting for the updated task
 * @param {number} updatedTaskId - ID of the task that was just updated
 * @param {Array} tasks - All tasks in the system
 * @returns {Array} Array of unblocked task IDs
 */
function checkAndUnblockDependentTasks(updatedTaskId, tasks) {
    const unblockedTasks = [];

    tasks.forEach(task => {
        // Skip if task is already completed or doesn't have dependencies
        if (task.status === 'DONE' || task.status === 'REVIEW' || task.status === 'APPROVED' ||
            !task.dependencies || task.dependencies.length === 0) {
            return;
        }

        // Check if this task depends on the updated task and is currently blocked
        if (task.status === 'BLOCKED' && task.dependencies.includes(updatedTaskId)) {
            // Check if all dependencies are now completed
            if (areAllDependenciesCompleted(task, tasks)) {
                task.status = 'TODO';
                task.updated_date = new Date().toISOString();

                // Add automatic unblocking comment
                const unblockedComment = {
                    timestamp: new Date().toISOString(),
                    comment: `Task automatically unblocked: all dependencies are now completed (including task ${updatedTaskId})`,
                    status_change: 'TODO'
                };

                task.comments = task.comments || [];
                task.comments.push(unblockedComment);
                task.last_comment = unblockedComment.comment;
                task.last_comment_timestamp = unblockedComment.timestamp;

                unblockedTasks.push(task.id);
            }
        }
    });

    return unblockedTasks;
}

/**
 * Removes dependencies to non-existent tasks (orphaned dependencies)
 * @param {Array} tasks - All tasks in the system
 * @returns {Array} Array of task IDs that had orphaned dependencies cleaned up
 */
function cleanupOrphanedDependencies(tasks) {
    const taskIds = new Set(tasks.map(t => t.id));
    const cleanedUpTasks = [];

    tasks.forEach(task => {
        if (!task.dependencies || task.dependencies.length === 0) {
            return;
        }

        const originalDependencies = [...task.dependencies];
        const validDependencies = task.dependencies.filter(depId => taskIds.has(depId));

        if (validDependencies.length !== originalDependencies.length) {
            const removedDependencies = originalDependencies.filter(depId => !taskIds.has(depId));
            task.dependencies = validDependencies;
            task.updated_date = new Date().toISOString();

            // Add cleanup comment
            const cleanupComment = {
                timestamp: new Date().toISOString(),
                comment: `Orphaned dependencies automatically removed: tasks ${removedDependencies.join(', ')} no longer exist`,
                status_change: task.status
            };

            task.comments = task.comments || [];
            task.comments.push(cleanupComment);
            task.last_comment = cleanupComment.comment;
            task.last_comment_timestamp = cleanupComment.timestamp;

            cleanedUpTasks.push(task.id);

            // If task was blocked and now has no dependencies or all dependencies are completed, unblock it
            if (task.status === 'BLOCKED' && areAllDependenciesCompleted(task, tasks)) {
                task.status = 'TODO';

                const unblockedComment = {
                    timestamp: new Date().toISOString(),
                    comment: 'Task automatically unblocked after orphaned dependency cleanup',
                    status_change: 'TODO'
                };

                task.comments.push(unblockedComment);
                task.last_comment = unblockedComment.comment;
                task.last_comment_timestamp = unblockedComment.timestamp;
            }
        }
    });

    return cleanedUpTasks;
}

/**
 * Handles the update-task tool call
 * Updates existing tasks by ID with only the provided fields
 * 
 * @param {Object} params - Tool parameters
 * @param {number} params.task_id - ID of task to update
 * @param {string} params.comment - Required comment explaining the update
 * @param {string} [params.title] - Updated title
 * @param {string} [params.short_description] - Updated brief description
 * @param {string} [params.detailed_description] - Updated detailed description
 * @param {number[]} [params.dependencies] - Updated dependencies
 * @param {string} [params.status] - Updated status
 * @param {string[]} [params.impacted_files] - Updated affected files
 * @param {string} [params.validation_criteria] - Updated validation criteria
 * @param {number|null} [params.parent_id] - Updated parent task ID
 * @param {number} [params.priority] - Updated priority level
 * @param {string} [params.image] - Updated image path for the task
 * @returns {Object} Tool response with updated task information
 */
export async function handleUpdateTask(params) {
    try {
        const { task_id, comment, ...updates } = params;

        const tasks = await readTasks();
        const taskIndex = tasks.findIndex(task => task.id === task_id);

        if (taskIndex === -1) {
            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Task with ID ${task_id} not found`,
                        updated_task: null
                    }, null, 2)
                }]
            };
        }

        const existingTask = { ...tasks[taskIndex] };

        // Validate parent task exists if parent_id is being updated
        if (updates.parent_id !== undefined && updates.parent_id !== null) {
            const parentTask = tasks.find(task => task.id === updates.parent_id);
            if (!parentTask) {
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: `Parent task with ID ${updates.parent_id} not found`,
                            updated_task: null
                        }, null, 2)
                    }]
                };
            }

            // Prevent setting self as parent
            if (updates.parent_id === task_id) {
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: 'Task cannot be its own parent',
                            updated_task: null
                        }, null, 2)
                    }]
                };
            }
        }

        // Add the comment to the task's comment history
        // For IN_PROGRESS status, allow empty comments as no justification is needed
        const effectiveComment = comment || (updates.status === 'IN_PROGRESS' ? 'Task started' : comment);
        const commentEntry = {
            timestamp: new Date().toISOString(),
            comment: effectiveComment,
            status_change: updates.status || existingTask.status
        };

        // Initialize comments array if it doesn't exist (for backward compatibility)
        const existingComments = existingTask.comments || [];
        const updatedComments = [...existingComments, commentEntry];

        // Create the updated task object
        const updatedTask = {
            ...existingTask,
            ...Object.fromEntries(Object.entries(updates).filter(([_, v]) => v !== undefined)),
            comments: updatedComments,
            last_comment: effectiveComment,
            last_comment_timestamp: commentEntry.timestamp,
            updated_date: new Date().toISOString()
        };

        tasks[taskIndex] = updatedTask;

        // Automatic dependency management when task status changes to REVIEW or DONE
        let unblockedTasks = [];
        let cleanedUpTasks = [];

        if (updates.status && (updates.status === 'REVIEW' || updates.status === 'DONE')) {
            // First, clean up orphaned dependencies across all tasks
            cleanedUpTasks = cleanupOrphanedDependencies(tasks);

            // Then, check and unblock tasks that were waiting for this task
            unblockedTasks = checkAndUnblockDependentTasks(task_id, tasks);
        }

        await writeTasks(tasks);

        // Prepare success response
        const response = {
            status: 'success',
            message: `Task ${task_id} updated successfully`,
            workflow_reminder: "IMPORTANT: You are in a workflow. After this update, you MUST call remember() to continue.",
            updated_task: updatedTask,
            changes_made: {
                fields_updated: Object.keys(updates).filter(k => updates[k] !== undefined),
                update_count: Object.keys(updates).filter(k => updates[k] !== undefined).length,
                previous_status: existingTask.status,
                new_status: updatedTask.status
            },
            summary: {
                task_id: updatedTask.id,
                has_dependencies: updatedTask.dependencies.length > 0,
                dependency_count: updatedTask.dependencies.length,
                is_subtask: updatedTask.parent_id !== null,
                priority_level: updatedTask.priority,
                status_changed: existingTask.status !== updatedTask.status
            },
            automatic_actions: {
                unblocked_tasks: unblockedTasks,
                cleaned_up_tasks: cleanedUpTasks,
                total_affected_tasks: unblockedTasks.length + cleanedUpTasks.length
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
                    message: `Error updating task: ${error.message}`,
                    updated_task: null,
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message,
                        task_id: params.task_id
                    }
                }, null, 2)
            }]
        };
    }
} 