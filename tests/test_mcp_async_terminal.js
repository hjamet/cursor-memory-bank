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

        // --- Test Success Case --- 
        console.log('\n[Test] === Executing Command (Success Case) ===');
        // Use a command that should succeed and produce predictable output
        const successCommand = `node -e "process.exit(0);"`;
        const successExecResultRaw = await sendRequest('execute_command', {
            command: successCommand,
            timeout: 5
        });
        console.log('[Test] Success Execute Result (Raw MCP Result Object):', successExecResultRaw);
        let successExecResult = JSON.parse(successExecResultRaw.content[0].text);
        let successPid = successExecResult.pid;
        assert(successPid, 'Successful command should return a PID');
        console.log('[Test] Success Execute: PASSED');

        console.log('\n[Test] === Getting Status (Success Case) ===');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for completion
        const successStatusResultRaw = await sendRequest('get_terminal_status', {});
        let successStatusResult = JSON.parse(successStatusResultRaw.content[0].text);
        const successProcessStatus = successStatusResult.terminals.find(t => t.pid === successPid);
        assert(successProcessStatus, 'Status result should include the success PID');
        assert.strictEqual(successProcessStatus.status, 'Success', 'node exit 0 command should succeed');
        assert.strictEqual(successProcessStatus.exit_code, 0, 'node exit 0 command exit code should be 0');
        console.log('[Test] Success Get Status: PASSED');

        console.log('\n[Test] === Getting Output (Success Case) ===');
        const successOutputResultRaw = await sendRequest('get_terminal_output', { pid: successPid, lines: 10 });
        let successOutputResult = JSON.parse(successOutputResultRaw.content[0].text);
        assert.strictEqual(successOutputResult.stdout, '', 'Successful node exit 0 stdout should be empty');
        assert.strictEqual(successOutputResult.stderr, '', 'Successful node exit 0 stderr should be empty');
        console.log('[Test] Success Get Output: PASSED');

        console.log('\n[Test] === Stopping Command (Success Case) ===');
        const successStopResultRaw = await sendRequest('stop_terminal_command', { pids: [successPid] });
        let successStopResultsArray = JSON.parse(successStopResultRaw.content[0].text);
        const successStopResult = successStopResultsArray[0];
        const successExpectedStatusPattern = /already exited before termination attempt.*Log cleanup successful/;
        assert(successExpectedStatusPattern.test(successStopResult.status), `Stop status should indicate already exited and successful cleanup. Got: "${successStopResult.status}"`);
        console.log('[Test] Success Stop Command: PASSED');

        // --- Test Failure Case ---
        console.log('\n[Test] === Executing Command (Failure Case) ===');
        // Use a command that should fail and produce predictable output
        const failCommand = `node -e "process.exit(1);"`;
        const failExecResultRaw = await sendRequest('execute_command', {
            command: failCommand,
            timeout: 5
        });
        console.log('[Test] Failure Execute Result (Raw MCP Result Object):', failExecResultRaw);
        let failExecResult = JSON.parse(failExecResultRaw.content[0].text);
        let failPid = failExecResult.pid;
        assert(failPid, 'Failing command should return a PID');
        console.log('[Test] Failure Execute: PASSED');

        console.log('\n[Test] === Getting Status (Failure Case) ===');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for completion
        const failStatusResultRaw = await sendRequest('get_terminal_status', {});
        let failStatusResult = JSON.parse(failStatusResultRaw.content[0].text);
        const failProcessStatus = failStatusResult.terminals.find(t => t.pid === failPid);
        assert(failProcessStatus, 'Status result should include the fail PID');
        assert.strictEqual(failProcessStatus.status, 'Failure', 'node exit 1 command should fail');
        assert.strictEqual(failProcessStatus.exit_code, 1, 'node exit 1 command exit code should be 1');
        console.log('[Test] Failure Get Status: PASSED');

        console.log('\n[Test] === Getting Output (Failure Case) ===');
        const failOutputResultRaw = await sendRequest('get_terminal_output', { pid: failPid, lines: 10 });
        let failOutputResult = JSON.parse(failOutputResultRaw.content[0].text);
        assert.strictEqual(failOutputResult.stdout, '', 'Failing node exit 1 stdout should be empty');
        assert.strictEqual(failOutputResult.stderr, '', 'Failing node exit 1 stderr should be empty');
        console.log('[Test] Failure Get Output: PASSED');

        console.log('\n[Test] === Stopping Command (Failure Case) ===');
        const failStopResultRaw = await sendRequest('stop_terminal_command', { pids: [failPid] });
        let failStopResultsArray = JSON.parse(failStopResultRaw.content[0].text);
        const failStopResult = failStopResultsArray[0];
        const failExpectedStatusPattern = /already exited before termination attempt.*Log cleanup successful/;
        assert(failExpectedStatusPattern.test(failStopResult.status), `Stop status should indicate already exited and successful cleanup. Got: "${failStopResult.status}"`);
        console.log('[Test] Failure Stop Command: PASSED');


        // --- Final Checks --- 
        console.log('\n[Test] === Getting Status (Final Check) ===');
        const finalStatusResultRaw = await sendRequest('get_terminal_status', {});
        let finalStatusResult = JSON.parse(finalStatusResultRaw.content[0].text);
        const successProcessFinal = finalStatusResult.terminals.find(t => t.pid === successPid);
        const failProcessFinal = finalStatusResult.terminals.find(t => t.pid === failPid);
        assert(!successProcessFinal, 'Success process should be removed from status after stop');
        assert(!failProcessFinal, 'Failure process should be removed from status after stop');
        console.log('[Test] Final Status Check: PASSED');

        // Note: Log cleanup check removed as state doesn't store paths anymore for this test
        // Find state requires parsing state file directly
        // const successState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).find(s => s.pid === successPid);
        // const failState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).find(s => s.pid === failPid);
        // assert(!fs.existsSync(successState?.stdout_log), 'stdout log file should be deleted after stop');

        console.log('\n[Test] === ALL TESTS PASSED (using node exit commands) ===');

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