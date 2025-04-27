console.log('[MCP Test Script] Starting execution...'); // Added early log
// tests/test_mcp_send_input.js
const { v4: uuidv4 } = require('uuid');
const process = require('process');
const { spawn } = require('child_process');
const path = require('path');

// Configuration
const serverScriptPath = path.resolve(__dirname, '../.cursor/mcp/mcp-commit-server/server.js');
let mcpServerProcess = null;
let stdoutBuffer = '';
const pendingRequests = new Map(); // Map<requestId, { resolve, reject, timeoutTimer }>");

// Helper function to send MCP request via stdio and await response
function callMcpToolViaStdio(toolName, params, timeoutMs = 10000) { // Added timeout
    return new Promise((resolve, reject) => {
        if (!mcpServerProcess || mcpServerProcess.killed || !mcpServerProcess.stdin.writable) {
            return reject(new Error("MCP Server process is not running or stdin not writable."));
        }

        const requestId = uuidv4();
        const requestBody = JSON.stringify({
            mcp_version: '1.0',
            request_id: requestId,
            tool_name: toolName,
            tool_arguments: params
        });

        console.log(`[MCP Send] ID: ${requestId.substring(0, 8)} Tool: ${toolName}, Params: ${JSON.stringify(params)}`);

        // Set a timeout for the request
        const timeoutTimer = setTimeout(() => {
            if (pendingRequests.has(requestId)) {
                console.error(`[MCP Timeout] ID: ${requestId.substring(0, 8)} Request for tool '${toolName}' timed out after ${timeoutMs}ms.`);
                pendingRequests.get(requestId).reject(new Error(`MCP request timed out after ${timeoutMs}ms for tool ${toolName}`));
                pendingRequests.delete(requestId);
            }
        }, timeoutMs);

        pendingRequests.set(requestId, { resolve, reject, timeoutTimer });

        try {
            // Write the request JSON followed by a newline
            mcpServerProcess.stdin.write(requestBody + '\n', (err) => {
                if (err) {
                    console.error(`[MCP Write Error] ID: ${requestId.substring(0, 8)} Failed to write to MCP server stdin:`, err);
                    clearTimeout(timeoutTimer);
                    pendingRequests.delete(requestId);
                    reject(new Error(`Failed to write to MCP server stdin: ${err.message}`));
                } else {
                    // console.log(`[MCP Write OK] ID: ${requestId.substring(0,8)} Request sent.`);
                }
            });
        } catch (error) {
            console.error(`[MCP Write Exception] ID: ${requestId.substring(0, 8)} Exception writing to MCP server stdin:`, error);
            clearTimeout(timeoutTimer);
            pendingRequests.delete(requestId);
            reject(new Error(`Exception writing to MCP server stdin: ${error.message}`));
        }
    });
}

