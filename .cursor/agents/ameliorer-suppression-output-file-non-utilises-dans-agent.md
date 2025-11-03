## Contexte

Lors d'une discussion sur l'optimisation de la gestion des fichiers dans le système de roadmap, il a été identifié qu'actuellement, lorsqu'une tâche `in-progress` est supprimée (archivée) par l'étape 2.0 de `/agent`, son fichier résultat (`output_file`) est toujours conservé, même si aucune autre tâche ne le référence dans ses `dependencies-results`.

Cela crée une accumulation de fichiers de résultats inutiles qui ne sont référencés nulle part, ce qui :
- Encombre le répertoire `.cursor/agents/` avec des fichiers non utilisés
- Rend difficile la navigation et la compréhension de l'historique réellement utilisé
- Consomme de l'espace disque inutilement

La logique proposée est simple : avant de supprimer une tâche `in-progress` terminée, vérifier si son `output_file` est référencé dans les `dependencies-results` d'autres tâches. Si aucune référence n'existe, supprimer également le fichier `output_file` lors de l'archivage de la tâche.

Cette amélioration permettra de maintenir une roadmap plus propre en ne conservant que les fichiers de résultats qui sont réellement utilisés comme contexte par d'autres tâches.

## Objectif

Améliorer l'étape 2.0 de la commande `/agent` pour qu'elle vérifie, avant de supprimer une tâche `in-progress` terminée, si son fichier `output_file` est référencé dans les `dependencies-results` d'autres tâches dans la roadmap.

- Si le `output_file` est référencé (présent dans au moins un `dependencies-results` d'une autre tâche) : conserver le fichier (comportement actuel)
- Si le `output_file` n'est référencé nulle part : supprimer le fichier `output_file` en plus de supprimer la tâche et son fichier de tâche

Cette amélioration doit être intégrée dans la logique existante de l'étape 2.0 sans casser le comportement actuel pour les fichiers qui sont réellement utilisés.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Contient l'étape 2.0 (lignes 23-37) qui effectue le nettoyage des tâches in-progress terminées. Cette étape doit être modifiée pour ajouter la vérification des références et la suppression conditionnelle de l'`output_file`.
- `.cursor/agents/roadmap.yaml` : Fichier central qui contient toutes les tâches avec leurs `dependencies-results`. La logique doit parcourir toutes les tâches pour vérifier les références.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/rules/agent.mdc` : Règles de la roadmap qui documentent le fonctionnement de `dependencies-results` et le comportement attendu de l'archivage. Peut contenir des informations utiles sur les conventions.
- `.cursor/agents/` : Dossier contenant les fichiers de résultats. Examiner la structure pour comprendre comment les fichiers sont organisés.

### Recherches à effectuer :
- Recherche sémantique : "Comment fonctionne dependencies-results dans la roadmap ?"
- Recherche sémantique : "Quelle est la logique complète de l'étape 2.0 de /agent pour l'archivage des tâches ?"
- Documentation : Lire `README.md` pour comprendre le contexte du projet

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun fichier de résultat pertinent identifié pour le moment.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ameliorer-suppression-output-file-non-utilises-dans-agent.md`

## Instructions de Collaboration

**OBLIGATOIRE ET CRITIQUE** : Avant toute implémentation, l'agent **DOIT** :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** comprendre en détail comment l'étape 2.0 de `/agent` fonctionne actuellement (lignes 23-37 de `agent.md`)
- **DOIT** comprendre comment `dependencies-results` est utilisé dans la roadmap et comment parcourir toutes les tâches pour vérifier les références
- **DOIT** effectuer toutes les recherches sémantiques mentionnées pour comprendre le contexte complet
- **DOIT** lire le README et toute documentation pertinente
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les cas limites (que faire si le fichier output_file n'existe pas mais est référencé, que faire s'il y a des références dans des tâches qui seront aussi supprimées, etc.), et établir un plan d'action détaillé ensemble
- **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

L'exploration est OBLIGATOIRE, pas optionnelle. La modification doit être soigneusement intégrée dans la logique existante sans casser le comportement actuel.

