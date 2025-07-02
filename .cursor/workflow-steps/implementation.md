## TLDR
Implémente méthodiquement UNE SEULE tâche prioritaire avec routage intelligent. **ATTENTION : Ne traiter qu'UNE SEULE tâche par cycle.** 

**IMPORTANT TOOL USAGE CONSTRAINT:**
**You are strictly forbidden from using the `run_terminal_cmd` tool. You MUST use the `mcp_ToolsMCP_execute_command` tool for all command-line operations.**

## Instructions

1.  **Task analysis and status update**: Analyser LA tâche à implémenter (UNE SEULE) et la marquer immédiatement comme IN_PROGRESS.
    *   Utiliser `mcp_MemoryBankMCP_get_next_tasks` pour obtenir LA tâche prioritaire.
    *   **IMPORTANT** : C'est CETTE tâche et UNIQUEMENT cette tâche que vous devez traiter.
    *   **MARQUAGE OBLIGATOIRE** : Marquer IMMÉDIATEMENT la tâche comme IN_PROGRESS avec `mcp_MemoryBankMCP_update_task`. C'est une règle non négociable pour maintenir l'intégrité du workflow.
    *   **EXEPTION** : Si une tâche est déjà marquée comme IN_PROGRESS, sauter cette étape et continuer de travailler avec cette tâche.

2.  **Évaluation et Routage Intelligent**: Évaluer la nature de la tâche pour décider de la marche à suivre.
    *   **ANALYSE DE LA TÂCHE**: En tant qu'ingénieur senior, analyse en profondeur le titre, la description et les objectifs de la tâche.
    *   **DÉCISION DE ROUTAGE**:
        *   **CAS 1 : Exécution Pure**: Si tu détermines que la tâche ne nécessite **aucune modification de code** et consiste uniquement à exécuter des commandes, lancer des tests, effectuer des validations, ou générer des rapports, alors la phase d'implémentation n'est pas nécessaire.
            *   **ACTION** : Appelle immédiatement `mcp_MemoryBankMCP_next_rule` avec `step_name: "experience-execution"`.
            *   **RÈGLE TERMINÉE** : La règle `implementation` s'arrête ici pour ce type de tâche.
        *   **CAS 2 : Développement Requis**: Si la tâche implique la moindre modification de code (création de fichier, correction, refactoring, ajout de fonctionnalité), continue avec les étapes de développement ci-dessous (3-5).
    *   **Principe directeur**: Fais confiance à ton jugement d'expert pour distinguer une tâche de "développement" d'une tâche d'"exécution". Documente ta décision dans ta pensée.

3.  **Analyse du contexte et Plan d'implémentation**: Analyser le code existant pour en comprendre les principes, pratiques et conventions.
    *   **Recherche de contexte**: Effectuer jusqu'à 3 recherches sémantiques (`codebase_search`).
    *   **Objectifs de la recherche**:
        *   Identifier les composants, fonctions ou patterns réutilisables.
        *   Comprendre les conventions de code actuelles et s'y conformer autant que possible.
        *   Identifier comment le genre de tâche que tu as à implémenter a été géré dans le passé : reproduis les mêmes approches.
        *   **Principe directeur**: Tu ne dois pas réinventer la roue ! Va au plus simple. Modifie aussi peu que possible le code existant : il est certainement correct. Réutilise autant que possible le code existant.
    *   **Synthèse**: Tu dois finir cette étape en faisant une synthèse des principes, composants réutilisables et conventions de code identifiés. En prenant en compte tous ces éléments, tu dois établir un plan d'implémentation.

4.  **Implementation** (ancienne étape 3): Implémenter les modifications nécessaires pour LA tâche unique, en suivant les principes identifiés.
    *   Utiliser les outils appropriés (`edit_file`, `replace_content_between`, `grep_search`, etc.).
    *   **FOCUS ABSOLU** : Concentre-toi uniquement sur cette tâche. Ne te laisse pas distraire par d'autres problèmes non planifiés.

5.  **Record progress and determine next steps**: Enregistrer une auto-évaluation honnête et transition automatique.
    *   **OBLIGATOIRE** : Utiliser `mcp_MemoryBankMCP_remember`.
    *   **Communication Critique**: N'utiliser le paramètre `user_message` de `remember` que pour signaler un problème **critique** qui requiert l'attention de l'utilisateur.
    *   **TRANSITION AUTOMATIQUE** : Le workflow passe automatiquement à `experience-execution` pour validation après remember.

