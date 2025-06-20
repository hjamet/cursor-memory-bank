#!/usr/bin/env node

/**
 * Test script to validate remember and next_rule MCP tools
 * Tests that the tools accept their real parameters AND return correct responses
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the MCP server
const serverPath = path.join(__dirname, '.cursor', 'mcp', 'memory-bank-mcp', 'server.js');

console.log('🧪 Testing remember and next_rule MCP tools (full validation)...\n');

/**
 * Send a tool request to the MCP server and return the parsed response
 */
async function sendToolRequest(toolName, params) {
    return new Promise((resolve, reject) => {
        const server = spawn('node', [serverPath], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: __dirname
        });

        let stdout = '';
        let stderr = '';

        server.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        server.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        server.on('close', (code) => {
            try {
                // Parse JSON-RPC responses from stdout
                const lines = stdout.split('\n').filter(line => line.trim());
                let toolResponse = null;

                for (const line of lines) {
                    try {
                        const response = JSON.parse(line);
                        if (response.id === 2) { // Tool call response
                            toolResponse = response;
                            break;
                        }
                    } catch (e) {
                        // Skip non-JSON lines
                    }
                }

                if (!toolResponse) {
                    reject(new Error(`No valid tool response found. stdout: ${stdout}, stderr: ${stderr}`));
                    return;
                }

                if (toolResponse.error) {
                    reject(new Error(`Tool error: ${JSON.stringify(toolResponse.error)}`));
                    return;
                }

                // Return the result directly (not wrapped in content/text)
                resolve(toolResponse.result);
            } catch (error) {
                reject(new Error(`Failed to parse response: ${error.message}. stdout: ${stdout}`));
            }
        });

        server.on('error', (error) => {
            reject(error);
        });

        // Send initialization request
        const initRequest = {
            jsonrpc: "2.0",
            id: 1,
            method: "initialize",
            params: {
                protocolVersion: "2024-11-05",
                capabilities: {},
                clientInfo: {
                    name: "test-client",
                    version: "1.0.0"
                }
            }
        };

        // Send tool request
        const toolRequest = {
            jsonrpc: "2.0",
            id: 2,
            method: "tools/call",
            params: {
                name: toolName,
                arguments: params
            }
        };

        // Send both requests
        server.stdin.write(JSON.stringify(initRequest) + '\n');
        server.stdin.write(JSON.stringify(toolRequest) + '\n');
        server.stdin.end();

        // Auto-close after timeout
        setTimeout(() => {
            server.kill();
            reject(new Error('Test timeout'));
        }, 10000);
    });
}

/**
 * Test the remember tool with real parameters and validate response
 */
async function testRememberTool() {
    console.log('🔍 Testing remember tool...');

    try {
        const params = {
            past: "Test past state - identified MCP schema issue",
            present: "Test present state - fixed z.object() to plain object",
            future: "Test future state - validate tools work correctly",
            long_term_memory: "MCP schema format: use plain objects, not z.object()"
        };

        const result = await sendToolRequest('remember', params);

        // Validate response structure - result is directly the tool response
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid response structure - expected object');
        }

        // Validate response content
        const expectedFields = ['message', 'current_state', 'possible_next_rules', 'long_term_memory', 'recent_memories'];
        const missingFields = expectedFields.filter(field => !(field in result));

        if (missingFields.length > 0) {
            throw new Error(`Missing response fields: ${missingFields.join(', ')}`);
        }

        // Validate specific content
        if (!result.message.includes('successfully recorded')) {
            throw new Error('Success message not found in response');
        }

        if (result.current_state !== params.future) {
            throw new Error(`Current state mismatch. Expected: "${params.future}", Got: "${result.current_state}"`);
        }

        if (result.long_term_memory !== params.long_term_memory) {
            throw new Error(`Long term memory mismatch. Expected: "${params.long_term_memory}", Got: "${result.long_term_memory}"`);
        }

        // Validate recent_memories is an array
        if (!Array.isArray(result.recent_memories)) {
            throw new Error('recent_memories should be an array');
        }

        // Check if the last memory entry matches our input
        const lastMemory = result.recent_memories[result.recent_memories.length - 1];
        if (!lastMemory || lastMemory.past !== params.past || lastMemory.present !== params.present || lastMemory.future !== params.future) {
            throw new Error('Last memory entry does not match input parameters');
        }

        console.log('✅ remember tool test PASSED');
        console.log('   Parameters accepted:', Object.keys(params).join(', '));
        console.log('   Response structure: Valid');
        console.log('   Memory persistence: Working');
        console.log('   Long-term memory: Stored correctly');
        console.log('   Recent memories count:', result.recent_memories.length);
        return true;
    } catch (error) {
        console.log('❌ remember tool test FAILED');
        console.log('   Error:', error.message);
        return false;
    }
}

