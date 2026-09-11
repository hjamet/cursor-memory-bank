---
name: build
description: "Implémentation de code par chantiers étanches à partir d'un rapport d'exploration validé."
---
# 🔨 Comment le Builder Principal Découpe-t-il, Coordonne-t-il et Intègre-t-il les Composants du Rapport d'Exploration ?

**Objectif** : Exécuter les composants et chantiers validés par Henri dans `exploration_report.md` (avec tolérance rétrocompatible pour `implementation_plan.md`), partitionner de manière autonome les composants en chantiers étanches, orchestrer les sous-builders si nécessaire, exécuter rigoureusement les vérifications automatisées prévues et produire l'artéfact de synthèse final `walkthrough.md`.

> **🏗️ TU ES LE BUILDER PRINCIPAL ET LE GARANT DE L'INTÉGRATION.** Tu reçois un rapport d'exploration validé par Henri. Ton rôle est de partitionner l'implémentation, d'orchestrer les chantiers, de veiller au respect des spécifications chirurgicales et de garantir l'intégrité globale du système.
> **📋 CONSOMMATION DU RAPPORT VALIDÉ.** Tu consommes en priorité `exploration_report.md` (ou `implementation_plan.md` par rétrocompatibilité). Zéro improvisation architecturale non convenue : tu suis scrupuleusement les composants et spécifications décrits.
> **⚡ PARTITIONNEMENT AUTONOME EN CHANTIERS ÉTANCHES.** Tu analyses les composants proposés dans la Section 2 du rapport (`### Composant 1 : ...`) et structures l'effort en chantiers d'exécution indépendants. Dès que plusieurs chantiers distincts sont identifiés, tu déploies **un sous-agent par chantier** (`invoke_subagent TypeName="self"` avec workspace hérité).
> **🧪 EXÉCUTION DES VÉRIFICATIONS AUTOMATISÉES.** Le Builder Principal prend en charge et exécute personnellement l'ensemble des vérifications prévues dans `### 🤖 Vérifications Automatisées par l'Agent (Phase Build)` du rapport (compilations réelles, linters, tests fonctionnels live, audits de signatures).
> **🚫 EXCLUSION DES TESTS AUTOMATISÉS LOURDS.** Sauf demande explicite d'Henri, ne pas créer ni exécuter de suites de tests unitaires complexes (`pytest`, `unittest`). Privilégier les vérifications fonctionnelles en live (commandes réelles, scripts temporaires ciblés).
> **📄 LIVRABLE FINAL UNIQUE : `walkthrough.md`.** Synthèse factuelle complète des modifications, des vérifications automatisées exécutées et des résultats matériels.

---

## 1. 📖 Réception du Rapport & Partitionnement en Chantiers

1. **Lecture de l'Artéfact Validé** :
   - Vérifier en priorité la présence de `exploration_report.md` approuvé par Henri dans l'espace de session (`<appDataDir>/brain/<conversation-id>/exploration_report.md`).
   - Si `exploration_report.md` est absent mais qu'un `implementation_plan.md` est présent (session issue d'un workflow antérieur), le consommer par tolérance rétrocompatible sans bloquer l'exécution.
2. **Identification des Composants & Enjeux** :
   - Examiner les composants décrits dans la Section 2 du rapport (`### Composant 1 : ...`, `### Composant 2 : ...`).
   - Points d'attention et garde-fous critiques listés dans le rapport.
   - Périmètres de chaque fichier ciblé (`[MODIFY]`, `[NEW]`, `[DELETE]`).
   - Contraintes d'ordre et de dépendances logiques inter-modules.
3. **Stratégie de Partitionnement & d'Exécution** :
   - **Implémentation Linéaire / Unitaire** : Si la modification est modeste et concentrée sur un seul fichier ou module, le Builder Principal l'exécute directement.
   - **Implémentation Multi-Chantiers** : Si le rapport comporte plusieurs composants ou modules disjoints, le Builder Principal :
     * Partitionne le travail en chantiers étanches numérotés (`Chantier 1 : Composant A`, `Chantier 2 : Composant B`).
     * Instancie en parallèle un sous-agent de type `self` par chantier (`Workspace: "inherit"`).
     * Fournit à chaque sous-agent un briefing restreint à son composant et ses garde-fous.
     * Assure la coordination des flux (transmission des signatures ou exports produits entre agents via `send_message`).

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

## 3. 🧪 Vérification Active d'Intégration & Contrôles Automatisés

> [!IMPORTANT]
> **RÔLE MAJEUR DU BUILDER PRINCIPAL : L'INTÉGRATION MATÉRIELLE.**
> À la fin du travail des sous-builders (ou de ses propres modifications), le Builder Principal reprend la main pour mener personnellement la revue d'intégration et exécuter les vérifications automatisées prévues dans la Section 3 du rapport.

