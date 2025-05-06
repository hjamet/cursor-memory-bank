import assert from 'assert';
import { McpClient, StdioClientTransport } from '@modelcontextprotocol/sdk';

async function main() {
    console.log('[Test] Starting test_get_terminal_status_timeout_rejection.js...');
    const transport = new StdioClientTransport({ command: 'node', args: ['../server.js'] });
    const client = new McpClient({ transport });

    try {
        await client.connect();
        console.log('[Test] Connected to MCP server.');

        const toolName = 'InternalAsyncTerminal'; // Make sure this matches server name

        // Attempt to get terminal status with a timeout greater than 300 seconds
        const params = {
            timeout: 301 // Exceeds the 300-second limit
        };
        console.log(`[Test] Calling get_terminal_status on ${toolName} with params:`, params);

        const result = await client.tool(toolName, 'get_terminal_status', params);
        console.log('[Test] Result from get_terminal_status:', JSON.stringify(result, null, 2));

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
        await client.disconnect();
        console.log('[Test] Disconnected from MCP server.');
    }
}

main(); 