import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

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
 * Handles the update-task tool call.
 * This tool updates an existing task by its ID. It is designed to enforce a high standard of communication and accountability.
 *
 * **CRITICAL ANALYSIS IS MANDATORY.**
 * When updating a task, especially to `BLOCKED` or `REVIEW`, the `comment` field is not just for notes—it's for critical analysis.
 *
 * - **For `BLOCKED` status**: Clearly explain the root cause of the blockage. What are the specific obstacles? What dependencies are failing? What has been tried? Propose a clear plan to unblock the task.
 * - **For `REVIEW` status**: Do not just state what you did. Highlight the problems you encountered, even if you resolved them. Mention potential weaknesses, trade-offs, and areas that need careful scrutiny during review. Guide the reviewer to the most critical parts of your implementation.
 * - **For all other updates**: Be transparent about the impact, risks, and any potential issues. Simple, low-effort comments are not acceptable.
 *
 * A comment is ALWAYS required. Short, uninformative comments will be rejected.
 * 
 * @param {Object} params - Tool parameters
 * @param {number} params.task_id - ID of the task to update. This is a mandatory field.
 * @param {string} params.comment - **CRITICAL COMMENT OBLIGATOIRE** - Your analysis of the update. See rules above. Must be detailed and analytical.
 * @param {string} [params.title] - New title for the task.
 * @param {string} [params.short_description] - New brief description.
 * @param {string} [params.detailed_description] - New detailed specification of the task.
 * @param {number[]} [params.dependencies] - New list of dependency task IDs. This will overwrite the existing list.
 * @param {string} [params.status] - New status. Must be one of: 'IN_PROGRESS', 'BLOCKED', 'REVIEW'.
 * @param {string[]} [params.impacted_files] - New list of affected files. This will overwrite the existing list.
 * @param {string} [params.validation_criteria] - New validation criteria for the task.
 * @param {number|null} [params.parent_id] - New parent task ID. Use `null` to remove the parent relationship.
 * @param {number} [params.priority] - New priority level (1-5).
 * @param {string} [params.image] - New path to an image associated with the task.
 * @returns {Object} Tool response with the updated task information and a summary of actions performed.
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

        // Determine the effective status for validation
        const effectiveStatus = updates.status || existingTask.status;

        // CRITICAL COMMENT VALIDATION for BLOCKED or REVIEW status
        const isCriticalStatus = effectiveStatus === 'BLOCKED' || effectiveStatus === 'REVIEW';
        if (isCriticalStatus) {
            // This validation applies even if the status is not changing, but the existing status is critical
            if (!comment || comment.trim().length < 50) {
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: `Critical analysis required. The comment for status '${effectiveStatus}' must be a detailed analysis of at least 50 characters. Your comment was too short or missing. Please provide a thorough explanation of the problem, your solution, and any remaining risks.`,
                            updated_task: null
                        }, null, 2)
                    }]
                };
            }
        }

        // STANDARD COMMENT VALIDATION for all other updates
        // A comment is always required, unless it's a programmatic status change to IN_PROGRESS (where no comment is passed).
        const isProgrammaticInProgress = updates.status === 'IN_PROGRESS' && !comment;

        if (!isCriticalStatus && !isProgrammaticInProgress) {
            if (!comment || comment.trim().length < 10) {
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: `A meaningful comment of at least 10 characters is required for this update. Please describe the change you made.`,
                            updated_task: null
                        }, null, 2)
                    }]
                };
            }
        }

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
            ...updates,
            updated_date: new Date().toISOString(),
            comments: updatedComments,
            last_comment: effectiveComment,
            last_comment_timestamp: commentEntry.timestamp
        };

        tasks[taskIndex] = updatedTask;

        // After updating the task, check for dependent tasks that can be unblocked
        const unblockedTasks = checkAndUnblockDependentTasks(task_id, tasks);

        // Also, perform a cleanup of orphaned dependencies for all tasks
        const cleanedUpTasks = cleanupOrphanedDependencies(tasks);

        await writeTasks(tasks);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'success',
                    message: `Task ${task_id} updated successfully`,
                    workflow_reminder: 'IMPORTANT: You are in a workflow. After this update, you MUST call remember() to continue.',
                    updated_task: updatedTask,
                    changes_made: {
                        fields_updated: Object.keys(updates),
                        update_count: Object.keys(updates).length,
                        previous_status: existingTask.status,
                        new_status: updatedTask.status,
                    },
                    summary: {
                        task_id: updatedTask.id,
                        has_dependencies: updatedTask.dependencies && updatedTask.dependencies.length > 0,
                        dependency_count: updatedTask.dependencies ? updatedTask.dependencies.length : 0,
                        is_subtask: updatedTask.parent_id !== null,
                        priority_level: updatedTask.priority,
                        status_changed: existingTask.status !== updatedTask.status,
                    },
                    automatic_actions: {
                        unblocked_tasks: unblockedTasks,
                        cleaned_up_tasks: cleanedUpTasks,
                        total_affected_tasks: unblockedTasks.length + cleanedUpTasks.length,
                    }
                }, null, 2)
            }]
        };

    } catch (error) {
        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `An unexpected error occurred: ${error.message}`,
                    stack: error.stack
                }, null, 2)
            }]
        };
    }
}

/**
 * Main function to handle tool calls for this MCP
 * @param {Object} tool_call - The tool call object
 * @returns {Object} The result of the tool call
 */
export default async function handleToolCall(tool_call) {
    if (tool_call.tool_name === 'mcp_MemoryBankMCP_update_task') {
        return await handleUpdateTask(tool_call.tool_input);
    }
    // Add other tool handlers here if needed
    return {
        content: [{
            type: 'text',
            text: JSON.stringify({
                status: 'error',
                message: `Tool '${tool_call.tool_name}' not found in this MCP.`
            }, null, 2)
        }]
    };
} 