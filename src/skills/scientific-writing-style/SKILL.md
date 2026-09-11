---
name: scientific-writing-style
description: "Charte stylistique académique sans fard IA et suppression des tics rédactionnels."
---
# Charte Stylistique Académique & Moteur Déterministe Anti-IA (`scientific-writing-style`)

> [!IMPORTANT]
> **Source de Vérité Stylistique Universelle** : Ce skill définit la posture académique de référence et les barrières déterministes anti-IA applicables à toute rédaction scientifique (articles de conférence ACM, IEEE, AAAI, TheWebConf, revues, abstracts, lettres de réponse). Il couple la suite d'outils déterministe Node.js [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) à l'armada multi-modèles SOTA `ai_detector.py` en boucle fermée sous le **seuil strict de 10% ($P(\text{AI}) < 0.10$)**.

---

## 1. 🏛️ Posture du Chercheur Senior

L'écriture scientifique doit refléter la maturité d'un chercheur senior : rigueur, sobriété, précision factuelle et neutralité absolue.

### Principes Directeurs
1. **Objectivité & Neutralité** : Aucun superlatif non quantifié, aucune flatterie ou auto-congratulation (*« revolutionary »*, *« groundbreaking »*, *« remarkable »*, *« exceptional »* sont proscrits). La valeur d'un résultat découle de ses métriques ($N$, $p$, gain relatif, latence), pas de l'enthousiasme du texte.
2. **Précision Chirurgicale** : Bannir le vague. Remplacer les abstractions floues par des grandeurs mesurables. Ne pas dire *« our system improves performance significantly »*, mais *« our framework reduces inference latency by 34.2% across 10,000 queries »*.
3. **Économie de Mots & Attaque Directe** : Chaque mot doit être porteur d'information vérifiable. Éliminer le meublage (*padding*), les phrases de réchauffement (*« It is widely acknowledged that... »*) et les ouvertures ronflantes.
4. **Voix Active & Clarté Syntactique** : Privilégier des phrases actives et concises. Éviter l'empilement de passifs mous (*« It can be observed that the results were produced by... »* $\to$ *« The results indicate that... »*).
5. **Dénué de Sensationnalisme** : Présenter les limites avec la même rigueur et sérénité que les succès expérimentaux.

---

## 2. 🚫 Bannissement Formel des Tirets Cadratins (`—` et `--`)

Le tiret cadratin (*em-dash* `—` ou `--` en LaTeX) est identifié comme le **marqueur stylistique #1 des modèles de langage contemporains**. Dans les textes générés par LLM, l'em-dash est sur-utilisé pour insérer des apartés dramatiques, des conclusions en chute libre ou des contrastes artificiels.

> [!CAUTION]
> **Cible Absolue : 0 Em-Dash dans tout document final**.
> L'utilisation de `—`, `---` ou `--` (hors tirets d'union ordinaires dans les mots composés comme *trade-off* ou *state-of-the-art*) est formellement interdite.

### Stratégies de Remplacement Systématique :
| Structure Initiale avec Em-Dash | Remplacement Autorisé | Exemple |
|---|---|---|
| **Aparté / Précision incidente** | Virgules ou Parenthèses | *« The method—developed in 2024—scales »* $\to$ *« The method (developed in 2024) scales »* |
| **Explication ou Énumération** | Deux-points (`:`) | *« We identify two bottlenecks—latency and memory »* $\to$ *« We identify two bottlenecks: latency and memory »* |
| **Rupture ou Rebond d'idée** | Deux phrases indépendantes | *« The model converged—however, variance remained high »* $\to$ *« The model converged. However, variance remained high »* |
| **Opposition ou Concession** | Conjonction explicite (*while*, *whereas*) | *« Strategy A minimizes cost—Strategy B maximizes speed »* $\to$ *« Strategy A minimizes cost, whereas Strategy B maximizes speed »* |

---

## 3. 🎯 Élimination Déterministe des Clichés IA (La Table des 112 Mots)

Issu du corpus canonique [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing), ces 112 termes et constructions typiques doivent être systématiquement purgés et remplacés par du vocabulaire technique précis.

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
| **game-changer / game-changing** | (décrire le changement précis : *improves accuracy by X%*) |
| **watershed moment** | turning point, transition |
| **nestled** | situated, located, configured in |
| **vibrant / thriving** | active, expanding, growing |
| **showcasing** | demonstrating, illustrating, presenting |
| **deep dive / dive into** | detailed analysis, comprehensive investigation |
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
- **Bannir les adverbes mécaniques de début de phrase** : *Moreover*, *Furthermore*, *Additionally*, *Notably*, *Importantly*.
  - *Règle* : Restructurer la syntaxe pour rendre le lien logique évident, ou utiliser *Also*, *In addition*, ou relier par coordination (*and*, *while*).
- **Éliminer les ouvertures d'ère** : *« In today's landscape »*, *« In an era of rapid AI advancement »*.
- **Supprimer les contrastes binaires théâtraux** : *« It is not merely X, but Y »*, *« Rather than doing X, we do Y »*. Énoncer directement ce que le système fait.

---

## 4. ⚙️ La Suite Déterministe `avoid-ai-writing`

Pour tout passage rédigé ou révisé, l'agent ou le sous-agent exécute la suite d'outils Node.js locale située dans `antigravity/tools/avoid-ai-writing/` selon un workflow déterministe en 4 étapes :

