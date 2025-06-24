import { regexEditTool } from '../mcp_tools/regex_edit.js';
const handleRegexEdit = regexEditTool.run;
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function testRegexEdit() {
    const testFilePath = path.join(__dirname, 'test_file.txt');
    const originalContent = "Hello world! This is a test.";
    const pattern = "world";
    const replacement = "universe";
    const expectedContent = "Hello universe! This is a test.";

    // 1. Create a test file
    await fs.writeFile(testFilePath, originalContent, 'utf8');
    console.log('Test file created.');

    // 2. Run the regex_edit tool
    const result = await handleRegexEdit({
        file_path: testFilePath,
        regex_pattern: pattern,
        replacement_text: replacement,
    });

    console.log('Tool result:', result);

    // 3. Verify the result
    if (!result.success) {
        console.error('Test FAILED: Tool reported failure.');
        return;
    }

    const updatedContent = await fs.readFile(testFilePath, 'utf8');

    if (updatedContent !== expectedContent) {
        console.error(`Test FAILED: Content mismatch.`);
        console.error(`Expected: "${expectedContent}"`);
        console.error(`Got:      "${updatedContent}"`);
    } else {
        console.log('Test PASSED!');
    }

    // 4. Clean up the test file
    await fs.unlink(testFilePath);
    console.log('Test file cleaned up.');
}

testRegexEdit(); 