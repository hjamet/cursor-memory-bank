import { regexEditTool } from '../mcp_tools/regex_edit.js';
import fs from 'fs/promises';
import path from 'path';

async function testRegexEdit() {
    const testFile = path.join(process.cwd(), 'test_regex_edit.txt');
    const testContent = `Line 1: Hello World
Line 2: This is a test
Line 3: Replace this line
Line 4: End of file`;

    try {
        // Create test file
        await fs.writeFile(testFile, testContent, 'utf8');
        console.log('Test file created.');

        // Test the regex_edit tool
        const result = await regexEditTool.run({
            file_path: testFile,
            regex_pattern: 'Replace this line',
            replacement_text: 'This line was replaced successfully'
        });

        console.log('Tool result:', result);

        if (result.success) {
            // Verify the file was updated correctly
            const updatedContent = await fs.readFile(testFile, 'utf8');
            const expectedContent = testContent.replace('Replace this line', 'This line was replaced successfully');

            if (updatedContent === expectedContent) {
                console.log('Test PASSED! File was updated correctly.');
            } else {
                console.error('Test FAILED: File content mismatch.');
                console.error('Expected:', expectedContent);
                console.error('Got:', updatedContent);
            }
        } else {
            console.error('Test FAILED: Tool reported failure:', result.error);
        }

        // Clean up
        await fs.unlink(testFile);
        console.log('Test file cleaned up.');

    } catch (error) {
        console.error('Test error:', error);
    }
}

// Run test if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    testRegexEdit();
}

export { testRegexEdit }; 