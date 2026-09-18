---
name: scout
description: "Exploration approfondie du contexte, clarification active et production de rapports d'exploration incrémentaux et immutables (exploration_report_X.md)."
---
# 🧭 Comment l'Agent Principal Coordonne-t-il Directement l'Exploration et Rédige-t-il les Rapports d'Exploration Numérotés ?

**Objectif** : L'Agent Principal coordonne directement l'exploration exhaustive du codebase, de la documentation, du coffre (vault) Obsidian, des dépendances et du web pour comprendre un besoin, formalise les questions clés, déploie les sous-agents d'exploration en direct ($P=1$), clarifie en amont toutes les incertitudes via les arbitrages documentés, applique le protocole de rédaction personnelle pour les textes sensibles, et rédige directement le **rapport d'exploration incrémental et immutable** numéroté dans son brain racine : `<appDataDir>/brain/<conversation-id>/exploration_report_X.md` ($X = 1, 2, \dots$).

> [!IMPORTANT]
> **PRINCIPES CARDINAUX DU SCOUT :**
> - **🎯 PILOTAGE DIRECT PAR L'AGENT PRINCIPAL ($P=0$)** : L'Agent Principal définit directement les questions d'exploration, déploie les sous-agents d'exploration en lecture seule ($P=1$) et rédige directement le rapport d'exploration incrémental `exploration_report_X.md`. Zéro Lead intermédiaire, zéro perte de contexte ni téléphone arabe.
> - **🚫 SANCTUARISATION DU CODE DE PRODUCTION & AUTORISATION DES ARTÉFACTS DE PROTOTYPAGE** :
>   * **Interdiction Stricte** : Ni l'Agent Principal ni les sous-scouts ne touchent à aucun fichier de production dans les dépôts de code (`C:\Users\...\code\...`) ni aux notes pérennes du coffre Obsidian (`VoiceNotes/`) pendant la phase d'exploration.
>   * **Habilitation Explicite de Prototypage** : Les sous-agents d'exploration ($P=1$) sont FORMELLEMENT AUTORISÉS ET ENCOURAGÉS à exécuter des scripts de calcul temporaires dans `<appDataDir>/brain/<conversation-id>/scratch/`, générer des artéfacts de simulation, tracer des figures vectorielles (SVG, Mermaid, HTML) et rédiger des brouillons préliminaires (via `/draft`) au sein du brain. Ces artéfacts permettent à Henri de visualiser concrètement les résultats, d'arbitrer sur pièces et de valider la stratégie avant tout build.
> - **🔢 NUMÉROTATION INCRÉMENTALE (`exploration_report_X.md`)** : Chaque passage de `/scout` produit un nouveau rapport numéroté ($X=1$ pour le premier, $X=2$ au deuxième tour après feedback d'Henri, etc.).
> - **🔒 IMMUTABILITÉ ABSOLUE DES RAPPORTS PASSÉS** : Les rapports antérieurs (`exploration_report_1.md` à `exploration_report_{X-1}.md`) sont strictement intouchables et verrouillés.
> - **⚡ RÈGLE DU DELTA PUR ($X \ge 2$)** : Le rapport $X$ ne recopie JAMAIS le plan précédent. Si Henri n'a commenté qu'un seul élément, le rapport $X$ ne traite QUE de cet élément. **En Section 2 ($X \ge 2$), interdiction formelle de re-lister les chantiers/fichiers inchangés** : seuls les ajouts et modifications directes y figurent. Le merge additif du Build conserve tout le reste.
> - **🔄 PERSISTANCE DU CONTEXTE RACINE & ITÉRATIONS ($X \ge 2$)** : L'Agent Principal conserve l'intégralité du contexte en mémoire vive tout au long de la session. Lors des itérations ultérieures ($X \ge 2$), il explore directement le delta via de nouveaux sous-agents ciblés ($P=1$) et incrémente son rapport.
> - **⏱️ HEARTBEAT & TIMER DE LIVENESS (5 MINUTES)** : Dès le déploiement des sous-agents d'exploration ($P=1$), l'Agent Principal arme systématiquement un timer schedule de 300s (`TimerCondition: "any"`, `Prompt: "Vérifier la progression des sous-scouts"`) pour vérifier qu'aucun sous-scout n'est bloqué ou silencieux.
> - **📂 CENTRALISATION DANS LE BRAIN PRINCIPAL** : Le rapport `exploration_report_X.md` est généré et maintenu directement dans le répertoire brain de la conversation principale (`<appDataDir>/brain/<conversation-id>/exploration_report_X.md`).
> - **👁️ VISIBILITÉ ROOT DES ARTÉFACTS D'ARBITRAGE** : Dès qu'un artéfact visuel d'aide à la décision (ex: galerie de figures, maquette d'interface, tableau d'arbitrage) est généré à la demande d'Henri dans le cadre du Scout, il est écrit ou copié directement dans `<appDataDir>/brain/<conversation-id>/` pour être immédiatement consultable dans l'interface Antigravity.
> - **🔀 DEUX MODES OPÉRATIONNELS DÉDIÉS** : Mode Enquête Pure (Section 1 + Section Finale d'Arbitrages sans édition) vs Mode Implémentation (Sections 1 et 2 + Section Finale d'Arbitrages sans Section 3).
> - **🚫 ATTAQUE DIRECTE SOUS H1 (SUPPRESSION DU GRAPHE 3 COLONNES)** : L'artéfact attaque directement sous H1 sur la Section 1 (Questions Clés & Réponses Scan-First), sans graphe Mermaid à 3 colonnes ni arborescence textuelle redondante.
> - **🗣️ SECTION 1 SCAN-FIRST & QUESTIONS D'EXPLORATION PURES (RÈGLE 1:1)** : 1 question concrète = 1 sous-agent d'exploration $P=1$ en lecture seule = 1 titre H3 dédié (`### ❓ ... ?`). Chaque réponse est obligatoirement structurée en **liste à puces ou numérotée** (`**[Clé]** : [Valeur brute]`), concise, aérée et percutante, permettant à Henri d'identifier immédiatement les chiffres, dates, citations et décisions sans bloc de texte verbeux.
> - **🏗️ SECTION 2 CHANTIERS PAR FICHIER SANS QUESTIONS (FORMAT GOOGLE NATIF)** : Regroupement par module logique (`### Chantier X : ...`), ciblage direct des fichiers (`[NEW]`, `[MODIFY]`, `[DELETE]`) avec rôle et description chirurgicale, et INTERDICTION formelle de formuler des questions dans cette section.
> - **🛑 SUPPRESSION DÉFINITIVE DE LA SECTION 3 & QUESTIONS EN FIN DE RAPPORT** : Le rapport d'exploration en Mode Implémentation remplace toute Section 3 de tâches utilisateur par la section finale dédiée aux questions et arbitrages soumis à Henri.
> - **🚫 INTERDICTION DE PLAYWRIGHT** : Playwright est banni au profit de `search_web` et `read_url_content` (sauf formulaire privé d'Henri ou site web déployé demandé explicitement par Henri).
> - **✍️ PROTOCOLE RÉDACTION PERSONNELLE & EXCEPTION /DRAFT IMMÉDIATE DÈS LE SCOUT** : Bien que /scout interdise toute modification du codebase de production, **la rédaction, la retouche et le polissage de textes humains sensibles (courriels, lettres, résumés, justifications) via le skill `/draft` constituent une exception formelle autorisée et obligatoire dès la phase Scout**. L'Agent Principal déploie immédiatement un sous-agent exécutant direct ($P=1$) appliquant l'instrumentation machine officielle (`doc_version_cli.py diff` ou MCP `doc-version`) pour sceller la baseline v0 et générer l'artéfact de diff interactif (`diff_*.md`). Cet artéfact est obligatoirement lié dans `exploration_report_X.md` et dans le chat PENDANT la conception du plan, permettant à Henri d'arbitrer sur pièces la version retouchée avant le Build.
> - **🧹 RÉFLEXE « DREAM » & HYGIÈNE DU VAULT** : Veille contextuelle autonome sur les notes consultées (AGENTS.md) ; chantier d'hygiène conditionné aux désordres réels sans solliciter Henri sur le rangement.
> - 🚫 **BANNISSEMENT FORMEL D'ASK_QUESTION DANS /SCOUT** : Il est strictement INTERDIT à l'Agent Principal et aux sous-agents d'utiliser l'outil interactif `ask_question` pendant un workflow `/scout`. Toutes les questions ouvertes, variantes techniques et décisions d'arbitrage doivent figurer EXCLUSIVEMENT sous forme textuelle à la fin du rapport d'exploration (`exploration_report_X.md`) sous la section dédiée `## ❓ Quelles Sont les Questions & Décisions Soumises à l'Arbitrage d'Henri ?`. Henri annote l'artéfact ou répond librement dans le chat sans subir de modale bloquante.

---

## 1. 🎯 Comment S'Opère le Cadrage & l'Exploration Multi-Clusters ?

> [!IMPORTANT]
> **Matrice d'Habilitation Stricte du Workflow Scout (Architecture Directe à 2 Niveaux)** :
> - **Agent Principal ($P=0$, Superviseur Aveugle)** : Définit les questions d'exploration, déploie directement les sous-scouts ($P=1$), arme le timer `schedule`, lit les retours bruts et rédige `exploration_report_X.md` dans son brain racine (`<appDataDir>/brain/<conversation-id>/`). Il ne modifie pas le code de production ni les notes du coffre pendant l'exploration.
> - **Sous-Agents d'Exploration ($P=1$, `TypeName: 'self'`)** : Enquêtent en stricte lecture seule sur le codebase, le vault et le web. Prototypage scratch autorisé dans `<appDataDir>/brain/<conversation-id>/scratch/`. INTERDICTION formelle d'éditer le code de production et INTERDICTION formelle de déployer des sous-agents (exécutants feuilles directs, profondeur maximale $P=1$).

### 1.0 🏛️ Comment l'Agent Principal Pilote-t-il Directement l'Exploration sans Lead Intermédiaire ?
- **Pilotage Direct ($P=0 \to P=1$)** : À l'invocation de `/scout`, l'Agent Principal analyse le besoin, formalise les questions d'exploration et déploie DIRECTEMENT les sous-agents d'exploration spécialisés ($P=1$). Zéro Scout Lead intermédiaire, éliminant la double délégation et le risque de distorsion de l'information.
- **Persistance Multi-Itérations ($X \ge 2$)** : L'Agent Principal conserve tout son historique et son contexte en mémoire vive. Lors des itérations suivantes ($X \ge 2$), il n'a pas besoin d'intermédiaire : il évalue les remarques d'Henri, déploie de nouveaux sous-agents ciblés ($P=1$) pour explorer le delta, et rédige directement `exploration_report_X.md`.

### 1.0.1 🛑 Quelle Est la Règle Anti-Récursion pour les Sous-Agents d'Exploration ($P=1$) ?
- **Exécutants Feuilles Purs sans Re-délégation ($P=1$)** : Les sous-agents d'exploration sont déployés directement par l'Agent Principal (`TypeName: 'self'`, `Model: 'inherit'`). Ils disposent de l'accès complet aux outils de recherche, d'inspection CLI (`run_command` pour `git log`, `git status`, `git diff`, `curl`, `gh`, etc.) et à tous les MCPs. Ils ont l'**interdiction formelle** d'éditer ou de modifier des fichiers de production (`write_to_file`, `replace_file_content` interdits sur le codebase/vault) et l'**interdiction formelle** de déployer des sous-agents (`invoke_subagent` interdit au niveau $P=1$).
- **Prototypage & Scratch Local Autorisé ($P=1$)** : Pour répondre aux demandes d'Henri nécessitant des calculs empiriques, estimations de variance ou figures exploratoires, les sous-agents $P=1$ sont expressément autorisés à créer et exécuter des scripts scratch dans `<appDataDir>/brain/<conversation-id>/scratch/` et à consigner leurs résultats sous forme d'artéfacts de visualisation consultables par Henri.
- **Profondeur Maximale Stricte** : Agent Principal ($P=0$) ➔ Sous-agents d'exploration ($P=1$). Zéro sous-agent de sous-agent au niveau $P=1$.

### 1.1 🗺️ Quelle Est la Matrice des Clusters d'Exploration ?

| Cluster | Axes de Délégation | Outils Privilégiés |
| :--- | :--- | :--- |
| 💻 **Codebase** | Architecture existante, fonctions, types, points d'insertion | `list_dir`, `view_file`, `grep_search` |
| 📚 **Documentation** | Spécifications internes, README, guidelines, issues de suivi | `view_file`, `find_by_name` |
| 📓 **Vault Obsidian** | Notes du coffre, notes maîtresses de projet, décisions passées, AIVC | `view_file`, MCP `aivc` (`recall`, `consult_memory`) |
| 📦 **Dépendances** | Fichiers de configuration (`package.json`, `pyproject.toml`, requirements, extensions) | `view_file`, `grep_search` |
| 🌐 **Web** | Documentation officielle externe, changelogs, issues GitHub publiques, bonnes pratiques SOTA | `search_web`, `read_url_content` |

### 1.2 👥 Comment Déployer les Sous-Agents d'Exploration en Règle 1:1 Stricte ($N$ Questions = $N$ Agents) ?
- **Listing Préalable des Questions d'Exploration Pures** : Avant tout déploiement, l'Agent Principal formalise la liste exhaustive des questions pures d'exploration contextuelle indispensables pour cadrer le sujet (« De quoi ai-je besoin pour concevoir le plan ? Qu'est-ce que je dois savoir ? »). Règle canonique absolue : **1 question concrète = 1 sous-agent d'exploration `self` en lecture seule ($P=1$) = 1 titre H3 dédié (`### ❓ ... ?`)**. Zéro méta-section floue.
- **Règle 1:1 Inconditionnelle ($N \ge 1$)** : L'Agent Principal déploie **EXACTEMENT 1 sous-agent d'exploration par question** ($N$ questions = $N$ sous-agents `TypeName: 'self'` en stricte lecture seule lancés en parallèle via un unique appel `invoke_subagent`, `Model: "inherit"`).
- **Armement du Timer de Liveness (300s)** : Dès le déploiement des sous-agents $P=1$, l'Agent Principal arme systématiquement `schedule(DurationSeconds: 300, TimerCondition: "any", Prompt: "Vérifier la progression des sous-scouts")` pour garantir qu'aucune exploration ne reste bloquée plus de 5 minutes sans supervision active.

### 1.3 🧹 Comment Appliquer le Réflexe « Dream » et l'Hygiène Contextuelle du Coffre ?
Lors de l'exploration du cluster Vault Obsidian et des mémos vocaux (`voicenotes/`) :
Le sous-agent Vault a pour mandat exclusif la détection d'anomalies (notes orphelines, doublons, contradictions) dans le périmètre des notes consultées.
- **Autonomie d'Organisation** : Antigravity est le gestionnaire autonome du Digital Brain : **INTERDICTION formelle de déranger Henri avec des questions sur l'organisation interne ou le rangement de ses notes**.
- **Conditionnalité Stricte du Chantier d'Hygiène** : Intégrer conditionnellement un chantier `### Chantier : Hygiène & Organisation du Coffre Obsidian (AGENTS.md)` **UNIQUEMENT** si des anomalies réelles sont constatées sur les notes consultées.

### 1.4 🤝 Protocole Humain-Machine & Répartition des Tâches Immédiates
Dès le cadrage du Scout, l'Agent Principal prend connaissance de la note maîtresse ou des notes de contexte directes du projet via `view_file` (permis en lecture pure à l'Agent Principal comme "Calpin en Braille").

