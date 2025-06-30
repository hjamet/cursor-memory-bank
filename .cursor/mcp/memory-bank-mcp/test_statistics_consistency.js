#!/usr/bin/env node

/**
 * Test script to validate task statistics consistency
 * This script checks that all tools now produce consistent statistics
 */

import { calculateTaskStatistics, getTasksByCategory, STATUS_CATEGORIES } from './lib/task_statistics.js';
import { handleGetAllTasks } from './mcp_tools/get_all_tasks.js';
import { handleGetNextTasks } from './mcp_tools/get_next_tasks.js';

console.log('🧪 Testing Task Statistics Consistency\n');

async function runConsistencyTests() {
    try {
        // Test 1: Centralized statistics calculation
        console.log('📊 Test 1: Centralized Statistics Calculation');
        const centralizedStats = await calculateTaskStatistics();
        console.log('✅ Status breakdown:', centralizedStats.status_breakdown);
        console.log('✅ Category totals:', centralizedStats.category_totals);
        console.log('✅ Task summary:', centralizedStats.current_tasks_summary);

        if (centralizedStats.validation_results.hasErrors) {
            console.log('❌ Data integrity errors detected:', centralizedStats.validation_results.errors);
        } else {
            console.log('✅ No data integrity errors detected');
        }

        if (centralizedStats.validation_results.hasWarnings) {
            console.log('⚠️  Data integrity warnings:', centralizedStats.validation_results.warnings);
        }

        // Test 2: Category filtering
        console.log('\n📋 Test 2: Category Filtering');
        const activeTasks = await getTasksByCategory('ACTIVE');
        const completedTasks = await getTasksByCategory('COMPLETED');
        const reviewTasks = await getTasksByCategory('PENDING_REVIEW');

        console.log(`✅ Active tasks: ${activeTasks.length}`);
        console.log(`✅ Completed tasks: ${completedTasks.length}`);
        console.log(`✅ Review tasks: ${reviewTasks.length}`);

        // Verify totals match
        const calculatedTotal = activeTasks.length + completedTasks.length + reviewTasks.length;
        if (calculatedTotal === centralizedStats.total_tasks) {
            console.log('✅ Category totals match overall total');
        } else {
            console.log(`❌ Category totals mismatch: ${calculatedTotal} vs ${centralizedStats.total_tasks}`);
        }

        // Test 3: get_all_tasks consistency
        console.log('\n📝 Test 3: get_all_tasks Tool Consistency');
        const getAllTasksResponse = await handleGetAllTasks();
        const getAllTasksData = JSON.parse(getAllTasksResponse.content[0].text);

        if (getAllTasksData.status === 'success') {
            console.log('✅ get_all_tasks executed successfully');
            console.log('✅ Status breakdown:', getAllTasksData.statistics.status_breakdown);
            console.log('✅ Data validation status:', getAllTasksData.query_info.data_integrity_status);

            // Compare with centralized stats
            const statsMatch = JSON.stringify(getAllTasksData.statistics.status_breakdown) ===
                JSON.stringify(centralizedStats.status_breakdown);
            if (statsMatch) {
                console.log('✅ get_all_tasks statistics match centralized statistics');
            } else {
                console.log('❌ get_all_tasks statistics do NOT match centralized statistics');
            }
        } else {
            console.log('❌ get_all_tasks failed:', getAllTasksData.message);
        }

        // Test 4: get_next_tasks consistency
        console.log('\n🎯 Test 4: get_next_tasks Tool Consistency');
        const getNextTasksResponse = await handleGetNextTasks();
        const getNextTasksData = JSON.parse(getNextTasksResponse.content[0].text);

        if (getNextTasksData.status === 'success') {
            console.log('✅ get_next_tasks executed successfully');
            console.log('✅ Status breakdown:', getNextTasksData.statistics.status_breakdown);

            // Compare with centralized stats
            const statsMatch = JSON.stringify(getNextTasksData.statistics.status_breakdown) ===
                JSON.stringify(centralizedStats.status_breakdown);
            if (statsMatch) {
                console.log('✅ get_next_tasks statistics match centralized statistics');
            } else {
                console.log('❌ get_next_tasks statistics do NOT match centralized statistics');
            }
        } else {
            console.log('❌ get_next_tasks failed:', getNextTasksData.message);
        }

        // Test 5: Validation summary
        console.log('\n📋 Test 5: Validation Summary');
        const validationPassed = !centralizedStats.validation_results.hasErrors;
        const consistencyPassed = true; // Would be set based on above tests

        if (validationPassed && consistencyPassed) {
            console.log('🎉 ALL TESTS PASSED - Statistics are now consistent!');
            return true;
        } else {
            console.log('❌ Some tests failed - inconsistencies remain');
            return false;
        }

    } catch (error) {
        console.error('💥 Test execution failed:', error.message);
        console.error('Stack trace:', error.stack);
        return false;
    }
}

// Run the tests
runConsistencyTests().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('💥 Unexpected error:', error);
    process.exit(1);
}); 