// Setup stdout listener to process responses
function setupStdioListeners() {
    if (!mcpServerProcess) return;

    mcpServerProcess.stdout.on('data', (data) => {
        stdoutBuffer += data.toString();
        // console.log(`[MCP Recv Raw] Chunk: ${data.toString()}`); // Verbose logging

        let newlineIndex;
        while ((newlineIndex = stdoutBuffer.indexOf('\n')) >= 0) {
            const jsonLine = stdoutBuffer.substring(0, newlineIndex).trim();
            stdoutBuffer = stdoutBuffer.substring(newlineIndex + 1);

            if (!jsonLine) continue; // Skip empty lines

            // console.log(`[MCP Recv JSON] Line: ${jsonLine}`); // Debug log

            try {
                const response = JSON.parse(jsonLine);
                const requestId = response.response_id; // Corrected field name

                if (requestId && pendingRequests.has(requestId)) {
                    const { resolve, reject, timeoutTimer } = pendingRequests.get(requestId);
                    clearTimeout(timeoutTimer); // Clear the timeout

                    console.log(`[MCP Recv OK] ID: ${requestId.substring(0, 8)} Received response.`);

                    if (response.error) {
                        console.error(`[MCP Error Resp] ID: ${requestId.substring(0, 8)} Tool: ${response.tool_name}, Error: ${JSON.stringify(response.error)}`);
                        reject(new Error(response.error.message || `MCP Tool Error for ${response.tool_name || 'unknown tool'}`));
                    } else {
                        // Basic validation of expected format
                        if (!response.content || !Array.isArray(response.content) || response.content.length === 0 || typeof response.content[0].text !== 'string') {
                            console.warn(`[MCP Warn] Unexpected response content format for ${response.tool_name}: ${jsonLine}`);
                            // Resolve with raw response for now, maybe reject in future?
                            resolve(response);
                        } else {
                            resolve(response); // Resolve with the full response object
                        }
                    }
                    pendingRequests.delete(requestId);
                } else if (response.event === 'log_message') {
                    // Handle log messages from the server if needed
                    console.log(`[MCP Server Log] Level: ${response.level}, Message: ${response.message}`);
                }
                else {
                    console.warn(`[MCP Orphan Resp] Received response for unknown or timed out request ID: ${requestId || 'N/A'}. Data: ${jsonLine}`);
                }
            } catch (parseError) {
                console.error(`[MCP Parse Error] Failed to parse JSON line: ${jsonLine}. Error: ${parseError}`);
                // How to handle? Could reject a pending request if only one exists? Risky.
            }
        }
    });

    mcpServerProcess.stderr.on('data', (data) => {
        console.error(`[MCP Server STDERR] ${data.toString()}`);
    });

    mcpServerProcess.on('error', (err) => {
        console.error('[MCP Server ERROR] Failed to start or crashed:', err);
        // Reject all pending requests on server error?
        pendingRequests.forEach(({ reject, timeoutTimer }, id) => {
            clearTimeout(timeoutTimer);
            reject(new Error(`MCP Server error: ${err.message}`));
            pendingRequests.delete(id);
        });
    });

    mcpServerProcess.on('exit', (code, signal) => {
        console.log(`[MCP Server EXIT] Exited with code ${code}, signal ${signal}`);
        mcpServerProcess = null; // Mark as stopped
        // Reject any remaining pending requests
        pendingRequests.forEach(({ reject, timeoutTimer }, id) => {
            clearTimeout(timeoutTimer);
            reject(new Error(`MCP Server exited with code ${code}, signal ${signal} before response received.`));
            pendingRequests.delete(id);
        });
    });
}


