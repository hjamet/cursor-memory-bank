## TLDR
Adopte une posture de testeur critique. Ton but n'est pas de valider que ça fonctionne, mais de découvrir *comment ça casse*. Cherche activement les failles et les points de rupture de l'implémentation récente.

## Purpose & Scope
L'étape `experience-execution` est conçue pour une **validation critique et manuelle**. L'objectif est de stresser l'implémentation pour découvrir ses faiblesses avant qu'elles n'atteignent l'utilisateur.

- **Chercher les points de rupture**: N'exécute pas seulement le cas nominal. Essaie des entrées inattendues, des ordres d'exécution inhabituels.
- **Valider la robustesse**: Que se passe-t-il en cas d'erreur ? Le système gère-t-il l'échec gracieusement ?
- **Identifier les effets de bord**: Ta modification a-t-elle eu un impact inattendu sur une autre partie du système ?

**Ce n'est PAS pour**:
- Des tests de complaisance (happy path testing).
- Valider uniquement que le code tourne sans erreur.

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
        - Comment puis-je mettre en échec cette implémentation ?
        - Quel est le point le plus fragile de ce que je viens de coder ?
        - Que se passe-t-il si je fournis une entrée vide, invalide, ou si j'exécute l'action deux fois ?
        - Quel est le test simple qui a le plus de chances de révéler une faiblesse ?
    `</think>`
    - Mène un test critique. Exemples :
        - Running a command to test functionality
        - Interacting with a UI to verify behavior
        - Checking file contents or outputs
        - Testing API endpoints or interfaces
        - Executing the main use case for the feature
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
            - What is the correct emoji, type, title, and description for the commit?
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
        - **FINAL STEP: Call `mcp_MemoryBankMCP_remember`. N'utilise `user_message` que si tu as découvert un problème CRITIQUE qui nécessite l'attention immédiate de l'utilisateur.** La plupart du temps, ce champ doit être vide.

    - **If the test was a FAILURE**:
        - `<think>`
            - Excellent, j'ai trouvé une faille. Quelle est sa nature exacte ?
            - Quelle est la cause racine la plus probable ?
            - Comment puis-je décrire ce problème de manière claire et actionnable pour l'étape `fix` ?
        `</think>`
        - Call `mcp_MemoryBankMCP_remember` to document the failure and set the future step to `fix`. **Utilise l'argument `user_message` pour communiquer l'échec et son impact.** (ex: "Échec critique du test : La nouvelle API de paiement autorise des transactions négatives, ce qui pourrait entraîner des pertes financières.").

    - **If you were INTERRUPTED**:
        - `<think>`
            - What was I trying to do when I was interrupted?
            - If I was trying to update a task's status (e.g., to 'APPROVED'), I should handle this to avoid a loop.
        `</think>`
        - If the interruption occurred during a task status update, change the task's status to **BLOCKED** using `mcp_MemoryBankMCP_update_task`. Add a comment explaining that the approval was interrupted by the user.
        - Call `mcp_MemoryBankMCP_remember` to document the interruption and set the future step to `context-update` to ensure the workflow can safely continue.

## Adversarial Mindset
Pense comme un attaquant ou un utilisateur maladroit.
- **Entrées invalides**: Que se passe-t-il avec `null`, `undefined`, des chaînes vides, des nombres négatifs ?
- **Double exécution**: Si tu lances une commande deux fois de suite, est-ce que ça crée un état incohérent ?
- **Conditions de course**: Y a-t-il un risque si deux processus accèdent à la même ressource ?
- **Gestion d'erreur**: Si une dépendance (ex: une API externe) échoue, le système se comporte-t-il correctement ?

## Validation Strategies

### Code/Logic Changes
- Run the main functionality to ensure it works
- Test with typical inputs and check outputs
- Verify error handling with invalid inputs

### UI/Interface Changes  
- Load the interface and check for visual issues
- Test main user interactions
- Verify responsive behavior if applicable

### API/Service Changes
- Make test requests to new endpoints
- Verify response formats and status codes
- Check integration with existing systems

### Configuration/Setup Changes
- Test the configuration loads correctly
- Verify services start without errors
- Check that settings are applied properly

### File/Data Processing
- Process sample data through the new logic
- Verify output format and content
- Check error handling for malformed inputs

## Specifics
- This rule is for quick, targeted manual validation, not exhaustive testing.
- Focus on the main use case and obvious failure modes.
- The outcome must be a clear choice: SUCCESS, FAILURE, or INTERRUPTED.
- A commit is mandatory after a successful test.
- The `remember` tool is used to transition to the next logical step.
- **Remember**: You're validating that your implementation works, not building a comprehensive test suite.

