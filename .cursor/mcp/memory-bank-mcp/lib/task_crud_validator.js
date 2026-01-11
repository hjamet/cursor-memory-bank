/**
 * Centralized CRUD Validation System for Tasks
 * 
 * This module provides comprehensive validation for all task CRUD operations,
 * consolidating validation logic from multiple sources and adding robust
 * transactional validation to prevent data corruption.
 * 
 * CRITICAL DESIGN PRINCIPLES:
 * 1. Single source of truth for all validation rules
 * 2. Atomic validation (all-or-nothing approach)
 * 3. Layered validation (syntax → semantics → business rules)
 * 4. Comprehensive error reporting with actionable feedback
 * 5. Performance-optimized validation with early exit strategies
 */

import { z } from 'zod';
import { validateNewTaskDependencies, validateReplacementDependencies } from '../mcp_tools/circular_dependency_validator.js';
// Note: validateTaskData is not exported, we'll implement our own integrity validation

// =============================================================================
// VALIDATION SCHEMAS
// =============================================================================

/**
 * Core task schema with comprehensive validation rules
 */
const TaskSchema = z.object({
    id: z.number().int().positive().describe("Unique task identifier"),
    title: z.string()
        .min(1, "Title cannot be empty")
        .max(200, "Title cannot exceed 200 characters")
        .refine(title => title.trim().length > 0, "Title cannot be only whitespace"),
    short_description: z.string()
        .min(1, "Short description cannot be empty")
        .max(500, "Short description cannot exceed 500 characters"),
    detailed_description: z.string()
        .min(1, "Detailed description cannot be empty"),
    status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'BLOCKED', 'REVIEW', 'APPROVED'])
        .describe("Task status"),
    dependencies: z.array(z.number().int().positive())
        .default([])
        .describe("Array of task IDs this task depends on"),
    impacted_files: z.array(z.string()).default([]),
    validation_criteria: z.string().default(""),
    created_date: z.string().datetime(),
    updated_date: z.string().datetime(),
    parent_id: z.number().int().positive().nullable().default(null),
    priority: z.number().int().min(1).max(5).default(3)
});

/**
 * Schema for task creation with required fields only
 */
const CreateTaskSchema = TaskSchema.omit({
    id: true,
    created_date: true,
    updated_date: true
});

/**
 * Schema for task updates (all fields optional except task_id)
 */
const UpdateTaskSchema = TaskSchema.partial().extend({
    task_id: z.number().int().positive().describe("ID of task to update")
});

// =============================================================================
// VALIDATION ERROR CLASSES
// =============================================================================

class ValidationError extends Error {
    constructor(message, code, details = {}) {
        super(message);
        this.name = 'ValidationError';
        this.code = code;
        this.details = details;
    }
}

class BusinessRuleViolation extends ValidationError {
    constructor(message, rule, details = {}) {
        super(message, 'BUSINESS_RULE_VIOLATION', { rule, ...details });
        this.rule = rule;
    }
}

class DataIntegrityError extends ValidationError {
    constructor(message, details = {}) {
        super(message, 'DATA_INTEGRITY_ERROR', details);
    }
}

// =============================================================================
// CORE VALIDATION FUNCTIONS
// =============================================================================

/**
 * Comprehensive CRUD validation for task operations
 * @param {Object} taskData - Task data to validate
 * @param {Array} existingTasks - Array of existing tasks for context validation
 * @param {string} operation - Operation type: 'create', 'update', 'delete'
 * @returns {Object} Validation result
 */
