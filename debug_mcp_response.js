#!/usr/bin/env node

/**
 * Debug script to see exactly what the MCP tools return
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the MCP server
const serverPath = path.join(__dirname, '.cursor', 'mcp', 'memory-bank-mcp', 'server.js');

console.log('🔍 Debugging MCP tool responses...\n');

/**
 * Send a tool request and capture raw output
 */
async function debugToolRequest(toolName, params) {
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
            resolve({ stdout, stderr, code });
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
                    name: "debug-client",
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

        console.log(`📤 Sending ${toolName} request:`, JSON.stringify(params, null, 2));

        // Send both requests
        server.stdin.write(JSON.stringify(initRequest) + '\n');
        server.stdin.write(JSON.stringify(toolRequest) + '\n');
        server.stdin.end();

        // Auto-close after timeout
        setTimeout(() => {
            server.kill();
            resolve({ stdout, stderr, code: 'TIMEOUT' });
        }, 5000);
    });
}

async function debugRemember() {
    console.log('=== DEBUGGING REMEMBER TOOL ===');

    const params = {
        past: "Debug past",
        present: "Debug present",
        future: "Debug future"
    };

    const result = await debugToolRequest('remember', params);

    console.log('📥 Raw stdout:');
    console.log(result.stdout);
    console.log('\n📥 Raw stderr:');
    console.log(result.stderr);
    console.log('\n📥 Exit code:', result.code);

    // Try to parse JSON responses
    console.log('\n🔍 Parsing JSON responses:');
    const lines = result.stdout.split('\n').filter(line => line.trim());
    lines.forEach((line, index) => {
        try {
            const parsed = JSON.parse(line);
            console.log(`Line ${index + 1}:`, JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log(`Line ${index + 1} (not JSON):`, line);
        }
    });
}

async function debugNextRule() {
    console.log('\n=== DEBUGGING NEXT_RULE TOOL ===');

    const params = {
        rule_name: "system"
    };

    const result = await debugToolRequest('next_rule', params);

    console.log('📥 Raw stdout:');
    console.log(result.stdout);
    console.log('\n📥 Raw stderr:');
    console.log(result.stderr);
    console.log('\n📥 Exit code:', result.code);

    // Try to parse JSON responses
    console.log('\n🔍 Parsing JSON responses:');
    const lines = result.stdout.split('\n').filter(line => line.trim());
    lines.forEach((line, index) => {
        try {
            const parsed = JSON.parse(line);
            console.log(`Line ${index + 1}:`, JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log(`Line ${index + 1} (not JSON):`, line);
        }
    });
}

// Run debug
async function runDebug() {
    try {
        await debugRemember();
        await debugNextRule();
    } catch (error) {
        console.error('Debug failed:', error);
    }
}

runDebug(); 