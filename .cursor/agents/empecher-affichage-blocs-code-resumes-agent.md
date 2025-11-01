## Contexte

Lors des dernières interactions avec la commande `/agent`, l'utilisateur a observé que l'agent présente systématiquement des blocs de code dans ses résumés de tâches. Cette habitude surcharge les explications et détourne l'attention du discours en langage naturel attendu. Ce constat a émergé pendant l'analyse des règles décrivant la commande `/task`, révélant un besoin clair d'ajuster la manière dont les résumés sont générés et présentés.

## Objectif

Explorer les mécanismes qui pilotent la génération des résumés de tâches afin d'empêcher l'apparition de blocs de code dans ces messages et de garantir une communication exclusivement textuelle et narrative.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/rules/task.md` : Document actuel détaillant la gestion de la commande `/task`, point de départ de la remontée de l'anomalie.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/rules/agent.mdc` : Spécifie le comportement attendu lors de la commande `/agent` et pourrait contenir les règles à ajuster.
- `.cursor/agents/roadmap.yaml` : Référentiel centralisé où inscrire les tâches et valider la cohérence avec les autres travaux.

### Recherches à effectuer :
- Recherche sémantique : "Comment les résumés de la commande /agent sont-ils formatés".
- Recherche web : "Best practices for natural language summaries without code blocks".
- Documentation interne : Vérifier les guides éventuels dans `documentation/` sur les conventions de communication de l'agent.

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun rapport existant identifié pour ce sujet.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-empecher-affichage-blocs-code-resumes-agent.md`

## Instructions de Collaboration

- **IL EST INTERDIT** de commencer une implémentation immédiate ; l'exploration détaillée est obligatoire au préalable.
- **IL DOIT** lire exhaustivement tous les fichiers listés dans "Fichiers Concernés" avant toute autre action.
- **IL DOIT** effectuer toutes les recherches sémantiques et web mentionnées pour comprendre le contexte existant.
- **IL DOIT** consulter le README et toute documentation pertinente afin de saisir les conventions de communication actuelles.
- **IL DOIT** dialoguer avec l'utilisateur pour clarifier les attentes précises, les contraintes techniques et convenir d'un plan d'action détaillé.
- **IL DOIT** rédiger le rapport final dans le fichier output indiqué une fois l'analyse et la planification terminées.
- Ce n'est qu'après cette exploration exhaustive et cette planification collaborative qu'une éventuelle implémentation pourra débuter.

