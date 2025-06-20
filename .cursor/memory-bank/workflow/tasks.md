# Tasks

**Emoji Legend for Tasks:**
*   ⚪️ TODO
*   🟡 IN_PROGRESS
*   🟢 DONE
*   🔴 BLOCKED
*   🔵 REVIEW

---

🟢 **30. Refactor userbrief management to use JSON**
    *   **Description**: Refactor the entire userbrief management system to use a JSON file (`userbrief.json`) instead of the current Markdown file (`userbrief.md`). This will involve creating a new JSON schema, updating the I/O operations, and modifying the MCP tools (`read-userbrief`, `update-userbrief`) to work with structured JSON data and unique IDs instead of line numbers and emoji parsing.
    *   **Impacted Rules/Files**:
        *   `.cursor/mcp/memory-bank-mcp/lib/userbrief_manager.js`
        *   `.cursor/mcp/memory-bank-mcp/mcp_tools/read_userbrief.js`
        *   `.cursor/mcp/memory-bank-mcp/mcp_tools/update_userbrief.js`
        *   `.cursor/mcp/memory-bank-mcp/server.js`
        *   `.cursor/memory-bank/workflow/userbrief.json` (new file)
        *   `.cursor/memory-bank/userbrief.md` (to be deleted)
    *   **Dependencies**: None.
    *   **Validation**: The userbrief system operates entirely on `userbrief.json`. The `read-userbrief` and `update-userbrief` tools function correctly with the new JSON structure, using IDs for selection. The old `userbrief.md` file is removed.
    *   **Sub-Tasks**:
        *   🟢 **30.1. Create userbrief.json and schema**
            *   **Description**: Create a new `userbrief.json` file in `.cursor/memory-bank/workflow/` and define a JSON schema for it, similar to `tasks_schema.json`. The schema should include a `requests` array, where each request object has a unique `id`, `content`, `status` (`new`, `in_progress`, `archived`), and timestamps.
            *   **Impacted Rules/Files**: 
                *   `.cursor/memory-bank/workflow/userbrief.json` (new file)
                *   A new schema file or inline schema definition.
            *   **Dependencies**: None.
            *   **Validation**: `userbrief.json` is created with a valid structure. The schema is well-defined.
        *   🟢 **30.2. Refactor userbrief_manager.js for JSON I/O**
            *   **Description**: Modify all functions in `userbrief_manager.js` to read from and write to `userbrief.json`. Replace line-based operations with JSON object manipulation (e.g., finding, adding, updating requests by ID). The `USERBRIEF_PATH` constant should be updated to point to the new JSON file.
            *   **Impacted Rules/Files**: 
                *   `.cursor/mcp/memory-bank-mcp/lib/userbrief_manager.js`
            *   **Dependencies**: 30.1.
            *   **Validation**: The manager correctly reads, parses, and writes data to `userbrief.json`. All markdown-specific logic is removed.
        *   🟢 **30.3. Update read-userbrief tool**
            *   **Description**: Refactor `read_userbrief.js` to use the new JSON-based functions from the manager. It should find and return the current request (in-progress or new) and archived requests based on their status in the JSON file.
            *   **Impacted Rules/Files**: 
                *   `.cursor/mcp/memory-bank-mcp/mcp_tools/read_userbrief.js`
            *   **Dependencies**: 30.1.
            *   **Validation**: The tool correctly retrieves and returns request data from `userbrief.json`.
        *   🟢 **30.4. Update update-userbrief tool**
            *   **Description**: Refactor `update_userbrief.js` to use an `id` parameter instead of `line_number`. Update its logic to modify request objects in the `userbrief.json` file. If no `id` is provided, it should target the current request identified by the `read-userbrief` logic.
            *   **Impacted Rules/Files**: 
                *   `.cursor/mcp/memory-bank-mcp/mcp_tools/update_userbrief.js`
            *   **Dependencies**: 30.1.
            *   **Validation**: The tool correctly retrieves and returns request data from `userbrief.json`.
        *   🟢 **30.5. Update MCP Server Schemas**
            *   **Description**: In `server.js`, update the Zod schema for the `update-userbrief` tool to accept an optional `id` (number) instead of `line_number`.
            *   **Impacted Rules/Files**: 
                *   `.cursor/mcp/memory-bank-mcp/server.js`
            *   **Dependencies**: 30.4.
            *   **Validation**: The server registers the tool with the correct, updated schema.
        *   🟢 **30.6. Test the new userbrief implementation**
            *   **Description**: Create a test script or manually test the `read-userbrief` and `update-userbrief` tools to ensure they work as expected with the new JSON-based system.
            *   **Impacted Rules/Files**: A new test file (e.g., `tests/test_userbrief_json.js`)
            *   **Dependencies**: 30.4.
            *   **Validation**: Tests pass, confirming the new system is working correctly.
        *   🟢 **30.7. Cleanup userbrief.md**
            *   **Description**: After confirming the new system works, delete the old `.cursor/memory-bank/userbrief.md` file.
            *   **Impacted Rules/Files**: 
                *   `.cursor/memory-bank/userbrief.md`
            *   **Dependencies**: 30.6.
            *   **Validation**: The old markdown file is successfully deleted.

