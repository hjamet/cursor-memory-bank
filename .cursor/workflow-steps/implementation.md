## TLDR
Implémente méthodiquement les tâches prioritaires du projet en analysant le contexte, en exécutant les modifications nécessaires, et en gérant les dépendances entre tâches.

## Instructions

1. **Task analysis**: Analyser les tâches à implémenter.
   - Lire le fichier `.cursor/memory-bank/workflow/tasks.md`
   - Identifier les tâches avec le statut ⚪️ TODO ou 🟡 IN_PROGRESS
   - Prioriser selon l'ordre d'apparition et les dépendances

2. **Active context update**: Mettre à jour le contexte actif.
   - Mettre à jour `.cursor/memory-bank/context/activeContext.md` avec les tâches en cours
   - Documenter les décisions prises et les approches choisies

3. **Implementation**: Implémenter les modifications nécessaires.
   - Utiliser les outils appropriés (`edit_file`, `codebase_search`, etc.)
   - Suivre les conventions établies dans `techContext.md`
   - Marquer les tâches comme 🟡 IN_PROGRESS pendant l'implémentation

4. **Task status update**: Mettre à jour le statut des tâches.
   - Marquer les tâches terminées comme 🟢 DONE
   - Documenter les modifications apportées

5. **Call next step**: Appeler la prochaine étape appropriée.
   - `test-implementation` si de nouveaux comportements doivent être testés
   - `context-update` pour finaliser les changements
   - `fix` si des problèmes sont détectés

## Specifics
- Travailler sur une tâche à la fois pour maintenir la cohérence
- Documenter les décisions importantes dans le contexte actif
- Respecter les conventions de code établies
- Tester les modifications localement si possible

## Next Steps
- `test-implementation` - Si de nouveaux comportements stables doivent être testés
- `context-update` - Pour finaliser et commiter les changements
- `fix` - Si des problèmes sont détectés pendant l'implémentation

## Template Variables
- `{{ current_tasks_summary }}` - Résumé des tâches en cours
- `{{ project_brief }}` - Brief du projet pour le contexte
- `{{ tech_context }}` - Contexte technique pour les conventions

## Example

# Implementation: 1 - Task analysis
Je commence par analyser les tâches à implémenter. **(Implementation: 1 - Task analysis)**
[...lecture de tasks.md...]
J'ai identifié {{ current_tasks_summary }} **(Implementation: 1 - Task analysis)**

# Implementation: 2 - Active context update
Je mets à jour le contexte actif avec les tâches en cours. **(Implementation: 2 - Active context update)**
[...mise à jour d'activeContext.md...]
**(Implementation: 2 - Active context update)**

# Implementation: 3 - Implementation
Je procède maintenant à l'implémentation des modifications. **(Implementation: 3 - Implementation)**
[...implémentation des changements...]
**(Implementation: 3 - Implementation)**

# Implementation: 4 - Task status update
Je mets à jour le statut des tâches terminées. **(Implementation: 4 - Task status update)**
[...mise à jour de tasks.md...]
**(Implementation: 4 - Task status update)**

# Implementation: 5 - Call next step
Je vais maintenant appeler la prochaine étape appropriée. **(Implementation: 5 - Call next step)**
[...appel de la prochaine étape...]