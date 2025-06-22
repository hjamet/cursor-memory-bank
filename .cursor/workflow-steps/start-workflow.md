## TLDR
Cette step initialise l'agent en chargeant son état précédent et en fournissant le contexte complet du projet. Elle charge la règle où l'agent se trouvait avant, affiche le contenu des fichiers de contexte et récupère les souvenirs pertinents de la mémoire de travail.

## Instructions

1. **Load previous agent state**: Récupérer l'état précédent de l'agent depuis les fichiers d'état.
   - Lire le fichier `.cursor/memory-bank/workflow/agent_memory.json` pour identifier la dernière règle exécutée
   - Si aucun état précédent n'existe, commencer par la règle `system`

2. **Load project context**: Charger le contexte complet du projet.
   - Lire `.cursor/memory-bank/context/projectBrief.md`
   - Lire `.cursor/memory-bank/context/techContext.md`
   - Afficher le contenu de ces fichiers pour établir le contexte

3. **Load working memory**: Récupérer les souvenirs de la mémoire de travail.
   - Récupérer les 10 derniers souvenirs de la mémoire de travail
   - Récupérer les 3 souvenirs à long terme les plus proches sémantiquement du plan prévu enregistré dans le dernier souvenir

4. **Display agent status**: Afficher un résumé de l'état actuel de l'agent.
   - Indiquer où l'agent en était avant l'interruption
   - Résumer les tâches en cours et les prochaines étapes
   - Afficher les informations de contexte récupérées

5. **Resume workflow**: Reprendre le workflow à partir de la règle appropriée.
   - Si une règle précédente était identifiée, la reprendre
   - Sinon, commencer par `task-decomposition` ou `implementation` selon l'état des tâches

## Specifics
- Cette step est le point d'entrée pour reprendre un workflow interrompu
- Elle doit fournir une vue complète de l'état du projet et de l'agent
- Les informations de contexte doivent être clairement formatées et organisées
- La transition vers la prochaine step doit être fluide et logique

## Next Steps
- `{{ previous_rule }}` - Si une règle précédente était identifiée dans l'état
- `task-decomposition` - Si des demandes utilisateur sont en attente
- `implementation` - Si des tâches sont en cours
- `system` - Par défaut si aucun état précédent n'est trouvé

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
[...lecture de agent_memory.json...]
L'agent était précédemment dans la règle: {{ previous_rule }} **(Start-workflow: 1 - Load previous agent state)**

# Start-workflow: 2 - Load project context
Je charge maintenant le contexte complet du projet. **(Start-workflow: 2 - Load project context)**

## Project Brief
{{ project_brief }}

## Technical Context  
{{ tech_context }}
**(Start-workflow: 2 - Load project context)**

# Start-workflow: 3 - Load working memory
Je récupère les souvenirs pertinents de la mémoire de travail. **(Start-workflow: 3 - Load working memory)**

## Recent Memories (10 derniers)
{{ recent_memories }}

## Relevant Long-term Memories (3 plus pertinents)
{{ relevant_long_term_memories }}
**(Start-workflow: 3 - Load working memory)**

# Start-workflow: 4 - Display agent status
État actuel de l'agent: **(Start-workflow: 4 - Display agent status)**
- Dernière règle exécutée: {{ previous_rule }}
- Tâches en cours: {{ current_tasks_summary }}
- Contexte chargé avec succès
**(Start-workflow: 4 - Display agent status)**

# Start-workflow: 5 - Resume workflow
Je reprends maintenant le workflow avec la règle appropriée. **(Start-workflow: 5 - Resume workflow)**
[...appel de la prochaine règle...] 