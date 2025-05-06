import assert from 'assert';
import { McpClient, StdioClientTransport } from '@modelcontextprotocol/sdk';
import path from 'path';
import os from 'os';

const toolName = 'InternalAsyncTerminal';
const SCRIPT_PATH = path.join(process.cwd(), '.cursor/mcp/mcp-commit-server/tests/helper_scripts/persistent_child.sh').replace(/\\/g, '/');

async function main() {
    console.log('[Test] Starting test_stop_command_tree_kill.js...');
    const transport = new StdioClientTransport({ command: 'node', args: ['../server.js'], cwd: path.join(process.cwd(), '.cursor/mcp/mcp-commit-server') });
    const client = new McpClient({ transport });

    let parentPid;
    let childPidToWatch;

    try {
        await client.connect();
        console.log('[Test] Connected to MCP server.');

        // 1. Execute the parent script which starts a child
        console.log(`[Test] Executing script: ${SCRIPT_PATH}`);
        const execResult = await client.tool(toolName, 'execute_command', { command: SCRIPT_PATH, timeout: 10 });
        console.log('[Test] Result from initial execute_command:', JSON.stringify(execResult, null, 2));

        const execResponse = JSON.parse(execResult.content[0].text);
        assert.strictEqual(execResponse.status, 'Running', 'Script should be running initially or timed out while running');
        parentPid = execResponse.pid;
        assert(parentPid, 'Parent PID not found in execute_command response');
        console.log(`[Test] Parent script started with PID: ${parentPid}`);

        // 2. Parse CHILD_PROCESS_PID_MARKER from stdout to get the actual child's PID
        const childPidRegex = /CHILD_PROCESS_PID_MARKER:(\d+)/;
        const match = execResponse.stdout.match(childPidRegex);
        assert(match && match[1], 'CHILD_PROCESS_PID_MARKER not found in script output.');
        childPidToWatch = parseInt(match[1], 10);
        console.log(`[Test] Parsed child process PID to watch: ${childPidToWatch}`);

        // 3. Call stop_terminal_command on the parent PID
        console.log(`[Test] Calling stop_terminal_command for parent PID: ${parentPid}`);
        const stopResult = await client.tool(toolName, 'stop_terminal_command', { pids: [parentPid], lines: 10 });
        console.log('[Test] Result from stop_terminal_command:', JSON.stringify(stopResult, null, 2));
        const stopResponse = JSON.parse(stopResult.content[0].text);
        assert(stopResponse[0].status.includes('kill signal sent') || stopResponse[0].status.includes('Error during tree kill'), 'Stop command did not report expected status');
        // We proceed even if kill reported an error, to check the child status

        // 4. Wait briefly for processes to terminate
        console.log('[Test] Waiting a few seconds for processes to terminate...');
        await new Promise(resolve => setTimeout(resolve, 3000)); // 3 seconds

        // 5. Check if the child process is still running
        let checkCmd;
        if (os.platform() === 'win32') {
            checkCmd = `tasklist /FI "PID eq ${childPidToWatch}"`;
        } else {
            checkCmd = `ps -p ${childPidToWatch}`;
        }
        console.log(`[Test] Checking for child PID ${childPidToWatch} using command: ${checkCmd}`);
        const checkPidResult = await client.tool(toolName, 'execute_command', { command: checkCmd, timeout: 5 });
        console.log('[Test] Result from PID check command:', JSON.stringify(checkPidResult, null, 2));
        const checkPidResponse = JSON.parse(checkPidResult.content[0].text);

        if (os.platform() === 'win32') {
            // On Windows, if tasklist doesn't find the PID, stdout usually contains "INFO: No tasks are running..."
            // and exit_code might be 0 if the filter is valid but finds nothing, or 1 if PID is invalid format (less likely here).
            // A more reliable check is that stdout *doesn't* contain the PID itself if the process is gone.
            const childStillRunning = checkPidResponse.stdout.includes(childPidToWatch.toString());
            assert.strictEqual(childStillRunning, false, `Child process ${childPidToWatch} should NOT be running after tree kill (tasklist output: ${checkPidResponse.stdout})`);
        } else {
            // On POSIX, `ps -p <PID>` has exit code 1 if PID not found.
            assert.notStrictEqual(checkPidResponse.exit_code, 0, `Child process ${childPidToWatch} should NOT be running (ps exit code: ${checkPidResponse.exit_code})`);
        }

        console.log('[Test] test_stop_command_tree_kill.js PASSED');

    } catch (error) {
        console.error('[Test] test_stop_command_tree_kill.js FAILED:', error);
        if (childPidToWatch) console.error(`[Test] Child PID was: ${childPidToWatch}`);
        // Attempt to clean up if parent is still tracked, in case of test failure mid-way
        if (parentPid && client.isConnected) {
            try {
                console.log(`[Test] Attempting cleanup: stopping parent PID ${parentPid} if test failed.`);
                await client.tool(toolName, 'stop_terminal_command', { pids: [parentPid] });
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