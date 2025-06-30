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
 * Generate a unique task ID with collision detection and retry logic
 * @param {Array} tasks - Existing tasks array
 * @returns {number} Unique task ID
 */
function generateUniqueTaskId(tasks) {
    const maxRetries = 10;
    let attempt = 0;

    while (attempt < maxRetries) {
        // Calculate next ID based on current maximum
        const candidateId = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;

        // Verify uniqueness (defense against race conditions)
        const isDuplicate = tasks.some(task => task.id === candidateId);

        if (!isDuplicate) {
            return candidateId;
        }

        // If collision detected, force a higher ID
        const highestId = Math.max(...tasks.map(t => t.id));
        const forcedId = highestId + attempt + 1;

        // Double-check the forced ID
        if (!tasks.some(task => task.id === forcedId)) {
            console.warn(`[CreateTask] ID collision detected for ${candidateId}, using fallback ID ${forcedId}`);
            return forcedId;
        }

        attempt++;
    }

    // Ultimate fallback: use timestamp-based ID
    const timestampId = Date.now() % 1000000; // Last 6 digits of timestamp
    console.error(`[CreateTask] Failed to generate unique ID after ${maxRetries} attempts, using timestamp-based ID: ${timestampId}`);
    return timestampId;
}

/**
 * Validate task data integrity before saving
 * @param {Array} tasks - Tasks array to validate
 * @throws {Error} If duplicate IDs are found
 */
function validateTaskIntegrity(tasks) {
    const ids = tasks.map(t => t.id);
    const uniqueIds = new Set(ids);

    if (ids.length !== uniqueIds.size) {
        const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
        throw new Error(`Duplicate task IDs detected: ${duplicates.join(', ')}`);
    }
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

        // Generate a new task ID with enhanced collision detection
        const newTaskId = generateUniqueTaskId(tasks);

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
            image: params.image || null,
            refactoring_target_file: params.refactoring_target_file || null
        };

        // Add the new task and validate integrity before saving
        tasks.push(createdTask);

        // Validate no duplicates were introduced
        validateTaskIntegrity(tasks);

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
                image: createdTask.image,
                refactoring_target_file: createdTask.refactoring_target_file
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