> [!IMPORTANT]
> **Armement Automatique du Pomodoro Racine (work)** :
> Si l'exploration porte sur un projet identifié du coffre (note existante ou créée taggée #todo/#project), l'Agent Principal DOIT impérativement lancer en tâche de fond la session Pomodoro via l'habilitation dérogatoire :
> `run_command: python "C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "<NomDuProjet>"`
> L'effort de cadrage et de recherche d'architecture fait partie intégrante du travail de projet et doit être horodaté et régulé dans project-memory.

Pendant que les sous-agents mènent l'exploration autonome en parallèle ($P=1$) :
1. **Proposition de 2 à 4 Tâches Humaines Ciblées** : L'Agent Principal propose immédiatement dans le chat 2 à 4 micro-tâches à haute valeur ajoutée réalisables par Henri en temps masqué (ex: arbitrer une orientation conceptuelle clé, retrouver un identifiant/accès externe, écouter un mémo vocal spécifique, ou valider un prérequis métier).
2. **Parallélisation Humain-Machine** : L'humain et l'équipe d'agents progressent simultanément dès la première minute sans temps mort.

---

## 2. 🔀 Quels Sont les Deux Modes Opérationnels de /scout ?

### 2.1 🔍 Mode Enquête Pure
Invoqué pour répondre à une question complexe, explorer une technologie ou auditer une faisabilité sans édition de code ni de notes. L'artéfact comprend l'Introduction, la Section 1 (Questions & Réponses Scan-First) et la section finale d'arbitrages pour Henri. Zéro Section 2 factice.

