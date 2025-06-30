import { z } from 'zod';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { validateNewTaskDependencies, formatCycleErrors } from './circular_dependency_validator.js';
import { validateCreateTask } from '../lib/task_crud_validator.js';

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
 * Calculate similarity between two strings using Levenshtein distance
 * @param {string} str1 - First string
 * @param {string} str2 - Second string
 * @returns {number} Similarity score between 0 and 1 (1 = identical)
 */
function calculateSimilarity(str1, str2) {
    if (!str1 || !str2) return 0;

    const s1 = str1.toLowerCase().trim();
    const s2 = str2.toLowerCase().trim();

    if (s1 === s2) return 1;

    const longer = s1.length > s2.length ? s1 : s2;
    const shorter = s1.length > s2.length ? s2 : s1;
    const editDistance = levenshteinDistance(longer, shorter);

    if (longer.length === 0) return 1;
    return (longer.length - editDistance) / longer.length;
}

/**
 * Calculate Levenshtein distance between two strings
 * @param {string} str1 - First string
 * @param {string} str2 - Second string
 * @returns {number} Edit distance
 */
function levenshteinDistance(str1, str2) {
    const matrix = [];

    for (let i = 0; i <= str2.length; i++) {
        matrix[i] = [i];
    }

    for (let j = 0; j <= str1.length; j++) {
        matrix[0][j] = j;
    }

    for (let i = 1; i <= str2.length; i++) {
        for (let j = 1; j <= str1.length; j++) {
            if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // substitution
                    matrix[i][j - 1] + 1,     // insertion
                    matrix[i - 1][j] + 1      // deletion
                );
            }
        }
    }

    return matrix[str2.length][str1.length];
}

/**
 * Check for duplicate tasks based on title and description similarity
 * @param {Array} tasks - Existing tasks array
 * @param {string} newTitle - Title of the new task
 * @param {string} newDescription - Description of the new task
 * @param {number} titleThreshold - Similarity threshold for titles (default: 0.85)
 * @param {number} descriptionThreshold - Similarity threshold for descriptions (default: 0.7)
 * @returns {Object} Duplicate check result
 */
function checkForDuplicates(tasks, newTitle, newDescription, titleThreshold = 0.85, descriptionThreshold = 0.7) {
    const duplicates = [];

    for (const task of tasks) {
        // Skip archived/done tasks for duplicate detection
        if (task.status === 'DONE' || task.status === 'APPROVED') {
            continue;
        }

        const titleSimilarity = calculateSimilarity(newTitle, task.title);
        const descriptionSimilarity = calculateSimilarity(newDescription, task.short_description);

        // Check for exact title match (critical)
        if (titleSimilarity === 1) {
            duplicates.push({
                task: task,
                reason: 'identical_title',
                titleSimilarity: titleSimilarity,
                descriptionSimilarity: descriptionSimilarity,
                severity: 'critical'
            });
        }
        // Check for high similarity in both title and description
        else if (titleSimilarity >= titleThreshold && descriptionSimilarity >= descriptionThreshold) {
            duplicates.push({
                task: task,
                reason: 'high_similarity',
                titleSimilarity: titleSimilarity,
                descriptionSimilarity: descriptionSimilarity,
                severity: 'warning'
            });
        }
        // Check for very high title similarity alone
        else if (titleSimilarity >= 0.9) {
            duplicates.push({
                task: task,
                reason: 'similar_title',
                titleSimilarity: titleSimilarity,
                descriptionSimilarity: descriptionSimilarity,
                severity: 'warning'
            });
        }
    }

    return {
        hasDuplicates: duplicates.length > 0,
        duplicates: duplicates,
        criticalDuplicates: duplicates.filter(d => d.severity === 'critical'),
        warningDuplicates: duplicates.filter(d => d.severity === 'warning')
    };
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

        // CENTRALIZED CRUD VALIDATION - Replace all existing validations
        const validationResult = validateCreateTask(params, tasks);

        if (!validationResult.isValid) {
            // Format errors for user-friendly response
            const errorMessages = validationResult.errors.map(error => error.message).join('; ');
            const errorDetails = {
                validation_errors: validationResult.errors,
                warnings: validationResult.warnings,
                operation: validationResult.operation
            };

            // Check for specific error types to provide enhanced feedback
            const hasCircularDependency = validationResult.errors.some(e => e.code === 'CIRCULAR_DEPENDENCY');
            const hasDuplicateTitle = validationResult.errors.some(e => e.code === 'DUPLICATE_TITLE');
            const hasSchemaError = validationResult.errors.some(e => e.type === 'SCHEMA_VALIDATION_ERROR');

            if (hasCircularDependency) {
                const circularError = validationResult.errors.find(e => e.code === 'CIRCULAR_DEPENDENCY');
                errorDetails.circular_dependency_prevention = {
                    reason: 'circular_dependency_detected',
                    detected_cycles: circularError.details?.cycles || [],
                    prevention_note: "This validation prevents the creation of tasks that would introduce circular dependencies."
                };
            }

            if (hasDuplicateTitle) {
                const duplicateError = validationResult.errors.find(e => e.code === 'DUPLICATE_TITLE');
                errorDetails.duplicate_detection = {
                    reason: 'identical_title',
                    existing_task: duplicateError.details?.existingTask || null
                };
            }

            return {
                content: [{
                    type: 'text',
                    text: JSON.stringify({
                        status: 'error',
                        message: `Task creation blocked: ${errorMessages}`,
                        ...errorDetails,
                        created_task: null
                    }, null, 2)
                }]
            };
        }

        // Log warnings if any (non-blocking issues)
        if (validationResult.warnings.length > 0) {
            console.warn(`[CreateTask] Validation warnings for task "${params.title}":`,
                validationResult.warnings.map(w => w.message));
        }

        // Generate a new task ID with enhanced collision detection
        const newTaskId = generateUniqueTaskId(tasks);

        // Create the new task object using normalized data from validation
        const normalizedData = validationResult.normalizedData;
        const createdTask = {
            id: newTaskId,
            title: normalizedData.title,
            short_description: normalizedData.short_description,
            detailed_description: normalizedData.detailed_description,
            dependencies: normalizedData.dependencies || [],
            status: normalizedData.status || 'TODO',
            impacted_files: normalizedData.impacted_files || [],
            validation_criteria: normalizedData.validation_criteria || '',
            created_date: new Date().toISOString(),
            updated_date: new Date().toISOString(),
            parent_id: normalizedData.parent_id || null,
            priority: normalizedData.priority || 3,
            image: normalizedData.image || null,
            refactoring_target_file: normalizedData.refactoring_target_file || null
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