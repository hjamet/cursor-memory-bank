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

1. **Vérifier les dépendances** :
   - Pour chaque tâche, vérifier que toutes ses dépendances (task IDs dans `dependencies`) existent dans la roadmap
   - Une dépendance est considérée comme "résolue" si le task ID existe dans la roadmap (c'est-à-dire que la tâche dépendante n'a pas encore été traitée)
   - Exclure les tâches avec dépendances non résolues (si un task ID dans `dependencies` n'existe pas dans la roadmap)

2. **Trier les tâches disponibles** :
   - Par priorité décroissante (5 = plus haute priorité)
   - En cas d'égalité, prendre la première tâche rencontrée

3. **Sélectionner** :
   - La première tâche de la liste triée

Si aucune tâche n'est disponible → **INFORMER L'UTILISATEUR** que toutes les tâches sont soit bloquées par des dépendances non résolues, soit la roadmap est vide.

### Étape 3 : Charger le Contexte de la Tâche

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
   - Utiliser des lectures en parallèle pour gagner du temps et inclure tous les fichiers mentionnés
   - Lire exhaustivement chaque fichier disponible
   - Si un fichier est introuvable, invalide ou inaccessible → **NE PAS interrompre**; consigner l'élément exact dans la liste "Fichiers introuvables" avec la raison (ex: `absent`, `lecture refusée`, `parse YAML`)
   - Lire aussi les fichiers de résultats d'autres agents mentionnés (s'ils existent dans `.cursor/agents/`)

### Étape 3.5 : Consolider les éléments introuvables

1. **Maintenir une liste dédiée** :
   - Chaque entrée décrit le type d'élément (`fichier`, `rapport`, `recherche`) et le chemin ou la requête concernée
   - Ajouter un court message explicatif (ex: "fichier supprimé", "rapport jamais généré")
2. **Aucun masquage** :
   - Ces informations doivent être restituées telles quelles à l'utilisateur lors de la présentation finale
   - Ne jamais ignorer ou reformuler vaguement un manque : la traçabilité est obligatoire

4. **Effectuer les recherches mentionnées** :
   - Recherches sémantiques dans le codebase si mentionnées
   - Recherches web si mentionnées dans "Fichiers Concernés"
   - Lire le README et la documentation pertinente

### Étape 4 : Supprimer la Tâche de la Roadmap et Nettoyer les Dépendances

1. **Supprimer la tâche sélectionnée** :
   - Retirer la tâche sélectionnée de la liste `tasks` dans `roadmap.yaml`
   - Sauvegarder le fichier `roadmap.yaml`

2. **Nettoyer les dépendances** :
   - Parcourir toutes les tâches restantes dans la roadmap
   - Pour chaque tâche, retirer l'ID de la tâche supprimée de sa liste `dependencies` (si présent)
   - Sauvegarder le fichier `roadmap.yaml`

3. **Supprimer le fichier de tâche** :
   - Supprimer le fichier `.cursor/agents/{task_file}` (où `task_file` est défini dans la tâche sélectionnée)
   - Si le fichier n'existe pas → **ÉCHOUER EXPLICITEMENT** avec un message clair

4. **Calculer les compteurs de priorités restants** :
   - À partir des `tasks` RESTANTES dans `roadmap.yaml` (après suppression), calculer le nombre de tâches par priorité
   - Mappage emojis: 5=🔴, 4=🟠, 3=🔵, 2–1=🟢
   - Toujours afficher les quatre compteurs, même si 0

### Étape 5 : Présenter la Tâche à l'Utilisateur (Résumé)

Cette étape **EST le résumé** de la tâche sélectionnée. Elle se fait après la suppression (étape 4) et le chargement du contexte (étape 3).

**CRITIQUE** : Tout doit être écrit **EN FRANÇAIS** avec des emojis appropriés.

Présenter dans cet ordre normalisé (sections fixes) :

1. 🎯 **Tâche sélectionnée** — titre de la tâche, suffixé par les compteurs `(🔴X, 🟠Y, 🔵Z, 🟢W)` calculés sur TOUTES les tâches restantes
2. 📋 **Contexte** — pourquoi la tâche existe, découvertes, problèmes
3. 🎯 **Objectif** — ce qui doit être accompli (ton exploratoire)
4. 🧠 **Idées** — premières pistes/approches envisagées

## Format de Présentation Requis

🚫 **Interdiction absolue** d'utiliser des blocs de code ou des backticks : la sortie doit être en texte brut, sans encadrement par `\`` ou `\`\`\``.

Reproduire exactement les lignes suivantes (en texte brut, avec des lignes vides comme indiqué) :

🎯 **Tâche sélectionnée :** [Titre] (🔴X, 🟠Y, 🔵Z, 🟢W)

📋 **Contexte :**
[Pourquoi cette tâche existe, découvertes, problèmes]

🎯 **Objectif :**
[But à atteindre, ton exploratoire]

🧠 **Idées :**
- [Piste 1]
- [Piste 2]

⚠️ **Fichiers introuvables :**
- [Chemin ou recherche] — [Raison]

❓ **Questions :** *(optionnel — chaque question numérotée avec des options a/b/c pour permettre des réponses compactes comme 1A)*
1. [Question 1] ?
   - a) [Proposition A]
   - b) [Proposition B]
   - c) [Proposition C]
2. [Question 2] ?
   - a) [Proposition A]
   - b) [Proposition B]
   - c) [Proposition C]

Si aucun élément n'est manquant, afficher la phrase « ⚠️ **Fichiers introuvables :** Aucun ».

## Gestion des Erreurs (Fail-Fast)

Si une étape échoue, tu **DOIS** :
- Arrêter immédiatement
- Informer l'utilisateur de l'erreur avec un message clair
- Expliquer ce qui a échoué et pourquoi
- Ne pas continuer avec des données partielles ou invalides

⚠️ **Exception** : la liste "Fichiers introuvables" n'est pas considérée comme une erreur bloquante tant que la roadmap et le fichier de tâche ont été chargés correctement.

## Notes Importantes

- **Tout en français** : Tous les messages à l'utilisateur doivent être en français
- **Emojis** : Utiliser des emojis appropriés pour rendre la présentation claire et engageante
- **Exploration exhaustive** : Ne présenter la tâche qu'après avoir lu TOUS les fichiers et fait TOUTES les recherches
- **Pas d'implémentation immédiate** : L'objectif est la discussion et la planification collaborative
- **Important** : Ne jamais créer de plan pour la sélection/consultation de la roadmap. Le plan ne concerne que l'implémentation de la tâche sélectionnée.
- **Validation stricte** : Échouer explicitement si quelque chose est invalide ou manquant
 - **Suppression irréversible** : La suppression de la tâche et de son fichier lors des étapes 4–5–6 est immédiate et irréversible par design. Aucune journalisation additionnelle n'est requise.
 - **Signalement obligatoire** : Toute donnée manquante doit apparaître telle quelle dans la section `⚠️ Fichiers introuvables`, même si la liste est vide (utiliser "Aucun").

## Exemple de Séquence Complète

```
1. Lecture roadmap.yaml ✓
2. Sélection de la tâche la plus prioritaire ✓
3. Chargement du fichier de tâche et du contexte ✓
4. Suppression immédiate de la tâche de la roadmap + nettoyage des dépendances + suppression du fichier de tâche ✓
5. Présentation à l'utilisateur (résumé avec émojis) ✓
6. Discussion collaborative → éventuel passage en mode plan pour créer le plan d'implémentation ✓
7. Implémentation après validation du plan ✓
```

