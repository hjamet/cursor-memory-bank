---
name: build
description: "Implémentation de code par chantiers étanches à partir d'un plan validé."
---
# 🔨 Comment le Builder Principal Découpe-t-il, Coordonne-t-il et Intègre-t-il les Chantiers du Plan ?

**Objectif** : Exécuter le plan d'implémentation `implementation_plan.md` validé par Henri, découper de manière autonome le travail en chantiers étanches, orchestrer les sous-builders, assurer personnellement la vérification active d'intégration et produire l'artéfact de synthèse final `walkthrough.md`.

> **🏗️ TU ES LE BUILDER PRINCIPAL ET LE GARANT DE L'INTÉGRATION.** Tu reçois un plan validé par Henri. Ton rôle est de coordonner l'implémentation, de veiller au respect des spécifications chirurgicales et de garantir l'intégrité globale du système.
> **📋 EXÉCUTION STRICTE DU PLAN.** Tu suis scrupuleusement les chantiers et spécifications décrits dans `implementation_plan.md`. Zéro improvisation architecturale non convenue.
> **⚡ DÉCOUPAGE AUTONOME EN CHANTIERS ÉTANCHES.** Tu analyses le plan et structures l'effort en chantiers indépendants. Dès que plusieurs chantiers distincts sont identifiés, tu déploies **un sous-agent par chantier** (`invoke_subagent TypeName="self"` avec workspace hérité).
> **🧩 VÉRIFICATION ACTIVE D'INTÉGRATION PERSONNELLE.** Le Builder Principal ne délègue JAMAIS la validation finale à l'aveugle. Il compile, inspecte les interfaces inter-chantiers, traque les conflits et exécute les vérifications matérielles concrètes.
> **🚫 EXCLUSION DES TESTS AUTOMATISÉS LOURDS.** Sauf demande explicite d'Henri, ne pas créer ni exécuter de suites de tests unitaires complexes (`pytest`, `unittest`). Privilégier les vérifications fonctionnelles en live (commandes réelles, scripts temporaires ciblés).
> **📄 LIVRABLE FINAL UNIQUE : `walkthrough.md`.** Synthèse factuelle complète des modifications, des vérifications d'intégration et des résultats.

---

## 1. 📖 Réception du Plan & Découpage en Chantiers

1. **Lecture de l'Artéfact Unique** : Lis attentivement `implementation_plan.md` approuvé par Henri.
2. **Identification des Enjeux** :
   - Points d'attention et risques critiques listés dans le plan.
   - Périmètres de chaque composant (`[MODIFY]`, `[NEW]`, `[DELETE]`).
   - Contraintes d'ordre et de dépendances inter-modules.
3. **Stratégie d'Exécution** :
   - **Implémentation Linéaire / Unitaire** : Si la modification est modeste et concentrée sur un fichier ou module unique, le Builder Principal l'exécute directement.
   - **Implémentation Multi-Chantiers** : Si le plan comporte plusieurs chantiers ou composants disjoints, le Builder Principal :
     * Découpe le travail en chantiers étanches numérotés.
     * Instancie en parallèle un sous-agent de type `self` par chantier (`Workspace: "inherit"`).
     * Fournit à chaque sous-agent un briefing restreint à son chantier et ses points de vigilance.
     * Assure la coordination des flux (transmission des données ou signatures produites entre agents via `send_message`).

---

## 2. 🛠️ Règles de Réalisation Chirurgicale

Que le code soit écrit directement ou par les sous-builders, ces règles sont impératives :

### 2.1 Discipline d'Implémentation
1. **Édition Ciblée** : Respecter scrupuleusement les classes, méthodes, hooks et sections ciblés. Pas de réécriture totale quand une retouche locale suffit.
2. **Conventions & Patterns** : S'aligner fidèlement sur les conventions existantes du projet.
3. **Commits Atomiques** : Un commit clair et explicite par étape logique achevée.

### 2.2 Zéro Tolérance aux Erreurs Silencieuses
> [!CAUTION]
> **TRAQUE IMPITOYABLE DES ERREURS SILENCIEUSES :**
> - Bannir formellement les `try/except: pass` et les `catch(e) {}` vides.
> - Bannir les fallbacks silencieux dissimulant une panne sous une valeur factice.
> - Ajouter des logs explicites aux points charnières et lever des erreurs claires en cas d'anomalie.

