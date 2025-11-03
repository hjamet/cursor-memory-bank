# Commande Clean — Nettoyage des Tâches in-progress 🧹

## Objectif

Quand l'utilisateur tape `/clean`, tu dois nettoyer automatiquement les tâches marquées comme `in-progress` dans la roadmap centralisée. Pour chaque tâche `in-progress`, vérifier si son fichier résultat existe : si oui, archiver la tâche (comme l'étape 2.0 de `/agent`), sinon remettre la tâche en `todo` pour qu'elle puisse être reprise plus tard.

Cette commande permet de maintenir l'hygiène de la roadmap sans avoir à invoquer `/agent`, et permet de récupérer des tâches qui ont été marquées `in-progress` mais jamais terminées.

## Comportement Requis

Lorsque l'utilisateur tape `/clean` (avec ou sans instructions supplémentaires), tu dois suivre cette séquence exacte :

### Étape 1 : Charger ou Créer la Roadmap

1. **Lire le fichier `.cursor/agents/roadmap.yaml`**
   - Si le fichier n'existe pas → Créer une roadmap vide avec la structure suivante :
     ```yaml
     version: "1.0"
     tasks: []
     ```
     Puis terminer immédiatement avec la sortie : "Aucune roadmap trouvée, roadmap vide créée"
   - Si le fichier existe mais est invalide (YAML mal formé) → **ÉCHOUER EXPLICITEMENT** avec les détails de l'erreur

2. **Valider la structure de la roadmap**
   - Vérifier que `version` existe
   - Vérifier que `tasks` est un tableau
   - Pour chaque tâche, vérifier ou initialiser le champ `state` (doit être `"todo"` ou `"in-progress"`)
   - Si validation échoue → **ÉCHOUER EXPLICITEMENT**

### Étape 2 : Nettoyer les Tâches in-progress

Initialiser deux compteurs :
- `archived_count` = 0 (tâches archivées)
- `reset_count` = 0 (tâches remises en todo)

**Pour chaque tâche avec `state: "in-progress"`** :

1. **Vérifier si le fichier `.cursor/agents/{output_file}` existe** (où `output_file` est défini dans la tâche)

2. **Si le fichier existe** (tâche terminée) :
   - La tâche est terminée → archiver la tâche (logique identique à l'étape 2.0 de `/agent`) :
     - Retirer la tâche de `tasks` (supprimer complètement l'entrée)
     - Parcourir toutes les tâches restantes dans `tasks` :
       - Retirer l'ID de cette tâche de leurs `dependencies` (si présent)
       - Pour chaque tâche qui avait cette dépendance, ajouter `{output_file}` (nom de fichier seul, ex: `"rapport-tache-1.md"`) dans leur liste `dependencies-results` (initialiser à liste vide si le champ n'existe pas). Le format de `dependencies-results` est une liste de strings contenant uniquement les noms de fichiers (sans chemin, ex: `["rapport-tache-1.md", "rapport-tache-2.md"]`)
     - Supprimer le fichier de tâche `.cursor/agents/{task_file}` s'il existe encore
   - Incrémenter `archived_count`
   - Sauvegarder `roadmap.yaml` immédiatement après l'archivage

3. **Si le fichier n'existe pas** (tâche non terminée ou abandonnée) :
   - Modifier `state: "in-progress"` → `state: "todo"`
   - Incrémenter `reset_count`
   - Sauvegarder `roadmap.yaml` immédiatement après le changement

### Étape 3 : Afficher la Sortie

Afficher la sortie minimale selon les résultats :

- Si `archived_count` > 0 ou `reset_count` > 0 :
  ```
  Nettoyage terminé : X tâches archivées, Y tâches remises en todo
  ```
  (Remplacer X par `archived_count` et Y par `reset_count`)

- Si `archived_count` = 0 et `reset_count` = 0 :
  ```
  Aucune tâche in-progress à nettoyer
  ```

## Format de Sortie

La sortie doit être minimale et en français :

**Exemples de sortie :**
- "Nettoyage terminé : 2 tâches archivées, 1 tâche remise en todo"
- "Nettoyage terminé : 3 tâches archivées, 0 tâche remise en todo"
- "Nettoyage terminé : 0 tâche archivée, 2 tâches remises en todo"
- "Aucune tâche in-progress à nettoyer"
- "Aucune roadmap trouvée, roadmap vide créée"

## Gestion des Erreurs (Fail-Fast)

Si une étape échoue :
- Arrêter immédiatement
- Informer l'utilisateur de l'erreur avec un message clair
- Expliquer ce qui a échoué et pourquoi
- Ne pas continuer avec des données partielles ou invalides

⚠️ **Exception** : Si la roadmap n'existe pas, créer une roadmap vide n'est pas considéré comme une erreur — c'est un comportement normal.

## Notes Importantes

- **Tout en français** : Tous les messages à l'utilisateur doivent être en français
- **Comportement autonome** : La commande peut être exécutée indépendamment de `/agent`
- **Logique identique** : L'archivage suit exactement la même logique que l'étape 2.0 de `/agent`
- **Sauvegarde immédiate** : Sauvegarder `roadmap.yaml` après chaque modification (archivage ou remise en todo)
- **Validation stricte** : Échouer explicitement si quelque chose est invalide ou manquant
- **Fail-Fast** : Si roadmap.yaml existe mais est invalide → échouer explicitement avec détails

## Exemple de Séquence Complète

```
1. Lecture ou création de roadmap.yaml ✓
2. Validation de la structure ✓
3. Parcours des tâches in-progress ✓
   - Pour chaque tâche in-progress :
     - Si output_file existe → Archivage (retirer de tasks, mettre à jour dependencies et dependencies-results, supprimer task_file) ✓
     - Si output_file n'existe pas → Remettre en todo ✓
   - Sauvegarder roadmap.yaml après chaque modification ✓
4. Affichage de la sortie minimale avec compteurs ✓
```

