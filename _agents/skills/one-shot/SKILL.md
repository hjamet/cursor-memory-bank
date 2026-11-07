---
name: one-shot
description: "Traitement asynchrone en une seule passe (/one-shot) des commentaires et consignes d'Henri sur un projet : scelle d'abord l'état validé par Henri dans doc-version (author='henri'), exécute toutes les demandes après le départ d'Henri (zéro question hors interview /grill-me préalable), met à jour la Note Maîtresse (et sa section narrative « Prochaines Étapes »), écrase l'artéfact de diff _agents/project_diffs/🤖 <Nom>.md via doc-version (author='henri' -> actuel, wikilinks cliquables Antigravity) et clôture la session dans project-memory. Trigger sur /one-shot."
aliases:
  - one-shot
---

# 🎯 Skill One-Shot — Traitement Asynchrone en Passe Unique via `doc-version` & Clôture Automatique

> [!IMPORTANT]
> **Philosophie & Postulat Fondamental (« Fire-and-Leave »)** :
> Lorsqu'Henri invoque `/one-shot [à l'aise | ok | stressé / urgence | terminé]` après avoir déposé ses commentaires sur `_agents/project_diffs/🤖 <Nom>.md` (ou directement sur la Note Maîtresse `notes/<Titre>.md` ou d'autres artefacts `🤖 <Sujet>.md`) et/ou ses consignes dans le chat, **considère qu'il a immédiatement quitté la conversation et qu'il n'y reviendra plus**.
> - L'agent traite **intégralement les commentaires, questions et demandes d'Henri**, exactement comme dans un tour de conversation synchrone normal selon [`bonnes-pratiques-developpement.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/bonnes-pratiques-developpement.md), [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) et [`task-tracking.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md).
> - **Spécificités d'interaction asynchrone** :
>   1. **Zéro question (`ask_question` interdit en exécution) & Zéro long résumé dans le chat** : Henri ne lira pas la réponse du chat. Si une interview préalable (`/grill-me`) est demandée conjointement par Henri, mener d'abord l'interview complète, puis enchaîner de manière 100 % autonome l'exécution et la clôture sans plus aucune question.
>   2. **Restitution 100 % dans la Note Maîtresse (`notes/<Titre>.md`) et son Diff Cumulatif `_agents/project_diffs/🤖 <Titre>.md`** : à la fin du traitement, la Note Maîtresse (incluant sa section narrative `## 🚀 Quelles Sont les Prochaines Étapes ?`) est à jour et son diff cumulatif par rapport à la baseline `author="henri"` est généré dans `_agents/project_diffs/🤖 <Titre>.md` (avec `[[wikilinks]]` convertis en liens cliquables Antigravity).

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
1. Découper les demandes d'Henri en lots atomiques et lancer **en parallèle au même tour** les sous-agents appropriés (`eclaireur`, `executant`, `claude_subagent.py`) selon les 3 régimes de [`sous-agents.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md), suivis d'`auditeur-alignement` (`Model: 'inherit'`) si du code/UI/outil a été modifié.
2. **Travail sur la branche principale (`main` / `master`), la Note Maîtresse & Boucle `/learn` sur `skills/*.md`** :
   - Appliquer les modifications de code, committer et pousser (`git push`) directement sur la branche principale de chaque dépôt.
   - Mettre à jour la **Note Maîtresse (`notes/<Titre>.md`)** selon [`coffre-obsidian.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md) : intégrer les réponses aux questions d'Henri, les nouveaux résultats/tableaux demandés, et actualiser en bas de note la section narrative en langage naturel **`## 🚀 Quelles Sont les Prochaines Étapes ?`** (sans listes de cases à cocher `- [ ]`).
   - **Boucle d'Auto-Évolution (`/learn` + Rasoir d'Ockham à taille constante)** : si Henri a émis une critique ou un commentaire sur une tâche ayant mobilisé un skill `skills/<nom>.md`, mettre à jour `skills/<nom>.md` à taille constante.
   - Pour tout courriel, message (`virtual:<Sujet>`) ou manuscrit LaTeX modifié : générer/écraser son artéfact `doc-version` dans `_agents/project_diffs/🤖 <Nom>.md` via `get_diff_artifact(mode="draft")`.

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
   - Si Henri a indiqué son estimation (`à l'aise` $\to$ `less-often`, `ok` $\to$ `ok`, `stressé` / `urgence` $\to$ `more-often` ou `emergency`, `terminé` $\to$ `finished`) : utiliser l'action correspondante ; sinon l'évaluer lucidement sans `ask_question`.
2. **Clôture ultra-courte dans le chat (2 à 3 lignes maximum)** : afficher uniquement le lien `[🤖 <Titre>](file:///...)`, l'action appliquée et le nouveau score $S_{\text{base}} \to S_{\text{eff}}$, puis s'arrêter immédiatement.
