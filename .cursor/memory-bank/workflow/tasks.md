# In Progress

## 4. Corrections des tests
4.1. [ ] **Corriger le test d'installation via curl** : Résoudre l'erreur "Core rules not installed".
- Actions: 
  1. Vérifier si le fichier core.mdc est réellement créé lors de l'installation
  2. Modifier le test pour vérifier un autre fichier existant ou créer un core.mdc lors de l'installation
- Fichiers: tests/test_curl_install.sh, install.sh
- Dépendances: Aucune
- Validation: Le test d'installation via curl passe sans erreur

4.2. [ ] **Corriger le test d'options d'installation curl** : Résoudre l'erreur "Backup was created despite --no-backup option".
- Actions: 
  1. Vérifier si la nouvelle logique de backup avec l'option --backup est prise en compte dans les tests
  2. Mettre à jour les tests pour utiliser la nouvelle option --backup au lieu de l'ancienne logique --no-backup
- Fichiers: tests/test_curl_install.sh, install.sh
- Dépendances: Aucune
- Validation: Le test d'options d'installation curl passe sans erreur

4.3. [ ] **Implémenter la fonction download_file manquante** : Ajouter la fonction download_file qui est attendue dans les tests.
- Actions: 
  1. Créer une fonction download_file similaire à download_archive mais adaptée pour les fichiers individuels
  2. Implémenter la gestion des codes d'erreur HTTP
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: La fonction download_file peut être appelée dans les tests et télécharge correctement les fichiers

4.4. [ ] **Corriger le test de téléchargement d'archive** : Résoudre l'erreur avec le code HTTP "00023".
- Actions: 
  1. Analyser comment le code HTTP est extrait dans la fonction download_archive
  2. Améliorer la gestion des protocoles file:// dans la fonction download_archive
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Le test de téléchargement d'archive passe sans erreur

4.5. [ ] **Compléter le test de répertoire invalide** : Assurer que la sortie du test est correctement capturée.
- Actions: 
  1. Vérifier l'implémentation du test de répertoire invalide dans tests/test_git_install.sh
  2. S'assurer que les messages d'erreur ou de succès sont affichés correctement
- Fichiers: tests/test_git_install.sh
- Dépendances: Aucune
- Validation: Le test de répertoire invalide affiche clairement son résultat

# ToDo

# Done

## 1. Correction des références à la branche
1.1. [x] **Corriger les références à "main" dans le README** : Remplacer toutes les occurrences de la branche "main" par "master" dans le README.
- Actions: Identifier et remplacer les références à la branche "main" par "master" dans le README.md (lignes 51 et 57)
- Fichiers: README.md
- Dépendances: Aucune
- Validation: Toutes les URL pointent vers la branche "master" au lieu de "main"

1.2. [x] **Corriger les références à "main" dans les tests** : Remplacer toutes les occurrences de la branche "main" par "master" dans les fichiers de test.
- Actions: Identifier et remplacer les références à la branche "main" par "master" dans tests/test_curl_install.sh (lignes 86 et 133)
- Fichiers: tests/test_curl_install.sh
- Dépendances: Aucune
- Validation: Toutes les URL pointent vers la branche "master" au lieu de "main"

## 2. Amélioration du script d'installation
2.1. [x] **Désactiver le backup par défaut** : Modifier le script d'installation pour que l'option de backup soit désactivée par défaut.
- Actions: Inverser la logique de l'option --no-backup dans install.sh pour que le backup soit désactivé par défaut
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Le script ne crée pas de backup par défaut, sauf si une nouvelle option (--backup) est spécifiée

2.2. [x] **Ajouter l'affichage de la date de version** : Modifier la fonction show_version pour inclure la date de la version des règles installées.
- Actions: Modifier la fonction show_version dans install.sh pour afficher la date au format YYYY-MM-DD en plus du numéro de version
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: La commande install.sh --version affiche la date en plus du numéro de version

## 3. Documentation des bugs et limitations
3.1. [x] **Documenter le bug d'édition des fichiers .mdc** : Ajouter une documentation sur le bug qui empêche l'édition directe des fichiers .mdc avec Cursor.
- Actions: 
  1. Renommer les fichiers fix.mdc et user-preference-saving.mdc en .md
  2. Ajouter une section sur le bug et la solution de contournement
  3. Renommer les fichiers en .mdc
- Fichiers: .cursor/rules/fix.mdc, .cursor/rules/user-preference-saving.mdc
- Dépendances: Aucune
- Validation: Les fichiers contiennent une documentation claire sur le bug et la méthode de contournement

- [x] **Analyse et compréhension des besoins** : Analyse des problèmes identifiés et des améliorations nécessaires. 