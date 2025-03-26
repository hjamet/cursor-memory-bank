# In Progress

## 1. Amélioration de la structure des règles
1.1. [x] **Standardiser la structure des règles** : Modification de toutes les règles pour suivre exactement la même structure claire : 1. TLDR, 2. Instructions, 3. Précisions, 4. Next Rules. Cette structure est maintenant respectée de façon uniforme dans chaque fichier de règle.
1.2. [x] **Ajouter une phrase de résumé après invocation** : Intégration à chaque règle d'une phrase standardisée que l'agent doit réciter après avoir invoqué la règle, résumant ce qu'il va faire, ne pas faire, et les prochaines règles possibles.

## 2. Correction de la syntaxe d'invocation des règles
2.1. [ ] **Modifier la syntaxe d'invocation** : Changer dans tous les fichiers de règle la syntaxe d'appel `@cursor-rules fetch [nom-de-la-règle]` par `fetch_rules ["nom-de-la-règle"]` pour correspondre à l'API réelle de Cursor.
2.2. [x] **Mettre à jour les exemples et instructions** : Remplacer tous les exemples et instructions qui utilisent l'ancienne syntaxe, y compris dans les fichiers de contexte.

## 3. Amélioration de la gestion des tâches
3.1. [ ] **Rendre la suppression des tâches terminées plus agressive** : Modifier task-decomposition.mdc pour renforcer la suppression des tâches terminées, en conservant uniquement celles qui sont strictement liées aux tâches en cours.
3.2. [ ] **Ajouter des règles claires pour le nettoyage** : Définir des critères précis pour déterminer quand une tâche terminée doit être supprimée (par exemple, après X jours ou lorsqu'une section entière est terminée).

## 4. Renforcement de l'adhérence au workflow
4.1. [ ] **Ajouter des vérifications du respect du workflow** : Implémenter des mécanismes de vérification plus stricts pour s'assurer que l'agent ne dévie jamais du workflow défini.
4.2. [ ] **Améliorer les instructions de suivi du workflow** : Renforcer les avertissements dans chaque règle pour empêcher l'agent de sortir du workflow et de sauter des étapes.

# ToDo

## 5. Simplification des règles
5.1. [ ] **Simplifier le langage des règles** : Revoir toutes les règles pour utiliser un langage plus simple et direct, en évitant les formulations complexes ou ambiguës.
5.2. [ ] **Réduire la longueur des instructions** : Condenser les instructions tout en conservant leur clarté, pour faciliter leur suivi par l'agent.

## 6. Tests et validation
6.1. [ ] **Créer des scénarios de test** : Développer des scénarios spécifiques pour tester le respect du workflow dans différentes situations.
6.2. [ ] **Valider les améliorations** : Tester les modifications apportées pour confirmer qu'elles résolvent efficacement les problèmes identifiés.

# Done

## Améliorations récentes
- [x] **Modifier system.mdc pour renforcer l'indication de l'étape** : Ajout d'une instruction explicite que l'agent doit afficher le titre de l'étape (dans le format requis) AVANT de consulter tout fichier.
- [x] **Clarifier les restrictions de lecture de fichiers** : Ajout d'un avertissement plus visible dans system.mdc indiquant que l'agent ne doit consulter que les fichiers spécifiquement autorisés par l'étape en cours.
- [x] **Limiter la lecture des fichiers dans context-loading** : Modification de la règle context-loading.mdc pour limiter explicitement la lecture aux trois fichiers spécifiés.
- [x] **Renforcer context-loading.mdc** : Ajout d'avertissements supplémentaires pour insister sur l'obligation d'afficher l'étape actuelle avant toute lecture de fichier.
- [x] **Ajouter un mécanisme de vérification du respect du workflow** : Implémentation d'un moyen de vérifier que l'agent suit correctement le workflow et affiche correctement l'étape actuelle.
- [x] **Mettre à jour les fichiers de contexte avec la nouvelle syntaxe** : Mise à jour de techContext.md pour refléter la syntaxe correcte d'invocation des règles (fetch_rules ["nom-de-la-règle"]) et l'ajout de la phrase de résumé comme nouvelle convention.