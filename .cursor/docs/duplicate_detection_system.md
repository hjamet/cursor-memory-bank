# Système de Détection de Doublons de Tâches

## Vue d'ensemble

Le système de détection de doublons a été implémenté pour résoudre le problème critique identifié lors de l'audit adversarial où des tâches avec des titres identiques pouvaient être créées sans validation.

## Architecture

### Composants principaux

1. **Algorithme de similarité** : Utilise la distance de Levenshtein pour calculer la similarité entre les chaînes de caractères
2. **Validation multi-niveaux** : Vérifie à la fois les titres et les descriptions
3. **Système de seuils configurables** : Permet d'ajuster la sensibilité de la détection
4. **Logging détaillé** : Trace toutes les tentatives de duplication

### Fichiers modifiés

- `.cursor/mcp/memory-bank-mcp/mcp_tools/create_task.js` : Implémentation principale
- `.cursor/mcp/memory-bank-mcp/test_duplicate_detection.js` : Tests de validation

## Fonctionnement

### Algorithme de détection

```javascript
function checkForDuplicates(tasks, newTitle, newDescription, titleThreshold = 0.85, descriptionThreshold = 0.7)
```

#### Niveaux de détection

1. **Critique (BLOCKED)** : Titre identique (similarité = 1.0)
2. **Avertissement (ALLOWED avec log)** : 
   - Similarité titre + description élevée (≥ 0.85 + ≥ 0.7)
   - Similarité titre très élevée seule (≥ 0.9)

#### Exclusions

- Les tâches avec statut `DONE` ou `APPROVED` sont ignorées dans la détection
- Seules les tâches actives sont considérées pour éviter les faux positifs

### Calcul de similarité

Utilise la distance de Levenshtein normalisée :

```
similarité = (longueur_max - distance_edit) / longueur_max
```

- **1.0** : Chaînes identiques
- **0.0** : Chaînes complètement différentes
- **0.85+** : Très similaires (seuil d'avertissement)

## Exemples d'utilisation

### Cas bloqués (Critique)

```javascript
// Tâche existante
{
  title: "Test adversarial de duplication de tâches",
  short_description: "Premier test"
}

// Tentative de création (BLOQUÉE)
{
  title: "Test adversarial de duplication de tâches", // Identique
  short_description: "Deuxième test"
}
```

**Résultat** : Erreur avec détails de la tâche existante

### Cas d'avertissement (Autorisé avec log)

```javascript
// Tâche existante
{
  title: "Corriger le bug de validation",
  short_description: "Correction du système"
}

// Tentative de création (AUTORISÉE avec warning)
{
  title: "Corriger le bug de validations", // Très similaire
  short_description: "Correction du système"
}
```

**Résultat** : Création autorisée + log d'avertissement

## Configuration

### Seuils par défaut

- **Titre critique** : 1.0 (identique)
- **Titre avertissement** : 0.85
- **Description avertissement** : 0.7
- **Titre seul avertissement** : 0.9

### Personnalisation

Les seuils peuvent être ajustés dans la fonction `checkForDuplicates()` pour adapter la sensibilité selon les besoins.

## Tests

### Script de test

```bash
node .cursor/mcp/memory-bank-mcp/test_duplicate_detection.js
```

### Cas de test couverts

1. **Titres identiques** : Doit être bloqué
2. **Titres très similaires** : Doit être autorisé avec avertissement
3. **Tâches complètement différentes** : Doit être autorisé sans avertissement

## Monitoring et logs

### Logs d'avertissement

```javascript
console.warn(`[CreateTask] Potential duplicate detected for task "${params.title}":`, 
    duplicateCheck.warningDuplicates.map(d => ({
        existing_id: d.task.id,
        existing_title: d.task.title,
        title_similarity: d.titleSimilarity,
        description_similarity: d.descriptionSimilarity,
        reason: d.reason
    }))
);
```

### Réponse d'erreur (critique)

```json
{
  "status": "error",
  "message": "Task creation blocked: A task with identical title already exists",
  "duplicate_detection": {
    "reason": "identical_title",
    "existing_task": {
      "id": 252,
      "title": "Test adversarial de duplication de tâches",
      "status": "APPROVED",
      "created_date": "2025-06-30T16:57:59.817Z"
    },
    "similarity_scores": {
      "title": 1.0,
      "description": 0.65
    }
  }
}
```

## Impact sur les performances

### Complexité algorithmique

- **Distance de Levenshtein** : O(n×m) où n et m sont les longueurs des chaînes
- **Validation complète** : O(k×n×m) où k est le nombre de tâches existantes

### Optimisations implémentées

1. **Exclusion des tâches archivées** : Réduit le nombre de comparaisons
2. **Arrêt précoce** : Stoppe dès qu'un doublon critique est trouvé
3. **Calcul lazy** : Ne calcule la similarité description que si nécessaire

### Recommandations

- Pour de gros volumes (>1000 tâches actives), considérer un index de recherche
- Monitoring des temps de réponse pour détecter les dégradations
- Possibilité d'ajuster les seuils si trop de faux positifs

## Maintenance

### Points de vigilance

1. **Ajustement des seuils** : Surveiller les faux positifs/négatifs
2. **Performance** : Monitorer les temps de réponse
3. **Logs** : Analyser les patterns de duplication pour améliorer l'algorithme

### Évolutions possibles

1. **Détection sémantique** : Utiliser NLP pour détecter les doublons conceptuels
2. **Index de recherche** : Implémentation d'un index pour de meilleures performances
3. **Interface utilisateur** : Suggestions de tâches similaires lors de la création
4. **Machine learning** : Apprentissage des patterns de duplication spécifiques au projet

## Résolution des problèmes

### Problèmes courants

1. **Faux positifs** : Réduire les seuils de similarité
2. **Faux négatifs** : Augmenter les seuils ou améliorer l'algorithme
3. **Performance lente** : Optimiser l'algorithme ou ajouter un cache

### Debugging

1. Vérifier les logs d'avertissement pour comprendre les détections
2. Utiliser le script de test pour valider les modifications
3. Analyser les métriques de similarité dans les réponses d'erreur 