## Next Steps
- `fix` - If the manual test failed.
- `implementation` - If the test was successful and the change was not drastic, and there are more tasks.
- `context-update` - If the test was successful and the change was drastic, or if no tasks are left, or if the process was interrupted.

## Example (Successful Test, Minor Change)

# Experience-Execution: 1 - Execute Manual Test
<think> I just implemented the JWT token generation in `auth.js`. I will run the associated test file `auth.test.js` to see if it passes and generates a token as expected. </think>
I will run the tests for the new authentication module.
`npm test -- src/auth/auth.test.js`
The test command finished successfully with all tests passing. The outcome is a **SUCCESS**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think>The test for task #42 succeeded. I MUST mark it as 'REVIEW' BEFORE doing anything else. ⚠️ CRITICAL: I must update the task status FIRST to prevent infinite loops.</think>
🚨 MANDATORY FIRST STEP: I'm marking task #42 as REVIEW before proceeding with any other action.
[...calling `mcp_MemoryBankMCP_update_task` with task_id: 42, status: 'REVIEW'...]
<think> Now that the task is marked as REVIEW, I can proceed with the commit. A good commit message would be `feat(auth): Implement JWT generation`. I'll use the ✨ emoji. The description will detail the new endpoint. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '✨', type: 'feat', title: 'feat(auth): Implement JWT generation', description: '- Added /login endpoint to generate JWT...']
<think> The commit was successful. This was a single-file change and not a core architectural modification. The change was not drastic. I see other tasks are pending. The next step should be `implementation`. </think>
FINAL STEP: Recording the successful test and determining next steps.
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested JWT generation", PRESENT: "Task marked as REVIEW, changes committed", FUTURE: "Proceed to the next task in `implementation`.", user_message: "Expérience réussie : Les tests pour la génération JWT sont tous passés (12/12)." ...]

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
<think> Now that the task is marked as REVIEW, I can proceed with the commit. The changes affected multiple core workflow files. This is a drastic architectural change. The commit message should reflect this. </think>
[...calling `mcp_MemoryBankMCP_commit` with emoji: '♻️', type: 'refactor', title: 'refactor(workflow): Streamline agent decision logic', description: '- Refactored experience-execution.md and implementation.md...']
<think> The commit was successful. Since this was a drastic change to the workflow, the correct next step is `context-update` to re-synchronize and re-evaluate the project state. </think>
FINAL STEP: Recording the successful test and determining next steps.
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Successfully tested the refactored workflow", PRESENT: "Task marked as REVIEW, drastic changes committed", FUTURE: "Proceed to `context-update` for project re-synchronization.", user_message: "Expérience réussie : Le remaniement des règles de workflow a été validé. L'agent suit correctement le nouveau flux."...]

## Example (Failed Test)

# Experience-Execution: 1 - Execute Manual Test
<think> I just refactored the database connection pool. I'll try to start the server, which should now connect to the database immediately. </think>
I will attempt to start the server.
`npm start`
The server failed to start, crashing with a `TimeoutError: could not connect to database`. The outcome is a **FAILURE**.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> The server can't connect to the database after my refactoring. It's likely an issue with the new connection string or pooling options. I need to investigate this in the `fix` step. </think>
[...calling `mcp_MemoryBankMCP_remember` with PAST: "Tested the new DB connection logic by starting the server.", PRESENT: "The server failed to start with a connection timeout.", FUTURE: "Switch to the `fix` workflow to debug the database connection.", user_message: "Expérience échouée : Le serveur n'a pas pu démarrer et a retourné une erreur `TimeoutError: could not connect to database`."...]

# Experience-Execution: 1 - Execute Manual Test
<think> J'ai implémenté la génération de token JWT. Le cas nominal fonctionne. Essayons de casser quelque chose. Que se passe-t-il si je demande un token avec un payload vide ? </think>
Je vais tenter de générer un token JWT avec un payload vide.
`node -e "require('./src/auth').generateToken('')"`
La commande a crashé avec une erreur `TypeError: payload must be a non-empty string`. C'est un **FAILURE**. Le système devrait gérer cette erreur gracieusement.

# Experience-Execution: 2 - Report Outcome & Next Steps
<think> Le test a échoué. J'ai trouvé une faille : le système ne gère pas les payloads vides. C'est une information cruciale pour l'étape `fix`. </think>
[...appel de `mcp_MemoryBankMCP_remember` avec PAST: "Test critique de la génération JWT.", PRESENT: "Le système crash avec un payload vide (TypeError). Il manque une validation d'entrée.", FUTURE: "Passer à l'étape `fix` pour ajouter la validation.", user_message: "Échec du test de robustesse sur la génération JWT : le système ne gère pas les entrées invalides et expose une erreur brute."...]
