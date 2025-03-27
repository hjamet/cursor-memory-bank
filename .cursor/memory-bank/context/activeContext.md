# Contexte Actif

## Focus Actuel
Le focus actuel est sur la correction des tests qui échouent suite aux modifications récentes du script d'installation et à la correction des références de branche.

## Problèmes en Cours
- Tests échoués:
  - Core rules not installed: Le test vérifie l'existence d'un fichier qui n'est pas créé
  - Backup créé malgré l'option --no-backup: Le changement de logique de backup n'est pas compatible avec les tests existants
  - download_file: command not found: Fonction attendue par les tests mais non implémentée
  - Erreur HTTP "00023": Problème dans la gestion des codes HTTP pour les protocoles file://
  - Test de répertoire invalide sans sortie visible

## Décisions Récentes
- [2023-03-27] - Nécessité de contourner le bug d'édition des fichiers *.mdc: Renommer en .md, éditer, puis renommer en .mdc
- [2023-03-27] - Correction des références à la branche "main" vers "master"
- [2023-03-27] - Modification de la logique de backup: Désactivée par défaut avec nouvelle option --backup

## Prochaines Étapes
- Implémenter les corrections nécessaires pour faire passer les tests échoués
- Ajouter la fonction download_file manquante
- Améliorer la gestion des codes HTTP pour les protocoles file://

## Notes Importantes
Le bug avec Cursor qui empêche l'édition des fichiers *.mdc a été documenté dans les règles fix et user-preference-saving. 