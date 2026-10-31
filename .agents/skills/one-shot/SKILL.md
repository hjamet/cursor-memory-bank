---
name: one-shot
description: "Traitement asynchrone en une seule passe (/one-shot) des commentaires et consignes d'Henri sur un projet : exécute toutes les demandes comme dans un tour synchrone normal après le départ d'Henri (zéro question, zéro long résumé final, zéro initiative hors périmètre), consigne toutes les réponses dans AIVC (await_validation dans 🤖 <Titre>.md, validation uniquement sur accord explicite), met à jour sobrement la note maîtresse Obsidian (uniquement les réflexions et décisions pérennes réellement utiles) et clôture la session dans project-memory (avec le ressenti indiqué par Henri ou auto-évalué par l'agent). Trigger sur /one-shot."
aliases:
  - one-shot
---

# 🎯 Skill One-Shot — Traitement Asynchrone en Passe Unique & Clôture Automatique

> [!IMPORTANT]
> **Philosophie & Postulat Fondamental (« Fire-and-Leave »)** :
> Lorsqu'Henri invoque `/one-shot [à l'aise | ok | stressé / urgence | terminé]` après avoir déposé ses commentaires sur `advance_tldr/🤖 <Titre>.md` (ou sur d'autres artefacts du projet) et/ou ses consignes dans le chat, **considère qu'il a immédiatement quitté la conversation et qu'il n'y reviendra plus**.
> - **Contrairement à [`/advance`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/advance/SKILL.md)** : l'agent ne prend **aucune initiative spéculative** hors périmètre et n'invente pas d'explorations non demandées. Il traite **exclusivement et intégralement les commentaires, questions et demandes d'Henri**, exactement comme dans un tour de conversation synchrone normal (mise à jour des notes Obsidian, commits et `git push` sur `main`, préparation des brouillons [`/draft`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md), hors toute action externe irréversible telle que l'envoi effectif d'un e-mail, une soumission finale ou un paiement).
> - **Contrairement à une session synchrone** :
>   1. **Zéro question (`ask_question` strictement interdit) & Zéro long résumé dans le chat** : Henri ne lira pas la réponse du chat.
>   2. **Restitution 100 % prête dans `advance_tldr/🤖 <Titre>.md` via AIVC (`task_commit`) & Clôture [`project-memory`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/project-memory/SKILL.md)** : à la fin du traitement, 100 % des réponses aux commentaires, questions et tâches d'Henri doivent être consignées dans AIVC afin que, lors de sa prochaine ouverture du projet, Henri trouve immédiatement toutes ses réponses et livrables prêts en haut de `🤖 <Titre>.md`.

---

## ⚡ 1. Dérogation CLI & Architecture d'Exécution Directe ($P=0 \to P=1$)

1. **Orchestration directe par le Superviseur Racine ($P=0$)** :
   - Étant donné qu'une conversation `/one-shot` est dédiée à un unique projet et se ferme définitivement à l'issue du traitement, le Superviseur Racine ($P=0$) pilote directement ses sous-agents feuilles (`eclaireur`, `executant`, `auditeur-alignement` ou Claude Code via `claude_subagent.py` selon [`sous-agents.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)) sans couche intermédiaire `superviseur-projet`, ce qui préserve le `transcript.jsonl` exact de la session pour le calcul automatique du temps (`--transcript auto`).
2. **Dérogation d'exécution CLI pour $P=0$** :
   - Conformément à [`superviseur-aveugle.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md) et [`project-memory/SKILL.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/project-memory/SKILL.md), le Superviseur Racine ($P=0$) est habilité à exécuter directement via `run_command` :
     - les appels AIVC (`mcp-cli call aivc ...`) ;
     - les commandes de [`project_memory_cli.py`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/project_memory_cli.py) (`get`, `feedback "<Projet>" <action> --transcript auto`, `status-work`).

---

## 🔄 2. Protocole Séquence par Séquence

