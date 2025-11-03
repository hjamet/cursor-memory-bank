# Rapport : Créer la commande /clean pour nettoyer les tâches in-progress

## Résumé

Cette tâche a été complétée avec succès. La commande `/clean` existait déjà dans `.cursor/commands/clean.md` avec la logique de base pour archiver les tâches terminées et remettre en todo les tâches non terminées. La tâche consistait à compléter cette commande en ajoutant la phase de nettoyage global des output_file, identique à la phase 4 de l'étape 2.0 de `/agent`, afin de garantir une cohérence totale entre les deux mécanismes de nettoyage.

## Modifications apportées

### Fichier modifié : `.cursor/commands/clean.md`

**Ajout de la phase de nettoyage global des output_file** :

1. **Collecte des output_file archivés** :
   - Ajout d'une liste `archived_output_files` pour collecter les `output_file` des tâches archivées pendant l'étape 2
   - Lors de l'archivage d'une tâche terminée, son `output_file` est maintenant ajouté à cette liste

2. **Nouvelle étape 2.5 : Nettoyage Global des Output Files** :
   - Pour chaque `output_file` dans `archived_output_files`, vérification de :
     - Si le fichier est référencé dans les `dependencies-results` d'autres tâches
     - Si le fichier existe physiquement
   - Logique de nettoyage identique à la phase 4 de l'étape 2.0 de `/agent` :
     - **Référencé ET existe** : conserver le fichier (fichier utilisé)
     - **Référencé MAIS n'existe pas** : retirer la référence de tous les `dependencies-results` concernés (nettoyer référence invalide) et sauvegarder `roadmap.yaml`
     - **Non référencé** : supprimer le fichier (fichier orphelin)

3. **Mise à jour de la documentation** :
   - Mise à jour de l'exemple de séquence complète pour inclure la phase de nettoyage
   - Mise à jour de la note "Logique identique" pour préciser que l'archivage ET le nettoyage suivent exactement la logique de l'étape 2.0 de `/agent`

## Décisions prises

- **Réutilisation de la logique existante** : La phase de nettoyage a été copiée exactement depuis l'étape 2.0 de `/agent` pour garantir une cohérence totale entre les deux mécanismes
- **Ordre d'exécution** : Le nettoyage global des output_file se fait après avoir archivé toutes les tâches, ce qui permet d'avoir une vue complète des dépendances avant de décider quels fichiers supprimer
- **Sauvegarde conditionnelle** : La sauvegarde de `roadmap.yaml` se fait seulement si des références invalides sont nettoyées, en plus des sauvegardes déjà effectuées lors de l'archivage

## Vérifications effectuées

- ✅ La commande `/clean` implémente maintenant exactement la même logique de nettoyage que l'étape 2.0 de `/agent` (phases 1-4)
- ✅ La phase de nettoyage global des output_file est fonctionnellement identique à la phase 4 de `/agent`
- ✅ La documentation a été mise à jour pour refléter le nouveau comportement
- ✅ Aucune erreur de linting détectée

## État final

La commande `/clean` est maintenant complète et alignée avec l'étape 2.0 de `/agent`. Les deux mécanismes utilisent exactement la même logique pour :
- Archiver les tâches terminées (retirer de la roadmap, mettre à jour les dépendances, supprimer les fichiers de tâches)
- Nettoyer les fichiers output_file orphelins ou avec références invalides

Cela garantit une cohérence totale dans le maintien de l'hygiène de la roadmap, que le nettoyage soit effectué via `/agent` ou `/clean`.

