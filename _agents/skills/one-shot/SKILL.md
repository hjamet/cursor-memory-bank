---
name: one-shot
description: "Traitement asynchrone en une seule passe (/one-shot) des commentaires et consignes d'Henri sur un projet : scelle d'abord l'état validé par Henri dans doc-version (author='henri'), exécute toutes les demandes après le départ d'Henri (zéro ask_question), met à jour la Note Maîtresse (et sa section « Prochaines Étapes » en items - [ ]), écrase l'artéfact de diff _agents/project_diffs/🤖 <Nom>.md via doc-version (author='henri' -> actuel, wikilinks cliquables Antigravity) et clôture la session dans project-memory (score + task list - [ ]). Trigger sur /one-shot."
aliases:
  - one-shot
---

# 🎯 Skill One-Shot — Traitement Asynchrone en Passe Unique via `doc-version` & Clôture Automatique

> [!IMPORTANT]
> **Philosophie & Postulat Fondamental (« Fire-and-Leave »)** :
> Lorsqu'Henri invoque `/one-shot [à l'aise | ok | stressé / urgence | terminé]` après avoir déposé ses commentaires sur `_agents/project_diffs/🤖 <Nom>.md` (ou directement sur la Note Maîtresse `notes/<Titre>.md` ou d'autres artefacts `🤖 <Sujet>.md`) et/ou ses consignes dans le chat, **considère qu'il a immédiatement quitté la conversation et qu'il n'y reviendra plus**.
> - L'agent traite **intégralement les commentaires, questions et demandes d'Henri**, exactement comme dans un tour de conversation synchrone normal selon [`bonnes-pratiques-developpement.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/bonnes-pratiques-developpement.md), [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) et [`task-tracking.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md).
> - **Spécificités d'interaction asynchrone (Abandon total de `ask_question`, Persistance Roadmap & Task-List finale)** :
>   1. **Interdiction formelle de l'outil `ask_question` & Zéro interruption** : l'outil `ask_question` est **strictement banni** (y compris pour les brouillons `/draft`, les clarifications ou le ressenti). Par défaut, Henri lance `/one-shot` et quitte la conversation : l'agent exécute l'intégralité du travail réalisable sans s'interrompre (pendant l'exécution autonome, **ne jamais passer de mot de passe, jeton ou clé API littérale en ligne de commande**, et ne jamais proposer d'activer l'accès écriture payant dans Spark, cf. [`pomodoro-projets.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/pomodoro-projets.md)).
>   2. **Double Persistance Obligatoire & Tri par Émojis de Priorité (`🚨` / `⚠️` / `🔵`) dans la Roadmap (`## 🚀 Quelles Sont les Prochaines Étapes ?`)** : toute question à poser à Henri, vérification attendue, brouillon `/draft` prêt à envoyer (`[[_agents/project_diffs/🤖 <Sujet>|🤖 Brouillon ...]]` + canal/lien d'envoi) et action humaine requise **DOIVENT impérativement être ajoutés sous forme de tâches `- [ ] <Émoji>` non cochées (triées `🚨` $\to$ `⚠️` $\to$ `🔵`) dans `## 🚀 Quelles Sont les Prochaines Étapes ?` de la Note Maîtresse** (ainsi que des autres Notes Maîtresses touchées) : **`- [ ] 🚨`** pour les actions immédiates à traiter tout de suite (envois de courriels/messages `/draft`, dépôts/publications de documents, validations immédiates), **`- [ ] ⚠️`** pour les chantiers qu'il faudrait commencer maintenant idéalement, et **`- [ ] 🔵`** pour les nouvelles tâches de fond à ne regarder que si Henri n'est pas déjà en train de traiter d'autres éléments sur le projet.
>   3. **Clôture minimaliste dans le chat (Évolution du score + Task-List `- [ ] 🚨 / ⚠️ / 🔵` uniquement)** : à la toute fin de `/one-shot`, **n'écrire aucun récit ni bilan en prose dans le chat**. Afficher **uniquement** : (a) le lien `[🤖 <Titre>](file:///...)` et l'évolution du score appliquée au projet ($S_{\text{base}} \to S_{\text{eff}}$), suivis de (b) la **task list (`- [ ] 🚨 ...`, `- [ ] ⚠️ ...`, `- [ ] 🔵 ...`)** regroupant par ordre de priorité les actions immédiates, points d'attention, questions et vérifications (avec liens cliquables `[🤖 <Sujet>.md](file:///...)` et liens vers les notes/portails concernés).

---

## 🔄 Protocole Séquence par Séquence

### Étape 1 — Lecture du Contexte, Inventaire des Commentaires & Scellement de la Baseline Validée (`author="henri"`)
1. Identifier le projet cible et lire en parallèle :
   - `_agents/project_diffs/🤖 <Titre>.md` et la Note Maîtresse `notes/<Titre>.md` (en inspectant systématiquement sa section `## Skills` en haut de note et en lisant en *Lazy Loading* tout skill `skills/<nom>.md` pertinent) ;
   - tout autre artéfact `🤖 <Nom>.md` sur lequel Henri a déposé un commentaire `Comment: "..."`.
2. **Scellement de la Baseline Validée par Henri (`author="henri"`)** :
   - Si Henri a rejeté ou demandé d'annuler un passage du diff précédent dans `notes/<Titre>.md`, rétablir d'abord ce passage conformément à sa remarque ;
   - Sceller immédiatement cet état revu/approuvé par Henri comme la **nouvelle baseline de référence** via `doc-version` :
     `call_mcp_tool(ServerName="doc-version", ToolName="commit_document", Arguments={"target": "<chemin_note_maitresse>", "message": "Validation Henri (/one-shot)", "author": "henri", "mode": "draft"})`
   - Ainsi, le diff qui sera généré à la fin de la session `/one-shot` ne montrera **que les nouvelles modifications apportées par l'agent en réponse aux commentaires du jour** !

### Étape 2 — Exécution Parallèle de Toutes les Demandes & Mise à Jour de la Note Maîtresse
1. Traiter directement toutes les demandes d'Henri de bout en bout et tester manuellement en conditions réelles toute modification de code, d'outil ou d'interface.
2. **Travail sur la branche principale (`main` / `master`), la Note Maîtresse & Boucle `/learn` sur `skills/*.md`** :
   - Appliquer les modifications de code, committer et pousser (`git push`) directement sur la branche principale de chaque dépôt.
   - Mettre à jour les sous-notes concernées (qui restent des **instantanés purs de l'état actuel**, sans diff `doc-version`) et mettre à jour la **Note Maîtresse (`notes/<Titre>.md`)** selon [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) et [`task-tracking.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md) : dans chaque section thématique active `## <Question de la sous-note> ?`, placer le lien `[[notes/Sous-Note|Titre]]`, résumer le contenu actuel de la sous-note, **détailler explicitement tous les changements intervenus depuis la dernière consultation d'Henri** (pour qu'ils apparaissent dans `🤖 <Titre>.md`), intégrer les réponses aux questions d'Henri, et actualiser en bas de note la section **`## 🚀 Quelles Sont les Prochaines Étapes ?`** (chaque tâche listée sous forme `- [ ] 🚨` / `- [ ] ⚠️` / `- [ ] 🔵` jamais cochée, triée par urgence décroissante, avec wikilinks Obsidian `[[...]]` vers les notes/sous-notes/diffs liés et zéro chemin de fichier brut).
   - **Directive `« archive »` & Mini-Dream sur Réflexions Tangentielles (`->`)** : lorsqu'Henri commente `« archive »` sur le titre d'une section (`#` / `##` / `###`), déplacer tout son contenu dans `notes/<Sous-Note>.md` et **transformer directement ce titre lui-même en lien cliquable** (`## [[notes/Sous Note|Question de la section ?]]`, **sans sous-titre additionnel, paragraphe, `Source :` ni citation dessous**, cf. [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md)). Lorsqu'un commentaire ou prompt `/one-shot` glisse une réflexion tangentielle hors du projet courant, exécuter un **mini-Dream immédiat** : sauvegarder le **verbatim original exact** d'Henri dans la Note Maîtresse du projet concerné (ou créer une Note Maîtresse `#project #todo` dédiée si l'effet de levier l'exige, jamais en note quotidienne datée), y ajouter ses `- [ ] 🚨 / ⚠️ / 🔵`, générer son `🤖 <Nom>.md` (`author="agent"`) et ajuster son score via `project_memory_cli.py set-score` (l'action `feedback` de l'Étape 4 restant appliquée au seul projet principal du `/one-shot`).
   - **Synchronisation automatique de la Fiche Partagée Collaborateurs (`notes/Project Overview <Nom>.md`)** : si le projet possède une note partagée `notes/Project Overview <Nom>.md` (liée dans la Note Maîtresse ou sa section `## Skills`), lire obligatoirement [`/briefing`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/briefing/SKILL.md), y répercuter en anglais propre tous les nouveaux résultats, figures et arbitrages (zéro lien interne, zéro nom de collaborateur, `avoid-ai-writing`), puis republier en place via `obsidian-comment-share` (`cli.cjs share`) afin que les collaborateurs voient immédiatement l'état à jour avant la prochaine réunion.
   - **Boucle d'Auto-Évolution (`/learn` + Rasoir d'Ockham à taille constante)** : si Henri a émis une critique ou un commentaire sur une tâche ayant mobilisé un skill `skills/<nom>.md`, mettre à jour `skills/<nom>.md` à taille constante.
   - Pour tout courriel, message (`virtual:<Sujet>`) ou manuscrit LaTeX modifié via `/draft` : générer/écraser son artéfact `doc-version` dans `_agents/project_diffs/🤖 <Nom>.md` via `get_diff_artifact(mode="draft")` (**ne jamais appeler `doc-version` sur une sous-note Obsidian**).

### Étape 3 — Génération du Diff Cumulatif `_agents/project_diffs/🤖 <Titre>.md` via `doc-version`
Appeler `get_diff_artifact` sur la Note Maîtresse `notes/<Titre>.md` (avec `author="agent"`, qui compare automatiquement à la baseline `author="henri"` scellée à l'Étape 1 et écrase `_agents/project_diffs/🤖 <Titre>.md` en convertissant les `[[wikilinks]]` en liens cliquables Antigravity) :
```python
call_mcp_tool(
    ServerName="doc-version",
    ToolName="get_diff_artifact",
    Arguments={
        "target": "C:/Users/hjamet/Documents/VoiceNotes/notes/<Titre>.md",
        "diff_explanation": "Traitement /one-shot des commentaires d'Henri",
        "mode": "draft",
        "language": "fr"
    }
)
```

### Étape 4 — Clôture `project_memory_cli.py` & Fin Silencieuse
1. Exécuter la commande de feedback rétrospectif (en passant `--keep-diff` / sans écraser la baseline `author="henri"` de l'Étape 1 afin que le nouveau diff `🤖 <Titre>.md` généré à l'Étape 3 reste visible pour la prochaine ouverture d'Henri) :
   ```powershell
   python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "<Titre>" <action> --transcript auto --keep-diff
   ```
   - Si Henri a indiqué son estimation (`à l'aise` $\to$ `less-often`, `ok` $\to$ `ok`, `stressé` / `urgence` $\to$ `more-often` ou `emergency`, `terminé` $\to$ `finished`) : utiliser l'action correspondante ; sinon l'évaluer lucidement selon la marge calendaire (zéro `ask_question`).
2. **Clôture épurée dans le chat (Score + Task-List uniquement, zéro texte superflu)** : n'écrire **aucun résumé ni commentaire narratif** à la fin. Afficher **exclusivement** :
   - En tête : le lien `[🤖 <Titre>](file:///...)`, l'action appliquée et l'évolution du score ($S_{\text{base}} \to S_{\text{eff}}$) ;
   - Dessous, sous forme de **task list triée par émojis de priorité (`- [ ] 🚨`, `- [ ] ⚠️`, `- [ ] 🔵`)** : les envois/publications et validations immédiates (`🚨`), les chantiers à entamer maintenant idéalement (`⚠️`), et les nouvelles tâches de fond à n'ouvrir que si rien n'est en cours (`🔵`), avec liens `[🤖 <Sujet>.md](file:///...)` et URLs directes, **tous ces points ayant été préalablement inscrits dans `## 🚀 Quelles Sont les Prochaines Étapes ?` de la Note Maîtresse**, puis s'arrêter immédiatement.
