---
name: paper-writing
description: Rédaction scientifique, charte stylistique académique sans fard IA (112 mots bannis, 0 em-dash, avoid-ai-writing, StealthRL), figures/tableaux, compilation LaTeX, révision chirurgicale et synchro Overleaf.
aliases:
  - paper-writing
---
# 📝 Comment Rédiger, Polir et Réviser des Papiers Académiques (`paper-writing`) ?

> [!IMPORTANT]
> **Rôle Canonique : Orchestrateur Technique & Charte Stylistique Académique Unifiée**
> Ce skill unifie l'orchestration technique d'un article scientifique (synchronisation Overleaf, conception des figures et tableaux, compilation LaTeX, versioning déclaratif `doc-version`) et la charte stylistique académique sans fard IA (posture de chercheur senior, bannissement absolu des tirets cadratins `—`, table des 112 clichés IA, suite déterministe Node.js [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) et érosion statistique [`stealth_rewriter.py`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/stealth_rewriter.py) sous le seuil $P(\text{AI}) < 0,10$).
> - **Pour la Relecture Chirurgicale de Brouillons d'Henri** : Mobiliser [`draft`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md) (résolution des balises `<XXX>` et rétention $\ge 90\,\%$ de la voix d'Henri).
> - **Pour la Revue Bibliographique Amont & l'Hygiène `.bib`** : Mobiliser [`literature-review`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/skills/literature-review/SKILL.md) et vérifier systématiquement le fichier `.bib` sur **[https://refscheck.ch/](https://refscheck.ch/)** (et `https://refscheck.ch/bib-fixer/`) via le MCP Playwright (en onglet furtif d'arrière-plan) pour éliminer tout DOI erroné ou référence altérée et enrichir les DOIs manquants.

---

## 1. 🏛️ Posture du Chercheur Senior & Conception Scientifique (Directives Henri Jamet, Prof. Michalis Vlachos & Prof. Yash Raj Shrestha)

