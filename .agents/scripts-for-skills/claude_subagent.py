#!/usr/bin/env python3
"""Pont Hybride Antigravity -> Claude Code / Antigravity CLI (mode headless `claude -p` ou `agy -p`).

Permet à un agent ou sous-agent Antigravity de déléguer une mission à Claude Opus 5.5
(ou Sonnet 5.5) soit via les crédits Claude Code (Anthropic OAuth), soit via les
crédits tiers Antigravity (`agy.exe --model claude-opus-5-5-medium`), avec routage
automatique optimisé pour exploiter les crédits inclus sans les gaspiller.

Exemples (PowerShell) :
  python claude_subagent_updated.py --prompt-file C:\\...\\brief.md --cwd C:\\...
  python claude_subagent_updated.py --quota-only
  python claude_subagent_updated.py --backend agy --prompt "Réponds uniquement ARTEFACT: ok.md"
  python claude_subagent_updated.py --backend claude --prompt "Réponds juste PONG"
  python claude_subagent_updated.py --resume <SESSION_ID> --prompt "Continue : corrige le test"

Sortie stdout standard :
  QUOTA_AGY_3P_5H: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XhYm>)
  QUOTA_AGY_3P_7D: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XjYh> | cible_96%: <cible>% | delta: <delta>%)
  QUOTA_SESSION_5H: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XhYm>)
  QUOTA_WEEK_7D: <utilization>% (reset <YYYY-MM-DD HH:MM>, reste <XjYh> | cible_96%: <cible>% | delta: <delta>%)
  BACKEND_RETENU: agy (claude-opus-5-5-medium)
  SESSION: <session_id>
  STATUS: ok | error (exit N)
  COST_USD: <estimation>
  LOG: <chemin du JSON brut complet>
  ARTEFACT: <chemin>
  ----- RESULT -----
  <réponse finale>
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
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_LOG_DIR = Path.home() / ".claude" / "antigravity-runs"

CONTRACT = """Tu interviens comme SOUS-AGENT d'un superviseur Antigravity qui travaille pour Henri Jamet.
- Tu n'as pas d'humain en face : ne pose aucune question, fais un choix raisonnable et signale-le.
- Respecte strictement le périmètre de fichiers donné par le brief ; tout écart est signalé comme `ÉCART`, jamais fait en silence.
- Pas de fallback silencieux, pas de valeur en dur, pas de try/except qui avale les erreurs.
- Si le brief demande un artefact, écris-le au chemin indiqué (sources brutes, chemins:Lxx-Lyy, commandes + code retour) et termine ta réponse par la ligne exacte `ARTEFACT: <chemin absolu>`.
- Termine toujours par une section `## Qu'est-ce que je pense qui échappe au superviseur ?`.
- Écris en français."""


def find_claude() -> Optional[str]:
    exe = shutil.which("claude")
    if exe:
        return exe
    candidates = [
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".local" / "bin" / "claude.exe",
        Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "claude.exe",
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def find_agy() -> Optional[str]:
    exe = shutil.which("agy")
    if exe:
        return exe
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe",
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / "AppData" / "Local" / "agy" / "bin" / "agy.exe",
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / ".local" / "bin" / "agy.exe",
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def refresh_claude_oauth_token(claude_bin: str) -> bool:
    """Déclenche le rafraîchissement natif du jeton OAuth via une exécution légère de Claude Code."""
    cred_path = Path.home() / ".claude" / ".credentials.json"
    mtime_before = cred_path.stat().st_mtime if cred_path.exists() else 0.0
    try:
        proc = subprocess.run(
            [claude_bin, "-p", "ok", "--output-format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            stdin=subprocess.DEVNULL,
        )
        if cred_path.exists() and cred_path.stat().st_mtime > mtime_before:
            return True
        return proc.returncode == 0
    except Exception as exc:
        sys.stderr.write(f"Warning: refresh_claude_oauth_token failed: {exc}\n")
        return False


def fetch_claude_quotas(claude_bin: Optional[str] = None) -> Optional[dict]:
    cred_path = Path.home() / ".claude" / ".credentials.json"
    if not cred_path.exists():
        return None

    def read_token() -> Tuple[Optional[str], int]:
        try:
            data = json.loads(cred_path.read_text(encoding="utf-8"))
            oauth = data.get("claudeAiOauth", {})
            return oauth.get("accessToken"), int(oauth.get("expiresAt") or 0)
        except Exception:
            return None, 0

    token, expires_at_ms = read_token()
    now_ms = int(time.time() * 1000)

    # Si le token expire dans moins de 60s ou est déjà expiré, rafraîchir en premier
    if (expires_at_ms <= now_ms + 60000) and claude_bin:
        refresh_claude_oauth_token(claude_bin)
        token, expires_at_ms = read_token()

    if not token:
        return None

    def do_request(t: str) -> Optional[dict]:
        url = "https://api.anthropic.com/api/oauth/usage"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {t}",
                "anthropic-beta": "oauth-2025-04-20",
                "User-Agent": "claude-code/2.1.309",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
        return None

    try:
        return do_request(token)
    except urllib.error.HTTPError as http_err:
        if http_err.code == 401 and claude_bin:
            # Token révoqué ou rejeté : tente un refresh immédiat
            if refresh_claude_oauth_token(claude_bin):
                token, _ = read_token()
                if token:
                    try:
                        return do_request(token)
                    except Exception as inner_exc:
                        sys.stderr.write(f"Warning: fetch_claude_quotas retry failed: {inner_exc}\n")
        sys.stderr.write(f"Warning: fetch_claude_quotas HTTP error: {http_err}\n")
    except Exception as exc:
        sys.stderr.write(f"Warning: fetch_claude_quotas failed: {exc}\n")
    return None


def compute_weekly_trajectory(reset_time_iso: str, used_pct: float) -> Tuple[float, float, str, str, str]:
    """Calcule la cible linéaire 96% et le delta pour une fenêtre hebdomadaire de 168h."""
    now = dt.datetime.now(dt.timezone.utc)
    try:
        clean_iso = reset_time_iso.replace("Z", "+00:00")
        reset_dt = dt.datetime.fromisoformat(clean_iso)
        if reset_dt.tzinfo is None:
            reset_dt = reset_dt.replace(tzinfo=dt.timezone.utc)
        rem_sec = max(0.0, (reset_dt - now).total_seconds())
        rem_days = int(rem_sec // 86400)
        rem_hours = int((rem_sec % 86400) // 3600)
        reset_local = reset_dt.astimezone().strftime("%Y-%m-%d %H:%M")
        reste_str = f"{rem_days}j{rem_hours:02d}h"

        rem_total_hours = rem_sec / 3600.0
        elapsed_hours = max(0.0, min(168.0, 168.0 - rem_total_hours))
        target_pct = round(96.0 * (elapsed_hours / 168.0), 1)
        delta = round(used_pct - target_pct, 1)
        sign = "+" if delta >= 0 else ""
        delta_str = f"{sign}{delta:.1f}%"
        return target_pct, delta, delta_str, reset_local, reste_str
    except Exception:
        return 0.0, 0.0, "+0.0%", reset_time_iso, "inconnu"


def compute_5h_remaining(reset_time_iso: str) -> Tuple[str, str]:
    now = dt.datetime.now(dt.timezone.utc)
    try:
        clean_iso = reset_time_iso.replace("Z", "+00:00")
        reset_dt = dt.datetime.fromisoformat(clean_iso)
        if reset_dt.tzinfo is None:
            reset_dt = reset_dt.replace(tzinfo=dt.timezone.utc)
        rem_sec = max(0.0, (reset_dt - now).total_seconds())
        rem_h = int(rem_sec // 3600)
        rem_m = int((rem_sec % 3600) // 60)
        reset_local = reset_dt.astimezone().strftime("%Y-%m-%d %H:%M")
        return reset_local, f"{rem_h}h{rem_m:02d}m"
    except Exception:
        return reset_time_iso, "inconnu"


def fetch_agy_quotas(agy_bin: Optional[str] = None) -> Optional[dict]:
    if not agy_bin:
        return None
    try:
        proc = subprocess.run(
            [agy_bin, "--output-format", "json", "-p", "/usage"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            stdin=subprocess.DEVNULL,
        )
        if proc.returncode != 0:
            return None
        data = json.loads(proc.stdout)
        groups = data.get("command", {}).get("data", {}).get("groups", [])
        if not groups:
            groups = data.get("groups", [])

        res: Dict[str, Any] = {"raw": data, "buckets": {}}
        for g in groups:
            for b in g.get("buckets", []):
                bid = b.get("id")
                rem_frac = float(b.get("remaining_fraction", 1.0))
                used_pct = round((1.0 - rem_frac) * 100.0, 1)
                reset_time = b.get("reset_time", "")

                bucket_info: Dict[str, Any] = {
                    "id": bid,
                    "name": b.get("name"),
                    "used_pct": used_pct,
                    "remaining_pct": round(rem_frac * 100.0, 1),
                    "reset_time": reset_time,
                }

                if b.get("window") == "weekly":
                    t_pct, delta_val, delta_str, r_local, reste = compute_weekly_trajectory(reset_time, used_pct)
                    bucket_info.update({
                        "cible_96": t_pct,
                        "delta": delta_val,
                        "delta_str": delta_str,
                        "reset_local": r_local,
                        "reste": reste,
                    })
                elif b.get("window") == "5h":
                    r_local, reste = compute_5h_remaining(reset_time)
                    bucket_info.update({
                        "reset_local": r_local,
                        "reste": reste,
                    })

                res["buckets"][bid] = bucket_info

        return res
    except Exception as exc:
        sys.stderr.write(f"Warning: fetch_agy_quotas failed: {exc}\n")
        return None


def format_quota_banner(
    claude_quotas: Optional[dict],
    agy_quotas: Optional[dict],
    chosen_backend: Optional[str] = None,
    chosen_model: Optional[str] = None,
) -> List[str]:
    lines: List[str] = []

    # 1. Antigravity 3P Quotas (Claude Opus / Sonnet)
    if agy_quotas and "buckets" in agy_quotas:
        b_3p_5h = agy_quotas["buckets"].get("3p-5h")
        if b_3p_5h:
            lines.append(
                f"QUOTA_AGY_3P_5H: {b_3p_5h['used_pct']:.1f}% (reset {b_3p_5h.get('reset_local', '')}, reste {b_3p_5h.get('reste', '')})"
            )
        b_3p_7d = agy_quotas["buckets"].get("3p-weekly")
        if b_3p_7d:
            lines.append(
                f"QUOTA_AGY_3P_7D: {b_3p_7d['used_pct']:.1f}% (reset {b_3p_7d.get('reset_local', '')}, reste {b_3p_7d.get('reste', '')} | "
                f"cible_96%: {b_3p_7d.get('cible_96', 0.0):.1f}% | delta: {b_3p_7d.get('delta_str', '')})"
            )

    # 2. Claude Code Quotas (Anthropic direct)
    if claude_quotas:
        fh = claude_quotas.get("five_hour")
        if fh and "utilization" in fh and fh.get("resets_at"):
            util_5h = float(fh["utilization"])
            r_local, rem = compute_5h_remaining(fh["resets_at"])
            lines.append(f"QUOTA_SESSION_5H: {util_5h:.1f}% (reset {r_local}, reste {rem})")

        sd = claude_quotas.get("seven_day")
        if sd and "utilization" in sd and sd.get("resets_at"):
            util_7d = float(sd["utilization"])
            t_pct, delta_val, delta_str, r_local, rem = compute_weekly_trajectory(sd["resets_at"], util_7d)
            lines.append(
                f"QUOTA_WEEK_7D: {util_7d:.1f}% (reset {r_local}, reste {rem} | "
                f"cible_96%: {t_pct:.1f}% | delta: {delta_str})"
            )
    else:
        lines.append("QUOTA_SESSION_5H: indisponible")
        lines.append("QUOTA_WEEK_7D: indisponible")

    if chosen_backend:
        mod_desc = f" ({chosen_model})" if chosen_model else ""
        lines.append(f"BACKEND_RETENU: {chosen_backend}{mod_desc}")

    return lines


def map_model_for_agy(model: str, effort: str) -> str:
    m = model.lower()
    eff = effort if effort in ("low", "medium", "high") else "medium"
    if "opus" in m:
        return f"claude-opus-5-5-{eff}"
    if "sonnet" in m:
        return f"claude-sonnet-5-5-{eff}"
    if any(m.startswith(prefix) for prefix in ("claude-", "gemini-", "gpt-")):
        return model
    return f"claude-opus-5-5-{eff}"


def select_optimal_backend(
    backend_arg: str,
    claude_bin: Optional[str],
    agy_bin: Optional[str],
    claude_quotas: Optional[dict],
    agy_quotas: Optional[dict],
    model: str,
    effort: str,
) -> Tuple[str, str]:
    """Sélectionne le backend (agy ou claude) et le modèle exact selon la stratégie d'optimisation."""
    if backend_arg == "agy":
        if not agy_bin:
            sys.exit("ERREUR: binaire `agy` introuvable mais `--backend agy` spécifié.")
        return "agy", map_model_for_agy(model, effort)

    if backend_arg == "claude":
        if not claude_bin:
            sys.exit("ERREUR: binaire `claude` introuvable mais `--backend claude` spécifié.")
        return "claude", model

    # Mode "auto"
    agy_available = bool(agy_bin)
    claude_available = bool(claude_bin)

    if not agy_available and not claude_available:
        sys.exit("ERREUR: Ni `agy` ni `claude` ne sont disponibles sur cette machine.")
    if not agy_available:
        return "claude", model
    if not claude_available:
        return "agy", map_model_for_agy(model, effort)

    # Vérification des crédits Antigravity 3P
    buckets = agy_quotas.get("buckets", {}) if agy_quotas else {}
    b_3p_5h = buckets.get("3p-5h", {})
    b_3p_7d = buckets.get("3p-weekly", {})
    agy_3p_5h_used = float(b_3p_5h.get("used_pct", 0.0))
    agy_3p_7d_used = float(b_3p_7d.get("used_pct", 0.0))
    agy_3p_delta = float(b_3p_7d.get("delta", 0.0))

    # Vérification des crédits Claude Code
    claude_5h_used = 0.0
    claude_7d_used = 0.0
    if claude_quotas:
        fh = claude_quotas.get("five_hour", {})
        sd = claude_quotas.get("seven_day", {})
        claude_5h_used = float(fh.get("utilization", 0.0))
        claude_7d_used = float(sd.get("utilization", 0.0))

    agy_usable = (agy_3p_5h_used < 85.0) and (agy_3p_7d_used < 95.0)
    claude_saturated = (claude_5h_used >= 85.0) or (claude_7d_used >= 95.0) or (claude_quotas is None)

    # Règle d'Henri : consommer de façon optimale les crédits Antigravity Claude Opus
    if agy_usable:
        if agy_3p_delta <= 5.0 or claude_saturated:
            return "agy", map_model_for_agy(model, effort)
        return "claude", model

    return "claude", model


