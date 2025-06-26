# MCP Terminal Tools - User Guide

## Overview

The MCP Terminal Tools provide three main functions for executing and monitoring terminal commands:

1. **`execute_command`** - Execute a command and get immediate results
2. **`get_terminal_output`** - Retrieve output from a running or completed process
3. **`get_terminal_status`** - Check the status of all tracked processes

## Understanding Output Behavior

### execute_command

Always returns the command output immediately:
- For **completed commands** (within timeout): Returns full stdout/stderr
- For **running commands** (timeout exceeded): Returns partial output available at timeout

```javascript
// Example: Quick command
execute_command({ command: "echo Hello", timeout: 5 })
// Returns: { pid: 1234, status: "Success", stdout: "Hello\n", stderr: "" }

// Example: Long command with timeout
execute_command({ command: "long_running_task", timeout: 2 })
// Returns: { pid: 1234, status: "Running", stdout: "partial output...", stderr: "" }
```

### get_terminal_output

Has two modes of operation:

#### Default Mode (from_beginning: false)
- Returns **NEW** output since the last call to `get_terminal_output` for the same PID
- Uses internal read indices to track what has been read
- Subsequent calls return only additional output

```javascript
// First call after execute_command
get_terminal_output({ pid: 1234 })
// Returns: { stdout: "", stderr: "" } // Empty because execute_command already read it

// During a running process
get_terminal_output({ pid: 1234 })
// Returns: { stdout: "new output since last call", stderr: "" }
```

#### Full Output Mode (from_beginning: true)
- Returns **ALL** output from the beginning of the process
- Ignores read indices, always reads the complete log files
- Useful when you need the complete output history

```javascript
get_terminal_output({ pid: 1234, from_beginning: true })
// Returns: { stdout: "complete output from start", stderr: "complete errors" }
```

### get_terminal_status

Always shows the last portion of output for all tracked processes:
- Returns up to 1500 characters from the end of each log
- Provides a snapshot view of all processes
- Does not affect read indices used by `get_terminal_output`

## Common Usage Patterns

### Pattern 1: Quick Commands
```javascript
// For commands that complete quickly
const result = await execute_command({ command: "ls -la", timeout: 10 });
// Result contains all output immediately
```

### Pattern 2: Long-Running Commands
```javascript
// Start a long command with short timeout
const result = await execute_command({ 
    command: "npm install", 
    timeout: 5 
});

if (result.status === "Running") {
    // Monitor progress
    const status = await get_terminal_status({ timeout: 10 });
    
    // Get new output since execute_command
    const newOutput = await get_terminal_output({ 
        pid: result.pid,
        from_beginning: false 
    });
    
    // Or get complete output
    const fullOutput = await get_terminal_output({ 
        pid: result.pid,
        from_beginning: true 
    });
}
```

### Pattern 3: Monitoring Multiple Processes
```javascript
// Check all running processes
const status = await get_terminal_status({ timeout: 0 });
console.log(`Found ${status.terminals.length} processes`);

// Get full output for each
for (const terminal of status.terminals) {
    const output = await get_terminal_output({ 
        pid: terminal.pid,
        from_beginning: true 
    });
    console.log(`Process ${terminal.pid}: ${output.stdout}`);
}
```

## Troubleshooting

### "get_terminal_output returns empty"
This is normal behavior when:
- The process has already completed and `execute_command` returned all output
- You're using default mode (`from_beginning: false`) and there's no new output
- **Solution**: Use `from_beginning: true` to get complete output

### "Output seems truncated"
- `execute_command` limits output during timeout (1500 chars)
- `get_terminal_output` limits incremental reads (20000 chars)
- `get_terminal_status` shows last 1500 chars
- **Solution**: Use `get_terminal_output` with `from_beginning: true` for complete output

### "Process not found"
- Processes are automatically cleaned up when using `reuse_terminal: true`
- Old processes may be removed from tracking
- **Solution**: Check `get_terminal_status` first to see available processes

## Best Practices

1. **Use appropriate timeouts**: Start with short timeouts (5-10s) for `execute_command`
2. **Monitor long processes**: Use `get_terminal_status` to check if processes are still running
3. **Get complete output when needed**: Use `from_beginning: true` for full command history
4. **Handle both success and timeout cases**: Check the `status` field in responses
5. **Clean up**: Let `reuse_terminal: true` handle cleanup automatically 