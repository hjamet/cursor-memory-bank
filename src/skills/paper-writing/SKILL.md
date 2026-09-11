---
name: paper-writing
description: "Rédaction scientifique, compilation LaTeX, révision chirurgicale et synchro Overleaf."
---
# 📝 Comment Rédiger et Réviser des Papiers Académiques (Paper Writing) ?

> [!IMPORTANT]
> **Rôle Canonique : Orchestrateur Technique de Projet d'Article**
> Ce skill régit l'orchestration technique, le cycle collaboratif comment-driven, la projection AST différentielle (`latex_to_markdown_artifact.py`), la synchronisation Overleaf/GitHub et la gestion automatisée des médias.
> - **Pour la Charte Stylistique & Anti-IA** : Appliquer impérativement le skill dédié [`scientific-writing-style`](file:///C:/Users/Jamet/Documents/VoiceNotes/antigravity/skills/scientific-writing-style/SKILL.md) (posture de chercheur senior, bannissement absolu des tirets cadratins `—`, suite déterministe `avoid-ai-writing` et barrière bloquante $P(\text{AI}) < 0.10$).
> - **Pour la Revue Bibliographique Amont** : Mobiliser [`literature-review`](file:///C:/Users/Jamet/Documents/VoiceNotes/antigravity/skills/literature-review/SKILL.md) (synthèse de littérature, fiches médico-légales Zotero et cartographie des baselines).

---

## 0. 🎯 Quelle est la Règle de Restitution Obligatoire du Livrable (Brain vs Obsidian) ?

> [!IMPORTANT]
> **RÈGLE D'OR DE RESTITUTION À HENRI DANS LE CHAT :**
> - **OBLIGATION ABSOLUE** : Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain (`file:///<appDataDir>/brain/<conversation-id>/<nom>.md`) en tête de réponse dans le fil de discussion Antigravity. Cet artéfact est le **SEUL et UNIQUE livrable de travail interactif** contenant l'arborescence des deltas (Tree TOC), le word-diff interactif (<ins>/<del>), les badges de conformité IA par paragraphe, le callout de conciliation et les images compilées directement visibles.
> - **INTERDICTION FORMELLE** : Ne **JAMAIS** partager ni mentionner le lien de la note Obsidian (`papers/<nom>.md`) dans le fil de discussion Antigravity. La note Obsidian est une note miroir passive interne au coffre réservée au rattachement documentaire et au graphe de connaissances ; elle ne doit jamais encombrer le chat ni être proposée comme espace de relecture interactif.

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
│ 3. Modifications Liées aux Commentaires (Pipeline en 4 Étapes)         │
│    (1) Fond Brut : Rédaction pure axée sur le fond scientifique.       │
│    (2) Style & Anti-IA : scientific-writing-style & avoid-ai-writing.  │
│    (3) Érosion StealthRL : stealth_rewriter.py & audit factualité.     │
│    (4) Insertion Chirurgicale : replace_file_content exclusif sur .tex.│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Projection Différentielle Immédiate (--diff "explication")          │
│    Exécution directe :                                                 │
│    python antigravity/scripts/latex_to_markdown_artifact.py            │
│        paper/main.tex --diff "Explication claire des changements"      │
│    (Livrable chat : EXCLUSIVEMENT le lien vers l'artéfact Brain).      │
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

#### 3. Pipeline Canonique de Rédaction & d'Humanisation en 4 Étapes
- **(a) Étape 1 (Fond Brut)** :
  * Rédaction pure axée sur le fond, la clarté et l'exactitude scientifique, les chiffres, les formules et la logique argumentative, sans fard stylistique ni artifice.
- **(b) Étape 2 (Style & Anti-IA Déterministe)** :
  * Application stricte des consignes de style ([`scientific-writing-style`](file:///C:/Users/Jamet/Documents/VoiceNotes/antigravity/skills/scientific-writing-style/SKILL.md)) et du repo `avoid-ai-writing`.
  * Le repo `avoid-ai-writing` suffit largement avec les consignes de style, sans ajouter d'autres instructions.
  * Purge impérative des clichés IA et bannissement absolu des tirets cadratins (`—`, `--`).
  * Réalisé par un sous-agent classique standard (aucune utilisation ni mention d'`independent-agents`).
- **(c) Étape 3 (Érosion Statistique StealthRL & Garde-Fou Fermé)** :
  * Exécution de l'érosion statistique neuronale :
    ```bash
    python antigravity/scripts/stealth_rewriter.py "<passage>"
    ```
    *(Modèle Qwen3-4B NF4, 90% VRAM, scoring CPU).*
  * **Validation stricte par le sous-agent** : Traque rigoureuse des hallucinations et erreurs factuelles introduites par le modèle Qwen3-4B (chiffres déformés, citations altérées, contresens).
  * **Règle d'or absolue** : **INTERDICTION FORMELLE de reformuler le texte après StealthRL**. Corriger UNIQUEMENT les erreurs factuelles ou les chiffres altérés afin de ne pas restaurer les motifs statistiques détectables par les classifieurs IA.
- **(d) Étape 4 (Insertion Chirurgicale Bloc par Bloc & Restitution)** :
  * **Édition Strictement Chirurgicale Bloc par Bloc** : Toute modification sur les sources du manuscrit (`paper/main.tex`, `.bib`, `.sty`) DOIT impérativement être effectuée de manière strictement chirurgicale, bloc par bloc et paragraphe par paragraphe.
  * **INTERDICTION ABSOLUE D'ÉCRASEMENT GLOBAL** : Il est FORMELLEMENT et ABSOLUMENT INTERDIT de tout réécrire d'un coup, de régénérer le document complet ou d'écraser le document entier avec `write_to_file` (notamment avec `Overwrite: true`).
  * **Obligation d'Opérer via `replace_file_content`** : L'intégration s'effectue EXCLUSIVEMENT via des appels ciblés à `replace_file_content` (ou application locale de patch) sur la portion exacte à modifier. `write_to_file` est strictement réservé à la création initiale de nouveaux fichiers.
  * **Projection AST & Restitution Chat** : Exécution immédiate de `python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --diff "<explication>"`. Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain (`file:///<appDataDir>/brain/<conversation-id>/<slug>.md`) en tête de réponse. INTERDICTION FORMELLE de partager ou mentionner le lien de la note Obsidian dans le fil de discussion.

#### 4. Projection Différentielle Immédiate (`--diff "<explication>"`)
- Rafraîchissement immédiat de l'artéfact Brain et de la note miroir avec le diff coloré et le callout d'explication :
  ```bash
  python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --diff "Intégration de la calibration N=500k et clarification de la Section 4.2" --brain-dir "<appDataDir>/brain/<conversation-id>"
  ```
- **Rappel Obligatoire de Restitution dans le Chat** : Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain affiché par le script (`file:///<appDataDir>/brain/<conversation-id>/<slug>.md`) en tête de réponse. INTERDICTION FORMELLE de partager ou mentionner le lien de la note Obsidian dans le fil de discussion.
- Vérifier que 100% des badges IA affichés dans l'artéfact sont verts ($\le 10\%$).

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

### 3. Invariant Strict Obligatoire (Interdiction d'Exécution sans Flag)
> [!CAUTION]
> **Interdiction Formelle du Mode sans Diff** : Le script refuse catégoriquement de s'exécuter sans `--diff "<explication>"` ou `--commit`. Tout mode par défaut sans comparaison est formellement banni pour préserver l'historique et empêcher l'écrasement silencieux des diffs.

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

---

## 6. 🚫 Pourquoi les Commandes Git Manuelles (CLI) Sont-elles Formellement Interdites ?

> [!CAUTION]
> **Interdiction Formelle des Commandes Git Manuelles (CLI)** :
> Aucun agent ne doit **JAMAIS** taper de commandes `git add`, `git commit` ou `git push` manuelles dans le terminal pour gérer le manuscrit.
> **Le script `latex_to_markdown_artifact.py` encapsule et orchestre 100% du cycle Git et Overleaf.**

### 🛠️ Quel Est le Seul et Unique Workflow Valide pour Gérer le Manuscrit ?

1. **Ancrer la Baseline (Avant Travail)** :
   ```powershell
   python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --commit "<commentaire / révision>"
   ```
   *(Le script fige la baseline Git, capture les métadonnées AST et initialise le point de repère).*

2. **Chirurgie Ciblée & Recompilation** :
   - Édition strictement chirurgicale bloc par bloc via `replace_file_content` (zéro `write_to_file` global).
   - Vérification `pdflatex` (code 0, 8 pages exactes).

3. **Diff & Synchronisation Overleaf (Après Travail)** :
   ```powershell
   python antigravity/scripts/latex_to_markdown_artifact.py paper/main.tex --diff "<explication détaillée>"
   ```
   *(Le script calcule le word-diff, pousse les révisions et régénère l'artéfact Brain prioritaire).*

