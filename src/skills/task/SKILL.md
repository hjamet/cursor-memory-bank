---
name: task
description: "Ajout instantané d'une tâche contextualisée à la roadmap centralisée sans interrompre le travail en cours."
---

# 📋 Comment Ajouter Rapidement une Tâche Contextualisée à la Roadmap ?

## Objectif

Quand l'utilisateur tape `/task` avec une description de tâche, tu dois créer une nouvelle tâche dans la roadmap centralisée avec tout le contexte nécessaire, **SANS INTERROMPRE** le travail que tu étais en train d'effectuer. Après avoir créé et enregistré la tâche, tu continues exactement là où tu t'étais arrêté, comme si de rien n'était. 

**INTERDICTION ABSOLUE**: Tu ne dois JAMAIS commencer à implémenter ou planifier l'implémentation de la tâche nouvellement créée. La planification/implémentation appartiennent exclusivement à `/agent` après discussion avec l'utilisateur.

**CRITIQUE - CE QUE TU NE DOIS ABSOLUMENT PAS FAIRE** :
- ❌ Implémenter la modification demandée par l'utilisateur
- ❌ Planifier l'implémentation de cette modification
- ❌ Réfléchir à la solution technique pour cette modification
- ❌ Commencer quoi que ce soit lié à la modification demandée
- ❌ Modifier le code en rapport avec la tâche créée
- ❌ Proposer des solutions ou des approches d'implémentation
- ❌ Examiner les fichiers qui seraient modifiés pour cette tâche

**CE QUE TU DOIS UNIQUEMENT FAIRE** :
- ✅ Créer la tâche dans la roadmap avec le contexte nécessaire
- ✅ Reprendre immédiatement ton travail précédent comme si rien ne s'était passé

## Principe Fondamental

