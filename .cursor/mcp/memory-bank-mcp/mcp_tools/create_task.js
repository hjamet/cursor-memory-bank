import { z } from 'zod';
import { taskManager } from '../lib/task_manager.js';

// Schema for the create_task tool parameters
export const createTaskSchema = z.object({
    title: z.string().min(1).max(200).describe('Short descriptive title of the task'),
    short_description: z.string().min(1).max(500).describe('Brief one-sentence description of what needs to be done'),
    detailed_description: z.string().min(1).describe('Comprehensive description with implementation details'),
    dependencies: z.array(z.number().int().positive()).optional().default([]).describe('Array of task IDs that must be completed before this task'),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW']).optional().default('TODO').describe('Initial status of the task'),
    impacted_files: z.array(z.string()).optional().default([]).describe('List of files or rules affected by this task'),
    validation_criteria: z.string().optional().default('').describe('Clear criteria to determine when the task is successfully completed'),
    parent_id: z.number().int().positive().optional().describe('ID of parent task for sub-tasks'),
    priority: z.number().int().min(1).max(5).optional().default(3).describe('Priority level (1=highest, 5=lowest)')
});

/**
 * Handles the create_task tool call
 * Creates new tasks with auto-generated IDs and comprehensive validation
 * 
 * @param {Object} params - Tool parameters
 * @param {string} params.title - Task title
 * @param {string} params.short_description - Brief description
 * @param {string} params.detailed_description - Detailed description
 * @param {number[]} [params.dependencies=[]] - Array of dependency task IDs
 * @param {string} [params.status='TODO'] - Initial task status
 * @param {string[]} [params.impacted_files=[]] - List of affected files
 * @param {string} [params.validation_criteria=''] - Validation criteria
 * @param {number} [params.parent_id] - Parent task ID for sub-tasks
 * @param {number} [params.priority=3] - Priority level
 * @returns {Object} Tool response with created task information
 */
export async function handleCreateTask(params) {
    try {
        console.log('[CreateTask] Creating new task:', params.title);

        // Validate parent task exists if parent_id is provided
        if (params.parent_id) {
            const parentTask = taskManager.getTaskById(params.parent_id);
            if (!parentTask) {
                return {
                    content: [{
                        type: 'text',
                        text: JSON.stringify({
                            status: 'error',
                            message: `Parent task with ID ${params.parent_id} not found`,
                            created_task: null
                        }, null, 2)
                    }]
                };
            }
        }

        // Create the task using TaskManager
        const createdTask = taskManager.createTask({
            title: params.title,
            short_description: params.short_description,
            detailed_description: params.detailed_description,
            dependencies: params.dependencies || [],
            status: params.status || 'TODO',
            impacted_files: params.impacted_files || [],
            validation_criteria: params.validation_criteria || '',
            parent_id: params.parent_id || null,
            priority: params.priority || 3
        });

        // Prepare success response
        const response = {
            status: 'success',
            message: `Task created successfully with ID ${createdTask.id}`,
            created_task: {
                id: createdTask.id,
                title: createdTask.title,
                short_description: createdTask.short_description,
                detailed_description: createdTask.detailed_description,
                status: createdTask.status,
                dependencies: createdTask.dependencies,
                impacted_files: createdTask.impacted_files,
                validation_criteria: createdTask.validation_criteria,
                created_date: createdTask.created_date,
                updated_date: createdTask.updated_date,
                parent_id: createdTask.parent_id,
                priority: createdTask.priority
            },
            summary: {
                task_id: createdTask.id,
                has_dependencies: createdTask.dependencies.length > 0,
                dependency_count: createdTask.dependencies.length,
                is_subtask: createdTask.parent_id !== null,
                priority_level: createdTask.priority
            }
        };

        console.log(`[CreateTask] Successfully created task ${createdTask.id}: ${createdTask.title}`);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify(response, null, 2)
            }]
        };

    } catch (error) {
        console.error('[CreateTask] Error:', error);

        return {
            content: [{
                type: 'text',
                text: JSON.stringify({
                    status: 'error',
                    message: `Error creating task: ${error.message}`,
                    created_task: null,
                    error_details: {
                        error_type: error.constructor.name,
                        error_message: error.message
                    }
                }, null, 2)
            }]
        };
    }
} 