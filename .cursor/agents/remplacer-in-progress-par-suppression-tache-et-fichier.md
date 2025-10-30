## Contexte

Dans le cadre de l'évolution de la commande `/agent`, nous avons constaté que le marquage des tâches en `IN_PROGRESS` avec `started_at` complexifie inutilement le flux et crée des états transitoires difficiles à coordonner entre agents. La volonté exprimée est de simplifier radicalement le comportement: à la sélection d'une tâche par `/agent`, ne plus mettre à jour son statut, mais simplement la retirer de la `roadmap.yaml` et supprimer le fichier de tâche associé, afin d'éviter tout état intermédiaire.

## Objectif

Explorer et définir précisément les changements nécessaires pour remplacer le marquage `IN_PROGRESS` par une **suppression immédiate** de l'entrée correspondante dans `roadmap.yaml` ainsi que du fichier de tâche associé lorsque `/agent` sélectionne une tâche.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Source de vérité des tâches; observation de l'usage actuel des champs `status` et `started_at`.
- `.cursor/rules/agent.mdc` : Règle décrivant la gestion de la roadmap et la création autonome de tâches; impact attendu sur la section de sélection/gestion.
- `README.md` : Documentation utilisateur de `/agent` et du système de roadmap; devra refléter le nouveau comportement.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/commands/agent.md` (si présent) : Documentation/commande de l'agent pouvant décrire le flux actuel.
- Historique des tâches liées (ex. `task-3`) qui parlent de supprimer la mise à jour de statut/timestamps pour alignement.

### Recherches à effectuer :
- Recherche sémantique : "Comment `/agent` met à jour `status` et `started_at` actuellement ?"
- Recherche sémantique : "Où la suppression d'une tâche de la roadmap est-elle gérée ?"
- Documentation : Valider que le README et les règles reflètent le nouveau flux sans `IN_PROGRESS`.

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-supprimer-mise-a-jour-statut-timestamps-roadmap.md` (si existant) : Convergence avec cette intention.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-remplacer-in-progress-par-suppression-tache-et-fichier.md`

## Instructions de Collaboration

- Il est INTERDIT de commencer à implémenter immédiatement.
- Tu DOIS lire EXHAUSTIVEMENT tous les fichiers listés plus haut.
- Tu DOIS effectuer les recherches sémantiques et vérifier la documentation.
- Tu DOIS discuter avec l'utilisateur pour cadrer précisément les cas limites (ex. dépendances non résolues, reprise après sélection, annulation).
- Tu DOIS établir un plan d'action détaillé (points d'entrée à modifier, validations, stratégie fail-fast) avant toute modification.
- Tu DOIS écrire le rapport final dans le fichier output indiqué après l'exploration.
- Seulement APRÈS cette exploration exhaustive et planification collaborative, tu peux démarrer l'implémentation.

