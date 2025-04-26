# ToDo

## 7. Repository Cleanup

7.1. [x] **Track MCP Commit Server Files**:
    - Description: Add the `.cursor/mcp/` directory (containing the server code, dependencies, and configuration) and the `.cursor/mcp.json` template file to git tracking using `git add`. Verify they are staged correctly.
    - Impacted Files: `.gitignore`, `.cursor/mcp/`, `.cursor/mcp.json`
    - Dependencies: None
    - Validation: `git status` showed the files/directory as staged for commit. (Confirmed files were already tracked).

7.2. [x] **Analyze Root `mcp.json` and `tools/` Directory**:
    - Description: Re-evaluate the purpose of the root `mcp.json` file (previously thought required by `install.sh`) and the `tools/` directory. Determine if they are essential, contain generated binaries, or are remnants of development/testing that should be removed or added to `.gitignore`.
    - Impacted Files: `mcp.json`, `tools/`, `install.sh`, `.gitignore`
    - Dependencies: Understanding of `install.sh` logic.
    - Validation: Root `mcp.json` confirmed obsolete/non-existent and deleted/absent. `tools/` directory confirmed absent.

7.3. [x] **Delete Temporary Log Files**:
    - Description: Remove the temporary/backup log files identified in the `tests/` directory (`exit_codes.log[201~`, `exit_codes.log~`).
    - Impacted Files: `tests/exit_codes.log[201~`, `tests/exit_codes.log~`
    - Dependencies: None
    - Validation: Specified temporary log files confirmed absent in `tests/`.

7.4. [x] **Delete Root node_modules and tmp Directories**:
    - Description: Remove potentially generated `node_modules` and `tmp` directories from the project root.
    - Impacted Files: `node_modules/`, `tmp/`
    - Dependencies: None
    - Validation: Directories successfully deleted using `rm -rf`.

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

## 10. Rule Modification for MCP Debug Usage

10.1. [x] **Modify fix.mdc**: Add logic to step 2.2 to encourage using the MCP `Debug` tool under specific conditions (uncertainty, 3rd iteration failure, complexity, lack of understanding) and update the Specifics section to prioritize it over logging.
    - Actions: Edit `fix.mdc`.
    - Files: `.cursor/rules/fix.mdc`
    - Dependencies: MCP `Debug` tool available.
    - Validation: The rule includes prompts for using the Debug tool and updated Specifics section.