L'écriture scientifique doit refléter la maturité d'un chercheur senior : rigueur, sobriété, précision factuelle et neutralité absolue (voir aussi [Conseils Redaction Scientifique Michalis Vlachos.md](file:///c:/Users/Jamet/Documents/VoiceNotes/notes/Conseils%20Redaction%20Scientifique%20Michalis%20Vlachos.md) et [Conseils Methodologiques et Analyse de Yash Raj Shrestha.md](file:///c:/Users/Jamet/Documents/VoiceNotes/notes/Conseils%20Methodologiques%20et%20Analyse%20de%20Yash%20Raj%20Shrestha.md)).

### A. Principes Directeurs de Rédaction
1. **Objectivité & Neutralité** : Aucun superlatif non quantifié, aucune flatterie ou auto-congratulation (*« revolutionary »*, *« groundbreaking »*, *« remarkable »*, *« exceptional »* sont proscrits).
2. **Économie de Mots & Attaque Directe** : Chaque mot doit être porteur d'information vérifiable. Éliminer le meublage (*padding*), les phrases de réchauffement (*« It is widely acknowledged that... »*) et les ouvertures ronflantes.
3. **Voix Active & Clarté Syntactique** : Privilégier des phrases actives et concises (*« The results indicate that... »* plutôt que *« It can be observed that the results were produced by... »*).
4. **Dénué de Sensationnalisme** : Présenter les limites avec la même rigueur et sérénité que les succès expérimentaux.
5. **L'Abstract Doit Vendre un Message Unique avec des KPIs Explicites, Zéro Surcharge Cognitive (Directives Prof. Michalis Vlachos, 17–26/10/2026)** :
   - **Vendre l'idée sans ralentir le lecteur** (*« Abstract needs to SELL the paper, not confuse the reader. I would reject the paper, just by reading the abstract »*, *« for me the abstract had too much info, and I had to go reeeally slow to understand what it was saying »*) : un abstract doit délivrer un message unique et limpide en une seule lecture à vitesse normale. Bannir tout acronyme non expliqué (`OSF`), toute arithmétique secondaire d'effectifs (`28 + 25 + 25 = 78`) et tout glissement terminologique (ne pas appeler 3 éléments des *« approaches »* au début d'une phrase puis sa baseline un *« single-base model »* à la fin).
   - **Quantifier l'effet principal sur un KPI intuitif dans l'Abstract vs Bannir le bruit chiffré dans Experiments** :
     * **Dans l'Abstract** : ne jamais énoncer un résultat sous forme de formule abstraite ou énigmatique (*« Removing the knowledge graph causes structural collapse »* est obscur si l'on ne dit pas ce que cela signifie concrètement). Exprimer l'impact par un **ordre de grandeur explicite sur un KPI immédiatement compréhensible** (*how much better and under what KPI?* — ex. *« build 40% fewer course modules ($2.62$ vs. $4.35$) »*, *« $3.96/5$ vs. $3.56/5$ on a 14-item blind rubric »*), tout en éliminant les batteries de métriques abstraites et les $p$-values secondaires ou gonflées au niveau de l'item.
     * **Dans le corps du texte (`Experiments`)** : rendre le texte **conversationnel et humainement lisible** (*« go through the experiments and try to make the text conversational, as the following is not readable (at least by humans! ;) »*). Les tableaux et figures portent le détail des chiffres (`see Table X`, `Figure Y`) ; la prose raconte l'histoire causale (*a story*), interprète *pourquoi* chaque condition produit son effet et s'appuie sur un **exemple concret de bout en bout** (*working example*).
   - **Alignement strict Titre–Expériences** : ne jamais inclure dans le titre ou l'abstract une propriété (`on-device`, etc.) qui ne fait pas l'objet d'une expérience directe dans le papier (*« Remove on device from title and paper if you have. There are no experiments on that »*).
   - **Rigueur des Baselines & Abstraction Algorithmique** : optimiser soigneusement les hyperparamètres des baselines pour atteindre les scores attendus de la littérature (*« otherwise there is the risk they will say we didn't do a correct job »*), et abstraire les algorithmes présentés dans le papier en supprimant toute constante arbitraire codée en dur (ex. `100`).
6. **Écrire l'Abstract et l'Introduction dès le Jour 1 & Cibler une Conférence par ses Meilleurs Papiers (Directive Prof. Michalis Vlachos, 19/12/2025)** : Rédiger l'Abstract et l'Introduction dès le démarrage du projet (ce que l'on veut faire, pourquoi on le fait et comment cela s'inscrit dans le discours scientifique ne changent pas, même si l'algorithme ou les résultats évoluent), et choisir/positionner la conférence cible en analysant les meilleurs articles (*best papers*) des éditions précédentes plutôt que le seul appel à communications générique.
7. **Pensée Originale en Anglais Paragraphe par Paragraphe (Directive Prof. Michalis Vlachos, 20/10/2026)** : Structurer l'argumentation directement en anglais simple (*plain English*), paragraphe par paragraphe, afin que la réécriture préserve strictement le fil de pensée (*train of thought*) de l'auteur humain plutôt qu'une trame générique de LLM ou une traduction depuis le français.
8. **Continuité Notionnelle Stricte — Zéro Notion ou Indice Sorti du Chapeau (Directive Henri Jamet, 20/10/2026)** : Ne jamais employer un concept, un mécanisme, un sous-groupe (`Cohort 1`, `Cohort 2`) ou une variable ($N_2 = 25$ sans avoir préalablement posé $N_1 = 25$ et $N = N_1 + N_2 = 50$) avant de l'avoir introduit et défini dans le fil logique. Dans une introduction, motiver d'abord le problème et la nécessité d'un cadre expérimental unifié, dégager ensuite de l'état de l'art les grands piliers architecturaux et introduire explicitement leurs abréviations (*« Throughout this paper, we refer to these three pillars using the following abbreviations: … »*), puis construire les questions de recherche transversales (qualité réelle produite, utilité perçue vs qualité réelle, coût et efficacité) en traitant les piliers conjointement et individuellement.
9. **Paragraphes Continus, Zéro Identifiant de Code & Zéro Hyperbole Technique (Directive Henri Jamet, 20/10/2026)** : Bannir l'empilement de micro-paragraphes de 2 à 3 lignes précédés d'un titre en gras (`\noindent\textbf{Mini-titre.}`) qui hache la lecture et trahit une génération LLM ; développer l'argumentation en vrais paragraphes continus ancrés dans la littérature (*« following the formulation of [X] »*). Exclure du texte scientifique les noms internes de fonctions ou variables du code (`SearchSources`, `ReadSourceSection`, `snake_case`) ainsi que le jargon pompeux ou pseudo-absolu (*« ensuring 100% double-blind peer evaluation »*, *« with millisecond telemetry »*, *« Structural Flattening Gate »*) : expliquer simplement les mécanismes réels (ex. rendu linéaire uniforme façon livre, évaluation à l'aveugle sans connaissance des conditions expérimentales).
10. **Pare-Feu d'Anonymisation Double-Blind** : Dans tout manuscrit soumis en double aveugle (`anonymous`), interdiction absolue de mentionner le nom de l'université (`UNIL`, `HEC Lausanne`, `HES-SO`), la ville ou un numéro de dossier éthique traçable (`CER-HEC UNIL`, `LOOP 6a0f06ef8bb73`).
11. **Rigueur Statistique, Transparence CONSORT & Honnêteté des Résultats Nuls (Directives Prof. Yash Raj Shrestha, 26/10/2026)** :
    - **Zéro pseudo-réplication & Modèles pré-enregistrés vs exploratoires** (*« Reviewers forgive an honest null far more readily than a favourable model choice »*) : dans toute évaluation multi-items (ex. 14 items notés par évaluateur sur un même artefact/cours), ne jamais traiter les items comme des observations indépendantes de l'effet de condition sans inclure l'effet aléatoire de l'artefact/cours (`(1|evaluator) + (1|course) + (1|item)` en CLMM/LMM, complété par un test de permutation au niveau de l'unité expérimentale avec correction de Holm). Distinguer explicitement dans le corps du texte (et jamais uniquement en annexe) les analyses pré-enregistrées des analyses exploratoires.
    - **Transparence CONSORT & Sensibilité des Exclusions** : dès que des observations ou évaluateurs sont exclus (*straight-lining*, temps `< 60 s`, attention checks), ne jamais reléguer l'échantillon brut en note de bas de table ; présenter dans le texte principal le flux CONSORT complet, les taux d'exclusion par bras et une analyse de sensibilité *leave-one-criterion-out*.
    - **Calibrage des Affirmations & Titres Falsifiables** : bannir des titres tout qualificatif absolu infalsifiable (*« Bias-Free »*, *« Unbiased »*) au profit de descripteurs méthodologiques exacts (*« Double-Blind »*, *« Confound-Controlled »*). Ne jamais présenter un classement interne entre variantes comme établi lorsque leurs intervalles de confiance se chevauchent : le qualifier de *suggestif*, afficher les intervalles de confiance sur chaque $\Delta$, et inclure une section **Limitations** dédiée dans le corps de l'article.

### B. Conception des Figures, Tableaux & Protocoles d'Ablation (Directives Henri Jamet, 20/10/2026)
- **Figures** : Privilégier des figures épurées, lisibles et aérées (zéro boîte de texte saturée, zéro flèche traversant des étiquettes, zéro mention redondante `(/5)` ou code interne dans les graphiques), en déportant les formules et détails méthodologiques dans la légende LaTeX `\caption{}` sous la figure. Pour un article de plateforme/système, inclure une figure montrant côte à côte les écrans principaux de l'interface (ex. studio de création et interface d'évaluation) alimentés par un cas riche exécuté localement.
- **Tableau chronologique de l'état de l'art (`Related Work`)** : Plutôt qu'un tableau comparatif biaisé d'outils commerciaux fermés/opaques, construire un tableau chronologique de la littérature (`Year & Reference` | `What Was Done` | `Remaining Limitation / Gap` | `How Our Work Addresses It`, avec la dernière ligne dédiée à notre article), en intégrant des articles récents de la conférence visée (ex. *TheWebConf / WWW*) pour inscrire directement le papier dans le discours de la communauté.
- **Tableau de matrice des conditions d'ablation** : Supprimer toute colonne textuelle redondante avec les colonnes de coches/croix ; colorer les cellules actives (`\checkmark` sur fond vert clair) et inactives (`\texttimes` sur fond rouge clair) pour une lecture immédiate, et nommer les conditions de manière symétrique par le pilier retiré (`PKG Ablated`, `MAS Ablated`, `HITL Ablated`).
- **Architecture & Protocoles d'ablation** : Présenter d'abord la modularité du système et les groupes expérimentaux (groupe complet, groupe minimal, groupes à 1 pilier retiré), puis consacrer une sous-section structurée à chaque pilier (origine dans la littérature + implémentation). Pour les questionnaires, spécifier systématiquement le nombre exact d'items (Likert, ouverts, catégoriels, attention checks) et leur recoupement analytique.

---

## 2. 🚫 Bannissement Formel des Tirets Cadratins (`—` et `--`)

Le tiret cadratin (*em-dash* `—` ou `--` en LaTeX) est le **marqueur stylistique #1 des modèles de langage contemporains**.

> [!CAUTION]
> **Cible Absolue : 0 Em-Dash dans tout document final**.
> L'utilisation de `—`, `---` ou `--` (hors tirets d'union ordinaires dans les mots composés comme *trade-off* ou *state-of-the-art* et intervalles numériques `10--20` en LaTeX) est formellement interdite.

