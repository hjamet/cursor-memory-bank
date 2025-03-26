# Contexte Actif

## Focus Actuel
Amélioration du workflow Memory Bank avec standardisation des règles, ajout de phrases de résumé, correction de la syntaxe d'invocation, amélioration de la gestion des tâches et ajout d'exemples d'utilisation.

## Problèmes Résolus
- ✅ Structure non standardisée: Standardisation de toutes les règles pour suivre exactement la même structure claire: TLDR, Instructions, Précisions, Next Rules.
- ✅ Absence de résumé après invocation: Ajout d'une phrase de résumé dans chaque règle que l'agent doit réciter après l'avoir invoquée.
- ✅ Position incorrecte des résumés d'invocation: Déplacement de la section "Résumé d'invocation" à la fin de chaque règle, juste avant "Next Rules".
- ✅ Format inconsistant des résumés: Standardisation du format avec balises "<SYSTEM PROMPT>" pour tous les résumés d'invocation.
- ✅ Lecture excessive de fichiers: Correction de la règle context-loading pour limiter strictement la lecture aux trois fichiers de contexte spécifiés.
- ✅ Numérotation des tâches: Implémentation d'un système de numérotation des sections et sous-numérotation des tâches.
- ✅ Arborescence du code: Correction de la règle request-analysis pour éviter les mentions aux fichiers memory bank.
- ✅ Structure du projet: Organisation optimisée avec dossiers src/ et tests/.
- ✅ Workflow robuste: Consolidation des règles pour garantir l'appel explicite à la règle suivante.
- ✅ Format des exemples: Standardisation des exemples avec utilisation de [...] pour le contenu dynamique.
- ✅ Position des exemples: Déplacement de la section "Exemple" entre "Next Rules" et "Start Rule".
- ✅ Phrases explicatives: Ajout de phrases explicatives dans les exemples pour guider l'agent.
- ✅ Structure des tâches: Amélioration de la règle task-decomposition pour avoir des sections de plus haut niveau avec des tâches plus détaillées.

## Problèmes En Cours de Résolution
- ⚠️ Syntaxe d'invocation incorrecte: La syntaxe d'appel des règles doit être modifiée pour utiliser `fetch_rules ["nom-de-la-règle"]` au lieu de `@cursor-rules fetch [nom-de-la-règle]`.
- ⚠️ Suppression insuffisante des tâches terminées: Le nettoyage des tâches terminées dans tasks.md n'est pas suffisamment agressif.
- ⚠️ Adhérence insuffisante au workflow: L'agent a encore tendance à sortir du workflow défini dans certains cas.

## Décisions Récentes
- [29/03/2024] - Amélioration de la règle task-decomposition pour des sections de plus haut niveau
- [29/03/2024] - Standardisation des exemples avec utilisation de [...] pour le contenu dynamique
- [29/03/2024] - Déplacement de la section "Exemple" entre "Next Rules" et "Start Rule"
- [29/03/2024] - Ajout de phrases explicatives dans les exemples
- [29/03/2024] - Déplacement de la section "Résumé d'invocation" à la fin de chaque règle
- [29/03/2024] - Standardisation du format des résumés d'invocation avec balises "<SYSTEM PROMPT>"
- [28/03/2024] - Standardisation de la structure de toutes les règles (TLDR, Instructions, Précisions, Next Rules)
- [28/03/2024] - Ajout de phrases de résumé dans chaque règle pour guider l'agent
- [28/03/2024] - Restructuration complète de system.mdc pour suivre la même structure que les autres règles
- [26/03/2024] - Limitation stricte de la lecture de fichiers dans context-loading
- [26/03/2024] - Implémentation de la numérotation des tâches et sections
- [26/03/2024] - Correction de request-analysis pour l'arborescence du code
- [26/03/2024] - Nettoyage du fichier tasks.md
- [2024-03-19] - Ajout d'une section Exemple à la règle request-analysis pour améliorer la documentation

## Prochaines Étapes
- Corriger la syntaxe d'invocation dans toutes les règles
- Améliorer la gestion des tâches terminées
- Renforcer l'adhérence au workflow
- Simplifier le langage des règles
- Tester les améliorations
- Ajouter les exemples manquants dans les règles restantes
- Vérifier la cohérence des exemples
- Vérifier que toutes les autres règles ont une section Exemple
- Maintenir la cohérence des sections Exemple entre les règles

## Notes Importantes
- La section "Résumé d'invocation" est maintenant toujours placée à la fin de chaque règle, juste avant la section "Next Rules"
- Tous les résumés d'invocation utilisent le format standardisé avec balises "<SYSTEM PROMPT>"
- L'invocation correcte des règles doit utiliser la syntaxe `fetch_rules ["nom-de-la-règle"]` et non `@cursor-rules fetch [nom-de-la-règle]`
- L'agent doit toujours réciter mot pour mot la phrase de résumé après avoir invoqué une règle
- Lors de l'exécution du workflow, toujours indiquer les numéros des tâches en cours de résolution
- Maintenir les fichiers de contexte et workflow en dessous de 200 lignes
- Toujours respecter la structure de dossiers avec src/ et tests/
- Ne jamais sortir du workflow sans appeler explicitement la règle suivante
- Durant context-loading, se limiter strictement aux trois fichiers de contexte spécifiés, ne pas lire tasks.md
- La section "Exemple" est maintenant ajoutée entre "Next Rules" et "Start Rule" dans chaque règle
- Les exemples utilisent [...] pour représenter le contenu dynamique
- Les exemples incluent des phrases explicatives pour guider l'agent à chaque étape
- Les tâches sont maintenant organisées en sections de plus haut niveau avec des descriptions détaillées
- Les sections Exemple sont essentielles pour comprendre comment chaque règle doit être utilisée
