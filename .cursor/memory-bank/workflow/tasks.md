# In Progress

## 8. Corrections des tests curl
8.1. [x] **Corriger la création du répertoire de logs** : Résoudre le problème de création des logs dans les tests curl.
- Actions: 
  1. Modifier la fonction setup dans test_curl_install.sh pour créer correctement le répertoire des logs
  2. S'assurer que le répertoire parent TEST_DIR est créé avant de créer LOGS_DIR
  3. Ajouter une vérification de l'existence du répertoire avant d'écrire dans les fichiers de log
- Fichiers: tests/test_curl_install.sh
- Dépendances: Aucune
- Validation: Les tests ne génèrent plus d'erreurs liées aux logs

8.2. [x] **Corriger définitivement le problème de backup persistant** : Résoudre complètement le problème des backups créés malgré l'absence de l'option --backup.
- Actions:
  1. Analyser pourquoi les backups sont toujours créés malgré nos modifications
  2. Vérifier la fonction install_rules pour identifier où des backups pourraient être créés
  3. Trouver et corriger toutes les références à la création de backups dans install.sh
  4. S'assurer que la gestion des backups est cohérente dans toutes les parties du script
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Le test d'options d'installation curl ne trouve plus de backups

8.3. [x] **Corriger le test de gestion d'erreur curl** : Résoudre la régression dans le test de gestion d'erreur curl.
- Actions:
  1. Analyser pourquoi le test échoue maintenant alors qu'il fonctionnait avant
  2. Vérifier la commande curl et ses options dans le test
  3. Ajuster le test ou la vérification d'erreur pour que le test passe correctement
- Fichiers: tests/test_curl_install.sh
- Dépendances: Aucune
- Validation: Le test de gestion d'erreur curl passe correctement

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

## 4. Corrections des tests
4.1. [x] **Corriger le test d'installation via curl** : Résoudre l'erreur "Core rules not installed".
- Actions: 
  1. Vérifier si le fichier core.mdc est réellement créé lors de l'installation
  2. Modifier le test pour vérifier un autre fichier existant ou créer un core.mdc lors de l'installation
- Fichiers: tests/test_curl_install.sh, install.sh
- Dépendances: Aucune
- Validation: Le test d'installation via curl passe sans erreur

4.2. [x] **Corriger le test d'options d'installation curl** : Résoudre l'erreur "Backup was created despite --no-backup option".
- Actions: 
  1. Vérifier si la nouvelle logique de backup avec l'option --backup est prise en compte dans les tests
  2. Mettre à jour les tests pour utiliser la nouvelle option --backup au lieu de l'ancienne logique --no-backup
- Fichiers: tests/test_curl_install.sh, install.sh
- Dépendances: Aucune
- Validation: Le test d'options d'installation curl passe sans erreur

4.3. [x] **Implémenter la fonction download_file manquante** : Ajouter la fonction download_file qui est attendue dans les tests.
- Actions: 
  1. Créer une fonction download_file similaire à download_archive mais adaptée pour les fichiers individuels
  2. Implémenter la gestion des codes d'erreur HTTP
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: La fonction download_file peut être appelée dans les tests et télécharge correctement les fichiers

4.4. [x] **Corriger le test de téléchargement d'archive** : Résoudre l'erreur avec le code HTTP "00023".
- Actions: 
  1. Analyser comment le code HTTP est extrait dans la fonction download_archive
  2. Améliorer la gestion des protocoles file:// dans la fonction download_archive
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Le test de téléchargement d'archive passe sans erreur

4.5. [x] **Compléter le test de répertoire invalide** : Assurer que la sortie du test est correctement capturée.
- Actions: 
  1. Vérifier l'implémentation du test de répertoire invalide dans tests/test_git_install.sh
  2. S'assurer que les messages d'erreur ou de succès sont affichés correctement
- Fichiers: tests/test_git_install.sh
- Dépendances: Aucune
- Validation: Le test de répertoire invalide affiche clairement son résultat 

## 5. Corrections supplémentaires
5.1. [x] **Corriger l'installation des fichiers de règle avec curl** : S'assurer que system.mdc est correctement copié lors de l'installation via curl.
- Actions: 
  1. Vérifier la structure de l'archive téléchargée avec curl
  2. Déboguer le processus de copie des fichiers de règles pour s'assurer que system.mdc est inclus
  3. Ajouter une vérification explicite ou une copie de sauvegarde si le fichier n'existe pas
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Le test d'installation via curl passe sans erreur

5.2. [x] **Corriger la logique de backup dans tests/test_curl_install.sh** : Résoudre le problème de backup créé malgré l'absence de l'option --backup.
- Actions: 
  1. Analyser pourquoi un backup est créé malgré l'absence de l'option --backup
  2. Vérifier si la fonction backup_rules crée des backups en mode par défaut
  3. Corriger le test pour s'assurer qu'aucun backup n'est créé sans l'option --backup
- Fichiers: install.sh, tests/test_curl_install.sh
- Dépendances: Aucune
- Validation: Le test d'options d'installation curl passe sans erreur 

## 6. Corrections persistantes
6.1. [x] **Résoudre le problème de backup persistant dans l'installation curl** : Empêcher complètement la création de backups lorsque l'option --backup n'est pas utilisée.
- Actions: 
  1. Vérifier toutes les parties du code qui pourraient créer un backup
  2. S'assurer que la recherche de backups dans le test utilise le bon pattern
  3. Vérifier si d'autres fonctions créent des backups indépendamment de backup_rules
