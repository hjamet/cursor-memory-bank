---
name: paper-writing
description: "Rédaction scientifique, compilation LaTeX, révision chirurgicale et synchro Overleaf."
---
# 📝 Comment Rédiger et Réviser des Papiers Académiques (Paper Writing) ?

> [!IMPORTANT]
> **Rôle Canonique : Orchestrateur Technique de Projet d'Article**
> Ce skill régit l'orchestration technique, le cycle collaboratif comment-driven, la projection AST différentielle et le versioning déclaratif via les outils MCP doc-version (`call_mcp_tool`), la synchronisation Overleaf/GitHub et la gestion automatisée des médias.
> - **Pour la Charte Stylistique & Anti-IA** : Appliquer impérativement le skill dédié [`scientific-writing-style`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/skills/scientific-writing-style/SKILL.md) (posture de chercheur senior, bannissement absolu des tirets cadratins `—`, suite déterministe `avoid-ai-writing` et barrière bloquante $P(\text{AI}) < 0.10$).
> - **Pour la Relecture Chirurgicale & Préservation Stylistique** : Mobiliser le skill complémentaire [`draft`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md) pour le polissage scalpel de brouillons, la résolution de balises `<XXX>` et le respect strict de la voix d'Henri (seuil de rétention $\ge 90\%$).
> - **Pour la Revue Bibliographique Amont** : Mobiliser [`literature-review`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/skills/literature-review/SKILL.md) (synthèse de littérature, fiches médico-légales Zotero et cartographie des baselines).

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
│ 1. Réception des Commentaires Utilisateur & Pull Distant               │
│    Henri commente un artéfact ou la note miroir Obsidian.             │
│    Avant pull éventuel : record_git_pull_event(repo_path=...)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Sécurisation par Snapshot Baseline (commit_document)                │
│    Validation et commit de l'état actuel pour geler la baseline :      │
│    commit_document(target=..., message="...", author="collaborateur")  │
│    AUCUN commit sauvage sans commentaire !                             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Modifications Liées aux Commentaires (Pipeline en 4 Étapes)         │
│    (1) Fond Brut : Rédaction pure axée sur le fond scientifique.       │
│    (2) Style & Anti-IA : scientific-writing-style & avoid-ai-writing.  │
│    (3) Érosion StealthRL : stealth_rewriter.py & audit factualité.     │
│    (4) Insertion Chirurgicale : replace_file_content exclusif sur .tex │
│        suivi de commit_document(target=..., author="agent")            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Projection Différentielle Déclarative (get_diff_artifact)           │
│    Appel MCP :                                                         │
│    get_diff_artifact(target=..., diff_explanation=..., brain_dir=...) │
│    En cas d'erreur / rollback : restore_commit(commit_id=..., ...)    │
│    (Livrable chat : EXCLUSIVEMENT le lien vers l'artéfact Brain).      │
└────────────────────────────────────────────────────────────────────────┘
```

### Détail des 4 Temps :

#### 1. Réception des Commentaires Utilisateur
- **Règle d'or** : INTERDICTION FORMELLE de toute réécriture générale ou proactive sans retour préalable.
- Les retours proviennent soit de sélections contextuelles commentées par Henri dans l'artéfact de session Antigravity, soit d'annotations directes dans la note miroir Obsidian `papers/<nom_papier>.md`.
- **Synchronisation Amont** : En cas de modifications distantes (Overleaf/Git), consigner l'événement :
  ```python
  call_mcp_tool(
      ServerName="doc-version",
      ToolName="record_git_pull_event",
      Arguments={"repo_path": "paper", "autostash": True}
  )
  ```

#### 2. Sécurisation par Commit Précis (`commit_document`)
- **Geler la Baseline Validée** : Avant toute retouche suite à un commentaire, figer l'état actuel via l'outil MCP déclaratif :
  ```python
  call_mcp_tool(
      ServerName="doc-version",
      ToolName="commit_document",
      Arguments={
          "target": "paper/main.tex",
          "message": "Snapshot baseline",
          "author": "collaborateur/henri"
      }
  )
  ```
  *(Possibilité de spécifier `line_pivot` pour valider sélectivement les lignes antérieures au commentaire).*
- **Règle Zero-Trust** : Zéro commit sauvage ou anticipé sans commentaire explicite d'Henri.

#### 3. Pipeline Canonique de Rédaction & d'Humanisation en 4 Étapes
- **(a) Étape 1 (Fond Brut)** :
  * Rédaction pure axée sur le fond, la clarté et l'exactitude scientifique, les chiffres, les formules et la logique argumentative, sans fard stylistique ni artifice.
- **(b) Étape 2 (Style & Anti-IA Déterministe)** :
  * Application stricte des consignes de style ([`scientific-writing-style`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/skills/scientific-writing-style/SKILL.md)) et du repo `avoid-ai-writing`.
  * Le repo `avoid-ai-writing` suffit largement avec les consignes de style, sans ajouter d'autres instructions.
  * Purge impérative des clichés IA et bannissement absolu des tirets cadratins (`—`, `--`).
  * Réalisé par un sous-agent classique standard (aucune utilisation ni mention d'`independent-agents`).
- **(c) Étape 3 (Érosion Statistique StealthRL & Garde-Fou Fermé)** :
  * Exécution de l'érosion statistique neuronale :
    ```bash
    python _agents/scripts-for-skills/stealth_rewriter.py "<passage>"
    ```
    *(Modèle Qwen3-4B NF4, 90% VRAM, scoring CPU).*
  * **Validation stricte par le sous-agent** : Traque rigoureuse des hallucinations et erreurs factuelles introduites par le modèle Qwen3-4B (chiffres déformés, citations altérées, contresens).
  * **Règle d'or absolue** : **INTERDICTION FORMELLE de reformuler le texte après StealthRL**. Corriger UNIQUEMENT les erreurs factuelles ou les chiffres altérés afin de ne pas restaurer les motifs statistiques détectables par les classifieurs IA.
- **(d) Étape 4 (Insertion Chirurgicale Bloc par Bloc & Scellement Agent)** :
  * **Édition Strictement Chirurgicale Bloc par Bloc** : Toute modification sur les sources du manuscrit (`paper/main.tex`, `.bib`, `.sty`) DOIT impérativement être effectuée de manière strictement chirurgicale, bloc par bloc et paragraphe par paragraphe.
  * **INTERDICTION ABSOLUE D'ÉCRASEMENT GLOBAL** : Il est FORMELLEMENT et ABSOLUMENT INTERDIT de tout réécrire d'un coup, de régénérer le document complet ou d'écraser le document entier avec `write_to_file` (notamment avec `Overwrite: true`).
  * **Obligation d'Opérer via `replace_file_content`** : L'intégration s'effectue EXCLUSIVEMENT via des appels ciblés à `replace_file_content` (ou application locale de patch) sur la portion exacte à modifier. `write_to_file` est strictement réservé à la création initiale de nouveaux fichiers.
  * **Scellement de la Révision Agent** : Immédiatement après les retouches chirurgicales, sceller le snapshot agent :
    ```python
    call_mcp_tool(
        ServerName="doc-version",
        ToolName="commit_document",
        Arguments={
            "target": "paper/main.tex",
            "message": "Révision agent",
            "author": "agent"
        }
    )
    ```
  * **Projection Différentielle & Restitution Chat** : Déclencher `get_diff_artifact` (voir Étape 4). Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain (`file:///<appDataDir>/brain/<conversation-id>/<slug>.md`) en tête de réponse. INTERDICTION FORMELLE de partager ou mentionner le lien de la note Obsidian dans le fil de discussion.

#### 4. Projection Différentielle Immédiate (`get_diff_artifact`)
- Rafraîchissement immédiat de l'artéfact Brain et de la note miroir avec le diff coloré et le callout d'explication :
  ```python
  call_mcp_tool(
      ServerName="doc-version",
      ToolName="get_diff_artifact",
      Arguments={
          "target": "paper/main.tex",
          "diff_explanation": "Intégration de la calibration N=500k et clarification de la Section 4.2",
          "brain_dir": "C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>"
      }
  )
  ```
- **Restauration en Cas d'Erreur ou Rollback (`restore_commit`)** :
  Si une révision introduit une régression, restaurer instantanément un commit antérieur sain :
  ```python
  call_mcp_tool(
      ServerName="doc-version",
      ToolName="restore_commit",
      Arguments={
          "commit_id": "<commit_id>",
          "target": "paper/main.tex"
      }
  )
  ```
- **Rappel Obligatoire de Restitution dans le Chat** : Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain retourné par l'outil (`file:///<appDataDir>/brain/<conversation-id>/<slug>.md`) en tête de réponse. INTERDICTION FORMELLE de partager ou mentionner le lien de la note Obsidian dans le fil de discussion.
- Vérifier que 100% des badges IA affichés dans l'artéfact sont conformes ($P(\text{AI}) \le 10\%$).

---

## 2. ⚡ Outils Déclaratifs du Serveur MCP `doc-version` & Voie de Secours CLI

Le versioning déclaratif et la projection différentielle reposent sur une architecture à **double voie d'exécution** garantissant une disponibilité permanente :
1. **Voie Principale (MCP `doc-version`)** : Invocation directe des outils déclaratifs MCP (`commit_document`, `get_diff_artifact`, `restore_commit`, etc.) via `call_mcp_tool(ServerName="doc-version", ...)`.
2. **Voie de Secours Robuste (CLI Local `doc_version_cli.py`)** : Si le serveur MCP `doc-version` est temporairement inactif ou non joignable, les agents DOIVENT basculer immédiatement sur le script moteur CLI dédié :
   ```powershell
   & "C:\Users\hjamet\Documents\code\doc-version-mcp\.venv\Scripts\python.exe" "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\doc_version_cli.py" diff --target "<fichier>" --explanation "<motif>" --content-file "<fichier_retouche>" --brain-dir "<appDataDir>/brain/<id>" --artifact-name "<nom>.md"
   ```
   *Ce script implémente exactement la même logique CAS, le calcul différentiel, les badges de conformité IA et la projection d'artéfacts.*
- **Articulations avec le Skill [`draft`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md)** : Pour la relecture chirurgicale de passages rédigés ou de brouillons soumis par Henri, le mode `draft` (`mode="draft"`) garantit la traçabilité des balises `<XXX>`, le mot-à-mot différentiel coloré et le contrôle de rétention textuelle ($\ge 90\%$).

Le serveur MCP unifié `doc-version` expose une suite complète d'outils déclaratifs :

### 1. `record_git_pull_event` (Synchronisation Amont & Événement Distant)
- **Rôle** : Exécuté avant ou après un `git pull` distant pour consigner l'état des collaborateurs distants et configurer l'autostash.
```python
call_mcp_tool(
    ServerName="doc-version",
    ToolName="record_git_pull_event",
    Arguments={
        "repo_path": "paper",
        "autostash": True
    }
)
```

### 2. `commit_document` (Scellement de Snapshot & Baseline)
- **Rôle** : Fige une baseline validée ou scelle une révision agent dans le stockage CAS sans interférer avec Git.
```python
call_mcp_tool(
    ServerName="doc-version",
    ToolName="commit_document",
    Arguments={
        "target": "paper/main.tex",
        "message": "Snapshot baseline",  # ou "Révision agent"
        "author": "collaborateur/henri"   # ou "agent"
    }
)
```

### 3. `get_diff_artifact` (Génération d'Artéfact de Diff & Badges Anti-IA)
- **Rôle** : Calcule le mot-à-mot différentiel multi-sources, compile l'arborescence Tree TOC, insère les badges de conformité IA (< 10%) et génère l'artéfact Markdown dans le brain Antigravity.
```python
call_mcp_tool(
    ServerName="doc-version",
    ToolName="get_diff_artifact",
    Arguments={
        "target": "paper/main.tex",
        "diff_explanation": "Intégration de la calibration N=500k et clarification de la Section 4.2",
        "brain_dir": "C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>"
    }
)
```

### 4. `restore_commit` (Rollback Atomique & Sécurisé)
- **Rôle** : Restaure instantanément une version antérieure en cas d'erreur ou de régression après création automatique d'un snapshot de secours.
```python
call_mcp_tool(
    ServerName="doc-version",
    ToolName="restore_commit",
    Arguments={
        "commit_id": "<commit_id>",
        "target": "paper/main.tex"
    }
)
```

### 5. `list_commits` & `prune_commits` (Historique & Maintenance)
- `list_commits(target="paper/main.tex", limit=10)` : Consultation de l'historique CAS des clichés.
- `prune_commits(ttl_days=14, max_size_mb=500)` : Maintenance et purge du cache CAS.

### 6. Invariant Strict Obligatoire (Gouvernance d'Exécution & Zéro Simulation Manuelle)
> [!CAUTION]
> **Interdiction Formelle de Falsification ou Rédaction Manuelle** : Il est FORMELLEMENT INTERDIT de rédiger ou simuler manuellement un artéfact de diff ou un commit CAS via `write_to_file`. Tout passe obligatoirement par la voie déclarative :
> 1. En priorité absolue via les outils du serveur MCP `doc-version`.
> 2. En cas d'indisponibilité avérée du serveur MCP, exclusivement via le script CLI machine homologué `_agents/scripts-for-skills/doc_version_cli.py`. Aucune commande de build sauvage ou script artisanal non référencé n'est autorisé.

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
1. **Pull-First & Autostash Systématique (`record_git_pull_event`)** :
   - À chaque synchronisation avec le dépôt distant, consigner l'événement amont via l'outil MCP déclaratif :
     ```python
     call_mcp_tool(
         ServerName="doc-version",
         ToolName="record_git_pull_event",
         Arguments={"repo_path": "paper", "autostash": True}
     )
     ```
   - Intègre les modifications distantes sans créer de commit de merge parasite.
2. **Préservation Prioritaire des Co-Auteurs** :
   - Les modifications faites par les collaborateurs sont **STRICTEMENT PRIORITAIRES** et ne doivent **JAMAIS être écrasées ni supprimées unilatéralement**.
   - Interdiction formelle du force push (`git push -f`) et de l'arbitrage aveugle (`--ours`).
3. **Gestion Bloquante des Conflits Git (Code de Sortie 3)** :
   - Si un conflit survient lors du rebase, le script s'interrompt immédiatement avec l'alerte rouge `🚨 [ACTION AGENT CRITIQUE : CONFLIT GIT DÉTECTÉ]`.
   - **Procédure de Résolution** :
     1. Inspecter immédiatement les fichiers signalés.
     2. Identifier précisément l'intention de la modification des collaborateurs.
     3. Concilier astucieusement notre texte et le leur afin de préserver les deux apports sans perte d'information.
     4. Finaliser le rebase (`git add . && git rebase --continue`), puis régénérer l'artéfact de diff via `get_diff_artifact`.
4. **Reporting Obligatoire dans le Chat** :
   - Formuler systématiquement à Henri un compte-rendu clair précisant les apports collaborateurs rapatriés et la conciliation effectuée.

---

## 5. 📑 Recompilation Obligatoire & Contrôle de Pagination

- **Recompilation Fraîche** : Après tout `git pull` ou édition des sources LaTeX, recompiler systématiquement le document (`pdflatex` ou `latexmk`) avant tout audit de pagination ou de rendu.
- **Interdiction Formelle d'Auditer un PDF Obsolète** : Ne jamais formuler d'avis sur la structure ou la longueur des sections en se basant sur un `.pdf` préexistant sans compilation vérifiée.

---

## 6. 🚫 Pourquoi les Commandes Git Manuelles et CLI Sont-elles Formellement Interdites ?

> [!CAUTION]
> **Interdiction Formelle des Commandes Git Manuelles et Scripts CLI** :
> Aucun agent ne doit **JAMAIS** exécuter de commandes `git add`, `git commit` ou `git push` manuelles dans le terminal, ni lancer de scripts CLI dépréciés.
> **Le serveur MCP `doc-version` encapsule et orchestre 100% du cycle de versioning, de diff et d'intégration collaborative.**

### 🛠️ Quel Est le Seul et Unique Workflow Valide pour Gérer le Manuscrit ?

1. **Enregistrer l'Événement Distant (Avant Pull / Synchronisation)** :
   ```python
   call_mcp_tool(
       ServerName="doc-version",
       ToolName="record_git_pull_event",
       Arguments={"repo_path": "paper", "autostash": True}
   )
   ```

2. **Ancrer la Baseline Validée (Avant Travail)** :
   ```python
   call_mcp_tool(
       ServerName="doc-version",
       ToolName="commit_document",
       Arguments={
           "target": "paper/main.tex",
           "message": "Snapshot baseline",
           "author": "collaborateur/henri"
       }
   )
   ```
   *(Fige la baseline dans le stockage CAS, capture l'état AST et initialise le point de repère).*

3. **Chirurgie Ciblée & Recompilation** :
   - Édition strictement chirurgicale bloc par bloc via `replace_file_content` (zéro `write_to_file` global).
   - Vérification `pdflatex` (code 0, 8 pages exactes).
   - Scellement du snapshot agent :
     ```python
     call_mcp_tool(
         ServerName="doc-version",
         ToolName="commit_document",
         Arguments={
             "target": "paper/main.tex",
             "message": "Révision agent",
             "author": "agent"
         }
     )
     ```

4. **Diff Déclaratif & Restitution Brain Prioritaire (Après Travail)** :
   ```python
   call_mcp_tool(
       ServerName="doc-version",
       ToolName="get_diff_artifact",
       Arguments={
           "target": "paper/main.tex",
           "diff_explanation": "<explication détaillée>",
           "brain_dir": "C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>"
       }
   )
   ```
   *(Calcule le word-diff multi-sources, compile l'artéfact Brain interactif avec badges Anti-IA).*
   - Partager **EXCLUSIVEMENT** le lien cliquable vers l'artéfact Brain (`file:///...`) en première ligne de réponse chat.

5. **Rollback d'Urgence en Cas d'Erreur** :
   ```python
   call_mcp_tool(
       ServerName="doc-version",
       ToolName="restore_commit",
       Arguments={
           "commit_id": "<commit_id>",
           "target": "paper/main.tex"
       }
   )
   ```

