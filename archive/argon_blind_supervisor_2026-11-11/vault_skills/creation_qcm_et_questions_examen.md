---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags:
  - skill
  - enseignement
  - docimologie
  - qcm
  - examens
aliases:
  - Conception Docimologique de QCM & Questions Ouvertes
  - quiz-question-creator
---

# Conception Docimologique SOTA de QCM & Questions Ouvertes (`quiz-question-creator`)

Ce skill encadre la conception, le tri calendaire, la labellisation (`Tags:`) et le durcissement de questions à choix multiples (QCM / MCQs) et de questions ouvertes pour **tout type d'évaluation ou d'examen** (cours universitaires, contrôles continus, certifications professionnelles, questionnaires interactifs Wooclap, banques Moodle GIFT/XML ou auto-évaluations), quel que soit le domaine ou l'année.

---

## 🛑 1. Garde-Fou Absolu : Modèle `inherit` Exclusif & Approbation Unitaire Préalable (Hard Gate)

> [!IMPORTANT]
> **MODÈLE `inherit` OBLIGATOIRE POUR TOUTE RÉDACTION OU RETOUCHE DE QUESTIONS (`Model: 'inherit'`)**
> Comme tout contenu textuel profond où le texte porte l'essentiel de la valeur pédagogique et s'adresse directement à des êtres humains, **100 % de la conception, de la rédaction et de la retouche des QCM, des distracteurs, des justifications et des questions ouvertes DOIT être effectuée par un agent en `Model: 'inherit'`** (le superviseur ou un exécutant lancé avec `Model: 'inherit'`). Il est **strictement interdit** de déléguer la rédaction de questions d'examen à un modèle léger (`flash`). Seuls l'extraction de diapositives, les vérifications statistiques par script et la génération mécanique de fichiers relèvent de `flash`.

> [!CAUTION]
> **INTERDICTION D'ÉCRITURE DIRECTE EN PRODUCTION SANS VALIDATION QUESTION PAR QUESTION**
> 1. Toute nouvelle question ou toute réécriture/correction d'une question existante DOIT d'abord être soumise à Henri dans un **artefact de révision interactif dédié** (`<appDataDir>/brain/<conversation-id>/propositions_questions_<sujet>.md` avec `RequestFeedback: true`, synchronisé avec `notes/Propositions Questions <Sujet>.md`).
> 2. Il est **strictement interdit** d'insérer, de modifier ou de committer une question directement dans les fichiers de production d'un dépôt (`sample_quiz.md`, `real_quiz_*.md`, fichiers `.gift`/`.xml`) ou sur une plateforme en ligne (Moodle, Wooclap) tant qu'Henri n'a pas **approuvé explicitement chaque question une à une**.
> 3. Pour chaque question présentée dans le document de révision, afficher systématiquement :
>    - L'identifiant, le statut (`[À VALIDER]`, `[RECONÇUE / DURCIE]`, `[VALIDÉE]`) et les labels du module (`Tags: [...]`).
>    - L'ancre de source exacte dans le support de référence (`Nom explicite du Cours ou de l'Atelier + fichier PDF/MD + numéro exact de slide, page ou section`).
>    - Le texte complet (`Scenario:`, `Question:`, options `A)` à `D)`, `Correct Answer:`).
>    - Le champ **`Justification:`** structuré avec une puce par option (`✅ Pourquoi X est exacte` / `❌ Pourquoi Y est fausse`), rédigé **pour les apprenants** : chaque puce nomme explicitement **le cours ou l'activité ET la diapositive/section** (ex. *« Dans le Cours 2 (`Lec2-genAI4Business.pdf`, diapositive 48)... »* — ne jamais écrire seulement *« La diapositive 48... »* sans préciser de quel cours il s'agit) et explique clairement **pourquoi la bonne réponse est vraie ET pourquoi chacune des 3 autres options est fausse**. Ne JAMAIS mettre de commentaires méta anti-biais IA dans l'explication destinée aux étudiants.
>    - Dans l'export Moodle GIFT (`####[html]`), préserver ce formatage aéré et lisible avec des sauts de ligne HTML `<br>` et les puces `✅` / `❌` (ainsi qu'un `<br><br>` entre le `Scenario:` et la `Question:` dans l'énoncé), afin d'éviter tout pavé monolithique illisible dans l'encadré orange de correction Moodle.
>    - Contrôle automatique de langue, de ponctuation et d'encodage : vérifier par script qu'aucun caractère d'un autre alphabet (`[а-яА-Я\u4e00-\u9fff]`) ni **aucun tiret cadratin (`—`) ou demi-cadratin (`–`)** ne figure dans l'énoncé, les options ou la justification.

