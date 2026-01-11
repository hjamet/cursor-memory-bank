#!/usr/bin/env node

/**
 * Test script for duplicate task detection functionality
 * This script validates that the create_task tool properly detects and prevents duplicates
 */

import { handleCreateTask } from './mcp_tools/create_task.js';

/**
 * Test cases for duplicate detection
 */
const testCases = [
    {
        name: "Identical title (should be blocked)",
        task1: {
            title: "Test adversarial de duplication de tâches",
            short_description: "Premier test de duplication",
            detailed_description: "Description détaillée du premier test"
        },
        task2: {
            title: "Test adversarial de duplication de tâches",
            short_description: "Deuxième test de duplication",
            detailed_description: "Description différente du deuxième test"
        },
        expectBlocked: true
    },
    {
        name: "Very similar titles (should warn but allow)",
        task1: {
            title: "Corriger le bug de validation",
            short_description: "Premier test de similarité",
            detailed_description: "Description du premier test"
        },
        task2: {
            title: "Corriger le bug de validations",
            short_description: "Deuxième test de similarité",
            detailed_description: "Description du deuxième test"
        },
        expectBlocked: false
    },
    {
        name: "Completely different tasks (should allow)",
        task1: {
            title: "Implémenter l'authentification JWT",
            short_description: "Système d'authentification sécurisé",
            detailed_description: "Implémentation complète avec tokens"
        },
        task2: {
            title: "Créer l'interface utilisateur",
            short_description: "Interface moderne et responsive",
            detailed_description: "Design avec React et Tailwind"
        },
        expectBlocked: false
    }
];

/**
 * Run a single test case
 */
async function runTestCase(testCase) {
    console.log(`\n🧪 Test: ${testCase.name}`);
    console.log(`Expected result: ${testCase.expectBlocked ? 'BLOCKED' : 'ALLOWED'}`);

    try {
        // Create first task
        const result1 = await handleCreateTask(testCase.task1);
        const response1 = JSON.parse(result1.content[0].text);

        if (response1.status !== 'success') {
            console.log(`❌ Failed to create first task: ${response1.message}`);
            return false;
        }

        console.log(`✅ First task created: #${response1.created_task.id}`);

        // Try to create second task (potential duplicate)
        const result2 = await handleCreateTask(testCase.task2);
        const response2 = JSON.parse(result2.content[0].text);

        if (testCase.expectBlocked) {
            if (response2.status === 'error' && response2.message.includes('identical title')) {
                console.log(`✅ Test PASSED: Duplicate correctly blocked`);
                console.log(`   Reason: ${response2.duplicate_detection?.reason}`);
                return true;
            } else {
                console.log(`❌ Test FAILED: Expected blocking but task was created`);
                return false;
            }
        } else {
            if (response2.status === 'success') {
                console.log(`✅ Test PASSED: Task correctly allowed`);
                console.log(`   Second task created: #${response2.created_task.id}`);
                return true;
            } else {
                console.log(`❌ Test FAILED: Expected creation but task was blocked`);
                console.log(`   Error: ${response2.message}`);
                return false;
            }
        }

    } catch (error) {
        console.log(`❌ Test ERROR: ${error.message}`);
        return false;
    }
}

/**
 * Main test function
 */
async function runTests() {
    console.log('🚀 Starting duplicate detection tests...\n');

    let passedTests = 0;
    let totalTests = testCases.length;

    for (const testCase of testCases) {
        const passed = await runTestCase(testCase);
        if (passed) passedTests++;
    }

    console.log(`\n📊 Test Results:`);
    console.log(`   Passed: ${passedTests}/${totalTests}`);
    console.log(`   Success rate: ${Math.round((passedTests / totalTests) * 100)}%`);

    if (passedTests === totalTests) {
        console.log(`\n🎉 All tests passed! Duplicate detection is working correctly.`);
        process.exit(0);
    } else {
        console.log(`\n⚠️  Some tests failed. Please review the implementation.`);
        process.exit(1);
    }
}

// Run tests if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runTests().catch(console.error);
} 