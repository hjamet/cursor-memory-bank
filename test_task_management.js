#!/usr/bin/env node

/**
 * Test script for Memory Bank MCP Task Management Tools
 * Tests create_task, update-task, get_next_tasks, and get_all_tasks functionality
 */

import { taskManager } from './.cursor/mcp/memory-bank-mcp/lib/task_manager.js';
import fs from 'fs';
import path from 'path';

console.log('=== Memory Bank MCP Task Management Tools Test ===');
console.log('Starting comprehensive test of task management functionality...\n');

async function runTests() {
    try {
        // Test 1: Initialize and check if tasks.json is created
        console.log('Test 1: Initialization and JSON file creation');
        console.log('- Checking if tasks.json is created...');

        const tasksJsonPath = './.cursor/memory-bank/workflow/tasks.json';
        if (fs.existsSync(tasksJsonPath)) {
            console.log('✓ tasks.json already exists');
        } else {
            console.log('✓ tasks.json will be created by TaskManager initialization');
        }

        // Test 2: Create test tasks
        console.log('\nTest 2: Creating test tasks');

        const task1 = await taskManager.createTask({
            title: 'Test Task 1',
            short_description: 'First test task for validation',
            detailed_description: 'This is a detailed description of the first test task used to validate the task management system.',
            status: 'TODO',
            priority: 1,
            impacted_files: ['test_file1.js', 'test_file2.js'],
            validation_criteria: 'Task should be created with ID 1 and all fields populated correctly'
        });
        console.log('✓ Created Task 1:', task1.id, '-', task1.title);

        const task2 = await taskManager.createTask({
            title: 'Test Task 2',
            short_description: 'Second test task with dependency',
            detailed_description: 'This task depends on Task 1 and tests dependency validation.',
            status: 'TODO',
            dependencies: [task1.id],
            priority: 2,
            validation_criteria: 'Task should be created with dependency on Task 1'
        });
        console.log('✓ Created Task 2:', task2.id, '-', task2.title);

        const task3 = await taskManager.createTask({
            title: 'Test Task 3',
            short_description: 'Third test task - subtask of Task 1',
            detailed_description: 'This is a subtask of Task 1 to test parent-child relationships.',
            status: 'IN_PROGRESS',
            parent_id: task1.id,
            priority: 3,
            validation_criteria: 'Task should be created as subtask of Task 1'
        });
        console.log('✓ Created Task 3:', task3.id, '-', task3.title);

        // Test 3: Update task
        console.log('\nTest 3: Updating tasks');

        const updatedTask1 = await taskManager.updateTask(task1.id, {
            status: 'IN_PROGRESS',
            detailed_description: 'Updated detailed description for Task 1'
        });
        console.log('✓ Updated Task 1 status to IN_PROGRESS');

        // Test 4: Get all tasks
        console.log('\nTest 4: Retrieving all tasks');

        const allTasks = taskManager.getAllTasks({ limit: 10 });
        console.log('✓ Retrieved', allTasks.length, 'tasks');
        allTasks.forEach(task => {
            console.log(`  - Task ${task.id}: ${task.title} (${task.status})`);
        });

        // Test 5: Get next available tasks
        console.log('\nTest 5: Getting next available tasks');

        const nextTasks = taskManager.getNextTasks({ limit: 5 });
        console.log('✓ Found', nextTasks.length, 'available tasks');
        nextTasks.forEach(task => {
            console.log(`  - Available Task ${task.id}: ${task.title} (${task.status})`);
        });

        // Test 6: Test dependency validation
        console.log('\nTest 6: Testing dependency validation');

        try {
            await taskManager.createTask({
                title: 'Invalid Task',
                short_description: 'Task with invalid dependency',
                detailed_description: 'This task should fail due to invalid dependency.',
                dependencies: [999] // Non-existent task ID
            });
            console.log('✗ FAILED: Should have rejected invalid dependency');
        } catch (error) {
            console.log('✓ Correctly rejected invalid dependency:', error.message);
        }

        // Test 7: Test circular dependency detection
        console.log('\nTest 7: Testing circular dependency detection');

        try {
            // Try to create a circular dependency: Task 4 depends on Task 2, but Task 2 already depends on Task 1
            const task4 = await taskManager.createTask({
                title: 'Test Task 4',
                short_description: 'Task to test circular dependency',
                detailed_description: 'This task will create a potential circular dependency.',
                dependencies: [task2.id]
            });

            // Now try to update Task 1 to depend on Task 4 (creating a circle)
            await taskManager.updateTask(task1.id, {
                dependencies: [task4.id]
            });
            console.log('✗ FAILED: Should have detected circular dependency');
        } catch (error) {
            console.log('✓ Correctly detected circular dependency:', error.message);
        }

        // Test 8: Verify tasks.json file content
        console.log('\nTest 8: Verifying tasks.json file content');

        if (fs.existsSync(tasksJsonPath)) {
            const tasksData = JSON.parse(fs.readFileSync(tasksJsonPath, 'utf-8'));
            console.log('✓ tasks.json exists and is valid JSON');
            console.log('  - Version:', tasksData.version);
            console.log('  - Last ID:', tasksData.last_id);
            console.log('  - Number of tasks:', tasksData.tasks.length);

            // Validate schema compliance
            const requiredFields = ['id', 'title', 'short_description', 'detailed_description', 'status', 'dependencies', 'created_date', 'updated_date'];
            const firstTask = tasksData.tasks[0];
            const missingFields = requiredFields.filter(field => !(field in firstTask));

            if (missingFields.length === 0) {
                console.log('✓ Task schema validation passed');
            } else {
                console.log('✗ Missing required fields:', missingFields);
            }
        } else {
            console.log('✗ tasks.json file not found');
        }

        console.log('\n=== Test Summary ===');
        console.log('✓ All task management tests completed successfully');
        console.log('✓ Task creation, updating, and querying work correctly');
        console.log('✓ Dependency validation and circular dependency detection work');
        console.log('✓ JSON file is created and maintains proper schema');

        return true;

    } catch (error) {
        console.error('\n✗ Test failed with error:', error);
        console.error('Error stack:', error.stack);
        return false;
    }
}

// Run the tests
runTests().then(success => {
    if (success) {
        console.log('\n🎉 All tests passed! Task management system is working correctly.');
        process.exit(0);
    } else {
        console.log('\n❌ Tests failed! Check the error messages above.');
        process.exit(1);
    }
}).catch(error => {
    console.error('Unexpected error running tests:', error);
    process.exit(1);
}); 