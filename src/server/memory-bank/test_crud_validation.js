#!/usr/bin/env node

/**
 * Comprehensive Test Suite for CRUD Validation System
 * 
 * This test suite validates the centralized CRUD validation system
 * to ensure all validation rules work correctly and prevent data corruption.
 */

import {
    validateCreateTask,
    validateUpdateTask,
    validateDeleteTask,
    validateBatchOperations,
    ValidationError,
    BusinessRuleViolation,
    DataIntegrityError
} from './lib/task_crud_validator.js';

// =============================================================================
// TEST FRAMEWORK
// =============================================================================

class TestRunner {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}`);
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(`${message}: expected ${expected}, got ${actual}`);
        }
    }

    assertArrayEqual(actual, expected, message) {
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
            throw new Error(`${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
        }
    }

    async run() {
        console.log('🧪 Running CRUD Validation Test Suite...\n');

        for (const test of this.tests) {
            try {
                await test.testFunction();
                console.log(`✅ ${test.name}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ ${test.name}: ${error.message}`);
                this.failed++;
            }
        }

        console.log(`\n📊 Test Results: ${this.passed} passed, ${this.failed} failed`);

        if (this.failed > 0) {
            console.log('❌ Some tests failed. CRUD validation system has issues.');
            process.exit(1);
        } else {
            console.log('✅ All tests passed! CRUD validation system is working correctly.');
        }
    }
}

// =============================================================================
// TEST DATA
// =============================================================================

const sampleTasks = [
    {
        id: 1,
        title: "Setup project structure",
        short_description: "Create basic project structure",
        detailed_description: "Set up the initial project structure with folders and basic files",
        status: "DONE",
        dependencies: [],
        impacted_files: ["package.json", "README.md"],
        validation_criteria: "Project structure is complete",
        created_date: "2025-01-01T10:00:00.000Z",
        updated_date: "2025-01-01T10:00:00.000Z",
        parent_id: null,
        priority: 3
    },
    {
        id: 2,
        title: "Implement authentication",
        short_description: "Add user authentication system",
        detailed_description: "Implement JWT-based authentication with login/logout",
        status: "IN_PROGRESS",
        dependencies: [1],
        impacted_files: ["auth.js", "middleware.js"],
        validation_criteria: "Users can login and logout",
        created_date: "2025-01-02T10:00:00.000Z",
        updated_date: "2025-01-02T10:00:00.000Z",
        parent_id: null,
        priority: 4
    },
    {
        id: 3,
        title: "Write tests",
        short_description: "Add unit tests for authentication",
        detailed_description: "Write comprehensive unit tests for the authentication system",
        status: "TODO",
        dependencies: [2],
        impacted_files: ["auth.test.js"],
        validation_criteria: "All tests pass",
        created_date: "2025-01-03T10:00:00.000Z",
        updated_date: "2025-01-03T10:00:00.000Z",
        parent_id: 2,
        priority: 3
    }
];

// =============================================================================
// TESTS
// =============================================================================

const runner = new TestRunner();

// Test 1: Valid task creation
runner.test('Should validate correct task creation', () => {
    const newTask = {
        title: "New feature",
        short_description: "Implement new feature",
        detailed_description: "Add a new feature to the application",
        status: "TODO",
        dependencies: [1],
        priority: 3
    };

    const result = validateCreateTask(newTask, sampleTasks);
    runner.assert(result.isValid, 'Valid task should pass validation');
    runner.assert(result.errors.length === 0, 'Should have no errors');
    runner.assert(result.normalizedData !== null, 'Should return normalized data');
});

// Test 2: Invalid task creation - missing required fields
runner.test('Should reject task creation with missing required fields', () => {
    const invalidTask = {
        title: "", // Empty title
        short_description: "Test",
        // Missing detailed_description
    };

    const result = validateCreateTask(invalidTask, sampleTasks);
    runner.assert(!result.isValid, 'Invalid task should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');
});

