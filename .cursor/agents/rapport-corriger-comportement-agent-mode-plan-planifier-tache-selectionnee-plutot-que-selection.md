# Rapport : Corriger le comportement de /agent en mode plan

## Résumé

Ce rapport consolide la résolution de **task-5** et **task-11**, deux tâches étroitement liées qui traitaient du comportement de la commande `/agent` en mode plan. Les modifications permettent maintenant à `/agent` de gérer correctement le mode plan de Cursor.

## Problèmes identifiés

### Task-5 : Comportement incorrect de /agent en mode plan

**Problème** : Lors de l'exécution de `/agent` en mode plan, l'agent planifiait la consultation et la sélection de la roadmap elle-même, plutôt que d'exécuter directement ces étapes puis de créer un plan uniquement pour l'implémentation de la tâche sélectionnée.

**Impact** : Le workflow `/agent` ne fonctionnait pas correctement en mode plan, empêchant la planification correcte des implémentations de tâches.

### Task-11 : Suppression de tâche impossible en mode plan

**Problème** : En mode plan, l'agent ne peut pas modifier les fichiers (mécanisme de sécurité de Cursor). L'étape 4 de `/agent` supprimait immédiatement la tâche de la roadmap et son fichier, ce qui était impossible en mode plan.

**Impact** : La commande `/agent` échouait en mode plan car l'agent essayait de supprimer des fichiers qu'il n'avait pas le droit de modifier.

## Solution implémentée

### Modifications apportées à `.cursor/commands/agent.md`

#### 1. Étape 4 modifiée : Gestion conditionnelle de la suppression

L'Étape 4 a été modifiée pour gérer le mode plan :
- **En mode plan** : L'étape 4 est sautée (suppression impossible)
- **Hors mode plan** : L'étape 4 s'exécute normalement

La suppression est reportée dans le plan d'implémentation créé à l'Étape 5.5.

#### 2. Nouvelle Étape 5.5 : Création du plan d'implémentation

Une nouvelle étape a été ajoutée pour créer un plan d'implémentation lorsque l'agent est en mode plan :
- Vérifie si le mode plan est actif
- Crée un plan avec `create_plan` incluant tout le contexte chargé
- **Premier todo OBLIGATOIRE** : Supprimer la tâche de la roadmap, nettoyer les dépendances, et supprimer le fichier de tâche
- Todos suivants : étapes d'implémentation de la tâche

#### 3. Directive ajoutée dans Notes Importantes

Une section "CRITIQUE - Gestion du mode plan" a été ajoutée expliquant :
- Les étapes 1-3 s'exécutent TOUJOURS directement, jamais planifiées
- L'étape 4 est sautée en mode plan et devient le premier todo du plan
- Le plan d'implémentation est créé après présentation de la tâche

#### 4. Exemple de séquence mis à jour

L'exemple de séquence complète montre maintenant deux variantes :
- **Séquence normale** : Exécution complète avec suppression immédiate
- **Séquence en mode plan** : Exécution directe des étapes 1-3, création du plan avec suppression comme premier todo

## Workflow final

### Séquence normale (hors mode plan)

1. Lecture roadmap.yaml
2. Sélection de la tâche la plus intéressante
3. Chargement du contexte complet
4. **Suppression immédiate** de la tâche et du fichier
5. Présentation à l'utilisateur
6. Discussion collaborative
7. Implémentation

### Séquence en mode plan

1. Lecture roadmap.yaml
2. Sélection de la tâche la plus intéressante
3. Chargement du contexte complet
4. **[Étape 4 Sautée - mode plan détecté]**
5. Présentation à l'utilisateur
6. **Création du plan d'implémentation** avec suppression comme premier todo
7. Discussion collaborative
8. Exécution du plan (suppression en premier, puis implémentation)

## Principes clés

### Exécution directe vs planification

**Critique** : Les étapes 1-3 (lecture, sélection, chargement contexte) sont des opérations de **lecture seule** et doivent être exécutées directement, jamais planifiées.

### Suppression comme premier todo

**Critique** : En mode plan, la suppression de la tâche est **toujours** le premier todo OBLIGATOIRE du plan d'implémentation. C'est la première action que l'agent effectuera lors de l'exécution du plan.

### Séparation des responsabilités

- **Avant présentation** : Exécution directe (étapes 1-3) et création du plan (étape 5.5)
- **Après présentation** : Discussion collaborative et implémentation

## Fichiers modifiés

- `.cursor/commands/agent.md` : Modifications des étapes 4, 5.5, Notes Importantes, et Exemple de Séquence
- `.cursor/agents/roadmap.yaml` : Suppression de task-5 et task-11
- Fichiers supprimés :
  - `.cursor/agents/corriger-comportement-agent-mode-plan-planifier-tache-selectionnee-plutot-que-selection.md`
  - `.cursor/agents/ajouter-suppression-tache-dans-plan-mode-plan.md`
  - `corriger-agent-mode-plan.plan.md` (plan de transition)

## Validation

✅ Les modifications assurent que `/agent` fonctionne correctement en mode plan  
✅ La suppression est toujours effectuée (immédiatement ou comme premier todo)  
✅ Les étapes de lecture ne sont jamais planifiées  
✅ Le workflow respecte les contraintes du mode plan de Cursor  
✅ La documentation est claire et complète

## Conclusion

La fusion des solutions de task-5 et task-11 résout complètement les problèmes de comportement de `/agent` en mode plan. Le workflow est maintenant robuste et fonctionne correctement dans les deux modes (normal et plan), avec une séparation claire entre exécution directe et planification.