| Structure Initiale avec Em-Dash | Remplacement Autorisé | Exemple |
|---|---|---|
| **Aparté / Précision incidente** | Virgules ou Parenthèses | *« The method—developed in 2024—scales »* $\to$ *« The method (developed in 2024) scales »* |
| **Explication ou Énumération** | Deux-points (`:`) | *« We identify two bottlenecks—latency and memory »* $\to$ *« We identify two bottlenecks: latency and memory »* |
| **Rupture ou Rebond d'idée** | Deux phrases indépendantes | *« The model converged—however, variance remained high »* $\to$ *« The model converged. However, variance remained high »* |
| **Opposition ou Concession** | Conjonction explicite (*while*, *whereas*) | *« Strategy A minimizes cost—Strategy B maximizes speed »* $\to$ *« Strategy A minimizes cost, whereas Strategy B maximizes speed »* |

---

## 3. 🎯 Élimination Déterministe des Clichés IA (La Table des 112 Mots)

Issus du corpus canonique [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing), ces 112 termes et constructions typiques doivent être systématiquement purgés et remplacés par du vocabulaire technique précis.

### A. Tier 1A — Marqueurs de Fréquence IA (Remplacement Immédiat & Obligatoire)

| Mot ou Expression Proscrit | Remplacement Recommandé |
|---|---|
| **delve / delve into** | explore, analyze, examine, inspect, investigate |
| **tapestry** | (décrire la complexité ou la diversité réelle : structure, composition) |
| **landscape** *(métaphorique)* | field, domain, environment, setting, context |
| **realm** | area, field, domain |
| **paradigm** *(galvaudé)* | model, approach, framework, formulation |
| **embark / embark on** | begin, start, undertake |
| **beacon** *(métaphorique)* | reference, baseline, example |
| **testament to** | demonstrates, evidences, confirms, shows |
| **robust / robustness** *(non technique)* | resilient, stable, fault-tolerant, verified (si non-statistique) |
| **comprehensive** | thorough, complete, exhaustive, systematic |
| **cutting-edge** | recent, advanced, state-of-the-art |
| **leverage** *(verbe)* | use, employ, apply, exploit |
| **pivotal** | critical, essential, primary, key |
| **underscores** | highlights, demonstrates, reveals |
| **meticulous / meticulously** | careful, systematic, rigorous, detailed |
| **seamless / seamlessly** | direct, integrated, without interruption |
| **game-changer / game-changing** | (décrire le changement précis) |
| **watershed moment** | turning point, transition |
| **nestled** | situated, located, configured in |
| **vibrant / thriving** | active, expanding, growing |
| **showcasing** | demonstrating, illustrating, presenting |
| **deep dive / dive into** | detailed analysis, systematic investigation |
| **unpack / unpacking** | analyze, break down, formalize |
| **intricate / intricacies** | complex details, specific constraints |
| **ever-evolving** | dynamic, iterative, shifting |
| **holistic / holistically** | integrated, unified, global |
| **actionable** | concrete, directly applicable, operational |
| **learnings** | findings, insights, empirical observations |
| **synergy / synergies** | joint performance, combined effect, interaction |
| **interplay** | interaction, coupling, mutual influence |
| **embrace** *(métaphorique)* | adopt, integrate, incorporate |
| **load-bearing** *(métaphorique)* | critical dependency, core assumption |

