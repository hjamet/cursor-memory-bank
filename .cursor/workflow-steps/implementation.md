## TLDR
Implémente méthodiquement les tâches prioritaires du projet en analysant le contexte, en exécutant les modifications nécessaires, et en gérant les dépendances entre tâches en utilisant les outils MCP.

## Instructions

1. **Task analysis**: Analyser les tâches à implémenter.
   - Utiliser `mcp_MemoryBankMCP_get_next_tasks` pour obtenir les tâches disponibles
   - Identifier les tâches avec le statut TODO ou IN_PROGRESS
   - Prioriser selon les priorités et les dépendances

2. **Implementation**: Implémenter les modifications nécessaires.
   - Utiliser les outils appropriés (`edit_file`, `codebase_search`, etc.)
   - Suivre les conventions établies dans le contexte technique
   - Marquer les tâches comme IN_PROGRESS pendant l'implémentation avec `mcp_MemoryBankMCP_update_task`

3. **Task status update**: Mettre à jour le statut des tâches.
   - Marquer les tâches terminées comme DONE avec `mcp_MemoryBankMCP_update_task`
   - Documenter les modifications apportées dans les commentaires de tâche

4. **Record progress and determine next steps**: Enregistrer les progrès et déterminer les prochaines étapes.
   - Utiliser `mcp_MemoryBankMCP_remember` pour enregistrer l'état actuel
   - L'outil remember indiquera les prochaines étapes appropriées

## Specifics
- Travailler sur une tâche à la fois pour maintenir la cohérence
- Utiliser les outils MCP pour toute gestion de tâches
- Respecter les conventions de code établies
- Tester les modifications localement si possible
- Documenter les décisions importantes dans les souvenirs

## Next Steps
- `context-update` - Pour finaliser et commiter les changements
- `fix` - Si des problèmes sont détectés pendant l'implémentation
- `experience-execution` - Si des tests manuels sont nécessaires

## Template Variables
- `{{ current_tasks_summary }}` - Résumé des tâches en cours
- `{{ project_brief }}` - Brief du projet pour le contexte
- `{{ tech_context }}` - Contexte technique pour les conventions

## Example

# Implementation: 1 - Task analysis
Je commence par analyser les tâches à implémenter. **(Implementation: 1 - Task analysis)**
[...appel de mcp_MemoryBankMCP_get_next_tasks...]
J'ai identifié {{ current_tasks_summary }} **(Implementation: 1 - Task analysis)**

# Implementation: 2 - Implementation
Je procède maintenant à l'implémentation des modifications. **(Implementation: 2 - Implementation)**
[...mise à jour du statut avec mcp_MemoryBankMCP_update_task...]
[...implémentation des changements...]
**(Implementation: 2 - Implementation)**

# Implementation: 3 - Task status update
Je mets à jour le statut des tâches terminées. **(Implementation: 3 - Task status update)**
[...appel de mcp_MemoryBankMCP_update_task pour marquer comme DONE...]
**(Implementation: 3 - Task status update)**

# Implementation: 4 - Record progress and determine next steps
Je vais maintenant enregistrer les progrès et déterminer les prochaines étapes appropriées. **(Implementation: 4 - Record progress and determine next steps)**
[...appel de mcp_MemoryBankMCP_remember...]
**(Implementation: 4 - Record progress and determine next steps)**