```
[Texte Source]
      │
      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Étape 1 : Diagnostic Initial (Critic)                                  │
│ node antigravity/tools/avoid-ai-writing/skills/ai-writing-detector/     │
│      scripts/detect.js --file <draft.tex> --context technical          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Étape 2 : Réécriture Ciblée (Actor)                                    │
│ Correction unitaire des issues[] identifiées, élimination des em-dashes│
│ et variation de la longueur des phrases.                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Étape 3 : Validateur de Préservation Bloquant (Preservation Gate)       │
│ node antigravity/tools/avoid-ai-writing/detector/validate.js            │
│      <before.tex> <after.tex>                                          │
│ ➔ Rejet bloquant si residual-grew ou corruption maths/code/citations.  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Étape 4 : Contrôle de Style Mécanique (Style Linter)                   │
│ node antigravity/tools/avoid-ai-writing/scripts/check-style.js         │
│      <after.tex> --config technical                                    │
│ ➔ Vérifie : 0 tiret cadratin, parenthèses latines strictes.            │
└────────────────────────────────────────────────────────────────────────┘
```

### Commandes Précises :
1. **Diagnostic** :
   ```bash
   node antigravity/tools/avoid-ai-writing/skills/ai-writing-detector/scripts/detect.js --file <fichier.tex> --context technical
   ```
   *Extrait les `issues[]`, le score global et les phrases surlignées (`highlight_sentence_for_ai`).*

2. **Validation de Préservation** :
   ```bash
   node antigravity/tools/avoid-ai-writing/detector/validate.js <fichier_original.tex> <fichier_modifie.tex>
   ```
   *Vérifie que les blocs de code, formules mathématiques `$...$`, `\[...\]`, balises de citation `\cite{...}` et références croisées `\ref{...}` sont restés intacts.*
   *Active la barrière anti-régression `residual-grew` : la réécriture est rejetée si elle introduit plus de motifs suspects qu'elle n'en supprime.*

3. **Vérification Mécanique de Style** :
   ```bash
   node antigravity/tools/avoid-ai-writing/scripts/check-style.js <fichier_modifie.tex> --config technical
   ```
   *Contrôle que les abréviations latines (*e.g.*, *i.e.*) sont entre parenthèses et qu'aucun tiret cadratin superflu ne subsiste.*

---

## 5. 🔬 La Boucle Fermée Actor-Critic SOTA ($P(\text{AI}) < 0.10$)

Le contrôle final de conformité anti-détection repose sur le bagging multi-modèles SOTA GPU `ai_detector.py` (Gemma-4-E2B Binoculars, DeBERTa-v3 RAID, ModernBERT, RoBERTa TMR, XLM-RoBERTa, Stylométrie).

```bash
python antigravity/scripts/ai_detector.py --text "Paragraphe à auditer..."
```
Ou sur un fichier complet :
```bash
python antigravity/scripts/ai_detector.py paper/main.tex --json
```

> [!CAUTION]
> **Règle d'Or Absolue : Interdiction formelle de s'arrêter au-dessus de 10% ($P(\text{AI}) < 0.10$)**.
> Aucun texte, paragraphe ou modification ne peut être livré à Henri Jamet si son score $P(\text{AI})$ dépasse 10.0%.

### Protocole de Remédiation en cas de Score $\ge 10\%$ :
1. **Analyser la Heatmap Phrase par Phrase** : Repérer la phrase exacte marquée en `[SUSPECT]` ou `[HIGH]`.
2. **Casser la Régularité Métrique (Rhythm & Uniformity)** :
   - Si les phrases font toutes 18-22 mots, raccourcir drastiquement l'une d'elles à 5-8 mots.
   - Varier la taille des paragraphes.
3. **Diversifier le Vocabulaire (TTR)** :
   - Remplacer les abstractions génériques récurrentes par l'objet technique spécifique.
4. **Ré-exécuter l'Inférence** :
   - Boucler jusqu'à ce que $P(\text{AI}) < 0.10$.

---

## 6. 💉 Comment Intégrer les Modifications de Manière Strictement Chirurgicale ?

> [!CAUTION]
> **Interdiction Absolue d'Écrasement Global du Document :**
> - **Édition Strictement Chirurgicale Bloc par Bloc** : Toute modification sur un manuscrit ou document scientifique préexistant DOIT impérativement s'effectuer de manière strictement chirurgicale, bloc par bloc et paragraphe par paragraphe.
> - **INTERDICTION ABSOLUE D'ÉCRASEMENT GLOBAL** : Il est formellement et absolument interdit de tout réécrire d'un coup, de régénérer le fichier complet ou d'écraser le document entier avec `write_to_file` (notamment avec `Overwrite: true`).
> - **Obligation d'Opérer via `replace_file_content`** : L'intégration s'effectue EXCLUSIVEMENT via des remplacements délimités et ciblés avec `replace_file_content` (ou application locale de patch). `write_to_file` est strictement réservé à la création initiale de nouveaux fichiers.

---

## 7. 📋 Quelle Est la Checklist de Validation Avant Restitution ?

Pour tout texte académique rédigé :
- [ ] **Posture Senior** : Zéro buzzword publicitaire, ton neutre et scientifique, faits et chiffres mesurables.
- [ ] **Tirets Cadratins** : 0 em-dash (`—`, `--`, `---`). Remplacés par virgules, parenthèses ou points.
- [ ] **112 Mots Clichés** : 0 mot du Tier 1A / Tier 1B, 0 cluster du Tier 2, 0 connecteur mécanique de transition.
- [ ] **Suite avoid-ai-writing** :
  - [ ] `detect.js` exécuté (contexte `technical`).
  - [ ] `validate.js` passé avec succès (`PASS — preservation checks clear`, zéro `residual-grew`).
  - [ ] `check-style.js` vérifié sans violation dure.
- [ ] **Score SOTA `ai_detector.py`** : $P(\text{AI}) < 10.0\%$ vérifié et prouvé par les sorties de la commande.
- [ ] **Édition Strictement Chirurgicale** : Modification bloc par bloc via `replace_file_content`, aucun écrasement global via `write_to_file`.