- Fichiers: install.sh, tests/test_curl_install.sh
- Dépendances: Aucune
- Validation: Le test d'options d'installation curl passe sans erreur

6.2. [x] **Corriger le problème de flux d'exécution des tests curl** : S'assurer que les tests s'exécutent correctement dans l'ordre prévu.
- Actions: 
  1. Vérifier si le premier test crée un backup qui affecte le deuxième test
  2. Examiner comment l'environnement de test est réinitialisé entre les tests
  3. Ajouter un mécanisme pour nettoyer les backups entre les tests si nécessaire
- Fichiers: tests/test_curl_install.sh
- Dépendances: 6.1
- Validation: Tous les tests d'installation via curl passent correctement 

## 7. Améliorations du workflow
7.1. [x] **Modifier la règle fix concernant la documentation des erreurs** : Clarifier que seules les erreurs récurrentes liées aux bibliothèques doivent être documentées.
- Actions: 
  1. Modifier les précisions dans fix.mdc pour mettre l'accent sur la documentation uniquement des erreurs liées aux mises à jour de bibliothèques
  2. Ajouter l'exemple spécifique mentionné (dash-mantine-components avec "weight" devenu "w")
  3. Clarifier qu'il ne faut pas documenter les erreurs d'inattention ou les erreurs occasionnelles
- Fichiers: .cursor/rules/fix.mdc
- Dépendances: Aucune
- Validation: La règle fix.mdc contient des directives claires sur quelles erreurs documenter

## 9. Amélioration du script d'installation - Master Branch
9.1. [x] **Récupération depuis la branche master et affichage de la date** : Modifier le script d'installation pour récupérer les règles directement depuis la branche master et afficher la date du dernier commit.
- Actions:
  1. Ajouter une fonction get_last_commit_date pour récupérer la date du dernier commit
  2. Implémenter différentes méthodes de récupération (Git et API GitHub)
  3. Afficher la date du dernier commit lors de l'installation et dans la commande --version
  4. Mettre à jour les tests pour vérifier l'affichage de la date de commit
- Fichiers: install.sh, tests/test_curl_install.sh, tests/test_git_install.sh
- Dépendances: Aucune
- Validation: Les tests vérifient que la date du dernier commit est affichée correctement 

## 10. Amélioration de la méthode d'installation
10.1. [x] **Bannir l'utilisation de l'ARCHIVE_URL** : Modifier le script d'installation pour ne plus utiliser l'archive mais se concentrer uniquement sur la branche master.
- Actions:
  1. Remplacer la constante ARCHIVE_URL par une URL pointant directement vers la branche master
  2. Modifier la fonction install_rules pour ne plus télécharger ni extraire d'archive
  3. Adapter la méthode d'installation curl pour cloner directement depuis la branche master ou utiliser l'API GitHub
  4. Mettre à jour les messages de log pour refléter cette nouvelle approche
- Fichiers: install.sh
- Dépendances: Aucune
- Validation: Les tests d'installation continuent de passer après la modification

10.2. [x] **Mettre à jour le README pour favoriser curl** : Modifier le README pour faire de curl la méthode d'installation par défaut.
- Actions:
  1. Inverser les sections Method 1 et Method 2 dans le README
  2. Mettre à jour les descriptions pour présenter curl comme la méthode recommandée
  3. Adapter les exemples et les explications en conséquence
  4. S'assurer que la documentation reste cohérente avec le fonctionnement du script
- Fichiers: README.md
- Dépendances: 10.1
- Validation: Le README présente clairement curl comme la méthode d'installation par défaut

10.3. [x] **Mettre à jour les tests pour les changements** : S'assurer que les tests fonctionnent correctement avec les nouvelles modifications.
- Actions:
  1. Vérifier que tous les tests existants sont compatibles avec les nouvelles modifications
  2. Adapter les tests si nécessaire pour qu'ils fonctionnent avec la nouvelle approche
  3. Ajouter des tests supplémentaires si besoin pour valider le nouveau comportement
  4. Exécuter l'ensemble des tests pour s'assurer qu'il n'y a pas de régression
- Fichiers: tests/test_git_install.sh, tests/test_curl_install.sh
- Dépendances: 10.1, 10.2
- Validation: Tous les tests passent après les modifications 

## 11. Corrections des tests après bannissement de l'ARCHIVE_URL
11.1. [x] **Corriger les tests de téléchargement d'archive** : Résoudre le problème d'interruption des tests dans test_download.sh.
- Actions:
  1. Adapter les tests utilisant la fonction download_archive pour qu'ils fonctionnent avec la version commentée
  2. Vérifier les variables d'environnement et les chemins utilisés dans le test
  3. S'assurer que le test se termine correctement en affichant le message de succès
  4. Ajouter des logs supplémentaires pour mieux diagnostiquer les problèmes
- Fichiers: tests/test_download.sh
- Dépendances: Aucune
- Validation: Le test test_download.sh s'exécute complètement et affiche "All tests passed!"

11.2. [x] **Corriger le test d'installation standard** : Résoudre le problème de chemin relatif dans test_install.sh.
- Actions:
  1. Modifier les références à "../install.sh" pour utiliser un chemin absolu ou correct
  2. Mettre à jour les tests qui font référence à l'archive pour utiliser la nouvelle méthode d'installation
  3. Adapter les vérifications post-installation aux changements effectués
- Fichiers: tests/test_install.sh
- Dépendances: Aucune
- Validation: Le test test_install.sh s'exécute sans erreur "No such file or directory" 