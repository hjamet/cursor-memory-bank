---
name: paper-writing
description: Méthodologie complète pour la rédaction et la révision itérative de papiers académiques via la note miroir Obsidian (papers/<nom>.md), l'édition directe des sources LaTeX, la projection de diff AST, le cycle comment-driven, la CLI simplifiée (--diff "<explication>" et --commit), l'automatisation des images et l'articulation amont avec la revue bibliographique (/literature-review).
---

# 📝 Comment Rédiger et Réviser des Papiers Académiques (Paper Writing) ?

> [!IMPORTANT]
> **Rôle Canonique : Orchestrateur Technique de Projet d'Article**
> Ce skill régit l'orchestration technique, le cycle collaboratif comment-driven, la projection AST différentielle (`latex_to_markdown_artifact.py`), la synchronisation Overleaf/GitHub et la gestion automatisée des médias.
> - **Pour la Charte Stylistique & Anti-IA** : Appliquer impérativement le skill dédié [`scientific-writing-style`](file:///C:/Users/hjamet/Documents/VoiceNotes/.agent/skills/scientific-writing-style/SKILL.md) (posture de chercheur senior, bannissement absolu des tirets cadratins `—`, suite déterministe `avoid-ai-writing` et barrière bloquante $P(\text{AI}) < 0.10$).
> - **Pour la Revue Bibliographique Amont** : Mobiliser [`literature-review`](file:///C:/Users/hjamet/Documents/VoiceNotes/.agent/skills/literature-review/SKILL.md) (synthèse de littérature, fiches médico-légales Zotero et cartographie des baselines).

---

## 1. 🔄 Le Cycle Collaboratif Déterministe (Comment-Driven Loop)

Toute modification du document académique s'inscrit rigoureusement dans la séquence déterministe suivante à 4 temps :

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Réception des Commentaires Utilisateur                              │
│    Henri commente un artéfact ou la note miroir Obsidian.             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Sécurisation par Commit Précis (--commit)                           │
│    Validation et commit de l'état actuel pour tous les endroits        │
│    commentés (ou situés avant un endroit commenté) afin de geler       │
│    la baseline validée. AUCUN commit sauvage sans commentaire !        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Modifications Liées aux Commentaires (Protocole en 3 Étapes)        │
│    (a) Premier jet exhaustif axé à 100% sur le sens et la complétude.  │
│    (b) Sous-agent de réécriture avec 'scientific-writing-style' et la  │
│        suite avoid-ai-writing en boucle jusqu'à P(AI) < 10.0%.         │
│    (c) Réintégration du texte corrigé dans le document source.         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Projection Différentielle Immédiate (--diff "explication")          │
│    Exécution directe :                                                 │
│    python antigravity/scripts/latex_to_markdown_artifact.py            │
│        paper/main.tex --diff "Explication claire des changements"      │
│    (Suppression définitive du drapeau séparé --explanation).           │
└────────────────────────────────────────────────────────────────────────┘
```

### Détail des 4 Temps :

#### 1. Réception des Commentaires Utilisateur
- **Règle d'or** : INTERDICTION FORMELLE de toute réécriture générale ou proactive sans retour préalable.
- Les retours proviennent soit de sélections contextuelles commentées par Henri dans l'artéfact de session Antigravity, soit d'annotations directes dans la note miroir Obsidian `papers/<nom_papier>.md`.

#### 2. Sécurisation par Commit Précis (`--commit`)
- **Geler la Baseline Validée** : Avant toute retouche suite à un commentaire, valider l'état actuel :
  ```bash
  python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --commit
  ```
  *(Ou avec `--line <N>` pour valider sélectivement les lignes antérieures au commentaire).*
- **Règle Zero-Trust** : Zéro commit sauvage ou anticipé sans commentaire explicite d'Henri.

#### 3. Protocole de Modification en 3 Étapes
- **(a) Premier Jet Exhaustif** : Rédiger ou structurer les éléments techniques en se concentrant à 100% sur l'exactitude scientifique, les chiffres, les formules et la logique argumentative.
- **(b) Filtrage Stylistique & Anti-IA via `scientific-writing-style`** :
  - Exécuter la suite d'outils locale `avoid-ai-writing` (`detect.js`, `validate.js`, `check-style.js`).
  - Purger impérativement les 112 clichés IA et tout tiret cadratin (`—`, `--`).
  - Auditer via `ai_detector.py` jusqu'à conformité stricte $P(\text{AI}) < 0.10$.
  - Mandatement direct de Claude Opus via `antigravity-agents run --model claude-opus-4-6 --prompt "..."` si une reformulation stylistique avancée est requise.
- **(c) Réintégration dans les Sources** : Intégration chirurgicale dans les fichiers sources (`.tex`, `.bib`).

#### 4. Projection Différentielle Immédiate (`--diff "<explication>"`)
- Rafraîchissement immédiat de la note miroir et génération du diff coloré avec le callout d'explication :
  ```bash
  python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --diff "Intégration de la calibration N=500k et clarification de la Section 4.2"
  ```
- Vérifier que 100% des badges IA affichés dans la note miroir sont verts ($\le 10\%$).

---

## 2. ⚡ CLI Simplifiée de `latex_to_markdown_artifact.py`

Le script universel de projection différentielle dispose d'une interface épurée sans paramètres redondants :

### 1. Mode Différentiel Direct (Usage Standard)
```bash
python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --diff "<explication>"
```
- L'argument passé directement à `--diff` constitue l'explication obligatoire insérée dans le callout de conciliation.
- Déclenche la comparaison AST contre la baseline Git d'Henri Jamet.
- Calcule automatiquement les deltas différentiels, surligne les ajouts/suppressions et insère les badges de conformité IA.

### 2. Mode Commit de Baseline
```bash
python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --commit
```
- Valide l'état courant comme nouvelle baseline officielle.
- Option granulaire : `--line <N>` pour geler et committer uniquement jusqu'à la ligne $N$ de la note miroir.

### 3. Mode Projection Simple (Sans Diff)
```bash
python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex
```
- Convertit le document source vers la note miroir `papers/<nom_papier>.md` sans générer de diffs ni badges IA.

---

## 3. 🖼️ Automatisation Complète des Images & Médias

Le pipeline gère automatiquement et de manière totalement transparente l'extraction et l'affichage des figures :

1. **Auto-Détection & Résolution** :
   - Analyse récursive de toutes les balises LaTeX `\includegraphics[...]{chemin/figure}`.
   - Résolution multi-chemins (extensions `.pdf`, `.png`, `.jpg`, `.svg`).
2. **Copie Automatisée vers le Coffre Obsidian** :
   - Les figures sont automatiquement copiées vers les répertoires d'attachements canoniques :
     * `papers/_attachments/<nom_du_papier>/`
     * `papers/_attachments/`
     * `_attachments/`
3. **Synchronisation avec les Sessions Brain d'Antigravity** :
   - Duplication automatique dans `<appDataDir>/brain/<conversation_id>/` pour permettre le rendu visuel instantané dans les vues d'artéfacts.
4. **Syntaxe Universelle** :
   - La note miroir générée utilise la syntaxe standard compatible Obsidian et KaTeX/Markdown, garantissant un affichage visuel immédiat sans configuration manuelle.

---

## 4. 🤝 Priorité Absolue aux Collaborateurs & Synchronisation Git/Overleaf

Le projet académique est un travail d'équipe (Stergios, James, Isna, Yash Raj Shrestha). La préservation de leurs apports est un impératif absolu.

### Règles d'Or Collaboratives :
1. **Pull-First & Autostash Systématique** :
   - À chaque exécution, le script lance un `git pull --rebase --autostash origin <branch>` pour intégrer les modifications distantes sans créer de commit de merge parasite.
2. **Préservation Prioritaire des Co-Auteurs** :
   - Les modifications faites par les collaborateurs sont **STRICTEMENT PRIORITAIRES** et ne doivent **JAMAIS être écrasées ni supprimées unilatéralement**.
   - Interdiction formelle du force push (`git push -f`) et de l'arbitrage aveugle (`--ours`).
3. **Gestion Bloquante des Conflits Git (Code de Sortie 3)** :
   - Si un conflit survient lors du rebase, le script s'interrompt immédiatement avec l'alerte rouge `🚨 [ACTION AGENT CRITIQUE : CONFLIT GIT DÉTECTÉ]`.
   - **Procédure de Résolution** :
     1. Inspecter immédiatement les fichiers signalés.
     2. Identifier précisément l'intention de la modification des collaborateurs.
     3. Concilier astucieusement notre texte et le leur afin de préserver les deux apports sans perte d'information.
     4. Finaliser le rebase (`git add . && git rebase --continue`), puis relancer `--diff`.
4. **Reporting Obligatoire dans le Chat** :
   - Formuler systématiquement à Henri un compte-rendu clair précisant les apports collaborateurs rapatriés et la conciliation effectuée.

---

## 5. 📑 Recompilation Obligatoire & Contrôle de Pagination

- **Recompilation Fraîche** : Après tout `git pull` ou édition des sources LaTeX, recompiler systématiquement le document (`pdflatex` ou `latexmk`) avant tout audit de pagination ou de rendu.
- **Interdiction Formelle d'Auditer un PDF Obsolète** : Ne jamais formuler d'avis sur la structure ou la longueur des sections en se basant sur un `.pdf` préexistant sans compilation vérifiée.