/**
 * Test the next_rule tool with real parameters and validate response
 */
async function testNextRuleTool() {
    console.log('🔍 Testing next_rule tool...');

    try {
        const params = {
            rule_name: "system"
        };

        const result = await sendToolRequest('next_rule', params);

        // Validate response structure - result is directly the tool response
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid response structure - expected object');
        }

        // Validate response content
        if (!result.rule_name || !result.instructions) {
            throw new Error('Missing required fields: rule_name or instructions');
        }

        if (result.rule_name !== params.rule_name) {
            throw new Error(`Rule name mismatch. Expected: "${params.rule_name}", Got: "${result.rule_name}"`);
        }

        // Validate that instructions contain expected content for system rule
        const instructions = result.instructions;
        if (typeof instructions !== 'string') {
            throw new Error('Instructions should be a string');
        }

        const expectedContent = ['TLDR', 'Instructions', 'Specifics', 'Next Rules'];
        const missingContent = expectedContent.filter(content => !instructions.includes(content));

        if (missingContent.length > 0) {
            throw new Error(`System rule missing expected sections: ${missingContent.join(', ')}`);
        }

        // Check if the rule mentions Memory Bank (specific to system rule)
        if (!instructions.includes('Memory Bank')) {
            throw new Error('System rule should mention Memory Bank');
        }

        // Check if it mentions autonomous execution
        if (!instructions.includes('AUTONOMOUS EXECUTION')) {
            throw new Error('System rule should mention autonomous execution');
        }

        console.log('✅ next_rule tool test PASSED');
        console.log('   Parameters accepted:', Object.keys(params).join(', '));
        console.log('   Response structure: Valid');
        console.log('   Rule content: Complete system rule loaded');
        console.log('   Content length:', instructions.length, 'characters');
        console.log('   Contains expected sections: Yes');
        return true;
    } catch (error) {
        console.log('❌ next_rule tool test FAILED');
        console.log('   Error:', error.message);
        return false;
    }
}

/**
 * Test edge cases and error handling
 */
async function testEdgeCases() {
    console.log('🔍 Testing edge cases...');

    let passed = 0;
    let total = 0;

    // Test next_rule with non-existent rule
    total++;
    try {
        await sendToolRequest('next_rule', { rule_name: 'non_existent_rule' });
        console.log('   ⚠️  next_rule should have failed with non-existent rule');
    } catch (error) {
        if (error.message.includes('not found')) {
            console.log('   ✅ next_rule correctly handles non-existent rule');
            passed++;
        } else {
            console.log('   ❌ next_rule failed with unexpected error:', error.message);
        }
    }

    // Test remember with minimal parameters (no long_term_memory)
    total++;
    try {
        const result = await sendToolRequest('remember', {
            past: 'Minimal test past',
            present: 'Minimal test present',
            future: 'Minimal test future'
        });

        // Validate that it works without long_term_memory
        if (result && result.message && result.message.includes('successfully recorded')) {
            console.log('   ✅ remember works with minimal parameters');
            passed++;
        } else {
            console.log('   ❌ remember with minimal parameters returned unexpected result');
        }
    } catch (error) {
        console.log('   ❌ remember failed with minimal parameters:', error.message);
    }

    return { passed, total };
}

/**
 * Run all tests
 */
async function runTests() {
    console.log('🚀 Starting comprehensive MCP tool validation...\n');

    const results = [];

    // Test remember tool
    results.push(await testRememberTool());
    console.log('');

    // Test next_rule tool
    results.push(await testNextRuleTool());
    console.log('');

    // Test edge cases
    const edgeResults = await testEdgeCases();
    console.log('');

    // Summary
    const mainPassed = results.filter(r => r).length;
    const mainTotal = results.length;
    const totalPassed = mainPassed + edgeResults.passed;
    const totalTests = mainTotal + edgeResults.total;

    console.log('📊 Comprehensive Test Results:');
    console.log(`   Core functionality: ${mainPassed}/${mainTotal}`);
    console.log(`   Edge cases: ${edgeResults.passed}/${edgeResults.total}`);
    console.log(`   Overall: ${totalPassed}/${totalTests}`);

    if (totalPassed === totalTests) {
        console.log('🎉 ALL TESTS PASSED! Tools are fully functional.');
        console.log('   ✅ Parameter acceptance');
        console.log('   ✅ Response structure');
        console.log('   ✅ Business logic');
        console.log('   ✅ Error handling');
        process.exit(0);
    } else {
        console.log('💥 Some tests failed. Issues detected.');
        process.exit(1);
    }
}

// Run the tests
runTests().catch(error => {
    console.error('💥 Test runner failed:', error.message);
    process.exit(1);
}); 