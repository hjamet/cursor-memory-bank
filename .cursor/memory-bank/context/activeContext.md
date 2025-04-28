# Active Context

## Current Goal
Commit changes for MCP server process tree killing and `experience-execution` rule update.

## Current implementation context
- **Task Completed**: 1.1 Implement Process Tree Killing
    - Added `fkill` dependency to `package.json`.
    - Installed dependencies.
    - Modified `lib/process_manager.js` to use `fkill(pid, { force: true, tree: true, ... })` instead of `process.kill`.
    - Verified with parent/child script test that killing parent terminates child.
- **Task Completed**: 2.1 Update experience-execution Rule
    - Modified `.cursor/rules/experience-execution.mdc` instructions (Step 2) to detail incremental timeout strategy for monitoring long-running commands.
- **Files Involved**: `.cursor/mcp/mcp-commit-server/lib/process_manager.js`, `.cursor/mcp/mcp-commit-server/package.json`, `.cursor/rules/experience-execution.mdc`, `child_sleep.py` (test script), `parent_spawner.sh` (test script), `.cursor/memory-bank/workflow/tests.md` (updated).
- **Status**: Implementation and testing complete for both tasks.

## Lost workflow - 2024-MM-DD HH:MM:SS
I lost track of the workflow after addressing a user request. The actions taken were:
- Diagnosed a Node.js `MODULE_NOT_FOUND` error in `install.sh` occurring when used in a different repository. The root cause seemed to be incorrect absolute path calculation for the server script within the target directory, especially in MINGW64 environments.
- Modified the `merge_mcp_json` function in `install.sh` to refine absolute path determination and Windows path conversion logic (`cygpath`/manual).
- Added a new optional `--visible-mcp` flag to `install.sh` to allow launching the `MyMCP` server with a visible console window on Windows.
- Modified `merge_mcp_json` in `install.sh` to add `"--visible"` to the `MyMCP.args` array in the generated `.cursor/mcp.json` when the `--visible-mcp` flag is used.
- Modified `.cursor/mcp/mcp-commit-server/lib/process_manager.js` to check for the `"--visible"` argument in `process.argv` and set the `windowsHide` spawn option to `false` if present on Windows.
- Updated `README.md` to add documentation for the `--visible-mcp` flag and remove an obsolete troubleshooting section related to manually copying MCP server files.

Files involved:
- `install.sh`
- `.cursor/mcp/mcp-commit-server/lib/process_manager.js`
- `README.md`
- `.cursor/mcp.json` (modified in target repo by `install.sh`, and potentially locally for testing)

Next step is to identify the correct rule to resume the workflow.