---

## 🔬 2. Fondements Scientifiques & État de l'Art Docimologique

La génération naïve de QCM par LLM souffre de défauts docimologiques systématiques (*Item Writing Flaws* — IWFs) qui introduisent une variance non pertinente au construit (*Construct-Irrelevant Variance* — CIV) et permettent aux candidats (ou aux LLMs) de deviner la bonne réponse par heuristique superficielle (*test-wiseness*) :

1. **Taxonomie de Haladyna, Downing & Rodriguez (2002)** (*Applied Measurement in Education*, 31 règles validées) & **Downing (2005)** (*Advances in Health Sciences Education*) :
   - Les items violant les règles d'écriture (indices grammaticaux, option cible plus longue ou plus qualifiée, distracteurs absurdes, négations non mises en évidence) faussent le taux de réussite jusqu'à 15 points de pourcentage et pénalisent les candidats maîtrisant le fond.
2. **Homogénéité structurelle des options (Meyers et al., 2007)** (*Applied Measurement in Education*) :
   - Structurer les distracteurs avec une syntaxe, un niveau d'abstraction et une granularité strictement parallèles à la bonne réponse augmente significativement la difficulté réelle de l'item ($+0.12$) et son pouvoir discriminant.
3. **Distracteurs fondés sur les conceptions erronées (*Misconception-Driven Distractors*)** (**Arif et al., 2024** ; **Grévisse et al., 2024** ; **Feng et al., 2024** ; **Zengaffinen et al., 2026** ; **Tian et al., 2026 — ReQUESTA**) :
   - 57 % des QCM générés en zero-shot par LLM contiennent au moins un distracteur implausible (Arif et al., 2024).
   - Un distracteur de niveau avancé ne s'écrit JAMAIS en inventant un terme fantaisiste : il se construit par **ingénierie inverse d'une erreur de raisonnement précise** (confusion entre deux mécanismes adjacents du programme, inversion cause/conséquence, application d'une solution valide dans un contexte où une contrainte du scénario la rend inopérante).
4. **Vulnérabilité aux biais de sélection et de longueur des LLMs (**Zheng et al., 2023** ; **Zhao et al., 2025 — EMNLP** ; **Bonifazi et al., 2026 — GradQuiz**)** :
   - Sans contrainte explicite, les LLMs présentent un biais massif en faveur de l'option `A` en génération, et allongent ou sur-qualifient la bonne réponse pour se prémunir des cas limites.

---

## ⚖️ 3. Les 6 Invariants Anti-Biais Obligatoires (Protocole Jamet)

Chaque question créée ou révisée DOIT respecter simultanément ces 6 invariants :

### Invariant 1 — Équilibre strict de la position de la bonne réponse (`Position Balance`)
- **Interdiction du biais vers `A`** : Ne jamais placer la bonne réponse par défaut en première position (`A)`). *(Exemple historique à ne jamais reproduire : 40 questions sur 40 avec `Correct Answer: A` dans un fichier source).*
- **Répartition uniforme dès le Markdown source** : Sur un lot de $N$ questions, chacune des lettres `A`, `B`, `C`, `D` doit représenter **$25\% \pm 1$ question** des bonnes réponses dans le fichier source lui-même (même si la plateforme d'examen mélange ensuite les options, imposer cet équilibre à la source élimine le biais de position du LLM), avec au maximum 2 occurrences consécutives de la même lettre.

### Invariant 2 — Égalisation stricte des longueurs (`Length Parity`)
- **Interdiction de la bonne réponse la plus longue** : Les LLMs tendent à faire de la bonne réponse l'option la plus longue et la plus détaillée.
- **Plafond de dispersion intra-question** : Au sein d'une même question, l'écart de longueur (en nombre de mots ET en nombre de caractères) entre l'option la plus courte et l'option la plus longue ne doit pas excéder **$\pm 15\%$** (cible : **$\pm 10\%$**).
- **Contrôle statistique global** :
  - Le rang moyen de longueur de la bonne réponse sur l'ensemble de l'examen ($1.0 = \text{toujours la plus longue}$, $4.0 = \text{toujours la plus courte}$) DOIT se situer dans **$[2.30, 2.70]$** (cible idéale : **$2.50$**).
  - La bonne réponse ne doit être l'option la plus longue (rang 1) dans pas plus de **25 %** des questions.

### Invariant 3 — Symétrie typographique, grammaticale, zéro tiret cadratin et zéro parenthèse isolée (`Syntactic & Punctuation Symmetry`)
- **Zéro tiret cadratin (`—`) ou demi-cadratin (`–`)** : Bannis dans l'intégralité des énoncés (`Scenario:`, `Question:`), des options `A)`–`D)`, des questions ouvertes et des justifications. Utiliser des virgules, des deux-points ou des propositions subordonnées fluides.
- **Zéro parenthèse ou précision exclusive sur la clé** : Il est **interdit** que la bonne réponse contienne des parenthèses explicatives `(e.g., ...)`, des incises entre tirets ou deux-points qualificatifs si les 3 distracteurs n'en contiennent pas exactement au même format.
  - *Règle du `0/4` ou `4/4`* : Par défaut, viser **zéro parenthèse (`0/4`)** dans les options. Si une structure particulière (ex. mention du rôle d'aiguillage d'un nœud) est présente dans la bonne réponse, la décliner symétriquement dans les distracteurs pour ne donner aucun indice de surface.
- **Zéro modificateur d'atténuation asymétrique (*Hedging vs Absolutes*) & Zéro clause privative auto-sabotante (`No "Without / Sans" Self-Sabotage in Distractors`)** :
  - Ne jamais glisser `typically`, `generally`, `often`, `can help` uniquement dans la bonne réponse.
  - Ne jamais glisser `always`, `never`, `completely`, `exclusively`, `guarantees 100%` uniquement dans les distracteurs.
  - **Interdiction absolue des clauses privatives ou péjoratives qui amoindrissent un distracteur** : Ne jamais ajouter dans un distracteur « sans faire X » (`without...`, `ignoring...`, `by omitting...`, `sans schéma de sortie ni exemples`, `sans regarder...`) ni un qualificatif auto-disqualifiant (`anormalement`, `aléatoirement`, `aveuglément`, `unconstrained`, `naive`) qui révèle immédiatement que ce n'est pas le bon comportement (*ex. réel 15/10/2026 : « avec une température élevée sans schéma de sortie ni exemples » — équivalent à écrire « Je conduis anormalement vite, sans regarder dans mon rétroviseur »*). Chaque distracteur doit être formulé de manière **100 % affirmative et constructive**, en proposant positivement une architecture, un mécanisme ou une stratégie alternative crédible.
- **Zéro écho lexical (*Clang Association*) & Zéro fuite d'indice inter-questions (`No Cross-Question Clue Leakage`)** :
  - Un mot rare du `Scenario` ou de la `Question` ne doit pas se retrouver uniquement dans la bonne réponse.
  - **Étanchéité inter-questions stricte** : L'énoncé (`Scenario:` ou `Question:`) d'une question $Q_j$ ne doit **JAMAIS** affirmer ou présupposer un fait qui donne la réponse ou élimine un distracteur d'une autre question $Q_i$ du même quiz (*ex. réel 19/10/2026 : écrire dans le scénario de `Q1_03` que le pré-entraînement « traite des phrases brutes non annotées », ce qui permettait d'éliminer immédiatement le distracteur `B` de `Q1_02` affirmant que le pré-entraînement exige des phrases annotées manuellement par des experts*).
- **Zéro valeur numérique arbitraire dans les distracteurs (`No Arbitrary Numbers in Distractors`)** : Ne jamais inventer de nombres précis dans les distracteurs (« cinquante contrats », « dix mille jetons », « trois compartiments »), car cette fausse spécificité signale immédiatement un distracteur fabriqué.

### Invariant 4 — Unicité objective de la clé, Scénarios Décisionnels Créatifs & Haute plausibilité des distracteurs (`Single Indisputable Key`)
- **Une seule réponse défendable à 100 %** : La bonne réponse doit être **objectivement, rigoureusement et sans contestation possible la SEULE réponse vraie** au regard de la matière évaluée et du scénario posé. Aucun candidat de bonne foi maîtrisant le sujet ne doit pouvoir défendre un distracteur comme « partiellement vrai ».
- **Mises en situation décisionnelles créatives vs. reformulation passive du scénario (`No Scenario Paraphrasing / No Helping Illustrations`)** :
  - Il est **interdit** de rédiger des questions du type *« Voici un scénario détaillé ; sélectionne parmi ces 4 propositions la reformulation savante de ce scénario »*.
  - Le scénario ne doit jamais être une « illustration aidante » qui donne déjà la direction de la réponse (*ex. réel 15/10/2026 : décrire dans le scénario que « 80 % des revenus venaient de 500 best-sellers et les titres de niche ne se vendaient pas », ce qui fait immédiatement deviner que toute option n'allant pas dans le sens d'une plus grande couverture du catalogue est un distracteur*).
  - Le scénario doit être une **mise en situation opérationnelle ouverte faisant partie intégrante du problème à résoudre**, obligeant le candidat à **faire preuve de raisonnement et de créativité à partir des concepts étudiés** (concevoir une architecture, arbitrer entre deux stratégies, anticiper un effet pervers non annoncé dans l'énoncé, ou diagnostiquer une défaillance à partir d'observations brutes neutres).
- **Zéro hors-sujet ni contradiction logique avec l'énoncé (`Goal-Aligned Distractors`)** : Aucun distracteur ne doit être éliminable par simple lecture logique sans connaître la matière, soit parce qu'il contredit frontalement le scénario, soit parce qu'il traite un problème hors-sujet.
- **Protocole de construction des 3 distracteurs plausibles (tous affirmatifs et alignés sur le problème posé)** :
  Chaque distracteur doit proposer **positivement** une solution qui prétend résoudre **exactement le problème du scénario** avec un ton rigoureux (sans jamais utiliser « sans... / without... ») :
  1. **Distracteur $D_1$ (Inversion architecturale / Confusion de couche ou de concept adjacent)** : Attribue affirmativement à un concept ou composant $X$ du programme la fonction exacte d'un concept ou composant adjacent $Y$.
  2. **Distracteur $D_2$ (Violation d'une contrainte implicite du cas)** : Propose affirmativement une méthode réelle du programme qui cible le même objectif général mais échoue face aux contraintes spécifiques du cas posé.
  3. **Distracteur $D_3$ (Mécanisme pseudo-technique plausible ou compromis inversé)** : Soit inverse le sens d'un compromis théorique ou empirique étudié, soit formule affirmativement un **mécanisme pseudo-technique crédible qui prétend résoudre exactement le symptôme décrit** mais est scientifiquement ou techniquement fallacieux.

### Invariant 5 — Cadrage pédagogique : Compréhension conceptuelle et appliquée (Zéro par cœur superficiel)
- **Strictement interdits dans l'énoncé (`Scenario:` ou `Question:`)** :
  - **Toute mention de numéro de cours, de séance, de conférence ou de slide** : Ne jamais écrire « selon le cours 2 », « dans la séance 4 », « sur la slide 32 » dans la question posée au candidat. Ces ancres appartiennent exclusivement aux champs `Source:` et `Justification:`.
  - Définitions mot à mot d'acronymes triviaux ou questions de mémorisation purement déclarative (dates secondaires, syntaxe de clic d'interface de mémoire, constantes arbitraires).
- **Cibles prioritaires (Niveaux Application, Analyse et Évaluation de la taxonomie de Bloom)** :
  - Privilégier systématiquement le **diagnostic de situation**, l'**arbitrage architectural ou stratégique**, l'**analyse de compromis (*trade-offs*)** et le **transfert des mécanismes vus en cours ou en travaux pratiques** vers un cas inédit.

### Invariant 6 — Labellisation par Module/Séance (`Tags:`), Justification Structurée (`✅`/`❌`) & Pare-Feu Calendaire
1. **Taxonomie dynamique par cours/examen et pare-feu calendaire** :
   - Avant de générer ou réviser des questions, établir la liste des **tags de modules/séances** du programme cible et la **date limite des matières évaluées**.
   - Vérifier qu'aucune question d'une épreuve intermédiaire ne mobilise un concept enseigné dans une séance ultérieure.
2. **Citation explicite du Cours ou de l'Activité dans chaque Justification** :
   - Dans chaque justification (`✅ Pourquoi X est exacte` / `❌ Pourquoi Y est fausse`), **toujours nommer explicitement le numéro et le titre du Cours ou de l'Atelier en plus du numéro de diapositive ou de section** (ex. *« Dans le Cours 2 (GenAI for Business II, `Lec2-genAI4Business.pdf`, diapositive 48)... »* en FR, et *« In Lecture 2 (GenAI for Business II, `Lec2-genAI4Business.pdf`, Slide 48)... »* en EN). Ne jamais écrire seulement *« La diapositive 48... »* ou *« Slide 48... »*.
3. **Formatage multi-lignes lisible dans Moodle GIFT (`####[html]`)** :
   - Dans le fichier `.gift` généré pour Moodle, l'encadré général de feedback (`####`) doit impérativement utiliser des retours à la ligne HTML `<br>` avec une puce par option (`✅` pour la bonne réponse, `❌` pour chacun des 3 distracteurs), et l'énoncé doit séparer `Scenario:` et `Question:` par `<br><br>`.

---

## 📝 4. Conception des Questions Ouvertes (Études de Cas & Interventions Invitées)

> [!IMPORTANT]
> **LES 4 RÈGLES D'OR DES QUESTIONS OUVERTES (ZÉRO DÉVOILEMENT DU COURS & SCÉNARIO UTILE)**
> 1. **Un scénario opérationnel concret et indispensable (jamais d'habillage artificiel)** :
>    - *Anti-pattern banni* : Mettre en scène deux directeurs en réunion qui récitent deux thèses philosophiques abstraites. Un tel contexte n'apporte rien et rallonge artificiellement le texte.
>    - *Exigence* : Le scénario doit présenter un **cas concret d'entreprise ou d'ingénierie** (un incident réel, un déploiement précis, un arbitrage produit ou juridique) dont les **détails factuels servent directement de matière première** à l'analyse de l'étudiant.
> 2. **Zéro définition ni explication des concepts dans l'énoncé (`No Giving Away the Lecture`)** :
>    - Il est **formellement interdit** d'expliquer dans la question ce que signifient les concepts ou expériences de pensée cités (*ex. interdit : « en vous appuyant sur la Chambre Chinoise de Searle, où un opérateur manipule des symboles avec un livre de règles sans comprendre le chinois, ou sur le Trou de Beignet de Lewis, selon lequel un trou existe de manière relationnelle... »*).
>    - Pourquoi ? Si l'énoncé explique les concepts, (a) un étudiant qui n'est pas venu en cours peut simplement paraphraser la question sans rien connaître, et (b) un étudiant qui connaît son cours est bloqué car il ne peut plus expliquer le concept sans répéter mot pour mot l'énoncé !
>    - On se borne donc à **citer le nom des concepts ou expériences de pensée** (éventuellement accompagnés d'une très brève indication thématique de 2 à 4 mots pour situer le sujet, sans jamais en dévoiler le mécanisme ni la conclusion).
> 3. **Encourager à mobiliser « au moins un » concept ou expérience de pensée du cours (sans liste cumulative obligatoire)** :
>    - Ne jamais obliger l'étudiant à traiter cumulativement 3 ou 4 expériences de pensée en 5 à 10 minutes.
>    - Formuler la consigne de façon ouverte en proposant une liste de repères vus en cours (ex. *« To support your analysis, you are encouraged to draw on at least one concept or mechanism from the course, such as [...] »*), en vérifiant systématiquement que **100 % des notions citées figurent dans les diapositives ou supports d'ateliers du module** et qu'aucun pointeur ne livre la formule ou la réponse directe à une sous-question.
>    - **Principe de notation (/ 5 pts en quiz mixte ou / 6 pts en examen écrit intégral)** : Si un étudiant rédige une réponse cohérente de 4 à 6 phrases qui mobilise correctement **au moins un** élément pertinent du cours et l'applique avec justesse aux faits du scénario et à ses conséquences managériales, il obtient la totalité des points.
> 4. **Autonomie, zéro numéro de slide et gabarit LaTeX d'examen écrit sur table (`6 questions × 6.0 pts = 36.0 pts` en 60 min)** :
>    - Aucun numéro de slide (`Slide 18`) ni préfixe interne (`Module 1 (W2 Part 1)`) dans les titres des questions : afficher uniquement `Question N (6.0 pts) - <Titre thématique>`.
>    - Pour un examen écrit de rattrapage sur papier (60 min, livre fermé), calibrer **6 questions ouvertes sur `6.0 points` chacune (`36.0 points` au total, barème `2.0 + 2.0 + 2.0 pts`, ~10 min/question)** réparties à raison de 2 questions par page avec un grand cadre ligné de **15 lignes pointillées** par question (pour les écritures larges), **sans aucune mention du mot `OCR`**, sans bandeau `HANDWRITTEN ANSWER BOX` et sans marqueur `[END OF Q...]` en bas de cadre.

---

## 🛠️ 5. Flux d'Exécution & Migration Progressive vers la Production

Lors de toute mission de création ou de mise à jour d'un questionnaire ou d'un examen :
1. **Audit du programme, taggage et vérification visuelle des slides** : Vérifier le périmètre exact de l'évaluation, taguer chaque question par module/séance, et extraire en image PNG les diapositives sources dès qu'Henri souhaite vérifier visuellement le support d'une question.
2. **Rédaction par `Model: 'inherit'` et auto-contrôle psychométrique par script** :
   - Vérifier que les 4 options de chaque QCM ont une longueur quasi identique ($\le 15\%$ d'écart en mots et caractères), `0` parenthèse asymétrique, `0` tiret cadratin (`—`/`–`), `0` fuite d'indice inter-questions et `0` clause privative auto-sabotante (`sans`, `without`, `ignoring`, `omitting`).
   - Vérifier que la répartition des réponses `A`, `B`, `C`, `D` est équilibrée ($25\%$ chacune) et que le rang moyen de longueur de la bonne réponse est dans $[2.30, 2.70]$.
3. **Soumission dans l'artefact de révision interactif & Purge au fil de l'eau des questions validées** :
   - Présenter les questions à relire dans l'artefact Brain interactif (`<appDataDir>/brain/<id>/propositions_questions_<quiz>.md` avec `RequestFeedback: true`) et dans `notes/Propositions Questions <Nom du Quiz>.md`.
   - Dès qu'Henri valide un sous-ensemble de questions au fil de sa lecture, **transférer immédiatement ces questions validées dans les fichiers de production prêts à l'exécution** et **les supprimer de la note de relecture** afin qu'Henri ne voie plus que les questions reconçues à valider et les questions non encore lues.
4. **Compilation & Vérification finale (`.gift` multi-lignes aéré)** :
   - Exécuter le générateur et le vérificateur syntaxique pour certifier que 100 % des questions validées et leurs feedbacks multi-lignes (`✅` / `❌` avec `<br>`) sont prêts à être importés sans erreur.

---

## 🔄 Boucle d'Auto-Évolution (/learn — Rasoir d'Ockham à taille constante)

À chaque retour, rejet ou arbitrage d'Henri sur un QCM, une question ouverte ou un barème d'examen, l'agent déclenche une passe `/learn` pour ajuster les règles docimologiques, les pièges à éviter et les critères d'évaluation à taille constante sans empiler d'ajouts en bas de note.
