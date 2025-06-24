## TLDR
Implémente méthodiquement UNE SEULE tâche prioritaire du projet en analysant le contexte, en exécutant les modifications nécessaires, et en respectant strictement le workflow autonome. **ATTENTION : Ne traiter qu'UNE SEULE tâche par cycle d'implémentation.**

## Instructions

1. **Task analysis**: Analyser LA tâche à implémenter (UNE SEULE).
   - Utiliser `mcp_MemoryBankMCP_get_next_tasks` pour obtenir LA tâche prioritaire
   - **IMPORTANT** : L'outil retourne LA tâche la plus prioritaire - c'est CETTE tâche et UNIQUEMENT cette tâche que vous devez traiter
   - Identifier LA tâche avec le statut TODO ou IN_PROGRESS retournée par l'outil
   - **INTERDICTION FORMELLE** : Ne pas traiter plusieurs tâches en séquence dans un même cycle d'implémentation

2. **Implementation**: Implémenter les modifications nécessaires pour LA tâche unique.
   - Utiliser les outils appropriés (`edit_file`, `codebase_search`, etc.)
   - Suivre les conventions établies dans le contexte technique
   - Marquer LA tâche comme IN_PROGRESS pendant l'implémentation avec `mcp_MemoryBankMCP_update_task`
   - **FOCUS ABSOLU** : Concentrez-vous uniquement sur cette tâche, ses sous-tâches éventuelles, mais JAMAIS sur d'autres tâches

3. **Task status update**: Mettre à jour le statut de LA tâche terminée.
   - Marquer LA tâche terminée comme REVIEW avec `mcp_MemoryBankMCP_update_task` pour que l'utilisateur la valide.
   - Documenter les modifications apportées dans les commentaires de tâche
   - **RAPPEL** : Une seule tâche = un seul update de statut

4. **Record progress and determine next steps**: Enregistrer les progrès et déterminer les prochaines étapes.
   - **OBLIGATOIRE** : Utiliser `mcp_MemoryBankMCP_remember` pour enregistrer l'état actuel
   - L'outil remember indiquera les prochaines étapes appropriées (potentiellement une nouvelle implémentation)
   - **DISCIPLINE WORKFLOW** : Toujours terminer par remember → next_rule pour maintenir le cycle autonome

## Specifics - RÈGLES STRICTES
- **RÈGLE #1** : Travailler sur UNE SEULE tâche à la fois - JAMAIS plusieurs tâches en séquence
- **RÈGLE #2** : LA tâche à traiter est celle retournée par `mcp_MemoryBankMCP_get_next_tasks` - pas d'autres
- **RÈGLE #3** : Terminer OBLIGATOIREMENT par `mcp_MemoryBankMCP_remember` pour maintenir le workflow
- **RÈGLE #4** : Ne pas décider arbitrairement de traiter d'autres tâches "tant qu'on y est"
- **RÈGLE #5** : Si une tâche semble liée à d'autres, traiter UNIQUEMENT la tâche prioritaire retournée par l'outil
- **RÈGLE #6** : Les sous-tâches sont autorisées UNIQUEMENT si elles font partie intégrante de la tâche principale
- Utiliser les outils MCP pour toute gestion de tâches
- Respecter les conventions de code établies
- Tester les modifications localement si possible
- Documenter les décisions importantes dans les souvenirs

## ⚠️ ANTI-DRIFT WARNINGS ⚠️
- **INTERDIT** : Traiter plusieurs tâches "pour être efficace" - c'est contre-productif
- **INTERDIT** : Ignorer l'appel à remember à la fin - cela casse le workflow autonome
- **INTERDIT** : Décider soi-même quelle tâche traiter - utiliser next_rule/get_next_tasks
- **INTERDIT** : Continuer sur d'autres tâches après avoir terminé la tâche principale
- **INTERDIT** : Se dire "pendant que j'y suis, je vais aussi faire..." - NON, une seule tâche
- **INTERDIT** : Traiter des tâches "évidentes" ou "rapides" en plus de la tâche principale
- **INTERDIT** : Grouper des tâches similaires ensemble - chaque tâche doit être traitée individuellement
- **INTERDIT** : Sauter l'étape remember sous prétexte de "continuer directement"

## 🎯 SINGLE-TASK FOCUS ENFORCEMENT
- **MANTRA** : "Une tâche, un cycle, un focus"
- **VÉRIFICATION** : Avant chaque action, demandez-vous "Est-ce que cela concerne MA tâche unique ?"
- **LIMITE** : Si vous voyez d'autres problèmes, les noter dans remember mais NE PAS les traiter
- **CYCLE COMPLET** : Task analysis → Implementation → Status update → Remember → STOP
- **PROCHAINE TÂCHE** : Sera déterminée par le prochain appel à next_rule, pas par vous

## Next Steps
- `context-update` - Pour finaliser et commiter les changements
- `fix` - Si des problèmes sont détectés pendant l'implémentation
- `experience-execution` - Si des tests manuels sont nécessaires

## Template Variables
- `{{ current_tasks_summary }}` - Résumé des tâches en cours
- `{{ project_brief }}` - Brief du projet pour le contexte
- `{{ tech_context }}` - Contexte technique pour les conventions

## Example - SINGLE TASK WORKFLOW

# Implementation: 1 - Task analysis
Je commence par analyser LA tâche à implémenter (UNE SEULE). **(Implementation: 1 - Task analysis)**
[...appel de mcp_MemoryBankMCP_get_next_tasks...]
J'ai identifié LA tâche prioritaire : {{ current_tasks_summary }} 
**FOCUS** : Je vais traiter UNIQUEMENT cette tâche et aucune autre. **(Implementation: 1 - Task analysis)**

# Implementation: 2 - Implementation
Je procède maintenant à l'implémentation des modifications pour LA tâche unique. **(Implementation: 2 - Implementation)**
[...mise à jour du statut avec mcp_MemoryBankMCP_update_task...]
[...implémentation des changements pour CETTE tâche uniquement...]
**DISCIPLINE** : Je me concentre exclusivement sur cette tâche. **(Implementation: 2 - Implementation)**

# Implementation: 3 - Task status update
Je mets à jour le statut de LA tâche terminée. **(Implementation: 3 - Task status update)**
[...appel de mcp_MemoryBankMCP_update_task pour marquer CETTE tâche comme REVIEW...]
**TERMINÉ** : Cette tâche unique est maintenant complétée et en attente de revue. **(Implementation: 3 - Task status update)**

# Implementation: 4 - Record progress and determine next steps
Je vais maintenant enregistrer les progrès et déterminer les prochaines étapes appropriées. **(Implementation: 4 - Record progress and determine next steps)**
[...appel OBLIGATOIRE de mcp_MemoryBankMCP_remember...]
**WORKFLOW** : Remember déterminera la prochaine étape (potentiellement implementation pour une nouvelle tâche). **(Implementation: 4 - Record progress and determine next steps)**