### 2.2 🏗️ Mode Implémentation
Invoqué pour concevoir et cadrer des modifications de code ou de notes destinées à être appliquées par `/build`. L'artéfact comprend l'Introduction, la Section 1, la Section 2 (Chantiers par fichier au format Google sans questions) et la section finale d'arbitrages pour Henri.

---

## 3. 🔢 Comment Fonctionne la Numérotation Incrémentale et l'Immutabilité des Rapports ($X = 1, 2, \dots$) ?

- **Verrouillage Historique** : Les rapports passés `exploration_report_1.md` à `exploration_report_{X-1}.md` sont strictement inaltérables.
- **Règle du Delta Pur** : Le rapport $X$ ne recopie JAMAIS les plans antérieurs et traite EXCLUSIVEMENT les éléments modifiés ou ajoutés.
- **Stockage Centralisé dans le Brain Racine** : Rédigé directement dans `<appDataDir>/brain/<conversation-id>/exploration_report_X.md`.

---

## 4. 💬 Comment Inscrire les Questions Ouvertes et Décisions d'Arbitrage en Fin de Rapport ?

Toutes les questions ouvertes, variantes ou décisions structurantes doivent impérativement être inscrites à la fin de l'artéfact `exploration_report_X.md` sous la section dédiée :
`## ❓ Quelles Sont les Questions & Décisions Soumises à l'Arbitrage d'Henri ?`.
Chaque question est une sous-section H3 (`### ❓ N. ... ?`) détaillant les options possibles avec la formule `**(Recommandé)**` en tête de la première option.

