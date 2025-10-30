## Contexte

Lors de la présentation de la « Tâche sélectionnée » par `/agent`, l'agent n'affiche actuellement que le titre de la tâche. Pour aider à la priorisation et à la vue d'ensemble, il est souhaité d'afficher, entre parenthèses, le nombre de tâches restantes par priorité avec des emojis (🔴, 🟠, 🔵, 🟢).

## Objectif

Explorer l'ajout d'un indicateur synthétique au titre affiché par `/agent` listant les compteurs de tâches restantes par priorité (5→🔴, 4→🟠, 3→🔵, 2/1→🟢 ou à décider), calculés sur la roadmap filtrée selon les règles de disponibilité.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Source de vérité pour compter les tâches par priorité et statut
- `.cursor/rules/agent.mdc` : Règles de sélection, disponibilité et tri des tâches

### Fichiers potentiellement pertinents pour l'exploration :
- `README.md` : Décrit l'UX et la présentation attendue de `/agent`
- `.cursor/agents/TEMPLATE.md` : Format des fichiers de tâches (référence générale)

### Recherches à effectuer :
- Recherche sémantique : « Où est construit le rendu de la section Tâche sélectionnée ? »
- Recherche sémantique : « Comment sont filtrées les tâches disponibles (dépendances, timeout, priorités) ? »
- Documentation : Relire `README.md` pour valider la sémantique des statuts et priorités

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-*` : Rapports pouvant influencer les règles de disponibilité

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-afficher-compteurs-priorites-dans-titre-agent.md`

## Instructions de Collaboration

- Il est INTERDIT d'implémenter tout de suite.
- Tu DOIS lire les fichiers listés dans « Fichiers Concernés ».
- Tu DOIS définir précisément la correspondance priorité→emoji avec l'utilisateur et la granularité voulue (p.ex. 5=🔴, 4=🟠, 3=🔵, 2–1=🟢).
- Tu DOIS valider si les compteurs portent sur « disponibles » (après filtrage dépendances/timeout) ou « toutes tâches restantes ».
- Tu DOIS écrire le rapport final dans le fichier output mentionné.
- Ce n'est QU'APRÈS l'exploration exhaustive et la discussion que tu commencerais l'implémentation.


