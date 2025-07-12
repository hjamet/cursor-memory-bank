import { handleReadWebpage } from '../mcp_tools/read_webpage.js';

async function testReadWebpage() {
    console.log('Testing read_webpage tool...');

    // Test with a simple, reliable URL
    const testUrl = 'https://example.com';

    try {
        const result = await handleReadWebpage({ url: testUrl });

        console.log('Tool result received:', result);

        // Verify the response structure
        if (!result.content || !Array.isArray(result.content)) {
            console.error('Test FAILED: Invalid response structure');
            return false;
        }

        const content = result.content[0];
        if (!content || content.type !== 'text' || !content.text) {
            console.error('Test FAILED: Invalid content structure');
            return false;
        }

        const markdown = content.text;

        // Verify the markdown contains expected elements
        if (!markdown.includes('# Example Domain')) {
            console.error('Test FAILED: Expected title not found');
            return false;
        }

        if (!markdown.includes('Source: https://example.com')) {
            console.error('Test FAILED: Source URL not found');
            return false;
        }

        if (!markdown.includes('This domain is for use in illustrative examples')) {
            console.error('Test FAILED: Expected content not found');
            return false;
        }

        console.log('Test PASSED! read_webpage tool is working correctly.');
        console.log('Sample output:', markdown.substring(0, 200) + '...');
        return true;

    } catch (error) {
        console.error('Test FAILED with error:', error.message);
        return false;
    }
}

// Run the test
testReadWebpage().then(success => {
    console.log('\n=== Test Summary ===');
    console.log(`Status: ${success ? 'PASSED' : 'FAILED'}`);
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
}); 