- **Bannissement Formel d'`ask_question`** : Ces arbitrages sont soumis EXCLUSIVEMENT de manière purement textuelle dans le rapport d'exploration sans JAMAIS déclencher l'outil interactif `ask_question`. Henri prend connaissance du rapport à son rythme, annote directement l'artéfact ou répond librement dans le chat sans modale bloquante.

---

## 5. ✍️ Comment Dérouler le Protocole de Rédaction Personnelle (Proposition Unique) ?

Lorsque la mission implique la production ou l'évolution d'un texte personnel, privé ou stratégique requérant une voix humaine authentique (≥ 1 paragraphe) :

### 5.1 ❓ Quel Est le Déroulement Méthodologique du Protocole ?
1. **Exposition des Faits Clés** : Rappel concis des contraintes et objectifs.
2. **Proposition Unique Soignée en Français** : Formuler UNE SEULE version rédigée avec élégance, clarté et naturel dans un français irréprochable (au lieu de multiplier les variantes superflues).
3. **Deux Issues Possibles & Exécution Immédiate de `/draft`** :
   - **Adoption directe** : Henri valide la proposition, qui est intégrée dans le plan.
   - **Brouillon brut ou retouche demandée par Henri** : Dès qu'Henri fournit son texte ou invoque `/draft` sur une section textuelle, l'Agent Principal déploie immédiatement un sous-agent exécutant direct ($P=1$) appliquant rigoureusement le skill `/draft` :
     * Scellement de la baseline v0 via `commit_document(mode="draft")`.
     * Retouche chirurgicale scalpel avec respect du seuil de rétention $\ge 90\%$.
     * Exécution machine obligatoire de `doc_version_cli.py diff` pour générer l'artéfact interactif Markdown (`diff_*.md`) dans `<appDataDir>/brain/<conversation-id>/`.
     * **Présentation Immédiate dans l'Exploration** : Le lien cliquable vers `diff_*.md` et le texte poli sont immédiatement intégrés dans `exploration_report_X.md` et restitués dans le chat. Le workflow Build n'aura plus qu'à appliquer in-situ le texte déjà validé.

