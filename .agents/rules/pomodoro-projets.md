---
description: "Gestion proactive des projets et sessions Pomodoro (double lien vivant, Fast-Track au tour 0, zéro démon de fond, clôture sur demande explicite)."
trigger: always_on
---

# Gestion Proactive des Projets & Pomodoro (MANDATOIRE)

| Règle | Invariant |
|---|---|
| **Double lien vivant en tête** | Dès qu'un projet est abordé ➔ `[Nom Projet](file:///c:/Users/hjamet/Documents/VoiceNotes/.../NomProjet.md) · [🤖 Nom Projet](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/project_diffs/🤖%20NomProjet.md)` en première ligne. |
| **Contexte au tour 0 & Section `## Skills` (Lazy Loading)** | À chaque début de conversation sur un projet, lire la note maîtresse (si son chemin est connu) et `_agents/project_diffs/🤖 <Nom>.md` (zéro création de `task.md`), selon [task-tracking.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md) et [project-memory](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/project-memory/SKILL.md). **Chargement contextuel strict des Skills de Projet (`## Skills`)** : inspecter systématiquement la section `## Skills` en haut de la note maîtresse (`- [[skills/<nom>|Titre]] — <condition d'utilisation>`), mais **ne lire le contenu d'une note de skill (`skills/<nom>.md`) que si la tâche en cours remplit la condition décrite dans la puce (Lazy Loading)** ; dès que la condition est remplie (rédiger un message RP, générer une image, vérifier une mécanique, rédiger une section d'article), la lecture préalable du skill est **obligatoire**. **Boucle d'Auto-Évolution (`/learn` + Rasoir d'Ockham à taille constante)** : à chaque commentaire, critique ou rejet d'Henri sur une tâche ayant utilisé un skill de projet (ou si le message réellement envoyé par Henri diffère du `/draft`), déclencher une passe `/learn` sur `skills/<nom>.md` en réécrivant/fusionnant/condensant les règles existantes **sans inflation de taille** (zéro empilement en bas de note). |
| **Pas de démon ni d'alarme** | Aucune commande de fond permanente (`work`) ni alarme intrusive : le travail se fait librement, sans coupure. |
| **Clôture uniquement sur demande** | Une session ne se termine QUE quand Henri invoque le skill `project-memory` (ou `/one-shot`). Ne jamais déclarer soi-même une fin de session, même si tout est fait. Le bilan des chantiers, le calcul du temps réel et la mise à jour du registre sont réservés à cette invocation. |
| **Ressenti réservé à la clôture** | `ask_question` sur le ressenti uniquement lors de l'invocation interactive de `project-memory`, et seulement si Henri ne l'a pas déjà donné (jamais en `/one-shot`). |
| **Exemption veille et maintenance** | Veille proactive, maintenance mémorielle et cycles autonomes (hors session sur un projet métier) se clôturent sans question de ressenti, selon leur `SKILL.md`. |
| **Ajustement et calibrage** | Uniquement selon le skill dédié de gestion de projets (`project-memory`). |