export function validateTaskCRUD(taskData, existingTasks = [], operation = 'create') {
    const validationResult = {
        isValid: true,
        errors: [],
        warnings: [],
        normalizedData: null,
        operation: operation
    };

    try {
        // Layer 1: Schema Validation
        const schemaValidation = validateSchema(taskData, operation);
        if (!schemaValidation.isValid) {
            validationResult.isValid = false;
            validationResult.errors.push(...schemaValidation.errors);
            return validationResult;
        }
        validationResult.normalizedData = schemaValidation.data;

        // Layer 2: Business Rule Validation
        const businessValidation = validateBusinessRules(
            validationResult.normalizedData,
            existingTasks,
            operation
        );
        if (!businessValidation.isValid) {
            validationResult.isValid = false;
            validationResult.errors.push(...businessValidation.errors);
        }
        validationResult.warnings.push(...businessValidation.warnings);

        // Layer 3: Data Integrity Validation
        const integrityValidation = validateDataIntegrity(
            validationResult.normalizedData,
            existingTasks,
            operation
        );
        if (!integrityValidation.isValid) {
            validationResult.isValid = false;
            validationResult.errors.push(...integrityValidation.errors);
        }
        validationResult.warnings.push(...integrityValidation.warnings);

        return validationResult;

    } catch (error) {
        validationResult.isValid = false;
        validationResult.errors.push({
            type: 'VALIDATION_SYSTEM_ERROR',
            message: `Internal validation error: ${error.message}`,
            code: 'SYSTEM_ERROR',
            details: { originalError: error.message }
        });
        return validationResult;
    }
}

/**
 * Layer 1: Schema validation using Zod
 */
function validateSchema(taskData, operation) {
    try {
        let schema;
        switch (operation) {
            case 'create':
                schema = CreateTaskSchema;
                break;
            case 'update':
                schema = UpdateTaskSchema;
                break;
            default:
                schema = TaskSchema;
        }

        // Add defensive validation for input data
        if (taskData === null || taskData === undefined) {
            return {
                isValid: false,
                errors: [{
                    type: 'SCHEMA_VALIDATION_ERROR',
                    message: 'Task data cannot be null or undefined',
                    code: 'NULL_INPUT',
                    field: 'root',
                    details: { inputType: typeof taskData }
                }],
                data: null
            };
        }

        const result = schema.safeParse(taskData);

        if (!result.success) {
            return {
                isValid: false,
                errors: result.error.errors.map(err => {
                    // Create serializable error details without Zod objects
                    const serializableDetails = {
                        path: err.path,
                        received: err.received,
                        expected: err.expected,
                        code: err.code
                    };

                    // Safely handle potential circular references or complex objects
                    try {
                        JSON.stringify(serializableDetails);
                    } catch (serializationError) {
                        // Fallback to basic details if serialization fails
                        serializableDetails.path = err.path || [];
                        serializableDetails.code = err.code || 'UNKNOWN';
                        serializableDetails.serialization_error = 'Complex object details removed for JSON compatibility';
                    }

                    return {
                        type: 'SCHEMA_VALIDATION_ERROR',
                        message: `${err.path.join('.')}: ${err.message}`,
                        code: 'INVALID_SCHEMA',
                        field: err.path.join('.') || 'unknown',
                        details: serializableDetails
                    };
                }),
                data: null
            };
        }

        return {
            isValid: true,
            errors: [],
            data: result.data
        };

    } catch (error) {
        // Enhanced error logging for debugging
        console.error('[CRUD Validator] Schema validation error:', {
            error: error.message,
            operation: operation,
            taskDataType: typeof taskData,
            taskDataKeys: taskData && typeof taskData === 'object' ? Object.keys(taskData) : 'N/A'
        });

        return {
            isValid: false,
            errors: [{
                type: 'SCHEMA_VALIDATION_ERROR',
                message: `Schema validation failed: ${error.message}`,
                code: 'SCHEMA_ERROR',
                details: {
                    originalError: error.message,
                    operation: operation,
                    timestamp: new Date().toISOString()
                }
            }],
            data: null
        };
    }
}

/**
 * Layer 2: Business rule validation
 */