---

## 6. 📄 Comment Rédiger et Structurer le Rapport d'Exploration exploration_report_X.md ?

### 6.1 📐 Quelle Est la Structure Canonique en Mode Implémentation ?

> [!IMPORTANT]
> **INVARIANTS FORMELS DE STRUCTURE STRICTE DU RAPPORT SCOUT** :
> 1. **Titre H1 obligatoirement interrogatif** : Se termine impérativement par un point d'interrogation `?`.
> 2. **Attaque directe sous H1 sur la Section 1 (Zéro Graphe Mermaid 3 Colonnes)** : L'artéfact ne contient aucun diagramme Mermaid à 3 colonnes en en-tête. Après une brève synthèse sous H1, il attaque directement sur `## 🗣️ Section 1 : Quelles Sont les Questions Clés d'Exploration & Réponses Détaillées (Scan-First) ?`.
> 3. **100% des sous-sections de la Section 1 en titres H3 interrogatifs formels** : `### ❓ [Question concrète] ?`. Interdiction absolue de substituer des intitulés comme "Pilier X", "Axe Y" ou "Synthèse".
> 4. **Section 2 obligatoire au format Google natif** : `## 🏗️ Section 2 : Quelles Sont les Modifications Proposées par Chantier (Format Natif Google) ?`. Description technique affirmative par module logique (`### Chantier X : ...`), ciblage direct `[NEW]`, `[MODIFY]`, `[DELETE]`, zéro question dans cette section.
> 5. **Section finale obligatoire pour l'arbitrage** : `## ❓ Quelles Sont les Questions & Décisions Soumises à l'Arbitrage d'Henri ?` avec des titres H3 `### ❓ N. ... ?`. Bannissement formel de l'outil interactif `ask_question` dans /scout (arbitrage purement textuel).

