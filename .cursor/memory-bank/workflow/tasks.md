# In Progress

## 1. Installation Script Verification & Fixes

1.1. **Fix `install.sh` MCP Path/Name Issues**:
    - Status: Done (Server name "Commit" is correct; relative path fallback without `jq` is expected behavior and warned.)
    - Description: Investigate and fix why `install.sh` sets a relative path for the commit server in `.cursor/mcp.json` when `jq` is not available (user expects absolute) and why it might have used an incorrect name ("MonServeurTest" instead of "Commit"). Ensure the script uses the correct server name ("Commit") and handles the path issue gracefully, potentially by adding a clear warning or requiring `jq`. Update `expected_key_name` in `merge_mcp_json` from "Git Commit (Internal)" to "Commit".
    - Impacted Files: `install.sh`, `.cursor/mcp.json`
    - Dependencies: `jq` (optional), Understanding of shell scripting and `mcp.json` format.
    - Validation: Running `install.sh --use-curl` without `jq` results in `.cursor/mcp.json` with the correct server name "Commit" and a relative path, accompanied by a clear warning about the path. Running with `jq` results in an absolute path.

1.2. **Implement Installation for Memory, Context7, Debug Servers**:
    - Status: Done (Analysis complete - copy logic correctly warns about missing source dirs, which is expected for these servers; permission logic fixed in 1.3)
    - Description: Update `install.sh` to correctly handle the installation of the `memory`, `context7`, and `debug` MCP servers defined in `.cursor/mcp.json`. For `git` mode, ensure source directories are expected. For `curl` mode, implement download/installation logic (likely using `npx` commands specified in `mcp.json`). Consider if these servers require specific files to be copied/downloaded or if `npx` handles it.
    - Impacted Files: `install.sh`
    - Dependencies: `.cursor/mcp.json` definitions, `npx` availability.
    - Validation: Running `install.sh` (both git and curl modes) results in a functional setup where the memory, context7, and debug servers can be invoked via MCP.

1.3. **Verify `install.sh` Server Copy & Path Logic & Fix Permissions**:
    - Status: In Progress (Attempting fix 4 for persistent MINGW64/curl permission error)
    - Description: Double-check server file copy logic. Fix persistent permission errors (`: command not found`) during `curl | bash` in MINGW64. Latest attempt involves simplifying the permission loop structure to avoid conditionals/warnings.
    - Impacted Files: `install.sh` (`install_rules` permission loop)
    - Dependencies: MINGW64 environment for testing.
    - Validation: Running `install.sh` via `curl | bash` in MINGW64 no longer produces `: command not found` errors during permission setting.

## 2. Component Verification

2.1. **Verify MCP Commit Usage in Rules**:
    - Description: Double-check that `context-update.mdc` and `fix.mdc` correctly use the "Commit" MCP tool instead of direct `git` commands, as previous `tasks.md` edits failed.
    - Impacted Files: `.cursor/rules/context-update.mdc`, `.cursor/rules/fix.mdc`
    - Dependencies: MCP Commit server definition.
    - Validation: Rules use the `mcp_server_tool` command with the correct server name ("Commit") and arguments.

2.2. **Verify MCP Debug Usage in `fix` Rule**:
    - Description: Double-check that `fix.mdc` encourages the use of the MCP Debug tool under the specified conditions, as previous `tasks.md` edits failed.
    - Impacted Files: `.cursor/rules/fix.mdc`
    - Dependencies: MCP Debug server definition.
    - Validation: The rule text contains the logic described in the user request.

2.3. **Verify Commit Server Implementation**:
    - Description: Confirm that the current `.cursor/mcp/mcp-commit-server/server.js` matches the user's final requirement (accepts type, emoji, title, description; performs `git add .` and `git commit`).
    - Impacted Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: Node.js environment.
    - Validation: Code review confirms the implementation matches the specification.

## 3. Repository Cleanup

3.1. **Cleanup Test Logs**:
    - Description: Review the `.log` files in the `tests/` directory (`exit_codes.log`, `test_*.log`). Decide whether to delete them or add them to `.gitignore`.
    - Impacted Files: `tests/*.log`, `.gitignore`
    - Dependencies: None
    - Validation: Log files are either removed or ignored by git.

3.2. **General Repository Cleanup Review**:
    - Description: Perform a final review of the repository structure, removing any remaining unnecessary files (e.g., leftover test artifacts, logs not covered by specific tasks) and ensuring all necessary components are tracked by git. Add necessary entries to `.gitignore`.
    - Impacted Files: Various (potentially `tests/`, root), `.gitignore`
    - Dependencies: Completion of other cleanup tasks.
    - Validation: Repository contains only necessary files for operation and development, reflected in `.gitignore`.

# Done

## 9. Rule Modification for MCP Commit

9.1. [x] **Modify context-update.mdc**: Replace the `git commit -a` command in step 4 with a call to the "Commit" MCP tool, using appropriate arguments (type, emoji, title, description).
    - Actions: Edit `context-update.mdc`.
    - Files: `.cursor/rules/context-update.mdc`
    - Dependencies: MCP "Commit" server operational and correctly named.
    - Validation: The rule instructs to use the MCP tool instead of the git command.

9.2. [x] **Modify fix.mdc**: Replace the `git commit -m` command in step 2.5.2 (quick commit) with a call to the "Commit" MCP tool, using appropriate arguments (type=:wrench:, emoji=:bug:, title derived from test name, description=quick fix).
    - Actions: Edit `fix.mdc`.
    - Files: `.cursor/rules/fix.mdc`
    - Dependencies: MCP "Commit" server operational and correctly named.
    - Validation: The rule instructs to use the MCP tool instead of the git command for quick commits.

## 8. MCP Server Installation Logic

8.1. [x] **Modify install.sh for Local MCP Config**: Update `install.sh` to copy MCP server files to the local installation target directory and configure the local `.cursor/mcp.json` with the absolute path to the installed `server.js`.
    - Description: Ensure `install.sh` copies `.cursor/mcp/mcp-commit-server/` source files to `$INSTALL_DIR/.cursor/mcp/mcp-commit-server/`. Modify `merge_mcp_json` to calculate the absolute path of the installed `server.js` and use `jq` to update the temporary template JSON with this path before copying/merging it into `$INSTALL_DIR/.cursor/mcp.json`.
    - Impacted Files: `install.sh`
    - Dependencies: `jq` command.
    - Validation: Running `install.sh` creates/updates `.cursor/mcp.json` in the target directory with an absolute path in the server arguments.

