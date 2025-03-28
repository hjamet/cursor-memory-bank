# Fichier de tests

## Tests d'installation via curl
- ✅ **Test d'installation via curl** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test d'installation curl avec options par défaut (pas de backup)** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test de gestion d'erreur curl** : Test passé correctement - Stable, continue de fonctionner après les modifications.
- ✅ **Test d'affichage de la date du dernier commit (curl)** : Test passé correctement - Stable, continue de fonctionner après les modifications.

## Tests de téléchargement
- ⚠️ **Test de téléchargement de fichier** : Test partiellement réussi, mais s'interrompt encore avant la fin. - Amélioration, des logs supplémentaires ont été ajoutés, mais le problème d'interruption persiste.
- ❓ **Test d'URL invalide** : Impossible de déterminer si ce test passe correctement car le test précédent s'interrompt. - Inconnu.
- ❓ **Test de téléchargement d'archive** : Les tests liés à l'archive ont été modifiés pour éviter des échecs si la fonction download_archive n'est pas disponible. - Amélioration, mais l'effet exact est incertain en raison de l'interruption des tests.

## Tests d'installation via git
- ✅ **Test d'installation de base** : L'installation de base via git continue de fonctionner correctement. - Stable.
- ✅ **Test de préservation des règles personnalisées** : Les règles personnalisées sont correctement préservées lors de l'installation. - Stable.
- ✅ **Test d'option --no-backup** : L'option --no-backup fonctionne correctement dans le contexte git. - Stable.
- ✅ **Test d'option --force** : L'option --force continue de fonctionner correctement. - Stable.
- ✅ **Test de répertoire invalide** : Le test affiche maintenant clairement le message d'erreur capturé. - Stable.
- ✅ **Test d'affichage de la date du dernier commit (git)** : Test passé correctement - Stable, continue de fonctionner après les modifications.

## Tests d'installation standard
- ✅ **Test d'installation de base** : Le problème de chemin relatif a été corrigé, le test fonctionne maintenant. - Amélioration significative, le test qui échouait auparavant fonctionne maintenant.
- ✅ **Test de backup et restauration** : Le test fonctionne correctement. - Amélioration, le test a été mis à jour pour utiliser le chemin absolu.
- ❌ **Test de gestion d'erreur** : Échoue avec "Installation should fail with invalid repository" - Problème avec le test d'erreur pour les dépôts invalides, nécessite une correction supplémentaire.

## Problèmes persistants
- ⚠️ **Tests de téléchargement** : Les tests de téléchargement semblent toujours s'interrompre pendant l'exécution - Les améliorations apportées n'ont pas complètement résolu le problème.
- ❌ **Test de gestion d'erreur d'installation** : Le test échoue à cause d'un problème avec le test d'erreur pour les dépôts invalides - Nécessite une correction supplémentaire.

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
- ⚠️ **Tests de téléchargement** : Les tests de téléchargement semblent s'interrompre pendant l'exécution - Potentiellement lié aux modifications de la fonction de téléchargement

### 28/03/2024 - Corrections des tests
- ✅ **Correction des tests avec download_archive** : Amélioration des tests pour éviter les échecs si la fonction n'est pas disponible
- ✅ **Correction du test d'installation standard** : Résolution du problème de chemin relatif dans test_install.sh
- ❌ **Test de gestion d'erreur d'installation** : Nouveau problème identifié avec le test d'erreur pour les dépôts invalides 