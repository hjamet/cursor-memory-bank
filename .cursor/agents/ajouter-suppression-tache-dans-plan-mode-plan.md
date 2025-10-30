## Contexte

Lors du travail actuel sur la simplification du système de roadmap et la suppression des statuts/timestamps, il est apparu un problème : lorsque l'agent est en mode plan (activé automatiquement par le système Cursor), le prompt système l'empêche de modifier les fichiers. Cela devient problématique car, selon la nouvelle logique simplifiée, l'agent doit supprimer la tâche de la roadmap lorsqu'il commence à travailler dessus (via `/agent`).

Le mode plan est un mécanisme de sécurité de Cursor qui empêche toute modification de fichiers avant confirmation de l'utilisateur. Cependant, dans notre workflow, l'agent sélectionne une tâche, charge son contexte, puis crée un plan d'implémentation. Pendant cette phase de planification, il ne peut pas supprimer la tâche de la roadmap car il est en mode "plan only".

## Objectif

Explorer et définir une solution pour permettre à l'agent de travailler correctement sur une tâche même en mode plan. La solution privilégiée est d'ajouter systématiquement dans le plan d'implémentation une instruction explicite de supprimer la tâche de la roadmap et son fichier de tâche, car créer un plan signifie qu'on travaille effectivement dessus.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Commande `/agent` qui définit comment sélectionner et traiter une tâche - actuellement supprime la tâche après chargement du contexte mais avant présentation
- `.cursor/rules/debug.mdc` : Règle qui explique le workflow en mode plan et les contraintes
- Documentation système de Cursor : Le prompt système qui définit les contraintes du mode plan

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/commands/agent.md` : Doit être modifié pour inclure l'instruction de suppression dans le plan plutôt qu'en temps réel
- `.cursor/rules/agent.mdc` : Règle de création de tâches qui pourrait nécessiter des ajustements
- Documentation système : Comprendre les limites du mode plan et comment y travailler

### Recherches à effectuer :
- Recherche sémantique : "Comment fonctionne le mode plan dans Cursor et quelles sont ses contraintes ?"
- Recherche sémantique : "Comment les autres commandes gèrent-elles le mode plan pour les opérations qui nécessitent des modifications de fichiers ?"
- Documentation : Lire le README pour comprendre le workflow actuel de `/agent`

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-remplacer-in-progress-par-suppression-tache-et-fichier.md` : Rapport sur la suppression des tâches
- `.cursor/agents/rapport-supprimer-mise-a-jour-statut-timestamps-roadmap.md` : Rapport sur la simplification de la roadmap

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ajouter-suppression-tache-dans-plan-mode-plan.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre comment fonctionne actuellement `/agent` et le mode plan dans Cursor
2. **COMPRENDS** le problème : l'agent en mode plan ne peut pas supprimer la tâche immédiatement, mais créer un plan signifie qu'il travaille dessus
3. **EFFECTUE les recherches sémantiques** mentionnées pour identifier les patterns et solutions existantes
4. **IDENTIFIE** comment adapter `/agent` pour inclure la suppression de la tâche dans le plan plutôt qu'en temps réel
5. **ATTEINS une compréhension approfondie** du workflow attendu : sélection → chargement contexte → création plan (incluant suppression) → présentation → discussion → implémentation
6. **DISCUTE avec l'utilisateur** pour clarifier :
   - La solution privilégiée est-elle bien d'ajouter la suppression dans le plan ?
   - Quelle est la séquence exacte attendue : quand créer le plan (avant ou après présentation) ?
   - Faut-il aussi supprimer le fichier de tâche dans le plan ou seulement retirer de la roadmap ?
7. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
8. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer toute modification de `/agent` ou des règles associées. L'exploration est OBLIGATOIRE, pas optionnelle.

