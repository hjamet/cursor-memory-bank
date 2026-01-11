#!/usr/bin/env node

/**
 * Comprehensive Test Suite for Circular Dependency Prevention
 * 
 * This script tests the circular dependency validation system to ensure it correctly
 * prevents the creation of cycles in task dependencies. It includes both positive
 * and negative test cases to validate the robustness of the implementation.
 */

import {
    detectCircularDependencies,
    validateNoCycles,
    validateReplacementDependencies,
    validateNewTaskDependencies,
    formatCycleErrors,
    analyzeDependencyGraph
} from './mcp_tools/circular_dependency_validator.js';

// Test data setup
const testTasks = [
    { id: 1, title: 'Task A', dependencies: [] },
    { id: 2, title: 'Task B', dependencies: [1] },
    { id: 3, title: 'Task C', dependencies: [2] },
    { id: 4, title: 'Task D', dependencies: [3] },
    { id: 5, title: 'Task E', dependencies: [] },
    { id: 6, title: 'Task F', dependencies: [5] },
    { id: 7, title: 'Task G', dependencies: [6] },
    { id: 8, title: 'Task H', dependencies: [7, 1] }, // Multiple dependencies
];

// Test cases for circular dependencies
const cyclicTasks = [
    { id: 10, title: 'Cycle A', dependencies: [11] },
    { id: 11, title: 'Cycle B', dependencies: [12] },
    { id: 12, title: 'Cycle C', dependencies: [10] }, // Creates cycle: 10 -> 11 -> 12 -> 10
    { id: 13, title: 'Self Cycle', dependencies: [13] }, // Self-referencing cycle
    { id: 14, title: 'Complex A', dependencies: [15, 16] },
    { id: 15, title: 'Complex B', dependencies: [17] },
    { id: 16, title: 'Complex C', dependencies: [17] },
    { id: 17, title: 'Complex D', dependencies: [14] }, // Creates complex cycle
];

/**
 * Test runner with colored output
 */
class TestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
        this.tests = [];
    }

    test(name, testFunction) {
        this.tests.push({ name, testFunction });
    }

    async run() {
        console.log('🚀 Starting Circular Dependency Prevention Test Suite\n');

        for (const { name, testFunction } of this.tests) {
            try {
                await testFunction();
                console.log(`✅ ${name}`);
                this.passed++;
            } catch (error) {
                console.log(`❌ ${name}`);
                console.log(`   Error: ${error.message}`);
                this.failed++;
            }
        }

        console.log(`\n📊 Test Results: ${this.passed} passed, ${this.failed} failed`);

        if (this.failed > 0) {
            console.log('🔴 Some tests failed - circular dependency prevention needs attention');
            process.exit(1);
        } else {
            console.log('🟢 All tests passed - circular dependency prevention is working correctly');
        }
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message);
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
}

const runner = new TestRunner();

// Test 1: Basic cycle detection
runner.test('Basic cycle detection should identify simple cycles', () => {
    const taskMap = new Map(cyclicTasks.map(task => [task.id, task]));
    const cycles = detectCircularDependencies(cyclicTasks, taskMap);

    runner.assert(cycles.length > 0, 'Should detect at least one cycle');
    runner.assert(cycles.some(cycle => cycle.includes(10) && cycle.includes(11) && cycle.includes(12)),
        'Should detect the 10->11->12->10 cycle');
    runner.assert(cycles.some(cycle => cycle.includes(13) && cycle.length === 2),
        'Should detect the self-referencing cycle');
});

// Test 2: No false positives on acyclic graphs
runner.test('Should not detect cycles in acyclic graphs', () => {
    const taskMap = new Map(testTasks.map(task => [task.id, task]));
    const cycles = detectCircularDependencies(testTasks, taskMap);

    runner.assertEqual(cycles.length, 0, 'Acyclic graph should have no cycles');
});

// Test 3: New task dependency validation - valid case
runner.test('Should allow valid new task dependencies', () => {
    const result = validateNewTaskDependencies(testTasks, [1, 2, 3]);

    runner.assert(result.isValid, 'Valid dependencies should be allowed');
    runner.assertEqual(result.cycles.length, 0, 'Should not report any cycles');
});

// Test 4: New task dependency validation - invalid case
runner.test('Should reject new task dependencies that reference non-existent tasks', () => {
    const result = validateNewTaskDependencies(testTasks, [1, 999, 2]);

    runner.assert(!result.isValid, 'Should reject non-existent dependencies');
    runner.assert(result.missingDependencies.includes(999), 'Should identify missing dependency');
});

// Test 5: Replacement dependency validation - valid case
runner.test('Should allow valid dependency replacements', () => {
    const result = validateReplacementDependencies(testTasks, 4, [1, 2]); // Change task 4 deps from [3] to [1, 2]

    runner.assert(result.isValid, 'Valid replacement should be allowed');
    runner.assertEqual(result.cycles.length, 0, 'Should not create any cycles');
});

// Test 6: Replacement dependency validation - creates cycle
runner.test('Should reject dependency replacements that create cycles', () => {
    const result = validateReplacementDependencies(testTasks, 1, [4]); // Make task 1 depend on task 4, creating cycle

    runner.assert(!result.isValid, 'Should reject cycle-creating replacement');
    runner.assert(result.cycles.length > 0, 'Should detect the created cycle');
});

