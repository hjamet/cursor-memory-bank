import { replaceContentBetweenTool } from './.cursor/mcp/mcp-commit-server/mcp_tools/replace_content_between.js';
import { promises as fs } from 'fs';

async function testReplaceContentBetween() {
    const testFile = 'test_file_temp.txt';
    const testContent = `Line 1: Start
<!-- START_MARKER -->
Old content to replace
<!-- END_MARKER -->
Line 4: End`;

    try {
        // Create test file
        await fs.writeFile(testFile, testContent, 'utf8');
        console.log('✅ Test file created');

        // Test the tool
        const result = await replaceContentBetweenTool.func({
            target_file: testFile,
            start_marker: '<!-- START_MARKER -->',
            end_marker: '<!-- END_MARKER -->',
            replacement_content: 'New content successfully replaced!'
        });

        console.log('🔧 Tool result:', result);

        // Verify file was updated
        const updatedContent = await fs.readFile(testFile, 'utf8');
        console.log('📄 Updated file content:');
        console.log(updatedContent);

        // Check if the replacement worked
        if (updatedContent.includes('New content successfully replaced!')) {
            console.log('✅ TEST PASSED: Content was replaced successfully!');
        } else {
            console.log('❌ TEST FAILED: Content was not replaced');
        }

        // Clean up
        await fs.unlink(testFile);
        console.log('🧹 Test file cleaned up');

    } catch (error) {
        console.error('❌ Test error:', error);
        // Try to clean up even if test failed
        try {
            await fs.unlink(testFile);
        } catch (cleanupError) {
            // Ignore cleanup errors
        }
    }
}

testReplaceContentBetween(); 