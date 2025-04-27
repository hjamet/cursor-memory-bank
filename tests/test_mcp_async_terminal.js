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

        // 1. Execute command (already renamed)
        console.log('\n[Test] === Executing Command ===');
        const execResult = await sendRequest('execute_command', {
            command: 'echo test_command_stdout && >&2 echo test_command_stderr',
            timeout: 5 // Short timeout, echo is fast
        });
        console.log('[Test] Execute Result:', execResult);
        assert(execResult.pid, 'Execute command should return a PID');
        assert(execResult.exit_code === null || typeof execResult.exit_code === 'number', 'Execute result exit code should be null or number');
        // Note: exit_code might be 0 if echo finishes within the 5s timeout
        executedPid = execResult.pid;

        // Find state to get log paths
        const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')).find(s => s.pid === executedPid);
        assert(state, 'State file should contain executed PID');
        stdoutLog = state.stdout_log;
        stderrLog = state.stderr_log;
        assert(fs.existsSync(stdoutLog), 'Stdout log file should exist');
        assert(fs.existsSync(stderrLog), 'Stderr log file should exist');
        console.log('[Test] Execute: PASSED');


        // 2. Get Status
        console.log('\n[Test] === Getting Status (after slight delay) ===');
        await new Promise(resolve => setTimeout(resolve, 1000));
        const statusResult = await sendRequest('get_terminal_status', {}); // Renamed
        console.log('[Test] Status Result:', statusResult);
        const processStatus = statusResult.terminals.find(t => t.pid === executedPid);
        assert(processStatus, 'Status result should include the executed PID');
        assert(processStatus.status === 'Success' || processStatus.status === 'Failure', 'Process status should be Success or Failure after delay');
        // We expect success for echo
        assert.strictEqual(processStatus.status, 'Success', 'Echo command should succeed');
        assert.strictEqual(processStatus.exit_code, 0, 'Echo command exit code should be 0');
        console.log('[Test] Get Status: PASSED');


        // 3. Get Output
        console.log('\n[Test] === Getting Output ===');
        const outputResult = await sendRequest('get_terminal_output', { pid: executedPid, lines: 50 }); // Renamed
        console.log('[Test] Output Result:', outputResult);
        assert(outputResult.stdout.includes('test_command_stdout'), 'Stdout should contain expected string');
        assert(outputResult.stderr.includes('test_command_stderr'), 'Stderr should contain expected string');
        console.log('[Test] Get Output: PASSED');


        // 4. Stop Command
        console.log('\n[Test] === Stopping Command ===');
        const stopResult = await sendRequest('stop_terminal_command', { pid: executedPid }); // Renamed
        console.log('[Test] Stop Result:', stopResult);
        assert(stopResult.status, 'Stop command should return a status message');
        assert(stopResult.status.includes('Cleanup successful'), 'Stop status should indicate successful cleanup');
        console.log('[Test] Stop Command: PASSED');


        // 5. Get Status Again (verify removed)
        console.log('\n[Test] === Getting Status (after stop) ===');
        const finalStatusResult = await sendRequest('get_terminal_status', {}); // Renamed
        console.log('[Test] Final Status Result:', finalStatusResult);
        const finalProcessStatus = finalStatusResult.terminals.find(t => t.pid === executedPid);
        assert(!finalProcessStatus, 'Process should be removed from status after stop');
        console.log('[Test] Final Status Check: PASSED');

        // 6. Check Log File Cleanup
        console.log('\n[Test] === Checking Log Cleanup ===');
        assert(!fs.existsSync(stdoutLog), 'Stdout log file should be deleted');
        assert(!fs.existsSync(stderrLog), 'Stderr log file should be deleted');
        console.log('[Test] Log Cleanup: PASSED');


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