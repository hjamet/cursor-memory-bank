---
name: claude-code
description: "Déléguer une mission à Claude Code (Anthropic, Opus medium en full access) comme sous-agent autonome externe via la CLI headless `claude -p`, appelée à travers le pont `claude_subagent.py` avec suivi automatique des quotas de session (5h) et de semaine (7j). Alternative privilégiée aux sous-agents `inherit` pour un second avis indépendant, du code complexe/sensible de bout en bout ou une mission autonome."
---

# Comment faire travailler Claude Code comme sous-agent d'Antigravity ?

Claude Code est l'agent en ligne de commande d'Anthropic. En mode headless (`claude -p`), il travaille de bout en bout en totale autonomie (lecture, édition, shell Git Bash, recherche web, sous-agents internes) puis rend un résultat JSON et un artefact de sources. Le pont [`claude_subagent.py`](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/claude_subagent.py) encapsule l'appel, configure par défaut **Opus (`medium`) en *full access***, et remonte automatiquement les quotas de **session (5h)** et de **semaine (7j)** ainsi que la cible linéaire hebdomadaire (96 %), en conformité avec [sous-agents.md](file:///C:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md).

## 🎯 Quand l'utiliser ? (Sélectivité Qualitative & Trajectoire Hebdomadaire)

- **Sélectivité stricte — Zéro gaspillage sur des tâches triviales** *(directive d'Henri, 05/11/2026)* : Claude Opus étant un modèle très puissant doté d'une perspective cognitive distincte de Gemini, **ne jamais brûler ses jetons en début de semaine sur des tâches simples ou mécaniques juste pour consommer du quota**. L'objectif est d'atteindre ~96 % du quota hebdomadaire (fenêtres glissantes de 5h et 7j) à la fin de la semaine en réservant exclusivement Claude aux missions où sa valeur ajoutée est maximale :
  1. **Vision différente & Second avis indépendant hors chambre d'écho Gemini** : revue critique de fond d'un article scientifique, d'un mémoire de Master, d'une architecture ou d'un choix méthodologique.
  2. **Tâches très complexes de bout en bout en autonomie** : refactoring profond, débogage algorithmique ou mathématique ardu, rédaction/chirurgie LaTeX délicate.
  3. **Code ou action à risque sensible/irréversible** : là où `flash` est formellement proscrit.
- **Sur demande explicite d'Henri** (« fais bosser Claude », « demande à Claude »).

## 🔗 Synchronisation automatique des Règles & Skills (Zéro doublon)

- Les règles (`_agents/rules/*.md`) et les skills (`_agents/skills/*/SKILL.md`) d'Antigravity sont reliés **uniquement au niveau global utilisateur** (`%USERPROFILE%\.claude\rules` et `%USERPROFILE%\.claude\skills`) par des **jonctions NTFS Windows**.
- **Pourquoi uniquement dans `%USERPROFILE%\.claude\` ?** Si un dossier `.claude\` existait aussi dans `VoiceNotes\`, Claude Code injecterait deux fois toutes les règles et tous les skills lorsqu'il travaille dans le coffre. En ne posant la jonction qu'au niveau global `%USERPROFILE%\.claude\`, les règles et skills sont chargés **une seule fois**, quel que soit le répertoire `--cwd` (`VoiceNotes` ou `~/Documents/code/<projet>`), et toute modification par Antigravity est instantanément active pour Claude.
- Le fichier `%USERPROFILE%\.claude\CLAUDE.md` précise à Claude qu'il agit comme agent d'exécution autonome (non soumis à l'interdiction d'outils du Superviseur Aveugle) tout en appliquant strictement `coffre-obsidian.md`, `bonnes-pratiques-developpement.md`, `zero-trust.md` et `web-playwright.md`.

## 🚀 Comment l'appeler ?

1. **Consulter les quotas (Session 5h & Semaine 7j) sans lancer de prompt** :
```powershell
python "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\claude_subagent.py" --quota-only
```

2. **Lancer une mission complète directement depuis le superviseur** : écrire le brief dans un fichier `brief_claude_<sujet>.md` (objectif, chemins absolus, périmètre, format d'artefact attendu), puis le **superviseur principal appelle directement `run_command`** (`WaitMsBeforeAsync=500`, unique commande autorisée au superviseur car équivalente à `invoke_subagent` — ne jamais passer par un sous-agent `flash` intermédiaire pour lancer Claude) :
```powershell
python "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\claude_subagent.py" `
  --prompt-file "<chemin>\brief_claude_<sujet>.md" `
  --cwd "<racine du projet>" `
  --artefact "<chemin absolu>\sources_claude.md"
```
*(Par défaut : `--model opus`, `--effort medium`, `--mode bypassPermissions` avec `--dangerously-skip-permissions` et `CLAUDE_CODE_GIT_BASH_PATH` pointant vers Git Bash Windows. **Invariant OAuth strict : un seul processus `claude` à la fois & Zéro test destructif sur `/v1/oauth/token`** — le refresh token OAuth d'Anthropic étant à rotation unique et Cloudflare filtrant `User-Agent: claude-code/*` en HTTP 429 au profit de `axios/1.7.9`, ne jamais lancer deux commandes `claude` en parallèle ni appeler `platform.claude.com/v1/oauth/token` dans un script de test sans persister immédiatement le nouveau couple `accessToken`/`refreshToken` dans `~/.claude/.credentials.json`, sous peine de révoquer la session).*

3. **Lire la sortie standard** :

| Ligne | Usage |
|---|---|
| `SESSION: <id>` | à repasser avec `--resume <id>` pour continuer la **même** conversation Claude |
| `STATUS: ok / error` | succès ou échec |
| `COST_USD:` | estimation équivalente en USD de la session |
| `QUOTA_SESSION_5H:` | % utilisé sur la fenêtre de 5h + heure locale de reset |
| `QUOTA_WEEK_7D:` | % utilisé sur la fenêtre de 7j + heure de reset + comparaison à la **cible linéaire 96 %** |
| `LOG:` | trace JSON complète dans `%USERPROFILE%\.claude\antigravity-runs\` (hors du coffre Obsidian) |
| `ARTEFACT:` | chemin de l'artefact de sources écrit par Claude |
| `----- RESULT -----` | réponse finale de Claude |

## 🧩 Options utiles

- `--model opus|sonnet` (défaut : `opus`)
- `--effort low|medium|high|xhigh|max` (défaut : `medium`)
- `--mode bypassPermissions|plan|acceptEdits|auto` (défaut : `bypassPermissions` = *full access* ; utiliser `plan` uniquement si l'on veut contraindre un éclaireur/auditeur à la lecture seule stricte)
- `--resume <session_id>` : poursuivre un échange multi-tours avec la même instance Claude
- `--add-dir <chemin>` (répétable) : autoriser un répertoire supplémentaire
- `--no-contract` : ne pas ajouter le contrat d'artefact sous-agent
