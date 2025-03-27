# Fichier de tests

## Tests d'installation via curl
- ❌ **Test d'installation via curl** : L'installation échoue avec "Core rules not installed". Cela peut être dû à une modification dans la structure du projet ou au format de l'archive téléchargée. - Première exécution.
- ❌ **Test d'options d'installation curl** : L'erreur "Backup was created despite --no-backup option" indique que l'option --no-backup ne fonctionne pas correctement, ce qui n'est pas cohérent avec nos modifications. - Première exécution.
- ✅ **Test de gestion d'erreur curl** : Le test de gestion d'URL invalide a réussi, ce qui signifie que le script gère correctement les erreurs d'URL invalides. - Première exécution.

## Tests de téléchargement
- ❌ **Test de téléchargement de fichier** : L'erreur "download_file: command not found" suggère que la fonction n'est pas correctement définie ou accessible dans le contexte du test. - Première exécution.
- ✅ **Test d'URL invalide** : Le test de gestion d'URL invalide a réussi. - Première exécution.
- ❌ **Test de téléchargement d'archive** : L'erreur avec le code HTTP "00023" suggère un problème dans la gestion des codes de retour HTTP ou dans le téléchargement local de l'archive. - Première exécution.

## Tests d'installation via git
- ✅ **Test d'installation de base** : L'installation de base via git fonctionne correctement. - Première exécution.
- ✅ **Test de préservation des règles personnalisées** : Les règles personnalisées sont correctement préservées lors de l'installation. - Première exécution.
- ✅ **Test d'option --no-backup** : L'option --no-backup semble fonctionner correctement dans ce contexte, contrairement au test curl. - Première exécution.
- ✅ **Test d'option --force** : L'option --force fonctionne correctement, permettant l'installation même si le répertoire n'est pas vide. - Première exécution.
- ⚠️ **Test de répertoire invalide** : Pas de sortie visible pour ce test, ce qui suggère qu'il peut ne pas avoir été exécuté correctement ou que sa sortie n'a pas été capturée. - Première exécution. 