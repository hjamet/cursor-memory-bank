## TLDR
Implémente méthodiquement UNE SEULE tâche prioritaire du projet en analysant le contexte, en exécutant les modifications nécessaires, et en respectant strictement le workflow autonome. **ATTENTION : Ne traiter qu'UNE SEULE tâche par cycle d'implémentation.**

## Instructions

1.  **Task analysis and status update**: Analyser LA tâche à implémenter (UNE SEULE) et la marquer immédiatement comme IN_PROGRESS.
    *   Utiliser `mcp_MemoryBankMCP_get_next_tasks` pour obtenir LA tâche prioritaire
    *   **IMPORTANT** : L'outil retourne LA tâche la plus prioritaire - c'est CETTE tâche et UNIQUEMENT cette tâche que vous devez traiter
    *   Identifier LA tâche avec le statut TODO ou IN_PROGRESS retournée par l'outil
    *   **MARQUAGE OBLIGATOIRE** : Dès qu'une tâche est identifiée, la marquer IMMÉDIATEMENT comme IN_PROGRESS avec `mcp_MemoryBankMCP_update_task`
    *   **INTERDICTION FORMELLE** : Ne pas traiter plusieurs tâches en séquence dans un même cycle d'implémentation

2.  **Analyse du contexte et Plan d'implémentation**: Analyser le code existant pour garantir la cohérence et la réutilisation.
    *   **Recherche de contexte**: Effectuer jusqu'à 3 recherches sémantiques (`codebase_search`) pour identifier le code existant en rapport avec la tâche.
    *   **Objectifs de la recherche**:
        *   Identifier les composants, fonctions ou patterns réutilisables.
        *   Comprendre les conventions de code, le style, les bibliothèques utilisées et les patterns architecturaux du projet.
    *   **Synthèse et Planification**: Analyser les résultats des recherches et formuler un plan d'implémentation. Ce plan doit explicitement décrire :
        *   Comment le code existant sera réutilisé. **Prioriser fortement la réutilisation des composants existants, même s'ils nécessitent des modifications mineures, plutôt que de réimplémenter une fonctionnalité similaire. La réécriture doit être une exception, pas la norme.**
        *   Comment le nouveau code s'alignera sur les pratiques existantes (nommage, structure des fonctions, documentation, style, etc.).
        *   Le même type de fonction, les mêmes types de déclarations, les mêmes types de docstring, le même type d'écriture, de commentaires, le même style graphique si l'application est visuelle, les mêmes bibliothèques autant que possible, de manière à minimiser les imports, etc.
    *   **Principe directeur**: Partir du principe que le code actuel est fonctionnel et constitue la meilleure référence. L'objectif est de s'intégrer de manière transparente pour ne pas introduire d'erreurs, pas de réinventer la roue.

3.  **Implementation**: Implémenter les modifications nécessaires pour LA tâche unique, en suivant le plan établi.
    *   Utiliser les outils appropriés (`edit_file`, `regex_edit`, `grep_search`, etc.)
    *   Suivre les conventions établies dans le contexte technique et le plan d'implémentation.
    *   **RAPPEL** : La tâche a déjà été marquée comme IN_PROGRESS à l'étape 1
    *   **FOCUS ABSOLU** : Concentrez-vous uniquement sur cette tâche, ses sous-tâches éventuelles, mais JAMAIS sur d'autres tâches.
    *   **EXCEPTION**: Si la tâche ne nécessite que l'exécution de commandes, une validation ou des expériences sans modification de code (par exemple, "vérifier que cette commande fonctionne"), vous pouvez appeler `mcp_MemoryBankMCP_next_rule` avec `step_name: 'experience-execution'` pour passer directement aux tests.

4.  **Task status update**: Mettre à jour le statut de LA tâche terminée.
    *   Marquer LA tâche terminée comme REVIEW avec `mcp_MemoryBankMCP_update_task` pour que l'utilisateur la valide.
    *   Documenter les modifications apportées dans les commentaires de tâche
    *   **RAPPEL** : Une seule tâche = un seul update de statut

5.  **Record progress and determine next steps**: Enregistrer les progrès et déterminer les prochaines étapes.
    *   **OBLIGATOIRE** : Utiliser `mcp_MemoryBankMCP_remember` pour enregistrer l'état actuel
    *   L'outil remember indiquera les prochaines étapes appropriées (potentiellement une nouvelle implémentation)
    *   **DISCIPLINE WORKFLOW** : Toujours terminer par remember → next_rule pour maintenir le cycle autonome
    *   **Communication**: N'utiliser le paramètre `user_message` de `remember` que pour signaler un problème majeur ou une décision d'implémentation critique qui s'écarte du plan initial. En temps normal, la communication est superflue et ce paramètre doit être omis.

## Specifics - RÈGLES STRICTES
- **RÈGLE #1** : Travailler sur UNE SEULE tâche à la fois - JAMAIS plusieurs tâches en séquence
- **RÈGLE #2** : LA tâche à traiter est celle retournée par `mcp_MemoryBankMCP_get_next_tasks` - pas d'autres
- **RÈGLE #3** : MARQUER IMMÉDIATEMENT la tâche comme IN_PROGRESS dès l'étape 1 - AUCUNE EXCEPTION
- **RÈGLE #4** : Terminer OBLIGATOIREMENT par `mcp_MemoryBankMCP_remember` pour maintenir le workflow
- **RÈGLE #5** : Ne pas décider arbitrairement de traiter d'autres tâches "tant qu'on y est"
- **RÈGLE #6** : Si une tâche semble liée à d'autres, traiter UNIQUEMENT la tâche prioritaire retournée par l'outil
- **RÈGLE #7** : Les sous-tâches sont autorisées UNIQUEMENT si elles font partie intégrante de la tâche principale
- Utiliser les outils MCP pour toute gestion de tâches
- Respecter les conventions de code établies
- Tester les modifications localement si possible
- Documenter les décisions importantes dans les souvenirs

