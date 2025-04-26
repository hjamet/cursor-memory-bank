# Active Context

## Current Status
- **Last Action**: Analyzed user request regarding `install.sh` failures.
- **Outcome**: Identified specific issues in `install.sh`: MCP server copy logic (git mode), permission setting commands (`find -exec chmod`), and `mcp.json` path handling fallback (relative path without `jq`).
- **Next Step**: Implement tasks from section 1: "Installation Script Verification & Fixes" in `tasks.md`.

## Current Implementation Context
- **Task Section**: 1. Installation Script Verification & Fixes
- **Tasks**:
    - **1.1 Fix `install.sh` MCP Path/Name Issues**: Already addressed (server name is "Commit", relative path fallback is expected without jq). Focus is now on other issues.
    - **1.2 Implement Installation for Memory, Context7, Debug Servers**: Refine logic in `install_rules` (git mode) to *not* attempt copying files for these servers, as they don't exist in the repo and are defined via `npx`/`url` in `mcp.json`. The existing `warn` is correct but redundant if the copy isn't attempted.
    - **1.3 Verify `install.sh` Server Copy & Path Logic**: This overlaps with fixing the permission issues found during analysis. Refine permission setting in `install_rules` (lines ~446-459) to avoid `find -exec chmod u+x` which causes errors in MINGW64. Ensure `u+rw` is set, and specifically `u+x` for `server.js` if necessary (though likely not, as it's run via `node`). Add better error checking (`|| warn ...`) to chmod commands.
- **Goal**: Make `install.sh` robustly handle MCP server installation (copying only necessary files) and permission setting across different environments (especially MINGW64), ensuring `mcp.json` path handling is correct (absolute with jq, relative fallback without).
- **Impacted Files**: `install.sh`
- **Impacted Symbols**: `install_rules` (specifically the git mode MCP server loop and the permission setting loop).
- **Dependencies**: Bash scripting, `chmod`, `find` (potential issues), `jq` (optional for absolute paths).
- **Online Research**: Confirmed `chmod` limitations and potential issues with `find -exec` in MINGW64. Simpler `chmod` or relying on Node.js execution might be better.
- **Decisions**:
    - Skip `cp -r` for non-commit servers in git mode.
    - Replace `find -exec chmod u+x` with simpler/safer permission logic.