## TLDR
Adopte une posture de testeur **pragmatique et rapide**. Ton but est de valider que le cas d'usage principal de l'implémentation fonctionne comme attendu, via une **exécution manuelle et directe**. La vitesse est prioritaire sur l'exhaustivité.

**IMPORTANT TOOL USAGE CONSTRAINT:**
**You are strictly forbidden from using the `run_terminal_cmd` tool. You MUST use the `mcp_ToolsMCP_execute_command` tool for all command-line operations.**

## Purpose & Scope
L'étape `experience-execution` est conçue pour une **validation manuelle, rapide et ciblée**. L'objectif est de confirmer que la fonctionnalité de base est opérationnelle avec un minimum de friction.

- **Valider le cas d'usage principal**: Exécute la commande ou l'action qui correspond directement à l'objectif de la tâche.
- **Confirmation rapide**: L'objectif est d'obtenir un signal "ça marche" ou "ça ne marche pas" le plus vite possible.
- **Tests dynamiques**: Privilégie l'exécution de commandes directes plutôt que la création de scripts de test complexes et longs à maintenir.

**Ce n'est PAS pour**:
- Des tests automatisés exhaustifs.
- La recherche de tous les cas limites possibles.
- Des tests de performance ou de charge.

## When to Use Experience-Execution
This step is particularly valuable after:
- **Implementation steps**: To validate that the code you just wrote actually works
- **When tasks are in REVIEW**: To test implementations before user validation
- **After significant changes**: To ensure nothing broke during development
- **Before committing**: To avoid committing broken code

## Instructions

⚠️ **CRITICAL ANTI-LOOP PROTECTION**: When a test is **SUCCESSFUL**, you MUST follow this exact sequence to prevent infinite loops:
1. **FIRST**: Update task status to REVIEW using `mcp_MemoryBankMCP_update_task`
2. **SECOND**: Create commit using `mcp_MemoryBankMCP_commit`  
3. **THIRD**: Call remember using `mcp_MemoryBankMCP_remember`

**NEVER** skip step 1 or change this order. The workflow depends on this sequence for proper loop prevention.

1.  **Execute Manual Test**:
    - `<think>`
        - Quel est le moyen le plus rapide et direct de vérifier que la fonctionnalité principale fonctionne ?
        - Quelle est la commande unique que je peux exécuter pour valider le changement ?
        - Le test doit-il être plus complexe qu'une seule commande ? Si oui, pourquoi ?
    `</think>`
    - Mène un test ciblé. Exemples :
        - Exécuter la commande principale de l'outil en ligne de commande.
        - Démarrer le serveur et vérifier qu'il ne crash pas.
        - Lire un fichier de configuration pour s'assurer que les modifications ont été appliquées.
    - Clearly state whether the test was a **SUCCESS**, a **FAILURE**, or if you were **INTERRUPTED**.

2.  **Report Outcome & Next Steps**:

    - **If the test was a SUCCESS**:
        - `<think>`
            - Le test principal a réussi, mais ai-je identifié des faiblesses ? Ma mission est de rapporter les problèmes.
            - Je dois marquer la tâche comme 'REVIEW' AVANT tout.
        `</think>`
        - **🚨 MANDATORY FIRST STEP: Call `mcp_MemoryBankMCP_update_task` to set the status of the related task to `REVIEW`. This MUST be done before any other action.**
        - `<think>`
            - Now that the task is marked as REVIEW, I can proceed with the commit.
            - Formulate a clear and concise commit message that follows conventions. The message should summarize the changes that were just validated.
            - **Critique du commit**: Mon message de commit est-il précis ? Décrit-il le *pourquoi* du changement, pas seulement le *quoi* ? Le titre est-il concis et informatif ?
        `</think>`
        - Call the `mcp_MemoryBankMCP_commit` tool with the composed message.
        - `<think>`
            - Now that the work is committed, I must evaluate if the changes were "drastic" to decide the next step.
            - A change is "drastic" if it involves:
                - Modifications to core architectural files (e.g., workflow rules, MCP server logic).
                - A large number of files being changed at once.
                - The completion of a major feature or epic.
            - Based on my last commit, were the changes drastic?
            - If YES, the next step should be `context-update` to ensure the project's context is fully synchronized.
            - If NO, and there are more tasks, the next step is `implementation`.
            - If NO, and there are no more tasks, `context-update` is still appropriate.
        `</think>`
        - **FINAL STEP: Call `mcp_MemoryBankMCP_remember`.** Dans le champ `present`, sois bref et factuel. Confirme que le cas d'usage principal a été validé. (ex: "Le test a réussi. La commande X a produit le résultat Y comme attendu.").

    - **If the test was a FAILURE**:
        - `<think>`
            - Excellent, j'ai trouvé une faille. Quelle est sa nature exacte ?
            - Quelle est la cause racine la plus probable ?
            - Comment puis-je décrire ce problème de manière claire et actionnable pour l'étape `fix` ?
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to document the failure and set the future step to `fix`. **Utilise l'argument `user_message` pour communiquer l'échec et son impact.** (ex: "Échec du test : La commande principale a échoué avec l'erreur X, bloquant la fonctionnalité clé.").

    - **If you were INTERRUPTED**:
        - `<think>`
            - What was I trying to do when I was interrupted?
            - If I was trying to update a task's status (e.g., to 'APPROVED'), I should handle this to avoid a loop.
        `</think>`
        - If the interruption occurred during a task status update, change the task's status to **BLOCKED** using `mcp_MemoryBankMCP_update_task`. Add a comment explaining that the approval was interrupted by the user.
        - Call `mcp_MemoryBankMCP_remember` to document the interruption and set the future step to `context-update` to ensure the workflow can safely continue.

