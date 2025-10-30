## Contexte

La commande `/task` est utilisée pour ajouter rapidement des travaux à la roadmap sans interrompre le flux en cours. Dans la pratique, elle peut être invoquée à n'importe quel moment (au milieu d'une autre commande, en séquence, ou entourée de commentaires). Il est nécessaire d'acter que `/task` est toujours prioritaire mais strictement temporaire : l'agent doit ajouter la ou les tâches demandées, confirmer, puis reprendre immédiatement le travail précédent comme si de rien n'était.

## Objectif

Explorer et cadrer le comportement de `/task` afin qu'elle soit traitée systématiquement comme une interruption non‑bloquante et temporaire, avec priorité d'exécution immédiate limitée à la seule création des tâches (aucune planification/implémentation), puis reprise du flux initial.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Source de vérité pour enregistrer les nouvelles tâches
- `README.md` : Comporte la description du système de roadmap et des commandes
- `.cursor/rules/agent.mdc` : Règle sur la gestion de la roadmap et interruptions non‑bloquantes

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/agents/TEMPLATE.md` : Format attendu des fichiers de tâches (sections obligatoires)
- `.cursor/commands/task.md` : Spécification utilisateur de la commande (si présent)

### Recherches à effectuer :
- Recherche sémantique : « Comment `/task` est-il géré et où s'insère-t-il dans le flux ? »
- Recherche sémantique : « Comment l'agent reprend-il le travail précédent après une interruption ? »
- Documentation : Consolider les règles d'interruption non‑bloquante dans `README.md`

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-*` : Rapports liés pouvant préciser le comportement historique

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-prioriser-et-rendre-temporaire-la-commande-task.md`

## Instructions de Collaboration

- Il est INTERDIT de commencer à implémenter quoi que ce soit immédiatement.
- Tu DOIS lire EXHAUSTIVEMENT tous les fichiers listés dans « Fichiers Concernés ».
- Tu DOIS définir précisément les cas d'usage (enchaînements `/task`, `/agent /task ...`, commentaires intercalés) et les règles de priorité/résumption.
- Tu DOIS discuter avec l'utilisateur pour valider le wording des confirmations minimales et les cas limites.
- Tu DOIS écrire le rapport final dans le fichier output mentionné.
- Ce n'est QU'APRÈS cette exploration et planification que tu pourras envisager une implémentation.

