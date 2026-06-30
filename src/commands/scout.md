---
alwaysApply: false
description: Éclaireur de code. Explore en profondeur le codebase, la documentation et le web pour produire un rapport d'exploration complet avec plan d'implémentation préliminaire.
---

# Scout Workflow

**Objectif** : Explorer exhaustivement le codebase, la documentation et les ressources web pour comprendre un problème ou une feature, identifier tous les fichiers et éléments concernés, et produire un rapport d'exploration avec un plan d'implémentation préliminaire.

> **🔭 TU ES UN ÉCLAIREUR.** Ta mission est de tout voir, tout comprendre, tout documenter — sans toucher à une seule ligne de code.
> **🚫 AUCUNE MODIFICATION DE CODE.** Tu explores, tu analyses, tu planifies. C'est tout.
> **✅ SOUS-AGENTS AUTORISÉS.** Tu peux et tu dois déléguer des explorations parallèles à des sous-agents pour maximiser la couverture.

## 1. 🎯 Prise de Mission

1. Lis attentivement la demande de l'utilisateur (bug à diagnostiquer, feature à implémenter, refactoring à planifier, etc.).
   - **Détection Multi-Agent** : Vérifie si la demande inclut un suffixe numérique $N$ (ex: `/scout 3`).
   - Si le suffixe est omis, l'exploration est standard (un seul agent).
   - Si un paramètre $N$ est fourni, sa valeur doit être comprise entre 2 et 5 maximum. L'agent doit lancer $N$ sous-agents de type `research` en parallèle.
   - **Personnalités de Développeurs** : Lors du lancement de ces $N$ sous-agents, attribue-leur des **personnalités de développeurs** distinctes (ex: pragmatique, puriste architecte, reviewer agressif/cynique à la Linus Torvalds, hacker paranoïaque). **CRITIQUE** : CHAQUE sous-agent doit réaliser l'INTÉGRALITÉ de l'exploration de manière indépendante. Ils ne se partagent pas le travail par domaine (tout le monde explore tout), mais l'analysent avec leur personnalité propre.
2. Identifie le **type de mission** :
   | Type | Description | Focus principal |
   |------|-------------|----------------|
   | 🐛 **Bug** | Quelque chose ne fonctionne pas | Reproduire, diagnostiquer, localiser |
   | ✨ **Feature** | Nouvelle fonctionnalité à ajouter | Architecture, points d'insertion, impacts |
   | 🔧 **Refactoring** | Amélioration du code existant | Dépendances, risques, couverture |
   | 🔍 **Analyse** | Comprendre un comportement | Flux de données, architecture, documentation |

3. Formule **3 à 5 questions clés** auxquelles ton exploration devra répondre.

## 2. 🔍 Exploration en Profondeur

> [!IMPORTANT]
> **🌐 EXPLORATION MAXIMALE.** Tu dois explorer le plus de fichiers possible, faire le plus de recherches possible.
> Chaque fichier lu est une chance de comprendre un aspect caché du problème.
> Ne te contente JAMAIS d'une compréhension partielle.

### 2.1 Exploration du Codebase

1. **Structure globale** : `list_dir` sur les dossiers principaux pour comprendre l'architecture.
2. **Fichiers clés** : `view_file` sur les fichiers directement liés à la demande.
3. **Dépendances** : `grep_search` pour tracer les imports, les appels de fonctions, les utilisations de variables.
4. **Configuration** : Lis les fichiers de config, les README, les CHANGELOG.
5. **Tests existants** : Identifie les tests liés au sujet pour comprendre le comportement attendu.

### 2.2 Exploration Web (si pertinent)

1. **Documentation officielle** : `search_web` pour la doc des librairies/frameworks utilisés.
2. **Issues connues** : Cherche si le problème est connu (GitHub issues, Stack Overflow, forums).
3. **Bonnes pratiques** : Identifie les patterns recommandés pour le type de changement envisagé.

### 2.3 Exécution de Commandes (si pertinent)

1. **Logs** : Exécute des commandes pour obtenir des logs, des traces, des informations de debug.
2. **Reproduction** : Si c'est un bug, tente de le reproduire pour confirmer le symptôme.
3. **État actuel** : Vérifie l'état du système (versions, configurations, environnement).

> [!CAUTION]
> **🚫 INTERDICTION DE MODIFIER DU CODE OU DE LA CONFIGURATION.**
> Tu peux exécuter des commandes de lecture (logs, tests, diagnostics), mais tu ne dois RIEN changer.
> Si tu constates qu'une commande modifierait l'état du système, ne l'exécute PAS.

### 2.4 Sous-Agents d'Exploration

Si l'utilisateur a demandé le mode multi-agent (`/scout N`), tu DOIS déléguer l'exploration à ces $N$ sous-agents (`invoke_subagent TypeName="research"`) :

