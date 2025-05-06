import assert from 'assert';
// Explicitly target index.js for ESM import and StdioClientTransport from stdio.js
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path'; // Keep path for potential future use if needed, but cwd logic changing

async function main() {
    console.log('[Test] Starting test_execute_command_timeout_rejection.js...');
    // Assuming the test is run from .cursor/mcp/mcp-commit-server directory,
    // process.cwd() will be the server's directory.
    // server.js is directly in that CWD.
    const serverDir = process.cwd(); // This should be .cursor/mcp/mcp-commit-server
    const serverScriptPath = path.join(serverDir, 'server.js');

    // console.log(`[Test] Server script path for StdioClientTransport: ${serverScriptPath}`);
    // console.log(`[Test] CWD for StdioClientTransport: ${serverDir}`);

    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'], // server.js should be directly in the CWD
        cwd: serverDir // Set CWD to the server's directory
    });

    const client = new McpClient({ name: "TestClient", version: "0.0.1" });

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        // Attempt a minimal call first to see if the base command works
        const minimalParams = { command: 'echo MinimalCall' };
        console.log(`[Test] Calling tool 'execute_command' with minimal params:`, minimalParams);
        const minimalResult = await client.callTool({
            name: 'execute_command',
            arguments: minimalParams
        });
        console.log('[Test] Result from minimal callTool("execute_command"):', JSON.stringify(minimalResult, null, 2));
        const minimalResponse = JSON.parse(minimalResult.content[0].text);
        // Basic assertion for the minimal call - should succeed or be 'Running' if timeout is default 10s
        assert(minimalResponse.status === 'Success' || minimalResponse.status === 'Running', 'Minimal call failed unexpectedly: ' + minimalResponse.stderr);
        console.log('[Test] Minimal call to execute_command seems okay.');

        // Now test the timeout rejection
        const timeoutRejectParams = {
            command: 'echo HelloTimeout',
            timeout: 301
        };
        console.log(`[Test] Calling tool 'execute_command' with timeout rejection params:`, timeoutRejectParams);

        const timeoutRejectResult = await client.callTool({
            name: 'execute_command',
            arguments: timeoutRejectParams
        });
        console.log('[Test] Result from timeout rejection callTool("execute_command"):', JSON.stringify(timeoutRejectResult, null, 2));

        assert(timeoutRejectResult.content && timeoutRejectResult.content[0] && typeof timeoutRejectResult.content[0].text === 'string', 'Result content text is missing or not a string for timeout rejection call');
        const timeoutRejectResponse = JSON.parse(timeoutRejectResult.content[0].text);

        assert.strictEqual(timeoutRejectResponse.status, 'Failure', 'Expected status to be Failure for timeout > 300');
        assert(timeoutRejectResponse.stderr && timeoutRejectResponse.stderr.includes('Timeout cannot exceed 300 seconds'), 'Expected stderr to contain timeout error message for timeout > 300');

        console.log('[Test] test_execute_command_timeout_rejection.js PASSED');
    } catch (error) {
        console.error('[Test] test_execute_command_timeout_rejection.js FAILED:', error);
        process.exit(1);
    } finally {
        if (client.isConnected) {
            await client.disconnect();
        }
        console.log('[Test] Disconnected from MCP server.');
    }
}

main(); 