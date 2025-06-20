import rememberTool from './.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js';
import { promises as fs } from 'fs';
import path from 'path';
import assert from 'assert';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const memoryFilePath = path.join(__dirname, '.cursor', 'memory-bank', 'workflow', 'agent_memory.json');

async function cleanup() {
    try {
        await fs.unlink(memoryFilePath);
    } catch (error) {
        if (error.code !== 'ENOENT') {
            console.error('Error cleaning up memory file:', error);
        }
    }
}

async function runTest(name, testFn) {
    console.log(`\n--- Running test: ${name} ---`);
    let success = false;
    try {
        await cleanup();
        await testFn();
        success = true;
        console.log(`✅ Test PASSED: ${name}`);
    } catch (error) {
        console.error(`❌ Test FAILED: ${name}`);
        console.error(error);
        process.exit(1);
    }
    return success;
}

async function test_initialMemoryCreation() {
    const args = {
        past: "Initial plan",
        present: "Initial execution",
        future: "Next step"
    };
    const result = await rememberTool.run(args);

    assert.strictEqual(result.message, "Memory successfully recorded.");
    assert.strictEqual(result.recent_memories.length, 1);
    assert.strictEqual(result.recent_memories[0].past, "Initial plan");

    const data = await fs.readFile(memoryFilePath, 'utf8');
    const memories = JSON.parse(data);
    assert.strictEqual(memories.length, 1);
    assert.strictEqual(memories[0].future, "Next step");
}

async function test_addMultipleMemories() {
    for (let i = 0; i < 5; i++) {
        await rememberTool.run({
            past: `Plan ${i}`,
            present: `Execution ${i}`,
            future: `Next ${i}`
        });
    }

    const data = await fs.readFile(memoryFilePath, 'utf8');
    const memories = JSON.parse(data);
    assert.strictEqual(memories.length, 5);
    assert.strictEqual(memories[4].past, "Plan 4");

    const result = await rememberTool.run({ past: "final", present: "final", future: "final" });
    assert.strictEqual(result.recent_memories.length, 6);
}

async function test_memoryCapping() {
    for (let i = 0; i < 105; i++) {
        await rememberTool.run({
            past: `Plan ${i}`,
            present: `Execution ${i}`,
            future: `Next ${i}`
        });
    }

    const data = await fs.readFile(memoryFilePath, 'utf8');
    const memories = JSON.parse(data);
    assert.strictEqual(memories.length, 100);
    assert.strictEqual(memories[0].past, "Plan 5");
    assert.strictEqual(memories[99].past, "Plan 104");
}

async function test_returnLast15Memories() {
    for (let i = 0; i < 20; i++) {
        await rememberTool.run({
            past: `Plan ${i}`,
            present: `Execution ${i}`,
            future: `Next ${i}`
        });
    }

    const result = await rememberTool.run({ past: "last one", present: "final", future: "final" });
    assert.strictEqual(result.recent_memories.length, 15);
    // The 21st memory is added, total is 21. The last 15 are returned.
    // The first memory in recent_memories should be item index 6 (21 - 15)
    assert.strictEqual(result.recent_memories[0].past, "Plan 6");
    assert.strictEqual(result.recent_memories[14].past, "last one");
}


async function main() {
    await runTest("Initial memory creation", test_initialMemoryCreation);
    await runTest("Add multiple memories", test_addMultipleMemories);
    await runTest("Memory capping at 100", test_memoryCapping);
    await runTest("Return last 15 memories", test_returnLast15Memories);

    console.log("\n--- All tests passed! ---");
    await cleanup();
}

main().catch(err => {
    console.error("A critical error occurred in the test runner:", err);
    process.exit(1);
}); 