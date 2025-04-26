# In Progress

# ToDo


# Done

## 8. MCP Server Installation Logic

8.1. [x] **Modify install.sh for Local MCP Config**: Update `install.sh` to copy MCP server files to the local installation target directory and configure the local `.cursor/mcp.json` with the absolute path to the installed `server.js`.
    - Description: Ensure `install.sh` copies `.cursor/mcp/mcp-commit-server/` source files to `$INSTALL_DIR/.cursor/mcp/mcp-commit-server/`. Modify `merge_mcp_json` to calculate the absolute path of the installed `server.js` and use `jq` to update the temporary template JSON with this path before copying/merging it into `$INSTALL_DIR/.cursor/mcp.json`.
    - Impacted Files: `install.sh`
    - Dependencies: `jq` command.
    - Validation: Running `install.sh` creates/updates `.cursor/mcp.json` in the target directory with an absolute path in the server arguments.

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

## 5. MCP Server Testing

5.1. [x] **Test MCP commit server functionality**:
    - Description: Execute the MCP commit server script (`node .cursor/mcp/mcp-commit-server/server.js`) using the `timeout` command (e.g., `timeout 60s node ...`) to ensure it runs correctly and exits if it hangs. Verify it can be started and potentially interact with it if possible via MCP tooling (if available).
    - Impacted Files: `.cursor/mcp/mcp-commit-server/server.js`
    - Dependencies: Node.js installed (v22.14.0 confirmed by user), `timeout` command available (or alternative).
    - Validation: The server script starts without immediate errors when run via `timeout` (exits with code 124 as expected) and logs connection success. Import paths in `server.js` were corrected to use documented subpaths (`@modelcontextprotocol/sdk/server/...`).

## 1. MCP Memory Server Update

1.1. [x] **Test New `memory` MCP Server**:
    - Description: Explore and test the functionalities of the newly added `memory` MCP server to understand its capabilities (e.g., adding, searching, deleting data).
    - Impacted Files/Components: New `memory` MCP server tools (e.g., `mcp_memory_...`)
    - Dependencies: None
    - Validation: A clear understanding of how to use the `memory` server tools is documented or readily available for the next step.

1.2. [x] **Update Rules to Use `memory` Server**:
    - Description: Modify the `fix` and `request-analysis` rules (and any others using the old system) to replace calls to `supermemory` or `mcp_servers_*` with the equivalent calls to the new `memory` server tools.
    - Impacted Files: `.cursor/rules/fix.mdc`, `.cursor/rules/request-analysis.mdc` (potentially others)
    - Dependencies: Task 1.1 (understanding the server)
    - Validation: Rules correctly use the `memory` server tools for their intended purpose (e.g., storing fix details, retrieving context).

## 2. Installation Script Enhancement

2.1. [x] **Create `.cursor/mcp.json` Template**:
    - Description: Create a new file `.cursor/mcp.json` in the root of this repository. This file will serve as a template containing default MCP server definitions (e.g., the commit server) that should be available after installation.
    - Impacted Files: `.cursor/mcp.json` (new file)
    - Dependencies: None
    - Validation: The `.cursor/mcp.json` file exists and contains valid JSON with necessary default server definitions.

2.2. [x] **Update `install.sh` for `mcp.json` Merging**:
    - Description: Modify the `install.sh` script. Instead of potentially overwriting an existing `.cursor/mcp.json` in the target installation directory, the script should download the template `.cursor/mcp.json` from this repo and merge its contents with the existing file. The merge logic should add new server definitions from the template if they don't already exist in the target file, preserving existing definitions.
    - Impacted Files: `install.sh`
    - Dependencies: Task 2.1 (template file creation)
    - Validation: Running `install.sh` correctly merges the template `.cursor/mcp.json` with a pre-existing `.cursor/mcp.json` file, adding new entries without removing old ones. If no file exists, the template is copied.

## 3. Rule Refinement

3.1. [x] **Simplify `fix` rule debugging logic**:
    - Description: Modify step 2 of the `fix` rule. Introduce a binary choice for the model: if unsure about the problem's origin, use debugging alongside attempting a solution.
    - Impacted Files: `.cursor/rules/fix.mdc`
    - Dependencies: None
    - Validation: The `fix` rule incorporates the simplified debugging decision logic.

## 4. File Structure Investigation

4.1. [x] **Investigate duplicate `mcp.json` files**:
    - Description: Analyze the presence and purpose of `mcp.json` at the root and in `.cursor/`. Determine if the root file is redundant.
    - Impacted Files: `mcp.json`, `.cursor/mcp.json`, `install.sh`
    - Dependencies: None
    - Validation: Conclusion reached that the root `mcp.json` is required by `install.sh` and should not be removed without script modification. Status documented.

## 6. Rule Refinement (Parallel Debug)

6.1. [x] **Refine `fix` rule for parallel debugging/implementation**:
    - Description: Modify the `fix.mdc` rule (specifically step 2.4) to allow the agent to attempt an implementation concurrently while debugging is active, if uncertainty about the error cause triggered the debugging step.
    - Impacted Files: `.cursor/rules/fix.mdc`
    - Dependencies: Task 3.1 (previous simplification) might be relevant context.
    - Validation: The `fix` rule text clearly instructs the agent to attempt implementation in parallel with debugging when uncertainty exists.

