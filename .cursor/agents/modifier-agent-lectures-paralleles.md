## Contexte

Lors de l'exécution de la commande `/agent`, l'agent lit successivement de nombreux fichiers (fichier de tâche, fichiers listés dans « Fichiers Concernés », README, règles). Or, ces lectures sont indépendantes et doivent toutes être réalisées avant la présentation. En l'état, les lectures séquentielles rallongent le temps de sélection/présentation, alors qu'elles pourraient être parallélisées sans changer le résultat.

## Objectif

Explorer et concevoir une amélioration de `/agent` pour paralléliser au maximum les lectures nécessaires au chargement de contexte (tous les fichiers mentionnés par la tâche sélectionnée, README, règles et rapports liés), afin de réduire la latence perçue avant la présentation de la tâche.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Source de vérité des tâches et métadonnées utilisées pour la sélection
- `.cursor/rules/agent.mdc` : Règle de sélection/chargement et exigences d'exploration exhaustive

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/agents/TEMPLATE.md` : Format attendu des fichiers de tâches (sections obligatoires)
- `README.md` : Décrit le comportement attendu de `/agent` et l'exploration exhaustive
- `.cursor/commands/agent.md` : Si présent, spécifie la commande slash et ses attentes UX

### Recherches à effectuer :
- Recherche sémantique : « Où sont lues les sections de la tâche sélectionnée ? »
- Recherche sémantique : « Comment sont enchaînées les lectures des fichiers liés (rapports, README) ? »
- Documentation : Lire `README.md` et `.cursor/rules/agent.mdc` pour lister les fichiers à charger systématiquement

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-*` : Rapports liés aux tâches parentes/corrélées pouvant être mentionnés dans « Fichiers Concernés »

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-modifier-agent-lectures-paralleles.md`

## Instructions de Collaboration

- Il est INTERDIT de commencer à implémenter immédiatement.
- Tu DOIS lire EXHAUSTIVEMENT tous les fichiers listés dans « Fichiers Concernés » avant toute action.
- Tu DOIS effectuer les recherches sémantiques mentionnées et recenser toutes les lectures systématiques de `/agent`.
- Tu DOIS lire le README et `.cursor/rules/agent.mdc` pour cadrer l'attendu exact (exploration exhaustive avant présentation).
- Tu DOIS discuter avec l'utilisateur pour valider la stratégie de parallélisation (lots de lectures, limites, ordre des erreurs, fail-fast) et les contraintes de robustesse.
- Tu DOIS écrire le rapport final dans le fichier output mentionné.
- Ce n'est QU'APRÈS cette exploration et la planification convenue que tu pourras commencer l'implémentation.