```markdown
# 🧭 Rapport d'Exploration X : [Titre du Projet / Objectif] ?

[Description synthétique et dense de l'objectif, du contexte métier et de la cible architecturale.]

---

## 🗣️ Section 1 : Quelles Sont les Questions Clés d'Exploration & Réponses Détaillées (Scan-First) ?

> [!IMPORTANT]
> **Format Scan-First en Listes à Puces ou Numérotées Obligatoire** :
> 1 question H3 dédiée par élément exploré (règle 1:1 avec les sous-scouts). Chaque réponse est obligatoirement structurée en **liste à puces ou numérotée** (`**[Clé]** : [Valeur brute]`), concise, aérée et percutante, permettant d'identifier immédiatement les chiffres, dates, citations et décisions sans bloc de texte verbeux.

### ❓ [Première question d'exploration contextuelle précise issue du cadrage 1:1] ?

- **[Clé 1]** : [Valeur brute / métrique / citation textuelle exacte]
- **[Clé 2]** : [Fait technique vérifié / contrainte identifiée]

### ❓ [Deuxième question d'exploration contextuelle précise issue du cadrage 1:1] ?

- **[Clé 1]** : [Constat technique direct / paramètre clé]
- **[Clé 2]** : [Point d'attention / dépendance identifiée]

---

## 🏗️ Section 2 : Quelles Sont les Modifications Proposées par Chantier (Format Natif Google) ?

> [!IMPORTANT]
> Description technique affirmative par module logique. Interdiction formelle de poser des questions dans cette section. Pour tout rapport $X \ge 2$ : lister strictement les chantiers modifiés ou créés (zéro re-listing des chantiers acquis).

### Chantier 1 : [Nom du premier module logique]

#### [MODIFY] [nom_du_fichier.ext](file:///chemin/absolu/nom_du_fichier.ext)
- **Cible** : [Classe / Méthode / Section spécifique]
- **Modification chirurgicale** : [Description précise des changements]
- **Garde-fous** : [Points de vigilance]

#### [NEW] [nouveau_fichier.ext](file:///chemin/absolu/nouveau_fichier.ext)
- **Rôle** : [Responsabilité unique du nouveau fichier]
- **Interfaces** : [Exports et connexions]

---

### Chantier 2 : [Nom du deuxième module logique]

#### [DELETE] [fichier_obsolete.ext](file:///chemin/absolu/fichier_obsolete.ext)
- **Motif** : [Justification du retrait]

---

## ❓ Quelles Sont les Questions & Décisions Soumises à l'Arbitrage d'Henri ?

### ❓ 1. [Intitulé de la première question ou décision structurante] ?
- **(Recommandé) Option A** : [Description de l'option recommandée]
- **Option B** : [Alternative envisagée]
```