### B. Tier 1B — Clichés de Remplissage & Fausse Formalité

| Mot ou Expression Proscrit | Remplacement Épuré |
|---|---|
| **utilize / utilization** | use |
| **in order to** | to |
| **due to the fact that** | because, since |
| **serves as** | is, acts as |
| **features** *(verbe gonflé)* | includes, incorporates, contains |
| **boasts** | achieves, reports, demonstrates |
| **commence** | start, initiate |
| **ascertain** | determine, verify, quantify |
| **endeavor** | attempt, effort |

### C. Tier 2 — Mots Suspects en Groupe (Interdits dès 2+ par Paragraphe)

| Terme | Alternatives Précises |
|---|---|
| **harness** | use, apply, channel |
| **navigate** | handle, resolve, manage |
| **foster** | encourage, promote, facilitate |
| **elevate** | increase, enhance, improve |
| **unleash** | enable, unlock, release |
| **streamline** | simplify, accelerate, optimize |
| **empower** | allow, enable, permit |
| **bolster** | support, reinforce, strengthen |
| **spearhead** | lead, direct, conduct |
| **resonate with** | align with, match, correspond to |
| **revolutionize** | transform, replace, overhaul |
| **underpin / underpinnings** | support, foundation, basis |
| **nuanced** | subtle, specific, detailed |
| **crucial** | important, necessary, required |
| **multifaceted** | composite, heterogeneous, multi-component |
| **ecosystem** *(métaphorique)* | framework, platform, environment |
| **myriad / plethora** | multiple, numerous, extensive set of |
| **encompass** | include, cover, span |
| **catalyze** | trigger, initiate, speed up |
| **reimagine** | redesign, reconsider, reformulate |
| **galvanize** | motivate, drive |
| **augment** | supplement, expand, extend |
| **illuminate / elucidate** | clarify, explain, detail |
| **juxtapose** | compare, contrast |
| **cornerstone / paramount** | foundational / primary, central |
| **nascent / burgeoning** | emerging, early-stage |
| **overarching** | primary, central, principal |

