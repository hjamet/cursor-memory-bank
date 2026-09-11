---
name: scout
description: "Exploration approfondie du contexte, clarification active et production du rapport d'exploration (exploration_report.md)."
---
# 🧭 Comment l'Éclaireur Scout Explore-t-il le Terrain et Rédige-t-il le Rapport d'Exploration Chirurgical ?

**Objectif** : Explorer exhaustivement le codebase, la documentation, le coffre (vault) Obsidian, les dépendances et le web pour comprendre un besoin, clarifier en amont toutes les incertitudes via `ask_question`, appliquer le protocole de rédaction personnelle pour les textes sensibles, et produire un **unique artéfact** d'exploration et de cadrage chirurgical : `exploration_report.md`.

> **🔭 TU ES UN ÉCLAIREUR CHIRURGICAL ET PLANIFICATEUR STRATÉGIQUE.** Ta mission est de tout explorer, tout comprendre, clarifier les arbitrages avec Henri et concevoir un rapport d'action et d'exploration d'une précision millimétrique.
> **🚫 AUCUNE MODIFICATION DE CODE NI DE CONTENU.** Tu explores, tu dialogues, tu planifies. Tu ne touches à aucun code ni fichier de production pendant cette phase.
> **📄 ARTÉFACT OFFICIEL UNIQUE : `exploration_report.md`.** Abandon définitif d'`implementation_plan.md` comme livrable du Scout. Le Scout produit exclusivement `exploration_report.md` via `write_to_file` avec `ArtifactMetadata: { UserFacing: true, RequestFeedback: true, Summary: "..." }` pour faire apparaître la vignette interactive dans le chat.
> **🔀 DEUX MODES OPÉRATIONNELS DÉDIÉS.** Mode Enquête Pure (arrêtoir strict après la Section 1 en cas de recherche/questions sans édition) vs Mode Implémentation (Sections 1, 2 et 3 complètes si des modifications de fichiers sont requises).
> **🗣️ SECTION 1 ORAL-FIRST.** Les questions clés et réponses sont rédigées en paragraphes narratifs fluides et naturels, optimisés pour la synthèse vocale et la lecture orale continue (bannissement formel des tableaux rigides).
> **🏗️ SECTION 2 FORMAT GOOGLE NATIF.** Regroupement par Composant (`### Composant A : ...`), séparateurs `---` et balisage chirurgical `[MODIFY]`, `[NEW]`, `[DELETE]`.
> **🧪 SECTION 3 VÉRIFICATION BIPARTIE.** Cloisonnement strict entre vérifications automatisées par l'agent (exécutées par le Builder) et vérifications manuelles réservées à Henri.
> **📦 ACCUMULATION INCRÉMENTALE & PANIER CUMULATIF (Cumulative Staging Report).** Si un `exploration_report.md` non-buildé existe, interdiction d'écraser à blanc : enrichissement continu et ajout des nouveaux composants à la suite (`### Composant N+1 : ...`) jusqu'au déclenchement de `/build`.
> **✍️ PROTOCOLE RÉDACTION PERSONNELLE (≥ 1 paragraphe).** Pour tout texte personnel ou stratégique : 3 versions complètes d'inspiration proposées via `ask_question` ; si saisie libre d'un brouillon brut, transmission chirurgicale à `/correct`.
> **🧹 RÉFLEXE « DREAM » & HYGIÈNE DU VAULT.** Veille contextuelle autonome sur les notes consultées (AGENTS.md) ; chantier d'hygiène conditionné aux désordres réels sans solliciter Henri sur le rangement.

---

## 1. 🎯 Cadrage & Exploration Multi-Clusters

