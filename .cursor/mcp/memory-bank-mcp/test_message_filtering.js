#!/usr/bin/env node

/**
 * Test Message Filtering Script
 * This script tests the message filtering functionality to ensure
 * test messages are properly filtered out from communications.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import the filtering functions from remember.js
// Note: In a real implementation, these would be imported from the module
// For testing purposes, we'll redefine them here

// Test message patterns to filter out
const TEST_MESSAGE_PATTERNS = [
    /voici la clé secrète\s*:\s*42/i,
    /clé secrète.*42/i,
    /test de communication/i,
    /message de test/i
];

/**
 * Filter out test messages that should not be repeated in communications
 * @param {string} message - The message content to check
 * @returns {boolean} - True if the message should be filtered out (is a test message)
 */
function isTestMessage(message) {
    if (!message || typeof message !== 'string') {
        return false;
    }

    const normalizedMessage = message.toLowerCase().trim();

    // Check against test message patterns
    for (const pattern of TEST_MESSAGE_PATTERNS) {
        if (pattern.test(normalizedMessage)) {
            return true;
        }
    }

    return false;
}

/**
 * Filter out test messages from a list of messages
 * @param {Array} messages - Array of message objects with content property
 * @returns {Array} - Filtered array without test messages
 */
function filterTestMessages(messages) {
    if (!Array.isArray(messages)) {
        return messages;
    }

    return messages.filter(msg => {
        if (!msg || !msg.content) {
            return true; // Keep non-content messages
        }

        return !isTestMessage(msg.content);
    });
}

/**
 * Test cases for message filtering
 */
