# Active Context

## Current Status
- **Last Action**: Completed `test-execution` after fixing the MINGW64 curl permission issue.
- **Outcome**: All installation script tests pass. Tasks 1.3, 2.1, 2.2, and 2.3 are Done.
- **Next Step**: Start implementing Task 1.1 from the "In Progress" section.

## Current Implementation Context
- **Task Section**: Section 1: Installation Script Verification & Fixes.
- **Task**: 1.1. Fix `install.sh` MCP Path/Name Issues
- **Goal**: Modify `install.sh` to ensure the `.cursor/mcp.json` file in the installation directory contains the correct server name ("Commit") and an *absolute* path for the commit server's script, even when the `jq` command is not available.
- **Logic**:
    - In the `merge_mcp_json` function (or where the final `mcp.json` is prepared):
        - Check if `jq` is available (`command -v jq > /dev/null`).
        - If `jq` is available, use the existing logic to update the server name and path.
        - If `jq` is NOT available:
            - Copy the template `mcp.json` to the target location.
            - Use shell commands (e.g., `pwd`, `sed`, `awk`) to read the target `mcp.json`, calculate the absolute path to the installed commit server's `server.js`, and replace the placeholder path and potentially incorrect name ("mcp-commit-server" instead of "Commit") in the target file.
            - Ensure the final JSON remains valid.
- **Impacted Files**: `install.sh`
- **Impacted Symbols**: `merge_mcp_json` function (or related logic).
- **Dependencies**: Shell scripting (manipulating JSON with `sed`/`awk` requires care). `pwd` command availability.
- **Online Research**: Might need examples of reliable JSON manipulation using `sed` or `awk` without `jq`.
- **Decision**: Implement a fallback mechanism using `sed` or `awk` within the `install.sh` script for the no-`jq` scenario. Create a test case for this specific scenario.