### D. Connecteurs Mécaniques & Transitions Biaisées
- **Bannir les adverbes mécaniques de début de phrase** : *Moreover*, *Furthermore*, *Additionally*, *Notably*, *Importantly* (restructurer la syntaxe pour rendre le lien logique évident, ou utiliser *Also*, *In addition*, ou relier par coordination *and*, *while*).
- **Éliminer les ouvertures d'ère** : *« In today's landscape »*, *« In an era of rapid AI advancement »*.
- **Supprimer les contrastes binaires théâtraux** : *« It is not merely X, but Y »*, *« Rather than doing X, we do Y »*. Énoncer directement ce que le système fait.

---

## 4. 🔬 Pipeline Canonique en 4 Étapes : `avoid-ai-writing` + `stealth_rewriter.py` (`bfloat16`) + Chirurgie `.tex`

Toute rédaction ou révision d'un passage scientifique suit ces 4 étapes :

1. **Étape 1 — Fond Brut & Diagnostic `avoid-ai-writing` (`< 0,5 s`)** :
   - Rédiger en anglais simple (*plain English*) axé sur l'interprétation causale, sans chiffres redondants dans la prose.
   - Exécuter le détecteur déterministe :
     ```powershell
     node "c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\avoid-ai-writing\skills\ai-writing-detector\scripts\detect.js" --file "<fichier.tex>" --context technical
     ```
