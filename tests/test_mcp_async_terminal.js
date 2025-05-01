const child_process = require('child_process');
const path = require('path');
const fs = require('fs');
const assert = require('assert');
const util = require('util'); // Needed for util.format

// Revert: Use the commit server path again for spawning
const SERVER_PATH = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/server.js');
const LOGS_DIR = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/logs');
const STATE_FILE = path.join(__dirname, '../.cursor/mcp/mcp-commit-server/terminals_status.json');
const TEST_LOG_FILE = path.join(__dirname, 'test_mcp_async_terminal.log');

// --- File Logging Helper ---
function logToFile(level, ...args) {
    const timestamp = new Date().toISOString();
    const message = util.format(...args);
    const logLine = `${timestamp} [${level}] ${message}\n`;
    try {
        fs.appendFileSync(TEST_LOG_FILE, logLine);
    } catch (e) {
        // Fallback to console if file logging fails
        console.error(`FALLBACK (Log file error: ${e.message}): ${logLine.trim()}`);
    }
}

// Clear log file at the start of the test run
try {
    if (fs.existsSync(TEST_LOG_FILE)) {
        fs.unlinkSync(TEST_LOG_FILE);
    }
} catch (e) {
    console.error(`Failed to clear old test log file ${TEST_LOG_FILE}: ${e.message}`);
}
// --- End File Logging Helper ---

let serverProcess;
let responseBuffer = '';
let responsePromises = [];
let requestIdCounter = 0;

// Helper to start the server process
function startServer() {
    return new Promise((resolve, reject) => {
        logToFile('INFO', 'Starting server...');
        // Clean up old state/logs if they exist
        try { if (fs.existsSync(STATE_FILE)) fs.unlinkSync(STATE_FILE); } catch (e) { logToFile('WARN', 'Could not delete old state file', e.message); }
        try { if (fs.existsSync(LOGS_DIR)) fs.rmSync(LOGS_DIR, { recursive: true, force: true }); } catch (e) { logToFile('WARN', 'Could not delete old logs dir', e.message); }
        // Ensure logs dir exists *after* potential deletion
        try { if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, { recursive: true }); } catch (e) { logToFile('ERROR', '[Test Setup] Failed to recreate logs dir:', e.message); reject(e); return; }

        logToFile('INFO', 'Spawning server process...');
        // Revert: Use node to spawn the commit server script
        serverProcess = child_process.spawn('node', [SERVER_PATH], {
            stdio: ['pipe', 'pipe', 'pipe'] // Pipe stdin, stdout, stderr
        });
        logToFile('INFO', 'Spawn called.');

        serverProcess.stdout.on('data', (data) => {
            // logToFile('DEBUG', `Server STDOUT: ${data}`); // Optionally log server stdout
            responseBuffer += data.toString();
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
                        logToFile('ERROR', 'Failed to parse server response JSON:', jsonString, e);
                    }
                }
            }
        });

        serverProcess.stderr.on('data', (data) => {
            logToFile('ERROR', `Server STDERR: ${data}`);
        });

        serverProcess.on('error', (err) => {
            logToFile('ERROR', 'Server process error:', err);
            reject(err);
        });

        serverProcess.on('close', (code) => {
            logToFile('INFO', `Server process exited with code ${code}`);
            serverProcess = null; // Mark as stopped
            Object.values(responsePromises).forEach(p => p.reject(new Error('Server process exited unexpectedly')));
            responsePromises = {};
        });

        setTimeout(() => {
            if (serverProcess && !serverProcess.killed) {
                logToFile('INFO', 'Server started (PID: ' + serverProcess.pid + ').');
                resolve();
            } else {
                logToFile('ERROR', 'Server failed to start or exited immediately');
                reject(new Error('Server failed to start or exited immediately'));
            }
        }, 1500);
    });
}

// Helper to stop the server process
function stopServer() {
    return new Promise((resolve) => {
        if (serverProcess && !serverProcess.killed) {
            logToFile('INFO', 'Stopping server...');
            serverProcess.kill('SIGTERM');
            setTimeout(resolve, 500);
        } else {
            logToFile('INFO', 'Server already stopped.');
            resolve();
        }
        serverProcess = null;
    });
}

