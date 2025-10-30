# Commande Task — Ajout de Tâche à la Roadmap 📝

## Objectif

Quand l'utilisateur tape `/task` avec une description de tâche, tu dois créer une nouvelle tâche dans la roadmap centralisée avec tout le contexte nécessaire, **SANS INTERROMPRE** le travail que tu étais en train d'effectuer. Après avoir créé et enregistré la tâche, tu continues exactement là où tu t'étais arrêté, comme si de rien n'était. 

**INTERDICTION ABSOLUE**: Tu ne dois JAMAIS commencer à implémenter ou planifier l'implémentation de la tâche nouvellement créée. La planification/implémentation appartiennent exclusivement à `/agent` après discussion avec l'utilisateur.

## Principe Fondamental

**CRITIQUE** : Cette commande est une **interruption non-bloquante**. Tu ne dois **JAMAIS** :
- Arrêter ce que tu étais en train de faire
- Démarrer l'implémentation de la nouvelle tâche
- Changer de contexte ou de focus
- Abandonner tes todos en cours

Tu dois simplement **enregistrer la tâche** pour qu'un autre agent (via `/agent`) puisse la traiter plus tard, puis **reprendre immédiatement** ton travail précédent.

### Interdictions absolues (rappel)
- Ne pas créer de plan de transition pour cette nouvelle tâche
- Ne pas modifier, refactorer ou amorcer un correctif relatif à la nouvelle tâche
- Ne pas changer de contexte, d'onglet ou de fichier hors de ton travail en cours

## Comportement Requis

Lorsque l'utilisateur tape `/task [description de la tâche]`, tu dois :

### Étape 1 : Analyser la Demande

1. **Extraire la description** de la tâche fournie par l'utilisateur
2. **Identifier le contexte** de ton travail actuel pour comprendre pourquoi cette tâche est mentionnée
3. **Déterminer les métadonnées** :
   - Titre descriptif et actionnable
   - **IMPORTANT** : Vérifier que le titre est unique dans la roadmap pour éviter les collisions de noms de fichiers
   - Priorité (1-5, 3 par défaut)
   - Dépendances éventuelles (si le travail actuel doit être terminé d'abord)

### Étape 2 : Générer le Nom de Fichier

1. Convertir le titre en format kebab-case
2. **IMPORTANT** : Vérifier que le titre est unique dans la roadmap pour éviter les collisions
3. Nom du fichier de tâche : `{titre-kebab-case}.md`
4. Nom du fichier de résultat : `rapport-{titre-kebab-case}.md`

### Étape 3 : Créer le Fichier de Tâche

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

### Étape 4 : Ajouter à la Roadmap

1. **Lire** `.cursor/agents/roadmap.yaml`
2. **Générer un ID unique** : Identifier le plus grand ID existant et incrémenter (ex: `task-1`, `task-2`, etc.)
3. **Ajouter l'entrée** dans la liste `tasks` :

```yaml
- id: "task-{unique-id}"
  title: "Titre descriptif de la tâche"
  priority: 3  # 1-5, ajuster selon l'importance
  dependencies: []  # Liste d'IDs de tâches ou []
  task_file: "{nom-fichier-tache}.md"
  output_file: "rapport-{nom-fichier-tache}.md"
  deadline: null  # Optionnel
```

4. **Valider** :
   - Le fichier `task_file` existe (que tu viens de créer)
   - Les dépendances mentionnées existent dans la roadmap (si spécifiées)
   - Si validation échoue → **ÉCHOUER EXPLICITEMENT** avec message clair

5. **Sauvegarder** le fichier `roadmap.yaml`

### Étape 5 : Confirmation et Reprise

**CRITIQUE** : Après avoir créé la tâche, tu dois :

1. **Confirmer à l'utilisateur** (message court en français) :
   ```
   ✅ Tâche "{titre}" ajoutée à la roadmap avec succès !
   📋 ID: task-{id}
   📁 Fichier: {nom-fichier-tache}.md
   ```

2. **Reprendre immédiatement** ton travail précédent comme si rien ne s'était passé :
   - Continuer tes todos en cours
   - Reprendre exactement là où tu t'étais arrêté
   - Ne pas mentionner la nouvelle tâche (elle est déléguée à un autre agent)

## Format de Réponse Minimal

Après avoir créé la tâche, répondre uniquement :

```
✅ Tâche "{titre}" ajoutée à la roadmap (ID: task-{id})

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
2. ✅ Créer le fichier `optimiser-performances-auth.md` avec les 4 sections (vérifier l'unicité du titre)
3. ✅ Ajouter l'entrée dans `roadmap.yaml` avec ID `task-1`
4. ✅ Confirmer : "✅ Tâche 'Optimiser les performances d'authentification' ajoutée à la roadmap (ID: task-1)"
5. ✅ Reprendre immédiatement l'implémentation de l'authentification

**Résultat** : La tâche est créée, un autre agent peut la traiter via `/agent`, et tu continues ton travail actuel sans interruption.

## Notes Importantes

- **Pas d'interruption** : Cette commande ne doit jamais interrompre le flux de travail
- **Délégation** : La tâche est créée pour être traitée par un autre agent (via `/agent`)
- **Jamais d'implémentation immédiate** : Aucune action d'implémentation ni de planification ne doit suivre la création de la tâche
- **Contexte préservé** : Les fichiers de ton travail actuel sont mentionnés dans la section "Fichiers Concernés"
- **Format cohérent** : Suivre exactement le même format que les autres fichiers de tâches
- **Français** : Tout le contenu doit être en français
- **Fail-Fast** : Échouer explicitement si quelque chose est invalide, mais reprendre le travail après

## Intégration avec agent.mdc

Cette commande utilise les mêmes règles que `.cursor/rules/agent.mdc` pour créer les tâches, mais avec une différence critique : **elle ne change pas le focus de l'agent**. L'agent continue son travail après avoir créé la tâche.

