import assert from 'assert';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Mock functions from userbrief_manager and tool handlers
import { readUserbriefData, writeUserbriefData, addUserbriefRequest } from '../.cursor/mcp/memory-bank-mcp/lib/userbrief_manager.js';
import { handleReadUserbrief } from '../.cursor/mcp/memory-bank-mcp/mcp_tools/read_userbrief.js';
import { handleUpdateUserbrief } from '../.cursor/mcp/memory-bank-mcp/mcp_tools/update_userbrief.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const USERBRIEF_PATH = path.resolve(__dirname, '../.cursor/memory-bank/workflow/userbrief.json');

const defaultUserbrief = {
    version: "1.0.0",
    last_id: 0,
    requests: []
};

// Helper function to reset userbrief.json before each test
function resetUserbrief() {
    fs.writeFileSync(USERBRIEF_PATH, JSON.stringify(defaultUserbrief, null, 2), 'utf-8');
}

async function runTest(name, testFn) {
    try {
        resetUserbrief();
        console.log(`\nRunning test: ${name}...`);
        await testFn();
        console.log(`✅ Test passed: ${name}`);
    } catch (error) {
        console.error(`❌ Test failed: ${name}`);
        console.error(error);
        process.exit(1); // Exit with error code if a test fails
    }
}

async function main() {
    await runTest('Add a new request and read it', async () => {
        // 1. Add a request
        const content = "This is a test request.";
        const newRequest = addUserbriefRequest(content);
        assert.strictEqual(newRequest.id, 1);
        assert.strictEqual(newRequest.content, content);
        assert.strictEqual(newRequest.status, 'new');

        // 2. Read the userbrief
        const readResult = await handleReadUserbrief({});
        const response = JSON.parse(readResult.content[0].text);

        assert.strictEqual(response.status, 'active');
        assert.ok(response.current_request, 'Current request should not be null');
        assert.strictEqual(response.current_request.id, 1);
        assert.strictEqual(response.current_request.content, content);
    });

    await runTest('Mark a request as in_progress', async () => {
        addUserbriefRequest("Test request to be marked in progress.");

        // 1. Mark as in_progress (auto-detect)
        const updateResult = await handleUpdateUserbrief({ action: 'mark_in_progress' });
        const updateResponse = JSON.parse(updateResult.content[0].text);

        assert.strictEqual(updateResponse.status, 'success');
        assert.strictEqual(updateResponse.action_performed.target_request.id, 1);
        assert.strictEqual(updateResponse.action_performed.target_request.new_status, 'in_progress');

        // 2. Verify the change
        const data = readUserbriefData();
        assert.strictEqual(data.requests[0].status, 'in_progress');
    });

    await runTest('Add a comment to a request', async () => {
        addUserbriefRequest("Test request for adding a comment.");

        // Add a comment using the ID
        const comment = "This is a test comment.";
        const updateResult = await handleUpdateUserbrief({ id: 1, action: 'add_comment', comment: comment });
        const updateResponse = JSON.parse(updateResult.content[0].text);

        assert.strictEqual(updateResponse.status, 'success');

        // Verify the comment was added
        const data = readUserbriefData();
        assert.strictEqual(data.requests[0].history.length, 1);
        assert.strictEqual(data.requests[0].history[0].action, 'add_comment');
        assert.strictEqual(data.requests[0].history[0].comment, comment);
    });

    await runTest('Archive a request', async () => {
        addUserbriefRequest("Test request to be archived.");

        // Archive the request using its ID
        const archiveComment = "Archiving this request now.";
        const updateResult = await handleUpdateUserbrief({ id: 1, action: 'mark_archived', comment: archiveComment });
        const updateResponse = JSON.parse(updateResult.content[0].text);

        assert.strictEqual(updateResponse.status, 'success');
        assert.strictEqual(updateResponse.action_performed.target_request.new_status, 'archived');

        // Verify the change
        const data = readUserbriefData();
        assert.strictEqual(data.requests[0].status, 'archived');
        assert.strictEqual(data.requests[0].history.length, 1);
        assert.strictEqual(data.requests[0].history[0].comment, archiveComment);

        // Verify there are no active requests
        const readResult = await handleReadUserbrief({});
        const readResponse = JSON.parse(readResult.content[0].text);
        assert.strictEqual(readResponse.status, 'no_pending');
        assert.strictEqual(readResponse.current_request, null);
    });

    console.log("\nAll userbrief tests completed successfully!");
}

main().catch(err => {
    console.error("A critical error occurred in the test runner:", err);
    process.exit(1);
}); 