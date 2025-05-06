import assert from 'assert';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

// ES module equivalent for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// persistent_child.sh sleeps for 20s then parent sleeps for 20s.
// We will use its path for a long-running command.
const projectRoot = path.resolve(__dirname, '../../');
// const helperScriptRelativePath = 'tests/mcp_server_tests/helper_scripts/persistent_child.sh';
// let LONG_RUNNING_SCRIPT_PATH = path.resolve(projectRoot, helperScriptRelativePath);

// if (os.platform() === 'win32') {
//     LONG_RUNNING_SCRIPT_PATH = LONG_RUNNING_SCRIPT_PATH.replace(/^([A-Za-z]):\\/, (match, drive) => `/${drive.toLowerCase()}/`);
//     LONG_RUNNING_SCRIPT_PATH = LONG_RUNNING_SCRIPT_PATH.replace(/\\/g, '/');
// }

const LONG_RUNNING_COMMAND = 'sleep 25s'; // Using sleep directly

async function main() {
    console.log('[Test] Starting test_execute_command_long_timeout.js...');
    const serverDir = path.resolve(__dirname, '../../.cursor/mcp/mcp-commit-server');
    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'],
        cwd: serverDir
    });
    const client = new McpClient({ name: "TestClientLongTimeout", version: "0.0.1" });

    let scriptPid;

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        // const commandToRun = LONG_RUNNING_SCRIPT_PATH;
        const commandToRun = LONG_RUNNING_COMMAND;
        // Execute with a timeout shorter than the command's total duration
        // MCP execute_command default timeout is 10s, let's use that explicitly for clarity.
        const executeTimeout = 10; // seconds

        console.log(`[Test] Executing long-running script: ${commandToRun} with MCP timeout: ${executeTimeout}s`);
        const execResult = await client.callTool({
            name: 'execute_command',
            arguments: { command: commandToRun, timeout: executeTimeout }
        });
        console.log('[Test] Result from initial execute_command:', JSON.stringify(execResult, null, 2));

        const execResponse = JSON.parse(execResult.content[0].text);
        assert(execResponse.pid, 'Long-running script execution should return a PID');
        scriptPid = execResponse.pid;
        assert.strictEqual(execResponse.status, 'Running', `Expected status to be 'Running' due to timeout, got: ${execResponse.status}. Stderr: ${execResponse.stderr}`);
        console.log(`[Test] Long-running script started with PID: ${scriptPid}, status: ${execResponse.status}`);

        console.log('[Test] Waiting for 15 seconds (longer than MCP timeout, shorter than script duration)...');
        await new Promise(resolve => setTimeout(resolve, 15000));

        console.log(`[Test] Calling get_terminal_status to check on PID: ${scriptPid}`);
        const statusResult = await client.callTool({ name: 'get_terminal_status', arguments: {} });
        const statusResponse = JSON.parse(statusResult.content[0].text);
        const processState = statusResponse.terminals.find(t => t.pid === scriptPid);
        assert(processState, `PID ${scriptPid} not found in get_terminal_status response.`);
        assert.strictEqual(processState.status, 'Running', `Expected PID ${scriptPid} to still be 'Running', got: ${processState.status}`);
        console.log(`[Test] PID ${scriptPid} confirmed status: ${processState.status}`);

        console.log(`[Test] Calling stop_terminal_command for PID: ${scriptPid}`);
        const stopResult = await client.callTool({
            name: 'stop_terminal_command',
            arguments: { pids: [scriptPid], lines: 10 }
        });
        const stopResponse = JSON.parse(stopResult.content[0].text);
        assert(stopResponse[0].status.includes('kill signal sent') || stopResponse[0].status.includes('Error during tree kill') || stopResponse[0].status.includes('already exited'), 'Stop command did not report expected status: ' + stopResponse[0].status);
        console.log(`[Test] Stop command reported: ${stopResponse[0].status}`);

        console.log('[Test] Waiting a few seconds for script to terminate fully...');
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Final check if process is gone
        let checkCmd;
        if (os.platform() === 'win32') {
            checkCmd = `tasklist /NH /FI "PID eq ${scriptPid}"`;
        } else {
            checkCmd = `ps -p ${scriptPid} -o pid=`;
        }
        const checkPidResult = await client.callTool({ name: 'execute_command', arguments: { command: checkCmd, timeout: 5 } });
        const checkPidResponse = JSON.parse(checkPidResult.content[0].text);
        let scriptStillRunning = false;
        if (os.platform() === 'win32') {
            scriptStillRunning = checkPidResponse.stdout.trim().includes(scriptPid.toString());
        } else {
            scriptStillRunning = checkPidResponse.stdout.trim() !== '';
        }
        assert.strictEqual(scriptStillRunning, false, `Script ${scriptPid} should NOT be running after stop. Check stdout: ${checkPidResponse.stdout}`);

        console.log('[Test] test_execute_command_long_timeout.js PASSED');

    } catch (error) {
        console.error('[Test] test_execute_command_long_timeout.js FAILED:', error);
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