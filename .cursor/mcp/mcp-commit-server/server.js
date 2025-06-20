import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import process from 'process';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determine project root (assuming server.js is in .cursor/mcp/mcp-commit-server/)
const projectRoot = path.resolve(__dirname, '../../..');

// Import library modules
import * as StateManager from './lib/state_manager.js';
// import * as Logger from './lib/logger.js'; // Not directly needed in server.js anymore
// import * as ProcessManager from './lib/process_manager.js'; // Not directly needed

// Import tool handlers
import { handleExecuteCommand } from './mcp_tools/terminal_execution.js';
import { handleGetTerminalStatus } from './mcp_tools/terminal_status.js';
import { handleGetTerminalOutput } from './mcp_tools/terminal_output.js';
import { handleStopTerminalCommand } from './mcp_tools/terminal_stop.js';
import { handleConsultImage } from './mcp_tools/consult_image.js';
import { handleWebpageScreenshot } from './mcp_tools/webpage_screenshot.js';
import { regexEditTool } from './mcp_tools/regex_edit.js';

// --- State Persistence and Logging Setup --- START ---
const LOGS_DIR = path.join(__dirname, 'logs');
const STATE_FILE = path.join(__dirname, 'terminals_status.json');
let terminalStates = []; // In-memory store for terminal statuses

/**
 * Function to ensure logs directory exists
 */
function ensureLogsDirExists() {
    if (!fs.existsSync(LOGS_DIR)) {
        try {
            fs.mkdirSync(LOGS_DIR, { recursive: true });
        } catch (err) {
            console.error(`[MyMCP Setup] Error creating logs directory ${LOGS_DIR}:`, err);
            // Decide if this is fatal - for now, log and continue, 
            // subsequent log writes will likely fail.
        }
    }
}

/**
 * Ensure logs directory exists on startup
 */
// ensureLogsDirExists(); // Moved into execute_command handler

/**
 * Reads the terminal state from the JSON file.
 * Initializes with an empty array if the file doesn't exist or is invalid.
 */
function loadTerminalState() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            const fileContent = fs.readFileSync(STATE_FILE, 'utf8');
            terminalStates = JSON.parse(fileContent);
            // Basic validation (check if it's an array)
            if (!Array.isArray(terminalStates)) {
                console.error(`Invalid state file format in ${STATE_FILE}. Expected an array. Resetting state.`);
                terminalStates = [];
            }
            // console.log(`Loaded terminal state from ${STATE_FILE}`); // Optional: for debugging
        } else {
            terminalStates = [];
            // console.log(`State file ${STATE_FILE} not found. Initializing empty state.`); // Optional
        }
    } catch (error) {
        console.error(`Error reading or parsing state file ${STATE_FILE}:`, error);
        terminalStates = []; // Reset state on error
    }
}

/**
 * Writes the current terminal state to the JSON file.
 * @param {Array} state The state array to write.
 */
function writeTerminalState(state) {
    try {
        const fileContent = JSON.stringify(state, null, 2); // Pretty print JSON
        fs.writeFileSync(STATE_FILE, fileContent, 'utf8');
        // console.log(`Wrote terminal state to ${STATE_FILE}`); // Optional: for debugging
    } catch (error) {
        console.error(`Error writing state file ${STATE_FILE}:`, error);
    }
}

// --- State Persistence and Logging Setup --- END ---

// --- Background Status Monitor --- START ---
let statusMonitorInterval = null;

/**
 * Checks the status of running processes and updates the state file.
 * This is a polling mechanism and mainly detects if a process previously marked
 * as 'Running' no longer exists. It doesn't reliably capture exit codes immediately.
 */
async function updateRunningProcessStatuses() {
    // console.log('Running status check...'); // Optional: for debugging
    let stateChanged = false;
    const currentStates = [...terminalStates]; // Work on a copy

    for (const state of currentStates) {
        if (state.status === 'Running') {
            try {
                // process.kill with signal 0 tests if the process exists
                const isRunning = process.kill(state.pid, 0);
                // If kill returns true, the process exists. We don't know if it *just* exited.
                // Polling isn't perfect for immediate exit detection.
            } catch (error) {
                // If error is ESRCH, the process doesn't exist anymore
                if (error.code === 'ESRCH') {
                    // console.log(`Process ${state.pid} (${state.command}) no longer running.`); // Optional
                    state.status = 'Stopped'; // Or potentially 'Failure', but we don't know exit code here
                    state.exit_code = state.exit_code ?? null; // Keep existing exit code if set by 'exit' event, else null
                    state.endTime = state.endTime ?? new Date().toISOString();
                    stateChanged = true;
                } else if (error.code === 'EPERM') {
                    // Process exists, but we lack permissions to send signals.
                    // Should not happen for child processes spawned by us, but log it.
                    console.warn(`Permission error checking status for PID ${state.pid}. Assuming it's still running.`);
                } else {
                    // Other unexpected error
                    console.error(`Error checking status for PID ${state.pid}:`, error);
                }
            }
        }
    }

    if (stateChanged) {
        // console.log('Detected status changes, writing state file.'); // Optional
        writeTerminalState(currentStates);
        terminalStates = currentStates; // Update in-memory state
    }
}
// --- Background Status Monitor --- END ---

