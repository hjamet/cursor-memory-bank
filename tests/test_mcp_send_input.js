// tests/test_mcp_send_input.js
const { McpHttpClient } = require('@modelcontextprotocol/sdk/client/http.js');
const { v4: uuidv4 } = require('uuid');
const process = require('process');

// Configuration
const mcpServerUrl = process.env.MCP_SERVER_URL || 'http://localhost:8888'; // Get from env var or default
const client = new McpHttpClient({ serviceUrl: mcpServerUrl });

// Helper function to introduce delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runTest() {
    const testId = uuidv4().substring(0, 8);
    console.log(`[Test Start] test_mcp_send_input - ID: ${testId}`);

    let targetPid = null;
    let finalStatus = 'FAIL'; // Default to failure

    try {
        // 1. Start a target interactive script
        console.log(`[${testId}] Step 1: Starting target interactive script...`);
        const targetCommand = `node -e "console.log('Target script started.'); process.stdin.on('data', (data) => { const input = data.toString().trim(); console.log('Received: ' + input); if (input === 'quit') { console.log('Quitting.'); process.exit(0); } });"`;

        const executeResponse = await client.tool('execute_command', { command: targetCommand, timeout: 10 });

        // Basic check on executeResponse structure
        if (!executeResponse?.content?.[0]?.type === 'text' || !executeResponse.content[0].text) {
            throw new Error(`Invalid response format from execute_command: ${JSON.stringify(executeResponse)}`);
        }
        const executeResult = JSON.parse(executeResponse.content[0].text);

        if (!executeResult.pid) {
            throw new Error(`Failed to get PID from execute_command. Response: ${JSON.stringify(executeResult)}`);
        }
        targetPid = executeResult.pid;
        console.log(`[${testId}] Step 1: Target script started with PID: ${targetPid}. Initial output: stdout='${executeResult.stdout}', stderr='${executeResult.stderr}', exit_code=${executeResult.exit_code}`);

        // Wait a moment for the script to be ready
        await delay(1000);

        // 2. Send initial input
        console.log(`[${testId}] Step 2: Sending initial input ('hello ${testId}')...`);
        const input1 = `hello ${testId}`;
        const sendInputResponse1 = await client.tool('send_terminal_input', { pid: targetPid, input: input1, timeout: 5 });

        // Basic check on sendInputResponse1 structure
        if (!sendInputResponse1?.content?.[0]?.type === 'text' || !sendInputResponse1.content[0].text) {
            throw new Error(`Invalid response format from send_terminal_input (1): ${JSON.stringify(sendInputResponse1)}`);
        }
        const inputResult1 = JSON.parse(sendInputResponse1.content[0].text);
        console.log(`[${testId}] Step 2: Response 1: ${JSON.stringify(inputResult1)}`);

        if (inputResult1.status !== 'Input Sent' && inputResult1.status !== 'Timeout') {
            throw new Error(`Expected status 'Input Sent' or 'Timeout' after first input, but got '${inputResult1.status}'. Stderr: ${inputResult1.stderr}`);
        }
        if (!inputResult1.stdout || !inputResult1.stdout.includes(`Received: ${input1}`)) {
            throw new Error(`Expected stdout to contain 'Received: ${input1}', but got: '${inputResult1.stdout}'`);
        }
        console.log(`[${testId}] Step 2: Initial input sent and expected echo received successfully.`);

        // 3. Send 'quit' command
        console.log(`[${testId}] Step 3: Sending 'quit' command...`);
        const sendInputResponse2 = await client.tool('send_terminal_input', { pid: targetPid, input: 'quit', timeout: 5 });

        // Basic check on sendInputResponse2 structure
        if (!sendInputResponse2?.content?.[0]?.type === 'text' || !sendInputResponse2.content[0].text) {
            throw new Error(`Invalid response format from send_terminal_input (2): ${JSON.stringify(sendInputResponse2)}`);
        }
        const inputResult2 = JSON.parse(sendInputResponse2.content[0].text);
        console.log(`[${testId}] Step 3: Response 2: ${JSON.stringify(inputResult2)}`);

        // Check if the process exited as expected
        // It might return "Input Sent" if the exit happens *after* the listeners detach but before the timeout
        // Or it might return "Process Exited" if the exit was captured.
        if (inputResult2.status !== 'Process Exited' && inputResult2.status !== 'Input Sent' && inputResult2.status !== 'Timeout') {
            throw new Error(`Expected status 'Process Exited', 'Input Sent', or 'Timeout' after quit command, but got '${inputResult2.status}'. Stderr: ${inputResult2.stderr}`);
        }
        if (inputResult2.stdout && !inputResult2.stdout.includes('Received: quit')) {
            console.warn(`[${testId}] Warning: Expected stdout to contain 'Received: quit' in response 2, but got: '${inputResult2.stdout}' (Might be okay if exit was fast)`);
        }
        if (inputResult2.status === 'Process Exited' && inputResult2.exit_code !== 0) {
            throw new Error(`Process exited after quit, but with unexpected code: ${inputResult2.exit_code}`);
        }
        console.log(`[${testId}] Step 3: 'quit' command sent successfully. Status: ${inputResult2.status}`);

        // Allow a moment for the process to fully terminate if needed
        await delay(500);

        // 4. Verify process is no longer running (optional, cleanup should handle)
        console.log(`[${testId}] Step 4: Verifying target process termination (using get_terminal_status)...`);
        const statusResponse = await client.tool('get_terminal_status', { timeout: 0 });
        if (!statusResponse?.content?.[0]?.type === 'text' || !statusResponse.content[0].text) {
            throw new Error(`Invalid response format from get_terminal_status: ${JSON.stringify(statusResponse)}`);
        }
        const statusResult = JSON.parse(statusResponse.content[0].text);
        const targetFinalState = statusResult.terminals.find(t => t.pid === targetPid);

        if (targetFinalState && targetFinalState.status === 'Running') {
            console.warn(`[${testId}] Warning: Target process ${targetPid} still reported as 'Running' after quit command.`);
            // Attempt cleanup just in case
            throw new Error("Process did not terminate as expected after 'quit'.");
        } else if (targetFinalState) {
            console.log(`[${testId}] Step 4: Target process final status: ${targetFinalState.status}, Exit Code: ${targetFinalState.exit_code}`);
        } else {
            console.log(`[${testId}] Step 4: Target process ${targetPid} not found in status list (likely cleaned up).`);
        }

        console.log(`[${testId}] Test steps completed successfully.`);
        finalStatus = 'PASS';

    } catch (error) {
        console.error(`[${testId}] Test Error:`, error);
        finalStatus = 'FAIL';
    } finally {
        // 5. Cleanup: Stop the terminal command if it's still somehow running
        if (targetPid) {
            console.log(`[${testId}] Final Cleanup: Attempting to stop PID ${targetPid}...`);
            try {
                const stopResponse = await client.tool('stop_terminal_command', { pids: [targetPid], lines: 5 });
                if (!stopResponse?.content?.[0]?.type === 'text' || !stopResponse.content[0].text) {
                    console.error(`[${testId}] Invalid response format from stop_terminal_command: ${JSON.stringify(stopResponse)}`);
                } else {
                    const stopResult = JSON.parse(stopResponse.content[0].text);
                    console.log(`[${testId}] Cleanup response: ${JSON.stringify(stopResult)}`);
                }
            } catch (cleanupError) {
                console.error(`[${testId}] Error during cleanup for PID ${targetPid}:`, cleanupError);
                // Don't fail the test run solely on cleanup error if main steps passed
            }
        }
        console.log(`[Test End] test_mcp_send_input - ID: ${testId} - Status: ${finalStatus}`);
        // Exit with appropriate code for test runners
        process.exit(finalStatus === 'PASS' ? 0 : 1);
    }
}

runTest(); 