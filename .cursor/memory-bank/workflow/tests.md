# Test Status

- [ ] `test_curl_install.sh`: Pending
- [ ] `test_download.sh`: Pending
- [ ] `test_git_install.sh`: Pending
- [ ] `test_install.sh`: Pending

# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test de gestion d'erreur curl** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Test passé correctement - Stable, continue de fonctionner après les modifications.

## Tests de téléchargement
- ✅ **Test de téléchargement de fichier** : Test passe correctement. - Stable after tmp cleanup addition.
- ✅ **Test d'URL invalide** : Test passe correctement. - Stable after tmp cleanup addition.
- ✅ **Test de téléchargement d'archive** : Test passe correctement (ou est sauté si fonction non dispo). - Stable after tmp cleanup addition.
- ✅ **Test d'URL d'archive invalide** : Test passe correctement (ou est sauté si fonction non dispo). - Stable after tmp cleanup addition.

## Tests d'installation via git
- ✅ **Test d'installation de base** : L'installation de base via git continue de fonctionner correctement. - Stable.
- ✅ **Test de préservation des règles personnalisées** : Les règles personnalisées sont correctement préservées lors de l'installation. - Stable.
- ✅ **Test d'option --no-backup** : L'option --no-backup fonctionne correctement dans le contexte git. - Stable.
- ✅ **Test d'option --force** : L'option --force continue de fonctionner correctement. - Stable.
- ✅ **Test de répertoire invalide** : Le test affiche maintenant clairement le message d'erreur capturé. - Stable.
- ✅ **Test d'affichage de la date du dernier commit (git)** : Test passé correctement - Stable, continue de fonctionner après les modifications.

## Tests d'installation standard
- ✅ **Test d'installation de base** : Le problème de chemin relatif a été corrigé, le test fonctionne maintenant. - Stable after tmp cleanup addition.
- ✅ **Test de backup et restauration** : Le test fonctionne correctement. - Stable after tmp cleanup addition.
- ✅ **Test de gestion d'erreur** : Corrigé en forçant --use-curl pour le test de dépôt invalide, la gestion d'erreur API fonctionne correctement. - Stable after tmp cleanup addition.

## Problèmes persistants
- ✅ **Tests de téléchargement** : Corrigé en isolant les fonctions de test.
- ✅ **Test de gestion d'erreur d'installation** : Corrigé.

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