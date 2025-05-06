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

        // const toolName = 'InternalAsyncTerminal'; // Server name, not used directly in callTool like this

        const toolParams = {
            command: 'echo Hello',
            timeout: 301
        };
        console.log(`[Test] Calling tool 'execute_command' with params:`, toolParams);

        // Corrected: Use client.callTool with structured parameters
        const result = await client.callTool({
            toolID: 'execute_command', // The specific tool to call
            params: toolParams         // Parameters for the 'execute_command' tool itself
        });
        console.log('[Test] Result from callTool("execute_command"):', JSON.stringify(result, null, 2));

        assert(result.content && result.content[0] && typeof result.content[0].text === 'string', 'Result content text is missing or not a string');
        const response = JSON.parse(result.content[0].text);

        assert.strictEqual(response.status, 'Failure', 'Expected status to be Failure for timeout > 300');
        assert(response.stderr && response.stderr.includes('Timeout cannot exceed 300 seconds'), 'Expected stderr to contain timeout error message');

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