// Test 3: Circular dependency prevention
runner.test('Should prevent circular dependencies in task creation', () => {
    const cyclicTask = {
        title: "Cyclic task",
        short_description: "This would create a cycle",
        detailed_description: "Task that would create a circular dependency",
        status: "TODO",
        dependencies: [3], // This would create cycle: 3 -> 2 -> 1, and new task -> 3
        priority: 3
    };

    const result = validateCreateTask(cyclicTask, sampleTasks);
    runner.assert(!result.isValid, 'Task with circular dependency should fail');

    const circularError = result.errors.find(e => e.code === 'CIRCULAR_DEPENDENCY');
    runner.assert(circularError !== undefined, 'Should have circular dependency error');
});

// Test 4: Non-existent dependency validation
runner.test('Should reject dependencies to non-existent tasks', () => {
    const taskWithInvalidDeps = {
        title: "Task with invalid deps",
        short_description: "Has dependencies to non-existent tasks",
        detailed_description: "This task depends on tasks that don't exist",
        status: "TODO",
        dependencies: [999, 1000], // Non-existent task IDs
        priority: 3
    };

    const result = validateCreateTask(taskWithInvalidDeps, sampleTasks);
    runner.assert(!result.isValid, 'Task with invalid dependencies should fail');

    const missingDepsError = result.errors.find(e => e.code === 'MISSING_DEPENDENCIES');
    runner.assert(missingDepsError !== undefined, 'Should have missing dependencies error');
});

// Test 5: Valid task update
runner.test('Should validate correct task update', () => {
    const updateData = {
        task_id: 2,
        status: "REVIEW",
        priority: 5
    };

    const result = validateUpdateTask(updateData, sampleTasks);
    runner.assert(result.isValid, 'Valid update should pass validation');
    runner.assert(result.errors.length === 0, 'Should have no errors');
});

// Test 6: Invalid status transition
runner.test('Should prevent invalid status transitions', () => {
    const invalidUpdate = {
        task_id: 1, // Task is DONE
        status: "IN_PROGRESS" // Invalid transition from DONE to IN_PROGRESS
    };

    const result = validateUpdateTask(invalidUpdate, sampleTasks);
    runner.assert(!result.isValid, 'Invalid status transition should fail');

    const transitionError = result.errors.find(e => e.code === 'INVALID_STATUS_TRANSITION');
    runner.assert(transitionError !== undefined, 'Should have status transition error');
});

// Test 7: Self-parent prevention
runner.test('Should prevent task from being its own parent', () => {
    const selfParentUpdate = {
        task_id: 2,
        parent_id: 2 // Self as parent
    };

    const result = validateUpdateTask(selfParentUpdate, sampleTasks);
    runner.assert(!result.isValid, 'Self-parent update should fail');

    const selfParentError = result.errors.find(e => e.code === 'SELF_PARENT');
    runner.assert(selfParentError !== undefined, 'Should have self-parent error');
});

// Test 8: Valid task deletion
runner.test('Should validate deletion of task without dependents', () => {
    const result = validateDeleteTask(3, sampleTasks); // Task 3 has no dependents
    runner.assert(result.isValid, 'Valid deletion should pass');
    runner.assert(result.errors.length === 0, 'Should have no errors');
    runner.assert(result.taskToDelete !== undefined, 'Should return task to delete');
});

// Test 9: Prevent deletion of task with dependents
runner.test('Should prevent deletion of task with dependents', () => {
    const result = validateDeleteTask(2, sampleTasks); // Task 2 has task 3 as dependent
    runner.assert(!result.isValid, 'Deletion of task with dependents should fail');

    const dependentsError = result.errors.find(e => e.code === 'HAS_DEPENDENTS');
    runner.assert(dependentsError !== undefined, 'Should have dependents error');
});

