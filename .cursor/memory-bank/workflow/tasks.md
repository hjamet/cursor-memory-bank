# Tasks

## In Progress

## ToDo

## Done

### Corrections
- [x] **Correction des tests d'installation**
  - Actions:
    * Modifier la fonction setup() pour utiliser mktemp -d
    * Stocker le chemin du répertoire temporaire dans une variable
    * Ajouter un trap EXIT pour supprimer le répertoire temporaire
    * Utiliser le répertoire temporaire pour les tests
  - Files:
    * tests/test_git_install.sh
  - Dependencies: None
  - Validation:
    * Les tests d'installation passent
    * Aucun fichier temporaire n'est laissé après les tests
    * Les tests fonctionnent même en cas d'erreur

### 1. Suppression du script create-release.sh
- [x] Suppression du fichier scripts/create-release.sh
- [x] Mise à jour des fichiers de contexte
- [x] Commit des changements

### 3. Corrections
- [x] Correction des erreurs de syntaxe dans test_curl_install.sh
- [x] Correction de l'environnement de test
- [x] Correction de la structure des archives GitHub
- [x] Mise à jour des tests pour refléter les changements

## 3. Documentation
3.1. [ ] **Update Installation Documentation** : Document the new installation process
- Actions:
  * Update README.md with new installation URLs
  * Document the release process
  * Add section on creating new releases
  * Include error handling details
- Files:
  * README.md
- Dependencies: 2.1
- Validation:
  * Documentation is clear and complete
  * Installation instructions are accurate
  * Release process is well documented

3.2. [ ] **Create Comprehensive Documentation** : Complete project documentation
- Actions:
  * Document installation process
  * Document usage instructions
  * Document configuration options
  * Add troubleshooting section
  * Include development guidelines