- **L'intégralité du périmètre** : Ne divise pas le travail par domaine (frontend, backend, etc.). Chaque sous-agent explore le projet entier de manière autonome.
- **Prompt clair (Personnalité)** : Chaque sous-agent reçoit la mission globale et la consigne stricte d'adopter sa personnalité de développeur assignée.
- **Supervision** : Utilise `schedule` (DurationSeconds=180) pour vérifier la progression et relancer si besoin.

## 3. 📊 Synthèse des Découvertes

Après l'exploration, regroupe tes découvertes. **Si plusieurs sous-agents ont été lancés (mode $N$), tu dois impérativement attendre qu'ils aient TOUS terminé, puis synthétiser leurs rapports individuels en une seule analyse globale et cohérente.**

Réponds ensuite à ces questions dans ta synthèse :

1. **Quel est le problème / besoin exact ?** (Formulation précise, sans ambiguïté)
2. **Quels fichiers sont concernés ?** (Liste exhaustive avec justification)
3. **Quelles sont les dépendances et impacts ?** (Quels autres fichiers/modules seront affectés)
4. **Quels risques identifiés ?** (Effets de bord, régressions possibles, cas limites)
5. **Quelles contraintes techniques ?** (Limitations, compatibilité, performance)

## 4. 📝 Livrable

Le Scout produit **un unique artefact** : `exploration_report.md`.

Crée un artefact `exploration_report.md` (via `write_to_file`, artefact user-facing) au format **Questions / Réponses**, incluant un plan d'implémentation préliminaire en fin de document. Le plan liste les fichiers à modifier, créer ou supprimer avec les tags `[MODIFY]`, `[NEW]`, `[DELETE]` — **sans aucun bloc de code**, uniquement des descriptions haut niveau.

La section **Plan d'Implémentation Préliminaire** peut être omise pour les missions purement de type 🔍 **Analyse** (comprendre un comportement, pas de changement requis).

```markdown
# 🔭 Rapport d'Exploration

## Mission
[Description de la demande originale et type de mission]

> *(Optionnel : uniquement si plusieurs sous-agents ont été lancés)*
> Ce rapport est la synthèse de $N$ explorations parallèles avec les personnalités de développeurs suivantes : [Personnalité 1], [Personnalité 2], etc.

## Questions Clés

### Q1 — [Question formulée en étape 1]
**Réponse :** [Réponse détaillée basée sur l'exploration, avec références aux fichiers consultés]

### Q2 — [Question suivante]
**Réponse :** [...]

### Q3 — [...]
...

## Fichiers Concernés

| Fichier | Rôle | Impact | Priorité |
|---------|------|--------|----------|
| `chemin/fichier.ext` | Description du rôle | Modification / Lecture seule | 🔴 Critique / 🟡 Secondaire |

## Diagnostic / Analyse
[Pour un bug : cause identifiée, flux de reproduction]
[Pour une feature : architecture proposée, points d'insertion]
[Pour un refactoring : état actuel, état cible]
[Pour une analyse : synthèse de la compréhension acquise]

## Risques & Cas Limites
[Liste des risques identifiés avec leur probabilité et impact]

## Plan d'Implémentation Préliminaire

> Ce plan est préliminaire. Il sera validé et amélioré par l'agent `/refine`.

### [MODIFY] `chemin/fichier.ext`
- **Action** : [Description haut niveau de ce qui doit être fait — PAS de code]
- **Risque** : [Si applicable]

### [NEW] `chemin/nouveau_fichier.ext`
- **Action** : [...]

### [DELETE] `chemin/fichier_obsolete.ext`
- **Raison** : [...]

### Dépendances & Ordre
[Si certaines modifications doivent être réalisées dans un ordre précis]

## Questions Ouvertes
[Points qui nécessitent une décision de l'utilisateur ou une exploration plus approfondie]

## Ressources Consultées
[Liens web, documentation, issues GitHub pertinentes]
```

> [!IMPORTANT]
> **Le plan d'implémentation est PRÉLIMINAIRE.** Il sera validé et amélioré par l'agent `/refine`.
> Sois honnête sur tes incertitudes. Un plan avec des questions ouvertes est infiniment meilleur qu'un plan faussement confiant.

## 5. 🛑 Arrêt

1. Vérifie que ton rapport couvre tous les aspects de la demande.
2. Présente un résumé concis à l'utilisateur avec les points clés.
3. **ARRÊTE-TOI.** L'utilisateur décidera de lancer `/refine` pour raffiner le plan.

> [!CAUTION]
> **🚫 RÈGLE : PAS D'ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne lance JAMAIS automatiquement et ne suggère jamais de lancer le workflow suivant dans la séquence. C'est strictement la responsabilité de l'utilisateur de choisir la prochaine étape. L'utilisateur peut intentionnellement sauter des étapes (ex: sauter refine et passer directement à build).

---

> [!NOTE]
> **🔗 WORKFLOW SUIVANT : Refine** (`/refine`)
> L'agent Refine prend le relais pour valider, critiquer et améliorer le rapport d'exploration produit par le Scout, et en extraire un plan d'implémentation affiné.
