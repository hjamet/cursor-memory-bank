---
name: one-shot
description: "Traitement asynchrone en une seule passe (/one-shot) des commentaires et consignes d'Henri sur un projet : exécute toutes les demandes comme dans un tour synchrone normal après le départ d'Henri (zéro question — sauf en cas d'interview préalable demandée par Henri auquel cas l'agent mène d'abord l'interview complète puis enchaîne l'exécution et la clôture en totale autonomie —, zéro long résumé final), consigne toutes les réponses dans AIVC (await_validation dans 🤖 <Titre>.md, validation uniquement sur accord explicite ou obsolescence constatée) et clôture la session avec le ressenti indiqué par Henri ou auto-évalué par l'agent. Trigger sur /one-shot."
aliases:
  - one-shot
---

# 🎯 Skill One-Shot — Traitement Asynchrone en Passe Unique & Clôture Automatique

> [!IMPORTANT]
> **Philosophie & Postulat Fondamental (« Fire-and-Leave »)** :
> Lorsqu'Henri invoque `/one-shot [à l'aise | ok | stressé / urgence | terminé]` après avoir déposé ses commentaires sur `advance_tldr/🤖 <Titre>.md` (ou sur d'autres artefacts du projet) et/ou ses consignes dans le chat, **considère qu'il a immédiatement quitté la conversation et qu'il n'y reviendra plus**.
> - L'agent traite **intégralement les commentaires, questions et demandes d'Henri**, exactement comme dans un tour de conversation synchrone normal selon [`bonnes-pratiques-developpement.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/bonnes-pratiques-developpement.md) et [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) : travail et `git push` directement sur la branche principale (`main` / `master`, en y fusionnant et supprimant toute branche secondaire éventuelle), mise à jour des notes du coffre Obsidian et des fichiers du projet.
> - **Spécificités d'interaction asynchrone** :
>   1. **Zéro question (`ask_question` interdit en exécution) & Zéro long résumé dans le chat** : Henri ne lira pas la réponse du chat. Si une interview préalable est demandée conjointement par Henri, mener d'abord l'interview complète (via `ask_question`, une question à la fois avec option recommandée après exploration du code), puis dès l'interview terminée, enchaîner de manière 100 % autonome l'exécution et la clôture sans plus aucune question.
>   2. **Restitution 100 % prête dans `advance_tldr/🤖 <Titre>.md` via AIVC (`task_commit`) & Clôture de session** : à la fin du traitement, 100 % des réponses aux commentaires, questions et tâches d'Henri doivent être consignées dans AIVC afin que, lors de sa prochaine ouverture du projet, Henri trouve immédiatement toutes ses réponses et livrables prêts en haut de `🤖 <Titre>.md`.
>   3. **Mode Autonome Piloté par `watch-inbox` (`1 projet = 1 tâche new`)** : lorsque `/one-shot` est invoqué automatiquement par `watch-inbox` sur le projet le plus urgent dépourvu de tâche en `await_validation`, l'agent identifie dans `🤖 <Titre>.md` **la seule tâche `new` la plus urgente et immédiatement faisable** (ou la tâche récurrente `is_recurring=True` `[ockham-<slug>]` « Rasoir d'Ockham » si aucune autre tâche `new` réalisable n'est plus urgente), consulte son historique via `mcp-cli call aivc get_task_history`, traite **uniquement cette tâche** sur la branche principale (`main` / `master`) avec garde-fou `/draft` (`doc-version`) et **interdiction absolue de toute action impossible à annuler ou impliquant d'autres personnes** (envoi de message/courriel, soumission de formulaire, paiement, publication externe), dépose son livrable en `await_validation` (ce qui gèle le projet pour l'autonomie jusqu'à la revue d'Henri) et clôture par `project_memory_cli.py feedback "<Titre>" ok --agent`.

---

## ⚡ 1. Dérogation CLI & Architecture d'Exécution Directe ($P=0 \to P=1$)

1. **Orchestration directe par le Superviseur Racine ($P=0$)** :
   - Étant donné qu'une conversation `/one-shot` est dédiée à un unique projet et se ferme définitivement à l'issue du traitement, le Superviseur Racine ($P=0$) pilote directement ses sous-agents feuilles (`eclaireur`, `executant`, `auditeur-alignement` ou Claude Code via `claude_subagent.py` selon [`sous-agents.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)), ce qui préserve le `transcript.jsonl` exact de la session pour le calcul automatique du temps (`--transcript auto`).
2. **Dérogation d'exécution CLI pour $P=0$** :
   - Conformément à [`superviseur-aveugle.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md), le Superviseur Racine ($P=0$) est habilité à exécuter directement via `run_command` :
     - les appels AIVC (`mcp-cli call aivc ...`) ;
     - les commandes de [`project_memory_cli.py`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/project_memory_cli.py) (`get`, `feedback "<Projet>" <action> --transcript auto`, `status-work`).

---

## 🔄 2. Protocole Séquence par Séquence

### Étape 1 — Lecture du Contexte & Inventaire Exhaustif des Commentaires d'Henri (Tour 0)
1. Identifier le projet cible (depuis l'artefact `🤖 <Titre>.md` commenté, la note mentionnée ou le contexte) et lire en parallèle :
   - `C:\Users\Public\aivc\advance_tldr\🤖 <Titre>.md` (pour relever tous les `[id]` existants en `await_validation` et `new` — **règle anti-doublon d'`id` stricte**) ;
   - la note maîtresse du projet `notes/<Titre>.md` (en inspectant systématiquement sa section `## Skills` en haut de note et en lisant en *Lazy Loading* tout skill `skills/<nom>.md` dont la condition d'utilisation correspond aux tâches à traiter, tracé dans `read_files` de `task_commit`, cf. [`pomodoro-projets.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/pomodoro-projets.md)) ;
   - tout artefact sur lequel Henri a déposé un commentaire `Comment: "..."`.
2. Dresser la liste exacte de tous les commentaires d'artefacts (`Comment: "..."`) et de toutes les remarques/questions du message d'Henri en les classant en 3 catégories :
   - **Catégorie A — Validation ou rejet explicite d'Henri, ou tâche constatée comme accomplie / caduque au vu de la situation actuelle** (ex. *« ok », « c'est fait », « envoyé », « laisse tomber »*, ou constat factuel que le courriel a déjà été envoyé, que la réunion est passée ou qu'un événement récent rend la tâche obsolète) $\to$ à passer directement en `task_status: "validated"` avec préfixe obligatoire `[VALIDÉ PAR HENRI]` ou `[ÉCARTÉ PAR HENRI]`.
   - **Catégorie B — Demande de modification, d'action, question ou mise à jour de cohérence sur une tâche `[id]` existante** $\to$ à exécuter par sous-agent et/ou mettre à jour sur le **même `id`** en `task_status: "await_validation"` afin que toutes les tâches restent cohérentes avec la situation actuelle.
   - **Catégorie C — Nouveau commentaire libre, nouvelle question ou nouvelle demande hors `[id]` existant** $\to$ à exécuter par sous-agent, puis à enregistrer comme une nouvelle entrée `task_status: "await_validation"` dans `🤖 <Titre>.md` (ou `"new"` uniquement si Henri mentionne explicitement une idée pour plus tard qu'il ne demande pas de traiter maintenant).

### Étape 2 — Exécution Parallèle de Toutes les Demandes & Mise à Jour du Coffre
1. Découper les demandes des Catégories B et C en lots atomiques et lancer **en parallèle au même tour** les sous-agents appropriés (`eclaireur`, `executant`, `claude_subagent.py`) selon les 3 régimes de [`sous-agents.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md).
2. **Travail sur la branche principale (`main` / `master`), les notes du coffre & Boucle d'Auto-Évolution `/learn` sur `skills/*.md`** :
   - Appliquer les modifications, fusionner toute branche secondaire résiduelle dans `main` (ou `master`), committer et pousser (`git push`) directement sur la branche principale de chaque dépôt (GitHub, Overleaf, etc.) selon [`bonnes-pratiques-developpement.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/bonnes-pratiques-developpement.md).
   - Mettre à jour les notes du coffre Obsidian selon [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md).
   - **Boucle d'Auto-Évolution (`/learn` + Rasoir d'Ockham à taille constante)** : chaque fois qu'Henri émet un commentaire, une critique ou un rejet sur une tâche ayant mobilisé un skill de projet (`skills/<nom>.md`), ou lorsque le message réellement envoyé par Henri diffère du brouillon proposé, déclencher une passe réflexive `/learn` sur `skills/<nom>.md` en réécrivant, fusionnant et condensant les règles existantes **sans inflation de taille** (interdiction formelle d'empiler en bas de note).
   - Pour tout courriel ou message destiné à un tiers : générer ou mettre à jour l'artéfact de diff via `doc-version` (`commit_document` + `get_diff_artifact(mode="draft")`) sans l'envoyer soi-même.
3. **Gestion des ambiguïtés ou blocages** :
   - Si une demande comporte une ambiguïté mineure après le départ d'Henri, trancher selon le Critère de Simplicité d'Ockham en choisissant l'option la plus simple et réversible, et documenter ce choix dans `content` de la tâche `await_validation`.
   - Si un blocage technique majeur empêche d'exécuter une demande sans validation humaine : préparer le terrain au maximum et exposer clairement la question bloquante et les options dans l'entrée `await_validation` correspondante dans `🤖 <Titre>.md`.
4. **Silence dans le chat pendant l'exécution** : ne rédiger aucun pavé intermédiaire `🔎 Audit...` dans le chat (Henri ayant quitté la conversation), mais contrôler rigoureusement chaque artefact `sources_*.md` renvoyé par les sous-agents.

### Étape 3 — Enregistrement Atomique AIVC (`task_commit`) & Régénération de `🤖 <Titre>.md`
Pour chaque tâche traitée, mise à jour ou validée, appeler `mcp-cli call aivc task_commit` (alias `remember`) via `run_command` (avec encodage UTF-8 strict `$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); Get-Content -Raw -Encoding UTF8 "<appDataDir>/brain/<id>/scratch/task_commit_payload.json" | mcp-cli call aivc task_commit`) selon la signature plate et atomique (`1 appel = 1 tâche`) de [`task-tracking.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md) :
1. **`task_id`** : obligatoire pour toute tâche existante (Catégories A et B — **interdiction formelle d'inventer un nouvel ID si la tâche existe déjà dans `🤖 <Titre>.md`, même si son titre est affiné**). Laisser `task_id=None` uniquement pour créer une nouvelle tâche (Catégorie C).
2. **`title`** : intitulé clair et précis de la tâche.
3. **`content` (Paragraphe atomique en pur langage naturel : Contexte ➔ Action & TL;DR)** :
   - Rédiger un bon paragraphe complet et fluide en langage naturel commençant par le **Contexte explicite** (*« Tu m'avais demandé de vérifier X... », « Suite à ton commentaire sur Y... »*), suivi de l'**Action réalisée et des Conclusions / Chiffres clés (TL;DR)**.
   - **Intégrer directement dans le texte 1 ou 2 liens Markdown `[📄 nom](file:///...)` maximum** vers les artefacts principaux à consulter (résultat final, walkthrough, unique artéfact `[📄 diff_<sujet>.md](file:///...)` pour un courriel `/draft`, ou duo `[📕 <doc>.pdf](file:///...)` + `[📄 diff_<doc>.md](file:///...)` pour un document compilé), que `project-memory` et AIVC synchronisent et réécrivent automatiquement sur le poste actuel (zéro wikilink `[[...]]`, zéro bloc `Source :`, zéro `.tex` brut et zéro extrait de code dans `content`).
   - **Règle de validation (`task_status`) & Cohérence continue** : passer en `"task_status": "validated"` (avec `"content"` préfixé par `[VALIDÉ PAR HENRI]` ou `[ÉCARTÉ PAR HENRI]`) les tâches pour lesquelles Henri a indiqué qu'elles sont terminées/abandonnées **ainsi que toute tâche dont tu constates factuellement qu'elle n'est plus d'actualité** (courriel déjà envoyé, réunion passée, piste rendue obsolète par un événement récent). Mettre à jour proactivement les tâches restantes (Catégories B et C) en `"task_status": "await_validation"` pour qu'elles soient toujours cohérentes au regard de la situation actuelle.
4. **`main_project_file`** : `"notes/<Titre>.md"` (chemin exact de la note maîtresse du projet).
5. **`edited_files` & `read_files` (Graphe sémantique AIVC & Synchro Drive)** : inclure tous les fichiers modifiés et consultés pour cette tâche (en particulier 100 % des artefacts de `<appDataDir>/brain/<id>/` liés dans `content` ; zéro `.tex` brut) afin qu'AIVC maintienne son graphe et matérialise les artefacts dans `C:\Users\Public\aivc\artifacts\`.

### Étape 4 — Clôture `project_memory_cli.py` (Ressenti d'Henri ou Auto-Évaluation) & Fin Silencieuse
1. Exécuter la commande de feedback rétrospectif (qui comptabilise automatiquement le temps de travail d'Henri via ses flèches `->` et ses commentaires d'artefacts `Comment: "..."` dans le transcript) :
   ```powershell
   python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "<Titre>" <action> --transcript auto
   ```
   - **Si Henri a indiqué son estimation** en invoquant `/one-shot` (`à l'aise` $\to$ `less-often`, `ok` $\to$ `ok`, `stressé` / `urgence` $\to$ `more-often` ou `emergency`, `terminé` $\to$ `finished`) : utiliser l'action correspondante.
   - **Si Henri n'a pas précisé son ressenti** : **ne jamais appeler `ask_question`** ; évaluer toi-même lucidement le ressenti parmi les 3 options (`less-often`, `ok`, `more-often`) selon l'avancement, les blocages éventuels et la marge calendaire avant deadline, et exécuter directement `feedback`.
2. **Clôture ultra-courte dans le chat (3 lignes maximum)** :
   - Afficher uniquement une confirmation télégraphique de 2 à 3 lignes (lien `[🤖 <Titre>](file:///...)`, ID du commit AIVC, action appliquée et nouveau score $S_{\text{base}} \to S_{\text{eff}}$), puis s'arrêter immédiatement sans poser aucune question.