### Étape 1 — Lecture du Contexte & Inventaire Exhaustif des Commentaires d'Henri (Tour 0)
1. Identifier le projet cible (depuis l'artefact `🤖 <Titre>.md` commenté, la note mentionnée ou le contexte) et lire en parallèle :
   - `~/.gemini/antigravity/brain/advance_tldr/🤖 <Titre>.md` (pour relever tous les `[id]` existants en `await_validation` et `new` — **règle anti-doublon d'`id` stricte**) ;
   - la note maîtresse du projet `notes/<Titre>.md` ;
   - tout artefact sur lequel Henri a déposé un commentaire `Comment: "..."`.
2. Dresser la liste exacte de tous les commentaires d'artefacts (`Comment: "..."`) et de toutes les remarques/questions du message d'Henri en les classant en 3 catégories :
   - **Catégorie A — Validation ou rejet explicite sans action supplémentaire** (ex. *« ok », « c'est fait », « envoyé », « laisse tomber »* sur une tâche `[id]`) $\to$ à passer directement en `task_status: "validated"` avec préfixe obligatoire `[VALIDÉ PAR HENRI]` ou `[ÉCARTÉ PAR HENRI]`.
   - **Catégorie B — Demande de modification, d'action ou question sur une tâche `[id]` existante** $\to$ à exécuter par sous-agent, puis à mettre à jour sur le **même `id`** en `task_status: "await_validation"`.
   - **Catégorie C — Nouveau commentaire libre, nouvelle question ou nouvelle demande hors `[id]` existant** $\to$ à exécuter par sous-agent, puis à enregistrer comme une nouvelle entrée `task_status: "await_validation"` dans `🤖 <Titre>.md` (ou `"new"` uniquement si Henri mentionne explicitement une idée pour plus tard qu'il ne demande pas de traiter maintenant).

### Étape 2 — Exécution Parallèle de Toutes les Demandes (Mode Synchrone Sans Question)
1. Découper les demandes des Catégories B et C en lots atomiques et lancer **en parallèle au même tour** les sous-agents appropriés (`eclaireur`, `executant`, `claude_subagent.py`) selon les 3 régimes de [`sous-agents.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md).
2. **Exécution complète sur la branche principale & les notes (hors actions externes irréversibles)** :
   - Pour tout code ou document demandé par Henri : appliquer les modifications, exécuter les tests, committer et pousser (`git push`) directement sur la branche de travail du projet (`main` / `master` ou branche active).
   - Pour tout courriel ou message destiné à un tiers : générer ou mettre à jour l'artéfact [`/draft`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/draft/SKILL.md) (`doc-version` `commit_document` + `get_diff_artifact(mode="draft")`) sans jamais l'envoyer soi-même.
3. **Gestion des ambiguïtés ou blocages en l'absence d'Henri (Zéro `ask_question`)** :
   - Si une demande comporte une ambiguïté mineure : trancher selon le Critère de Simplicité d'Ockham en choisissant l'option la plus simple et réversible, et documenter ce choix dans `details` de la tâche `await_validation`.
   - Si un blocage technique ou un dilemme majeur empêche d'exécuter une demande sans validation humaine : préparer le terrain au maximum et exposer clairement la question bloquante et les options dans le champ `details` de l'entrée `await_validation` correspondante dans `🤖 <Titre>.md`.
4. **Silence dans le chat pendant l'exécution** : ne rédiger aucun pavé intermédiaire `🔎 Audit...` dans le chat (Henri ayant quitté la conversation), mais contrôler rigoureusement chaque artefact `sources_*.md` renvoyé par les sous-agents.

### Étape 3 — Mise à Jour Sobre et Utile de la Note Maîtresse Obsidian (Anti-Saturation)
1. **Conserver uniquement ce qui est véritablement utile et pérenne dans `notes/<Titre>.md`** :
   - Si Henri a exprimé dans ses commentaires une **réflexion de fond, une décision stratégique ou un choix d'architecture durable**, ou si l'exécution a produit un **résultat / livrable majeur**, mettre à jour `notes/<Titre>.md` (et ses sous-notes si $> 120$ lignes) au format canonique de [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) (`## Question ?` $\to$ 1–2 phrases d'explication directe $\to$ `Source : Prompt d'Henri Jamet (Chat <date>)` ou ancre primaire $\to$ citation exacte en bloc `>`).
   - **Interdiction de saturer la note maîtresse** : ne **jamais** y copier des micro-commentaires opérationnels de révision (*« reformule cette phrase », « vérifie ce bug », « ajoute tel argument »*), des échanges transitoires ou des checklists `- [ ]`.

### Étape 4 — Enregistrement AIVC (`task_commit`) & Régénération de `🤖 <Titre>.md`
Appeler `mcp-cli call aivc task_commit` via `run_command` (avec encodage UTF-8 strict `$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); Get-Content -Raw -Encoding UTF8 "<appDataDir>/brain/<id>/scratch/task_commit_payload.json" | mcp-cli call aivc task_commit`) en respectant :
1. **`title`** : `"[One-Shot] <Titre> — <Résumé court des commentaires traités>"`
2. **`main_project_file`** : `"notes/<Titre>.md"` (chemin exact de la note maîtresse du projet).
3. **`user_items` (Zéro validation automatique & Réponses exhaustives)** :
   - **Règle d'or de validation** : **ne JAMAIS passer une tâche en `"validated"` de ta propre initiative**. Seules les tâches pour lesquelles Henri a **expressément indiqué** dans ses commentaires qu'elles sont terminées, validées ou abandonnées (Catégorie A) passent en `"task_status": "validated"` (avec `"details"` préfixé par `[VALIDÉ PAR HENRI]` ou `[ÉCARTÉ PAR HENRI]`).
   - **Modifications sur tâche existante (Catégorie B)** : réutiliser impérativement l'`"id"` existant avec `"task_status": "await_validation"` et remplacer `"details"` par la nouvelle réponse directe / le nouveau livrable mis à jour (liens cliquables `[📄 ...](file:///...)`, `Source : <ancre primaire>` et citation exacte en bloc `>`), sans préambule superflu.
   - **Nouvelles questions ou remarques libres d'Henri (Catégorie C)** : créer une entrée `"task_status": "await_validation"` par demande/question traitée afin qu'Henri trouve immédiatement la réponse et le livrable en haut de `🤖 <Titre>.md` (`## ⚡ Décisions & Livrables Prêts`) à sa prochaine ouverture du projet.
4. **`journal`** : consigner dans `journal` la trace complète des commentaires verbatim déposés par Henri lors de ce `/one-shot` ainsi que le détail technique des actions, commits et vérifications réalisés (garantissant qu'aucune réflexion d'Henri dans Antigravity ne soit jamais perdue sans alourdir la note Obsidian).
5. **`edited_files` & `read_files`** : inclure 100 % des artefacts créés/modifiés dans `<appDataDir>/brain/<id>/` (notamment les `diff_*.md` `/draft`) et des fichiers modifiés afin qu'AIVC les synchronise dans `AIVC_Sync/files/` sur Google Drive.

### Étape 5 — Clôture `project-memory` (Ressenti d'Henri ou Auto-Évaluation) & Fin Silencieuse
1. Exécuter la commande de feedback rétrospectif (qui comptabilise automatiquement le temps de travail d'Henri via ses flèches `->` et ses commentaires d'artefacts `Comment: "..."` dans le transcript) :
   ```powershell
   python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "<Titre>" <action> --transcript auto
   ```
   - **Si Henri a indiqué son estimation** en invoquant `/one-shot` (`à l'aise` $\to$ `less-often`, `ok` $\to$ `ok`, `stressé` / `urgence` $\to$ `more-often` ou `emergency`, `terminé` $\to$ `finished`) : utiliser l'action correspondante.
   - **Si Henri n'a pas précisé son ressenti** : **ne jamais appeler `ask_question`** ; évaluer toi-même lucidement le ressenti parmi les 3 options (`less-often`, `ok`, `more-often`) selon l'avancement, les blocages éventuels et la marge calendaire avant deadline (règle du buffer 20–30 % de [`project-memory/SKILL.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/project-memory/SKILL.md)), et exécuter directement `feedback`.
2. **Clôture ultra-courte dans le chat (3 lignes maximum)** :
   - Afficher uniquement une confirmation télégraphique de 2 à 3 lignes (lien `[🤖 <Titre>](file:///...)`, ID du commit AIVC, action `project-memory` appliquée et nouveau score $S_{\text{base}} \to S_{\text{eff}}$), puis s'arrêter immédiatement sans poser aucune question.