---

🟢 **31. Finalize Userbrief Refactoring in Workflow Rules**
    *   **Description**: The userbrief system has been partially refactored to use `userbrief.json`, but the core workflow rules (`consolidate-repo`, `task-decomposition`) still interact directly with `userbrief.md`. This task is to complete the migration by refactoring these rules to use the `read-userbrief` and `update-userbrief` MCP tools instead. This will centralize userbrief logic and remove the dependency on the markdown file from the rules.
    *   **Impacted Rules/Files**:
        *   `.cursor/rules/consolidate-repo.mdc`
        *   `.cursor/rules/task-decomposition.mdc`
        *   `.cursor/memory-bank/userbrief.md` (for archival, then deletion)
    *   **Dependencies**: Task 30.
    *   **Validation**: The `consolidate-repo` and `task-decomposition` rules no longer read or write to `userbrief.md`. They use the MCP tools to manage user requests. The workflow for processing user requests functions correctly with the new JSON-based system.
    *   **Sub-Tasks**:
        *   🟢 **31.1. Refactor consolidate-repo.mdc**
            *   **Description**: Modify the `consolidate-repo.mdc` rule. Replace all direct `read_file` and `edit_file` operations on `userbrief.md` with calls to the `read-userbrief` and `update-userbrief` MCP tools. The rule should now fetch the current request via the tool, and if a new request is found, it should use the `update-userbrief` tool to mark it as `in_progress`.
            *   **Impacted Rules/Files**: `.cursor/rules/consolidate-repo.mdc`
            *   **Dependencies**: 31.
            *   **Validation**: The rule successfully identifies and marks a new user request as "in_progress" using only MCP tools.
        *   🟢 **31.2. Refactor task-decomposition.mdc**
            *   **Description**: Modify the `task-decomposition.mdc` rule. In steps 5 and 8, replace the direct file interactions with `userbrief.md` with calls to the MCP tools. Step 5 should use `read-userbrief` to get the `in_progress` task. Step 8 should use `update-userbrief` with the 'mark_archived' action to archive the request after it has been decomposed into `tasks.md`.
            *   **Impacted Rules/Files**: `.cursor/rules/task-decomposition.mdc`
            *   **Dependencies**: 31.
            *   **Validation**: The rule successfully fetches an in-progress request, creates tasks, and archives the request in `userbrief.json` using only MCP tools.
        *   🟢 **31.3. Cleanup userbrief.md**
            *   **Description**: Once the rules are refactored and tested, and all remaining items from `userbrief.md` have been migrated or processed, delete the `.cursor/memory-bank/userbrief.md` file.
            *   **Impacted Rules/Files**: `.cursor/memory-bank/userbrief.md`
            *   **Dependencies**: 31.1, 31.2.
            *   **Validation**: The `userbrief.md` file is deleted.