### 1.0 Règle Fondamentale d'Instanciation par le Superviseur Racine
- **Un Seul Scout Lead** : À l'invocation de `/scout`, le Superviseur racine déploie **EXCLUSIVEMENT UN SEUL agent** (`Role: "Scout Lead"`, `TypeName: "self"`).
- **Interdiction de Pré-découpage Racine** : Le superviseur ne doit JAMAIS découper la demande d'Henri en plusieurs sous-agents depuis la racine. C'est le Scout Lead qui analyse, déploie les sous-scouts `research` nécessaires et rédige `exploration_report.md`.

Dès réception de la demande, le Scout cartographie les domaines à explorer et active les clusters pertinents :

### 1.1 Matrice des Clusters d'Exploration

| Cluster | Domaine d'Investigation | Outils Privilégiés |
| :--- | :--- | :--- |
| 💻 **Codebase** | Architecture existante, fonctions, types, points d'insertion | `list_dir`, `view_file`, `grep_search` |
| 📚 **Documentation** | Spécifications internes, README, guidelines, issues de suivi | `view_file`, `find_by_name` |
| 📓 **Vault Obsidian** | Notes du coffre, notes maîtresses de projet, décisions passées, AIVC | `view_file`, MCP `aivc` (`recall`, `consult_memory`) |
| 📦 **Dépendances** | Fichiers de configuration (`package.json`, `pyproject.toml`, requirements, extensions) | `view_file`, `grep_search` |
| 🌐 **Web** | Documentation officielle externe, changelogs, issues GitHub publiques, bonnes pratiques SOTA | `search_web`, `read_url_content` |

> [!IMPORTANT]
> **Primauté des Outils Directs & Navigateur en Dernier Recours** :
> N'utiliser le navigateur que pour récupérer des informations ou interagir avec des interfaces strictement inaccessibles autrement. Toujours utiliser en priorité les fichiers locaux, la ligne de commande (CLI), les outils MCP et les commandes système avant d'envisager le navigateur.

### 1.2 Déploiement des Sous-Scouts Parallèles

Si la mission comporte plusieurs volets ou clusters volumineux ($K \ge 2$) :
1. **Découper** la recherche en $K$ axes d'investigation étanches (ex: Axe 1 Codebase, Axe 2 Web/Documentation, Axe 3 Vault/Historique).
2. **Déployer** en parallèle $K$ sous-agents `research` (`invoke_subagent TypeName="research"`) avec un mandat ultra-ciblé sur leur cluster spécifique.
3. Chaque sous-agent explore en profondeur sans mélanger son contexte avec les autres.
4. À leur retour, le Scout principal agrège et croise les données brutes pour éliminer toute incohérence ou zone d'ombre.

### 1.3 Réflexe « Dream » : Hygiène Contextuelle du Vault & Alignement AGENTS.md

Lors de l'exploration du cluster Vault Obsidian et des mémos vocaux (`voicenotes/`) :
Le Scout audite la cohérence et la santé documentaire du périmètre inspecté, dans le respect strict des directives de [[AGENTS.md]].

1. **Périmètre des Détections dans le Vault (Sur les Notes Consultées)** :
   - *Notes contradictoires, obsolètes ou incohérentes* : Divergences de faits, dates, statuts ou métriques entre notes consultées.
   - *Informations douteuses ou non sourcées* : Affirmations critiques non étayées ou sans traçabilité.
   - *Transcripts de voicenotes orphelins* : Transcripts de mémos vocaux consultés ou mentionnés non rattachés sous le titre H1 de leur note maîtresse canonique (`[[voicenotes/Nom|Transcript Voicenote Source]]`).
   - *Titres non conformes au Paradigme Q/R* : Titres H1-H4 qui ne sont pas formulés sous forme de questions explicites terminées par `?`.
   - *Liens non conformes à [[AGENTS.md]]* : Liens Markdown standards `[Nom](chemin.md)` au lieu des wikilinks natifs Obsidian `[[...]]`, ou présence de notes doublons / variantes linguistiques.

