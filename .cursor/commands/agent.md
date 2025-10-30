# Commande Agent — Sélection et Traitement de Tâche 🚀

## Objectif

Quand l'utilisateur tape `/agent`, tu dois consulter la roadmap centralisée, sélectionner la tâche la plus intéressante disponible, charger tout son contexte, puis présenter la tâche à l'utilisateur pour discussion collaborative avant implémentation.

## Comportement Requis

Lorsque l'utilisateur tape `/agent` (avec ou sans instructions supplémentaires), tu dois suivre cette séquence exacte :

### Étape 1 : Charger et Valider la Roadmap

1. **Lire le fichier `.cursor/agents/roadmap.yaml`**
   - Si le fichier n'existe pas → **ÉCHOUER EXPLICITEMENT** avec un message clair indiquant que la roadmap n'existe pas encore
   - Si le fichier est invalide (YAML mal formé) → **ÉCHOUER EXPLICITEMENT** avec les détails de l'erreur

2. **Valider la structure de la roadmap**
   - Vérifier que `version` existe
   - Vérifier que `tasks` est un tableau
   - Si validation échoue → **ÉCHOUER EXPLICITEMENT**

### Étape 2 : Sélectionner la Tâche la Plus Intéressante

Appliquer cette logique de sélection dans l'ordre :

1. **Filtrer les tâches disponibles** :
   - Statut = `TODO` OU
   - Statut = `IN_PROGRESS` ET (`started_at` est `null` OU plus de 24h écoulées depuis `started_at`)

2. **Vérifier les dépendances** :
   - Pour chaque tâche, vérifier que toutes ses dépendances (task IDs dans `dependencies`) ont le statut `DONE`
   - Exclure les tâches avec dépendances non résolues

3. **Vérifier le timeout** :
   - Si une tâche est `IN_PROGRESS` avec `started_at`, vérifier si plus de 24h se sont écoulées
   - Si timeout dépassé ET toutes les autres tâches sont `DONE`, alors la tâche peut être reprise

4. **Trier les tâches disponibles** :
   - Par priorité décroissante (5 = plus haute priorité)
   - En cas d'égalité, par ancienneté croissante (`created_at` le plus ancien en premier)

5. **Sélectionner** :
   - La première tâche de la liste triée

Si aucune tâche n'est disponible → **INFORMER L'UTILISATEUR** que toutes les tâches sont soit terminées, soit en cours, soit bloquées par des dépendances.

### Étape 3 : Marquer la Tâche comme IN_PROGRESS

1. **Mettre à jour la roadmap** :
   - Changer le `status` de la tâche sélectionnée à `IN_PROGRESS`
   - Définir `started_at` à l'heure actuelle (format ISO 8601 : `YYYY-MM-DDTHH:mm:ssZ`)
   - Sauvegarder le fichier `roadmap.yaml`

### Étape 4 : Charger le Contexte de la Tâche

1. **Lire le fichier de tâche** :
   - Chemin : `.cursor/agents/{task_file}` (où `task_file` est défini dans la roadmap)
   - Si le fichier n'existe pas → **ÉCHOUER EXPLICITEMENT** avec un message clair

2. **Parser le fichier de tâche** :
   - Le fichier doit contenir les 4 sections obligatoires :
     - **Contexte**
     - **Objectif**
     - **Fichiers Concernés**
     - **Instructions de Collaboration**

3. **Lire tous les fichiers mentionnés dans "Fichiers Concernés"** :
   - Lire exhaustivement chaque fichier listé
   - Si un fichier n'existe pas → **ÉCHOUER EXPLICITEMENT** avec le chemin du fichier manquant
   - Lire aussi les fichiers de résultats d'autres agents mentionnés (s'ils existent dans `.cursor/agents/`)

4. **Effectuer les recherches mentionnées** :
   - Recherches sémantiques dans le codebase si mentionnées
   - Recherches web si mentionnées dans "Fichiers Concernés"
   - Lire le README et la documentation pertinente

### Étape 5 : Présenter la Tâche à l'Utilisateur

**CRITIQUE** : Tout doit être écrit **EN FRANÇAIS** avec des emojis appropriés.

Présenter dans cet ordre :

1. **Titre de la tâche** avec emoji 🎯
   ```
   🎯 Tâche sélectionnée : [Titre de la tâche]
   ```

2. **Résumé du contexte** :
   - Expliquer brièvement pourquoi cette tâche existe (section Contexte)
   - Mentionner les découvertes ou problèmes qui ont mené à cette tâche

3. **Objectif** :
   - Reprendre l'objectif de la tâche en expliquant clairement ce qui doit être accompli
   - Garder un ton exploratoire, pas trop précis (la précision viendra avec la discussion)

4. **Ce que je compte faire** :
   - Expliquer ta compréhension initiale de ce qui doit être fait
   - Mentionner les fichiers que tu as lus et ce que tu as compris
   - Expliquer pourquoi cette approche semble logique

5. **Questions de clarification** (si nécessaire) :
   - Poser des questions sur les contraintes techniques
   - Clarifier les ambiguïtés identifiées
   - Demander confirmation sur l'approche prévue

6. **Appel à la discussion** :
   - Inviter l'utilisateur à discuter et planifier ensemble avant toute implémentation
   - Rappeler que l'exploration est terminée, maintenant on planifie

### Étape 6 : Attendre la Discussion Collaborative

**INTERDIT** de commencer l'implémentation avant d'avoir :
- Discuté avec l'utilisateur
- Clarifié les attentes précises
- Établi un plan d'action détaillé ensemble
- Obtenu la validation de l'utilisateur

L'objectif est une **planification collaborative** avant l'implémentation.

## Format de Présentation Requis

Utiliser ce format exact pour la présentation :

```
🎯 **Tâche Sélectionnée :** [Titre]

📋 **Contexte :**
[Expliquer pourquoi cette tâche existe, ce qui a été découvert, etc.]

🎯 **Objectif :**
[Reprendre l'objectif de manière claire mais exploratoire]

💡 **Ce que je compte faire :**
[Expliquer ta compréhension et ton approche prévue]

❓ **Questions de clarification :**
[Si nécessaire, poser des questions]

🤝 **Discussion :**
Discutons ensemble pour préciser l'approche et établir un plan détaillé avant de commencer l'implémentation.
```

## Gestion des Erreurs (Fail-Fast)

Si une étape échoue, tu **DOIS** :
- Arrêter immédiatement
- Informer l'utilisateur de l'erreur avec un message clair
- Expliquer ce qui a échoué et pourquoi
- Ne pas continuer avec des données partielles ou invalides

## Notes Importantes

- **Tout en français** : Tous les messages à l'utilisateur doivent être en français
- **Emojis** : Utiliser des emojis appropriés pour rendre la présentation claire et engageante
- **Exploration exhaustive** : Ne présenter la tâche qu'après avoir lu TOUS les fichiers et fait TOUTES les recherches
- **Pas d'implémentation immédiate** : L'objectif est la discussion et la planification collaborative
- **Validation stricte** : Échouer explicitement si quelque chose est invalide ou manquant

## Exemple de Séquence Complète

```
1. Lecture roadmap.yaml ✓
2. Sélection tâche "Optimiser authentification" (priorité 4, dépendances résolues) ✓
3. Marquage IN_PROGRESS avec started_at ✓
4. Lecture fichier tâche ✓
5. Lecture de 8 fichiers mentionnés ✓
6. Recherches sémantiques effectuées ✓
7. Présentation à l'utilisateur avec contexte complet ✓
8. Attente discussion collaborative...
```

