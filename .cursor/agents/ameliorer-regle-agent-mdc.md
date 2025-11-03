## Contexte

La règle `agent.mdc` contient des instructions sur la création automatique de tâches dans la roadmap centralisée. Cependant, cette règle nécessite plusieurs améliorations :

1. **Mise à jour avec la nouvelle commande /agent** : La règle doit refléter les changements récents dans la commande `/agent`, notamment l'étape 2.0 de nettoyage des tâches terminées et les nouvelles fonctionnalités de gestion des `dependencies-results`.

2. **Réduction de la longueur** : La règle est actuellement trop longue (307 lignes) et contient des répétitions qui pourraient être condensées sans perdre d'informations critiques.

3. **Emphase sur la création du rapport** : Il est CRITIQUE d'insister sur le fait que la création du fichier de rapport final est OBLIGATOIRE et doit TOUJOURS être ajoutée comme dernière étape de tout plan d'implémentation. Sans ce fichier, la tâche ne sera jamais marquée comme validée (via l'étape 2.0 de `/agent` ou `/clean`), ce qui est un problème grave dans le système de roadmap.

Cette amélioration est nécessaire pour maintenir la cohérence entre la règle et la commande `/agent`, améliorer la lisibilité, et surtout garantir que les agents comprennent l'importance absolue de créer le fichier de rapport.

## Objectif

Mettre à jour la règle `agent.mdc` pour qu'elle reflète fidèlement la commande `/agent` actuelle, la condenser pour améliorer sa lisibilité, et surtout insister de manière très explicite et répétée sur le fait que la création du fichier de rapport final est OBLIGATOIRE et doit TOUJOURS être la dernière étape de tout plan d'implémentation, sans exception. La règle doit clairement expliquer que sans ce fichier, la tâche ne sera jamais considérée comme terminée par le système.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/rules/agent.mdc` : Règle à améliorer avec mise à jour, réduction et emphase sur le rapport final.
- `.cursor/commands/agent.md` : Commande `/agent` avec sa logique actuelle, notamment l'étape 2.0 de nettoyage et la détection des tâches terminées via les fichiers output.
- `.cursor/commands/task.md` : Commande `/task` pour comprendre comment les tâches sont créées et leur format.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/agents/roadmap.yaml` : Pour comprendre la structure actuelle des tâches et le champ `output_file`.
- `.cursor/commands/clean.md` : Pour comprendre comment `/clean` détecte les tâches terminées via les fichiers output.
- Exemples de fichiers de rapports dans `.cursor/agents/rapport-*.md` : Pour voir la structure des rapports finaux.

### Recherches à effectuer :
- Recherche sémantique : "Comment les fichiers de rapports sont utilisés pour détecter les tâches terminées ?"
- Documentation : Lire `README.md` pour comprendre comment la commande `/agent` est documentée.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ameliorer-regle-agent-mdc.md`

## Instructions de Collaboration

**OBLIGATOIRE ET CRITIQUE** : Cette section doit être extrêmement directive et impérative. Tu DOIS spécifier que l'agent :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** effectuer toutes les recherches sémantiques mentionnées
- **DOIT** lire le README et toute documentation pertinente
- **DOIT** comparer minutieusement la règle `agent.mdc` avec la commande `/agent` actuelle pour identifier tous les écarts
- **DOIT** identifier toutes les répétitions et sections redondantes dans la règle pour proposer une version condensée
- **DOIT** comprendre précisément comment l'étape 2.0 de `/agent` et `/clean` détectent les tâches terminées via les fichiers output, et pourquoi il est CRITIQUE que ces fichiers soient toujours créés
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les priorités (réduction vs exhaustivité), et établir un plan d'action détaillé ensemble
- **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé
- **DOIT TOUJOURS** créer le fichier de rapport à la fin du chat, que la tâche soit réussie ou non (voir section "Instructions pour les Rapports Finaux")
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

**IMPORTANT CRITIQUE** : L'agent doit comprendre que la création du fichier de rapport est la chose la plus importante de cette tâche. Cette information doit être répétée, mise en évidence, et intégrée dans plusieurs sections de la règle mise à jour pour garantir qu'aucun agent ne l'oublie.

L'exploration est OBLIGATOIRE, pas optionnelle.