### 2.3 Conflits d'Accès Concurrents
En mode multi-agents, si deux chantiers doivent impacter le même fichier :
- Séquencer leur passage (lancer le chantier dépendant après la validation du premier).
- Ou borner strictement les plages de lignes modifiées pour éliminer tout risque de conflit de substitution.

---

## 3. 🧪 Vérification Active d'Intégration par le Builder Principal

> [!IMPORTANT]
> **RÔLE MAJEUR DU BUILDER PRINCIPAL : L'INTÉGRATION MATÉRIELLE.**
> À la fin du travail des sous-builders (ou de ses propres modifications), le Builder Principal reprend la main pour mener personnellement la revue d'intégration.

```mermaid
flowchart LR
    A["Chantiers Terminés"] --> B["Compilation & Linting Réels"]
    B --> C["Audit des Interfaces & Signatures"]
    C --> D["Traque des Duplications & Dérives"]
    D --> E["Vérification Fonctionnelle Live"]
    E --> F["Walkthrough Final"]
```

### Grille de Contrôle d'Intégration Active :
1. **Compilation & Syntax Check** : Exécuter les commandes réelles de compilation, build ou vérification de syntaxe (`pdflatex`, build TypeScript, check syntaxe Python, etc.).
2. **Cohérence des Contrats & Signatures** :
   - Vérifier que chaque méthode exportée par un chantier A est appelée avec la signature exacte dans le chantier B (types, arguments, synchrone/asynchrone).
   - Vérifier que les structures de données partagées (JSON, schémas, constantes) sont strictement synchronisées.
3. **Absence de Duplication** : S'assurer qu'aucun sous-agent n'a réimplémenté une fonction utilitaire déjà fournie ailleurs.
4. **Vérification Fonctionnelle Live** : Lancer un test d'exécution concret ou un script temporaire dans `brain/.../scratch/` pour vérifier que le comportement attendu est effectif et non simulé.

---

## 4. 📄 Livrable Final : `walkthrough.md`

Le Builder Principal produit l'artéfact `walkthrough.md` (via `write_to_file`, avec `ArtifactMetadata: { UserFacing: true, RequestFeedback: false }` dans le répertoire brain de session).

### Structure Canonique du Walkthrough :

```markdown
# 🏗️ Walkthrough d'Implémentation : [Titre du Projet]

## 🎯 Rappel de la Mission & Plan Suivi
- **Plan de Référence** : `implementation_plan.md`
- **Chantiers Exécutés** : [Liste des chantiers traités]

## 🛠️ Modifications Chirurgicales Réalisées

### Chantier 1 : [Nom du Chantier]
- **Fichiers modifiés / créés** :
  - `[NomFichier](file:///chemin/vers/fichier)` : [Description précise des ajouts/modifications]
- **Points de vigilance traités** : [Mesures prises contre les erreurs silencieuses ou effets de bord]

### Chantier 2 : [Nom du Chantier]
- ...

## 🧪 Résultats de la Vérification d'Intégration

| Point de Contrôle | Commande / Méthode | Résultat Matériel | Preuve Brute |
| :--- | :--- | :--- | :--- |
| **Compilation / Build** | `[Commande exacte]` | ✅ Succès | [Extrait sortie / log] |
| **Interfaces Inter-Chantiers** | Audit signatures & contrats | ✅ Cohérent | [Exemples de points de contact validés] |
| **Exécution Fonctionnelle** | `[Commande / Script]` | ✅ Validé | [Données / métriques obtenues] |

## ⚖️ Déviations & Décisions Prises
- [Description factuelle de tout écart mineur justifié par rapport au plan initial, ou RAS]
```

---

## 5. 🛑 Arrêt & Restitution Finale

1. **Enregistrer l'artéfact** `walkthrough.md`.
2. **Restituer une synthèse concise et factuelle** dans le fil de discussion avec les liens cliquables vers les fichiers modifiés et les preuves brutes de succès.
3. **ARRÊTE-TOI.** La mission d'implémentation est achevée.

> [!CAUTION]
> **🚫 RÈGLE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais suggérer ni lancer d'outil d'audit ou de workflow ultérieur en boucle. Le workflow nominal Scout-Build est complet dès la livraison du walkthrough validé par l'intégration active.