def run_via_agy(
    agy_bin: str,
    prompt: str,
    model: str,
    effort: str,
    cwd: str,
    timeout: int,
    log_dir: Path,
    artefact: Optional[str] = None,
    resume: Optional[str] = None,
    add_dirs: Optional[List[str]] = None,
    mode: str = "auto",
) -> Tuple[int, dict]:
    cmd = [
        agy_bin,
        "--model", model,
        "--dangerously-skip-permissions",
        "--output-format", "json",
    ]
    if resume:
        cmd += ["--conversation", resume]
    if add_dirs:
        for d in add_dirs:
            cmd += ["--add-dir", d]
    if effort:
        cmd += ["--effort", effort]
    if mode in ("accept-edits", "auto", "plan"):
        cmd += ["--mode", mode]
    cmd += ["-p", prompt]

    start_t = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return 124, {"is_error": True, "error": f"Timeout {timeout}s"}

    dur = time.time() - start_t
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"agy_{dt.datetime.now():%Y%m%d_%H%M%S}.json"

    try:
        raw_data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        log_path.write_text(proc.stdout + "\n--- STDERR ---\n" + proc.stderr, encoding="utf-8")
        return proc.returncode or 1, {
            "backend": "agy",
            "is_error": True,
            "session_id": "?",
            "log_path": str(log_path),
            "result": (proc.stdout or proc.stderr).strip()[:4000],
            "returncode": proc.returncode,
        }

    status = raw_data.get("status", "SUCCESS")
    is_error = (status != "SUCCESS") or (proc.returncode != 0)
    data = {
        "backend": "agy",
        "session_id": raw_data.get("conversation_id", "?"),
        "model": model,
        "duration_seconds": raw_data.get("duration_seconds", round(dur, 2)),
        "num_turns": raw_data.get("num_turns", 1),
        "usage": raw_data.get("usage", {}),
        "total_cost_usd": 0.0,
        "is_error": is_error,
        "status": status,
        "result": raw_data.get("response", ""),
        "raw_response": raw_data,
        "log_path": str(log_path),
    }
    log_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return (proc.returncode if not is_error else (proc.returncode or 1)), data


