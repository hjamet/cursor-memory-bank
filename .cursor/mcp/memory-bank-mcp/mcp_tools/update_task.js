import { z } from 'zod';
import { taskManager } from '../lib/task_manager.js';

// Schema for the update-task tool parameters
export const updateTaskSchema = z.object({
    task_id: z.number().int().positive().describe('ID of the task to update'),
    title: z.string().min(1).max(200).optional().describe('Updated task title'),
    short_description: z.string().min(1).max(500).optional().describe('Updated brief description'),
    detailed_description: z.string().min(1).optional().describe('Updated detailed description'),
    dependencies: z.array(z.number().int().positive()).optional().describe('Updated array of dependency task IDs'),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().describe('Updated task status'),
    impacted_files: z.array(z.string()).optional().describe('Updated list of affected files'),
    validation_criteria: z.string().optional().describe('Updated validation criteria'),
    parent_id: z.number().int().positive().nullable().optional().describe('Updated parent task ID (null to remove parent)'),
    priority: z.number().int().min(1).max(5).optional().describe('Updated priority level (1=highest, 5=lowest)')
});

/**
 * Handles the update-task tool call
 * Updates existing tasks by ID with only the provided fields
 * 
 * @param {Object} params - Tool parameters
 * @param {number} params.task_id - ID of task to update
 * @param {string} [params.title] - Updated title
 * @param {string} [params.short_description] - Updated brief description
 * @param {string} [params.detailed_description] - Updated detailed description
 * @param {number[]} [params.dependencies] - Updated dependencies
 * @param {string} [params.status] - Updated status
 * @param {string[]} [params.impacted_files] - Updated affected files
 * @param {string} [params.validation_criteria] - Updated validation criteria
 * @param {number|null} [params.parent_id] - Updated parent task ID
 * @param {number} [params.priority] - Updated priority level
 * @returns {Object} Tool response with updated task information
 */
export async function handleUpdateTask(params) {
    try {
        const { task_id, ...updates } = params;
        console.log(`[UpdateTask] Updating task ${task_id} with fields:`, Object.keys(updates));

        // Check if task exists
        const existingTask = taskManager.getTaskById(task_id);
        if (!existingTask) {
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

        // Validate parent task exists if parent_id is being updated
        if (updates.parent_id !== undefined && updates.parent_id !== null) {
            const parentTask = taskManager.getTaskById(updates.parent_id);
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

        // Remove undefined values to only update provided fields
        const cleanUpdates = Object.fromEntries(
            Object.entries(updates).filter(([_, value]) => value !== undefined)
        );

        // Update the task using TaskManager
        const updatedTask = taskManager.updateTask(task_id, cleanUpdates);

        // Prepare success response
        const response = {
            status: 'success',
            message: `Task ${task_id} updated successfully`,
            updated_task: updatedTask,
            changes_made: {
                fields_updated: Object.keys(cleanUpdates),
                update_count: Object.keys(cleanUpdates).length,
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
            }
        };

        console.log(`[UpdateTask] Successfully updated task ${task_id}: ${updatedTask.title}`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[UpdateTask] Error:', error);

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