2. **Étape 2 — Érosion Statistique [`stealth_rewriter.py`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/stealth_rewriter.py) (`bfloat16` natif) & Scalpel Lexical** :
   - Pour éliminer la signature RLHF et garantir un verdict `HUMAN_ONLY` ($> 95\,\%$ Human sur GPTZero `4.1o`), passer tout nouveau passage par `stealth_rewriter.py` (`Qwen/Qwen3-4B-Instruct-2507` + adaptateurs `suraj-ranganath/StealthRL` GRPO et `akhaliq/open-humanizer-4b` SFT en `bfloat16` natif dès $\ge 7,5\text{ GiB}$ VRAM) :
     ```powershell
     python "c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\stealth_rewriter.py" "<texte_ou_fichier>"
     ```
   - **Règles d'Or Post-StealthRL (Zéro Encodeur RoBERTa/DeBERTa, Zéro Flag `--fast`)** :
     * Les classifieurs RoBERTa/DeBERTa (`ai_detector.py`) et tout flag `--fast` sont proscrits (*RoBERTa AUROC anomaly*, `arXiv:2602.08934`).
     * **Scalpel Lexical Post-StealthRL** : **INTERDICTION FORMELLE de reformuler une phrase entière après `stealth_rewriter.py`**. Effectuer uniquement des remplacements lexicaux ciblés de 1 à 3 mots pour restaurer la terminologie technique exacte ou corriger un chiffre altéré, en conservant intacte la charpente syntaxique et la burstiness ($\text{CV} \ge 0,45$, zéro clause participiale finale `, -ing...`).
3. **Étape 3 — Validation de Préservation & Linter de Style (`< 0,5 s`)** :
   ```powershell
   node "c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\avoid-ai-writing\detector\validate.js" "<avant.tex>" "<apres.tex>"
   node "c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\avoid-ai-writing\scripts\check-style.js" "<apres.tex>" --config technical
   ```
   *(Vérifie que les formules `$...$`, `\[...\]`, `\cite{...}`, `\ref{...}` sont intactes, qu'aucun `residual-grew` n'apparaît et qu'il y a 0 tiret cadratin).*
4. **Étape 4 — Insertion Strictement Chirurgicale Bloc par Bloc (`replace_file_content` / `edit_file`) & Recompilation PDF** :
   - **INTERDICTION ABSOLUE D'ÉCRASEMENT GLOBAL** : Ne jamais réécrire ni écraser un fichier `.tex`, `.bib` ou `.sty` complet avec `write_to_file` (`Overwrite: true`). Opérer exclusivement bloc par bloc via `edit_file` (`replace_file_content`).
   - **Recompilation Fraîche Obligatoire** : Après tout `git pull` ou édition LaTeX, recompiler systématiquement (`pdflatex` ou `latexmk`, code retour 0) avant tout audit de pagination ou de rendu.

---

## 5. 🤝 Synchronisation Exclusivement via Overleaf & Cycle `doc-version`

> [!IMPORTANT]
> **EXCLUSIVITÉ ABSOLUE D'OVERLEAF POUR TOUS LES PAPIERS (ZÉRO REPO GITHUB MIROIR)** *(décision d'Henri, 21/10/2026)* :
> - Pour **tous les projets d'articles scientifiques**, la synchronisation Git du manuscrit (`paper/`) passe **uniquement et exclusivement par le dépôt Git Overleaf** (`origin` = `https://git.overleaf.com/<project_id>`).
> - Il est **strictement interdit** d'utiliser, de configurer ou de pousser vers un dépôt GitHub dédié au papier (tel qu'un ancien repo `*-paper.git`). Overleaf est l'unique remote Git du papier.
> - **Préservation Prioritaire des Co-Auteurs** (Pamela Delgado, Stergios, James, Isna, Yash Raj Shrestha) : leurs modifications sont strictement prioritaires (zéro `git push -f`, zéro arbitrage aveugle `--ours`). En cas de conflit lors du rebase, concilier soigneusement les deux apports sans perte d'information.