const execAsync = promisify(exec);

// Helper function to escape shell arguments safely
// Escapes double quotes, dollar signs, backticks, and backslashes
const escapeShellArg = (arg) => {
    if (arg === null || arg === undefined) {
        return '';
    }
    // 1. Replace backslash with double backslash
    // 2. Replace dollar sign with backslash-dollar sign
    // 3. Replace double quote with backslash-double quote
    // 4. Replace backtick with backslash-backtick
    return arg
        .replace(/\\/g, '\\\\')
        .replace(/\$/g, '\\$')
        .replace(/"/g, '\\"')
        .replace(/`/g, '\\`');
};

// Create an MCP server instance
const server = new McpServer({
    name: "InternalAsyncTerminal",
    version: "0.6.0", // Incremented version for new tool
    capabilities: {
        tools: {
            'execute_command': true,
            'get_terminal_status': true,
            'get_terminal_output': true,
            'stop_terminal_command': true,
            'consult_image': true,
            'take_webpage_screenshot': true,
            'regex_edit': true
        }
    }
});

// --- Register Tools --- 

// Define execute_command tool schema (as before)
server.tool(
    'execute_command',
    {
        command: z.string().describe("The command line to execute."),
        reuse_terminal: z.boolean().optional().default(true).describe("If true (default), attempts to clean up one finished terminal state before spawning a new process. Otherwise, always spawns without cleanup."),
        timeout: z.number().int().optional().default(10).describe("Maximum time in seconds to wait for the command to complete before returning. The command continues in the background if timeout is reached. Enforced maximum is 300 seconds (5 minutes). I recommend using a timeout of 10 seconds, then using the 'get_terminal_status' tool to monitor the process with longer timeouts.")
    },
    handleExecuteCommand // Use the imported handler
);

// Define get_terminal_status tool schema (as before)
server.tool(
    'get_terminal_status',
    {
        timeout: z.number().int().optional().default(0).describe("Maximum time in seconds to wait for any running process status to change before returning. 0 means return immediately. Enforced maximum is 300 seconds (5 minutes). I recommend starting with lower timeouts and increasing if necessary while monitoring the process to be able to interrupt it if needed.")
    },
    handleGetTerminalStatus // Use the imported handler
);

// Define get_terminal_output tool schema (as before)
server.tool(
    'get_terminal_output',
    {
        pid: z.number().int().describe("The PID of the terminal process to get output from."),
        lines: z.number().int().optional().default(100).describe("The maximum number of lines to retrieve from the end of each log (stdout, stderr).")
    },
    handleGetTerminalOutput // Use the imported handler
);

// Define stop_terminal_command tool schema (as before)
server.tool(
    'stop_terminal_command',
    {
        pids: z.array(z.number().int()).describe("An array of PIDs of the terminal processes to stop."),
        lines: z.number().int().optional().default(100).describe("The maximum number of lines to retrieve from the end of each log before stopping.")
    },
    handleStopTerminalCommand // Use the imported handler
);

// Define consult_image tool
server.tool(
    'consult_image',
    {
        path: z.string().describe("Relative path to the image file from the project root."),
        // Ensure working_directory schema is removed
    },
    handleConsultImage // Use direct handler reference
);

// Define take_webpage_screenshot tool
server.tool(
    'take_webpage_screenshot',
    {
        url: z.string().url().describe("URL of the webpage to capture.")
    },
    handleWebpageScreenshot
);

// Register regex_edit tool
server.tool(regexEditTool.name, regexEditTool.args, regexEditTool.run);

// --- Server Startup --- 

async function startServer() {
    // Load initial state from file using StateManager
    await StateManager.loadState();

    // Remove background status monitor? Decided against reimplementing polling for now.
    // Relying on process exit events handled in process_manager.js
    /*
    if (statusMonitorInterval) {
        clearInterval(statusMonitorInterval);
    }
    statusMonitorInterval = setInterval(updateRunningProcessStatuses, 1000);
    */

    try {
        const transport = new StdioServerTransport();
        await server.connect(transport);
        // console.log("[MCP Server] InternalAsyncTerminal Server v0.3.0 connected.");
    } catch (error) {
        console.error("[MCP Server] Failed to start MCP Commit Server:", error);
        process.exit(1);
    }
}

// Start the server
startServer();

process.on('uncaughtException', (error) => {
    console.error('[MCP Server] Uncaught Exception:', error);
    // Decide if the server should exit. For robustness, maybe not.
    // process.exit(1); // Optional: exit on uncaught exceptions
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('[MCP Server] Unhandled Rejection at:', promise, 'reason:', reason);
    // Decide if the server should exit. For robustness, maybe not.
    // process.exit(1); // Optional: exit on unhandled rejections
});

// Initial message to stdout indicates server is ready (removed to avoid JSON parse error)
// console.log("[MCP Server] InternalAsyncTerminal Server v0.3.0 connected."); 