#!/usr/bin/env node

/**
 * Test Suite for Zod Error Handling Fix
 * 
 * This test validates that Zod schema validation errors are properly handled
 * and return clean error messages instead of causing interruptions.
 */

import {
    validateCreateTask,
    validateUpdateTask
} from './lib/task_crud_validator.js';

// =============================================================================
// TEST FRAMEWORK
// =============================================================================

class ZodErrorTestRunner {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(description, testFn) {
        this.tests.push({ description, testFn });
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(`Assertion failed: ${message}`);
        }
    }

    async run() {
        console.log('🧪 Running Zod Error Handling Tests...\n');

        for (const { description, testFn } of this.tests) {
            try {
                console.log(`⚡ ${description}`);
                await testFn();
                console.log('✅ PASS\n');
                this.passed++;
            } catch (error) {
                console.log(`❌ FAIL: ${error.message}\n`);
                this.failed++;
            }
        }

        console.log('📊 Test Results:');
        console.log(`✅ Passed: ${this.passed}`);
        console.log(`❌ Failed: ${this.failed}`);
        console.log(`📈 Success Rate: ${(this.passed / (this.passed + this.failed) * 100).toFixed(1)}%`);

        return this.failed === 0;
    }
}

// =============================================================================
// TEST DATA
// =============================================================================

const sampleTasks = [
    {
        id: 1,
        title: "Sample Task 1",
        short_description: "A sample task",
        detailed_description: "This is a sample task for testing",
        status: "TODO",
        dependencies: [],
        created_date: "2025-01-01T00:00:00.000Z",
        updated_date: "2025-01-01T00:00:00.000Z",
        priority: 3
    }
];

// =============================================================================
// TESTS
// =============================================================================

const runner = new ZodErrorTestRunner();

// Test 1: Empty title (should return clean error, not interrupt)
runner.test('Should handle empty title validation error cleanly', () => {
    const invalidTask = {
        title: "", // Empty title should trigger Zod error
        short_description: "Test description",
        detailed_description: "Test detailed description"
    };

    const result = validateCreateTask(invalidTask, sampleTasks);

    runner.assert(!result.isValid, 'Task with empty title should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');
    runner.assert(result.errors.some(e => e.type === 'SCHEMA_VALIDATION_ERROR'), 'Should have schema validation error');

    // Critical: Ensure the result is JSON serializable
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Result should be JSON serializable');
    } catch (e) {
        throw new Error(`Result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Error details:', result.errors[0].message);
});

// Test 2: Invalid priority (should return clean error, not interrupt)
runner.test('Should handle invalid priority validation error cleanly', () => {
    const invalidTask = {
        title: "Valid title",
        short_description: "Test description",
        detailed_description: "Test detailed description",
        priority: 10 // Invalid priority (should be 1-5)
    };

    const result = validateCreateTask(invalidTask, sampleTasks);

    runner.assert(!result.isValid, 'Task with invalid priority should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');

    // Critical: Ensure the result is JSON serializable
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Result should be JSON serializable');
    } catch (e) {
        throw new Error(`Result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Error details:', result.errors[0].message);
});

// Test 3: Invalid status (should return clean error, not interrupt)
runner.test('Should handle invalid status validation error cleanly', () => {
    const invalidTask = {
        title: "Valid title",
        short_description: "Test description",
        detailed_description: "Test detailed description",
        status: "INVALID_STATUS" // Invalid status
    };

    const result = validateCreateTask(invalidTask, sampleTasks);

    runner.assert(!result.isValid, 'Task with invalid status should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');

    // Critical: Ensure the result is JSON serializable
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Result should be JSON serializable');
    } catch (e) {
        throw new Error(`Result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Error details:', result.errors[0].message);
});

// Test 4: Null/undefined input (should return clean error, not interrupt)
runner.test('Should handle null input validation error cleanly', () => {
    const result = validateCreateTask(null, sampleTasks);

    runner.assert(!result.isValid, 'Null input should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');
    runner.assert(result.errors.some(e => e.code === 'NULL_INPUT'), 'Should have null input error');

    // Critical: Ensure the result is JSON serializable
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Result should be JSON serializable');
    } catch (e) {
        throw new Error(`Result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Error details:', result.errors[0].message);
});

// Test 5: Update task with invalid data (should return clean error, not interrupt)
runner.test('Should handle update validation errors cleanly', () => {
    const invalidUpdate = {
        task_id: 1,
        title: "", // Empty title
        priority: -1 // Invalid priority
    };

    const result = validateUpdateTask(invalidUpdate, sampleTasks);

    runner.assert(!result.isValid, 'Invalid update should fail validation');
    runner.assert(result.errors.length > 0, 'Should have validation errors');

    // Critical: Ensure the result is JSON serializable
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Result should be JSON serializable');
    } catch (e) {
        throw new Error(`Result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Error count:', result.errors.length);
});

// Test 6: Complex nested validation errors (serialization stress test)
runner.test('Should handle complex validation errors without serialization issues', () => {
    const complexInvalidTask = {
        title: "", // Empty title
        short_description: "", // Empty description
        detailed_description: "", // Empty detailed description
        status: "INVALID_STATUS", // Invalid status
        priority: 100, // Invalid priority
        dependencies: [999, 1000, 1001], // Non-existent dependencies
        parent_id: 999 // Non-existent parent
    };

    const result = validateCreateTask(complexInvalidTask, sampleTasks);

    runner.assert(!result.isValid, 'Complex invalid task should fail validation');
    runner.assert(result.errors.length > 0, 'Should have multiple validation errors');

    // Critical: Ensure the result is JSON serializable even with multiple complex errors
    try {
        const serialized = JSON.stringify(result);
        runner.assert(serialized.length > 0, 'Complex result should be JSON serializable');

        // Parse back to ensure it's valid JSON
        const parsed = JSON.parse(serialized);
        runner.assert(parsed.errors.length > 0, 'Parsed result should maintain error structure');
    } catch (e) {
        throw new Error(`Complex result is not JSON serializable: ${e.message}`);
    }

    console.log('   📝 Complex error count:', result.errors.length);
});

// =============================================================================
// RUN TESTS
// =============================================================================

async function runTests() {
    console.log('🔧 Testing Zod Error Handling Fix');
    console.log('='.repeat(50));

    const success = await runner.run();

    if (success) {
        console.log('\n🎉 All Zod error handling tests passed!');
        console.log('✅ Schema validation errors now return clean messages instead of causing interruptions.');
        process.exit(0);
    } else {
        console.log('\n💥 Some tests failed. Zod error handling needs more work.');
        process.exit(1);
    }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runTests().catch(error => {
        console.error('Test execution failed:', error);
        process.exit(1);
    });
}

export { ZodErrorTestRunner }; 