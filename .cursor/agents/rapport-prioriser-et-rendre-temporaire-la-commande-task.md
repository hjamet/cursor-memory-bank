# Rapport : Prioriser et rendre temporaire la commande /task

## Résumé

Formalisation du comportement de la commande `/task` comme interruption obligatoire et immédiate, avec confirmation minimale et traitement séquentiel des multiples invocations. Les règles de priorité et de temporalité ont été clarifiées dans toute la documentation.

## Problèmes identifiés

### Absence de formalisation de la priorité et de la temporalité

**Problème** : La documentation existante indiquait que `/task` était "non-bloquante" sans préciser son comportement de priorité. L'agent pouvait interpréter cela comme signifiant qu'il pouvait reporter le traitement de `/task`, ce qui est incorrect.

**Impact** : Incertitude sur la façon dont `/task` devait interrompre le travail en cours. La documentation laissait place à des interprétations divergentes.

### Confirmation verbose non standardisée

**Problème** : La documentation proposait plusieurs formats de confirmation :
- "✅ Tâche "{titre}" ajoutée à la roadmap avec succès ! 📋 ID: task-{id} 📁 Fichier: {nom-fichier}.md"
- "✅ Tâche "{titre}" ajoutée à la roadmap (ID: task-{id})"

**Impact** : Messages longs ralentissant la reprise du travail. Aucun format minimal standardisé.

### Cas d'enchaînement non documentés

**Problème** : Aucune documentation sur le comportement face à des invocations multiples ou pendant une autre commande :
- `/task A /task B` : comment traiter plusieurs `/task` ?
- `/agent /task ...` : comment suspendre et reprendre ?

**Impact** : Comportement imprévisible dans ces cas, potentiels bugs ou perte de contexte.

### Distinction création autonome vs `/task` peu claire

**Problème** : Dans `.cursor/rules/agent.mdc`, la section "Différence avec `/task`" mentionnait seulement que la création autonome était "silencieuse" et "non-bloquante", sans distinguer suffisamment le comportement de `/task`.

**Impact** : Risque de confusion entre création autonome (silencieuse) et `/task` (interruption avec confirmation).

## Solutions implémentées

### 1. Ajout de la section "Priorité et Temporalité" dans `.cursor/commands/task.md`

**Changement** : Nouvelle section explicite décrivant que `/task` est une interruption obligatoire et immédiate.

**Contenu** :
- Priorité absolue : suspend TOUT travail en cours
- Traitement strictement séquentiel : multiples `/task` traitées l'une après l'autre
- Réponse minimale : confirmation la plus courte possible

### 2. Standardisation de la confirmation minimale

**Changement** : Format unique standardisé : `✅ Tâche ajoutée (task-{id})`

**Fichiers modifiés** :
- `.cursor/commands/task.md` : "Étape 5 : Confirmation et Reprise"
- `.cursor/commands/task.md` : "Format de Réponse Minimal"
- `.cursor/commands/task.md` : "Exemple Complet"

### 3. Documentation des cas d'enchaînement

**Changement** : Nouvelle section "Cas d'Usage et Enchaînements" documentant :
- `/task` seul : création immédiate, confirmation minimale, reprise
- Multiples `/task` : traitement séquentiel avec confirmation pour chaque
- Pendant une autre commande : suspension, création, confirmation, reprise

### 4. Mise à jour de `README.md`

**Changement** : Nouvelle section "Comportement" dans la description de `/task` ajoutant :
- Interruption obligatoire et immédiate
- Traitement strictement séquentiel
- Confirmation minimale standardisée

**Exemple mis à jour** : Confirmation `✅ Tâche ajoutée (task-1)` au lieu de format verbeux.

### 5. Clarification de la distinction dans `.cursor/rules/agent.mdc`

**Changement** : Section "Différence avec `/task`" réécrite avec tableaux comparatifs clairs :

**Création autonome (agent.mdc)** :
- Déclenché automatiquement
- Silencieux
- Non-bloquant

**Commande `/task`** :
- Interruption obligatoire et immédiate
- Avec confirmation
- Reprise immédiate

## Fichiers modifiés

1. **`.cursor/commands/task.md`**
   - Ajout section "Priorité et Temporalité"
   - Modification "Étape 5 : Confirmation et Reprise" (confirmation minimale)
   - Modification "Format de Réponse Minimal" (confirmation minimale)
   - Modification "Exemple Complet" (confirmation minimale)
   - Ajout section "Cas d'Usage et Enchaînements"

2. **`README.md`**
   - Ajout section "Comportement" dans description `/task`
   - Mise à jour "Workflow" avec confirmation minimale
   - Mise à jour "Exemple" avec confirmation minimale

3. **`.cursor/rules/agent.mdc`**
   - Réécriture section "Différence avec `/task`" avec distinctions claires

## Exemples de cas d'usage

### Exemple 1 : `/task` seul

**Input** : `/task il faudrait optimiser les performances`

**Comportement** :
1. Suspension immédiate du travail en cours
2. Création de task-12
3. Confirmation : `✅ Tâche ajoutée (task-12)`
4. Reprise du travail précédent

### Exemple 2 : Multiples `/task`

**Input** : `/task optimiser les performances /task améliorer le cache`

**Comportement** :
1. Suspension du travail en cours
2. Création de task-12 (optimiser les performances)
3. Confirmation : `✅ Tâche ajoutée (task-12)`
4. Création de task-13 (améliorer le cache)
5. Confirmation : `✅ Tâche ajoutée (task-13)`
6. Reprise du travail précédent

### Exemple 3 : Pendant une autre commande

**Input** : `/agent /task optimiser les performances`

**Comportement** :
1. `/agent` commence à s'exécuter
2. Détection de `/task`, suspension de `/agent`
3. Création de task-12
4. Confirmation : `✅ Tâche ajoutée (task-12)`
5. Reprise de `/agent` où l'agent s'était arrêté

## Validation

✅ Comportement `/task` formel : interruption obligatoire et immédiate  
✅ Confirmation standardisée : `✅ Tâche ajoutée (task-{id})`  
✅ Cas d'enchaînement documentés et pris en charge  
✅ Distinction claire : création autonome vs `/task`  
✅ Documentation alignée entre `.cursor/commands/task.md`, `README.md` et `.cursor/rules/agent.mdc`

## Conclusion

Les règles de `/task` sont désormais explicites. L'agent sait qu'il doit traiter `/task` immédiatement, confirmer de façon minimale, puis reprendre. La distinction avec la création autonome de tâches est claire, et les cas d'enchaînement sont couverts.

