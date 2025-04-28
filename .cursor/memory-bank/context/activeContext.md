# Active Context

## Current Goal
Fixed `consult_image` MCP tool (previously crashed on large images).

## Summary of Fix
- Identified `Maximum call stack size exceeded` error when returning large base64 image data.
- Attempting to return file path caused MCP schema validation errors.
- **Solution:** Implemented server-side image processing using the `sharp` library.
  - Added `sharp` to MCP server dependencies (`package.json`) and ran `npm install`.
  - Modified `consult_image.js` to resize (max 1024px width) and compress (JPEG quality 80) the image *before* base64 encoding.
- Successfully tested with the large `tests/assets/image.png`, resolving the crash.

## Current implementation context
-   **Task:** Modify `consult_image` handler and server registration.
-   **Approach:** Mimic `execute_command` parameter handling.
    1.  Modify handler (`consult_image.js`) to accept optional `working_directory` in params.
    2.  Use `working_directory` if provided, else fallback to `process.cwd()` (expected to be wrong in MCP calls).
    3.  Use `path.join(cwd_to_use, params.path)` for path resolution.
    4.  Update server schema (`server.js`) to include optional `working_directory` string parameter.
    5.  Keep direct handler reference (`handleConsultImage`) in server registration.
    6.  Update test script (`test_consult_image.js`) to pass `working_directory: projectRootForTest` in params.
-   **Hypothesis:** Avoids wrapper function (stack overflow source). Relies on MCP environment providing correct `working_directory` implicitly, fixing path issues.
-   **Files to Modify:** `consult_image.js`, `server.js`, `test_consult_image.js`.

## Previous Context (Preserved)
- Strengthened `experience-execution` rule analysis (Steps 3 & 4.1) using a `.mdc` -> `.md` -> `.mdc` rename workaround to ensure Git detection.
- Modified `experience-execution` rule error handling (Step 6) to call `task-decomposition` instead of `fix`.
- Verified `mcp_MyMCP_stop_terminal_command`.
- Debugged `MODULE_NOT_FOUND` error with `mcp-commit-server` in `trail-rag-article` repo.