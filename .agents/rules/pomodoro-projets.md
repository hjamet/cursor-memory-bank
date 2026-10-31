# Gestion Proactive des Projets & Pomodoro (MANDATOIRE)

| Règle | Invariant |
|---|---|
| **Double lien vivant en tête** | Dès qu'un projet est abordé ➔ `[Nom Projet](file:///c:/Users/hjamet/Documents/VoiceNotes/.../NomProjet.md) · [🤖 Nom Projet](file:///C:/Users/hjamet/.gemini/antigravity/brain/advance_tldr/🤖 Nom Projet.md)` en première ligne. |
| **Contexte au tour 0 & Fast-Track** | À chaque début de conversation sur un projet, le superviseur lit la note maîtresse (si son chemin est connu) et `~/.gemini/antigravity/brain/advance_tldr/🤖 <Titre>.md` (zéro création de `task.md`), selon [task-tracking.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md) et [project-memory](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/project-memory/SKILL.md). Si la demande est un correctif ou bug sans risque (Régime A, cf. [sous-agents.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)), lancer directement l'`executant` au tour 0 sans éclaireur préalable ; n'utiliser d'éclaireur de contexte au tour 0 que si l'information est éparpillée ou s'il s'agit d'une exploration (Régime B). |
| **Pas de démon ni d'alarme** | Aucune commande de fond permanente (`work`) ni alarme intrusive : le travail se fait librement, sans coupure. |
| **Clôture uniquement sur demande** | Une session ne se termine QUE quand Henri invoque le skill `project-memory`. Ne jamais déclarer soi-même une fin de session, même si tout est fait. Le bilan des chantiers, le calcul du temps réel et la mise à jour du registre sont réservés à cette invocation. |
| **Ressenti réservé à la clôture** | `ask_question` sur le ressenti uniquement lors de cette invocation, et seulement si Henri ne l'a pas déjà donné. |
| **Exemption veille et maintenance** | Veille proactive, maintenance mémorielle et cycles autonomes (hors session sur un projet métier) se clôturent sans question de ressenti, selon leur `SKILL.md`. |
| **Ajustement et calibrage** | Uniquement selon le skill dédié de gestion de projets (`project-memory`). |
