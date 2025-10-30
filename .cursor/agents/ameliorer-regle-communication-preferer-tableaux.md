## Contexte

Travail actuel sur la correction du comportement de `/agent` en mode plan (task-5 et task-11) → implémentation effectuée avec succès avec plusieurs modifications dans `.cursor/commands/agent.md`. L'utilisateur souhaite améliorer la règle de communication pour encourager l'utilisation de tableaux plutôt que de listes à puces, lorsque cela est pertinent.

La règle de communication actuelle (`communication.mdc`) autorise déjà les tableaux dans certains cas ("quand la comparaison aide, préférez un tableau à 2–4 colonnes maximum"), mais pourrait être améliorée pour être plus directive sur ce point et réduire au maximum l'usage de listes à puces quand les tableaux sont plus appropriés.

## Objectif

Améliorer la règle de communication pour encourager activement l'utilisation de tableaux plutôt que de listes à puces, lorsque cela améliore la lisibilité et la compréhension. L'objectif est d'être plus directif sur quand et comment utiliser des tableaux pour structurer l'information.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Commande `/agent` récemment modifiée pour corriger le comportement en mode plan - contient plusieurs listes à puces qui pourraient être transformées en tableaux
- `.cursor/rules/communication.mdc` : Règle de communication actuelle - fichier principal à modifier pour être plus directif sur l'usage des tableaux
- `.cursor/rules/README.mdc` : Règle README - pourrait contenir des listes pertinentes
- `.cursor/rules/agent.mdc` : Règle agent - contient des sections avec listes qui pourraient être en tableaux

### Fichiers potentiellement pertinents pour l'exploration :
- Tous les fichiers `.mdc` dans `.cursor/rules/` : Autres règles qui pourraient bénéficier de tableaux
- Tous les fichiers `.md` dans `.cursor/commands/` : Autres commandes avec des structures de liste
- `README.md` : Documentation principale qui contient de nombreuses listes structurées

### Recherches à effectuer :
- Recherche sémantique : "Où sont utilisées des listes à puces dans les règles et commandes qui pourraient être remplacées par des tableaux ?"
- Documentation : Exemples de bonnes pratiques de mise en forme markdown avec tableaux

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun pour le moment

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-ameliorer-regle-communication-preferer-tableaux.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre la règle de communication actuelle et identifier où les tableaux seraient plus appropriés que les listes
2. **IDENTIFIE** des exemples concrets de listes à puces qui pourraient être transformées en tableaux pour améliorer la lisibilité
3. **COMPRENDS** les cas d'usage spécifiques où les tableaux sont préférables aux listes (comparaisons, métadonnées structurées, informations à colonnes multiples)
4. **PROPOSE** une amélioration de la règle `communication.mdc` qui soit plus directive sur l'usage des tableaux
5. **DISCUTE avec l'utilisateur** pour clarifier :
   - Quels types de listes sont prioritaires pour transformation en tableaux ?
   - Faut-il des exemples concrets dans la règle ?
   - Doit-on aussi modifier des fichiers existants comme exemples ou seulement mettre à jour la règle ?
6. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
7. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer toute modification de `communication.mdc` ou d'autres fichiers. L'exploration est OBLIGATOIRE, pas optionnelle.

