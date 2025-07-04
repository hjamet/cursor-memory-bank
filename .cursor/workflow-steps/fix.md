## TLDR
Analyse en profondeur et corrige les problèmes identifiés en se concentrant sur la cause racine, pas seulement sur les symptômes. Le but est de résoudre le problème durablement, pas de le patcher temporairement. Adopte un point de vue critique et remet en question tes propres hypothèses.

**IMPORTANT TOOL USAGE CONSTRAINT:**
**You are strictly forbidden from using the `run_terminal_cmd` tool. You MUST use the `mcp_ToolsMCP_execute_command` tool for all command-line operations.**

## Instructions

1. **Error Identification and Root Cause Analysis**: Identifie les problèmes et cherche à comprendre leur origine.
   - Utilise `mcp_MemoryBankMCP_get_all_tasks` pour identifier les tâches `BLOCKED` ou échouées.
   - Analyse les souvenirs récents pour les rapports d'erreur.
   - **Analyse Critique**: Ne te contente pas de lister les erreurs. Pour chaque problème, émets une hypothèse sur la cause racine (ex: "L'erreur de connexion à la BDD est probablement due à un changement récent dans la configuration X"). Sois sceptique. Pourquoi cette hypothèse est-elle la plus probable ? Y a-t-il d'autres explications possibles ?

2. **Correction Loop**: Pour CHAQUE problème identifié, suis ce cycle :
   - **2.1. Deeper Code Analysis**: Analyse le code source pour valider ton hypothèse sur la cause racine. Demande-toi *pourquoi* cette erreur se produit maintenant. Est-ce une régression ? Un effet de bord ? Sois exhaustif dans ton investigation.
   - **2.2. Propose Correction & Assess Risks**: Formule un correctif. Évalue les risques et les effets de bord potentiels de ta correction. (ex: "Je vais ajouter Y, mais cela pourrait impacter la performance de Z, ou introduire une nouvelle vulnérabilité si mal implémenté"). Ne minimise pas les risques.
   - **2.3. Apply Correction**: Applique le correctif avec `edit_file`.
   - **2.4. Test Execution**: Relance les tests pertinents.
   - **2.5. Verification & Critical Review**: Analyse le résultat.
     - **Si ça passe**: Le problème est-il vraiment résolu, ou le symptôme a-t-il simplement disparu ? Sois ton propre avocat du diable. Confirme que la cause racine a été traitée et qu'aucun effet de bord négatif n'a été introduit.
     - **Si ça échoue encore**: Revois ton hypothèse. La cause racine est ailleurs. Retourne à l'étape 2.1 avec une nouvelle approche. Documente pourquoi ta première hypothèse était incorrecte. C'est un apprentissage, pas un échec.
     - **Après 3 échecs**: Marque la tâche comme `BLOCKED`. Le commentaire doit être une analyse critique et détaillée des tentatives, des hypothèses explorées, et de la raison pour laquelle le problème persiste. Ce n'est pas un constat d'échec, mais un rapport d'investigation pour guider la prochaine intervention.

3. **Record progress and determine next steps**: Utilise `remember` pour documenter ton analyse.
   - Appelle `mcp_MemoryBankMCP_remember`. Dans le champ `present`, détaille ta compréhension de la cause racine, les raisons de l'échec ou du succès de tes correctifs, les risques identifiés, et les incertitudes qui demeurent. Sois honnête sur les limites de ta correction.

## Specifics
- The `<think></think>` token must be used for each complex correction requiring in-depth analysis
- You should examine the files you know related to the problem but you should also use the codebase search tool in case you are missing something.
- Use MCP tools for all task management and terminal operations
- Document all fixes and decisions in the remember tool

## Using the Advanced MCP Terminal Tools

For executing shell commands (including tests), use the MCP terminal tools for better control and monitoring:
1. **Launch:** Call the `mcp_ToolsMCP_execute_command` MCP tool with the `command` to run and an optional `timeout` in seconds.
2. **Check Status:** Call the `mcp_ToolsMCP_get_terminal_status` MCP tool with an optional `timeout` in seconds to get the status of running/completed commands.
3. **Get Output:** Call the `mcp_ToolsMCP_get_terminal_output` MCP tool with the target `pid` and an optional `lines` count to retrieve output.
4. **Stop & Cleanup:** Call the `mcp_ToolsMCP_stop_terminal_command` MCP tool with the target `pid` to terminate a running command.