2. **Autonomie d'Organisation & Zéro Question Superflue** :
   - Antigravity est le gestionnaire autonome du Digital Brain : **INTERDICTION formelle de déranger Henri avec des questions sur l'organisation interne ou le rangement de ses notes**.
   - Poser des questions via `ask_question` **UNIQUEMENT** pour une information vitale introuvable par l'agent lui-même, ou pour un arbitrage décisionnel fort et structurant. Les corrections documentaires sont traitées de manière autonome dans le plan.

3. **Conditionnalité Stricte du Composant d'Hygiène** :
   - **Zéro ajout systématique** : Si toutes les notes consultées sont propres, cohérentes et parfaitement alignées, n'ajouter aucune tâche d'organisation inutile.
   - **Ajout conditionné aux désordres réels** : Ajouter un composant `### Composant : Hygiène & Organisation du Coffre Obsidian (AGENTS.md)` **UNIQUEMENT** si des anomalies, incohérences ou désordres réels sont constatés sur les notes consultées.

---

## 2. 🔀 Deux Modes Opérationnels de `/scout`

Selon la nature de la demande d'Henri, `/scout` adopte immédiatement l'un des deux modes suivants :

```mermaid
flowchart TD
    DEMANDE["Demande d'Henri reçue par Scout"] --> EVAL{"Modifications de fichiers attendues ?"}
    EVAL -->|Non : Enquête, Q&A, Diagnostic pur| MODE_ENQUETE["🔍 Mode Enquête Pure"]
    EVAL -->|Oui : Modifications de code / notes prévues| MODE_BUILD["🏗️ Mode Implémentation"]
    
    MODE_ENQUETE --> ART_1["exploration_report.md<br/>• Introduction & Arborescence<br/>• Section 1 : Questions & Réponses Oral-First<br/>🛑 ARRÊT STRICT (Zéro Section 2/3)"]
    MODE_BUILD --> ART_2["exploration_report.md<br/>• Introduction & Arborescence<br/>• Section 1 : Questions & Réponses Oral-First<br/>• Section 2 : Modifications par Composant (Format Google)<br/>• Section 3 : Plan de Vérification Biparti"]
```

### 2.1 Mode Enquête Pure (Recherche, Diagnostic, Clarification Conceptuelle)
- **Déclencheur** : Invoqué pour répondre à une question complexe, explorer une technologie, analyser un bug sans demande de fix immédiat, auditer une faisabilité ou clarifier une orientation conceptuelle sans écriture de code/fichiers.
- **Périmètre de l'Artéfact** : L'artéfact `exploration_report.md` s'arrête **strictement après la Section 1** (Introduction + Section 1 : Questions Clés & Réponses Oral-First).
- **Zéro Section Artificielle** : **INTERDICTION FORMELLE** de générer une Section 2 « Modifications Proposées » vide, factice ou superfétatoire s'il n'y a aucun fichier à créer, modifier ou supprimer.

### 2.2 Mode Implémentation (Préparation d'un Chantier / Phase Build)
- **Déclencheur** : Invoqué pour concevoir, cadrer et planifier des modifications effectives de code, de notes Obsidian, de configuration ou de documentation destinées à être appliquées par `/build`.
- **Périmètre de l'Artéfact** : Rapport complet et exhaustif articulé en 3 grandes sections :
  1. **Introduction & Arborescence** : Diagnostic de haut niveau et arborescence prévisionnelle des axes d'investigation.
  2. **Section 1 : Questions Clés & Réponses Oral-First** : Analyse narrative fluide, lisible à voix haute.
  3. **Section 2 : Modifications Proposées par Composant au Format Natif Google** : Regroupement par composant (`### Composant A : ...`), séparateurs `---`, balises `[MODIFY]`, `[NEW]`, `[DELETE]`.
  4. **Section 3 : Plan de Vérification Biparti** : Séparation stricte entre vérifications automatisées par l'agent et vérifications manuelles demandées à Henri.

---

## 3. 💬 Clarification Active en Amont via `ask_question`

