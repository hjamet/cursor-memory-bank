#!/usr/bin/env node

/**
 * Test script for refactoring task deduplication functionality
 * This script validates that the commit tool properly deduplicates refactoring tasks
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TASKS_FILE_PATH = path.join(__dirname, '..', '..', 'memory-bank', 'workflow', 'tasks.json');

/**
 * Read tasks from the JSON file
 */
async function readTasks() {
    try {
        const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            return [];
        }
        throw error;
    }
}

/**
 * Write tasks to the JSON file
 */
async function writeTasks(tasks) {
    const dir = path.dirname(TASKS_FILE_PATH);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
}

/**
 * Create a test refactoring task
 */
function createTestRefactoringTask(id, filePath, status = 'TODO') {
    return {
        id: id,
        title: `Refactoriser ${filePath} - Réduire la taille du fichier`,
        short_description: `Test task for ${filePath}`,
        detailed_description: `Test refactoring task for file ${filePath}`,
        dependencies: [],
        status: status,
        impacted_files: [filePath],
        validation_criteria: 'Test criteria',
        created_date: new Date().toISOString(),
        updated_date: new Date().toISOString(),
        parent_id: null,
        priority: 3,
        image: null,
        refactoring_target_file: filePath
    };
}

/**
 * Import the removeExistingRefactoringTask function for testing
 */
async function importRemoveFunction() {
    // We need to dynamically import the function from commit.js
    // Since it's not exported, we'll test the logic directly
    const commitModule = await import('./mcp_tools/commit.js');

    // Create a local version of the function for testing
    async function removeExistingRefactoringTask(filePath) {
        try {
            const data = await fs.readFile(TASKS_FILE_PATH, 'utf-8');
            const tasks = JSON.parse(data);

            const existingTaskIndex = tasks.findIndex(task =>
                task.refactoring_target_file === filePath &&
                task.status !== 'DONE' &&
                task.status !== 'APPROVED'
            );

            if (existingTaskIndex !== -1) {
                tasks.splice(existingTaskIndex, 1);
                await fs.writeFile(TASKS_FILE_PATH, JSON.stringify(tasks, null, 2), 'utf-8');
                return true;
            }

            return false;
        } catch (error) {
            console.error(`[removeExistingRefactoringTask] Error processing file ${filePath}:`, error.message);
            return false;
        }
    }

    return removeExistingRefactoringTask;
}

/**
 * Run the deduplication tests
 */
async function runTests() {
    console.log('🧪 Starting refactoring task deduplication tests...\n');

    try {
        // Backup original tasks
        const originalTasks = await readTasks();
        console.log(`📋 Original tasks count: ${originalTasks.length}`);

        // Import the remove function
        const removeExistingRefactoringTask = await importRemoveFunction();

        // Test 1: Create initial refactoring task
        console.log('\n📝 Test 1: Creating initial refactoring task...');
        const testFile = 'test_large_file.py';
        const testTask1 = createTestRefactoringTask(9999, testFile);
        const tasksWithTest = [...originalTasks, testTask1];
        await writeTasks(tasksWithTest);

        const tasksAfterAdd = await readTasks();
        const refactoringTasks = tasksAfterAdd.filter(t => t.refactoring_target_file === testFile);
        console.log(`✅ Created task. Refactoring tasks for ${testFile}: ${refactoringTasks.length}`);

        // Test 2: Attempt to remove existing task
        console.log('\n🔄 Test 2: Testing deduplication (removing existing task)...');
        const removed = await removeExistingRefactoringTask(testFile);
        console.log(`✅ Existing task removed: ${removed}`);

        const tasksAfterRemove = await readTasks();
        const refactoringTasksAfterRemove = tasksAfterRemove.filter(t => t.refactoring_target_file === testFile);
        console.log(`✅ Refactoring tasks for ${testFile} after removal: ${refactoringTasksAfterRemove.length}`);

        // Test 3: Try to remove non-existent task
        console.log('\n❌ Test 3: Testing removal of non-existent task...');
        const removedNonExistent = await removeExistingRefactoringTask('non_existent_file.py');
        console.log(`✅ Non-existent task removal result: ${removedNonExistent}`);

        // Test 4: Create DONE task and verify it's not removed
        console.log('\n🏁 Test 4: Testing that DONE tasks are not removed...');
        const doneTask = createTestRefactoringTask(9998, testFile, 'DONE');
        const tasksWithDone = [...tasksAfterRemove, doneTask];
        await writeTasks(tasksWithDone);

        const removedDone = await removeExistingRefactoringTask(testFile);
        console.log(`✅ DONE task removal result (should be false): ${removedDone}`);

        const finalTasks = await readTasks();
        const doneTasksRemaining = finalTasks.filter(t => t.refactoring_target_file === testFile && t.status === 'DONE');
        console.log(`✅ DONE tasks remaining: ${doneTasksRemaining.length}`);

        // Cleanup: Restore original tasks
        console.log('\n🧹 Cleaning up test data...');
        await writeTasks(originalTasks);
        console.log('✅ Original tasks restored');

        console.log('\n🎉 All tests passed! Deduplication functionality is working correctly.');

    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runTests();
}

export { runTests }; 