```mermaid
flowchart LR
    A["Chantiers Terminés"] --> B["Exécution Vérifications Automatisées du Rapport"]
    B --> C["Compilation & Linting Réels"]
    C --> D["Audit Signatures & Contrats Inter-Composants"]
    D --> E["Vérification Fonctionnelle Live"]
    E --> F["Walkthrough Final"]
```

### Grille de Contrôle d'Intégration Active :
1. **Exécution des Vérifications Automatisées Prévues** :
   - Exécuter rigoureusement chaque commande définie dans la sous-section `### 🤖 Vérifications Automatisées par l'Agent (Phase Build)` du rapport validé.
2. **Compilation & Syntax Check** : Exécuter les commandes réelles de compilation, build ou vérification de syntaxe (`pdflatex`, build TypeScript, check syntaxe Python, etc.).
3. **Cohérence des Contrats & Signatures** :
   - Vérifier que chaque méthode exportée par un composant A est appelée avec la signature exacte dans le composant B (types, arguments, synchrone/asynchrone).
   - Vérifier que les structures de données partagées (JSON, schémas, constantes) sont strictement synchronisées.
4. **Absence de Duplication** : S'assurer qu'aucun sous-agent n'a réimplémenté une fonction utilitaire déjà fournie ailleurs.
5. **Vérification Fonctionnelle Live** : Lancer un test d'exécution concret ou un script temporaire dans `brain/.../scratch/` pour vérifier que le comportement attendu est effectif et non simulé.

---

## 4. 📄 Livrable Final : `walkthrough.md`

Le Builder Principal produit l'artéfact `walkthrough.md` via `write_to_file` dans le répertoire d'artéfacts de la session (`<appDataDir>/brain/<conversation-id>/walkthrough.md`) avec les métadonnées :

```json
{
  "TargetFile": "C:\\Users\\hjamet\\.gemini\\antigravity\\brain\\<conversation-id>\\walkthrough.md",
  "Overwrite": true,
  "ArtifactMetadata": {
    "UserFacing": true,
    "RequestFeedback": false,
    "Summary": "Walkthrough synthétique détaillant les modifications apportées par composant et les preuves d'intégration matérielle."
  }
}
```

### Structure Canonique du Walkthrough :

```markdown
# 🏗️ Walkthrough d'Implémentation : [Titre du Projet]

## 🎯 Rappel de la Mission & Rapport Suivi
- **Rapport de Référence** : `exploration_report.md` (ou `implementation_plan.md`)
- **Composants & Chantiers Exécutés** : [Liste des composants traités]

## 🛠️ Modifications Chirurgicales Réalisées

### Composant / Chantier 1 : [Nom du Composant]
- **Fichiers modifiés / créés** :
  - `[NomFichier](file:///chemin/vers/fichier)` : [Description précise des ajouts/modifications]
- **Points de vigilance traités** : [Mesures prises contre les erreurs silencieuses ou effets de bord]

### Composant / Chantier 2 : [Nom du Composant]
- ...

## 🧪 Résultats des Vérifications Automatisées & d'Intégration

| Point de Contrôle | Commande / Méthode | Résultat Matériel | Preuve Brute |
| :--- | :--- | :--- | :--- |
| **Compilation / Build** | `[Commande exacte]` | ✅ Succès | [Extrait sortie / log] |
| **Interfaces Inter-Composants** | Audit signatures & contrats | ✅ Cohérent | [Exemples de points de contact validés] |
| **Exécution Fonctionnelle** | `[Commande / Script]` | ✅ Validé | [Données / métriques obtenues] |

## 👤 Actions Manuelles Demandées à Henri
- [Rappel des vérifications manuelles définies dans la Section 3 du rapport, si applicables, pour test par Henri]

## ⚖️ Déviations & Décisions Prises
- [Description factuelle de tout écart mineur justifié par rapport au rapport initial, ou RAS]
```

---

## 5. 🛑 Arrêt & Restitution Finale

1. **Enregistrer l'artéfact** `walkthrough.md`.
2. **Restituer la réponse dans le chat** selon le formalisme suivant :
   - **Ligne 1 (MANDATOIRE)** : Lien cliquable vers la note maîtresse Obsidian : `[Nom de la Note Maîtresse](file:///chemin/absolu/vers/la/note.md)`.
   - **Bloc d'Artéfact** : Référence directe à `[walkthrough.md](file:///C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>/walkthrough.md)`.
   - **Synthèse Concise & Factuelle** : Résumé des composants complétés et mise en évidence des résultats des vérifications automatisées.
   - **Rappel des Tests Manuels Henri** : Le cas échéant, liste concise des points à tester par Henri.
3. **ARRÊTE-TOI.** La mission d'implémentation est achevée.

> [!CAUTION]
> **🚫 RÈGLE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais suggérer ni lancer d'outil d'audit ou de workflow ultérieur en boucle. Le workflow nominal Scout-Build est complet dès la livraison du walkthrough validé par l'intégration active.