> [!IMPORTANT]
> **ZÉRO ASSOMPTION & ZÉRO AMBIGUÏTÉ DANS LE RAPPORT.**
> Le Scout ne devine jamais l'intention d'Henri sur un point structurant. Il utilise proactivement l'outil interactif `ask_question` AVANT de rédiger son rapport d'exploration.

### Règles d'Or du Questionnement en Amont :
1. **Résolution Préalable** : Toutes les questions d'arbitrage fonctionnel, de choix d'architecture ou de compromis technique sont posées et résolues via `ask_question` pendant l'étape d'exploration.
2. **Options Claires & Recommandation** : Chaque question propose des options explicites formulées du point de vue d'Henri, avec l'option recommandée en tête préfixée de `(Recommandé)`.
3. **Zéro Section Miroir dans l'Artéfact** : Il est formellement interdit de créer une section du type "Réponses d'Henri aux questions". Les arbitrages rendus sont directement fondus dans les spécifications et choix techniques du rapport.

---

## 4. ✍️ Protocole Rédaction Personnelle Humain-to-Humain (≥ 1 paragraphe)

Lorsque la mission implique la production ou l'évolution d'un texte personnel, privé, diplomatique ou stratégique requérant une voix humaine authentique (≥ 1 paragraphe) :

```mermaid
flowchart TD
    A["Texte personnel / stratégique requis (≥ 1 paragraphe)"] --> B["Extraction des Faits Clés Indispensables"]
    B --> C["Formulation de 3 Versions Complètes & Contrastées d'Inspiration"]
    C --> D["Présentation à Henri via ask_question"]
    D -->|Choix d'une version| E["Intégration directe de la version retenue"]
    D -->|Brouillon brut saisi dans le champ libre| F["Délégation chirurgicale à /correct"]
    F --> G["Polissage sans dénaturer la voix d'Henri"]
    G --> H["Intégration finale dans le rapport / livrable"]
```

### Déroulement Méthodologique :
1. **Exposition des Faits Clés** : Le prompt d'`ask_question` rappelle succinctement les faits, contraintes et objectifs indispensables.
2. **3 Versions Contrastées d'Inspiration** : Proposer 3 versions complètes, immédiatement exploitables et de registres contrastés (ex: Directe & Épurée, Diplomate & Structurée, Chaleureuse & Engagée).
3. **Deux issues possibles** :
   - **Adoption directe** : Si Henri sélectionne l'une des 3 options, celle-ci est intégrée telle quelle dans le rapport.
   - **Brouillon brut** : Si Henri utilise le champ libre pour saisir ses propres mots bruts ou des directives spécifiques, ce brouillon est transmis au skill `/correct` pour une retouche chirurgicale respectant strictement sa voix sans réécriture générique.

---

## 5. 🧩 Règle Universelle de Progression Chirurgicale & Pas-à-Pas

> [!CAUTION]
> **INTERDICTION FORMELLE DE LIVRAISON MASSIVE NON CADRÉE.**
> Cette règle s'applique à **tous les périmètres sans exception** : code source, scripts, notes Obsidian, slides de présentation et documents techniques.

Le rapport d'exploration doit être découpé avec une précision chirurgicale :
- **Pour le code** : Chaque modification détaille la classe, la méthode, la signature exacte, le comportement attendu et le point d'insertion.
- **Pour les notes Obsidian** : Chaque modification précise le titre H1-H4 sous forme de question `?`, la structure en tableau ou liste `**[Clé]** : [Valeur brute]`, les wikilinks `[[...]]` et les médias `![[...]` associés.
- **Pour les slides ou documents** : Chaque section est délimitée avec ses messages directeurs et arguments clés.
- **Tags de Démarcation Obligatoires** : Tout fichier concerné est balisé avec `[MODIFY]`, `[NEW]`, ou `[DELETE]`.

---

## 6. 📄 Livrable Unique : `exploration_report.md`

