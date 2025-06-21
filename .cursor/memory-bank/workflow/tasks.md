🟢 **41. Diagnostiquer et réparer le workflow MCP**
    *   **Description**: Le workflow MCP, qui repose sur les outils `mcp_MemoryBank_remember` et `mcp_MemoryBank_next_rule`, échoue de manière intermittente, empêchant l'agent de fonctionner de manière autonome. Cette tâche vise à identifier la cause première du problème et à le corriger.
    *   **Impacted Rules/Files**: 
        *   `.cursor/mcp/memory-bank-mcp/server.js`
        *   `.cursor/mcp/memory-bank-mcp/mcp_tools/next_rule.js`
        *   `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js`
        *   `test_remember_next_rule.js`
    *   **Dependencies**: Aucune.
    *   **Validation**: Le workflow autonome peut être exécuté sans que les appels à `next_rule` ou `remember` n'échouent. L'agent peut enchaîner plusieurs règles de manière autonome.
    *   **Sub-Tasks**:
        *   🟢 **41.1. Analyse des logs et reproduction**: Analyser les logs d'erreurs fournis (`Unexpected token 'R'`, interruptions). Essayer de reproduire le bug de manière fiable, potentiellement en adaptant ou en utilisant `test_remember_next_rule.js`.
        *   🟢 **41.2. Correction du code**: Une fois la cause identifiée (ex: problème de sérialisation JSON, gestion des processus enfants, erreur de logique dans le serveur), appliquer les corrections nécessaires au code du serveur MCP.
        *   🟢 **41.3. Test de validation**: Exécuter le scénario de test de la sous-tâche 41.1 pour confirmer que le bug est résolu. Lancer un workflow de test complet pour s'assurer qu'il n'y a pas de régressions et que l'enchaînement des règles est stable.
        *   🟢 **41.4. Nettoyage et documentation**: Nettoyer le code de test et documenter la cause du bug et la solution apportée dans un nouveau fichier de résultat (`results/mcp_workflow_fix_YYYYMMDD/README.md`).

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

🟢 **39. Pre-download ML Model during Installation**
*   **Description**: Modify the `install.sh` script to pre-download the `all-MiniLM-L6-v2` sentence-transformer model. This avoids a long download time on the first use of the `remember` tool.
*   **Impacted Rules/Files**: 
    *   `install.sh`
    *   A new Python script for downloading the model (e.g., `.cursor/memory-bank/download_model.py`).
    *   A new directory for the model (e.g., `.cursor/memory-bank/models/`).
*   **Dependencies**: None.
*   **Validation**: The `install.sh` script successfully downloads the ML model into the designated directory.
*   **Sub-Tasks**:
    *   🟢 **39.1. Create model download script**: Create a Python script that uses the `sentence-transformers` library to download the `all-MiniLM-L6-v2` model to a specified directory.
    *   🟢 **39.2. Update installation script**: Add a new function to `install.sh` that first installs the `sentence-transformers` library via pip, and then executes the download script.

---

🟢 **40. Refactor Userbrief Status Management**
*   **Description**: Refactor the userbrief management tools to automate status changes and correctly handle pinned items, as requested by the user.
*   **Impacted Rules/Files**: 
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/update_userbrief.js`
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/read_userbrief.js`
    *   `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js`
*   **Dependencies**: None.
*   **Validation**: The `update-userbrief` tool prevents manual status changes to 'in_progress'. The `read-userbrief` and `remember` tools correctly include pinned items in their output.
*   **Sub-Tasks**:
    *   🟢 **40.1. Modify `update_userbrief.js`**: Prevent the agent from setting a request's status to 'in_progress'. This status should only be set automatically by the system.
    *   🟢 **40.2. Modify `read_userbrief.js`**: Update the tool to always include pinned (📌) items in its response, in addition to the other statuses it already returns.
    *   🟢 **40.3. Modify `remember.js`**: Update the `remember` tool to read the userbrief and include the content of any pinned (📌) items in the memory context it provides.

---