// Helper function to introduce delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runTest() {
    const testId = uuidv4().substring(0, 8);
    console.log(`[Test Start] test_mcp_send_input (stdio) - ID: ${testId}`);
    let targetPid = null;
    let finalStatus = 'FAIL'; // Default to FAIL

    try {
        // Start the MCP server process
        console.log(`[${testId}] Spawning MCP server: node ${serverScriptPath}...`);
        mcpServerProcess = spawn('node', [serverScriptPath], {
            stdio: ['pipe', 'pipe', 'pipe'] // Pipe stdin, stdout, stderr
        });
        setupStdioListeners();
        console.log(`[${testId}] MCP server process spawned with PID: ${mcpServerProcess.pid}`);

        // Wait a moment for the server to initialize (increased delay)
        console.log(`[${testId}] Waiting 5 seconds for server initialization...`);
        await delay(5000);
        if (!mcpServerProcess || mcpServerProcess.killed) throw new Error("MCP Server failed to start or exited prematurely after delay.");
        console.log(`[${testId}] Server seems alive. Proceeding with test steps.`);

        // 1. Start a simple interactive command (`cat`)
        console.log(`[${testId}] Step 1: Starting target command ('cat')...`);
        // Assume 'cat' is in PATH (Git Bash usually adds it)
        const targetCommand = 'cat'; // Simpler, relies on PATH

        const executeResponse = await callMcpToolViaStdio('execute_command', { command: targetCommand, timeout: 5 });
        // Assuming the response content text is the JSON result string
        const executeResult = JSON.parse(executeResponse.content[0].text);
        if (!executeResult.pid) throw new Error(`Failed to get PID from execute_command. Response: ${JSON.stringify(executeResult)}`);
        targetPid = executeResult.pid;
        console.log(`[${testId}] Step 1: Target command started with PID: ${targetPid}. Initial exit_code=${executeResult.exit_code}`);
        if (executeResult.exit_code !== null) {
            let errOutput = '(no output retrieved)';
            try {
                const outResp = await callMcpToolViaStdio('get_terminal_output', { pid: targetPid, lines: 20 });
                errOutput = JSON.parse(outResp.content[0].text).stdout;
            } catch (getOutErr) { /* Ignore */ }
            throw new Error(`'cat' command exited immediately with code ${executeResult.exit_code}. Output: ${errOutput}`);
        }

        await delay(1000); // Wait briefly

        // 2. Send input line
        const inputLine = `Test line from ${testId}`;
        console.log(`[${testId}] Step 2: Sending input ('${inputLine}')...`);
        const sendInputResponse = await callMcpToolViaStdio('send_terminal_input', { pid: targetPid, input: inputLine });
        // Check success message from the tool's direct response
        if (!sendInputResponse.content[0].text.includes('Successfully sent input')) {
            throw new Error(`send_terminal_input did not confirm sending. Response: ${sendInputResponse.content[0].text}`);
        }
        console.log(`[${testId}] Step 2: Send confirmation received: ${sendInputResponse.content[0].text}`);


        await delay(1500); // Wait for cat to process/echo

        // 3. Check output
        console.log(`[${testId}] Step 3: Checking output...`);
        const outputResponse = await callMcpToolViaStdio('get_terminal_output', { pid: targetPid, lines: 20 });
        const outputResult = JSON.parse(outputResponse.content[0].text);
        const combinedOutput = outputResult.stdout + outputResult.stderr; // Check both streams
        console.log(`[${testId}] Step 3: Combined output received: ${JSON.stringify(combinedOutput)}`);
        if (!combinedOutput || !combinedOutput.trim().includes(inputLine)) {
            throw new Error(`Expected output to contain '${inputLine}', but got: '${combinedOutput}'`);
        }
        console.log(`[${testId}] Step 3: Input line found in output successfully.`);

        finalStatus = 'PASS'; // If we reach here, basic test passed

    } catch (error) {
        console.error(`[${testId}] Test Error:`, error.message);
        console.error("Stack:", error.stack); // Log stack trace for debugging
        finalStatus = 'FAIL';
    } finally {
        // 4. Cleanup: Stop the terminal command if started
        if (targetPid) {
            console.log(`[${testId}] Final Cleanup: Attempting to stop PID ${targetPid}...`);
            try {
                const stopResponse = await callMcpToolViaStdio('stop_terminal_command', { pids: [targetPid], lines: 5 });
                const stopResult = JSON.parse(stopResponse.content[0].text);
                console.log(`[${testId}] Cleanup response: ${JSON.stringify(stopResult[0] || stopResult)}`);
            } catch (cleanupError) {
                console.error(`[${testId}] Error during target process cleanup for PID ${targetPid}:`, cleanupError.message);
                if (finalStatus === 'PASS') finalStatus = 'PASS_CLEANUP_FAILED';
            }
        } else {
            console.log(`[${testId}] Final Cleanup: No target PID to stop.`);
        }

        // Ensure MCP server process is killed
        if (mcpServerProcess && !mcpServerProcess.killed) {
            console.log(`[${testId}] Final Cleanup: Killing MCP server process PID ${mcpServerProcess.pid}...`);
            const killed = mcpServerProcess.kill();
            console.log(`[${testId}] MCP server process kill signal sent (Success: ${killed}).`);
            mcpServerProcess = null; // Reset reference
        } else {
            console.log(`[${testId}] Final Cleanup: MCP server process already stopped or never started.`);
        }

        console.log(`[Test End] test_mcp_send_input (stdio) - ID: ${testId} - Status: ${finalStatus}`);
        process.exit(finalStatus.startsWith('PASS') ? 0 : 1);
    }
}

runTest(); 