- Files:
  * README.md
  * docs/* (if needed)
- Dependencies: 3.1
- Validation:
  * Documentation covers all aspects
  * Instructions are clear and tested
  * Examples are provided where needed

## 4. Corrections
4.1. [x] **Fix Syntax Error in test_curl_install.sh** : Corriger l'erreur de syntaxe dans le script de test
- Actions:
  * Supprimer l'accolade fermante après le if à la ligne 90 ✓
  * Vérifier la structure des autres blocs if ✓
  * Tester l'exécution du script ✓
- Files:
  * tests/test_curl_install.sh
- Dependencies: None
- Validation:
  * Le script s'exécute sans erreur de syntaxe ✓
  * Les tests d'installation via curl passent ✗ (Échec non lié à la syntaxe)

4.2. [x] **Fix Test Environment Setup** : Corriger la configuration de l'environnement de test pour les tests d'installation via curl
- Actions:
  * Modifier la fonction setup pour ne pas créer le répertoire des règles avant l'installation ✓
  * Déplacer la création du fichier de test après l'installation ✓
  * Ajouter l'option --force aux commandes d'installation ✓
- Files:
  * tests/test_curl_install.sh
- Dependencies: None
- Validation:
  * Les tests d'installation via curl passent ✓
  * Les tests d'installation avec options passent ✓
  * Le test de gestion des erreurs continue de passer ✓

4.3. [x] **Fix GitHub Archive Structure** : Corriger la structure de l'archive GitHub pour les tests d'installation via curl
- Actions:
  * Vérifier la structure de l'archive GitHub ✓
  * Créer le répertoire rules dans l'archive ✓
  * Déplacer les fichiers de règles dans le répertoire rules ✓
  * Mettre à jour les tests pour utiliser la nouvelle structure ✓
- Files:
  * install.sh
  * tests/test_curl_install.sh
- Dependencies: None
- Validation:
  * L'archive GitHub a la structure attendue ✓
  * Les tests d'installation via curl passent ✓
  * Les tests d'installation avec options passent ✓

4.4. [ ] **Fix Release Archive Structure** : Corriger la structure de l'archive de release pour les tests d'installation via curl
- Actions:
  * Modifier le script create-release.sh pour créer une archive avec la bonne structure
    - Créer un répertoire temporaire pour la release
    - Copier les fichiers nécessaires dans la bonne structure
    - Créer l'archive à partir du répertoire temporaire
  * Mettre à jour les tests pour utiliser la nouvelle structure
- Files:
  * scripts/create-release.sh
  * tests/test_curl_install.sh
- Dependencies: None
- Validation:
  * L'archive contient le répertoire rules à la racine
  * Les tests d'installation via curl passent
  * Les tests d'installation avec options passent

# Done

## 1. Préparation
1.1. [x] **Suppression du script create-release.sh** : Supprimer le script devenu obsolète
- Actions:
  * Supprimer le fichier scripts/create-release.sh ✓
  * Mettre à jour .gitignore si nécessaire ✓
- Files:
  * scripts/create-release.sh
  * .gitignore
- Dependencies: None
- Validation:
  * Le fichier est supprimé ✓
  * Aucune référence au script ne reste dans le projet ✓

## 3. GitHub Release Integration
3.1. [x] **Update Installation Script** : Modify install.sh to use GitHub release archives
- Actions:
  * Mettre à jour les variables pour utiliser les archives GitHub
    - Modifier ARCHIVE_NAME pour utiliser le format GitHub "v1.0.0.tar.gz"
    - Mettre à jour DOWNLOAD_URL pour utiliser l'URL GitHub "https://github.com/hjamet/cursor-memory-bank/archive/refs/tags/"
  * Supprimer la vérification du checksum
    - Supprimer la fonction verify_checksum
    - Modifier download_and_verify pour ne plus télécharger ni vérifier le checksum
  * Adapter l'extraction pour le nouveau format d'archive
    - Modifier install_rules pour gérer le répertoire racine cursor-memory-bank-1.0.0/
    - Mettre à jour les chemins d'extraction
  * Mettre à jour les tests
    - Adapter test_download.sh pour le nouveau format d'archive
    - Adapter test_install.sh pour le nouveau format d'archive
    - Supprimer les tests de vérification de checksum
- Files:
  * install.sh
  * tests/test_download.sh
  * tests/test_install.sh
- Dependencies: None
- Validation:
  * Installation réussie avec les archives GitHub
  * Tests passent avec le nouveau format
  * Pas de vérification de checksum

## 4. Corrections
4.1. [x] **Fix Rule Files** : Fix the rule files content and encoding
- Actions: Rewrite rule files with correct encoding and line endings
- Files: .cursor/rules/core.mdc, .cursor/rules/memory-bank.mdc
- Dependencies: None
- Validation: All repository structure tests pass

- [x] Fix backup path in install.sh
  - Problem: Double path inclusion with $target_dir/$RULES_DIR
  - Solution: Use relative path for RULES_DIR or handle absolute path correctly
  - Files: install.sh:backup_rules()

- [x] Fix custom rules restoration in install.sh
  - Problem: Backup directory pattern doesn't match created format
  - Solution: Update pattern to match "RULES_DIR.bak-YYYYMMDD-HHMMSS"
  - Files: install.sh:install_rules()

- [x] Fix path handling in create-release.sh
  - Problem: Script ignores environment variables for paths
  - Solution: Use environment variables with defaults
  - Files: scripts/create-release.sh

- [x] Fix backup creation in install.sh
  - Problem: Backup is not created in test mode
  - Solution: Remove test mode check for backup creation
  - Files: install.sh:backup_rules()

- [x] Fix error handling in create-release.sh
  - Problem: Script continues after directory check failure
  - Solution: Add error handling for non-writable dist directory
  - Files: scripts/create-release.sh

- [x] Fix backup path in test_install.sh
  - Problem: Test checks backup in wrong path
  - Solution: Update test to check backup in $target_dir/$RULES_DIR.bak-*
  - Files: tests/test_install.sh:test_backup_restore()

- [x] Fix error handling in create-release.sh
  - Problem: Script doesn't check permissions before operations
  - Solution: Add permission check before any file operation
  - Files: scripts/create-release.sh

- [x] Fix backup path in test_install.sh
  - Problem: Test uses absolute path in backup pattern
  - Solution: Use relative path for backup pattern
  - Files: tests/test_install.sh:test_backup_restore()

- [x] Fix error handling in test_create_release.sh
  - Problem: stderr redirection prevents error detection
  - Solution: Capture stderr and verify error messages
  - Files: tests/test_create_release.sh:test_error_handling()

- [x] Fix double path in backup_rules function
  - File: install.sh:backup_rules()
  - Problem: Double path inclusion when creating backup
  - Solution: Use relative path for backup directory
  - Changes:
    - Replace `$target_dir/$RULES_DIR` with `$target_dir/.cursor/rules`
    - Update backup_dir variable to use correct path

- [x] Fix error handling in create-release.sh
  - File: scripts/create-release.sh
  - Problem: stderr redirection prevents error messages from being seen
  - Solution: Remove stderr redirection and handle errors properly
  - Changes:
    - Remove `2>/dev/null` from commands
    - Add proper error handling for each command
    - Update error messages to be more descriptive

- [x] Fix error handling in create-release.sh and test
  - File: scripts/create-release.sh, tests/test_create_release.sh
  - Problem: Script uses set -e but test doesn't check return code
  - Solution: Update test to check return code and ensure script returns 1 on error
  - Changes:
    - Add return code check in test_error_handling
    - Ensure error function returns 1 in create-release.sh
    - Update test to verify both error message and return code

- [x] Fix error handling with set -e
  - File: scripts/create-release.sh
  - Problem: set -e doesn't work as expected with error function
  - Solution: Use exit 1 and disable set -e temporarily
  - Changes:
    - Replace `return 1` with `exit 1` in error function
    - Add `set +e` before error calls and `set -e` after
    - Update error function to handle set -e properly

- [x] Fix error handling with if blocks
  - File: scripts/create-release.sh
  - Problem: Error handling with if blocks captures errors and prevents set -e from working
  - Solution: Remove if blocks and let set -e handle errors directly
  - Changes:
    - Remove if blocks around directory checks
    - Let set -e handle command failures
    - Keep error function with exit 1 for explicit error messages

- [x] Fix error handling test
  - File: tests/test_create_release.sh
  - Problem: Test captures output with $() which may interfere with exit code propagation
  - Solution: Separate output capture and exit code check
  - Changes:
    - Run script directly and redirect output to a file
    - Check exit code immediately after script execution
    - Read output from file for message verification

4.2. [x] **Fix Test Environment Setup** : Corriger la configuration de l'environnement de test pour les tests d'installation via curl
- Actions:
  * Modifier la fonction setup pour ne pas créer le répertoire des règles avant l'installation ✓
  * Déplacer la création du fichier de test après l'installation ✓
  * Ajouter l'option --force aux commandes d'installation ✓
- Files:
  * tests/test_curl_install.sh
- Dependencies: None
- Validation:
  * Les tests d'installation via curl passent ✓
  * Les tests d'installation avec options passent ✓
  * Le test de gestion des erreurs continue de passer ✓

### 2. Installation via Git Clone
- [x] Amélioration de la gestion des erreurs
  - Actions:
    * Ajout de set -o pipefail ✓
    * Redirection des messages vers stderr ✓
    * Capture du code de sortie dans cleanup ✓
    * Messages d'erreur plus descriptifs ✓
    * Vérification des permissions ✓
    * Vérification de git ✓
    * Gestion des erreurs pour les fichiers ✓
    * Nettoyage des fichiers temporaires ✓
  - Files:
    * install.sh
  - Dependencies: None
  - Validation:
    * Les erreurs sont détectées et rapportées
    * Les messages d'erreur sont clairs
    * Les fichiers temporaires sont nettoyés

### 5. Simplification du script d'installation
5.1. [x] **Simplify Installation Script** : Simplifier le script d'installation pour préserver les fichiers existants
- Actions:
  * Modifier le script d'installation pour préserver les fichiers existants non liés aux règles ✓
  * Supprimer la vérification qui empêche l'installation si le répertoire des règles existe déjà ✓
  * Mettre à jour les tests pour refléter ce nouveau comportement ✓
  * Mettre à jour la documentation README.md ✓
- Files:
  * install.sh
  * tests/test_git_install.sh
  * README.md
- Dependencies: None
- Validation:
  * Les tests d'installation passent ✓
  * Les fichiers existants sont préservés lors de l'installation ✓
  * La documentation reflète ce nouveau comportement ✓