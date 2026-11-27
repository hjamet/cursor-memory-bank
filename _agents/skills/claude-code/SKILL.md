---
name: claude-code
description: "Déléguer de façon proactive ou sur demande une mission autonome à Claude Opus (Antigravity Claude agy.exe ou Claude Code claude -p) via le pont CLI unifié claude_subagent.py avec équilibrage automatique des quotas 5h et 7j."
---

# Comment déléguer une mission à Claude Opus en CLI (`claude-code`) ?

Le script [`claude_subagent.py`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/claude_subagent.py) permet au coordinateur Antigravity (Gemini) d'exécuter **Claude Opus (`medium`) en *full access*** à travers les deux pools de quotas affichés dans SlideFlow AGY :
- **`Antigravity Claude`** : via la CLI Antigravity (`agy.exe --model claude-opus-5-5-medium -p ...`, bucket `"Claude and GPT models"` `3p-weekly` / `3p-5h`) ;
- **`Claude Code (Opus)`** : via la CLI Anthropic (`claude -p --model opus --effort medium`, quota OAuth `api.anthropic.com/api/oauth/usage`).

Par défaut (`--backend auto`), le script compare les deux quotas (session 5h et semaine 7j face à la cible linéaire de 96 %) et route automatiquement l'appel vers le pool ayant le plus de marge disponible.

## 🎯 Quand l'utiliser ? (Délégation proactive pour équilibrer les 3 budgets IA)

- **Dès que l'agent Antigravity envisage un sous-agent ou identifie une sous-tâche autonome substantielle** (développement/refactoring isolé sur un dépôt de code, audit critique indépendant hors chambre d'écho Gemini, revue de code ou de manuscrit, chantier parallèle lors d'un `/one-shot` multi-projets) : **consulter d'abord `claude_subagent.py --quota-only`**. Si `Antigravity Claude` ou `Claude Code (Opus)` dispose d'une marge confortable (`delta_7d < 0 %` / budget hebdomadaire sous-utilisé et fenêtre 5h `< 80 %`), **privilégier `claude_subagent.py --backend auto` (ou répartir explicitement `--backend claude` et `--backend agy` sur 2 tâches parallèles)** plutôt que de tout consommer sur le seul quota Gemini.
- **Également sur demande explicite d'Henri** (invocation `/claude-code`, « fais bosser Claude », « demande un second avis à Claude »).
- **Garde-fou anti-récursion** : ne jamais appeler `claude_subagent.py` depuis l'intérieur d'une session déjà exécutée par Claude (`agy` Claude ou `claude -p`).

## 🔗 Synchronisation automatique des Règles & Skills (Zéro doublon)

- Les règles (`_agents/rules/*.md`) et les skills (`_agents/skills/*/SKILL.md`) sont reliés **uniquement au niveau global utilisateur** (`%USERPROFILE%\.claude\rules` et `%USERPROFILE%\.claude\skills`) par des **jonctions NTFS Windows**. *(Note : le sous-dossier `_agents/skills/synced/` est le cache automatique des skills internes `anthropic-skills` de Claude Code recréé à chaque lancement via la jonction `~/.claude/skills` — ne jamais chercher à le supprimer lors d'un audit `/dream`)*.
- **Pourquoi uniquement dans `%USERPROFILE%\.claude\` ?** Si un dossier `.claude\` existait aussi dans `VoiceNotes\`, Claude Code injecterait deux fois toutes les règles et tous les skills lorsqu'il travaille dans le coffre. En ne posant la jonction qu'au niveau global `%USERPROFILE%\.claude\`, les règles et skills sont chargés **une seule fois**, quel que soit le répertoire `--cwd` (`VoiceNotes` ou `~/Documents/code/<projet>`), et toute modification est instantanément active pour Claude.
- Le fichier `%USERPROFILE%\.claude\CLAUDE.md` rappelle à Claude l'application stricte de `coffre-obsidian.md`, `bonnes-pratiques-developpement.md`, `zero-trust.md` et `web-playwright.md`.

## 🚀 Comment l'appeler ?

1. **Consulter les deux quotas (`Antigravity Claude` & `Claude Code`) sans lancer de prompt** :
```powershell
python "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\claude_subagent.py" --quota-only
```

2. **Lancer une mission en CLI** : écrire le brief dans un fichier `brief_claude_<sujet>.md` (objectif, chemins absolus, périmètre), puis exécuter :
```powershell
python "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\claude_subagent.py" `
  --prompt-file "<chemin>\brief_claude_<sujet>.md" `
  --cwd "<racine du projet>" `
  --artefact "<chemin absolu>\result_claude.md"
```
*(Par défaut : `--backend auto`, `--model opus`, `--effort medium`, `--mode bypassPermissions` avec `--dangerously-skip-permissions`. **Invariant OAuth strict pour `claude`** : ne jamais appeler `platform.claude.com/v1/oauth/token` dans un script de test sans persister immédiatement le nouveau couple `accessToken`/`refreshToken` dans `~/.claude/.credentials.json`).*

3. **Lire la sortie standard** :

| Ligne | Usage |
|---|---|
| `BACKEND: agy / claude` | pool sélectionné automatiquement (`claude-opus-5-5-medium` via `agy.exe` ou `opus medium` via `claude`) |
| `SESSION: <id>` | à repasser avec `--resume <id>` pour continuer la **même** conversation |
| `STATUS: ok / error` | succès ou échec |
| `QUOTA_AGY_CLAUDE_5H / 7D:` | % utilisé sur 5h et 7j pour `Antigravity Claude` + comparaison à la **cible linéaire 96 %** |
| `QUOTA_CLAUDE_CODE_5H / 7D:` | % utilisé sur 5h et 7j pour `Claude Code (Opus)` + comparaison à la **cible linéaire 96 %** |
| `LOG:` | trace JSON complète dans `%USERPROFILE%\.claude\antigravity-runs\` |
| `ARTEFACT:` | chemin du fichier de sortie écrit par Claude |
| `----- RESULT -----` | réponse finale de Claude |

## 🧩 Options utiles

- `--backend auto|agy|claude` (défaut : `auto` — choisit le pool Opus ayant le `delta_7d` le plus bas sous les seuils de pause 85 %/96 %)
- `--model opus|sonnet` (défaut : `opus`)
- `--effort low|medium|high|xhigh|max` (défaut : `medium`)
- `--mode bypassPermissions|plan|acceptEdits|auto` (défaut : `bypassPermissions` = *full access* ; utiliser `plan` pour contraindre à la lecture seule)
- `--resume <session_id>` : poursuivre un échange multi-tours avec la même instance
- `--add-dir <chemin>` (répétable) : autoriser un répertoire supplémentaire
- `--no-contract` : ne pas ajouter de consigne de format d'artefact additionnelle
