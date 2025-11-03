## Contexte

Lors d'une discussion sur l'amélioration du système de roadmap, il a été identifié qu'il serait utile d'avoir une commande dédiée `/clean` qui permet de nettoyer automatiquement les tâches marquées comme `in-progress` dans la roadmap. Actuellement, cette vérification est effectuée uniquement lors de l'exécution de `/agent` (étape 2.0), mais une commande autonome permettrait de maintenir la roadmap propre à tout moment, indépendamment de l'utilisation de `/agent`.

La logique attendue est simple : pour chaque tâche `in-progress`, vérifier si son fichier résultat existe. Si oui, archiver la tâche (comme le fait actuellement l'étape 2.0 de `/agent`). Si non, remettre la tâche en `todo` car cela indique que la tâche a été abandonnée ou interrompue sans avoir été complétée.

Cette commande sera utile pour maintenir l'hygiène de la roadmap sans avoir à invoquer `/agent`, et permettra de récupérer des tâches qui ont été marquées `in-progress` mais jamais terminées.

## Objectif

Créer une nouvelle commande `/clean` qui parcourt toutes les tâches avec `state: "in-progress"` dans la roadmap, vérifie l'existence de leur fichier résultat (`output_file`), et :
- Si le fichier résultat existe : archive la tâche (supprime l'entrée de la roadmap, met à jour les dépendances des autres tâches, supprime le fichier de tâche)
- Si le fichier résultat n'existe pas : remet la tâche en `state: "todo"` pour qu'elle puisse être reprise plus tard

La commande doit suivre le même comportement que l'étape 2.0 de `/agent` pour l'archivage, et doit être autonome (peut être exécutée indépendamment de `/agent`).

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Contient l'étape 2.0 qui effectue déjà le nettoyage des tâches in-progress terminées (lignes 23-37). Cette logique doit être réutilisée ou adaptée pour `/clean`.
- `.cursor/agents/roadmap.yaml` : Fichier central qui contient toutes les tâches. La commande `/clean` doit le lire et le modifier.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/commands/` : Dossier contenant les autres commandes (`agent.md`, `task.md`, `janitor.md`, `enqueteur.md`, `prompt.md`). Examiner la structure et le format des commandes existantes pour maintenir la cohérence.
- `.cursor/rules/agent.mdc` : Règles de la roadmap qui documentent comment les tâches sont gérées. Peut contenir des informations utiles sur le format et les comportements attendus.

### Recherches à effectuer :
- Recherche sémantique : "Comment les autres commandes comme /janitor ou /enqueteur sont-elles structurées ?"
- Recherche sémantique : "Comment fonctionne l'archivage des tâches dans l'étape 2.0 de /agent ?"
- Documentation : Lire `README.md` pour comprendre le contexte du projet et les conventions de commandes

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun fichier de résultat pertinent identifié pour le moment.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-creer-commande-clean-nettoyer-taches-in-progress.md`

## Instructions de Collaboration

**OBLIGATOIRE ET CRITIQUE** : Avant toute implémentation, l'agent **DOIT** :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** examiner la structure et le format des autres commandes dans `.cursor/commands/` pour comprendre le pattern à suivre
- **DOIT** comprendre en détail comment l'étape 2.0 de `/agent` fonctionne pour réutiliser ou adapter cette logique
- **DOIT** effectuer toutes les recherches sémantiques mentionnées pour comprendre le contexte complet
- **DOIT** lire le README et toute documentation pertinente
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les cas limites (que faire si roadmap.yaml n'existe pas, que faire si une tâche in-progress a des dépendances actives, etc.), et établir un plan d'action détaillé ensemble
- **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

L'exploration est OBLIGATOIRE, pas optionnelle. La commande `/clean` doit être cohérente avec les autres commandes existantes et respecter les mêmes conventions de format et de comportement.

