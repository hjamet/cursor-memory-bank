#!/usr/bin/env python3
"""Pont Antigravity -> Claude Code (mode headless `claude -p`).

Permet à un agent ou sous-agent Antigravity de déléguer une mission à Claude
Code comme à un sous-agent, via `run_command`, sans serveur MCP (donc sans
timeout MCP).

Exemples (PowerShell) :
  python claude_subagent.py --prompt-file brief_claude.md --cwd .
  python claude_subagent.py --quota-only
  python claude_subagent.py --prompt "Réponds juste PONG" --mode plan --no-contract
  python claude_subagent.py --resume <SESSION_ID> --prompt "Continue : corrige maintenant le test"

Sortie stdout (toujours dans cet ordre) :
  QUOTA_SESSION_5H: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XhYm>)
  QUOTA_WEEK_7D: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XjYh> | cible_96%: <cible_pct>% | delta: <delta>%)
  SESSION: <session_id>          -> à réutiliser avec --resume pour un échange multi-tours
  STATUS: ok | error (exit N)
  COST_USD: <estimation>
  LOG: <chemin du JSON brut complet>
  ARTEFACT: <chemin>             -> seulement si --artefact est fourni et que le fichier existe
  ----- RESULT -----
  <réponse finale de Claude>

Code retour : celui de `claude` (0 = succès).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_LOG_DIR = Path.home() / ".claude" / "antigravity-runs"
CONTRACT = """Tu interviens comme SOUS-AGENT d'un superviseur Antigravity qui travaille pour Henri Jamet.
- Tu n'as pas d'humain en face : ne pose aucune question, fais un choix raisonnable et signale-le.
- Respecte strictement le périmètre de fichiers donné par le brief ; tout écart est signalé comme `ÉCART`, jamais fait en silence.
- Pas de fallback silencieux, pas de valeur en dur, pas de try/except qui avale les erreurs.
- Si le brief demande un artefact, écris-le au chemin indiqué (sources brutes, chemins:Lxx-Lyy, commandes + code retour) et termine ta réponse par la ligne exacte `ARTEFACT: <chemin absolu>`.
- Termine toujours par une section `## Qu'est-ce que je pense qui échappe au superviseur ?`.
- Écris en français."""


def find_claude() -> str:
    exe = shutil.which("claude")
    if exe:
        return exe
    candidate = Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".local" / "bin" / "claude.exe"
    if candidate.exists():
        return str(candidate)
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        desktop_candidates = sorted(Path(local_appdata).glob("Claude-Data/*/claude-code/*/*/claude.exe"))
        if desktop_candidates:
            return str(desktop_candidates[-1])
    sys.exit(
        "ERREUR: exécutable `claude` introuvable. Installer Claude Code : "
        "`irm https://claude.ai/install.ps1 | iex` (PowerShell), puis rouvrir le terminal."
    )


def _refresh_claude_token(cred_path: Path, data: dict) -> str:
    oauth_data = data.get("claudeAiOauth", {})
    refresh_token = oauth_data.get("refreshToken")
    if not refresh_token:
        raise RuntimeError("refreshToken absent dans .credentials.json (claudeAiOauth)")
    scopes = oauth_data.get("scopes", [])
    scope_str = " ".join(scopes) if isinstance(scopes, list) else str(scopes)
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "9d1c250a-e61b-44d9-88ed-5944d1962f5e",
        "scope": scope_str,
    }
    req = urllib.request.Request(
        "https://platform.claude.com/v1/oauth/token",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "claude-code/2.1.309",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status == 200:
            res_data = json.loads(resp.read().decode("utf-8"))
            new_access_token = res_data.get("access_token")
            if new_access_token:
                oauth_data["accessToken"] = new_access_token
                if "refresh_token" in res_data:
                    oauth_data["refreshToken"] = res_data["refresh_token"]
                if "expires_in" in res_data:
                    oauth_data["expiresAt"] = int(time.time() * 1000) + int(res_data["expires_in"]) * 1000
                data["claudeAiOauth"] = oauth_data
                cred_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
                return new_access_token
    raise RuntimeError("Le rafraîchissement du token OAuth a échoué (réponse inattendue de platform.claude.com)")


def fetch_claude_quota() -> dict:
    cred_path = Path.home() / ".claude" / ".credentials.json"
    if not cred_path.exists():
        raise FileNotFoundError(f"Identifiants Claude introuvables : {cred_path}")

    def _query(token: str) -> dict:
        url = "https://api.anthropic.com/api/oauth/usage"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "anthropic-beta": "oauth-2025-04-20",
                "User-Agent": "claude-code/2.1.309",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
        raise RuntimeError("Usage API returned unexpected status")

    data = json.loads(cred_path.read_text(encoding="utf-8"))
    oauth_data = data.get("claudeAiOauth", {})
    token = oauth_data.get("accessToken")
    expires_at = oauth_data.get("expiresAt", 0)
    now_ms = int(time.time() * 1000)

    # Si token expiré ou expire dans moins de 60s, refresh préventif
    if expires_at and now_ms >= (expires_at - 60000):
        token = _refresh_claude_token(cred_path, data)

    if not token:
        raise RuntimeError("accessToken manquant dans .credentials.json (claudeAiOauth)")

    try:
        return _query(token)
    except urllib.error.HTTPError as http_err:
        if http_err.code == 401:
            refreshed = _refresh_claude_token(cred_path, data)
            return _query(refreshed)
        raise



fetch_quotas = fetch_claude_quota


def format_quotas(quota_data: dict) -> list[str]:
    lines = []
    now = dt.datetime.now(dt.timezone.utc)

    # 5h session quota
    fh = quota_data.get("five_hour")
    if fh and "utilization" in fh and fh.get("resets_at"):
        util_5h = float(fh["utilization"])
        reset_5h_dt = dt.datetime.fromisoformat(fh["resets_at"])
        rem_5h_sec = max(0.0, (reset_5h_dt - now).total_seconds())
        rem_5h_h = int(rem_5h_sec // 3600)
        rem_5h_m = int((rem_5h_sec % 3600) // 60)
        reset_5h_local = reset_5h_dt.astimezone().strftime("%Y-%m-%d %H:%M")
        lines.append(f"QUOTA_SESSION_5H: {util_5h:.1f}% (reset {reset_5h_local}, reste {rem_5h_h}h{rem_5h_m:02d}m)")

    # 7d weekly quota
    sd = quota_data.get("seven_day")
    if sd and "utilization" in sd and sd.get("resets_at"):
        util_7d = float(sd["utilization"])
        reset_7d_dt = dt.datetime.fromisoformat(sd["resets_at"])
        rem_7d_sec = max(0.0, (reset_7d_dt - now).total_seconds())
        rem_7d_days = int(rem_7d_sec // 86400)
        rem_7d_hours = int((rem_7d_sec % 86400) // 3600)
        reset_7d_local = reset_7d_dt.astimezone().strftime("%Y-%m-%d %H:%M")

        # Cible linéaire 96% sur fenêtre de 168h
        rem_hours = rem_7d_sec / 3600.0
        elapsed_hours = max(0.0, min(168.0, 168.0 - rem_hours))
        cible_pct = 96.0 * (elapsed_hours / 168.0)
        delta = util_7d - cible_pct
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"QUOTA_WEEK_7D: {util_7d:.1f}% (reset {reset_7d_local}, reste {rem_7d_days}j{rem_7d_hours:02d}h | "
            f"cible_96%: {cible_pct:.1f}% | delta: {sign}{delta:.1f}%)"
        )

    return lines


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", help="Brief en ligne (court).")
    ap.add_argument("--prompt-file", help="Chemin d'un fichier .md contenant le brief (recommandé).")
    ap.add_argument("--quota-only", action="store_true", help="Affiche uniquement les quotas 5h/7j et quitte.")
    ap.add_argument("--cwd", default=os.getcwd(), help="Répertoire de travail de Claude (racine du projet).")
    ap.add_argument("--add-dir", action="append", default=[], help="Répertoire supplémentaire accessible (répétable).")
    ap.add_argument("--resume", help="session_id d'un run précédent pour continuer la même conversation.")
    ap.add_argument(
        "--mode",
        default="bypassPermissions",
        choices=["plan", "default", "acceptEdits", "auto", "dontAsk", "bypassPermissions"],
        help="Mode de permission (défaut bypassPermissions ; `plan` = lecture seule).",
    )
    ap.add_argument(
        "--effort",
        default="medium",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="Niveau d'effort de raisonnement (défaut medium).",
    )
    ap.add_argument("--model", default="opus", help="Ex. opus, sonnet (défaut opus).")
    ap.add_argument("--allowed-tools", default="", help='Ex. "Bash(git *),Bash(python *),WebSearch".')
    ap.add_argument("--artefact", help="Chemin absolu attendu de l'artefact de retour (vérifié après le run).")
    ap.add_argument("--timeout", type=int, default=3600, help="Timeout en secondes (défaut 3600).")
    ap.add_argument("--no-contract", action="store_true", help="Ne pas ajouter le contrat sous-agent au system prompt.")
    ap.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    a = ap.parse_args()

    if a.quota_only:
        quota_data = fetch_quotas()
        for ql in format_quotas(quota_data):
            print(ql)
        return 0

    if not a.prompt and not a.prompt_file:
        ap.error("L'un des arguments --prompt ou --prompt-file est requis (sauf si --quota-only est spécifié).")

    prompt = Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else a.prompt
    if a.artefact:
        prompt += f"\n\nÉcris ton artefact de retour exactement ici : {a.artefact}"

    cmd = [find_claude(), "-p", prompt, "--output-format", "json"]
    if a.mode == "bypassPermissions":
        cmd += ["--dangerously-skip-permissions", "--permission-mode", "bypassPermissions"]
    else:
        cmd += ["--permission-mode", a.mode]
    if a.effort:
        cmd += ["--effort", a.effort]
    if not a.no_contract:
        cmd += ["--append-system-prompt", CONTRACT]
    if a.resume:
        cmd += ["--resume", a.resume]
    if a.model:
        cmd += ["--model", a.model]
    if a.allowed_tools:
        cmd += ["--allowedTools", a.allowed_tools]
    for d in a.add_dir:
        cmd += ["--add-dir", d]

    env = os.environ.copy()
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if git_bash.exists() and "CLAUDE_CODE_GIT_BASH_PATH" not in env:
        env["CLAUDE_CODE_GIT_BASH_PATH"] = str(git_bash)

    try:
        proc = subprocess.run(
            cmd,
            cwd=a.cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=a.timeout,
            stdin=subprocess.DEVNULL,
            env=env,
        )
    except subprocess.TimeoutExpired:
        quota_data = fetch_quotas()
        for ql in format_quotas(quota_data):
            print(ql)
        print(f"STATUS: error (timeout {a.timeout}s)")
        return 124

    quota_data = fetch_quotas()
    quota_lines = format_quotas(quota_data)

    log_dir = Path(a.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"claude_{dt.datetime.now():%Y%m%d_%H%M%S}.json"

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        log_path.write_text(proc.stdout + "\n--- STDERR ---\n" + proc.stderr, encoding="utf-8")
        for ql in quota_lines:
            print(ql)
        print(f"STATUS: error (exit {proc.returncode}, sortie non JSON)")
        print(f"LOG: {log_path}")
        print("----- RESULT -----")
        print((proc.stdout or proc.stderr).strip()[:4000])
        return proc.returncode or 1

    log_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    is_error = bool(data.get("is_error")) or proc.returncode != 0
    for ql in quota_lines:
        print(ql)
    print(f"SESSION: {data.get('session_id', '?')}")
    print(f"STATUS: {'error (exit %d)' % proc.returncode if is_error else 'ok'}")
    print(f"COST_USD: {data.get('total_cost_usd', '?')}")
    print(f"LOG: {log_path}")
    if a.artefact and Path(a.artefact).exists():
        print(f"ARTEFACT: {a.artefact}")
    print("----- RESULT -----")
    print(data.get("result", ""))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
