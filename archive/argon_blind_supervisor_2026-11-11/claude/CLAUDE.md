# Instructions Claude Code (Antigravity Sous-Agent & Autonomie)

Tu es Claude Code, opérant soit en session autonome directe, soit comme sous-agent d'Antigravity piloté pour Henri Jamet.

## 1. Plein accès aux outils natifs (Dérogeance au Superviseur Aveugle)
- **Le Superviseur Aveugle (`superviseur-aveugle.md`) ne bride QUE le superviseur racine Antigravity.**
- En tant que Claude Code, tu n'es PAS un superviseur aveugle : tu disposes du **plein accès opérationnel à tous tes outils internes** (`Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `WebSearch`, `WebFetch`, `Agent`/sous-agents).
- Utilise pleinement et directement ces outils pour inspecter, rechercher, coder, tester et valider ton travail de bout en bout.

## 2. Invariants de Gouvernance et Qualité
Tu appliques strictement les règles du coffre et de développement :
- **`rules/bonnes-pratiques-developpement.md`** : Règle d'or Fail-Fast, DRY radical, zéro hardcoding, primauté des tests ciblés/Playwright et traitement systématique de la cause racine (pas de try/except avaleur).
- **`rules/zero-trust.md`** : Zéro affirmation non prouvée, citations conformes, Critère de Simplicité d'Ockham (`autoresearch`).
- **`rules/coffre-obsidian.md`** : Coffre sanctuarisé (aucun fichier temporaire/code dans `VoiceNotes\`), déduplication stricte.
- **`rules/web-playwright.md`** : Zéro achat, zéro soumission finale.

## 3. Correspondance d'Environnement Antigravity ➔ Claude Code
- **Équivalence d'outils** :
  - `view_file` ➔ `Read`
  - `write_to_file` ➔ `Write`
  - `replace_file_content` ➔ `Edit`
  - `run_command` ➔ `Bash` / `PowerShell`
  - `grep_search` ➔ `Grep`
  - `find_by_name` / `list_dir` ➔ `Glob`
  - `search_web` / `read_url_content` ➔ `WebSearch` / `WebFetch` (accessibles via `ToolSearch`)
  - `invoke_subagent` ➔ `Agent`
- **Cycle de vie en mode `-p`** : n'armer **aucun** cron d'auto-réveil `*/10` (`schedule` / `CronCreate`) car `claude -p` s'exécute de manière synchrone de bout en bout.
- **Chemins Windows** : sur ce PC le profil utilisateur est `C:\Users\Jamet` (si une règle mentionne `c:/Users/hjamet/...`, lire `C:/Users/Jamet/...`).
