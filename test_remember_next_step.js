#!/usr/bin/env node

/**
 * Test script to validate remember and next_step MCP tools
 * Tests that the tools accept their real parameters AND return correct responses
 */

import { spawn, fork } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import assert from 'assert';
// Note: McpClient and StdioClientTransport imports removed due to SDK export issues
// This test uses spawn to communicate directly with the MCP server via JSON-RPC
import { promises as fs } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the MCP server
const serverPath = path.join(__dirname, '.cursor', 'mcp', 'memory-bank-mcp', 'server.js');
const workflowDir = path.join(__dirname, '.cursor', 'workflow');

console.log('🧪 Testing remember and next_step MCP tools (full validation)...\n');

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
                    // Correctly reject the promise if the tool returns an error
                    reject(new Error(`Tool error: ${JSON.stringify(toolResponse.error.data || toolResponse.error.message)}`));
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
        const expectedFields = ['message', 'current_state', 'possible_next_steps', 'long_term_memory', 'recent_memories'];
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
 * Test the next_step tool with real parameters and validate response
 */
async function testNextStepTool() {
    console.log('🔍 Testing next_step tool...');

    try {
        const params = {
            step_name: "system"
        };

        const result = await sendToolRequest('next_step', params);

        // Validate response structure - result is directly the tool response
        if (!result || typeof result !== 'object') {
            throw new Error('Invalid response structure - expected object');
        }

        // Validate response content
        if (!result.step_name || !result.instructions) {
            throw new Error('Missing required fields: step_name or instructions');
        }

        if (result.step_name !== params.step_name) {
            throw new Error(`Step name mismatch. Expected: "${params.step_name}", Got: "${result.step_name}"`);
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

        // Check if the step mentions memory-bank (specific to system step)
        if (!instructions.includes('memory-bank')) {
            throw new Error('System step should mention memory-bank');
        }

        // Check if it mentions autonomous execution
        if (!instructions.includes('AUTONOMOUS EXECUTION')) {
            throw new Error('System rule should mention autonomous execution');
        }

        console.log('✅ next_step tool test PASSED');
        console.log('   Parameters accepted:', Object.keys(params).join(', '));
        console.log('   Response structure: Valid');
        console.log('   Step content: Complete system step loaded');
        console.log('   Content length:', instructions.length, 'characters');
        console.log('   Contains expected sections: Yes');
        return true;
    } catch (error) {
        console.log('❌ next_step tool test FAILED');
        console.log('   Error:', error.message);
        return false;
    }
}

/**
 * Test edge cases and error handling
 */
async function testEdgeCases() {
    console.log('\n🔍 Testing edge cases...');
    let passed = 0;
    let total = 0;

    // Test: next_step should fail with a non-existent step
    total++;
    try {
        await sendToolRequest('next_step', { step_name: 'non_existent_step_12345' });
        console.log('   ❌ next_step should have failed with non-existent step');
    } catch (error) {
        if (error.message.includes('Step file not found')) {
            console.log('   ✅ next_step correctly failed with non-existent step');
            passed++;
        } else {
            console.log('   ❌ next_step failed for an unexpected reason:', error.message);
        }
    }

    // Test: remember tool with minimal parameters (no long_term_memory)
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
    console.log('🧪 Testing remember and next_step MCP tools (full validation)...\n');
    let coreFunctionalityPassed = 0;
    const coreFunctionalityTotal = 2;

    const rememberResult = await testRememberTool();
    if (rememberResult) coreFunctionalityPassed++;

    const nextStepResult = await testNextStepTool();
    if (nextStepResult) coreFunctionalityPassed++;

    const { passed: edgeCasesPassed, total: edgeCasesTotal } = await testEdgeCases();

    const totalPassed = coreFunctionalityPassed + edgeCasesPassed;
    const totalTests = coreFunctionalityTotal + edgeCasesTotal;

    console.log('\n📊 Comprehensive Test Results:');
    console.log(`   Core functionality: ${coreFunctionalityPassed}/${coreFunctionalityTotal}`);
    console.log(`   Edge cases: ${edgeCasesPassed}/${edgeCasesTotal}`);
    console.log(`   Overall: ${totalPassed}/${totalTests}`);

    if (totalPassed < totalTests) {
        console.log('💥 Some tests failed. Issues detected.');
        process.exit(1);
    } else {
        console.log('🎉 All tests passed successfully!');
        process.exit(0);
    }
}

async function runTest() {
    console.log('Starting test: New Remember -> Next Step Workflow');

    // Ensure dummy step file exists
    const dummyStepFile = path.join(workflowDir, 'implementation.md');
    await fs.mkdir(workflowDir, { recursive: true });
    await fs.writeFile(dummyStepFile, 'This is the implementation step.');

    const serverProcess = fork(serverPath, [], { stdio: 'pipe' });

    const transport = new StdioClientTransport(serverProcess);
    const client = new McpClient({
        transport,
        // debug: true,
    });

    try {
        await client.connect();
        console.log('Client connected to server.');

        // 1. Call remember to get possible next steps
        console.log("Calling 'remember'...");
        const rememberResult = await client.tool('mcp_MemoryBank_remember', {
            past: "planning to test",
            present: "testing now",
            future: "verifying result"
        });
        console.log("'remember' result:", rememberResult);

        assert(rememberResult.possible_next_steps, "Result from 'remember' should have a 'possible_next_steps' property.");
        assert(Array.isArray(rememberResult.possible_next_steps), "'possible_next_steps' should be an array.");
        assert(rememberResult.possible_next_steps.length > 0, "'possible_next_steps' array should not be empty.");

        const nextStepName = rememberResult.possible_next_steps[0];
        console.log(`Chose '${nextStepName}' as the next step.`);

        // 2. Call next_step with the suggested step
        console.log(`Calling 'next_step' with argument: ${nextStepName}`);
        const nextStepResult = await client.tool('mcp_MemoryBank_next_step', { step_name: nextStepName });
        console.log("'next_step' result:", nextStepResult);

        assert.strictEqual(nextStepResult.step_name, nextStepName, "The returned step name should match the requested one.");
        assert(nextStepResult.instructions, "The result should include instructions for the step.");

        console.log('--- Test Suite Completed Successfully ---');
    } catch (error) {
        console.error('Test failed:', error);
        process.exit(1);
    } finally {
        await client.disconnect();
        serverProcess.kill();
        // Clean up dummy file
        await fs.unlink(dummyStepFile).catch(() => { });
    }
}

runTests(); 