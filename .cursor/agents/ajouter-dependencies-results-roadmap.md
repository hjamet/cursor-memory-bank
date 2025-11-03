## Contexte

Lorsqu'une tâche dépendante est complétée et archivée dans la roadmap, actuellement le système retire simplement son ID de la liste `dependencies` des tâches qui en dépendaient. Cependant, cette approche perd l'information précieuse contenue dans les rapports de résultats des dépendances terminées. Les agents qui travaillent sur des tâches ayant eu des dépendances doivent pouvoir accéder facilement aux rapports de ces dépendances pour comprendre le contexte et les décisions prises lors de leur implémentation. Il serait donc bénéfique d'ajouter un système de `dependencies-results` qui conserve les références aux fichiers de résultats des dépendances terminées, permettant ainsi une meilleure continuité de contexte entre les tâches liées.

## Objectif

Ajouter un champ `dependencies-results` dans la structure de la roadmap pour toutes les tâches. Ce champ doit contenir une liste des noms des fichiers de rapports (.md) des tâches dépendances qui ont été complétées. Le système doit automatiquement remplir ce champ lorsque des dépendances sont archivées, et l'agent doit lire ces fichiers lors du chargement du contexte d'une tâche.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Structure actuelle de la roadmap avec les tâches et leurs dépendances
- `.cursor/commands/agent.md` : Commande `/agent` qui gère le nettoyage des tâches in-progress (étape 2.0) et le chargement du contexte (étape 3). C'est ici que la logique de `dependencies-results` doit être intégrée.

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/rules/agent.mdc` : Règles générales sur la gestion de la roadmap et des dépendances
- `.cursor/commands/task.md` : Commande `/task` qui crée de nouvelles tâches, potentiellement à adapter pour inclure le champ `dependencies-results`
- `.cursor/agents/TEMPLATE.md` : Template des fichiers de tâches, peut-être à mettre à jour si nécessaire

### Recherches à effectuer :
- Recherche sémantique : "Comment les dépendances de tâches sont-elles gérées lors de l'archivage d'une tâche complétée ?"
- Recherche sémantique : "Comment le contexte d'une tâche est chargé avec les fichiers mentionnés dans Fichiers Concernés ?"
- Documentation : Lire `README.md` pour comprendre l'architecture du projet

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun rapport spécifique à consulter pour l'instant

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ajouter-dependencies-results-roadmap.md`

## Instructions de Collaboration

**CRITIQUE** : L'agent qui traitera cette tâche **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Il **DOIT** :

1. Lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
2. Effectuer toutes les recherches sémantiques mentionnées dans la section "Recherches à effectuer"
3. Lire le README et toute documentation pertinente
4. Atteindre une compréhension approfondie du fonctionnement actuel du système de roadmap et de dépendances
5. Discuter avec l'utilisateur pour clarifier les attentes précises, notamment :
   - Comment gérer le champ `dependencies-results` lors de la création d'une nouvelle tâche (initialisé vide ?)
   - Comment garantir que les anciennes tâches existantes soient compatibles (ajouter le champ manquant ?)
   - Préciser le format exact attendu pour `dependencies-results` (liste de strings avec les noms de fichiers ? chemins complets ?)
   - Clarifier le comportement si plusieurs dépendances sont archivées simultanément
6. Établir un plan d'action détaillé avec l'utilisateur avant toute implémentation
7. Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, commencer toute implémentation
8. **DOIT TOUJOURS** créer le fichier de rapport final à la fin du chat, que la tâche soit réussie ou non

L'exploration est OBLIGATOIRE, pas optionnelle.

