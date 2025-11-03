## Contexte

Travail actuel sur l'amélioration de la commande `/task` pour mieux gérer les dépendances bidirectionnelles → besoin d'améliorer aussi la commande `/clean` pour qu'elle maintienne automatiquement la cohérence des dépendances dans la roadmap. La commande `/clean` devrait analyser toutes les paires de tâches pour identifier les dépendances manquantes, similaire à ce qui a été implémenté dans `/task`. De plus, `/clean` devrait créer automatiquement les descriptions manquantes pour les tâches existantes qui n'en ont pas encore.

## Objectif

Améliorer la commande `/clean` pour qu'elle mette à jour automatiquement les dépendances en analysant chaque tâche par rapport à chaque autre tâche. La commande devrait également créer les descriptions manquantes en extrayant l'information depuis les fichiers de tâches ou en générant une description courte à partir du titre.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/clean.md` : La commande `/clean` existante qui nettoie les tâches in-progress
- `.cursor/commands/task.md` : La commande `/task` qui contient la logique d'analyse de dépendances bidirectionnelles à réutiliser
- `.cursor/rules/agent.mdc` : Les règles pour créer des tâches avec des descriptions

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/agents/roadmap.yaml` : Le fichier de roadmap centralisée contenant toutes les tâches avec leurs descriptions et dépendances
- `.cursor/agents/*.md` : Les fichiers de tâches existants qui peuvent être lus pour extraire des descriptions

### Recherches à effectuer :
- Recherche sémantique : "Comment fonctionne l'analyse de dépendances dans task.md ?"
- Recherche sémantique : "Comment sont structurées les tâches dans roadmap.yaml ?"

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ameliorer-clean-pour-mettre-a-jour-les-dependances.md`

## Instructions de Collaboration

**OBLIGATOIRE ET CRITIQUE** : L'agent qui traitera cette tâche DOIT :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** effectuer toutes les recherches sémantiques mentionnées
- **DOIT** lire le README et toute documentation pertinente
- **DOIT** atteindre une compréhension approfondie du contexte et du projet avant toute discussion
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les contraintes techniques, et établir un plan d'action détaillé ensemble
- **DOIT TOUJOURS** créer le fichier de rapport final dans le fichier output mentionné après avoir terminé (voir section "Instructions pour les Rapports Finaux")
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

L'exploration est OBLIGATOIRE, pas optionnelle.