## Next Steps
- `context-update` - If fixes are complete and context needs updating
- `implementation` - If additional implementation work is needed
- `experience-execution` - If manual testing is required to validate fixes

## Example

# Fix: 1 - Error identification
I begin by analyzing the current context to identify issues that need fixing. **(Fix: 1 - Error identification)**
[...calling mcp_MemoryBankMCP_get_all_tasks to identify BLOCKED tasks...]
[...reviewing recent memories for error reports...]

I've identified the following issues:
1. Task #X is BLOCKED due to compilation error
2. Recent memory indicates database connection issue
3. User reported authentication problem

<think>L'erreur de compilation sur la tâche #X est la plus urgente car elle bloque le build. Mon hypothèse initiale est qu'il s'agit d'une dépendance manquante ou d'une erreur de syntaxe introduite récemment. Je vais commencer par ça, car c'est souvent le plus simple à résoudre. Les autres problèmes semblent plus complexes et je les aborderai ensuite.</think>
I will now start the correction loop for these issues. **(Fix: 1 - Error identification)**

# Fix: 2 - Correction loop

## Fix - 2.1: Correcting Task #X compilation error

### Fix - 2.1.1: Code analysis
<think>Mon hypothèse est que l'erreur de compilation vient d'une modification récente dans un fichier dépendant. Je vais analyser l'historique git et les fichiers liés pour confirmer. Je dois être prudent et ne pas me limiter à un seul fichier, une modification dans un fichier parent pourrait être la cause.</think>
J'analyse le code pour trouver la **cause racine** de l'erreur. **(Fix: 2.1.1 - Code analysis)**
[... `read_file` et `codebase_search` pour valider l'hypothèse ...]
**(Fix: 2.1.1 - Code analysis)**

### Fix - 2.1.2: Propose correction
<think>L'hypothèse est confirmée. Un renommage de fonction n'a pas été répercuté ici. Le correctif est de mettre à jour l'appel de fonction. Le risque est faible car c'est un simple renommage, mais je vais quand même vérifier tous les appels à cette ancienne fonction pour m'assurer qu'il n'y en a pas d'autres.</think>
**(Fix: 2.1.2 - Propose correction)**

### Fix - 2.1.3: Apply correction
J'applique le correctif. **(Fix: 2.1.3 - Apply correction)**
[... `edit_file` pour corriger l'appel de fonction ...]
**(Fix: 2.1.3 - Apply correction)**

### Fix - 2.1.4: Test execution
I'll test the fix by running the compilation. **(Fix: 2.1.4 - Test execution)**
[... `mcp_ToolsMCP_execute_command` with compilation command ...]
**(Fix: 2.1.4 - Test execution)**

### Fix - 2.1.5: Verification
<think>La compilation a réussi. Le problème semble résolu. Mais est-ce vraiment le cas ? Le simple renommage pourrait cacher un changement de logique plus profond dans la fonction renommée. Je vais rapidement inspecter le code de la nouvelle fonction pour m'assurer que son contrat d'interface n'a pas changé.</think>
La compilation a réussi. La cause racine (renommage non répercuté) est corrigée. Je mets à jour le statut de la tâche. **(Fix: 2.1.5 - Verification)**
[... `mcp_MemoryBankMCP_update_task` pour débloquer la tâche ...]

# Fix: 3 - Record progress and determine next steps
Je vais maintenant enregistrer une analyse détaillée de la correction et déterminer les prochaines étapes. **(Fix: 3 - Record progress and determine next steps)**
[...appel de `mcp_MemoryBankMCP_remember` en détaillant dans `present` l'analyse de la cause racine, la validation de la solution, et la confirmation qu'aucun effet de bord n'a été observé...]
**(Fix: 3 - Record progress and determine next steps)**