---

## 7. 🛑 Comment S'Effectuent l'Arrêt et la Restitution Finale du Scout ?

### 7.1 📊 Quel Est le Protocole de Restitution & Invariant Anti-Publication Anticipée ?

> [!CAUTION]
> **INVARIANT DE RESTITUTION : INTERDICTION DE PUBLIER LE TABLEAU TANT QUE LE RAPPORT N'EST PAS PRODUIT.**
> Il est FORMELLEMENT INTERDIT de publier dans le chat un tableau récapitulatif mentionnant un rapport avec le statut « En cours de rédaction » ou « En préparation ».
> Le tableau d'historique ne doit être affiché qu'au moment précis où `exploration_report_X.md` est entièrement écrit sur le disque et validé.
> 
> **CLÔTURE STRICTE SANS RECOPIE DES QUESTIONS :**
> Le message de restitution dans le chat affiche la synthèse du delta et le tableau des rapports, sans recopier intégralement les questions d'arbitrage sous le tableau (elles figurent déjà de manière claire et ordonnée dans l'artéfact `exploration_report_X.md`).

```markdown
### 📑 Quel Est l'Historique des Rapports d'Exploration ?

| Rapport | Type & Statut | Synthèse du Contenu & Nouveautés |
|---|:---:|---|
| [Rapport d'Exploration 1](file:///...) | 🎯 Initial | Cadrage initial, questions 1..N, chantiers préliminaires |
| ... | ... | ... |
| **👉 [Rapport d'Exploration X (À relire)](file:///...)** | ⚡ **Dernier Delta** | **[Résumé des ajouts/corrections de cette itération]** |

> 📄 **Prêt pour le Build ?** Cliquez sur **Proceed** ou lancez `/build` pour que l'ensemble de ces rapports soit fusionné dans le plan d'implémentation final.
```

### 7.2 🚫 Pourquoi Aucun Enchaînement Automatique N'est-il Toléré (No Auto-Chaining) ?
L'agent ne doit JAMAIS lancer `/build` de sa propre initiative. Le passage au Build requiert une mention explicite de `/build` par Henri ou un clic sur Proceed.
