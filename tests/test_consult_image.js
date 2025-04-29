import assert from 'assert';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs/promises';
import { handleConsultImage } from '../.cursor/mcp/mcp-commit-server/mcp_tools/consult_image.js';

// Helper to get __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Calculate project root (assuming test script is in tests/)
// const projectRootForTest = path.resolve(__dirname, '..'); // REMOVED

// Basic test suite
async function runTests() {
    console.log('Running consult_image tests...');

    // Test Case 1: Unsupported File Type
    console.log('  Testing unsupported file type...');
    const testPathTxt = 'tests/dummy_file.txt'; // Relative path from project root
    try {
        const result = await handleConsultImage({ path: testPathTxt });
        assert.strictEqual(typeof result, 'object', 'Test Failed: Result should be an object');
        assert.ok(Array.isArray(result.content), 'Test Failed: result.content should be an array');
        assert.strictEqual(result.content.length, 1, 'Test Failed: Result content array should have one element');
        assert.strictEqual(result.content[0].type, 'text', 'Test Failed: Result type should be text for unsupported file');
        assert.ok(result.content[0].text.includes('Unsupported file type'), 'Test Failed: Error message should mention unsupported type');
        console.log(`    PASS: Correctly handled unsupported file type (${testPathTxt})`);
    } catch (error) {
        console.error(`    FAIL: Unexpected error during unsupported file type test:`, error);
        process.exitCode = 1; // Indicate test failure
    }

    // Test Case 2: Success Case (PNG)
    console.log('  Testing success case (PNG image)...');
    const testPathPng = 'tests/assets/image.png'; // Relative path from project root
    const actualImagePath = path.resolve(__dirname, '..', testPathPng); // Path for fs.readFile
    try {
        const result = await handleConsultImage({ path: testPathPng });
        // REMOVED: Reading original file and comparing base64 is no longer valid
        // const expectedBuffer = await fs.readFile(actualImagePath);
        // const expectedBase64 = expectedBuffer.toString('base64');

        assert.strictEqual(typeof result, 'object', 'Test Success PNG Failed: Result should be an object');
        assert.ok(Array.isArray(result.content), 'Test Success PNG Failed: result.content should be an array');
        assert.strictEqual(result.content.length, 1, 'Test Success PNG Failed: Result content array should have one element');
        const imageResult = result.content[0]; // Easier access
        assert.strictEqual(imageResult.type, 'image', 'Test Success PNG Failed: Result type should be image');
        // UPDATED: Expect image/jpeg due to server-side conversion
        assert.strictEqual(imageResult.mimeType, 'image/jpeg', 'Test Success PNG Failed: MimeType should be image/jpeg');
        // REMOVED: Base64 comparison is removed as output is processed
        // assert.strictEqual(imageResult.data, expectedBase64, 'Test Success PNG Failed: Base64 data mismatch');
        // ADDED: Check that base64 data exists and is a non-empty string
        assert.ok(typeof imageResult.data === 'string' && imageResult.data.length > 0, 'Test Success PNG Failed: Base64 data should be a non-empty string');
        console.log(`    PASS: Correctly handled PNG image (${testPathPng})`);
    } catch (error) {
        console.error(`    FAIL: Unexpected error during success PNG test:`, error);
        process.exitCode = 1; // Indicate test failure
    }

    console.log('Finished consult_image tests.');
}

runTests().catch(err => {
    console.error("Critical error running tests:", err);
    process.exitCode = 1;
}); 