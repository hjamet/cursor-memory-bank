🟢 **32. Investigate and Fix MCP Tool Argument Visibility**
*   **Description**: The user reports that the `remember` and `next_rule` tools appear to have no arguments in the Cursor UI. This task is to investigate the root cause and propose a solution.
*   **Impacted Rules/Files**: 
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js`
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/next_rule.js`
    *   `.cursor/mcp/memory-bank-mcp/server.js`
    *   `results/` for documentation.
*   **Dependencies**: None.
*   **Validation**: A clear root cause is identified and documented. The issue is either fixed via code change or a solution is proposed (e.g., client restart).
*   **Sub-Tasks**:
    *   🟢 **32.1. Analyze Argument Schema**: Confirm that `remember` and `next_rule` tools correctly export a Zod schema in their `args` property.
    *   🟢 **32.2. Hypothesize Root Cause**: Based on analysis and project documentation, determine the most likely root cause (e.g., client-side caching, stray debug logs).
    *   🟢 **32.3. Document Findings**: In the final experiment report, document the analysis, findings, and the recommended solution.

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

---

🟢 **36. Create Streamlit UI for Task Management**
*   **Description**: Create a simple Python application using Streamlit to provide a UI for managing user requests and viewing task status.
*   **Impacted Rules/Files**: 
    *   `src/main.py`
    *   `src/pages/task_status.py`
    *   `requirements.txt`
*   **Dependencies**: None.
*   **Validation**: A Streamlit application is created with a "Hello World" page and a page that displays task statuses from a `tasks.json` file.
*   **Sub-Tasks**:
    *   🟢 **36.1. Create project structure**: Create the `src` directory and a `requirements.txt` file with `streamlit`.
    *   🟢 **36.2. Create Hello World page**: Create a `src/main.py` with a simple "Hello World" Streamlit page.
    *   🟢 **36.3. Create Task Status page**: Create a `src/pages/task_status.py` that reads task information from a (to-be-created) `tasks.json` and displays it.

---

🟢 **37. Automate Task Management**
*   **Description**: Automate the task management process by updating the `next_rule` tool and related rules to handle task management automatically.
*   **Impacted Rules/Files**: 
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/next_rule.js`
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/read_userbrief.js`
    *   `.cursor/mcp/memory-bank-mcp/server.js`
    *   All files in `.cursor/workflow/`
*   **Dependencies**: None.
*   **Validation**: The task management process is automated, and the `tasks.md` file is updated correctly.
*   **Sub-Tasks**:
    *   🟢 **37.1. Modify `next_rule.js`**: Update the `next_rule` tool to make the `rule_name` argument optional. If `rule_name` is not provided, implement logic to read `userbrief.md` and `tasks.md` to determine the next rule (`task-decomposition` if there are pending requests, `implementation` if there are pending tasks, `context-update` otherwise).
    *   🟢 **37.2. Modify `read_userbrief.js`**: Update the `read_userbrief` tool to automatically change the status of any 'new' request to 'in_progress'.
    *   🟢 **37.3. Update `server.js`**: Update the schema for `next_rule` in `server.js` to reflect the optional argument.
    *   🟢 **37.4. Adapt `.md` rules**: Review and simplify all `.md` rules in `.cursor/workflow/` to use the new automated `next_rule` logic, removing manual calls to `consolidate-repo` and complex decision-making at the end of rules.

---

🟢 **38. Relocate Streamlit Application**
*   **Description**: Move the Streamlit application from `src/` to a new directory at `.cursor/memory-bank/streamlit_app/` and ensure it functions correctly from its new location when run from the repository root.
*   **Impacted Rules/Files**: 
    *   `src/main.py`
    *   `src/pages/task_status.py`
    *   `requirements.txt`
    *   `install.sh`
    *   `.cursor/memory-bank/streamlit_app/` (new directory)
*   **Dependencies**: None.
*   **Validation**: The Streamlit application is located in the new directory, the `install.sh` script installs its dependencies, and the application runs successfully from the project root, correctly loading all necessary files.
*   **Sub-Tasks**:
    *   🟢 **38.1. Move application files**: Move the `src` directory to `.cursor/memory-bank/streamlit_app`. Move `requirements.txt` into this new directory.
    *   🟢 **38.2. Update Streamlit file paths**: Modify `task_status.py` to correctly locate `tasks.json` and other necessary files (like `userbrief.md`) using paths relative to the project root, from where the app will be launched.
    *   🟢 **38.3. Update installation script**: Add logic to `install.sh` to check for Python/pip and install the Streamlit app's dependencies from the new `requirements.txt` location.