**CRITIQUE** : Cette commande est une **interruption non-bloquante**. Tu ne dois **JAMAIS** :
- Arrêter ce que tu étais en train de faire
- Démarrer l'implémentation de la nouvelle tâche
- Changer de contexte ou de focus
- Abandonner tes todos en cours
- **Effectuer la modification demandée par l'utilisateur** (l'utilisateur demande une modification, mais tu ne dois QUE créer une tâche, PAS l'implémenter)
- **Réfléchir à comment implémenter la modification** (cela appartient à l'agent qui traitera la tâche via `/agent`)
- **Modifier le code en rapport avec la modification demandée** (même si tu as des idées, tu ne dois rien changer)

Tu dois simplement **enregistrer la tâche** pour qu'un autre agent (via `/agent`) puisse la traiter plus tard, puis **reprendre immédiatement** ton travail précédent.

**IMPORTANT** : Quand l'utilisateur dit `/task optimiser les performances`, il demande que cette optimisation soit faite, mais toi tu ne dois QUE créer une tâche dans la roadmap. L'implémentation de l'optimisation sera faite plus tard par un autre agent (via `/agent`).

### Interdictions absolues (rappel)

**CRITIQUE - Rappel explicite de ce qui est INTERDIT** :

- ❌ Ne PAS créer de plan de transition pour cette nouvelle tâche
- ❌ Ne PAS modifier, refactorer ou amorcer un correctif relatif à la nouvelle tâche
- ❌ Ne PAS changer de contexte, d'onglet ou de fichier hors de ton travail en cours
- ❌ Ne PAS implémenter la modification demandée par l'utilisateur (même si elle semble simple)
- ❌ Ne PAS planifier comment implémenter cette modification
- ❌ Ne PAS réfléchir à la solution technique
- ❌ Ne PAS examiner les fichiers qui seraient modifiés pour cette tâche
- ❌ Ne PAS proposer des solutions ou des approches
- ❌ Ne PAS modifier le code en rapport avec la modification demandée

**EXEMPLE CONCRET** : Si l'utilisateur tape `/task améliorer la validation des emails`, tu dois :
- ✅ Créer la tâche "Améliorer la validation des emails" dans la roadmap
- ✅ Mentionner les fichiers de ton travail actuel dans "Fichiers Concernés"
- ✅ Confirmer : "✅ Tâche ajoutée (task-X)"
- ✅ Reprendre ton travail précédent

Tu ne dois PAS :
- ❌ Aller voir le code de validation des emails
- ❌ Réfléchir à comment améliorer la validation
- ❌ Commencer à modifier le code de validation
- ❌ Proposer une solution technique

## Priorité et Temporalité

**CRITIQUE** : `/task` est une **interruption obligatoire et immédiate** :

- **Priorité absolue** : La commande `/task` suspend **TOUT** travail en cours pour être traitée immédiatement
- **Traitement strictement séquentiel** : Si plusieurs `/task` sont invoquées, elles sont traitées l'une après l'autre
- **Réponse minimale** : La confirmation doit être la plus courte possible pour reprendre rapidement le flux initial

### Cas d'enchaînement

- **Multiples `/task`** : Si l'utilisateur tape `/task A /task B`, tu crées task-1, confirmes brièvement, puis crées task-2, confirmes, puis reprends le travail précédent
- **Pendant une autre commande** : Si l'utilisateur tape `/agent /task ...`, tu suspend l'exécution de `/agent`, crées la tâche, confirmes, puis reprends `/agent` là où tu l'avais laissé

## Comportement Requis

Lorsque l'utilisateur tape `/task [description de la tâche]`, tu dois :

### Étape 1 : Analyser la Demande et Préparer les Métadonnées

1. **Extraire la description** de la tâche fournie par l'utilisateur
2. **Identifier le contexte** de ton travail actuel pour comprendre pourquoi cette tâche est mentionnée
3. **Déterminer les métadonnées** :
   - Titre descriptif et actionnable
   - **IMPORTANT** : Vérifier que le titre est unique dans la roadmap pour éviter les collisions de noms de fichiers
  - **Description courte** : Générer une description de 3 phrases maximum qui résume l'objectif de la tâche. Cette description sera utilisée pour l'analyse automatique des dépendances avec les autres tâches
  - Dépendances éventuelles (si le travail actuel doit être terminé d'abord)

### Étape 2 : Lire la Roadmap et Générer l'ID

1. **Lire** `.cursor/agents/roadmap.yaml` pour obtenir toutes les tâches existantes
2. **Générer un ID unique** : Identifier le plus grand ID existant et incrémenter (ex: `task-1`, `task-2`, etc.)

### Étape 3 : Analyser les Dépendances Bidirectionnelles

**CRITIQUE** : Cette étape utilise les données lues à l'Étape 2.

1. **Pour chaque tâche existante** :
   - Lire son champ `description` (court résumé de 3 phrases max)
   - Comparer avec la description de la nouvelle tâche
   - Analyser les relations logiques :
     - **Tâches dont la nouvelle tâche dépend** : Tâches qui fournissent une infrastructure/base nécessaire, qui résolvent un problème bloquant, qui créent des fichiers/modules requis, ou qui établissent des conventions/patterns à suivre
     - **Tâches qui dépendent de la nouvelle tâche** : Tâches qui nécessitent ce que la nouvelle tâche va produire, qui sont bloquées par un problème que la nouvelle tâche résout, ou qui étendent/utilisent ce que la nouvelle tâche va créer
2. **Construire deux listes** :
   - `dependencies_new_task` : IDs des tâches dont la nouvelle tâche dépend
   - `dependencies_existing_tasks` : Liste des IDs des tâches existantes qui doivent dépendre de la nouvelle tâche

**Points importants** :
- Ne PAS lire les fichiers de tâches complets, utiliser uniquement le champ `description` de roadmap.yaml
- L'analyse doit être contextuelle et intelligente, pas exhaustive
- Si aucune dépendance n'est détectée, les listes restent vides (c'est normal)
- Ne PAS encore modifier roadmap.yaml à cette étape (ce sera fait à l'Étape 6)
- En cas d'erreur lors de l'analyse, **ÉCHOUER EXPLICITEMENT** avec message clair, mais reprendre le travail après avoir informé l'utilisateur

**Règle de graphe connecté** :
- **CRITIQUE** : Aucune tâche ne devrait être isolée dans le graphe de dépendances
- Il peut y avoir plusieurs points d'entrée possibles (tâches sans dépendances), mais toutes les tâches devraient avoir au moins un lien de dépendance dans le graphe
- Chaque tâche doit soit avoir des dépendances, soit être une dépendance d'une autre tâche (ou les deux)
- Si une nouvelle tâche est créée sans aucune dépendance et qu'aucune autre tâche ne dépend d'elle, l'analyse doit identifier au moins une relation logique pour créer un lien dans le graphe
- Si aucune relation logique ne peut être établie, créer une dépendance artificielle vers une tâche existante appropriée ou faire en sorte qu'une autre tâche dépende de la nouvelle tâche

### Étape 4 : Générer le Nom de Fichier

1. Convertir le titre en format kebab-case
2. **IMPORTANT** : Vérifier que le titre est unique dans la roadmap pour éviter les collisions
3. Nom du fichier de tâche : `{titre-kebab-case}.md`
4. Nom du fichier de résultat : `rapport-{titre-kebab-case}.md`

### Étape 5 : Créer le Fichier de Tâche

Créer le fichier `.cursor/agents/{nom-fichier-tache}.md` avec les 4 sections obligatoires :

#### Section 1 : Contexte

Écrire en français une histoire narrative expliquant :
- Pourquoi cette tâche existe (ce qui a été découvert, les problèmes identifiés, les opportunités)
- Le lien avec le travail actuel que tu effectuais
- Pourquoi cette tâche est importante ou nécessaire

**Exemple** : "Travail actuel sur [X] → découverte de [Y] → besoin de [Z] pour [raison]"

#### Section 2 : Objectif

Description vague mais claire de ce qui doit être accompli. Garder un ton exploratoire, pas trop précis.

#### Section 3 : Fichiers Concernés

Lister exhaustivement :
- **Du travail effectué précédemment** : Les fichiers que tu as modifiés/examinés dans ton travail actuel, avec explication
- **Fichiers potentiellement pertinents** : Fichiers qui pourraient être importants pour la tâche
- **Recherches à effectuer** : Recherches sémantiques, web, documentation à consulter
- **Fichiers de résultats d'autres agents** : Si pertinents
- **Fichier output** : `.cursor/agents/rapport-{titre-kebab-case}.md`

#### Section 4 : Instructions de Collaboration

Instructions impératives pour l'agent qui traitera cette tâche (via `/agent`) :
- INTERDIT d'implémenter immédiatement
- DOIT lire exhaustivement tous les fichiers
- DOIT effectuer toutes les recherches
- DOIT discuter avec l'utilisateur avant implémentation
- DOIT écrire le rapport final dans le fichier output

### Étape 6 : Ajouter à la Roadmap

1. **Déterminer la position d'insertion** :
   - Analyser les dépendances de la nouvelle tâche (liste `dependencies_new_task` de l'Étape 3)
   - Si la nouvelle tâche a des dépendances :
     - Parcourir le tableau `tasks` existant
     - Identifier la position la plus basse (plus loin dans le tableau) de toutes les tâches dont elle dépend
     - Insérer la nouvelle tâche juste après cette position (respectant ainsi l'ordre : les dépendances sont toujours avant la tâche qui en dépend)
   - Si la nouvelle tâche n'a pas de dépendances :
     - Insérer la nouvelle tâche au début du tableau `tasks` (première position)
   - **Principe** : La position dans le tableau définit l'ordre de traitement. La première tâche est la plus urgente, la dernière est la moins urgente.

2. **Ajouter l'entrée** dans la liste `tasks` à la position déterminée :

```yaml
- id: "task-{unique-id}"
  title: "Titre descriptif de la tâche"
  description: "Description courte de l'objectif de la tâche (3 phrases max)"  # Utilisé pour l'analyse de dépendances
  state: "todo"  # "todo" ou "in-progress" (toujours "todo" pour les nouvelles tâches)
  dependencies: []  # Liste d'IDs de tâches détectées lors de l'Étape 3
  dependencies-results: []  # Liste de noms de fichiers de rapports de dépendances terminées (format: liste de strings avec noms de fichiers uniquement, ex: ["rapport-tache-1.md"])
  task_file: "{nom-fichier-tache}.md"
  output_file: "rapport-{nom-fichier-tache}.md"
  deadline: null  # Optionnel
```

3. **Mettre à jour les dépendances bidirectionnelles** :
   - Remplir le champ `dependencies` de la nouvelle tâche avec `dependencies_new_task` de l'Étape 3
   - Pour chaque tâche existante dans `dependencies_existing_tasks` de l'Étape 3, ajouter l'ID de la nouvelle tâche à son champ `dependencies`

4. **Valider** :
   - Le fichier `task_file` existe (que tu viens de créer)
   - Les dépendances mentionnées existent dans la roadmap
   - Si validation échoue → **ÉCHOUER EXPLICITEMENT** avec message clair

5. **Sauvegarder** le fichier `roadmap.yaml`

### Étape 7 : Confirmation et Reprise

**CRITIQUE** : Après avoir créé la tâche, tu dois :

1. **Confirmer à l'utilisateur** (message minimal en français) :
   ```
   ✅ Tâche ajoutée (task-{id})
   ```

2. **Reprendre immédiatement** ton travail précédent comme si rien ne s'était passé :
   - Continuer tes todos en cours
   - Reprendre exactement là où tu t'étais arrêté
   - Ne pas mentionner la nouvelle tâche (elle est déléguée à un autre agent)
   - **NE PAS** commencer à implémenter la modification demandée
   - **NE PAS** réfléchir à la solution technique
   - **NE PAS** examiner les fichiers concernés par la modification
   - **NE PAS** proposer d'approches ou de solutions

**RAPPEL FORT** : L'utilisateur a demandé une modification via `/task`, mais cette modification sera implémentée PLUS TARD par un autre agent (via `/agent`). Toi, tu as UNIQUEMENT créé la tâche dans la roadmap. Tu ne dois rien faire d'autre concernant cette modification.

## Format de Réponse Minimal

Après avoir créé la tâche, répondre uniquement :

```
✅ Tâche ajoutée (task-{id})

[Reprendre immédiatement le travail précédent sans mentionner la tâche]
```

## Gestion des Erreurs (Fail-Fast)

Si une étape échoue :
- Arrêter la création de la tâche
- Informer l'utilisateur de l'erreur avec un message clair
- **Néanmoins, reprendre le travail précédent** après avoir informé de l'erreur

## Exemple Complet

**Situation** : Tu es en train d'implémenter un système d'authentification, l'utilisateur tape `/task il faudrait optimiser les performances plus tard`

**Actions** :
1. ✅ Analyser : "Optimiser les performances d'authentification" est une tâche future
   - Titre : "Optimiser les performances d'authentification"
   - Description : "Améliorer le temps de réponse du système d'authentification en optimisant les requêtes de base de données et en implémentant un cache pour les tokens JWT"
2. ✅ Lire roadmap.yaml et générer l'ID unique (task-1)
3. ✅ Analyser les dépendances bidirectionnelles avec les tâches existantes
4. ✅ Générer les noms de fichiers : `optimiser-performances-auth.md` et `rapport-optimiser-performances-auth.md`
5. ✅ Créer le fichier `optimiser-performances-auth.md` avec les 4 sections
6. ✅ Déterminer la position d'insertion et ajouter l'entrée dans `roadmap.yaml` avec les dépendances détectées
7. ✅ Confirmer : "✅ Tâche ajoutée (task-1)"
8. ✅ Reprendre immédiatement l'implémentation de l'authentification

**Ce que tu NE dois PAS faire** :
- ❌ Commencer à optimiser les performances maintenant
- ❌ Réfléchir à comment implémenter le cache
- ❌ Examiner le code d'authentification pour voir où optimiser
- ❌ Proposer des solutions d'optimisation
- ❌ Modifier quoi que ce soit lié aux performances

**Résultat** : La tâche est créée, un autre agent peut la traiter via `/agent`, et tu continues ton travail actuel sans interruption.

## Cas d'Usage et Enchaînements

### `/task` seul
L'utilisateur tape `/task il faudrait optimiser les performances` :
- Création immédiate de la tâche (task-1)
- Confirmation minimale : `✅ Tâche ajoutée (task-1)`
- Reprise immédiate du travail précédent

### Multiples `/task`
L'utilisateur tape `/task optimiser les performances /task améliorer le cache` :
- Création de task-1 (optimiser les performances)
- Confirmation : `✅ Tâche ajoutée (task-1)`
- Création de task-2 (améliorer le cache)
- Confirmation : `✅ Tâche ajoutée (task-2)`
- Reprise du travail précédent

### Pendant une autre commande
L'utilisateur tape `/agent /task optimiser les performances` :
- L'agent suspend l'exécution de `/agent`
- Création de la tâche (task-1)
- Confirmation : `✅ Tâche ajoutée (task-1)`
- Reprise de `/agent` là où l'agent s'était arrêté

## Notes Importantes

- **Pas d'interruption** : Cette commande ne doit jamais interrompre le flux de travail
- **Délégation** : La tâche est créée pour être traitée par un autre agent (via `/agent`)
- **Jamais d'implémentation immédiate** : Aucune action d'implémentation ni de planification ne doit suivre la création de la tâche
- **Ne jamais effectuer la modification demandée** : L'utilisateur demande une modification, mais tu ne dois QUE créer une tâche, PAS l'implémenter. L'implémentation sera faite plus tard par un autre agent.
- **Ne jamais planifier l'implémentation** : Même si tu sais comment faire, tu ne dois pas planifier. La planification appartient à l'agent qui traitera la tâche via `/agent`.
- **Ne jamais modifier le code** : Même si la modification semble simple, tu ne dois rien changer. Crée juste la tâche.
- **Contexte préservé** : Les fichiers de ton travail actuel sont mentionnés dans la section "Fichiers Concernés"
- **Format cohérent** : Suivre exactement le même format que les autres fichiers de tâches
- **Français** : Tout le contenu doit être en français
- **Fail-Fast** : Échouer explicitement si quelque chose est invalide, mais reprendre le travail après
- **Graphe connecté** : Aucune tâche ne doit être isolée dans le graphe de dépendances. Toutes les tâches doivent avoir au moins un lien (dépendance entrante ou sortante) avec le reste du graphe

## Intégration avec agent.mdc

Cette commande utilise les mêmes règles que `.cursor/rules/agent.mdc` pour créer les tâches, mais avec une différence critique : **elle ne change pas le focus de l'agent**. L'agent continue son travail après avoir créé la tâche.
