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
> **🗺️ CARTOGRAPHIE VISUELLE STANDARD EN 3 COLONNES VERTICALES.** Même cartographie que Scout : intégration systématique en tête de rapport d'un diagramme Mermaid à 3 colonnes verticales (`flowchart TD` avec 3 sous-graphes `subgraph` en `direction TB` chaînés de haut en bas avec `-->`) éliminant toute compression horizontale et garantissant une police de taille normale 100% lisible.
> **🗣️ SECTION 1 ORAL-FIRST & QUESTIONS D'EXPLORATION PURES.** 1 question concrète = 1 sous-agent d'exploration `self` en lecture seule = 1 titre H3 dédié (`### ❓ ...`). Zéro méta-section floue (« décisions d'arbitrage », « points de vigilance ») et ZÉRO prise de décision en Section 1 : UNIQUEMENT des questions/réponses d'information factuelle dense, nette et chiffrée. Résolues par puces télégraphiques (`- **[Clé]** : [Valeur]`) ou paragraphes courts (2 à 4 phrases). Zéro accordéon `<details><summary>` superflu. Bannissement formel des tableaux rigides en Section 1. Déport systématique des détails techniques ou juridiques lourds vers des sous-artéfacts dédiés dans `brain/<id>/`.
> **💡 VISUALISATION DES NOUVEAUTÉS PAR CALLOUTS (ZÉRO DIFF).** Interdiction formelle des blocs de code diff, balises `<span style="...">`, `<del>` ou `<ins>`. Pour chaque endroit modifié ou ajouté lors de l'itération de refine, insérer un simple callout Markdown immédiatement avant (`> [!NOTE] Modifié lors du Refine : ...` ou `> [!TIP] Nouveauté Refine : ...`). À chaque nouvelle itération de refine, nettoyer impérativement TOUS les anciens callouts des itérations précédentes afin de ne mettre en valeur que les deltas exclusifs de l'itération courante.
> **🚫 SUPPRESSION DE L'ARBORESCENCE REDONDANTE.** Dès lors que la cartographie visuelle à 3 colonnes verticales est générée, toute arborescence textuelle complémentaire est formellement bannie pour éviter les redites. Le rapport passe directement de la cartographie visuelle à la Section 1.
> **🏗️ SECTION 2 FORMAT GOOGLE NATIF.** Regroupement par Chantier (`### Chantier A : ...`), séparateurs `---` et balisage chirurgical `[MODIFY]`, `[NEW]`, `[DELETE]`.
> **🧪 SECTION 3 PLAN DE VÉRIFICATION BIPARTI EN TABLEAUX NATIFS.** Cloisonnement strict obligatoirement formalisé sous forme de TABLEAUX Markdown natifs (Contrôles automatisés agent vs Actions manuelles réservées à Henri).
> **👥 RÈGLE 1:1 DE DÉPLOIEMENT.** Le Refine Lead liste d'abord toutes les questions d'exploration contextuelle et de challenge à se poser, puis déploie EXACTEMENT 1 sous-agent d'exploration par question ($N$ questions = $N$ sous-agents `self` en stricte lecture seule en parallèle via un unique appel `invoke_subagent`).
> **🚫 INTERDICTION DE PLAYWRIGHT.** Playwright est banni au profit de `search_web` et `read_url_content` (sauf formulaire privé d'Henri ou site web déployé demandé explicitement par Henri).
> **🔄 CYCLE DE VIE DU PLAN : LECTURE SEULE, ACCUMULATION CONTINUE & CLEAN SLATE POST-BUILD.** Tant que `/build` n'a pas été formellement invoqué par Henri, maintien strict en lecture seule sans aucune modification de code ou de données. Toute idée, tâche, correction ou amélioration est obligatoirement consignée dans `exploration_report.md` qui s'enrichit continuellement pour devenir de plus en plus complet. Le passage en mode exécution s'opère exclusivement au `/build`, et une fois le travail validé par `walkthrough.md`, le plan est intégralement vidé (Clean Slate) pour la session suivante.

---

## 🛡️ Quelle est la Matrice d'Habilitation et la Contre-Instruction Anti-Récursion ($P=1$) ?

Le Superviseur Racine invoque obligatoirement le Refine Lead en tant que sous-agent (`TypeName: 'self'`, `Role: 'Refine Lead'`).

> [!CAUTION]
> ### Matrice d'Habilitation du Refine Lead
> 
> | Catégorie | Statut | Outils Spécifiques |
> |---|:---:|---|
> | **Délégation & Pilotage** | ✅ AUTORISÉ | `invoke_subagent` (déploiement exclusif de sous-agents d'exploration `self` en stricte lecture seule), `send_message`, `schedule` |
> | **Artefacts Brain & Mémoire** | ✅ AUTORISÉ | `view_file` (strictement limité aux fichiers `<appDataDir>/brain/<id>/...`), `write_to_file` (strictement limité à `exploration_report.md` et sous-analyses dans `brain/`), MCP `aivc` (`remember`, `recall`, `consult_memory`) |
| **Inspection du Code Source / Vault** | ❌ INTERDIT | `view_file` (sur le code du dépôt ou les notes), `grep_search`, `find_by_name`, `list_dir` |
| **Modification du Code Source** | ❌ INTERDIT | `write_to_file` (sur le dépôt), `replace_file_content` |
| **Exécution & Système** | ❌ INTERDIT | `run_command`, `manage_subagents` |
| **Dialogue Direct Utilisateur** | ❌ INTERDIT | `ask_question` (réservé exclusivement au Superviseur Racine) |

### ⚡ Contre-Instruction Anti-Récursion ($P=1$)
Les sous-agents mandatés par le Refine Lead sont des **exécutants directs en lecture seule** (`TypeName: 'self'`, `Model: 'inherit'`).
- Ils disposent de l'accès complet aux outils d'inspection : `view_file`, `grep_search`, `list_dir`, `find_by_name`, `run_command` (strictement limité aux commandes d'inspection en lecture seule : git log, status, diff, tests de diagnostic, curl) et tous les MCPs.
- Ils ont l'**interdiction formelle** d'éditer ou modifier des fichiers de production (`write_to_file`, `replace_file_content` interdits sur le codebase/vault).
- Pour le web, ils utilisent exclusivement `search_web` et `read_url_content` (Playwright banni sauf exception stricte).
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

### 1.1 🔄 Quel Est le Cycle de Vie Canonique du Plan (Lecture Seule, Accumulation Continue & Clean Slate Post-Build) ?

> [!IMPORTANT]
> **CYCLE DE VIE DU PLAN : DE L'EXPLORATION AU CLEAN SLATE POST-BUILD.**
> Le plan d'implémentation traverse un cycle de vie strict en 4 temps :
> 1. **Lecture Seule Stricte Amont** : Tant qu'Henri n'a pas formellement appelé `/build`, les agents (`scout`, `refine`, sous-agents d'exploration `self`) sont en **LECTURE SEULE STRICTE**. INTERDICTION FORMELLE d'effectuer la moindre modification sur du code, des fichiers sources, des notes du coffre, des formulaires web ou des services externes. Tout le travail consiste à explorer, vérifier les faits et perfectionner l'artéfact de cadrage.
> 2. **Consignation & Accumulation Continue (`exploration_report.md`)** : Toute idée de tâche, correction, point de vigilance ou amélioration doit être immédiatement consignée dans le plan d'implémentation unique `exploration_report.md`. Si un rapport non-buildé existe déjà, interdiction formelle d'écraser à blanc : le plan s'enrichit, se corrige, se complète et empile les nouveaux chantiers (`### Chantier N+1 : ...`) pour devenir de plus en plus exhaustif et précis au fil des échanges.
> 3. **Bascule en Mode Exécution au `/build`** : L'appel explicite de `/build` (ou la validation du bouton interactif Proceed) déclenche la transition vers le mode exécution. Le Build prend alors en charge l'application chirurgicale des modifications prévues dans le plan.
> 4. **Vidage Intégral Post-Build (Clean Slate)** : Une fois le travail de `/build` achevé, vérifié et validé par la production de `walkthrough.md`, le plan `exploration_report.md` est intégralement vidé (Clean Slate). La session est réinitialisée, prête à accueillir une nouvelle demande sur une table rase.

---

## 2. 👥 Comment Déployer les Sous-Agents d'Exploration en Règle 1:1 Stricte ($N$ Questions = $N$ Agents) ?

Le Refine Lead applique rigoureusement la règle 1:1 :
1. **Listing Préalable des Questions d'Exploration & de Challenge Pures** : Le Refine Lead liste exhaustivement toutes les questions pures d'investigation et de challenge technique à approfondir (« De quoi ai-je besoin pour consolider le plan ? Quelles hypothèses dois-je vérifier concrètement ? »). Règle canonique absolue : **1 question concrète = 1 sous-agent d'exploration `self` en lecture seule = 1 titre H3 dédié (`### ❓ ...`)**. Zéro méta-section floue (« décisions d'arbitrage », « points de vigilance »).
2. **Déploiement 1:1 Inconditionnel** : Le Refine Lead déploie **EXACTEMENT 1 sous-agent d'exploration par question** ($N$ questions = $N$ sous-agents `TypeName: 'self'` en stricte lecture seule en parallèle via un unique appel `invoke_subagent`, `Model: "inherit"`).
3. **Zéro Décision en Phase d'Exploration** : L'exploration est une recherche de preuves brutes et de faits avérés : aucune décision ni point de vigilance anticipé en Section 1 (zéro méta-section floue). Les décisions architecturales appartiennent à la Section 2 et au dialogue amont avec Henri.
4. **Template de Prompt pour Sous-Agent `self` en Lecture Seule** :
   ```text
   Tu es un sous-agent d'exploration 'self' mandaté par le Refine Lead (en stricte lecture seule).
   Question d'exploration / challenge assignée : [Formulation exacte de la question 1:1]
   Cibles & Périmètre : [Chemins absolus des fichiers ou modules à inspecter, CLI ou web]

   CONTRE-INSTRUCTION : Tu es un exécutant direct (P=1). Inspecte directement avec view_file, grep_search, list_dir, find_by_name, run_command (uniquement pour inspection CLI : git log, status, diff, curl, tests en lecture, etc.) et les MCPs.
   INTERDICTION FORMELLE d'éditer ou modifier du code ou des fichiers de production (write_to_file / replace_file_content interdits sur le projet).
   Pour toute recherche documentaire ou web, utilise exclusivement search_web et read_url_content (Playwright est formellement banni sauf exception stricte).
   Ne fais aucune supposition : rapporte des preuves matérielles brutes (citations mot à mot, chemins absolus, numéros de lignes, sorties de commandes).
   Transmets ton rapport chirurgical par send_message au Refine Lead.
   ```
5. **Agrégation Textuelle Exclusive par le Lead** :
   À leur retour, le Refine Lead agrège et croise exclusivement les données brutes textuelles renvoyées par `send_message`. **Zéro `view_file` de contre-vérification** sur le code source ou les notes par le Refine Lead.

---

## 3. 💬 Comment Remonter les Arbitrages au Superviseur Racine ?

> [!IMPORTANT]
> **ZÉRO ASSOMPTION, ZÉRO AMBIGUÏTÉ & OBLIGATION STRICTE D'ARBITRAGE ACTIF (`ask_question`).**
> Si le Refine Lead identifie la moindre incertitude, zone d'ombre, question ouverte ou arbitrage métier/technique (par ex. choix d'un seuil, d'une modalité d'exécution ou d'une conception), il est **STRICTEMENT INTERDIT de la laisser dormir dans un tableau passif ou une note annexe sans action**.
> Le Refine Lead ne devine jamais l'intention d'Henri sur un choix structurant. L'outil `ask_question` étant réservé exclusivement au Superviseur Racine ($P=0$) :
> 1. Le Refine Lead formalise obligatoirement une synthèse claire du dilemme avec les options envisageables formulées du point de vue d'Henri et l'option recommandée préfixée de `(Recommandé)`.
> 2. Il transmet cette demande d'arbitrage au Superviseur Racine via `send_message`.
> 3. Le Superviseur Racine a l'**obligation stricte de déclencher immédiatement `ask_question`** auprès d'Henri au même tour pour obtenir sa décision tranchée avant de valider l'artéfact ou de passer au `/build`.
> 4. Le Refine Lead intègre immédiatement l'arbitrage validé dans l'artéfact `exploration_report.md`.

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

### 4.0 💡 Comment Mettre en Valeur les Nouveautés par Callouts (Zéro Diff & Nettoyage Obligatoire) ?

Pour permettre à Henri de visualiser immédiatement et sans effort les apports de chaque passe d'affinement :

1. **Suppression Totale de Tout Format de Diff** :
   - **Interdiction formelle** des blocs de code ```diff, des annotations de suppression/ajout `+`/`-`, des balises HTML `<span style="...">`, `<del>` ou `<ins>`.
   - Le rapport reste un document Markdown propre, lisible et publiable en production.

2. **Mise en Valeur Chirurgicale par Callouts Standards** :
   - Pour chaque section, titre, question, chantier ou élément modifié ou ajouté lors de l'itération de refine en cours, insérer un simple callout Markdown natif immédiatement avant :
     * **Pour une modification d'un élément existant** :
       ```markdown
       > [!NOTE]
       > **Modifié lors du Refine** : [Explication concise du changement ou de l'ajustement apporté]
       ```
     * **Pour un ajout / une nouveauté** :
       ```markdown
       > [!TIP]
       > **Nouveauté Refine** : [Explication concise de la nouvelle tâche, du nouveau chantier ou du point clé ajouté]
       ```

3. **Règle de Nettoyage Préalable Obligatoire (Purge des Anciens Callouts)** :
   - **Nettoyage systématique** : À chaque nouvelle itération de refine (par exemple lors de la passe N+1), le Refine Lead doit **impérativement purger et supprimer tous les anciens callouts** (`> [!NOTE] Modifié lors du Refine` / `> [!TIP] Nouveauté Refine`) insérés lors des itérations précédentes.
   - **Zéro accumulation de callouts obsolètes** : Seuls les callouts correspondant aux nouveautés et modifications exclusives de l'itération courante doivent subsister dans le rapport.

### 4.1 📐 Structure Canonique de l'Artéfact (Mode Implémentation)

```markdown
# 🧭 Rapport d'Exploration : [Titre du Projet / Objectif]

[Description synthétique et dense de l'objectif, du contexte métier et de la cible architecturale.]

---

> [!TIP]
> **Nouveauté Refine** : Cartographie visuelle compacte à 3 piliers verticaux (`direction TB`), éliminant tout étirement horizontal pour une lisibilité parfaite.

## 🗺️ Cartographie Visuelle des Changements Prévus (3 Colonnes Verticales)

> [!IMPORTANT]
> **Diagramme Mermaid Standard à 3 Colonnes Verticales** :
> Afin d'éliminer toute compression ou étirement horizontal et de garantir une taille de police normale 100% lisible, la cartographie visuelle regroupe obligatoirement les actions sous forme de 3 colonnes verticales distinctes côte à côte (`flowchart TD` avec sous-graphes `subgraph` en `direction TB` chaînés de haut en bas avec `-->`).

```mermaid
flowchart TD
    ROOT["🎯 Plan d'Action Global : [Objectif]"] --> C1["🏗️ Chantier 1 : Module Principal"]
    ROOT --> C2["📓 Chantier 2 : Vault / Documentation"]
    ROOT --> C3["⚙️ Chantier 3 : Infra / Tests"]

    subgraph S1["Chantier 1 : Module Principal"]
        direction TB
        A1["Action 1.1 : Spécifications"] --> A2["Action 1.2 : Implémentation"]
        A2 --> A3["Action 1.3 : Validation Contrat"]
    end
    C1 --> S1

    subgraph S2["Chantier 2 : Vault / Documentation"]
        direction TB
        B1["Action 2.1 : Note Maîtresse"] --> B2["Action 2.2 : Sous-notes & Liens"]
        B2 --> B3["Action 2.3 : Hygiène & Q/R"]
    end
    C2 --> S2

    subgraph S3["Chantier 3 : Infra / Tests"]
        direction TB
        D1["Action 3.1 : Scripts Live"] --> D2["Action 3.2 : Intégration Git"]
        D2 --> D3["Action 3.3 : Checkpoint AIVC"]
    end
    C3 --> S3
```

---

## 🗣️ Section 1 : Questions Clés d'Exploration & Réponses Détaillées (Oral-First)

> [!NOTE]
> **Modifié lors du Refine** : Précision factuelle et chiffrée issue de la contre-expertise 1:1.

> [!IMPORTANT]
> **Doctrine Canonique des Questions d'Exploration Contextuelle** :
> - **Questions d'exploration contextuelle pures** : Ce sont les questions d'information pures que l'agent se pose au démarrage (« De quoi ai-je besoin pour affiner le plan ? Qu'est-ce que je dois savoir/vérifier ? »).
> - **1 Question H3 par élément d'investigation** : Chaque élément investigué ou challengé doit impérativement faire l'objet de sa PROPRE question H3 dédiée (`### ❓ [Question d'exploration précise] ?`).
> - **Correspondance 1:1 avec les sous-agents** : Chaque question H3 correspond exactement à la mission assignée à 1 sous-agent d'exploration (`self` en stricte lecture seule).
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
> La Section 3 est obligatoirement formalisée sous la forme de TABLEAUX Markdown natifs séparant strictement les contrôles automatisés exécutés par l'agent (phase Build) et les actions manuelles réservées à Henri.

### 🤖 Contrôles Automatisés par l'Agent (Phase Build)

| Domaine / Cible | Commande ou Mécanisme de Test | Résultat Attendu & Garde-Fou |
|---|---|---|
| **Compilation & Syntaxe** | `[Commande exacte de build ou lint]` | Exit code 0, zéro erreur de syntaxe |
| **Audit des Signatures & Contrats** | `[Script ou vérification des interfaces]` | Types et arguments conformes aux attentes |
| **Validation Fonctionnelle Live** | `[Script jetable dans scratch/ ou commande]` | Comportement nominal constaté sur sortie brute |

### 👤 Actions Manuelles Réservées à Henri

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