// Test 10: Duplicate title warning
runner.test('Should warn about duplicate titles', () => {
    const duplicateTask = {
        title: "Setup project structure", // Same as task 1
        short_description: "Another setup task",
        detailed_description: "This has the same title as an existing task",
        status: "TODO",
        priority: 3
    };

    const result = validateCreateTask(duplicateTask, sampleTasks);
    runner.assert(result.isValid, 'Duplicate title should be valid but warn');

    const duplicateWarning = result.warnings.find(w => w.code === 'DUPLICATE_TITLE');
    runner.assert(duplicateWarning !== undefined, 'Should have duplicate title warning');
});

// Test 11: Invalid file paths
runner.test('Should reject dangerous file paths', () => {
    const taskWithBadPaths = {
        title: "Task with bad paths",
        short_description: "Has dangerous file paths",
        detailed_description: "This task has dangerous file paths",
        status: "TODO",
        impacted_files: ["../../../etc/passwd", "/absolute/path", "normal\\path"],
        priority: 3
    };

    const result = validateCreateTask(taskWithBadPaths, sampleTasks);
    runner.assert(!result.isValid, 'Task with dangerous paths should fail');

    const pathError = result.errors.find(e => e.code === 'INVALID_FILE_PATHS');
    runner.assert(pathError !== undefined, 'Should have invalid file paths error');
});

// Test 12: Batch operations validation
runner.test('Should validate batch operations atomically', () => {
    const operations = [
        {
            type: 'create',
            data: {
                title: "Batch task 1",
                short_description: "First batch task",
                detailed_description: "First task in batch",
                status: "TODO",
                priority: 3
            }
        },
        {
            type: 'create',
            data: {
                title: "Batch task 2",
                short_description: "Second batch task",
                detailed_description: "Second task in batch",
                status: "TODO",
                dependencies: [999], // Invalid dependency - should fail batch
                priority: 3
            }
        }
    ];

    const result = validateBatchOperations(operations, sampleTasks);
    runner.assert(!result.isValid, 'Batch with invalid operation should fail');
    runner.assert(result.results.length === 2, 'Should process both operations');
    runner.assert(result.results[0].validation.isValid, 'First operation should be valid');
    runner.assert(!result.results[1].validation.isValid, 'Second operation should be invalid');
});

// Test 13: Priority-dependency conflict warning
runner.test('Should warn about critical priority with dependencies', () => {
    const criticalTaskWithDeps = {
        title: "Critical task with deps",
        short_description: "Critical priority but has dependencies",
        detailed_description: "This task is critical but depends on others",
        status: "TODO",
        dependencies: [1],
        priority: 5 // Critical priority
    };

    const result = validateCreateTask(criticalTaskWithDeps, sampleTasks);
    runner.assert(result.isValid, 'Should be valid but warn');

    const priorityWarning = result.warnings.find(w => w.code === 'CRITICAL_WITH_DEPS');
    runner.assert(priorityWarning !== undefined, 'Should have priority-dependency conflict warning');
});

// Test 14: Non-existent task update
runner.test('Should handle update of non-existent task', () => {
    const updateNonExistent = {
        task_id: 999, // Non-existent task
        status: "DONE"
    };

    const result = validateUpdateTask(updateNonExistent, sampleTasks);
    // Note: This might be valid at schema level but would fail at business level
    // The actual MCP tool should handle this case
    runner.assert(result.normalizedData !== null, 'Should normalize data even for non-existent task');
});

// Test 15: Edge case - empty dependencies array
runner.test('Should handle empty dependencies array correctly', () => {
    const taskWithEmptyDeps = {
        title: "Task with empty deps",
        short_description: "Has empty dependencies array",
        detailed_description: "This task has an empty dependencies array",
        status: "TODO",
        dependencies: [], // Empty array
        priority: 3
    };

    const result = validateCreateTask(taskWithEmptyDeps, sampleTasks);
    runner.assert(result.isValid, 'Task with empty dependencies should be valid');
    runner.assert(result.errors.length === 0, 'Should have no errors');
});

// =============================================================================
// RUN TESTS
// =============================================================================

console.log('🔧 CRUD Validation System Test Suite');
console.log('=====================================\n');

runner.run().catch(error => {
    console.error('💥 Test runner failed:', error);
    process.exit(1);
}); 