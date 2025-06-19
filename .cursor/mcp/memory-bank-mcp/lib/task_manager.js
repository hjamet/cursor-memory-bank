import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming this file is in .cursor/mcp/memory-bank-mcp/lib/)
const projectRoot = path.resolve(__dirname, '../../../..');
const TASKS_JSON_PATH = path.join(projectRoot, '.cursor/memory-bank/workflow/tasks.json');
const TASKS_MD_PATH = path.join(projectRoot, '.cursor/memory-bank/workflow/tasks.md');

/**
 * Task Manager Class for JSON-based task operations
 * Handles CRUD operations, dependency validation, and task querying
 */
export class TaskManager {
    constructor() {
        this.tasksData = null;
        this.initializeTasksFile();
    }

    /**
     * Initialize tasks.json file if it doesn't exist
     */
    initializeTasksFile() {
        try {
            if (!fs.existsSync(TASKS_JSON_PATH)) {
                const initialData = {
                    version: "1.0.0",
                    last_id: 0,
                    tasks: []
                };
                this.writeTasksData(initialData);
                console.log('[TaskManager] Initialized new tasks.json file');
            }
        } catch (error) {
            console.error('[TaskManager] Error initializing tasks file:', error);
            throw error;
        }
    }

    /**
     * Read and parse tasks.json file
     * @returns {Object} Tasks data object
     */
    readTasksData() {
        try {
            if (!fs.existsSync(TASKS_JSON_PATH)) {
                throw new Error(`Tasks file not found at ${TASKS_JSON_PATH}`);
            }

            const content = fs.readFileSync(TASKS_JSON_PATH, 'utf-8');
            this.tasksData = JSON.parse(content);
            return this.tasksData;
        } catch (error) {
            console.error('[TaskManager] Error reading tasks.json:', error);
            throw error;
        }
    }

    /**
     * Write tasks data to JSON file
     * @param {Object} data - Tasks data to write
     */
    writeTasksData(data) {
        try {
            const content = JSON.stringify(data, null, 2);
            fs.writeFileSync(TASKS_JSON_PATH, content, 'utf-8');
            this.tasksData = data;
            console.log('[TaskManager] tasks.json updated successfully');
        } catch (error) {
            console.error('[TaskManager] Error writing tasks.json:', error);
            throw error;
        }
    }

    /**
     * Generate next available task ID
     * @returns {number} Next task ID
     */
    generateNextId() {
        const data = this.readTasksData();
        data.last_id += 1;
        return data.last_id;
    }

    /**
     * Validate task dependencies
     * @param {number[]} dependencies - Array of task IDs
     * @param {number} [excludeId] - Task ID to exclude from validation (for updates)
     * @returns {Object} Validation result with valid/invalid dependencies
     */
    validateDependencies(dependencies, excludeId = null) {
        const data = this.readTasksData();
        const existingIds = new Set(data.tasks.map(task => task.id));

        if (excludeId) {
            existingIds.delete(excludeId);
        }

        const valid = [];
        const invalid = [];

        for (const depId of dependencies) {
            if (existingIds.has(depId)) {
                valid.push(depId);
            } else {
                invalid.push(depId);
            }
        }

        return { valid, invalid, isValid: invalid.length === 0 };
    }

    /**
     * Check for circular dependencies
     * @param {number} taskId - Task ID to check
     * @param {number[]} dependencies - Dependencies to validate
     * @returns {boolean} True if circular dependency detected
     */
    hasCircularDependency(taskId, dependencies) {
        const data = this.readTasksData();
        const taskMap = new Map(data.tasks.map(task => [task.id, task.dependencies]));
        const visited = new Set();
        const recursionStack = new Set();

        const hasCycle = (currentId) => {
            if (recursionStack.has(currentId)) {
                return true; // Circular dependency found
            }
            if (visited.has(currentId)) {
                return false; // Already processed
            }

            visited.add(currentId);
            recursionStack.add(currentId);

            const deps = currentId === taskId ? dependencies : (taskMap.get(currentId) || []);
            for (const depId of deps) {
                if (hasCycle(depId)) {
                    return true;
                }
            }

            recursionStack.delete(currentId);
            return false;
        };

        return hasCycle(taskId);
    }

    /**
     * Create a new task
     * @param {Object} taskData - Task data
     * @returns {Object} Created task with assigned ID
     */
    createTask(taskData) {
        try {
            const data = this.readTasksData();
            const taskId = this.generateNextId();
            const now = new Date().toISOString();

            // Validate dependencies
            const dependencies = taskData.dependencies || [];
            const depValidation = this.validateDependencies(dependencies);
            if (!depValidation.isValid) {
                throw new Error(`Invalid dependencies: ${depValidation.invalid.join(', ')}`);
            }

            // Check for circular dependencies
            if (this.hasCircularDependency(taskId, dependencies)) {
                throw new Error('Circular dependency detected');
            }

            const newTask = {
                id: taskId,
                title: taskData.title,
                short_description: taskData.short_description,
                detailed_description: taskData.detailed_description,
                status: taskData.status || 'TODO',
                dependencies: dependencies,
                impacted_files: taskData.impacted_files || [],
                validation_criteria: taskData.validation_criteria || '',
                created_date: now,
                updated_date: now,
                parent_id: taskData.parent_id || null,
                priority: taskData.priority || 3
            };

            data.tasks.push(newTask);
            data.last_id = taskId;
            this.writeTasksData(data);

            console.log(`[TaskManager] Created task ${taskId}: ${newTask.title}`);
            return newTask;
        } catch (error) {
            console.error('[TaskManager] Error creating task:', error);
            throw error;
        }
    }

