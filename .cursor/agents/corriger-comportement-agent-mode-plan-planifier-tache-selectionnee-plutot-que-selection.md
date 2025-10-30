## Contexte

Travail actuel sur la simplification du format de nommage des fichiers de tâches (task-2) → lors de l'exécution de la commande `/agent` en mode plan, découverte d'un problème de comportement : l'agent a planifié sa consultation de la roadmap (sélection de la tâche) plutôt que de charger directement la tâche sélectionnée et planifier ensuite son implémentation.

Le mode plan de Cursor devrait être utilisé pour planifier l'implémentation de la tâche sélectionnée, pas pour planifier la sélection de la tâche elle-même. La commande `/agent` devrait être exécutée directement (charger la roadmap, sélectionner la tâche, charger le contexte) sans créer de plan pour cette sélection, puis ensuite créer un plan pour l'implémentation de la tâche sélectionnée.

Cette correction est importante pour que le workflow `/agent` fonctionne correctement en mode plan et que l'utilisateur puisse planifier l'implémentation des tâches plutôt que leur sélection.

## Objectif

Corriger le comportement de la commande `/agent` pour qu'en mode plan, elle exécute directement la sélection et le chargement de la tâche (sans créer de plan pour cette étape), puis crée un plan pour l'implémentation de la tâche sélectionnée plutôt que pour sa sélection.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Commande `/agent` qui contient les instructions de sélection et traitement de tâche - comportement actuel à corriger
- `.cursor/agents/simplifier-nommage-taches.md` : Tâche en cours lors de la découverte du problème

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/commands/prompt.md` : Commande `/prompt` qui utilise aussi le mode plan - peut servir de référence pour comprendre comment gérer le mode plan
- `.cursor/rules/debug.mdc` : Règle qui explique le workflow en mode plan - peut donner des indications sur comment différencier les phases
- Documentation système sur le mode plan : Comment fonctionne le mode plan dans Cursor et quand il est activé

### Recherches à effectuer :
- Recherche sémantique : "Comment gérer le mode plan dans les commandes Cursor pour différencier exécution directe et planification ?"
- Recherche sémantique : "Quels autres fichiers utilisent le mode plan et comment l'utilisent-ils ?"
- Documentation : Lire `README.md` pour comprendre le contexte du système de roadmap

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun pour le moment

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-corriger-comportement-agent-mode-plan-planifier-tache-selectionnee-plutot-que-selection_30-10-2025.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre le comportement actuel de `/agent` et comment le mode plan fonctionne
2. **EFFECTUE les recherches sémantiques** mentionnées pour identifier comment gérer correctement le mode plan dans les commandes
3. **COMPRENDS** la différence entre exécuter directement la sélection de tâche et planifier son implémentation
4. **IDENTIFIE** les modifications nécessaires dans `.cursor/commands/agent.md` pour corriger le comportement
5. **ATTEINS une compréhension approfondie** de comment le mode plan devrait être utilisé dans ce contexte
6. **DISCUTE avec l'utilisateur** pour clarifier :
   - Comment différencier si on est en mode plan ou pas ?
   - Faut-il modifier la commande `/agent` pour détecter le mode plan et adapter son comportement ?
   - Quelle est la séquence exacte attendue : exécution directe de la sélection puis planification de l'implémentation ?
7. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
8. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer tout travail de modification. L'exploration est OBLIGATOIRE, pas optionnelle.