🔴 **42. Refactor Workflow: Rules to Steps & New Logic**
    *   **Description**: A major refactoring of the agent's workflow as per the user's request. This involves changing the core terminology from "rules" to "steps", overhauling the navigation logic to be explicit rather than automatic, and cleaning up legacy practices like creating `results` directories.
    *   **Impacted Rules/Files**: 
        *   All files in `.cursor/workflow/` and `.cursor/rules/`
        *   `.cursor/mcp/memory-bank-mcp/server.js`
        *   All files in `.cursor/mcp/memory-bank-mcp/mcp_tools/`
        *   All test scripts, especially `test_remember_next_rule.js`.
    *   **Dependencies**: None.
    *   **Validation**: The agent successfully uses the new "step-based" workflow. The `next_step` tool works as specified, `remember` provides `possible_next_steps`, test scripts are updated and pass, and no new `results` directories are created.
    *   **Sub-Tasks**:
        *   🔴 **42.1. Rename `next_rule` to `next_step`**:
            *   **Description**: Perform a global rename of the `next_rule` tool and its related assets to `next_step`. The new tool will take a mandatory `step_name` argument and will simply fetch the content of the corresponding `.md` file without any decision logic.
            *   **Impacted Rules/Files**: `.cursor/mcp/memory-bank-mcp/mcp_tools/next_rule.js`, `.cursor/mcp/memory-bank-mcp/server.js`, all workflow files calling the tool.
            *   **Validation**: The file `next_rule.js` is renamed to `next_step.js` and its content is updated. The tool registered in `server.js` is `next_step`. All calls in `.md` files are updated.
            *   **Status**: BLOCKED. The `edit_file` tool consistently fails to apply changes to `server.js`, preventing the registration of the new tool.
        *   🟢 **42.2. Update `remember` to suggest next steps**:
            *   **Description**: Modify the `remember` tool to analyze the current agent state (tasks, userbrief) and return a list of valid next steps (e.g., `['task-decomposition', 'implementation']`) in its output. It must also handle the initial state where no context exists, suggesting `['START']`.
            *   **Impacted Rules/Files**: `.cursor/mcp/memory-bank-mcp/mcp_tools/remember.js`.
            *   **Validation**: The `remember` tool returns a `possible_next_steps` array in its JSON output, and the logic correctly reflects the agent's state.
        *   🔴 **42.3. Update all workflow files (`.md`, `.mdc`)**:
            *   **Description**: Globally replace the term "rule" with "step". Update the workflow logic in all `.md` and `.mdc` files. Instead of calling `next_rule` directly, the agent must now first call `remember`, analyze the returned `possible_next_steps`, choose an appropriate step, and then call `next_step` with the chosen step name.
            *   **Impacted Rules/Files**: All files in `.cursor/workflow/` and `.cursor/rules/`.
            *   **Validation**: All workflow files use the term "step" and follow the new `remember` -> `choose` -> `next_step` pattern.
            *   **Status**: BLOCKED. The `edit_file` tool is unstable on markdown workflow files, applying incorrect and destructive changes.
        *   🔴 **42.4. Remove `results/` directory creation**:
            *   **Description**: Edit all workflow steps (formerly rules) to remove any instruction that obligates the agent to create a new subdirectory in `results/` to document its work. Documentation should be handled through context files and commits.
            *   **Impacted Rules/Files**: `context-update.md`, `experience-execution.md`, `fix.md`, etc.
            *   **Validation**: The agent no longer creates `results/` directories during its standard workflow.
            *   **Status**: BLOCKED. The `edit_file` tool is unstable on markdown workflow files.
        *   🔴 **42.5. Update Test Scripts**:
            *   **Description**: Update all relevant test scripts to reflect the workflow changes. This includes renaming `test_remember_next_rule.js` to `test_remember_next_step.js` and updating its logic to test the new `remember` output and the `next_step` tool.
            *   **Impacted Rules/Files**: `test_remember_next_rule.js`, potentially others.
            *   **Validation**: Test scripts are aligned with the new API and pass successfully.
            *   **Status**: BLOCKED. The test script fails due to a persistent `ERR_PACKAGE_PATH_NOT_EXPORTED` error from the `@modelcontextprotocol/sdk`, indicating a deep issue with the dependency itself or how it's being used.
        *   ⚪️ **42.6. Enforce `MyMCP` tools for terminal commands**:
            *   **Description**: Review all steps to ensure they exclusively use `mcp_MyMCP_execute_command` for any terminal operations, as per the user's directive for stability.
            *   **Impacted Rules/Files**: `test-execution.md`, `fix.md`, `install.sh` (if used by agent).
            *   **Validation**: No rule uses the old `run_terminal_cmd` tool.