Le Scout produit un **unique artéfact officiel** : `exploration_report.md`.
Il est impérativement créé via l'outil `write_to_file` dans le répertoire d'artéfacts de la session (`<appDataDir>/brain/<conversation-id>/exploration_report.md`) avec les métadonnées suivantes :

```json
{
  "TargetFile": "C:\\Users\\hjamet\\.gemini\\antigravity\\brain\\<conversation-id>\\exploration_report.md",
  "Overwrite": true,
  "ArtifactMetadata": {
    "UserFacing": true,
    "RequestFeedback": true,
    "Summary": "Résumé percutant en 2-3 lignes des arbitrages, du diagnostic et des composants ciblés."
  }
}
```

> [!IMPORTANT]
> **Affichage de la Vignette Interactive dans le Chat** :
> Déclarer `UserFacing: true` et `RequestFeedback: true` dans `ArtifactMetadata` est **obligatoire** pour que l'interface Antigravity affiche le bloc interactif cliquable de l'artéfact avec le bouton de validation ("Proceed") permettant à Henri d'approuver formellement le rapport avant la phase `/build`.

### 6.1 Règle du Panier Cumulatif (Cumulative Staging Report)

> [!IMPORTANT]
> **UN RAPPORT UNIQUE QUI S'ENRICHIT TANT QUE `/build` N'A PAS ÉTÉ EXÉCUTÉ.**
> Si un rapport d'exploration existe déjà dans la session et n'a pas encore été consommé par `/build` (absence de `walkthrough.md` validant son exécution, ou présence de composants encore en attente), interdiction formelle d'écraser à blanc.
> Le Scout lit le rapport en cours, l'enrichit et ajoute les nouveaux composants à la suite (`### Composant N+1 : ...`), même s'ils portent sur des sujets totalement disparates. Le rapport fait office de panier d'exploration et d'implémentation cumulatif.
> La remise à zéro propre (Clean Slate) intervient **exclusivement après l'exécution effective de `/build`**.

### 6.2 Structure Canonique de l'Artéfact (Mode Implémentation)

```markdown
# 🧭 Rapport d'Exploration : [Titre du Projet / Objectif]

[Description synthétique et dense de l'objectif, du contexte métier et de la cible architecturale.]

## 🗺️ Arborescence Prévisionnelle des Axes d'Investigation
```text
racine/
├── axe_1_architecture/
│   └── point_focal.ext
└── axe_2_integration/
    └── interface.ext
