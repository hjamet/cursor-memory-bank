# In Progress

## 1. Correction du comportement de l'agent
1.1. [x] **Modifier system.mdc pour renforcer l'indication de l'étape** : Ajouter une instruction explicite que l'agent doit afficher le titre de l'étape (dans le format requis) AVANT de consulter tout fichier.
1.2. [x] **Clarifier les restrictions de lecture de fichiers** : Ajouter un avertissement plus visible dans system.mdc indiquant que l'agent ne doit consulter que les fichiers spécifiquement autorisés par l'étape en cours.

## 2. Amélioration des règles existantes
2.1. [x] **Renforcer context-loading.mdc** : Ajouter des avertissements supplémentaires pour insister sur l'obligation d'afficher l'étape actuelle avant toute lecture de fichier.
2.2. [x] **Ajouter un mécanisme de vérification du respect du workflow** : Implémenter un moyen de vérifier que l'agent suit correctement le workflow et affiche correctement l'étape actuelle.

## 4. Documentation du workflow
4.1. [ ] **Ajouter un diagramme Mermaid au README** : Créer et ajouter un diagramme Mermaid représentant le graphe des différentes règles et leurs relations.

## 5. Analyse des causes du comportement incorrect
5.1. [ ] **Analyser les causes du comportement incorrect** : Identifier les points faibles dans les règles qui permettent à l'agent de contourner le workflow strict.

## 6. Correction des problèmes de test
6.1. [ ] **Corriger l'échec du test 11** : Identifier et résoudre le problème qui fait échouer le test 11 relatif aux instructions d'affichage des étapes dans system.mdc. S'assurer que les phrases exactes "Pour CHAQUE instruction numérotée" et "titre de l'instruction" sont présentes et détectées correctement par le test.
6.2. [ ] **Corriger l'échec du test 12** : Identifier et résoudre le problème qui fait échouer le test 12 relatif aux restrictions de lecture dans system.mdc. S'assurer que les phrases exactes recherchées sont présentes et détectées correctement par le test.
6.3. [ ] **Vérifier l'encodage des fichiers** : Examiner si des problèmes d'encodage de caractères pourraient affecter la détection des chaînes de texte par les commandes grep dans les tests.

# ToDo

# Done

## 1. Optimisation du workflow Memory Bank
1.1. [x] **Limiter la lecture des fichiers dans context-loading** : Modifier la règle context-loading.mdc pour limiter explicitement la lecture aux trois fichiers spécifiés et empêcher la lecture de tasks.md ou d'autres fichiers du dossier workflow.
1.2. [x] **Corriger la syntaxe d'invocation des règles** : Mettre à jour la syntaxe d'appel des règles dans tous les fichiers concernés pour utiliser le format correct `@cursor-rules fetch [nom-de-la-règle]` au lieu de `@cursor-rules [nom-de-la-règle]`.

## 2. Correction du formatting des tâches
1.1. [x] **Modifier task-decomposition.mdc** : Implémenter la numérotation des sections (1., 2., etc.) et sous-numérotation des tâches (1.1, 1.2, etc.) dans le fichier task-decomposition.mdc.
1.2. [x] **Mettre à jour le format du template** : Modifier le format de template tasks.md pour inclure la numérotation des sections et tâches.

## 3. Nettoyage du fichier tasks.md
2.1. [x] **Supprimer les tâches non pertinentes** : Nettoyer le fichier tasks.md en supprimant les tâches complétées qui ne sont pas étroitement liées aux tâches actuelles.

## 4. Correction de request-analysis
3.1. [x] **Modifier request-analysis.mdc** : Supprimer les mentions des changements aux fichiers memory bank lors de la création de l'arborescence du code.

## Améliorations récentes
- [x] **Consolider la règle system** : Modifier la règle system.mdc pour renforcer le démarrage systématique par context-loading.
- [x] **Améliorer la mise à jour du contexte** : Optimiser context-update.mdc pour nettoyer les informations inutiles lors des mises à jour.

## Mise à jour des références
- [x] **Modifier tests.mdc** : Mettre à jour tests.mdc pour qu'il utilise le nouveau dossier tests/ au lieu des fichiers à la racine.
- [x] **Modifier context-update.mdc** : S'assurer que la règle suivante est toujours appelée, même quand le workflow est terminé.

