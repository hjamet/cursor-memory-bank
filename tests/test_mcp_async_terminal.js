const child_process = require('child_process');
const path = require('path');
const fs = require('fs');
const assert = require('assert');

const SERVER_PATH = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/server.js');
const LOGS_DIR = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/logs');
const STATE_FILE = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/terminals_status.json');

let serverProcess;
let responseBuffer = '';
let responsePromises = [];
let requestIdCounter = 0;

// Helper to start the server process
function startServer() {
    return new Promise((resolve, reject) => {
        console.log('[Test] Starting server...');
        // Clean up old state/logs if they exist
        try { if (fs.existsSync(STATE_FILE)) fs.unlinkSync(STATE_FILE); } catch (e) { console.warn('Could not delete old state file', e.message); }
        try { if (fs.existsSync(LOGS_DIR)) fs.rmSync(LOGS_DIR, { recursive: true, force: true }); } catch (e) { console.warn('Could not delete old logs dir', e.message); }
        // Ensure logs dir exists *after* potential deletion
        try { if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, { recursive: true }); } catch (e) { console.error('[Test Setup] Failed to recreate logs dir:', e.message); reject(e); return; }


        serverProcess = child_process.spawn('node', [SERVER_PATH], {
            stdio: ['pipe', 'pipe', 'pipe'] // Pipe stdin, stdout, stderr
        });

        serverProcess.stdout.on('data', (data) => {
            // console.log(`[Server STDOUT] ${data}`); // Debug server output
            responseBuffer += data.toString();
            // Attempt to parse newline-delimited JSON responses
            let newlineIndex;
            while ((newlineIndex = responseBuffer.indexOf('\n')) >= 0) {
                const jsonString = responseBuffer.substring(0, newlineIndex).trim();
                responseBuffer = responseBuffer.substring(newlineIndex + 1);
                if (jsonString) {
                    try {
                        const response = JSON.parse(jsonString);
                        if (response.id && responsePromises[response.id]) {
                            if (response.error) {
                                responsePromises[response.id].reject(new Error(response.error.message || 'MCP Server Error'));
                            } else {
                                responsePromises[response.id].resolve(response.result);
                            }
                            delete responsePromises[response.id];
                        }
                    } catch (e) {
                        console.error('[Test] Failed to parse server response JSON:', jsonString, e);
                    }
                }
            }
        });

        serverProcess.stderr.on('data', (data) => {
            console.error(`[Server STDERR] ${data}`);
            // Reject the current promise if server logs error during startup?
            // For now, just log it. Might indicate background monitor issues etc.
        });

        serverProcess.on('error', (err) => {
            console.error('[Test] Server process error:', err);
            reject(err);
        });

        serverProcess.on('close', (code) => {
            console.log(`[Test] Server process exited with code ${code}`);
            serverProcess = null; // Mark as stopped
            // Reject any outstanding promises
            Object.values(responsePromises).forEach(p => p.reject(new Error('Server process exited unexpectedly')));
            responsePromises = {};
        });

        // Give the server a moment to start up
        setTimeout(() => {
            if (serverProcess && !serverProcess.killed) {
                console.log('[Test] Server started (PID: ' + serverProcess.pid + ').');
                resolve();
            } else {
                reject(new Error('Server failed to start or exited immediately'));
            }
        }, 1500); // Adjust timeout if server startup is slow
    });
}

// Helper to stop the server process
function stopServer() {
    return new Promise((resolve) => {
        if (serverProcess && !serverProcess.killed) {
            console.log('[Test] Stopping server...');
            serverProcess.kill('SIGTERM');
            // Wait a moment for cleanup
            setTimeout(resolve, 500);
        } else {
            console.log('[Test] Server already stopped.');
            resolve();
        }
        serverProcess = null;
    });
}

// Helper to send MCP request and get response
function sendRequest(method, params) {
    const id = ++requestIdCounter;
    // Always use 'tools/call' method and wrap the intended tool name and args
    const request = {
        jsonrpc: '2.0',
        id,
        method: 'tools/call',
        params: {
            name: method, // The actual tool name we want to call
            arguments: params // The arguments for that specific tool
        }
    };
    const requestString = JSON.stringify(request) + '\n'; // Newline delimiter

    // console.log(`[Test] Sending request ${id}:`, JSON.stringify(request)); // Debug request (use request object)

    return new Promise((resolve, reject) => {
        if (!serverProcess || serverProcess.killed) {
            return reject(new Error('Server process is not running'));
        }
        responsePromises[id] = { resolve, reject };
        try {
            serverProcess.stdin.write(requestString);
        } catch (e) {
            delete responsePromises[id]; // Clean up promise map on write error
            reject(new Error(`Failed to write to server stdin: ${e.message}`));
        }

        // Timeout for the request
        setTimeout(() => {
            if (responsePromises[id]) {
                responsePromises[id].reject(new Error(`Request ${id} (${method}) timed out`));
                delete responsePromises[id];
            }
        }, 10000); // 10 second timeout per request
    });
}