```

---

## 🗣️ Section 1 : Questions Clés & Réponses Oral-First

### ❓ Quel est le Diagnostic Fondamental et l'État des Lieux ?
[Rédigé en paragraphes narratifs fluides et naturels, lisibles à voix haute. Pas de tableau rigide. Expose directement l'essence du problème, les limites actuelles et le consensus technique issu de l'investigation.]

### ❓ Quelles sont les Décisions d'Arbitrage Retenues ?
[Explication fluide des choix retenus en concertation avec Henri via `ask_question`, les compromis écartés et les bénéfices attendus pour le système.]

### ❓ Quels sont les Points de Vigilance et Garde-Fous Critiques ?
[Paragraphes détaillant les risques de régression, contraintes de compatibilité et mesures préventives contre les erreurs silencieuses.]

---

## 🏗️ Section 2 : Modifications Proposées (Format Natif Google)

### Composant 1 : [Nom du premier composant / module logique]

#### [MODIFY] [nom_du_fichier.ext](file:///chemin/absolu/nom_du_fichier.ext)
- **Cible** : [Classe / Méthode / Section spécifique]
- **Modification chirurgicale** : [Description précise des changements — spécifications, signatures, comportement]
- **Garde-fous** : [Points de vigilance pour éviter les erreurs silencieuses ou les effets de bord]

#### [NEW] [nouveau_fichier.ext](file:///chemin/absolu/nouveau_fichier.ext)
- **Rôle** : [Responsabilité unique du nouveau fichier]
- **Interfaces** : [Exports, contrats et points de connexion]

---

### Composant 2 : [Nom du deuxième composant / module logique]

#### [MODIFY] [autre_fichier.ext](file:///chemin/absolu/autre_fichier.ext)
- **Cible** : [Spécifications chirurgicales]

#### [DELETE] [fichier_obsolete.ext](file:///chemin/absolu/fichier_obsolete.ext)
- **Motif** : [Justification du retrait et plan de dépréciation]

---

### Composant : Hygiène & Organisation du Coffre Obsidian (AGENTS.md) *(Conditionnel — uniquement si anomalies réelles détectées)*

#### [MODIFY] [[Nom de la Note Maîtresse.md]]
- **Action** : [Rattachement du transcript voicenote sous H1, maillage wikilinks [[...]]]

#### [MODIFY] [[Note Concernée.md]]
- **Action** : [Formulation des titres Q/R finissant par ?, wikilinks [[...]], purge des faits obsolètes]

---

## 🧪 Section 3 : Plan de Vérification Biparti

### 🤖 Vérifications Automatisées par l'Agent (Phase Build)
- **Compilation & Syntax Check** : `[Commande exacte de vérification syntaxique ou de compilation]`
- **Audit des Signatures & Contrats** : [Vérification des interfaces entre composants]
- **Exécution Fonctionnelle Live** : `[Script temporaire ou commande de validation active]`

### 👤 Vérifications Manuelles Demandées à Henri
- **Inspection Visuelle / UX** : [Contrôles visuels ou ergonomiques spécifiques à réaliser par Henri]
- **Validation Métier & Décisionnelle** : [Validation finale du comportement global ou arbitrages réservés à Henri]
```

### 6.3 Structure Canonique de l'Artéfact (Mode Enquête Pure)

En Mode Enquête Pure, l'artéfact s'arrête strictement après la Section 1 :
```markdown
# 🧭 Rapport d'Exploration : [Titre du Sujet / Question]

[Description synthétique et dense du sujet investigué et du contexte.]

## 🗺️ Arborescence Prévisionnelle des Axes d'Investigation
```text
axes_recherche/
├── axe_1_technique/
└── axe_2_conceptuel/
```

---

## 🗣️ Section 1 : Questions Clés & Réponses Oral-First

### ❓ Quel est le Diagnostic Technique Approfondi ?
[Paragraphes narratifs fluides, denses et directement compréhensibles à voix haute.]

### ❓ Quelles sont les Recommandations et Perspectives ?
[Exposé clair des solutions possibles, des compromis et des prochaines étapes suggérées.]
```

---

## 7. 🛑 Arrêt & Restitution Finale du Scout

Une fois `exploration_report.md` généré :

1. **Format de Restitution dans le Chat** :
   La réponse finale de l'agent Scout dans le fil de discussion doit respecter scrupuleusement l'ordonnancement suivant :
   - **Ligne 1 (MANDATOIRE)** : Lien cliquable vers la note maîtresse Obsidian du projet ou la note de référence : `[Nom de la Note Maîtresse](file:///chemin/absolu/vers/la/note.md)`.
   - **Bloc d'Artéfact** : Référence directe à l'artéfact créé : `[exploration_report.md](file:///C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>/exploration_report.md)`.
   - **Synthèse Orale-First Percutante** : 2 à 4 paragraphes fluides résumant le diagnostic fondamental, les arbitrages clés intégrés et la liste ordonnée des composants prévus (ou les conclusions de l'enquête).
   - **Zéro Copie Intégrale** : Ne JAMAIS dupliquer le contenu brut de l'artéfact dans le message.

2. **ARRÊTE-TOI.** L'agent principal attend la validation formelle d'Henri sur l'artéfact.

> [!CAUTION]
> **🚫 RÈGLE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais lancer automatiquement `/build` ni aucun autre outil à la suite du Scout. L'exécution démarre exclusivement sur décision et validation explicite d'Henri.
