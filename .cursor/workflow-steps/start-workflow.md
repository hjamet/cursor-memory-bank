## TLDR
Cette step initialise l'agent en chargeant son état précédent et en fournissant le contexte complet du projet. Elle charge la règle où l'agent se trouvait avant, affiche le contenu des fichiers de contexte et récupère les souvenirs pertinents de la mémoire de travail.

## Instructions

1. **Load previous agent state**: Récupérer l'état précédent de l'agent depuis les fichiers d'état.
   - Lire le fichier `.cursor/memory-bank/workflow/agent_memory.json` pour identifier la dernière règle exécutée
   - Si aucun état précédent n'existe, commencer par la règle `system`

2. **Load project context**: Charger le contexte complet du projet.
   - Le contexte du projet (projectBrief et techContext) est automatiquement chargé et disponible
   - Ces informations sont intégrées dans le contexte de la règle

3. **Load working memory**: Récupérer les souvenirs de la mémoire de travail.
   - Récupérer les 10 derniers souvenirs de la mémoire de travail
   - Récupérer les 3 souvenirs à long terme les plus proches sémantiquement du plan prévu enregistré dans le dernier souvenir

4. **Display agent status**: Afficher un résumé de l'état actuel de l'agent.
   - Indiquer où l'agent en était avant l'interruption
   - Résumer les tâches en cours et les prochaines étapes
   - Afficher les informations de contexte récupérées

5. **Record state and determine next steps**: Enregistrer l'état actuel et déterminer les prochaines étapes.
   - Utiliser l'outil `remember` pour enregistrer l'état de démarrage
   - L'outil `remember` indiquera les règles suivantes possibles

## Specifics
- Cette step est le point d'entrée pour reprendre un workflow interrompu
- Elle doit fournir une vue complète de l'état du projet et de l'agent
- Les informations de contexte doivent être clairement formatées et organisées
- La transition vers la prochaine step doit être fluide et logique
- Les objets mémoire doivent être formatés avec JSON.stringify pour un affichage lisible

## Next Steps
- `task-decomposition` - Si des demandes utilisateur sont en attente
- `implementation` - Si des tâches sont en cours
- `context-update` - Si une mise à jour du contexte est nécessaire
- `fix` - Si des problèmes ont été détectés
- `experience-execution` - Si des tests manuels sont requis

## Template Variables
- `{{ project_brief }}` - Contenu du fichier projectBrief.md
- `{{ tech_context }}` - Contenu du fichier techContext.md  
- `{{ recent_memories }}` - Les 10 derniers souvenirs de la mémoire de travail
- `{{ relevant_long_term_memories }}` - Les 3 souvenirs à long terme les plus pertinents
- `{{ previous_rule }}` - La dernière règle exécutée par l'agent
- `{{ current_tasks_summary }}` - Résumé des tâches en cours

## Example

# Start-workflow: 1 - Load previous agent state
Je commence par charger l'état précédent de l'agent pour comprendre où il en était. **(Start-workflow: 1 - Load previous agent state)**

L'agent était précédemment dans la règle: **{{ previous_rule }}** **(Start-workflow: 1 - Load previous agent state)**

# Start-workflow: 2 - Load project context  
Le contexte complet du projet (projectBrief et techContext) est automatiquement chargé et disponible dans le contexte de cette règle. **(Start-workflow: 2 - Load project context)**

# Start-workflow: 3 - Load working memory
Je récupère les souvenirs pertinents de la mémoire de travail. **(Start-workflow: 3 - Load working memory)**

## Recent Memories (10 derniers)
```json
{{ recent_memories | map(memory => JSON.stringify(memory, null, 2)) | join('\n\n') }}
```

## Relevant Long-term Memories (3 plus pertinents)
```json
{{ relevant_long_term_memories | map(memory => JSON.stringify(memory, null, 2)) | join('\n\n') }}
```
**(Start-workflow: 3 - Load working memory)**

# Start-workflow: 4 - Display agent status
État actuel de l'agent: **(Start-workflow: 4 - Display agent status)**
- Dernière règle exécutée: **{{ previous_rule }}**
- Tâches en cours: **{{ current_tasks_summary }}**
- Contexte chargé avec succès
**(Start-workflow: 4 - Display agent status)**

# Start-workflow: 5 - Record state and determine next steps
Je vais maintenant enregistrer l'état de démarrage et déterminer les prochaines étapes appropriées. **(Start-workflow: 5 - Record state and determine next steps)**
[...appel de l'outil remember...]
**(Start-workflow: 5 - Record state and determine next steps)** 