// Test 7: Complex cycle detection
runner.test('Should detect complex multi-node cycles', () => {
    const taskMap = new Map(cyclicTasks.map(task => [task.id, task]));
    const cycles = detectCircularDependencies(cyclicTasks, taskMap);

    // Should detect the complex cycle: 14 -> 15 -> 17 -> 14 and 14 -> 16 -> 17 -> 14
    const complexCycles = cycles.filter(cycle => cycle.includes(14) && cycle.includes(17));
    runner.assert(complexCycles.length > 0, 'Should detect complex multi-path cycles');
});

// Test 8: Cycle error formatting
runner.test('Should format cycle errors correctly', () => {
    const taskMap = new Map(cyclicTasks.map(task => [task.id, task]));
    const cycles = [[10, 11, 12, 10]]; // Simple cycle
    const errors = formatCycleErrors(cycles, taskMap);

    runner.assert(errors.length === 1, 'Should format one error');
    runner.assert(errors[0].includes('Cycle A'), 'Should include task titles');
    runner.assert(errors[0].includes('→'), 'Should show dependency direction');
});

// Test 9: Dependency graph analysis
runner.test('Should analyze dependency graph health correctly', () => {
    // Test healthy graph
    const healthyAnalysis = analyzeDependencyGraph(testTasks);
    runner.assert(healthyAnalysis.isHealthy, 'Acyclic graph should be healthy');
    runner.assertEqual(healthyAnalysis.cycleCount, 0, 'Should report zero cycles');

    // Test unhealthy graph
    const unhealthyAnalysis = analyzeDependencyGraph(cyclicTasks);
    runner.assert(!unhealthyAnalysis.isHealthy, 'Cyclic graph should be unhealthy');
    runner.assert(unhealthyAnalysis.cycleCount > 0, 'Should report cycles');
    runner.assert(unhealthyAnalysis.tasksInCycles.length > 0, 'Should identify tasks in cycles');
});

// Test 10: Edge cases
runner.test('Should handle edge cases correctly', () => {
    // Empty task list
    const emptyResult = validateNewTaskDependencies([], []);
    runner.assert(emptyResult.isValid, 'Empty dependencies should be valid');

    // Single task with no dependencies
    const singleTask = [{ id: 1, title: 'Single', dependencies: [] }];
    const singleResult = validateNewTaskDependencies(singleTask, []);
    runner.assert(singleResult.isValid, 'Single task with no deps should be valid');

    // Non-existent task ID in validation
    const nonExistentResult = validateReplacementDependencies(testTasks, 999, [1, 2]);
    runner.assert(!nonExistentResult.isValid, 'Should reject updates to non-existent tasks');
});

// Test 11: Performance test with large graph
runner.test('Should handle large dependency graphs efficiently', () => {
    // Create a large acyclic graph
    const largeTasks = [];
    for (let i = 1; i <= 1000; i++) {
        const deps = i > 1 ? [i - 1] : [];
        largeTasks.push({ id: i, title: `Task ${i}`, dependencies: deps });
    }

    const startTime = Date.now();
    const result = validateNewTaskDependencies(largeTasks, [500, 501, 502]);
    const endTime = Date.now();

    runner.assert(result.isValid, 'Large graph validation should succeed');
    runner.assert(endTime - startTime < 1000, 'Should complete within 1 second');
});

// Test 12: Stress test - create and detect multiple cycles
runner.test('Should detect all cycles in complex graphs', () => {
    const complexTasks = [
        // Chain 1: A -> B -> C -> A
        { id: 1, title: 'A1', dependencies: [2] },
        { id: 2, title: 'B1', dependencies: [3] },
        { id: 3, title: 'C1', dependencies: [1] },

        // Chain 2: D -> E -> F -> D
        { id: 4, title: 'D2', dependencies: [5] },
        { id: 5, title: 'E2', dependencies: [6] },
        { id: 6, title: 'F2', dependencies: [4] },

        // Interconnected: G -> H -> I -> G, and G -> J -> I
        { id: 7, title: 'G3', dependencies: [8, 10] },
        { id: 8, title: 'H3', dependencies: [9] },
        { id: 9, title: 'I3', dependencies: [7] },
        { id: 10, title: 'J3', dependencies: [9] },
    ];

    const taskMap = new Map(complexTasks.map(task => [task.id, task]));
    const cycles = detectCircularDependencies(complexTasks, taskMap);

    runner.assert(cycles.length >= 2, 'Should detect at least 2 distinct cycles');

    // Verify specific cycles are detected
    const cycle1 = cycles.some(cycle => cycle.includes(1) && cycle.includes(2) && cycle.includes(3));
    const cycle2 = cycles.some(cycle => cycle.includes(4) && cycle.includes(5) && cycle.includes(6));

    runner.assert(cycle1, 'Should detect first cycle (1-2-3)');
    runner.assert(cycle2, 'Should detect second cycle (4-5-6)');
});

// Run all tests
runner.run().catch(error => {
    console.error('Test runner failed:', error);
    process.exit(1);
}); 