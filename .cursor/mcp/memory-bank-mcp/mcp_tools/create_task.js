import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Use the absolute path that we know works
const TASKS_FILE_PATH = 'C:\\Users\\Jamet\\code\\cursor-memory-bank\\.cursor\\memory-bank\\streamlit_app\\tasks.json';

async function readTasks() {
    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return []; // Return empty array if file doesn't exist
        }
        throw error;
    }
}

async function writeTasks(tasks) {
    // Ensure the directory exists
    const dir = path.dirname(TASKS_FILE_PATH);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
}

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
 * @param {string} [params.image] - Optional image path for the task
 * @returns {Object} Tool response with created task information
 */
export async function handleCreateTask(params) {
    try {
        const tasks = await readTasks();

        // Validate parent task exists if parent_id is provided
        if (params.parent_id) {
            const parentTask = tasks.find(task => task.id === params.parent_id);
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

        // Generate a new task ID
        const newTaskId = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;

        // Create the new task object
        const createdTask = {
            id: newTaskId,
            title: params.title,
            short_description: params.short_description,
            detailed_description: params.detailed_description,
            dependencies: params.dependencies || [],
            status: params.status || 'TODO',
            impacted_files: params.impacted_files || [],
            validation_criteria: params.validation_criteria || '',
            created_date: new Date().toISOString(),
            updated_date: new Date().toISOString(),
            parent_id: params.parent_id || null,
            priority: params.priority || 3,
            image: params.image || null
        };

        // Add the new task and write to file
        tasks.push(createdTask);
        await writeTasks(tasks);

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
                priority: createdTask.priority,
                image: createdTask.image
            },
            summary: {
                task_id: createdTask.id,
                has_dependencies: createdTask.dependencies.length > 0,
                dependency_count: createdTask.dependencies.length,
                is_subtask: createdTask.parent_id !== null,
                priority_level: createdTask.priority
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