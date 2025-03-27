# In Progress

## 1. Développement des règles

## 2. Validation

## 3. Décomposition de la règle test
3.1. [ ] **Créer test-implementation.mdc** : Créer la nouvelle règle pour la création des tests
- Actions:
  * Créer le fichier test-implementation.mdc
  * Implémenter la structure standard (TLDR, Instructions, Précisions, Next Rules)
  * Ajouter la logique de création des tests unitaires
  * Ajouter une section Exemple
  * Configurer l'appel à test-execution comme seule règle suivante
- Fichiers: .cursor/rules/test-implementation.mdc
- Dépendances: Aucune
- Validation: La règle est créée et suit le format standard

3.2. [ ] **Créer test-execution.mdc** : Créer la nouvelle règle pour l'exécution des tests
- Actions:
  * Créer le fichier test-execution.mdc
  * Implémenter la structure standard (TLDR, Instructions, Précisions, Next Rules)
  * Ajouter la logique d'exécution et d'analyse des tests
  * Ajouter une section Exemple
  * Configurer l'appel à fix ou context-update selon les résultats
- Fichiers: .cursor/rules/test-execution.mdc
- Dépendances: 3.1
- Validation: La règle est créée et suit le format standard

3.3. [ ] **Modifier implementation.mdc** : Adapter la règle pour utiliser les nouvelles règles de test
- Actions:
  * Modifier la section Next Rules
  * Ajouter la logique de choix entre test-implementation et test-execution
  * Mettre à jour la section Exemple avec les nouveaux cas
- Fichiers: .cursor/rules/implementation.mdc
- Dépendances: 3.1, 3.2
- Validation: La règle est modifiée et utilise correctement les nouvelles règles

3.4. [ ] **Modifier workflow-perdu.mdc** : Mettre à jour les descriptions des règles
- Actions:
  * Ajouter les descriptions pour test-implementation et test-execution
  * Mettre à jour les descriptions existantes si nécessaire
- Fichiers: .cursor/rules/workflow-perdu.mdc
- Dépendances: 3.1, 3.2
- Validation: Les descriptions sont à jour et cohérentes

3.5. [ ] **Modifier system.mdc** : Ajouter l'appel à workflow-perdu
- Actions:
  * Ajouter la condition d'appel à workflow-perdu
  * Mettre à jour la section sur le workflow
- Fichiers: .cursor/rules/system.mdc
- Dépendances: 3.4
- Validation: L'appel à workflow-perdu est correctement configuré

## 4. Tests et validation
4.1. [ ] **Tester le nouveau workflow** : Vérifier que la décomposition fonctionne
- Actions:
  * Tester le passage de implementation à test-implementation
  * Tester le passage de implementation à test-execution
  * Tester le passage de test-implementation à test-execution
  * Tester le passage de test-execution à fix ou context-update
- Fichiers: Tous les fichiers .mdc modifiés
- Dépendances: Toutes les tâches de la section 3
- Validation: Le workflow fonctionne correctement avec les nouvelles règles

4.2. [ ] **Vérifier la cohérence** : S'assurer que toutes les règles sont cohérentes
- Actions:
  * Vérifier la cohérence des descriptions dans workflow-perdu
  * Vérifier la cohérence des sections Exemple
  * Vérifier la cohérence des Next Rules
  * Vérifier la cohérence des formats
- Fichiers: Tous les fichiers .mdc
- Dépendances: 4.1
- Validation: Toutes les règles sont cohérentes entre elles

# Done 