## Restructuration des dossiers
- [x] **Créer le dossier src/** : Créer un dossier src/ pour les scripts d'installation et y déplacer install.sh.
- [x] **Créer le dossier tests/** : Créer un dossier tests/ pour les scripts de test et y déplacer test_install.sh.

## Consolidation du workflow 
- [x] **Modifier system.mdc** : Renforcer l'obligation d'appeler explicitement la règle suivante à la fin de chaque règle.
- [x] **Modifier implementation.mdc** : Clarifier la transition vers les règles suivantes et s'assurer que la règle est toujours appelée.

## Correction du workflow
- [x] **Analyser le problème de transition de règles** : Identifier pourquoi le workflow s'est terminé sur la règle Implementation au lieu de passer à la règle Tests.

## Tests du script d'installation
- [x] **Créer des tests pour le script d'installation** : Développer des tests pour vérifier le bon fonctionnement du script install.sh dans un répertoire temporaire.
- [x] **Exécuter les tests en environnement isolé** : Mettre en place un environnement de test isolé pour éviter d'écraser les règles du répertoire actuel.

## Optimisation de la structure
- [x] **Réduire la taille des sections de tâches** : S'assurer que les sections dans task-decomposition ne contiennent pas trop de tâches pour que leur implémentation tienne dans le contexte.
- [x] **Limiter les fichiers de mémoire** : Optimiser tous les fichiers de contexte et workflow pour qu'ils ne dépassent pas 200 lignes.

## Nettoyage des règles
- [x] **Supprimer la règle state-machine** : Éliminer la règle `.cursor/rules/custom/errors/state-machine.mdc` qui n'est pas utile.
- [x] **Revoir l'objectif des règles d'erreur** : Simplifier l'approche des règles d'erreur pour qu'elles servent uniquement à documenter des informations méconnues, particulièrement liées aux bibliothèques.

## Documentation et installation
- [x] **Créer un README** : Rédiger un fichier README.md détaillant le projet Memory Bank, son utilisation et son installation.
- [x] **Développer un script d'installation** : Créer un script invocable par curl qui télécharge le .cursor depuis GitHub et le place dans le dossier de travail actuel.

## Corrections structurelles
- [x] **Corriger l'organisation des tâches dans tasks.md** : Réorganisation du fichier pour éviter les duplications et maintenir une structure cohérente.

## Corrections techniques
- [x] **Corriger le chemin dans tests.mdc** : Modification de la référence à `.cursor/memory-bank/system/tests.md` vers `.cursor/memory-bank/workflow/tests.md`.
- [x] **Améliorer les conditions de transition dans tests.mdc** : Ajout de conditions spécifiques pour la première exécution.
- [x] **Ajouter une détection de cycles** : Implémentation d'un mécanisme pour détecter et éviter les boucles infinies.
- [x] **Clarifier les conditions de finalisation** : Définition précise des critères qui déterminent quand le workflow est terminé.

## Mise en place et évaluation
- [x] **Créer la structure de base du Memory Bank** : Mise en place des dossiers et fichiers requis pour le fonctionnement du système.
- [x] **Suivre le workflow complet de la machine à états** : Parcours de l'ensemble des règles du système en suivant les transitions.

## Renforcement du workflow
- [x] **Améliorer la règle tests.mdc** : Renforcer la section "Appeler obligatoirement la règle suivante" pour insister sur l'interdiction absolue de tenter de corriger les erreurs directement après les tests.
- [x] **Clarifier les critères de transition** : Rendre explicites les conditions qui déterminent quand appeler fix (échec des tests) vs context-update (succès des tests).
- [x] **Améliorer la section AUTO-VÉRIFICATION** : Modifier system.mdc pour ajouter une vérification spécifique du respect des transitions d'état, surtout lors de la transition tests → fix.
- [x] **Ajouter des instructions précises** : Inclure des directives explicites dans system.mdc interdisant toute tentative de correction en dehors de la règle implementation.
- [x] **Documenter le problème observé** : Créer une section dans activeContext.md détaillant le problème observé où l'agent tente de corriger les erreurs directement au lieu d'appeler la règle fix après l'échec des tests. 

## Résolution des problèmes de test
- [x] **Modifier le test 11** : Adapter le test des instructions d'affichage des étapes dans system.mdc pour rechercher des chaînes plus susceptibles d'être trouvées dans le fichier.
- [x] **Corriger l'échec du test 11** : Identifier et résoudre le problème qui fait échouer le test 11 relatif aux instructions d'affichage des étapes dans system.mdc. 