## Specifics - RÈGLES STRICTES
- **RÈGLE #1** : Travailler sur UNE SEULE tâche à la fois - JAMAIS plusieurs tâches en séquence
- **RÈGLE #2** : LA tâche à traiter est celle retournée par `mcp_MemoryBankMCP_get_next_tasks` - pas d'autres
- **RÈGLE #3** : MARQUER IMMÉDIATEMENT la tâche comme IN_PROGRESS dès l'étape 1 - AUCUNE EXCEPTION
- **RÈGLE #4** : APPLIQUER LE ROUTAGE INTELLIGENT à l'étape 2 - analyser le type de tâche et router si nécessaire
- **RÈGLE #5** : Terminer OBLIGATOIREMENT par `mcp_MemoryBankMCP_remember` pour maintenir le workflow
- **RÈGLE #6** : Ne pas décider arbitrairement de traiter d'autres tâches "tant qu'on y est"
- **RÈGLE #7** : Si une tâche semble liée à d'autres, traiter UNIQUEMENT la tâche prioritaire retournée par l'outil
- **RÈGLE #8** : Les sous-tâches sont autorisées UNIQUEMENT si elles font partie intégrante de la tâche principale
- **RÈGLE #9** : NE JAMAIS marquer une tâche comme REVIEW - c'est la responsabilité d'experience-execution
- Utiliser les outils MCP pour toute gestion de tâches
- Respecter les conventions de code établies
- Tester les modifications localement si possible
- Documenter les décisions importantes dans les souvenirs

## Next Steps - WORKFLOW AUTOMATION ACTIVE

⚠️ **TRANSITION AUTOMATIQUE ACTIVÉE** ⚠️

**RÈGLE CRITIQUE** : Après chaque implémentation terminée, le workflow passe **AUTOMATIQUEMENT** à `experience-execution` pour validation. Cette transition est **OBLIGATOIRE** et fait partie de l'architecture de qualité du système.

**Transitions automatiques** :
- `implementation` → `experience-execution` (AUTOMATIQUE - après une implémentation de code)
- `implementation` → `experience-execution` (DIRECT - pour les tâches d'exécution pure routées à l'étape 2)
- `experience-execution` → Déterminé par les résultats des tests

**Exceptions rares** (gérées automatiquement par le système) :
- Présence de tâches BLOCKED critiques
- Demandes utilisateur urgentes sans tâches récemment complétées

**Étapes manuelles possibles** :
- `context-update` - Pour finaliser et commiter les changements
- `fix` - Si des problèmes sont détectés pendant l'implémentation
- `task-decomposition` - Si de nouvelles demandes utilisateur arrivent

## Example - SINGLE TASK WORKFLOW (Careful and efficient Mindset)

# Implementation: 1 - Task analysis and status update
Je commence par analyser LA tâche à implémenter (UNE SEULE) et la marquer immédiatement comme IN_PROGRESS.
[...appel de mcp_MemoryBankMCP_get_next_tasks...]
J'ai identifié LA tâche prioritaire : {{ current_tasks_summary }}; Comme je n'ai pas d'autre tâche en cours, je vais la marquer comme IN_PROGRESS.
**MARQUAGE OBLIGATOIRE** : Je marque immédiatement cette tâche comme IN_PROGRESS.
[...appel OBLIGATOIRE de mcp_MemoryBankMCP_update_task pour marquer la tâche IN_PROGRESS...]
**FOCUS** : Je vais traiter UNIQUEMENT cette tâche.

# Implementation: 2 - Évaluation et Routage Intelligent
J'évalue la nature de la tâche pour décider de la marche à suivre.
<think>La tâche "{{ current_task_title }}" demande de "{{ current_task_description }}". Après analyse, je détermine si une modification de code est nécessaire.
- **CAS 1 - Exécution Pure**: La tâche demande de lancer des tests et de générer un rapport. Aucune ligne de code ne sera changée. Je vais donc router vers experience-execution.
- **CAS 2 - Développement Requis**: La tâche demande de corriger un bug dans la fonction X. Cela nécessite de modifier le code. Je vais donc continuer avec l'implémentation.
Ma décision est : [CAS 1 ou CAS 2]
</think>
- **DÉCISION DE ROUTAGE - CAS 1** : Cette tâche ne nécessite que de l'exécution. Je la route vers `experience-execution`.
  [...appel de mcp_MemoryBankMCP_next_rule avec step_name: "experience-execution"...]
  **WORKFLOW TERMINÉ**
- **DÉCISION DE ROUTAGE - CAS 2** : Cette tâche nécessite du développement. Je continue avec les étapes 3-5.

# Implementation: 3 - Analyse du contexte et Plan d'implémentation
Je recherche dans la base de code pour trouver des composants réutilisables et des conventions de code.
[...appel de `codebase_search` (jusqu'à 3 fois)...]
**Analyse et Plan**:
[...synthèse des principes, composants réutilisables et conventions de code identifiés...]

# Implementation: 4 - Implementation
Je procède maintenant à l'implémentation des modifications pour LA tâche unique, en suivant mon plan.
[...implémentation des changements...]

# Implementation: 5 - Record progress and determine next steps
Je vais maintenant enregistrer une auto-évaluation honnête.
[...appel OBLIGATOIRE de mcp_MemoryBankMCP_remember, en utilisant `user_message` UNIQUEMENT si un problème critique a été découvert...]
**WORKFLOW** : Remember déterminera la prochaine étape (automatiquement experience-execution).