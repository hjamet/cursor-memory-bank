# ToDo

## 1. Diagnose Node.js Path Issue in MINGW64
- [x] **1.1 Verify Basic Node Execution**: Confirm Node.js itself runs correctly in the MINGW64 environment outside the problematic script.
    - *Description*: Run simple Node commands (`node -v`, `node -e "console.log(process.cwd())"`) directly in the MINGW64 terminal within the `trail-rag-article` repo root.
    - *Impacted Files/Components*: None (Environment verification).
    - *Dependencies*: MINGW64 environment, Node.js installation.
    - *Validation Criteria*: Commands execute without error and show expected output (version, correct CWD).
- [x] **1.2 Test Path Resolution**: Test Node.js path resolution with different path formats (Windows vs POSIX) directly.
    - *Description*: Use `node -e "console.log(require.resolve('C:\\path\\to\\server.js'))"` and `node -e "console.log(require.resolve('/c/path/to/server.js'))"` (using the actual path) to see if Node can resolve the script path correctly in MINGW64.
    - *Impacted Files/Components*: None (Node.js behavior test).
    - *Dependencies*: MINGW64 environment, Node.js installation, Target script path.
    - *Validation Criteria*: `require.resolve` either succeeds or fails consistently, providing insight into path format handling. (Result: Windows path OK, POSIX path fails)
- [x] **1.3 Isolate `--cwd` Argument**: Test running the script *without* the `--cwd` argument to see if it influences the initial path mangling error.
    - *Description*: Run `node C:\Users\Jamet\code\trail-rag-article\trail-rag\.cursor\mcp\mcp-commit-server\server.js` from the `trail-rag-article` root in MINGW64.
    - *Impacted Files/Components*: `server.js` execution.
    - *Dependencies*: MINGW64 environment, Node.js installation, Installed `mcp-commit-server`.
    - *Validation Criteria*: Observe if the error changes from the mangled path error to something else (e.g., the ESM import error, or a different error if CWD is required internally). (Result: Mangled path error gone, ESM import error appears).
- [x] **1.4 Investigate SDK Import Path**: Examine the `@modelcontextprotocol/sdk` package structure and `package.json` to understand why `server.js` might be trying to import from `dist/esm/server/mcp.js` and why it fails.
    - *Description*: Check the `node_modules/@modelcontextprotocol/sdk/package.json` (specifically the `exports` field) and the actual file structure within `dist/`.
    - *Impacted Files/Components*: `node_modules/@modelcontextprotocol/sdk`.
    - *Dependencies*: Installed `mcp-commit-server`.
    - *Validation Criteria*: Understanding of the intended module structure and potential mismatches with the import path used. (Result: `exports` map confirms `dist/esm/` path for imports is correct).

## 2. Potential Fixes (Pending Diagnosis)
- [ ] **2.1 Adjust Script Invocation**: Based on diagnosis, modify how `node server.js` is called (e.g., use POSIX paths, adjust arguments, run from a different directory).
    - *Description*: This depends heavily on findings from section 1.
    - *Impacted Files/Components*: Invocation method (potentially `.cursor/mcp.json` generation in `install.sh` or direct command execution).
    - *Dependencies*: Diagnosis results.
    - *Validation Criteria*: Script runs without `MODULE_NOT_FOUND` errors.
- [ ] **2.2 Modify `server.js` Imports/Path Handling**: If the issue is internal to the script or SDK interaction, adjust how paths or modules are handled within `server.js`.
    - *Description*: Could involve changing `import` statements or how `__dirname` / `path.resolve` are used.
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/server.js` (and potentially its dependencies).
    - *Dependencies*: Diagnosis results.
    - *Validation Criteria*: Script runs without `MODULE_NOT_FOUND` errors.

# In Progress

# Done

## 1. MCP Server Enhancement
- [x] **1.1 Implement Process Tree Killing**: Modify the `killProcess` function in the MCP server to terminate the entire process tree (parent and children) associated with a given PID.
    - *Description*: The current `process.kill` only terminates the parent. Research and implement a cross-platform solution, potentially using the `fkill` npm package.
    - *Impacted Files/Components*: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, `.cursor/mcp/mcp-commit-server/package.json` (add dependency).
    - *Dependencies*: None (external library `fkill` to be added).
    - *Validation Criteria*: A test case involving starting a parent process (e.g., bash script) that spawns a child process (e.g., python script `sleep(30)`), then stopping the parent PID via `mcp_MyMCP_stop_terminal_command`, should result in both parent and child processes being terminated (verified via OS tools like `tasklist` or `ps`).

## 2. Rule Enhancement
- [x] **2.1 Update experience-execution Rule**: Modify the `experience-execution.mdc` rule to incorporate an incremental timeout strategy for monitoring long-running commands.
    - *Description*: The rule should guide the agent to initially check command status/output with a short timeout (e.g., 20 seconds) using `mcp_MyMCP_get_terminal_status` or `mcp_MyMCP_get_terminal_output`, then progressively increase the timeout for subsequent checks, ensuring no single timeout exceeds ~5 minutes.
    - *Impacted Files/Components*: `.cursor/rules/experience-execution.mdc`.
    - *Dependencies*: None.
    - *Validation Criteria*: Manual review of the updated rule instructions to ensure they clearly describe the incremental timeout strategy.
