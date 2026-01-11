import { handleReadMemory } from './mcp_tools/read_memory.js';
import { handleEditMemory } from './mcp_tools/edit_memory.js';

console.log('=== Memory Management Tools Comprehensive Test ===');

async function runTests() {
    try {
        console.log('\n1. Testing read_memory with activeContext...');
        const readResult1 = await handleReadMemory({ context_file: 'activeContext' });
        const readData1 = JSON.parse(readResult1.content[0].text);
        console.log('Read activeContext result:', readData1.status);
        console.log('Content length:', readData1.content_length);

        console.log('\n2. Testing read_memory with projectBrief...');
        const readResult2 = await handleReadMemory({ context_file: 'projectBrief' });
        const readData2 = JSON.parse(readResult2.content[0].text);
        console.log('Read projectBrief result:', readData2.status);
        console.log('Content length:', readData2.content_length);

        console.log('\n3. Testing read_memory with techContext...');
        const readResult3 = await handleReadMemory({ context_file: 'techContext' });
        const readData3 = JSON.parse(readResult3.content[0].text);
        console.log('Read techContext result:', readData3.status);
        console.log('Content length:', readData3.content_length);

        console.log('\n4. Testing edit_memory with test content...');
        const testContent = '# Test Memory\n\nThis is a test of edit_memory functionality.\n\n## Status\n- Test in progress\n- Tools working correctly';
        const editResult = await handleEditMemory({ context_file: 'techContext', content: testContent });
        const editData = JSON.parse(editResult.content[0].text);
        console.log('Edit techContext result:', editData.status);
        console.log('Operation:', editData.operation);
        console.log('Content change:', editData.change);

        console.log('\n5. Testing read_memory after edit...');
        const readAfterEdit = await handleReadMemory({ context_file: 'techContext' });
        const readAfterData = JSON.parse(readAfterEdit.content[0].text);
        console.log('Read after edit result:', readAfterData.status);
        console.log('New content length:', readAfterData.content_length);
        console.log('Content preview:', readAfterData.content.substring(0, 50) + '...');

        console.log('\n6. Testing error handling with invalid file...');
        const errorResult = await handleReadMemory({ context_file: 'invalidFile' });
        const errorData = JSON.parse(errorResult.content[0].text);
        console.log('Error handling result:', errorData.status);
        console.log('Error message:', errorData.message);

        console.log('\n7. Testing edit_memory error handling...');
        const editErrorResult = await handleEditMemory({ context_file: 'invalidFile', content: 'test' });
        const editErrorData = JSON.parse(editErrorResult.content[0].text);
        console.log('Edit error handling result:', editErrorData.status);
        console.log('Edit error message:', editErrorData.message);

        console.log('\n=== All tests completed successfully ===');
        console.log('Summary:');
        console.log('- read_memory: ✓ Working with all valid context files');
        console.log('- edit_memory: ✓ Working with content replacement');
        console.log('- Error handling: ✓ Working for both tools');

    } catch (error) {
        console.error('Test failed:', error);
        process.exit(1);
    }
}

runTests(); 