def run_via_claude(
    claude_bin: str,
    prompt: str,
    model: str,
    effort: str,
    cwd: str,
    timeout: int,
    log_dir: Path,
    mode: str = "bypassPermissions",
    resume: Optional[str] = None,
    add_dirs: Optional[List[str]] = None,
    allowed_tools: str = "",
    no_contract: bool = False,
) -> Tuple[int, dict]:
    cmd = [claude_bin, "-p", prompt, "--output-format", "json"]
    if mode == "bypassPermissions":
        cmd += ["--dangerously-skip-permissions", "--permission-mode", "bypassPermissions"]
    else:
        cmd += ["--permission-mode", mode]
    if effort:
        cmd += ["--effort", effort]
    if not no_contract:
        cmd += ["--append-system-prompt", CONTRACT]
    if resume:
        cmd += ["--resume", resume]
    if model:
        cmd += ["--model", model]
    if allowed_tools:
        cmd += ["--allowedTools", allowed_tools]
    if add_dirs:
        for d in add_dirs:
            cmd += ["--add-dir", d]

    env = os.environ.copy()
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if git_bash.exists() and "CLAUDE_CODE_GIT_BASH_PATH" not in env:
        env["CLAUDE_CODE_GIT_BASH_PATH"] = str(git_bash)

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            stdin=subprocess.DEVNULL,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return 124, {"is_error": True, "error": f"Timeout {timeout}s"}

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"claude_{dt.datetime.now():%Y%m%d_%H%M%S}.json"

    try:
        raw_data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        log_path.write_text(proc.stdout + "\n--- STDERR ---\n" + proc.stderr, encoding="utf-8")
        return proc.returncode or 1, {
            "backend": "claude",
            "is_error": True,
            "session_id": "?",
            "log_path": str(log_path),
            "result": (proc.stdout or proc.stderr).strip()[:4000],
            "returncode": proc.returncode,
        }

    raw_data["backend"] = "claude"
    raw_data["log_path"] = str(log_path)
    log_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")
    is_error = bool(raw_data.get("is_error")) or (proc.returncode != 0)
    return (proc.returncode if not is_error else (proc.returncode or 1)), raw_data


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompt", help="Brief en ligne (court).")
    ap.add_argument("--prompt-file", help="Chemin d'un fichier .md contenant le brief (recommandé).")
    ap.add_argument("--backend", default="auto", choices=["auto", "agy", "claude"], help="Backend d'exécution (défaut auto).")
    ap.add_argument("--quota-only", action="store_true", help="Affiche uniquement les quotas et quitte.")
    ap.add_argument("--cwd", default=os.getcwd(), help="Répertoire de travail de l'agent.")
    ap.add_argument("--add-dir", action="append", default=[], help="Répertoire supplémentaire accessible (répétable).")
    ap.add_argument("--resume", help="session_id / conversation_id d'un run précédent pour continuer.")
    ap.add_argument(
        "--mode",
        default="bypassPermissions",
        choices=["plan", "default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "accept-edits"],
        help="Mode de permission (défaut bypassPermissions).",
    )
    ap.add_argument(
        "--effort",
        default="medium",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="Niveau d'effort de raisonnement (défaut medium).",
    )
    ap.add_argument("--model", default="opus", help="Ex. opus, sonnet, claude-opus-5-5-medium (défaut opus).")
    ap.add_argument("--allowed-tools", default="", help='Ex. "Bash(git *),Bash(python *),WebSearch".')
    ap.add_argument("--artefact", help="Chemin absolu attendu de l'artefact de retour (vérifié après le run).")
    ap.add_argument("--timeout", type=int, default=3600, help="Timeout en secondes (défaut 3600).")
    ap.add_argument("--no-contract", action="store_true", help="Ne pas ajouter le contrat sous-agent au system prompt.")
    ap.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    a = ap.parse_args()

    claude_bin = find_claude()
    agy_bin = find_agy()

    claude_quotas = fetch_claude_quotas(claude_bin)
    agy_quotas = fetch_agy_quotas(agy_bin)

    if a.quota_only:
        lines = format_quota_banner(claude_quotas, agy_quotas)
        for l in lines:
            print(l)
        return 0

    if not a.prompt and not a.prompt_file:
        ap.error("L'un des arguments --prompt ou --prompt-file est requis (sauf si --quota-only est spécifié).")

    prompt = Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else (a.prompt or "")
    if a.artefact:
        prompt += f"\n\nÉcris ton artefact de retour exactement ici : {a.artefact}"

    chosen_backend, chosen_model = select_optimal_backend(
        backend_arg=a.backend,
        claude_bin=claude_bin,
        agy_bin=agy_bin,
        claude_quotas=claude_quotas,
        agy_quotas=agy_quotas,
        model=a.model,
        effort=a.effort,
    )

    quota_lines = format_quota_banner(claude_quotas, agy_quotas, chosen_backend=chosen_backend, chosen_model=chosen_model)

    log_dir = Path(a.log_dir)

    if chosen_backend == "agy":
        ret, data = run_via_agy(
            agy_bin=agy_bin,  # type: ignore[arg-type]
            prompt=prompt,
            model=chosen_model,
            effort=a.effort,
            cwd=a.cwd,
            timeout=a.timeout,
            log_dir=log_dir,
            artefact=a.artefact,
            resume=a.resume,
            add_dirs=a.add_dir,
            mode="auto" if a.mode in ("bypassPermissions", "auto", "default") else a.mode,
        )
    else:
        ret, data = run_via_claude(
            claude_bin=claude_bin,  # type: ignore[arg-type]
            prompt=prompt,
            model=chosen_model,
            effort=a.effort,
            cwd=a.cwd,
            timeout=a.timeout,
            log_dir=log_dir,
            mode=a.mode,
            resume=a.resume,
            add_dirs=a.add_dir,
            allowed_tools=a.allowed_tools,
            no_contract=a.no_contract,
        )

    for ql in quota_lines:
        print(ql)

    if ret == 124:
        print(f"STATUS: error (timeout {a.timeout}s)")
        return 124

    sess_id = data.get("session_id") or data.get("conversation_id", "?")
    cost_usd = data.get("total_cost_usd", 0.0)
    is_err = bool(data.get("is_error")) or (ret != 0)

    print(f"SESSION: {sess_id}")
    print(f"STATUS: {'error (exit %d)' % ret if is_err else 'ok'}")
    print(f"COST_USD: {cost_usd}")
    print(f"LOG: {data.get('log_path', '?')}")
    if a.artefact and Path(a.artefact).exists():
        print(f"ARTEFACT: {a.artefact}")
    print("----- RESULT -----")
    print(data.get("result", ""))
    return ret


if __name__ == "__main__":
    sys.exit(main())
