## Contexte

Lors de l'implémentation du système de roadmap centralisée, j'ai défini un format de nommage pour les fichiers de tâches incluant la date : `{titre-kebab-case}_{DD-MM-YYYY}.md`. Cependant, cela nécessite d'exécuter une commande terminal pour obtenir la date actuelle à chaque création de tâche, ce qui ajoute de la friction inutile.

L'utilisateur préfère simplifier le système en supprimant les timestamps des noms de fichiers. Cela rendra la création de tâches plus fluide et moins dépendante d'outils externes.

## Objectif

Simplifier le format de nommage des fichiers de tâches en supprimant les timestamps (dates) des noms de fichiers. Adapter toutes les commandes et règles qui génèrent ces noms de fichiers pour utiliser un format simplifié sans date.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/task.md` : Commande qui génère les noms de fichiers avec date `{titre-kebab-case}_{DD-MM-YYYY}.md`
- `.cursor/rules/agent.mdc` : Règle qui explique le format de nommage avec date
- `.cursor/commands/agent.md` : Commande qui lit les fichiers de tâches (peut avoir des références au format)
- `.cursor/agents/TEMPLATE.md` : Template qui documente le format de nommage actuel

### Fichiers à modifier :
- `.cursor/commands/task.md` : Supprimer la génération de date dans les noms de fichiers
- `.cursor/rules/agent.mdc` : Adapter la section sur le format de nommage pour supprimer les dates
- `.cursor/agents/TEMPLATE.md` : Mettre à jour la documentation du format
- `.cursor/agents/roadmap.yaml` : Vérifier si les entrées existantes doivent être migrées (probablement pas nécessaire)

### Recherches à effectuer :
- Recherche sémantique : "Où sont générés les noms de fichiers de tâches avec format de date ?"
- Recherche sémantique : "Quels fichiers référencent le format de nommage avec date DD-MM-YYYY ?"

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun pour le moment

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-simplifier-nommage-taches.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre le format actuel et où il est utilisé
2. **EFFECTUE les recherches sémantiques** mentionnées pour identifier toutes les références au format de nommage avec date
3. **IDENTIFIE** un nouveau format de nommage simple sans date (ex: `{titre-kebab-case}.md` ou `{titre-kebab-case}_{id}.md`)
4. **VERIFIE** l'impact sur les fichiers existants dans `.cursor/agents/` - faut-il renommer les fichiers existants ?
5. **ATTEINS une compréhension approfondie** de tous les endroits où le format doit être changé
6. **DISCUTE avec l'utilisateur** pour clarifier :
   - Quel format de nommage préfère-t-il ? (ex: `{titre-kebab-case}.md`, `{titre-kebab-case}_{id}.md`)
   - Faut-il renommer les fichiers existants ou les garder avec leur nom actuel ?
   - Comment gérer les collisions potentielles si deux tâches ont le même titre ?
7. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
8. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer tout travail de modification. L'exploration est OBLIGATOIRE, pas optionnelle.