## Specifics
- This rule is for quick, targeted manual validation, not exhaustive testing.
- Focus on the main use case and obvious failure modes.
- The outcome must be a clear choice: SUCCESS, FAILURE, or INTERRUPTED.
- A commit is mandatory after a successful test.
- The `remember` tool is used to transition to the next logical step.

## Next Steps
- `fix` - If the manual test failed.
- `context-update` - If the test was successful and the change was drastic, or if no tasks are left, or if the process was interrupted.

## Example (Successful Test, Minor Change)

# Experience-Execution: 1 - Execute Manual Test
<think> I just implemented a new command `gemini-cli --version`. I will run this exact command to ensure it returns a version string. This is the fastest way to validate the core change. </think>
I will run the new version command.
`./gemini-cli --version`
The command finished successfully and returned `v1.2.3`. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think>The test for task #42 succeeded. I MUST mark it as 'REVIEW' BEFORE doing anything else. ⚠️ CRITICAL: I must update the task status FIRST to prevent infinite loops.</think>
🚨 MANDATORY FIRST STEP: I'm marking task #42 as REVIEW before proceeding with any other action.
[...calling `mcp_MemoryBankMCP_update_task` with task_id: 42, status: 'REVIEW'...]
<think> Now that the task is marked as REVIEW, I can proceed with the commit. A good commit message would be `feat(cli): Add --version command`. I'll use the ✨ emoji. The description will detail the new endpoint. My commit message is clear and follows the convention. It explains the "what" (adding the --version flag) and implies the "why" (to validate the core change). </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '✨', type: 'feat', title: 'feat(cli): Add --version command', description: '- Added the --version flag to the CLI...']
<think> The commit was successful. This was a minor change. There are more tasks pending. The next step should be `implementation`. </think>
FINAL STEP: Recording the successful test and determining next steps.
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Tested the new --version command.", PRESENT: "Test passed. The CLI returned the correct version string. The main use case is validated.", FUTURE: "Proceed to the next task in `implementation`.", user_message: ""]

## Example (Successful Test, Drastic Change)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored three workflow rules (`.md` files) to streamline the agent's decision-making. I will check the agent's memory to see if it correctly transitions between the new steps. </think>
I will check the agent's memory logs.
`cat .cursor/memory-bank/agent_memory.json`
The logs show the agent correctly followed the new workflow path. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think>The test for the workflow refactoring (task #43) succeeded. I MUST mark it as 'REVIEW' BEFORE doing anything else. ⚠️ CRITICAL: I must update the task status FIRST to prevent infinite loops.</think>
🚨 MANDATORY FIRST STEP: I'm marking task #43 as REVIEW before proceeding with any other action.
[...calling `mcp_MemoryBankMCP_update_task` with task_id: 43, status: 'REVIEW'...]
<think> Now that the task is marked as REVIEW, I can proceed with the commit. The changes affected multiple core workflow files. This is a drastic architectural change. The commit message must clearly state the scope and intent. `refactor(workflow): Streamline agent decision logic` seems appropriate. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '♻️', type: 'refactor', title: 'refactor(workflow): Streamline agent decision logic', description: '- Refactored experience-execution.md and implementation.md...']
<think> The commit was successful. Since this was a drastic change to the workflow, the correct next step is `context-update` to re-synchronize and re-evaluate the project state. This is crucial for stability. </think>
FINAL STEP: Recording the successful test and determining next steps.
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested the refactored workflow", PRESENT: "Task marked as REVIEW, drastic changes committed. Validated the main path and one failure path. The new logic seems robust.", FUTURE: "Proceed to `context-update` for project re-synchronization.", user_message: ""]

## Example (Failed Test)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored the database connection. The quickest way to check if it works is to start the server. </think>
I will attempt to start the server.
`npm start`
The server failed to start, crashing with a `TimeoutError: could not connect to database`. The outcome is a **FAILURE**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> The server can't connect. This is a critical failure of the main use case. I need to report this clearly for the `fix` step. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Tested the new DB connection by starting the server.", PRESENT: "The server failed to start with a connection timeout.", FUTURE: "Switch to the `fix` workflow to debug the database connection.", user_message: "Échec critique du test : La commande principale `npm start` a échoué. Le serveur n'a pas pu démarrer."...]
