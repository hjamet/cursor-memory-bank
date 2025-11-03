## Contexte

Lors de l'exécution de la commande `/clean`, les fichiers résultats (`output_file`) des tâches archivées sont supprimés lorsqu'ils ne sont plus référencés dans les `dependencies-results` d'autres tâches. Cependant, ces fichiers de rapports contiennent des informations importantes sur les modifications apportées, les décisions prises, et les changements effectués qui devraient être préservées selon la règle `README.mdc`.

La règle `README.mdc` indique que le README doit être maintenu constamment à jour à chaque modification du code, ajout/suppression de dépendances, services, bases de données, ou modification des scripts d'installation. Les rapports de tâches contiennent justement ces informations importantes qui devraient être intégrées dans le README avant la suppression des fichiers.

Actuellement, la commande `/clean` supprime silencieusement ces fichiers sans extraire et préserver les informations critiques dans le README, ce qui va à l'encontre de la règle de maintenance du README.

## Objectif

Améliorer la commande `/clean` pour qu'elle extraie les informations importantes des fichiers résultats (`output_file`) avant leur suppression, et les intègre automatiquement dans le README conformément à la règle `README.mdc`. Cette amélioration doit garantir que les modifications documentées dans les rapports ne soient pas perdues et soient correctement reflétées dans la documentation principale du projet.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/clean.md` : Commande `/clean` qui archive les tâches terminées et supprime les fichiers résultats non référencés. Cette logique doit être étendue pour extraire les informations des rapports avant suppression.
- `.cursor/agents/roadmap.yaml` : Contient les métadonnées des tâches archivées, permettant d'identifier les fichiers résultats à traiter.
- `.cursor/commands/agent.md` : Contient l'étape 2.0 qui effectue un nettoyage similaire et supprime aussi les fichiers résultats. Cette logique pourrait être partagée ou servir de référence pour l'extraction d'informations.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/rules/README.mdc` : Règle définissant les obligations de mise à jour du README et les sections obligatoires à maintenir.
- `README.md` : Fichier principal à mettre à jour avec les informations extraites des rapports supprimés.
- `.cursor/agents/rapport-*.md` : Exemples de fichiers résultats pour comprendre leur structure et identifier les informations critiques à extraire (modifications apportées, décisions prises, fichiers modifiés, services ajoutés, etc.).

### Recherches à effectuer :
- Recherche sémantique : "Comment sont structurés les fichiers de rapports dans le dossier agents ?"
- Recherche sémantique : "Quelles sections du README doivent être mises à jour selon la règle README.mdc ?"
- Documentation : Lire `README.md` pour comprendre la structure actuelle et identifier où intégrer les nouvelles informations.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ameliorer-commande-clean-informations-resultats-readme.md`

## Instructions de Collaboration

**OBLIGATOIRE ET CRITIQUE** : Cette section doit être extrêmement directive et impérative. Tu DOIS spécifier que l'agent :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** effectuer toutes les recherches sémantiques mentionnées
- **DOIT** lire le README et toute documentation pertinente pour comprendre la structure actuelle
- **DOIT** analyser plusieurs exemples de fichiers de rapports pour identifier les patterns d'information à extraire
- **DOIT** comprendre précisément quelles informations du README doivent être mises à jour selon la règle README.mdc (commandes principales, services & bases de données, variables d'environnement, architecture, fichiers importants, etc.)
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les contraintes techniques, et établir un plan d'action détaillé ensemble
- **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé
- **DOIT TOUJOURS** créer le fichier de rapport à la fin du chat, que la tâche soit réussie ou non (voir section "Instructions pour les Rapports Finaux")
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

L'exploration est OBLIGATOIRE, pas optionnelle.

