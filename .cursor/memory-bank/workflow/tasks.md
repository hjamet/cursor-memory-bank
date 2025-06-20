🟡 **32. Investigate and Fix MCP Tool Argument Visibility**
*   **Description**: The user reports that the `remember` and `next_rule` tools appear to have no arguments in the Cursor UI. This task is to investigate the root cause and propose a solution.
*   **Impacted Rules/Files**: 
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js`
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/next_rule.js`
    *   `.cursor/mcp/memory-bank-mcp/server.js`
    *   `results/` for documentation.
*   **Dependencies**: None.
*   **Validation**: A clear root cause is identified and documented. The issue is either fixed via code change or a solution is proposed (e.g., client restart).
*   **Sub-Tasks**:
    *   🟡 **32.1. Analyze Argument Schema**: Confirm that `remember` and `next_rule` tools correctly export a Zod schema in their `args` property.
    *   ⚪️ **32.2. Hypothesize Root Cause**: Based on analysis and project documentation, determine the most likely root cause (e.g., client-side caching, stray debug logs).
    *   ⚪️ **32.3. Document Findings**: In the final experiment report, document the analysis, findings, and the recommended solution.

---

🟢 **33. Improve MCP Tool Argument Descriptions**
*   **Description**: The user has requested more detailed and clearer descriptions for all `mcp_MemoryBank_*` tool arguments. This includes explicitly stating if an argument is optional or required and what its purpose is.
*   **Impacted Rules/Files**: 
    *   `.cursor/mcp/memory-bank-mcp/server.js`
    *   Potentially tool files in `.cursor/mcp/memory-bank-mcp/mcp_tools/` if schemas are defined there.
*   **Dependencies**: None.
*   **Validation**: The argument descriptions for all MemoryBank MCP tools in the Cursor UI are clear, explicit, and helpful to the user.
*   **Sub-Tasks**:
    *   🟢 **33.1. Review All MemoryBank Tool Schemas**: Systematically review the Zod schemas for every tool in the MemoryBank MCP server.
    *   🟢 **33.2. Enhance Argument Descriptions**: Update the `.describe()` string for each argument to include details such as "(optional)", "(required)", default values, and clearer explanations of their purpose. Apply these changes to the code.

---

🟢 **34. Systematically Test MCP Memory Bank Tools**
*   **Description**: Conduct a comprehensive test of all `mcp_MemoryBank_*` tools to ensure they function correctly. This will be done within a dedicated experiment.
*   **Impacted Rules/Files**: 
    *   `experience-execution.mdc` (will be called to perform this)
    *   `results/` for saving the experiment output.
*   **Dependencies**: Task 33 (to have the updated descriptions).
*   **Validation**: All tools are called successfully, and their outputs are documented and analyzed. Any bugs are identified.
*   **Sub-Tasks**:
    *   🟢 **34.1. Invoke experience-execution rule**: The workflow should call the `experience-execution` rule to create a formal experiment.
    *   🟢 **34.2. Test Each Tool**: Systematically call each `mcp_MemoryBank_*` tool with valid and, where appropriate, invalid parameters.
    *   🟢 **34.3. Document and Analyze Results**: For each tool call, the generated experiment report must contain the input, the full output, and a critical analysis of the result's correctness and format.

---

🟢 **35. Simplify New `.md` Rule Files**
*   **Description**: Simplify the new system's rules (`.md` files) by removing context loading and file validation steps, as this will be handled by the MCP server in the new system.
*   **Impacted Rules/Files**: 
    *   All files in `.cursor/workflow/`
*   **Dependencies**: None.
*   **Validation**: The new `.md` rule files are simplified and do not contain unnecessary steps.
*   **Sub-Tasks**:
    *   🟢 **35.1. Analyze new `.md` rule files**: Identify all rules that perform file reading for context (`projectBrief`, `activeContext`, etc.) and those that perform file validation/consolidation.
    *   🟢 **35.2. Modify `system.md` (new version)**: Remove the steps for reading context files.
    *   🟢 **35.3. Modify `consolidate-repo.md` (new version)**: Remove the file integrity/consolidation steps.
    *   🟢 **35.4. General review of other `.md` rules**: Check for similar patterns that can be simplified.