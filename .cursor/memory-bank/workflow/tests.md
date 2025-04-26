# Test Status

- [✅] User curl test (MINGW64, no jq): Passed (Latest Run: 2025-04-26 - Required `tr -d '\r'` before `bash` to fix CRLF issue causing `: command not found`)
- [✅] `test_curl_install.sh`: Passed (Latest Run: 2025-04-26)
- [✅] `test_download.sh`: Passed (Latest Run: 2025-04-26)
- [✅] `test_git_install.sh`: Passed (Latest Run: 2025-04-26)
- [✅] `test_install.sh`: Passed (Latest Run: 2025-04-26)
- [✅] `test_mcp_json_absolute_path_no_jq`: Passed (Latest Run: 2025-04-26 - Verified relative path and warning when jq missing)

# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test de gestion d'erreur curl** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test chemin absolu MCP sans jq** : Passed (Latest Run: 2025-04-26)

## Tests de téléchargement
- ✅ **Test de téléchargement de fichier** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'URL invalide** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test de téléchargement d'archive** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'URL d'archive invalide** : Passed - Stable (Latest Run: 2025-04-26)

## Tests d'installation via git
- ✅ **Test d'installation de base** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test de préservation des règles personnalisées** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'option --no-backup** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'option --force** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test de répertoire invalide** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test d'affichage de la date du dernier commit (git)** : Passed - Stable (Latest Run: 2025-04-26)

## Tests d'installation standard
- ✅ **Test d'installation de base**: Passed (Latest Run: 2025-04-26)
- ✅ **Test de backup et restauration** : Passed - Stable (Latest Run: 2025-04-26)
- ✅ **Test de gestion d'erreur** : Passed - Stable (Latest Run: 2025-04-26)

## Problèmes persistants
- ✅ **Install script permissions (MINGW64/curl)**: Fixed (Latest Run: 2025-04-26) - Root cause identified as CRLF line endings (`\r`) causing parsing errors in piped MINGW64 bash. Resolved by modifying the *execution command* to `curl ... | tr -d '\r' | bash`.

## Historique des problèmes

### 26/03/2024 - Problèmes initiaux
- ❌ **Test d'installation via curl** : Échec avec "Core rules not installed" - Problème avec les règles principales manquantes
- ❌ **Test d'installation curl avec options par défaut** : Échec avec "Backup was created despite default no-backup behavior" - Des backups étaient créés malgré l'absence de l'option --backup
- ❌ **Test de gestion d'erreur curl** : Régression dans la vérification des erreurs - Le test échouait car la gestion des erreurs ne fonctionnait pas correctement

### 28/03/2024 - Corrections
- ✅ **Test d'installation via curl** : Résolu en s'assurant que system.mdc est correctement créé
- ✅ **Test d'installation curl avec options** : Résolu en modifiant la logique de préservation des règles personnalisées pour éviter la création de backups non désirés
- ✅ **Test de gestion d'erreur curl** : Résolu en ajustant le test pour capturer correctement le code d'erreur curl

### 28/03/2024 - Amélioration récupération depuis la branche master
- ✅ **Affichage date du dernier commit** : Ajout de l'affichage de la date du dernier commit pour indiquer la fraîcheur des règles
- ✅ **Récupération depuis master** : Amélioration du script pour toujours récupérer les dernières règles depuis la branche master
- ✅ **Tests d'affichage de date** : Ajout de tests pour vérifier l'affichage de la date du dernier commit

### 28/03/2024 - Bannissement de l'ARCHIVE_URL
- ✅ **Modification du mécanisme de téléchargement** : Remplacé l'utilisation de l'archive par l'utilisation directe de l'API GitHub pour télécharger les fichiers individuellement
- ✅ **Mise à jour du README** : curl est maintenant présenté comme la méthode d'installation par défaut
- ✅ **Tests de téléchargement** : Corrigé en isolant les fonctions de test dans le script de test dédié. 