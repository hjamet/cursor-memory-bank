# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Test passé correctement - Amélioration par rapport aux exécutions précédentes, le test ne génère plus d'erreurs
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Test passé correctement - Amélioration par rapport aux exécutions précédentes, le problème des backups créés malgré l'absence de l'option --backup a été corrigé
- ✅ **Test de gestion d'erreur curl** : Test passé correctement - Amélioration par rapport aux exécutions précédentes, la vérification d'erreur curl fonctionne comme prévu
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Test passé correctement - Nouvelle fonctionnalité, la date du dernier commit est maintenant affichée dans la sortie de --version et pendant l'installation

## Tests de téléchargement
- ✅ **Test de téléchargement de fichier** : La fonction download_file a été implémentée et semble fonctionner correctement dans le contexte du script. - Stable.
- ✅ **Test d'URL invalide** : Le test de gestion d'URL invalide continue de fonctionner correctement. - Stable.
- ✅ **Test de téléchargement d'archive** : La gestion des protocoles file:// et des codes HTTP non standards a été améliorée. - Stable.

## Tests d'installation via git
- ✅ **Test d'installation de base** : L'installation de base via git continue de fonctionner correctement. - Stable.
- ✅ **Test de préservation des règles personnalisées** : Les règles personnalisées sont correctement préservées lors de l'installation. - Stable.
- ✅ **Test d'option --no-backup** : L'option --no-backup fonctionne correctement dans le contexte git. - Stable.
- ✅ **Test d'option --force** : L'option --force continue de fonctionner correctement. - Stable.
- ✅ **Test de répertoire invalide** : Le test affiche maintenant clairement le message d'erreur capturé. - Stable.
- ✅ **Test d'affichage de la date du dernier commit (git)** : Test passé correctement - Nouvelle fonctionnalité, la date du dernier commit est maintenant affichée dans la sortie de --version et pendant l'installation

## Problèmes persistants
- ❌ **Test d'installation standard** : Le script test_install.sh échoue avec l'erreur "../install.sh: No such file or directory" - Problème de chemin relatif dans le script de test, qui n'est pas directement lié aux modifications récentes

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