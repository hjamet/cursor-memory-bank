# 🤝 Délégation Proactive à Claude Opus (`Antigravity Claude` & `Claude Code`) — Équilibrage des Quotas

*(Règle applicable exclusivement au coordinateur Antigravity / Gemini — jamais à l'intérieur d'un sous-agent déjà exécuté sous Claude, afin d'éviter toute récursion.)*

| Règle | Directive |
|---|---|
| **Réflexe quota avant tout sous-agent ou chantier autonome** | Avant de lancer un sous-agent natif (`invoke_subagent`) ou dès qu'une session comporte une sous-tâche autonome substantielle et bien délimitée (développement/refactoring dans un dépôt `~/Documents/code/`, audit critique indépendant hors chambre d'écho Gemini, chantier parallèle en `/one-shot`), interroger les deux quotas Claude via `python "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\claude_subagent.py" --quota-only`. |
| **Activation & équilibrage des 3 pools IA** | Si `Antigravity Claude` (`3p-weekly`) ou `Claude Code (Opus)` (`seven_day`) est nettement sous-utilisé (`delta_7d < 0 %` face à la trajectoire linéaire 96 % et fenêtre 5h `< 80 %`), **privilégier la délégation via `claude_subagent.py` (`--backend auto` par défaut, ou `--backend claude` / `--backend agy` sur deux tâches disjointes en parallèle)** selon le skill [claude-code](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/skills/claude-code/SKILL.md). |
| **Périmètre propre & zéro sur-découpage** | Réserver la délégation à de vrais chantiers autonomes (code, audit, vérification, rédaction/revue indépendante) avec brief fichier (`--prompt-file`) et artefact de retour (`--artefact`), sans fragmenter des micro-éditions triviales qu'il est plus simple d'exécuter directement dans la conversation principale. |
