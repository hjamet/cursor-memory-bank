import assert from 'assert';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import { fileURLToPath } from 'url';

// ES module equivalent for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TEST_URL = 'http://httpbin.org/html'; // A simple, reliable public HTML page

async function main() {
    console.log('[Test] Starting test_take_webpage_screenshot.js...');
    const serverDir = path.resolve(__dirname, '../../.cursor/mcp/mcp-commit-server');
    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'],
        cwd: serverDir
    });
    const client = new McpClient({ name: "TestClientWebpageScreenshot", version: "0.0.1" });

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        console.log(`[Test] Calling take_webpage_screenshot with URL: ${TEST_URL}`);
        const result = await client.callTool({
            name: 'take_webpage_screenshot',
            arguments: { url: TEST_URL }
        });
        console.log('[Test] Result from take_webpage_screenshot:', JSON.stringify(result, null, 2));

        assert(result, 'Result from callTool should not be null');
        assert(result.content, 'Result should have a "content" field');
        assert(Array.isArray(result.content), 'result.content should be an array');
        assert.strictEqual(result.content.length, 1, 'result.content should have one element');

        const imageResult = result.content[0];
        assert.strictEqual(imageResult.type, 'image', 'Type of the result should be "image"');
        assert(imageResult.data, 'Image result should have a "data" field');
        assert.strictEqual(typeof imageResult.data, 'string', 'imageResult.data should be a string');
        assert(imageResult.data.length > 0, 'imageResult.data (base64 string) should not be empty');
        assert.strictEqual(imageResult.mimeType, 'image/png', 'MimeType should be "image/png"');

        console.log('[Test] Verified screenshot data structure successfully.');
        console.log('[Test] test_take_webpage_screenshot.js PASSED');

    } catch (error) {
        console.error('[Test] test_take_webpage_screenshot.js FAILED:', error);
        process.exit(1);
    } finally {
        if (client.isConnected) {
            await client.disconnect();
        }
        console.log('[Test] Disconnected from MCP server.');
    }
}

main(); 