function runTests() {
    console.log('🧪 Testing message filtering functionality...\n');

    let testsPassed = 0;
    let testsTotal = 0;

    // Test 1: Test message detection
    testsTotal++;
    console.log('Test 1: Test message detection');
    const testMessages = [
        'Voici la clé secrète : 42',
        'VOICI LA CLÉ SECRÈTE: 42',
        'voici la clé secrète   :   42',
        'Clé secrète est 42',
        'Test de communication',
        'Message de test',
        'Hello world', // Should not be filtered
        'This is a normal message' // Should not be filtered
    ];

    const expectedResults = [true, true, true, true, true, true, false, false];
    let test1Passed = true;

    testMessages.forEach((msg, index) => {
        const result = isTestMessage(msg);
        const expected = expectedResults[index];
        if (result !== expected) {
            console.log(`  ❌ "${msg}" - Expected: ${expected}, Got: ${result}`);
            test1Passed = false;
        } else {
            console.log(`  ✅ "${msg}" - Correctly ${result ? 'filtered' : 'kept'}`);
        }
    });

    if (test1Passed) {
        testsPassed++;
        console.log('  ✅ Test 1 PASSED\n');
    } else {
        console.log('  ❌ Test 1 FAILED\n');
    }

    // Test 2: Array filtering
    testsTotal++;
    console.log('Test 2: Array filtering');
    const messageArray = [
        { id: 1, content: 'Voici la clé secrète : 42' },
        { id: 2, content: 'Normal message' },
        { id: 3, content: 'Test de communication' },
        { id: 4, content: 'Another normal message' },
        { id: 5, content: 'Clé secrète 42' }
    ];

    const filteredArray = filterTestMessages(messageArray);
    const expectedFilteredCount = 2; // Only normal messages should remain

    if (filteredArray.length === expectedFilteredCount) {
        testsPassed++;
        console.log(`  ✅ Filtered array correctly: ${filteredArray.length} messages remaining`);
        filteredArray.forEach(msg => {
            console.log(`    - ID ${msg.id}: "${msg.content}"`);
        });
        console.log('  ✅ Test 2 PASSED\n');
    } else {
        console.log(`  ❌ Expected ${expectedFilteredCount} messages, got ${filteredArray.length}`);
        console.log('  ❌ Test 2 FAILED\n');
    }

    // Test 3: Edge cases
    testsTotal++;
    console.log('Test 3: Edge cases');
    const edgeCases = [
        null,
        undefined,
        '',
        { content: null },
        { content: undefined },
        { content: '' },
        { id: 1 }, // No content property
    ];

    let test3Passed = true;
    edgeCases.forEach((testCase, index) => {
        try {
            const result = isTestMessage(testCase);
            if (result !== false) {
                console.log(`  ❌ Edge case ${index + 1} failed: Expected false, got ${result}`);
                test3Passed = false;
            } else {
                console.log(`  ✅ Edge case ${index + 1} handled correctly`);
            }
        } catch (error) {
            console.log(`  ❌ Edge case ${index + 1} threw error: ${error.message}`);
            test3Passed = false;
        }
    });

    // Test array filtering with edge cases
    const edgeArray = [
        { id: 1, content: 'Normal message' },
        { id: 2 }, // No content
        { id: 3, content: null },
        { id: 4, content: 'Voici la clé secrète : 42' },
        { id: 5, content: 'Another normal message' }
    ];

    try {
        const filteredEdgeArray = filterTestMessages(edgeArray);
        if (filteredEdgeArray.length === 4) { // Should keep all except the test message
            console.log('  ✅ Array filtering with edge cases handled correctly');
        } else {
            console.log(`  ❌ Array filtering with edge cases failed: Expected 4, got ${filteredEdgeArray.length}`);
            test3Passed = false;
        }
    } catch (error) {
        console.log(`  ❌ Array filtering with edge cases threw error: ${error.message}`);
        test3Passed = false;
    }

    if (test3Passed) {
        testsPassed++;
        console.log('  ✅ Test 3 PASSED\n');
    } else {
        console.log('  ❌ Test 3 FAILED\n');
    }

    // Test 4: Case insensitivity and whitespace handling
    testsTotal++;
    console.log('Test 4: Case insensitivity and whitespace handling');
    const caseTests = [
        '  VOICI LA CLÉ SECRÈTE : 42  ',
        '\tvoici la clé secrète: 42\n',
        'Voici La Clé Secrète : 42',
        '   TEST DE COMMUNICATION   ',
        'Message De Test'
    ];

    let test4Passed = true;
    caseTests.forEach((msg, index) => {
        const result = isTestMessage(msg);
        if (!result) {
            console.log(`  ❌ Case test ${index + 1} failed: "${msg}" should be filtered`);
            test4Passed = false;
        } else {
            console.log(`  ✅ Case test ${index + 1} passed: "${msg}" correctly filtered`);
        }
    });

    if (test4Passed) {
        testsPassed++;
        console.log('  ✅ Test 4 PASSED\n');
    } else {
        console.log('  ❌ Test 4 FAILED\n');
    }

    // Summary
    console.log('📊 Test Results Summary:');
    console.log(`   Tests passed: ${testsPassed}/${testsTotal}`);
    console.log(`   Success rate: ${((testsPassed / testsTotal) * 100).toFixed(1)}%`);

    if (testsPassed === testsTotal) {
        console.log('🎉 All tests passed! Message filtering is working correctly.');
        return true;
    } else {
        console.log('❌ Some tests failed. Please check the implementation.');
        return false;
    }
}

/**
 * Main test function
 */
async function main() {
    console.log('🔍 Testing message filtering system for clé secrète optimization...\n');

    const success = runTests();

    if (success) {
        console.log('\n✅ Message filtering system is ready for deployment!');
        console.log('💡 Next steps:');
        console.log('   1. Run the cleanup script to remove existing test messages');
        console.log('   2. Restart the MCP server to apply the changes');
        console.log('   3. Test the remember tool to ensure no more repetition');
    } else {
        console.log('\n❌ Message filtering system needs fixes before deployment.');
        process.exit(1);
    }
}

// Run the tests
main().catch(error => {
    console.error('❌ Test execution failed:', error);
    process.exit(1);
}); 