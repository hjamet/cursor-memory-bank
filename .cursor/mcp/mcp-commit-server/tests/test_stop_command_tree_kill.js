import assert from 'assert';
import { Client as McpClient } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import os from 'os';

const toolName = 'InternalAsyncTerminal'; // Server name for context, toolID is used in callTool
const SCRIPT_PATH = path.join(process.cwd(), '.cursor/mcp/mcp-commit-server/tests/helper_scripts/persistent_child.sh').replace(/\\/g, '/');

async function main() {
    console.log('[Test] Starting test_stop_command_tree_kill.js...');
    const serverDir = process.cwd(); // Assuming test is run from .cursor/mcp/mcp-commit-server
    const transport = new StdioClientTransport({
        command: 'node',
        args: ['server.js'],
        cwd: serverDir
    });
    const client = new McpClient({ name: "TestClient", version: "0.0.1" });

    let parentPid;
    let childPidToWatch;

    try {
        await client.connect(transport);
        console.log('[Test] Connected to MCP server.');

        console.log(`[Test] Executing script: ${SCRIPT_PATH}`);
        const execResult = await client.callTool({
            toolID: 'execute_command',
            params: { command: SCRIPT_PATH, timeout: 10 }
        });
        console.log('[Test] Result from initial execute_command:', JSON.stringify(execResult, null, 2));

        const execResponse = JSON.parse(execResult.content[0].text);
        assert(execResponse.status === 'Running' || execResponse.status === 'Success', 'Script should be running or completed quickly if it failed to start child correctly');
        parentPid = execResponse.pid;
        assert(parentPid, 'Parent PID not found in execute_command response');
        console.log(`[Test] Parent script started with PID: ${parentPid}`);

        const childPidRegex = /CHILD_PROCESS_PID_MARKER:(\d+)/;
        const match = execResponse.stdout.match(childPidRegex);
        assert(match && match[1], 'CHILD_PROCESS_PID_MARKER not found in script output. Output: ' + execResponse.stdout);
        childPidToWatch = parseInt(match[1], 10);
        console.log(`[Test] Parsed child process PID to watch: ${childPidToWatch}`);

        console.log(`[Test] Calling stop_terminal_command for parent PID: ${parentPid}`);
        const stopResult = await client.callTool({
            toolID: 'stop_terminal_command',
            params: { pids: [parentPid], lines: 10 }
        });
        console.log('[Test] Result from stop_terminal_command:', JSON.stringify(stopResult, null, 2));
        const stopResponse = JSON.parse(stopResult.content[0].text);
        assert(stopResponse[0].status.includes('kill signal sent') || stopResponse[0].status.includes('Error during tree kill'), 'Stop command did not report expected status: ' + stopResponse[0].status);

        console.log('[Test] Waiting a few seconds for processes to terminate...');
        await new Promise(resolve => setTimeout(resolve, 3000));

        let checkCmd;
        if (os.platform() === 'win32') {
            checkCmd = `tasklist /NH /FI "PID eq ${childPidToWatch}"`; // NH for no header
        } else {
            checkCmd = `ps -p ${childPidToWatch} -o pid=`; // Only output PID if exists
        }
        console.log(`[Test] Checking for child PID ${childPidToWatch} using command: ${checkCmd}`);
        const checkPidResult = await client.callTool({
            toolID: 'execute_command',
            params: { command: checkCmd, timeout: 5 }
        });
        console.log('[Test] Result from PID check command:', JSON.stringify(checkPidResult, null, 2));
        const checkPidResponse = JSON.parse(checkPidResult.content[0].text);

        if (os.platform() === 'win32') {
            // If tasklist /NH finds the PID, it will print something. If not, stdout is usually empty or specific INFO message.
            // A more direct check: if stdout contains the PID string, it's likely still there.
            const childStillRunning = checkPidResponse.stdout.trim().includes(childPidToWatch.toString());
            assert.strictEqual(childStillRunning, false, `Child process ${childPidToWatch} should NOT be running after tree kill (tasklist output: ${checkPidResponse.stdout})`);
        } else {
            // On POSIX, `ps -p <PID> -o pid=` should be empty if PID not found, and exit code non-zero.
            const childStillRunning = checkPidResponse.stdout.trim() !== '';
            assert.strictEqual(childStillRunning, false, `Child process ${childPidToWatch} should NOT be running (ps output: ${checkPidResponse.stdout}, exit: ${checkPidResponse.exit_code})`);
            if (childStillRunning) {
                assert.notStrictEqual(checkPidResponse.exit_code, 0, `ps exit code should be non-zero if child was killed but ps found something.`);
            }
        }

        console.log('[Test] test_stop_command_tree_kill.js PASSED');

    } catch (error) {
        console.error('[Test] test_stop_command_tree_kill.js FAILED:', error);
        if (childPidToWatch) console.error(`[Test] Child PID was: ${childPidToWatch}`);
        if (parentPid && client.isConnected) {
            try {
                console.log(`[Test] Attempting cleanup: stopping parent PID ${parentPid} if test failed.`);
                await client.callTool({ toolID: 'stop_terminal_command', params: { pids: [parentPid] } });
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