function validateBusinessRules(taskData, existingTasks, operation) {
    const errors = [];
    const warnings = [];
    const taskMap = new Map(existingTasks.map(task => [task.id, task]));

    // Rule 1: Validate dependencies exist and are not circular
    if (taskData.dependencies && taskData.dependencies.length > 0) {
        // Check if all dependencies exist
        const missingDeps = taskData.dependencies.filter(depId => !taskMap.has(depId));
        if (missingDeps.length > 0) {
            errors.push({
                type: 'BUSINESS_RULE_VIOLATION',
                message: `Dependencies reference non-existent tasks: ${missingDeps.join(', ')}`,
                code: 'MISSING_DEPENDENCIES',
                rule: 'dependencies_must_exist',
                details: { missingDependencies: missingDeps }
            });
        }

        // Check for circular dependencies
        if (operation === 'create') {
            const circularCheck = validateNewTaskDependencies(existingTasks, taskData.dependencies);
            if (!circularCheck.isValid) {
                errors.push({
                    type: 'BUSINESS_RULE_VIOLATION',
                    message: circularCheck.error,
                    code: 'CIRCULAR_DEPENDENCY',
                    rule: 'no_circular_dependencies',
                    details: { cycles: circularCheck.cycles }
                });
            }
        } else if (operation === 'update' && taskData.task_id) {
            const circularCheck = validateReplacementDependencies(
                existingTasks,
                taskData.task_id,
                taskData.dependencies
            );
            if (!circularCheck.isValid) {
                errors.push({
                    type: 'BUSINESS_RULE_VIOLATION',
                    message: circularCheck.error,
                    code: 'CIRCULAR_DEPENDENCY',
                    rule: 'no_circular_dependencies',
                    details: { cycles: circularCheck.cycles }
                });
            }
        }
    }

    // Rule 2: Validate parent-child relationships
    if (taskData.parent_id) {
        const parentTask = taskMap.get(taskData.parent_id);
        if (!parentTask) {
            errors.push({
                type: 'BUSINESS_RULE_VIOLATION',
                message: `Parent task with ID ${taskData.parent_id} does not exist`,
                code: 'INVALID_PARENT',
                rule: 'parent_must_exist',
                details: { parent_id: taskData.parent_id }
            });
        }

        // Prevent self-parenting
        if (taskData.task_id && taskData.parent_id === taskData.task_id) {
            errors.push({
                type: 'BUSINESS_RULE_VIOLATION',
                message: 'Task cannot be its own parent',
                code: 'SELF_PARENT',
                rule: 'no_self_parenting',
                details: { task_id: taskData.task_id }
            });
        }
    }

    // Rule 3: Status transition validation
    if (operation === 'update' && taskData.status && taskData.task_id) {
        const existingTask = taskMap.get(taskData.task_id);
        if (existingTask) {
            const statusValidation = validateStatusTransition(
                existingTask.status,
                taskData.status,
                existingTask
            );
            if (!statusValidation.isValid) {
                errors.push(...statusValidation.errors);
            }
            warnings.push(...statusValidation.warnings);
        }
    }

    // Rule 4: Priority validation with context
    if (taskData.priority) {
        if (taskData.priority === 5 && taskData.dependencies && taskData.dependencies.length > 0) {
            warnings.push({
                type: 'BUSINESS_RULE_WARNING',
                message: 'Critical priority task (5) has dependencies which may delay execution',
                code: 'CRITICAL_WITH_DEPS',
                rule: 'priority_dependency_conflict',
                details: { priority: taskData.priority, dependencies: taskData.dependencies }
            });
        }
    }

    return {
        isValid: errors.length === 0,
        errors,
        warnings
    };
}

/**
 * Layer 3: Data integrity validation
 */
