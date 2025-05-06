import assert from 'assert';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

// ES module equivalent for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Construct an absolute POSIX-style path for the Python helper script
const projectRoot = path.resolve(__dirname, '../../'); // Moves from tests/mcp_server_tests/ to project root
const pythonHelperRelativePath = 'tests/mcp_server_tests/helper_scripts/temp_python_script.py';
let PYTHON_SCRIPT_PATH = path.resolve(projectRoot, pythonHelperRelativePath);

if (os.platform() === 'win32') {
    PYTHON_SCRIPT_PATH = PYTHON_SCRIPT_PATH.replace(/^([A-Za-z]):\\/, (match, drive) => `/${drive.toLowerCase()}/`);
    PYTHON_SCRIPT_PATH = PYTHON_SCRIPT_PATH.replace(/\\/g, '/');
}

const PYTHON_COMMAND = `python ${PYTHON_SCRIPT_PATH}`;

async function main() {
    console.log('[Test] Starting test_python_interrupt.js...');
    const serverDir = path.resolve(__dirname, '../../.cursor/mcp/mcp-commit-server');
    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'],
        cwd: serverDir
    });
    const client = new McpClient({ name: "TestClientPythonInterrupt", version: "0.0.1" });

    let scriptPid;

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        console.log(`[Test] Executing Python script: ${PYTHON_COMMAND}`);
        const execResult = await client.callTool({
            name: 'execute_command',
            arguments: { command: PYTHON_COMMAND, timeout: 30 } // Timeout for execute_command itself
        });
        console.log('[Test] Result from initial execute_command:', JSON.stringify(execResult, null, 2));

        const execResponse = JSON.parse(execResult.content[0].text);
        assert(execResponse.pid, 'Python script execution should return a PID');
        scriptPid = execResponse.pid;
        // Status could be 'Running' or 'Success' if script finishes within MCP's internal processing before timeout response
        assert(execResponse.status === 'Running' || execResponse.status === 'Success', `Python script should be Running or Success initially, got: ${execResponse.status}. Stderr: ${execResponse.stderr}`);
        console.log(`[Test] Python script started with PID: ${scriptPid}. Initial stdout:`, execResponse.stdout);
        assert(execResponse.stdout.includes('Python script (PID:'), 'Expected initial output from Python script');

        console.log('[Test] Waiting for 5 seconds to let Python script run...');
        await new Promise(resolve => setTimeout(resolve, 5000));

        console.log(`[Test] Calling stop_terminal_command for Python script PID: ${scriptPid}`);
        const stopResult = await client.callTool({
            name: 'stop_terminal_command',
            arguments: { pids: [scriptPid], lines: 50 } // Get some final output
        });
        console.log('[Test] Result from stop_terminal_command:', JSON.stringify(stopResult, null, 2));
        const stopResponse = JSON.parse(stopResult.content[0].text);
        assert(stopResponse[0].status.includes('kill signal sent') || stopResponse[0].status.includes('Error during tree kill') || stopResponse[0].status.includes('already exited'), 'Stop command did not report expected status: ' + stopResponse[0].status);

        console.log('[Test] Waiting a few seconds for Python script to terminate...');
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Verify process is gone
        let checkCmd;
        if (os.platform() === 'win32') {
            checkCmd = `tasklist /NH /FI "PID eq ${scriptPid}"`;
        } else {
            checkCmd = `ps -p ${scriptPid} -o pid=`;
        }
        console.log(`[Test] Checking for Python script PID ${scriptPid} using command: ${checkCmd}`);
        const checkPidResult = await client.callTool({
            name: 'execute_command',
            arguments: { command: checkCmd, timeout: 5 }
        });
        console.log('[Test] Result from PID check command:', JSON.stringify(checkPidResult, null, 2));
        const checkPidResponse = JSON.parse(checkPidResult.content[0].text);

        let pythonScriptStillRunning = false;
        if (os.platform() === 'win32') {
            pythonScriptStillRunning = checkPidResponse.stdout.trim().includes(scriptPid.toString());
        } else {
            pythonScriptStillRunning = checkPidResponse.stdout.trim() !== '';
        }
        assert.strictEqual(pythonScriptStillRunning, false, `Python script ${scriptPid} should NOT be running after tree kill. Check stdout: ${checkPidResponse.stdout}`);

        // Check script output for signs of termination
        const stoppedScriptOutput = stopResponse[0].stdout + stopResponse[0].stderr;
        console.log("[Test] Combined output from stopped script:", stoppedScriptOutput);
        assert(!stoppedScriptOutput.includes('completed normally without interruption'), 'Python script should not have completed normally.');
        // It might or might not say GRACEFUL_SHUTDOWN depending on how tree-kill works (SIGTERM vs SIGKILL)

        console.log('[Test] test_python_interrupt.js PASSED');

    } catch (error) {
        console.error('[Test] test_python_interrupt.js FAILED:', error);
        if (scriptPid && client.isConnected) {
            try {
                console.log(`[Test] Attempting cleanup: stopping script PID ${scriptPid} if test failed.`);
                await client.callTool({ name: 'stop_terminal_command', arguments: { pids: [scriptPid] } });
            } catch (cleanupError) {
                console.error('[Test] Error during test failure cleanup:', cleanupError);
            }
        }
        process.exit(1);
    } finally {
        if (client.isConnected) {
            await client.disconnect();
        }
        console.log('[Test] Disconnected from MCP server.');
    }
}

main(); 