    /**
     * Update an existing task
     * @param {number} taskId - Task ID to update
     * @param {Object} updates - Fields to update
     * @returns {Object} Updated task
     */
    updateTask(taskId, updates) {
        try {
            const data = this.readTasksData();
            const taskIndex = data.tasks.findIndex(task => task.id === taskId);

            if (taskIndex === -1) {
                throw new Error(`Task with ID ${taskId} not found`);
            }

            const existingTask = data.tasks[taskIndex];

            // Validate dependencies if provided
            if (updates.dependencies) {
                const depValidation = this.validateDependencies(updates.dependencies, taskId);
                if (!depValidation.isValid) {
                    throw new Error(`Invalid dependencies: ${depValidation.invalid.join(', ')}`);
                }

                // Check for circular dependencies
                if (this.hasCircularDependency(taskId, updates.dependencies)) {
                    throw new Error('Circular dependency detected');
                }
            }

            // Update task with provided fields
            const updatedTask = {
                ...existingTask,
                ...updates,
                id: taskId, // Ensure ID cannot be changed
                updated_date: new Date().toISOString()
            };

            data.tasks[taskIndex] = updatedTask;
            this.writeTasksData(data);

            console.log(`[TaskManager] Updated task ${taskId}: ${updatedTask.title}`);
            return updatedTask;
        } catch (error) {
            console.error('[TaskManager] Error updating task:', error);
            throw error;
        }
    }

    /**
     * Get task by ID
     * @param {number} taskId - Task ID
     * @returns {Object|null} Task object or null if not found
     */
    getTaskById(taskId) {
        try {
            const data = this.readTasksData();
            return data.tasks.find(task => task.id === taskId) || null;
        } catch (error) {
            console.error('[TaskManager] Error getting task by ID:', error);
            throw error;
        }
    }

    /**
     * Get all tasks with optional filtering and sorting
     * @param {Object} options - Query options
     * @returns {Object[]} Array of tasks
     */
    getAllTasks(options = {}) {
        try {
            const data = this.readTasksData();
            let tasks = [...data.tasks];

            // Filter by status if provided
            if (options.status) {
                tasks = tasks.filter(task => task.status === options.status);
            }

            // Filter by parent_id if provided
            if (options.parent_id !== undefined) {
                tasks = tasks.filter(task => task.parent_id === options.parent_id);
            }

            // Sort by priority (status priority, then task priority, then ID)
            const statusPriority = {
                'IN_PROGRESS': 1,
                'TODO': 2,
                'BLOCKED': 3,
                'REVIEW': 4,
                'DONE': 5
            };

            tasks.sort((a, b) => {
                const statusA = statusPriority[a.status] || 999;
                const statusB = statusPriority[b.status] || 999;

                if (statusA !== statusB) {
                    return statusA - statusB;
                }

                if (a.priority !== b.priority) {
                    return a.priority - b.priority;
                }

                return a.id - b.id;
            });

            // Limit results if specified
            if (options.limit) {
                tasks = tasks.slice(0, options.limit);
            }

            return tasks;
        } catch (error) {
            console.error('[TaskManager] Error getting all tasks:', error);
            throw error;
        }
    }

    /**
     * Get tasks that have no pending dependencies (available to work on)
     * @param {Object} options - Query options
     * @returns {Object[]} Array of available tasks
     */
    getNextTasks(options = {}) {
        try {
            const data = this.readTasksData();
            const taskMap = new Map(data.tasks.map(task => [task.id, task]));
            const availableTasks = [];

            for (const task of data.tasks) {
                // Skip completed or blocked tasks unless specifically requested
                if (!options.includeCompleted && task.status === 'DONE') {
                    continue;
                }
                if (!options.includeBlocked && task.status === 'BLOCKED') {
                    continue;
                }

                // Check if all dependencies are completed
                const allDepsCompleted = task.dependencies.every(depId => {
                    const depTask = taskMap.get(depId);
                    return depTask && depTask.status === 'DONE';
                });

                if (allDepsCompleted) {
                    availableTasks.push(task);
                }
            }

            // Sort by priority
            availableTasks.sort((a, b) => {
                const statusPriority = {
                    'IN_PROGRESS': 1,
                    'TODO': 2,
                    'REVIEW': 3,
                    'BLOCKED': 4,
                    'DONE': 5
                };

                const statusA = statusPriority[a.status] || 999;
                const statusB = statusPriority[b.status] || 999;

                if (statusA !== statusB) {
                    return statusA - statusB;
                }

                return a.priority - b.priority;
            });

            // Limit results if specified
            if (options.limit) {
                return availableTasks.slice(0, options.limit);
            }

            return availableTasks;
        } catch (error) {
            console.error('[TaskManager] Error getting next tasks:', error);
            throw error;
        }
    }

    /**
     * Delete a task (with dependency validation)
     * @param {number} taskId - Task ID to delete
     * @returns {boolean} Success status
     */
    deleteTask(taskId) {
        try {
            const data = this.readTasksData();
            const taskIndex = data.tasks.findIndex(task => task.id === taskId);

            if (taskIndex === -1) {
                throw new Error(`Task with ID ${taskId} not found`);
            }

            // Check if any other tasks depend on this task
            const dependentTasks = data.tasks.filter(task =>
                task.dependencies.includes(taskId)
            );

            if (dependentTasks.length > 0) {
                const dependentIds = dependentTasks.map(task => task.id);
                throw new Error(`Cannot delete task ${taskId}: it is a dependency for tasks ${dependentIds.join(', ')}`);
            }

            data.tasks.splice(taskIndex, 1);
            this.writeTasksData(data);

            console.log(`[TaskManager] Deleted task ${taskId}`);
            return true;
        } catch (error) {
            console.error('[TaskManager] Error deleting task:', error);
            throw error;
        }
    }
}

// Export singleton instance
export const taskManager = new TaskManager(); 