function validateDataIntegrity(taskData, existingTasks, operation) {
    const errors = [];
    const warnings = [];

    // Check for duplicate titles (warning only, not blocking)
    if (taskData.title && operation === 'create') {
        const duplicateTitles = existingTasks.filter(task =>
            task.title.toLowerCase().trim() === taskData.title.toLowerCase().trim()
        );

        if (duplicateTitles.length > 0) {
            warnings.push({
                type: 'DATA_INTEGRITY_WARNING',
                message: `Similar title already exists in task(s): ${duplicateTitles.map(t => t.id).join(', ')}`,
                code: 'DUPLICATE_TITLE',
                rule: 'unique_titles_preferred',
                details: { duplicateTasks: duplicateTitles.map(t => ({ id: t.id, title: t.title })) }
            });
        }
    }

    // Validate file paths in impacted_files
    if (taskData.impacted_files && taskData.impacted_files.length > 0) {
        const invalidPaths = taskData.impacted_files.filter(path => {
            // Basic path validation - no absolute paths, no dangerous patterns
            return path.includes('..') || path.startsWith('/') || path.includes('\\');
        });

        if (invalidPaths.length > 0) {
            errors.push({
                type: 'DATA_INTEGRITY_ERROR',
                message: `Invalid file paths detected: ${invalidPaths.join(', ')}`,
                code: 'INVALID_FILE_PATHS',
                rule: 'safe_file_paths_only',
                details: { invalidPaths }
            });
        }
    }

    // Validate task data consistency with existing dataset
    if (existingTasks.length > 0) {
        // Simple integrity check: duplicate IDs
        const ids = existingTasks.map(t => t.id);
        const uniqueIds = new Set(ids);
        if (ids.length !== uniqueIds.size) {
            const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
            warnings.push({
                type: 'DATA_INTEGRITY_WARNING',
                message: 'Existing task dataset has duplicate IDs',
                code: 'DATASET_INTEGRITY_ISSUES',
                rule: 'dataset_integrity',
                details: {
                    duplicateIds: [...new Set(duplicates)]
                }
            });
        }
    }

    return {
        isValid: errors.length === 0,
        errors,
        warnings
    };
}

/**
 * Validate status transitions according to business rules
 */
function validateStatusTransition(currentStatus, newStatus, taskContext) {
    const errors = [];
    const warnings = [];

    // Define valid transitions
    const validTransitions = {
        'TODO': ['IN_PROGRESS', 'BLOCKED'],
        'IN_PROGRESS': ['REVIEW', 'BLOCKED', 'TODO'],
        'BLOCKED': ['TODO', 'IN_PROGRESS'],
        'REVIEW': ['DONE', 'IN_PROGRESS', 'TODO', 'APPROVED'],
        'DONE': ['REVIEW', 'TODO'],
        'APPROVED': ['REVIEW', 'TODO'] // Allow reopening approved tasks
    };

    if (!validTransitions[currentStatus]?.includes(newStatus)) {
        errors.push({
            type: 'BUSINESS_RULE_VIOLATION',
            message: `Invalid status transition from '${currentStatus}' to '${newStatus}'`,
            code: 'INVALID_STATUS_TRANSITION',
            rule: 'valid_status_transitions',
            details: {
                currentStatus,
                newStatus,
                validTransitions: validTransitions[currentStatus] || []
            }
        });
    }

    // Check if task has unresolved dependencies when moving to IN_PROGRESS
    if (newStatus === 'IN_PROGRESS' && taskContext.dependencies?.length > 0) {
        warnings.push({
            type: 'BUSINESS_RULE_WARNING',
            message: 'Task moved to IN_PROGRESS but has dependencies. Ensure dependencies are completed.',
            code: 'IN_PROGRESS_WITH_DEPS',
            rule: 'dependencies_before_progress',
            details: { dependencies: taskContext.dependencies }
        });
    }

    return {
        isValid: errors.length === 0,
        errors,
        warnings
    };
}

// =============================================================================
// CRUD OPERATION VALIDATORS
// =============================================================================

/**
 * Validate task creation
 */
export function validateCreateTask(taskData, existingTasks) {
    return validateTaskCRUD(taskData, existingTasks, 'create');
}

/**
 * Validate task update
 */
export function validateUpdateTask(updateData, existingTasks) {
    return validateTaskCRUD(updateData, existingTasks, 'update');
}

/**
 * Validate task deletion
 */
