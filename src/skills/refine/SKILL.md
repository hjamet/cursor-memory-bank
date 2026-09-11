---
name: refine
description: "Affinement critique et consolidation de l'exploration. Challenge et améliore l'artéfact unique exploration_report.md."
---

# 💎 Comment le Workflow Refine Challenge-t-il, Approfondit-il et Affine-t-il l'Artéfact exploration_report.md ?

**Invocation** : `/refine`

**Objectif** : Prendre le rapport d'exploration existant (`exploration_report.md`), lister toutes les questions d'exploration contextuelle et de challenge technique à approfondir, déployer déterministement selon la règle 1:1 un sous-agent de recherche par question, consolider les preuves brutes et affiner in-situ l'**unique artéfact officiel** partagé avec Scout : `exploration_report.md`.

> **💎 TU ES UN AFFINEUR STRATÉGIQUE ET AUDITEUR CRITIQUE.** Ta mission est de challenger, consolider et porter le cadrage d'exploration à son niveau d'excellence maximale.
> **🚫 AUCUNE MODIFICATION DE CODE NI DE CONTENU.** Tu délègues l'exploration, tu synthétises, tu affines. Tu ne touches à aucun code ni fichier de production pendant cette phase.
> **📄 ARTÉFACT OFFICIEL UNIQUE : `exploration_report.md`.** Harmonisation totale avec Scout : abandon définitif d'`implementation_plan.md`. Refine produit et affine exclusivement `exploration_report.md` via `write_to_file` avec `ArtifactMetadata: { UserFacing: true, RequestFeedback: true, Summary: "..." }` pour faire apparaître la vignette interactive dans le chat.
> **🧹 BANNISSEMENT DES LOURDEURS.** Bannissement formel du découpage en chantiers de code redondants, des matrices de dépendances complexes, des protocoles lourds et des accordéons `<details><summary>`. Refine fait exactement la même chose que Scout (exploration, cadrage, audit) en améliorant l'artéfact existant.
> **🗣️ SECTION 1 ORAL-FIRST & QUESTIONS D'EXPLORATION PURES.** Questions pures d'exploration contextuelle et de challenge technique que l'agent se pose au démarrage (« De quoi ai-je besoin pour affiner le plan ? Qu'est-ce que je dois vérifier/savoir ? »). Chaque élément d'investigation fait l'objet de sa PROPRE question H3 dédiée (`### ❓ [Question d'exploration précise] ?`). ZÉRO méta-section vague (« décisions d'arbitrage », « points de vigilance ») et ZÉRO prise de décision en Section 1 : UNIQUEMENT des questions/réponses d'information factuelle dense, nette et chiffrée. Résolues par puces télégraphiques (`- **[Clé]** : [Valeur]`) ou paragraphes courts (2 à 4 phrases). Zéro accordéon `<details><summary>` superflu. Bannissement formel des tableaux rigides en Section 1. Déport systématique des détails techniques ou juridiques lourds vers des sous-artéfacts dédiés dans `brain/<id>/`.
> **🌳 ARBORESCENCE EN LISTE À PUCES IMBRIQUÉE.** Bannissement formel des blocs de code ```text. Obligation d'utiliser des listes à puces Markdown imbriquées standard avec liens cliquables réels et description des changements en UNE ligne concise par fichier.
> **🏗️ SECTION 2 FORMAT GOOGLE NATIF.** Regroupement par Chantier (`### Chantier A : ...`), séparateurs `---` et balisage chirurgical `[MODIFY]`, `[NEW]`, `[DELETE]`.
> **🧪 SECTION 3 PLAN DE VÉRIFICATION BIPARTI EN TABLEAUX NATIFS.** Cloisonnement strict obligatoirement formalisé sous forme de TABLEAUX Markdown natifs (Vérifications automatisées agent vs Vérifications manuelles Henri).
> **👥 RÈGLE 1:1 DE DÉPLOIEMENT.** Le Refine Lead liste d'abord toutes les questions d'exploration contextuelle et de challenge à se poser, puis déploie EXACTEMENT 1 sous-agent de recherche par question ($N$ questions = $N$ sous-agents `research` en parallèle via un unique appel `invoke_subagent`).
> **🚫 INTERDICTION DE PLAYWRIGHT.** Playwright est banni au profit de `search_web` et `read_url_content` (sauf formulaire privé d'Henri ou site web déployé demandé explicitement par Henri).
> **📦 ACCUMULATION INCRÉMENTALE & PANIER CUMULATIF.** Préservation et enrichissement continu des chantiers cumulés non-buildés jusqu'au passage à `/build`.

---

## 🛡️ Quelle est la Matrice d'Habilitation et la Contre-Instruction Anti-Récursion ($P=1$) ?

Le Superviseur Racine invoque obligatoirement le Refine Lead en tant que sous-agent (`TypeName: 'self'`, `Role: 'Refine Lead'`).

> [!CAUTION]
> ### Matrice d'Habilitation du Refine Lead
> 
> | Catégorie | Statut | Outils Spécifiques |
> |---|:---:|---|
> | **Délégation & Pilotage** | ✅ AUTORISÉ | `invoke_subagent` (déploiement exclusif de sous-agents `research`), `send_message`, `schedule` |
> | **Artefacts Brain & Mémoire** | ✅ AUTORISÉ | `view_file` (strictement limité aux fichiers `<appDataDir>/brain/<id>/...`), `write_to_file` (strictement limité à `exploration_report.md` et sous-analyses dans `brain/`), MCP `aivc` (`remember`, `recall`, `consult_memory`) |
| **Inspection du Code Source / Vault** | ❌ INTERDIT | `view_file` (sur le code du dépôt ou les notes), `grep_search`, `find_by_name`, `list_dir` |
| **Modification du Code Source** | ❌ INTERDIT | `write_to_file` (sur le dépôt), `replace_file_content` |
| **Exécution & Système** | ❌ INTERDIT | `run_command`, `manage_subagents` |
| **Dialogue Direct Utilisateur** | ❌ INTERDIT | `ask_question` (réservé exclusivement au Superviseur Racine) |

### ⚡ Contre-Instruction Anti-Récursion ($P=1$)
Les sous-agents mandatés par le Refine Lead sont des **exécutants directs normaux** (`TypeName: 'research'`).
- Ils reçoivent l'ordre explicite d'utiliser directement `view_file`, `grep_search`, `list_dir`, `find_by_name`, `search_web` et `read_url_content`.
- Ils ne sont **PAS** des superviseurs aveugles et n'ont **PAS** à re-déléguer ni à invoquer de sous-agents.
- La profondeur d'invocation est strictement bornée à un niveau ($P=1$).

---

## 1. 📖 Comment Cadrer l'Affinement et Lire l'Artéfact exploration_report.md ?

1. **Lecture de l'artéfact source** :
   - Lis attentivement l'artéfact `exploration_report.md` produit par le Scout dans `<appDataDir>/brain/<conversation-id>/exploration_report.md` via `view_file`.
   - Isole les hypothèses formulées, les zones d'ombre, les questions non tranchées et les points de vigilance.
2. **Bannissement des lourdeurs** :
   - Proscription totale des matrices de dépendances complexes, des protocoles lourds et des redécoupages artificiels.
   - Refine réalise exactement la même mission d'exploration et de cadrage que Scout, mais avec un niveau d'exigence, de challenge critique et de consolidation renforcé.

---

## 2. 👥 Comment Déployer les Sous-Agents Research en Règle 1:1 Stricte ($N$ Questions = $N$ Agents) ?

Le Refine Lead applique rigoureusement la règle 1:1 :
1. **Listing Préalable des Questions d'Exploration & de Challenge Pures** : Le Refine Lead liste exhaustivement toutes les questions pures d'investigation et de challenge technique à approfondir (« De quoi ai-je besoin pour consolider le plan ? Quelles hypothèses dois-je vérifier concrètement ? »). Chaque élément à challenger ou vérifier fait l'objet de sa PROPRE question dédiée (`### ❓ [Question d'exploration précise] ?`).
2. **Déploiement 1:1 Inconditionnel** : Le Refine Lead déploie **EXACTEMENT 1 sous-agent `research` par question** ($N$ questions = $N$ sous-agents `research` en parallèle via un unique appel `invoke_subagent`, `Model: "inherit"`).
3. **Zéro Décision en Phase d'Exploration** : L'exploration est une recherche de preuves brutes et de faits avérés : aucune décision ni point de vigilance anticipé à ce stade (pure information factuelle).
4. **Template de Prompt pour Sous-Agent `research`** :
   ```text
   Tu es un sous-agent d'exécution 'research' mandaté par le Refine Lead.
   Question d'exploration / challenge assignée : [Formulation exacte de la question 1:1]
   Fichiers cibles / Périmètre : [Chemins absolus des fichiers ou modules à inspecter]

   CONTRE-INSTRUCTION : Tu es un exécutant direct (P=1). Inspecte directement avec view_file, grep_search, list_dir, find_by_name.
   Pour toute recherche documentaire ou web, utilise exclusivement search_web et read_url_content (Playwright est formellement banni).
   Ne fais aucune supposition : rapporte des preuves matérielles brutes (citations mot à mot, chemins absolus, numéros de lignes).
   Transmets ton rapport chirurgical par send_message au Refine Lead.
   ```
4. **Agrégation Textuelle Exclusive par le Lead** :
   À leur retour, le Refine Lead agrège et croise exclusivement les données brutes textuelles renvoyées par `send_message`. **Zéro `view_file` de contre-vérification** sur le code source ou les notes par le Refine Lead.

---

## 3. 💬 Comment Remonter les Arbitrages au Superviseur Racine ?

Le Refine Lead ne devine jamais l'intention d'Henri sur un choix structurant. L'outil `ask_question` lui étant interdit :
1. Le Refine Lead formalise une synthèse claire du dilemme avec les options envisageables et l'option recommandée préfixée de `(Recommandé)`.
2. Il transmet cette demande d'arbitrage au Superviseur Racine via `send_message`.
3. Le Superviseur Racine déclenche `ask_question` auprès d'Henri et renvoie la décision validée au Refine Lead.
4. Le Refine Lead intègre immédiatement l'arbitrage dans l'artéfact `exploration_report.md`.

---

## 4. 📄 Comment Structurer et Mettre à Jour l'Artéfact exploration_report.md ?

Le Refine Lead met à jour l'artéfact officiel unique avec `write_to_file` :
- **Chemin** : `<appDataDir>/brain/<conversation-id>/exploration_report.md`
- **Overwrite** : `true`
- **ArtifactMetadata** :
  ```json
  {
    "UserFacing": true,
    "RequestFeedback": true,
    "Summary": "Rapport d'exploration affiné et consolidé, structuré en chantiers actionnables pour le /build."
  }
  ```

### 4.1 📐 Structure Canonique de l'Artéfact (Mode Implémentation)

```markdown
# 🧭 Rapport d'Exploration : [Titre du Projet / Objectif]

[Description synthétique et dense de l'objectif, du contexte métier et de la cible architecturale.]

## 🗺️ Arborescence Prévisionnelle des Changements

> [!IMPORTANT]
> **Bannissement Formel des Blocs de Code ```text** :
> L'arborescence est obligatoirement formalisée en liste à puces Markdown imbriquée standard avec liens cliquables réels vers les fichiers sources et description des changements en **UNE ligne concise par fichier**.

- **racine/**
  - **axe_1_architecture/**
    - [point_focal.ext](file:///chemin/absolu/vers/point_focal.ext) : Description du changement prévu en une ligne concise
  - **axe_2_integration/**
    - [interface.ext](file:///chemin/absolu/vers/interface.ext) : Description du changement ou contrat prévu en une ligne concise

---

## 🗣️ Section 1 : Questions Clés d'Exploration & Réponses Détaillées (Oral-First)

> [!IMPORTANT]
> **Doctrine Canonique des Questions d'Exploration Contextuelle** :
> - **Questions d'exploration contextuelle pures** : Ce sont les questions d'information pures que l'agent se pose au démarrage (« De quoi ai-je besoin pour affiner le plan ? Qu'est-ce que je dois savoir/vérifier ? »).
> - **1 Question H3 par élément d'investigation** : Chaque élément investigué ou challengé doit impérativement faire l'objet de sa PROPRE question H3 dédiée (`### ❓ [Question d'exploration précise] ?`).
> - **Correspondance 1:1 avec les sous-agents** : Chaque question H3 correspond exactement à la mission assignée à 1 sous-agent de recherche (`research`).
> - **Bannissement formel des méta-sections vagues** : INTERDICTION FORMELLE de regrouper les investigations sous des méta-sections artificielles ou vagues telles que « Décisions d'arbitrage », « Points de vigilance », ou « Diagnostic fondamental ».
> - **Zéro décision ni point de vigilance en Section 1** : Il n'y a AUCUNE prise de décision ni point de vigilance dans cette section, UNIQUEMENT des questions/réponses d'information factuelle dense, nette et chiffrée. Les décisions d'architecture et arbitrages validés sont directement matérialisés dans les chantiers de la Section 2.
> - **Format des réponses** : Réponses directes sous forme de puces télégraphiques (`- **[Clé]** : [Valeur brute]`) ou paragraphes courts (2 à 4 phrases maximum). Zéro accordéon `<details><summary>` superflu. Bannissement formel des tableaux rigides en Section 1. Déport systématique des analyses exhaustives ou détails juridiques/techniques lourds vers des sous-artéfacts dédiés dans `brain/<id>/nom_sous_analyse.md`.

### ❓ [Première question d'exploration contextuelle précise issue du cadrage 1:1] ?
- **[Fait / Mesure clé]** : Réponse factuelle dense, nette, chiffrée issue de l'investigation
- **[Source / Référence]** : Citation exacte, chemin absolu, commit ou URL vérifiée

### ❓ [Deuxième question d'exploration contextuelle précise issue du cadrage 1:1] ?
- **[Fait / Mesure clé]** : Réponse factuelle dense et détaillée
- **[Contrainte technique]** : Donnée d'observation directe sans extrapolation

### ❓ [N-ième question d'exploration contextuelle précise issue du cadrage 1:1] ?
- **[Donnée vérifiée]** : Réponse factuelle issue du sous-agent dédié

---

## 🏗️ Section 2 : Modifications Proposées (Format Natif Google)

### Chantier 1 : [Nom du premier chantier / module logique]

#### [MODIFY] [nom_du_fichier.ext](file:///chemin/absolu/nom_du_fichier.ext)
- **Cible** : [Classe / Méthode / Section spécifique]
- **Modification chirurgicale** : [Description précise des changements — spécifications, signatures, comportement]
- **Garde-fous** : [Points de vigilance pour éviter les erreurs silencieuses ou les effets de bord]

#### [NEW] [nouveau_fichier.ext](file:///chemin/absolu/nouveau_fichier.ext)
- **Rôle** : [Responsabilité unique du nouveau fichier]
- **Interfaces** : [Exports, contrats et points de connexion]

---

### Chantier 2 : [Nom du deuxième chantier / module logique]

#### [MODIFY] [autre_fichier.ext](file:///chemin/absolu/autre_fichier.ext)
- **Cible** : [Spécifications chirurgicales]

#### [DELETE] [fichier_obsolete.ext](file:///chemin/absolu/fichier_obsolete.ext)
- **Motif** : [Justification du retrait et plan de dépréciation]

---

### Chantier : Hygiène & Organisation du Coffre Obsidian (AGENTS.md) *(Conditionnel — uniquement si anomalies réelles détectées)*

#### [MODIFY] [[Nom de la Note Maîtresse.md]]
- **Action** : [Rattachement du transcript voicenote sous H1, maillage wikilinks [[...]]]

#### [MODIFY] [[Note Concernée.md]]
- **Action** : [Formulation des titres Q/R finissant par ?, wikilinks [[...]], purge des faits obsolètes]

---

## 🧪 Section 3 : Plan de Vérification Biparti (Tableaux Markdown Natifs)

> [!IMPORTANT]
> **Obligation de Tableaux Markdown Natifs** :
> La Section 3 est obligatoirement formalisée sous la forme de deux tableaux distincts : un tableau pour les vérifications automatisées par l'agent (phase Build) et un tableau pour les vérifications manuelles réservées à Henri.

### 🤖 Vérifications Automatisées par l'Agent (Phase Build)

| Domaine / Cible | Commande ou Mécanisme de Test | Résultat Attendu & Garde-Fou |
|---|---|---|
| **Compilation & Syntaxe** | `[Commande exacte de build ou lint]` | Exit code 0, zéro erreur de syntaxe |
| **Audit des Signatures & Contrats** | `[Script ou vérification des interfaces]` | Types et arguments conformes aux attentes |
| **Validation Fonctionnelle Live** | `[Script jetable dans scratch/ ou commande]` | Comportement nominal constaté sur sortie brute |

### 👤 Vérifications Manuelles Réservées à Henri

| Volet de Contrôle | Action Spécifique demandée à Henri | Critère d'Acceptation Métier |
|---|---|---|
| **Inspection Visuelle / UI** | [Observer le rendu de l'interface ou de la note] | Rendu conforme, fluidité et lisibilité |
| **Validation Métier & UX** | [Tester le cas d'usage en conditions réelles] | Comportement fonctionnel conforme aux attentes |
```

### 4.2 📐 Structure Canonique de l'Artéfact (Mode Enquête Pure)

En Mode Enquête Pure, l'artéfact s'arrête strictement après la Section 1 :
```markdown
# 🧭 Rapport d'Exploration : [Titre du Sujet / Question]

[Description synthétique et dense du sujet investigué et du contexte.]

## 🗺️ Arborescence Prévisionnelle des Axes d'Investigation
- **axes_recherche/**
  - **axe_1_technique/**
    - [analyse_technique.md](file:///chemin/absolu/axe_1/analyse_technique.md) : Diagnostic d'architecture en une ligne concise
  - **axe_2_conceptuel/**
    - [cadrage_theorique.md](file:///chemin/absolu/axe_2/cadrage_theorique.md) : Modèle conceptuel et état de l'art en une ligne concise

---

## 🗣️ Section 1 : Questions Clés d'Exploration & Réponses Détaillées (Oral-First)

> [!IMPORTANT]
> **Questions d'Exploration Pures en Enquête** :
> Chaque élément d'investigation fait l'objet de sa propre question H3 dédiée (`### ❓ [Question d'investigation précise] ?`). Zéro méta-section vague : questions directes et réponses factuelles denses.

### ❓ [Première question d'investigation précise issue du cadrage 1:1] ?
- **[Constat factuel]** : Réponse dense, nette et chiffrée
- **[Preuve brute]** : Extrait vérifié, log ou citation mot à mot

### ❓ [Deuxième question d'investigation précise issue du cadrage 1:1] ?
- **[Constat factuel]** : Réponse factuelle détaillée
- **[Synthèse d'analyse]** : Constat issu de l'exploration sans extrapolation
```

---

## 5. 🛑 Comment S'Effectuent l'Arrêt et la Restitution Finale du Refine ?

Une fois `exploration_report.md` mis à jour et émis avec sa vignette interactive :

1. **Format de Restitution dans le Chat** :
   - **Ligne 1 (MANDATOIRE)** : Lien cliquable vers la note maîtresse Obsidian ou la note de référence : `[Nom de la Note Maîtresse](file:///chemin/absolu/vers/la/note.md)`.
   - **Bloc d'Artéfact (Haut)** : Référence directe à l'artéfact affiné : `[exploration_report.md](file:///<appDataDir>/brain/<conversation-id>/exploration_report.md)`.
   - **Synthèse Orale-First Percutante** : 2 à 4 paragraphes fluides résumant les clarifications obtenues, les arbitrages intégrés et la liste des chantiers consolidés.
   - **Zéro Copie Intégrale** : Ne JAMAIS dupliquer le contenu brut de l'artéfact dans le message.
   - **Rappel de Clôture & Appel à l'Action (Pied de Message)** :
     `> 📄 **Validation requise** : Consultez le détail complet du plan affiné dans la vignette interactive ci-dessus (ou via [exploration_report.md](file:///<appDataDir>/brain/<conversation-id>/exploration_report.md)) et cliquez sur **Proceed** pour autoriser le lancement de /build.`

2. **ARRÊTE-TOI.**
   - **Interdiction formelle d'enchaînement automatique (No Auto-Chaining)** : Le Refine Lead ne déclenche jamais `/build` de son propre chef. La poursuite vers `/build` est soumise à la validation explicite d'Henri via le bouton vert **Proceed** ou message textuel.
