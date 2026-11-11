# Archive — Architecture Argon « Superviseur Aveugle + Sous-Agents » (11/11/2026)

Snapshot intégral pré-nettoyage avant le passage de Google Antigravity au fonctionnement **100 % natif mono-agent** sous **Gemini 4 Carbon** (11 novembre 2026).

## Contenu de l'archive

- `_agents/rules/` : les 8 règles originales (incluant `sous-agents.md` et `superviseur-aveugle.md`).
- `_agents/agents/` : les 4 sous-agents personnalisés (`eclaireur.md`, `executant.md`, `auditeur-alignement.md`, `superviseur-projet.md`).
- `_agents/skills/` : tous les skills globaux d'`_agents/skills/` dans leur version multi-agent.
- `vault_skills/` : les skills intra-projet de `VoiceNotes/skills/` avant nettoyage.
- `claude/CLAUDE.md` : configuration `%USERPROFILE%\.claude\CLAUDE.md` avant nettoyage.
- `sidecars/daily-dream_sidecar.json` : configuration de l'automation quotidienne `/dream` avant nettoyage.

## Restauration rapide (PowerShell)

```powershell
$Arch = "C:\Users\Jamet\Documents\code\cursor-memory-bank\archive\argon_blind_supervisor_2026-11-11"
$VN   = "C:\Users\Jamet\Documents\VoiceNotes"
Copy-Item "$Arch\_agents\rules\*"  "$VN\_agents\rules\" -Force
New-Item -ItemType Directory -Force "$VN\_agents\agents" | Out-Null
Copy-Item "$Arch\_agents\agents\*" "$VN\_agents\agents\" -Force
Copy-Item "$Arch\_agents\skills\*" "$VN\_agents\skills\" -Recurse -Force
Copy-Item "$Arch\vault_skills\*"    "$VN\skills\" -Recurse -Force
Copy-Item "$Arch\claude\CLAUDE.md"  "$env:USERPROFILE\.claude\CLAUDE.md" -Force
```