export function validateDeleteTask(taskId, existingTasks) {
    const errors = [];
    const warnings = [];

    const taskToDelete = existingTasks.find(task => task.id === taskId);
    if (!taskToDelete) {
        errors.push({
            type: 'VALIDATION_ERROR',
            message: `Task with ID ${taskId} not found`,
            code: 'TASK_NOT_FOUND',
            details: { taskId }
        });
        return { isValid: false, errors, warnings };
    }

    // Check for dependent tasks
    const dependentTasks = existingTasks.filter(task =>
        task.dependencies && task.dependencies.includes(taskId)
    );

    if (dependentTasks.length > 0) {
        errors.push({
            type: 'BUSINESS_RULE_VIOLATION',
            message: `Cannot delete task ${taskId}: ${dependentTasks.length} task(s) depend on it`,
            code: 'HAS_DEPENDENTS',
            rule: 'no_delete_with_dependents',
            details: {
                dependentTasks: dependentTasks.map(t => ({ id: t.id, title: t.title }))
            }
        });
    }

    // Check for child tasks
    const childTasks = existingTasks.filter(task => task.parent_id === taskId);
    if (childTasks.length > 0) {
        warnings.push({
            type: 'BUSINESS_RULE_WARNING',
            message: `Task ${taskId} has ${childTasks.length} child task(s). Consider reassigning or deleting them first.`,
            code: 'HAS_CHILDREN',
            rule: 'orphan_children_warning',
            details: {
                childTasks: childTasks.map(t => ({ id: t.id, title: t.title }))
            }
        });
    }

    return {
        isValid: errors.length === 0,
        errors,
        warnings,
        taskToDelete,
        affectedTasks: {
            dependents: dependentTasks,
            children: childTasks
        }
    };
}

// =============================================================================
// BATCH VALIDATION
// =============================================================================

/**
 * Validate multiple operations as a transaction
 */
export function validateBatchOperations(operations, existingTasks) {
    const results = [];
    let simulatedTasks = [...existingTasks];

    for (const operation of operations) {
        let result;

        switch (operation.type) {
            case 'create':
                result = validateCreateTask(operation.data, simulatedTasks);
                if (result.isValid) {
                    // Simulate adding the task for subsequent validations
                    const newTask = {
                        ...result.normalizedData,
                        id: Math.max(...simulatedTasks.map(t => t.id), 0) + 1,
                        created_date: new Date().toISOString(),
                        updated_date: new Date().toISOString()
                    };
                    simulatedTasks.push(newTask);
                }
                break;

            case 'update':
                result = validateUpdateTask(operation.data, simulatedTasks);
                if (result.isValid) {
                    // Simulate updating the task
                    const taskIndex = simulatedTasks.findIndex(t => t.id === operation.data.task_id);
                    if (taskIndex !== -1) {
                        simulatedTasks[taskIndex] = {
                            ...simulatedTasks[taskIndex],
                            ...result.normalizedData,
                            updated_date: new Date().toISOString()
                        };
                    }
                }
                break;

            case 'delete':
                result = validateDeleteTask(operation.data.task_id, simulatedTasks);
                if (result.isValid) {
                    // Simulate removing the task
                    simulatedTasks = simulatedTasks.filter(t => t.id !== operation.data.task_id);
                }
                break;

            default:
                result = {
                    isValid: false,
                    errors: [{
                        type: 'VALIDATION_ERROR',
                        message: `Unknown operation type: ${operation.type}`,
                        code: 'UNKNOWN_OPERATION'
                    }],
                    warnings: []
                };
        }

        results.push({
            operation: operation,
            validation: result
        });

        // Stop processing if any operation fails (atomic transaction)
        if (!result.isValid) {
            break;
        }
    }

    const allValid = results.every(r => r.validation.isValid);
    const allErrors = results.flatMap(r => r.validation.errors);
    const allWarnings = results.flatMap(r => r.validation.warnings);

    return {
        isValid: allValid,
        errors: allErrors,
        warnings: allWarnings,
        results: results,
        simulatedFinalState: simulatedTasks
    };
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
    ValidationError,
    BusinessRuleViolation,
    DataIntegrityError,
    TaskSchema,
    CreateTaskSchema,
    UpdateTaskSchema
};