### Versioning Déclaratif & Projection d'Artéfact de Diff (`doc-version`)
- **Règle de Restitution Obligatoire (Brain vs Obsidian) & Double Consultation Diff + PDF** : Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain (`file:///<appDataDir>/brain/<conversation-id>/<nom>.md`) en tête de réponse dans le chat. Ne **JAMAIS** partager le lien de la note miroir Obsidian (`papers/<nom>.md`). Pour tout fichier `.tex`, l'artéfact de diff généré par `doc-version` intègre automatiquement en haut de page (sur la ligne `📄 **Fichier Source**`) le lien `📕 **PDF Compilé** : [<nom>.pdf](file:///...)` vers le PDF compilé afin qu'Henri puisse inspecter et commenter à la fois les diffs et le rendu PDF natif dans Antigravity.
- **Exécution via `mcp-cli` (`doc-version`) ou CLI local [`doc_version_cli.py`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/doc_version_cli.py)** (zéro simulation manuelle de diff via `write_to_file`) :
  1. **Synchronisation amont** : `mcp-cli call doc-version record_git_pull_event '{"repo_path": "paper", "autostash": true}'`
  2. **Snapshot baseline avant retouche** : `mcp-cli call doc-version commit_document '{"target": "paper/main.tex", "message": "Snapshot baseline", "author": "collaborateur/henri"}'`
  3. **Snapshot agent après retouche chirurgicale** : `mcp-cli call doc-version commit_document '{"target": "paper/main.tex", "message": "Révision agent", "author": "agent"}'`
  4. **Génération de l'artéfact de diff dans `brain/`** :
     ```powershell
     mcp-cli call doc-version get_diff_artifact '{"target": "paper/main.tex", "diff_explanation": "<explication>", "brain_dir": "C:/Users/Jamet/.gemini/antigravity/brain/<conversation-id>"}'
     # Ou directement via le script CLI moteur :
     python "c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\doc_version_cli.py" diff --target "paper/main.tex" --explanation "<motif>" --content-file "<fichier_retouche>" --brain-dir "<appDataDir>/brain/<id>" --artifact-name "<nom>.md"
     ```
  5. **Rollback atomique si besoin** : `mcp-cli call doc-version restore_commit '{"commit_id": "<id>", "target": "paper/main.tex"}'`

---

## 6. 📋 Quelle Est la Checklist de Validation Avant Restitution ?

- [ ] **Posture Senior & Zéro Chiffre Redondant dans la Prose** : Zéro buzzword, prose focalisée sur l'interprétation causale (`see Table X`, `Figure Y`), paragraphes continus sans mini-titres en gras ni identifiants de code.
- [ ] **Pare-Feu Double-Blind & `.bib` Vérifié** : Zéro mention d'institution traçable en mode `anonymous` ; `.bib` vérifié sur `https://refscheck.ch/`.
- [ ] **Tirets Cadratins & 112 Mots Clichés** : 0 em-dash (`—`, `--`, `---`), 0 mot du Tier 1A / Tier 1B, 0 cluster du Tier 2, 0 connecteur mécanique de début de phrase.
- [ ] **Suite `avoid-ai-writing` (`< 0,5 s`) + `stealth_rewriter.py` (`bfloat16`)** : `detect.js`, `validate.js` (`PASS — preservation checks clear`) et `check-style.js` validés ; scalpel lexical respecté.
- [ ] **Édition Chirurgicale, Compilation PDF & Push Overleaf** : Modification via `edit_file`, compilation `pdflatex` sans erreur, et synchronisation poussée sur Overleaf (`https://git.overleaf.com/...`).
