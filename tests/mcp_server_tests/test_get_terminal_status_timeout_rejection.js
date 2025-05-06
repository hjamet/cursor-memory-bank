import assert from 'assert';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import { fileURLToPath } from 'url';

// ES module equivalent for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
    console.log('[Test] Starting test_get_terminal_status_timeout_rejection.js...');
    // Server is at .cursor/mcp/mcp-commit-server/server.js
    // Test is at tests/mcp_server_tests/
    const serverDir = path.resolve(__dirname, '../../.cursor/mcp/mcp-commit-server');
    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'], // server.js is directly in serverDir
        cwd: serverDir
    });
    const client = new McpClient({ name: "TestClient", version: "0.0.1" });

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        // const toolName = 'InternalAsyncTerminal'; // Server name, not used directly

        const toolParams = {
            timeout: 301 // Exceeds the 300-second limit
        };
        console.log(`[Test] Calling tool 'get_terminal_status' with params:`, toolParams);

        const result = await client.callTool({
            name: 'get_terminal_status',
            arguments: toolParams
        });
        console.log('[Test] Result from callTool("get_terminal_status"):', JSON.stringify(result, null, 2));

        assert(result.content && result.content[0] && typeof result.content[0].text === 'string', 'Result content text is missing or not a string');
        const response = JSON.parse(result.content[0].text);

        assert(response.error && response.error.includes('Timeout cannot exceed 300 seconds'), 'Expected error message for timeout > 300');
        assert.strictEqual(response.status_changed, false, 'Expected status_changed to be false on error');
        assert(Array.isArray(response.terminals) && response.terminals.length === 0, 'Expected terminals array to be empty on error');

        console.log('[Test] test_get_terminal_status_timeout_rejection.js PASSED');
    } catch (error) {
        console.error('[Test] test_get_terminal_status_timeout_rejection.js FAILED:', error);
        process.exit(1);
    } finally {
        if (client.isConnected) {
            await client.disconnect();
        }
        console.log('[Test] Disconnected from MCP server.');
    }
}

main(); 