// Helper to send MCP request and get response
function sendRequest(method, params) {
    const id = ++requestIdCounter;
    const request = {
        jsonrpc: '2.0',
        id,
        method: 'tools/call',
        params: {
            name: method,
            arguments: params
        }
    };
    const requestString = JSON.stringify(request) + '\n';
    logToFile('DEBUG', `Sending request ${id}:`, JSON.stringify(request));

    return new Promise((resolve, reject) => {
        if (!serverProcess || serverProcess.killed) {
            logToFile('ERROR', `Cannot send request ${id} (${method}), server process is not running`);
            return reject(new Error('Server process is not running'));
        }
        responsePromises[id] = { resolve, reject };
        try {
            serverProcess.stdin.write(requestString);
        } catch (e) {
            delete responsePromises[id];
            logToFile('ERROR', `Failed to write request ${id} (${method}) to server stdin: ${e.message}`);
            reject(new Error(`Failed to write to server stdin: ${e.message}`));
        }

        setTimeout(() => {
            if (responsePromises[id]) {
                logToFile('ERROR', `Request ${id} (${method}) timed out`);
                responsePromises[id].reject(new Error(`Request ${id} (${method}) timed out`));
                delete responsePromises[id];
            }
        }, 10000);
    });
}

// --- Test Workflow ---
async function runTests() {
    logToFile('INFO', 'runTests started');
    let executedPid = null;
    let stdoutLog = null;
    let stderrLog = null;

    try {
        logToFile('INFO', 'Starting server via startServer()...');
        await startServer();
        logToFile('INFO', 'startServer() promise resolved.');

        // 1. Execute command
        logToFile('INFO', 'Executing command via sendRequest...');
        const testMessage = `MCP Test Message ${Date.now()}`;
        // Ensure we use a simple command for testing the MCP tools themselves
        const commandToRun = `echo "${testMessage}" && >&2 echo test_command_stderr`;
        const execResultRaw = await sendRequest('execute_command', {
            command: commandToRun,
            timeout: 5 // Short timeout for simple echo
        });
        logToFile('INFO', 'Execute Result (Raw): %j', execResultRaw);

        let execResult = {};
        try {
            assert(execResultRaw.content && Array.isArray(execResultRaw.content) && execResultRaw.content.length > 0, 'Invalid execute result structure: missing content array');
            assert(execResultRaw.content[0].type === 'text', 'Invalid execute result structure: content type is not text');
            assert(typeof execResultRaw.content[0].text === 'string', 'Invalid execute result structure: text field is not a string');
            execResult = JSON.parse(execResultRaw.content[0].text);
            logToFile('INFO', 'Parsed Execute Result: %j', execResult);
        } catch (e) {
            logToFile('ERROR', 'Assertion Failed (Execute Result Parsing): %s. Raw: %j', e.message, execResultRaw);
            assert.fail(`Failed to parse execute_command result JSON from text field. Raw object: ${JSON.stringify(execResultRaw)} - Error: ${e.message}`);
        }

        assert(execResult.pid, 'Execute command should return a PID');
        executedPid = execResult.pid;
        logToFile('INFO', 'Execute: PASSED. PID: %s', executedPid);

        // 2. Get Status
        logToFile('INFO', 'Getting status via sendRequest...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        const statusResultRaw = await sendRequest('get_terminal_status', {});
        logToFile('INFO', 'Status Result (Raw): %j', statusResultRaw);

        let statusResult = {};
        try {
            assert(statusResultRaw.content && Array.isArray(statusResultRaw.content) && statusResultRaw.content.length > 0, 'Invalid status result structure: missing content array');
            assert(statusResultRaw.content[0].type === 'text', 'Invalid status result structure: content type is not text');
            assert(typeof statusResultRaw.content[0].text === 'string', 'Invalid status result structure: text field is not a string');
            statusResult = JSON.parse(statusResultRaw.content[0].text);
            logToFile('INFO', 'Parsed Status Result: %j', statusResult);
        } catch (e) {
            logToFile('ERROR', 'Assertion Failed (Status Result Parsing): %s. Raw: %j', e.message, statusResultRaw);
            assert.fail(`Failed to parse get_terminal_status result JSON from text field. Raw object: ${JSON.stringify(statusResultRaw)} - Error: ${e.message}`);
        }

        const processStatus = statusResult.terminals.find(t => t.pid === executedPid);
        assert(processStatus, 'Status result should include the executed PID');
        assert(processStatus.status === 'Success', 'Echo command should succeed');
        assert(processStatus.exit_code === 0, 'Echo command exit code should be 0');
        logToFile('INFO', 'Get Status: PASSED');

        // 3. Get Output
        logToFile('INFO', 'Getting output via sendRequest...');
        const outputResultRaw = await sendRequest('get_terminal_output', { pid: executedPid, lines: 50 });
        logToFile('INFO', 'Output Result (Raw): %j', outputResultRaw);

        let outputResult = {};
        try {
            assert(outputResultRaw.content && Array.isArray(outputResultRaw.content) && outputResultRaw.content.length > 0, 'Invalid output result structure: missing content array');
            assert(outputResultRaw.content[0].type === 'text', 'Invalid output result structure: content type is not text');
            assert(typeof outputResultRaw.content[0].text === 'string', 'Invalid output result structure: text field is not a string');
            outputResult = JSON.parse(outputResultRaw.content[0].text);
            logToFile('INFO', 'Parsed Output Result: %j', outputResult);
        } catch (e) {
            logToFile('ERROR', 'Assertion Failed (Output Result Parsing): %s. Raw: %j', e.message, outputResultRaw);
            assert.fail(`Failed to parse get_terminal_output result JSON from text field. Raw object: ${JSON.stringify(outputResultRaw)} - Error: ${e.message}`);
        }

        assert(outputResult.stdout.includes(testMessage), `Combined log (stdout) should contain '${testMessage}'`);
        assert(outputResult.stderr.includes('test_command_stderr'), 'stderr should contain stderr string');
        logToFile('INFO', 'Get Output: PASSED');

        // 4. Stop Command
        logToFile('INFO', 'Stopping command via sendRequest...');
        const stopResultRaw = await sendRequest('stop_terminal_command', { pids: [executedPid] });
        logToFile('INFO', 'Stop Result (Raw): %j', stopResultRaw);

        let stopResultsArray = [];
        try {
            assert(stopResultRaw.content && Array.isArray(stopResultRaw.content) && stopResultRaw.content.length > 0, 'Invalid stop result structure: missing content array');
            assert(stopResultRaw.content[0].type === 'text', 'Invalid stop result structure: content type is not text');
            assert(typeof stopResultRaw.content[0].text === 'string', 'Invalid stop result structure: text field is not a string');
            stopResultsArray = JSON.parse(stopResultRaw.content[0].text);
            logToFile('INFO', 'Parsed Stop Results Array: %j', stopResultsArray);
        } catch (e) {
            logToFile('ERROR', 'Assertion Failed (Stop Result Parsing): %s. Raw: %j', e.message, stopResultRaw);
            assert.fail(`Failed to parse stop_terminal_command result JSON from text field. Raw object: ${JSON.stringify(stopResultRaw)} - Error: ${e.message}`);
        }

        assert(Array.isArray(stopResultsArray) && stopResultsArray.length === 1, 'Stop result should be an array with one element');
        const stopResult = stopResultsArray[0];
        assert(stopResult.pid === executedPid, 'Stop result element should contain the correct PID');
        assert(stopResult.status, 'Stop command result element should return a status message');
        logToFile('INFO', 'Stop Command: PASSED');

        // 5. Get Status Again (verify removed)
        logToFile('INFO', 'Getting final status via sendRequest...');
        const finalStatusResultRaw = await sendRequest('get_terminal_status', {});
        logToFile('INFO', 'Final Status Result (Raw): %j', finalStatusResultRaw);

        let finalStatusResult = {};
        try {
            assert(finalStatusResultRaw.content && Array.isArray(finalStatusResultRaw.content) && finalStatusResultRaw.content.length > 0, 'Invalid final status result structure: missing content array');
            assert(finalStatusResultRaw.content[0].type === 'text', 'Invalid final status result structure: content type is not text');
            assert(typeof finalStatusResultRaw.content[0].text === 'string', 'Invalid final status result structure: text field is not a string');
            finalStatusResult = JSON.parse(finalStatusResultRaw.content[0].text);
            logToFile('INFO', 'Parsed Final Status Result: %j', finalStatusResult);
        } catch (e) {
            logToFile('ERROR', 'Assertion Failed (Final Status Parsing): %s. Raw: %j', e.message, finalStatusResultRaw);
            assert.fail(`Failed to parse final get_terminal_status result JSON from text field. Raw object: ${JSON.stringify(finalStatusResultRaw)} - Error: ${e.message}`);
        }

        const finalProcessStatus = finalStatusResult.terminals.find(t => t.pid === executedPid);
        assert(!finalProcessStatus, 'Process should be removed from status after stop');
        logToFile('INFO', 'Final Status Check: PASSED');

        logToFile('INFO', '=== ALL TESTS PASSED ===');

    } catch (error) {
        logToFile('ERROR', '=== TEST FAILED ===');
        logToFile('ERROR', 'Error object: %s', error.stack || error);
        process.exitCode = 1; // Indicate failure
    } finally {
        logToFile('INFO', 'Stopping server in finally block...');
        await stopServer();
        logToFile('INFO', 'runTests finished');
    }
}

runTests(); 