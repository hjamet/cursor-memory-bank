# Test Status

- [✅] `test_curl_install.sh`: Passed (Latest Run: YYYY-MM-DD - jq warning expected)
- [✅] `test_download.sh`: Passed (Latest Run: YYYY-MM-DD)
- [✅] `test_git_install.sh`: Passed (Latest Run: YYYY-MM-DD)
- [✅] `test_install.sh`: Passed (Latest Run: YYYY-MM-DD - jq warning expected, permission setting errors noted but non-blocking)

# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test de gestion d'erreur curl** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Passed - Stable (Latest Run: YYYY-MM-DD)

## Tests de téléchargement
- ✅ **Test de téléchargement de fichier** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'URL invalide** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test de téléchargement d'archive** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'URL d'archive invalide** : Passed - Stable (Latest Run: YYYY-MM-DD)

## Tests d'installation via git
- ✅ **Test d'installation de base** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test de préservation des règles personnalisées** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'option --no-backup** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'option --force** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test de répertoire invalide** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test d'affichage de la date du dernier commit (git)** : Passed - Stable (Latest Run: YYYY-MM-DD)

## Tests d'installation standard
- ✅ **Test d'installation de base**: Passed (Latest Run: YYYY-MM-DD - jq warning & perm errors noted)
- ✅ **Test de backup et restauration** : Passed - Stable (Latest Run: YYYY-MM-DD)
- ✅ **Test de gestion d'erreur** : Passed - Stable (Latest Run: YYYY-MM-DD)

## Problèmes persistants
- 🟡 **Install script permissions**: Lines 454/455 show `command not found` during permission setting (see `test_install.sh` logs), but tests pass. Needs investigation.

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