## ⚠️ ANTI-DRIFT WARNINGS ⚠️
- **INTERDIT** : Traiter plusieurs tâches "pour être efficace" - c'est contre-productif
- **INTERDIT** : Oublier de marquer la tâche comme IN_PROGRESS à l'étape 1 - c'est OBLIGATOIRE
- **INTERDIT** : Ignorer l'appel à remember à la fin - cela casse le workflow autonome
- **INTERDIT** : Décider soi-même quelle tâche traiter - utiliser next_rule/get_next_tasks
- **INTERDIT** : Continuer sur d'autres tâches après avoir terminé la tâche principale
- **INTERDIT** : Se dire "pendant que j'y suis, je vais aussi faire..." - NON, une seule tâche
- **INTERDIT** : Traiter des tâches "évidentes" ou "rapides" en plus de la tâche principale
- **INTERDIT** : Grouper des tâches similaires ensemble - chaque tâche doit être traitée individuellement
- **INTERDIT** : Sauter l'étape remember sous prétexte de "continuer directement"
- **INTERDIT** : Passer à experience-execution sans marquer la tâche IN_PROGRESS

## 🎯 SINGLE-TASK FOCUS ENFORCEMENT
- **MANTRA** : "Une tâche, un cycle, un focus"
- **VÉRIFICATION** : Avant chaque action, demandez-vous "Est-ce que cela concerne MA tâche unique ?"
- **LIMITE** : Si vous voyez d'autres problèmes, les noter dans remember mais NE PAS les traiter
- **CYCLE COMPLET** : Task analysis & status update → Context analysis & Plan → Implementation → Status update → Remember → STOP
- **PROCHAINE TÂCHE** : Sera déterminée par le prochain appel à next_rule, pas par vous
- **MARQUAGE SYSTÉMATIQUE** : Toute tâche identifiée DOIT être marquée IN_PROGRESS immédiatement, sans exception

## Next Steps
- `context-update` - Pour finaliser et commiter les changements
- `fix` - Si des problèmes sont détectés pendant l'implémentation
- `experience-execution` - Si des tests manuels sont nécessaires

## Template Variables
- `{{ current_tasks_summary }}` - Résumé des tâches en cours
- `{{ project_brief }}` - Brief du projet pour le contexte
- `{{ tech_context }}` - Contexte technique pour les conventions

## Example - SINGLE TASK WORKFLOW

# Implementation: 1 - Task analysis and status update
Je commence par analyser LA tâche à implémenter (UNE SEULE) et la marquer immédiatement comme IN_PROGRESS. **(Implementation: 1 - Task analysis and status update)**
[...appel de mcp_MemoryBankMCP_get_next_tasks...]
J'ai identifié LA tâche prioritaire : {{ current_tasks_summary }} 
**MARQUAGE OBLIGATOIRE** : Je marque immédiatement cette tâche comme IN_PROGRESS pour garantir qu'elle ne soit pas oubliée.
[...appel OBLIGATOIRE de mcp_MemoryBankMCP_update_task pour marquer la tâche IN_PROGRESS...]
**FOCUS** : Je vais traiter UNIQUEMENT cette tâche et aucune autre. **(Implementation: 1 - Task analysis and status update)**

# Implementation: 2 - Analyse du contexte et Plan d'implémentation
Je recherche dans la base de code pour comprendre les conventions et identifier le code à réutiliser. **(Implementation: 2 - Analyse du contexte et Plan d'implémentation)**
[...appel de `codebase_search` (jusqu'à 3 fois)...]
**Analyse et Plan**: Après avoir analysé les résultats, voici mon plan d'implémentation pour garantir la cohérence et la réutilisation :
- [Point 1 du plan, ex: Réutiliser la fonction `existingFunction` pour...]
- [Point 2 du plan, ex: Créer une nouvelle fonction `newFunction` en suivant le style de `similarFunction`...]
- [Point 3 du plan, ex: Utiliser la bibliothèque `existing-lib` déjà présente dans le projet...]
**COHÉRENCE** : Mon implémentation suivra rigoureusement ce plan pour s'intégrer au code existant. **(Implementation: 2 - Analyse du contexte et Plan d'implémentation)**

# Implementation: 3 - Implementation
Je procède maintenant à l'implémentation des modifications pour LA tâche unique, en suivant mon plan. **(Implementation: 3 - Implementation)**
**RAPPEL** : La tâche a déjà été marquée comme IN_PROGRESS à l'étape 1, je peux donc me concentrer sur l'implémentation.
[...implémentation des changements pour CETTE tâche uniquement, en respectant le plan...]
**DISCIPLINE** : Je me concentre exclusivement sur cette tâche. **(Implementation: 3 - Implementation)**

# Implementation: 4 - Task status update
Je mets à jour le statut de LA tâche terminée. **(Implementation: 4 - Task status update)**
[...appel de mcp_MemoryBankMCP_update_task pour marquer CETTE tâche comme REVIEW...]
**TERMINÉ** : Cette tâche unique est maintenant complétée et en attente de revue. **(Implementation: 4 - Task status update)**

# Implementation: 5 - Record progress and determine next steps
Je vais maintenant enregistrer les progrès et déterminer les prochaines étapes appropriées. **(Implementation: 5 - Record progress and determine next steps)**
[...appel OBLIGATOIRE de mcp_MemoryBankMCP_remember...]
**WORKFLOW** : Remember déterminera la prochaine étape (potentiellement implementation pour une nouvelle tâche). **(Implementation: 5 - Record progress and determine next steps)**