// --- Test Workflow ---
async function runTests() {
    let executedPid = null;
    let stdoutLog = null;
    let stderrLog = null;

    try {
        await startServer();

        // 1. Execute command (use specific echo)
        console.log('\n[Test] === Executing Command ===');
        const testMessage = `MCP Test Message ${Date.now()}`;
        const commandToRun = `echo "${testMessage}" && >&2 echo test_command_stderr`;
        const execResultRaw = await sendRequest('execute_command', {
            command: commandToRun,
            timeout: 5 // Short timeout, echo is fast
        });
        console.log('[Test] Execute Result (Raw MCP Result Object):', execResultRaw);

        // --- Corrected Parsing --- 
        let execResult = {}; // Initialize
        try {
            // Attempt to parse the JSON string inside the text field
            assert(execResultRaw.content && Array.isArray(execResultRaw.content) && execResultRaw.content.length > 0, 'Invalid execute result structure: missing content array');
            assert(execResultRaw.content[0].type === 'text', 'Invalid execute result structure: content type is not text');
            assert(typeof execResultRaw.content[0].text === 'string', 'Invalid execute result structure: text field is not a string');
            execResult = JSON.parse(execResultRaw.content[0].text); // Parse the actual JSON payload
        } catch (e) {
            assert.fail(`Failed to parse execute_command result JSON from text field. Raw object: ${JSON.stringify(execResultRaw)} - Error: ${e.message}`);
        }
        console.log('[Test] Parsed Execute Result:', execResult);

        // Original assertion causing the error:
        assert(execResult.pid, 'Execute command should return a PID'); // This should now work
        assert(execResult.exit_code === null || typeof execResult.exit_code === 'number', 'Execute result exit code should be null or number');
        // Note: exit_code might be 0 if echo finishes within the 5s timeout
        executedPid = execResult.pid;

        // Find state to get log paths
        const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).find(s => s.pid === executedPid);
        assert(state, 'State file should contain executed PID');
        stdoutLog = state.stdout_log; // Use stdout_log instead of logFile
        stderrLog = state.stderr_log;
        assert(stdoutLog, 'State should contain stdout_log path');
        assert(fs.existsSync(stdoutLog), 'stdout log file should exist');
        console.log('[Test] Execute: PASSED');


        // 2. Get Status
        console.log('\n[Test] === Getting Status (after slight delay) ===');
        await new Promise(resolve => setTimeout(resolve, 1000));
        const statusResultRaw = await sendRequest('get_terminal_status', {}); // Renamed
        console.log('[Test] Status Result (Raw MCP Result Object):', statusResultRaw);

        // --- Corrected Parsing for get_terminal_status --- 
        let statusResult = {}; // Initialize
        try {
            assert(statusResultRaw.content && Array.isArray(statusResultRaw.content) && statusResultRaw.content.length > 0, 'Invalid status result structure: missing content array');
            assert(statusResultRaw.content[0].type === 'text', 'Invalid status result structure: content type is not text');
            assert(typeof statusResultRaw.content[0].text === 'string', 'Invalid status result structure: text field is not a string');
            statusResult = JSON.parse(statusResultRaw.content[0].text); // Parse the actual JSON payload
        } catch (e) {
            assert.fail(`Failed to parse get_terminal_status result JSON from text field. Raw object: ${JSON.stringify(statusResultRaw)} - Error: ${e.message}`);
        }
        console.log('[Test] Parsed Status Result:', statusResult);

        const processStatus = statusResult.terminals.find(t => t.pid === executedPid); // This should now work
        assert(processStatus, 'Status result should include the executed PID');
        assert(processStatus.status === 'Success' || processStatus.status === 'Failure', 'Process status should be Success or Failure after delay');
        // We expect success for echo
        assert.strictEqual(processStatus.status, 'Success', 'Echo command should succeed');
        assert.strictEqual(processStatus.exit_code, 0, 'Echo command exit code should be 0');
        console.log('[Test] Get Status: PASSED');


        // 3. Get Output
        console.log('\n[Test] === Getting Output ===');
        const outputResultRaw = await sendRequest('get_terminal_output', { pid: executedPid, lines: 50 });
        console.log('[Test] Output Result (Raw MCP Result Object):', outputResultRaw);

        // --- Corrected Parsing for get_terminal_output --- 
        let outputResult = {}; // Initialize
        try {
            assert(outputResultRaw.content && Array.isArray(outputResultRaw.content) && outputResultRaw.content.length > 0, 'Invalid output result structure: missing content array');
            assert(outputResultRaw.content[0].type === 'text', 'Invalid output result structure: content type is not text');
            assert(typeof outputResultRaw.content[0].text === 'string', 'Invalid output result structure: text field is not a string');
            outputResult = JSON.parse(outputResultRaw.content[0].text); // Parse the actual JSON payload
        } catch (e) {
            assert.fail(`Failed to parse get_terminal_output result JSON from text field. Raw object: ${JSON.stringify(outputResultRaw)} - Error: ${e.message}`);
        }
        console.log('[Test] Parsed Output Result:', outputResult);

        // Original assertions, check combined stdout
        assert(outputResult.stdout.includes(testMessage), `Combined log (stdout) should contain '${testMessage}'`);
        assert(outputResult.stderr.includes('test_command_stderr'), 'stderr should contain stderr string');
        console.log('[Test] Get Output: PASSED');


        // 4. Stop Command
        console.log('\n[Test] === Stopping Command ===');
        // Modify the call to pass pid in an array `pids`
        const stopResultRaw = await sendRequest('stop_terminal_command', { pids: [executedPid] }); // Renamed & argument structure changed
        console.log('[Test] Stop Result (Raw MCP Result Object):', stopResultRaw);

        // The result is now expected to be { content: [{ type: "text", text: "[...]" }] }
        // We need to extract the text field and parse it
        let stopResultsArray = [];
        try {
            // Extract the JSON string from the text field before parsing
            assert(stopResultRaw.content && Array.isArray(stopResultRaw.content) && stopResultRaw.content.length > 0, 'Invalid stop result structure: missing content array');
            assert(stopResultRaw.content[0].type === 'text', 'Invalid stop result structure: content type is not text');
            assert(typeof stopResultRaw.content[0].text === 'string', 'Invalid stop result structure: text field is not a string');
            stopResultsArray = JSON.parse(stopResultRaw.content[0].text);
        } catch (e) {
            assert.fail(`Failed to parse stop_terminal_command result JSON from text field. Raw object: ${JSON.stringify(stopResultRaw)} - Error: ${e.message}`);
        }

        assert(Array.isArray(stopResultsArray) && stopResultsArray.length === 1, 'Stop result should be an array with one element');
        const stopResult = stopResultsArray[0];
        console.log('[Test] Parsed Stop Result (for PID ' + executedPid + '):', stopResult);

        assert(stopResult.pid === executedPid, 'Stop result element should contain the correct PID');
        assert(stopResult.status, 'Stop command result element should return a status message');
        assert(stopResult.status.includes('Cleanup successful'), 'Stop status should indicate successful cleanup');
        console.log('[Test] Stop Command: PASSED');


        // 5. Get Status Again (verify removed)
        console.log('\n[Test] === Getting Status (after stop) ===');
        const finalStatusResultRaw = await sendRequest('get_terminal_status', {}); // Renamed
        console.log('[Test] Final Status Result (Raw MCP Result Object):', finalStatusResultRaw);

        // --- Corrected Parsing for final get_terminal_status --- 
        let finalStatusResult = {}; // Initialize
        try {
            assert(finalStatusResultRaw.content && Array.isArray(finalStatusResultRaw.content) && finalStatusResultRaw.content.length > 0, 'Invalid final status result structure: missing content array');
            assert(finalStatusResultRaw.content[0].type === 'text', 'Invalid final status result structure: content type is not text');
            assert(typeof finalStatusResultRaw.content[0].text === 'string', 'Invalid final status result structure: text field is not a string');
            finalStatusResult = JSON.parse(finalStatusResultRaw.content[0].text); // Parse the actual JSON payload
        } catch (e) {
            assert.fail(`Failed to parse final get_terminal_status result JSON from text field. Raw object: ${JSON.stringify(finalStatusResultRaw)} - Error: ${e.message}`);
        }
        console.log('[Test] Parsed Final Status Result:', finalStatusResult);

        const finalProcessStatus = finalStatusResult.terminals.find(t => t.pid === executedPid); // This should now work
        assert(!finalProcessStatus, 'Process should be removed from status after stop');
        console.log('[Test] Final Status Check: PASSED');

        // 6. Check Log File Cleanup
        console.log('\n[Test] === Checking Log Cleanup ===');
        assert(!fs.existsSync(stdoutLog), 'stdout log file should be deleted after stop');
        assert(!fs.existsSync(stderrLog), 'stderr log file should be deleted after stop');
        console.log('[Test] Log Cleanup: PASSED');

        console.log('\n[Test] === ALL TESTS PASSED ===');

    } catch (error) {
        console.error('\n[Test] === TEST FAILED ===');
        console.error(error);
        process.exitCode = 1; // Indicate failure
    } finally {
        await stopServer();
        // Optional: Final cleanup
        try { if (fs.existsSync(STATE_FILE)) fs.unlinkSync(STATE_FILE); } catch { }
        try { if (fs.existsSync(LOGS_DIR)) fs.rmSync(LOGS_DIR, { recursive: true, force: true }); } catch { }
    }
}

runTests(); 