#!/usr/bin/env python3
"""
token_telemetry_cli_updated.py — CLI enrichie de télémétrie des tokens, sessions et quotas Antigravity & Claude Code.
Analyse les transcripts Antigravity et les logs de runs Claude Code / Antigravity dans ~/.claude/antigravity-runs.
Intègre le Calculateur de Trajectoire Tripartite des Quotas (--quota-pace) :
1. Antigravity Crédits 3P (Claude Opus 5.5 / Sonnet 5.5)
2. Claude Code (Anthropic OAuth)
3. Antigravity Gemini Models (Pro / Flash)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


@dataclass
class SubagentInfo:
    """Informations de déclaration d'un sous-agent."""
    conversation_id: str
    parent_id: str
    type_name: str
    model: str
    role: str


@dataclass
class ConversationStats:
    """Métriques et statistiques agrégées d'une conversation unique."""
    conversation_id: str
    category: str
    model: str
    role: str
    parent_id: Optional[str]
    mtime: datetime
    planner_turns: int
    steps: int
    input_tokens: int
    cache_read_tokens: int
    output_tokens: int
    total_tokens: int
    full_size_bytes: int
    tool_errors: int
    cron_post_artefact: int
    budget_exceeded: bool


@dataclass
class ClaudeRunStats:
    """Métriques d'un run Claude Code ou Antigravity autonome."""
    run_id: str
    backend: str
    timestamp: datetime
    model: str
    duration_sec: float
    num_turns: int
    total_cost_usd: float
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    total_tokens: int
    is_error: bool
    subtype: str
    result_preview: str


def clean_str(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s


def normalize_model(model_raw: str) -> str:
    m = model_raw.lower()
    if "flash" in m:
        return "flash"
    if "opus" in m:
        return "claude-opus"
    if "inherit" in m or "sonnet" in m or "gpt" in m or "pro" in m:
        return "inherit"
    return "unknown"


def normalize_category(type_name_raw: str, default: str = "unknown") -> str:
    t = type_name_raw.lower().strip()
    if "eclaireur" in t or "éclaireur" in t:
        return "eclaireur"
    if "executant" in t or "exécutant" in t:
        return "executant"
    if "auditeur" in t or "audit" in t:
        return "auditeur-alignement"
    if "superviseur-projet" in t or "superviseur_projet" in t:
        return "superviseur-projet"
    if "claude" in t:
        return "claude-subagent"
    if "image" in t:
        return "image-generator"
    if "self" in t:
        return "self"
    if "root" in t:
        return "ROOT"
    return default


def parse_subagent_registry(brain_dir: Path) -> Dict[str, SubagentInfo]:
    registry: Dict[str, SubagentInfo] = {}

    for conv_dir in brain_dir.iterdir():
        if not conv_dir.is_dir():
            continue

        tfile = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if not tfile.exists():
            tfile = conv_dir / "transcript.jsonl"
            if not tfile.exists():
                continue

        try:
            with open(tfile, "r", encoding="utf-8", errors="ignore") as f:
                lines = [json.loads(l) for l in f if l.strip()]
        except Exception:
            continue

        for i, line in enumerate(lines):
            tool_calls = line.get("tool_calls", [])
            line_sub_specs: List[Tuple[str, str, str]] = []
            for tc in tool_calls:
                name = tc.get("name") or tc.get("tool_name")
                if name != "invoke_subagent":
                    continue

                args = tc.get("args") or tc.get("arguments") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}

                if "Subagents" in args:
                    raw_subs = args["Subagents"]
                    if isinstance(raw_subs, str):
                        try:
                            raw_subs = json.loads(raw_subs)
                        except Exception:
                            raw_subs = []
                    if isinstance(raw_subs, list):
                        for s in raw_subs:
                            if isinstance(s, dict):
                                line_sub_specs.append((
                                    normalize_category(clean_str(s.get("TypeName"))),
                                    normalize_model(clean_str(s.get("Model"))),
                                    clean_str(s.get("Role")),
                                ))
                else:
                    t_name = normalize_category(clean_str(args.get("TypeName")))
                    mod = normalize_model(clean_str(args.get("Model")))
                    rol = clean_str(args.get("Role"))
                    line_sub_specs.append((t_name, mod, rol))

            if not line_sub_specs:
                continue

            found_ids: List[str] = []
            max_scan = min(i + 1 + max(len(tool_calls), len(line_sub_specs)) + 12, len(lines))
            for j in range(i + 1, max_scan):
                res = lines[j]
                content = str(res.get("content", ""))
                for m in re.finditer(r'"conversationId":\s*"([a-f0-9\-]+)"', content):
                    cid = m.group(1)
                    if cid not in found_ids:
                        found_ids.append(cid)
                if len(found_ids) >= len(line_sub_specs):
                    break

            for (cat, mod, rol), cid in zip(line_sub_specs, found_ids):
                registry[cid] = SubagentInfo(
                    conversation_id=cid,
                    parent_id=conv_dir.name,
                    type_name=cat,
                    model=mod,
                    role=rol,
                )

    return registry


def detect_fallback_category(conv_dir: Path, lines: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    scratch_dir = conv_dir / "scratch"
    if scratch_dir.is_dir():
        for f in scratch_dir.iterdir():
            fn = f.name.lower()
            if "sources_eclaireur" in fn:
                return "eclaireur", "unknown", "Éclaireur (déduit via scratch)"
            if "sources_executant" in fn:
                return "executant", "unknown", "Exécutant (déduit via scratch)"
            if "sources_audit" in fn:
                return "auditeur-alignement", "unknown", "Auditeur (déduit via scratch)"

    for line in lines[:5]:
        content = str(line.get("content", "")).lower()
        if "tu es un éclaireur" in content or "sources_eclaireur" in content:
            return "eclaireur", "unknown", "Éclaireur (déduit via prompt)"
        if "tu es un exécutant" in content or "sources_executant" in content or "implementation_plan" in content:
            return "executant", "unknown", "Exécutant (déduit via prompt)"
        if "tu es un auditeur" in content or "sources_audit" in content or "auditeur-alignement" in content:
            return "auditeur-alignement", "unknown", "Auditeur (déduit via prompt)"
        if "tu es le **superviseur de projet**" in content or "superviseur-projet" in content:
            return "superviseur-projet", "inherit", "Superviseur Projet (déduit via prompt)"
        if "image-generator" in content:
            return "image-generator", "unknown", "Générateur d'image (déduit)"

    for line in lines[:3]:
        source = line.get("source")
        msg_type = line.get("type")
        if source == "USER" or msg_type == "USER_INPUT":
            return "ROOT", "inherit", "Conversation principale (ROOT)"

    return "unknown", "unknown", "Inconnu"


def analyze_conversation(conv_dir: Path, registry: Dict[str, SubagentInfo]) -> Optional[ConversationStats]:
    tfile = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
    if not tfile.exists():
        tfile = conv_dir / "transcript.jsonl"
        if not tfile.exists():
            return None

    try:
        mtime = datetime.fromtimestamp(tfile.stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None

    try:
        with open(tfile, "r", encoding="utf-8", errors="ignore") as f:
            lines = [json.loads(l) for l in f if l.strip()]
    except Exception:
        return None

    if not lines:
        return None

    conv_id = conv_dir.name
    if conv_id in registry:
        info = registry[conv_id]
        category = info.type_name
        model = info.model
        role = info.role
        parent_id = info.parent_id
    else:
        category, model, role = detect_fallback_category(conv_dir, lines)
        parent_id = None

    planner_turns = 0
    input_tokens = 0
    cache_read_tokens = 0
    output_tokens = 0
    tool_errors = 0
    cron_post_artefact = 0
    seen_artefact = False

    for line in lines:
        l_type = line.get("type")
        status = line.get("status")

        if l_type == "PLANNER_RESPONSE":
            planner_turns += 1
            input_tokens += int(line.get("input_tokens") or 0)
            cache_read_tokens += int(line.get("cache_read_tokens") or 0)
            output_tokens += int(line.get("output_tokens") or 0)

        if status == "ERROR":
            tool_errors += 1

        content = str(line.get("content", ""))
        tool_calls = line.get("tool_calls", [])
        for tc in tool_calls:
            args_str = str(tc.get("args") or tc.get("arguments") or "")
            if "ARTEFACT:" in args_str:
                seen_artefact = True

        if "ARTEFACT:" in content:
            seen_artefact = True

        if seen_artefact and "Auto-check" in content and l_type == "SYSTEM_MESSAGE":
            cron_post_artefact += 1

    total_tokens = input_tokens + cache_read_tokens + output_tokens

    full_file = conv_dir / ".system_generated" / "logs" / "transcript_full.jsonl"
    if full_file.exists():
        full_size_bytes = full_file.stat().st_size
    else:
        full_size_bytes = tfile.stat().st_size

    budget_exceeded = False
    if category in ("eclaireur", "auditeur-alignement") and planner_turns > 20:
        budget_exceeded = True
    elif category == "executant" and planner_turns > 35:
        budget_exceeded = True
    elif category == "ROOT" and planner_turns > 80:
        budget_exceeded = True

    return ConversationStats(
        conversation_id=conv_id,
        category=category,
        model=model,
        role=role,
        parent_id=parent_id,
        mtime=mtime,
        planner_turns=planner_turns,
        steps=len(lines),
        input_tokens=input_tokens,
        cache_read_tokens=cache_read_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        full_size_bytes=full_size_bytes,
        tool_errors=tool_errors,
        cron_post_artefact=cron_post_artefact,
        budget_exceeded=budget_exceeded,
    )


def parse_claude_runs(
    claude_log_dir: Path = Path.home() / ".claude" / "antigravity-runs",
    since_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Analyse les runs Claude Code et Antigravity autonomes stockés dans ~/.claude/antigravity-runs.
    Distingue backend="claude" vs backend="agy".
    """
    runs: List[ClaudeRunStats] = []
    if not claude_log_dir.is_dir():
        return {
            "total_runs": 0,
            "claude_runs": 0,
            "agy_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "success_rate_pct": 100.0,
            "avg_duration_sec": 0.0,
            "total_duration_sec": 0.0,
            "total_cost_usd": 0.0,
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "runs": [],
        }

    for f in sorted(claude_log_dir.glob("*.json")):
        if not (f.name.startswith("claude_") or f.name.startswith("agy_")):
            continue

        file_dt = None
        m = re.search(r'(?:claude|agy)_(\d{8})_(\d{6})\.json', f.name)
        if m:
            try:
                file_dt = datetime.strptime(f"{m.group(1)}_{m.group(2)}", "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
            except Exception:
                pass
        if not file_dt:
            file_dt = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)

        if since_dt and file_dt < since_dt:
            continue

        try:
            data = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

        backend = str(data.get("backend") or ("agy" if f.name.startswith("agy_") else "claude"))
        usage = data.get("usage") or {}
        model_name = str(data.get("model") or "claude-opus")

        if backend == "claude":
            model_usage = data.get("modelUsage") or {}
            if model_usage:
                first_key = list(model_usage.keys())[0]
                if "opus" in first_key.lower():
                    model_name = "claude-opus"
                elif "sonnet" in first_key.lower():
                    model_name = "claude-sonnet"
                else:
                    model_name = first_key
            duration_ms = data.get("duration_ms") or data.get("duration_api_ms") or 0
            dur_sec = duration_ms / 1000.0
            num_turns = data.get("num_turns") or len(usage.get("iterations", [])) or 1
            cost_usd = float(data.get("total_cost_usd") or 0.0)
            is_error = bool(data.get("is_error")) or (data.get("api_error_status") is not None)
            subtype = str(data.get("subtype") or ("success" if not is_error else "error"))
            in_tok = int(usage.get("input_tokens") or 0)
            out_tok = int(usage.get("output_tokens") or 0)
            cache_read = int(usage.get("cache_read_input_tokens") or 0)
            cache_create = int(usage.get("cache_creation_input_tokens") or 0)
            total_tok = in_tok + out_tok + cache_read + cache_create
        else:
            # backend == "agy"
            dur_sec = float(data.get("duration_seconds") or 0.0)
            num_turns = int(data.get("num_turns") or 1)
            cost_usd = 0.0
            is_error = bool(data.get("is_error")) or (data.get("status") != "SUCCESS")
            subtype = "agy_success" if not is_error else "agy_error"
            in_tok = int(usage.get("input_tokens") or 0)
            out_tok = int(usage.get("output_tokens") or 0)
            cache_read = int(usage.get("cache_read_tokens") or 0)
            cache_create = 0
            total_tok = int(usage.get("total_tokens") or (in_tok + out_tok + cache_read))

        res_text = str(data.get("result") or "")[:150].replace("\n", " ")

        runs.append(ClaudeRunStats(
            run_id=f.stem,
            backend=backend,
            timestamp=file_dt,
            model=model_name,
            duration_sec=dur_sec,
            num_turns=num_turns,
            total_cost_usd=cost_usd,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cache_read_tokens=cache_read,
            cache_creation_tokens=cache_create,
            total_tokens=total_tok,
            is_error=is_error,
            subtype=subtype,
            result_preview=res_text,
        ))

    total_runs = len(runs)
    claude_runs = sum(1 for r in runs if r.backend == "claude")
    agy_runs = sum(1 for r in runs if r.backend == "agy")
    successes = sum(1 for r in runs if not r.is_error)
    fails = total_runs - successes
    succ_rate = (successes / total_runs * 100.0) if total_runs > 0 else 100.0
    tot_dur = sum(r.duration_sec for r in runs)
    avg_dur = (tot_dur / total_runs) if total_runs > 0 else 0.0
    tot_cost = sum(r.total_cost_usd for r in runs)
    tot_tk = sum(r.total_tokens for r in runs)
    in_tk = sum(r.input_tokens for r in runs)
    out_tk = sum(r.output_tokens for r in runs)
    cache_tk = sum(r.cache_read_tokens + r.cache_creation_tokens for r in runs)

    return {
        "total_runs": total_runs,
        "claude_runs": claude_runs,
        "agy_runs": agy_runs,
        "successful_runs": successes,
        "failed_runs": fails,
        "success_rate_pct": round(succ_rate, 1),
        "avg_duration_sec": round(avg_dur, 1),
        "total_duration_sec": round(tot_dur, 1),
        "total_cost_usd": round(tot_cost, 4),
        "total_tokens": tot_tk,
        "input_tokens": in_tk,
        "output_tokens": out_tk,
        "cache_tokens": cache_tk,
        "runs": [asdict(r) for r in runs],
    }


def find_agy_bin() -> Optional[str]:
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


def fetch_agy_quotas() -> Optional[Dict[str, Any]]:
    agy_bin = find_agy_bin()
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
        now = datetime.now(timezone.utc)

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
                    try:
                        clean_iso = reset_time.replace("Z", "+00:00")
                        reset_dt = datetime.fromisoformat(clean_iso)
                        if reset_dt.tzinfo is None:
                            reset_dt = reset_dt.replace(tzinfo=timezone.utc)
                        rem_sec = max(0.0, (reset_dt - now).total_seconds())
                        rem_days = int(rem_sec // 86400)
                        rem_hours = int((rem_sec % 86400) // 3600)
                        reset_local = reset_dt.astimezone().strftime("%Y-%m-%d %H:%M")
                        rem_total_hours = rem_sec / 3600.0
                        elapsed_hours = max(0.0, min(168.0, 168.0 - rem_total_hours))
                        cible_pct = round(96.0 * (elapsed_hours / 168.0), 1)
                        delta = round(used_pct - cible_pct, 1)
                        sign = "+" if delta >= 0 else ""
                        bucket_info.update({
                            "cible_96": cible_pct,
                            "delta": delta,
                            "delta_str": f"{sign}{delta:.1f}%",
                            "reset_local": reset_local,
                            "reste": f"{rem_days}j{rem_hours:02d}h",
                        })
                    except Exception:
                        pass
                elif b.get("window") == "5h":
                    try:
                        clean_iso = reset_time.replace("Z", "+00:00")
                        reset_dt = datetime.fromisoformat(clean_iso)
                        if reset_dt.tzinfo is None:
                            reset_dt = reset_dt.replace(tzinfo=timezone.utc)
                        rem_sec = max(0.0, (reset_dt - now).total_seconds())
                        rem_h = int(rem_sec // 3600)
                        rem_m = int((rem_sec % 3600) // 60)
                        reset_local = reset_dt.astimezone().strftime("%Y-%m-%d %H:%M")
                        bucket_info.update({
                            "reset_local": reset_local,
                            "reste": f"{rem_h}h{rem_m:02d}m",
                        })
                    except Exception:
                        pass

                res["buckets"][bid] = bucket_info

        return res
    except Exception:
        return None


def extract_latest_claude_quotas(brain_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Récupère le dernier snapshot de quotas Claude Code :
    1. Tente OAuth Anthropic direct si token actif.
    2. Sinon, extrait le snapshot le plus récent depuis les transcripts Antigravity.
    """
    cred_path = Path.home() / ".claude" / ".credentials.json"
    if cred_path.exists():
        try:
            import urllib.request
            data = json.loads(cred_path.read_text(encoding="utf-8"))
            token = data.get("claudeAiOauth", {}).get("accessToken")
            if token:
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
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status == 200:
                        raw = json.loads(resp.read().decode("utf-8"))
                        fh = raw.get("five_hour") or {}
                        sd = raw.get("seven_day") or {}
                        now = datetime.now(timezone.utc)
                        util_7d = float(sd.get("utilization") or 0.0)
                        reset_7d_dt = datetime.fromisoformat(sd.get("resets_at", now.isoformat()))
                        rem_7d_sec = max(0.0, (reset_7d_dt - now).total_seconds())
                        elapsed_hours = max(0.0, min(168.0, 168.0 - (rem_7d_sec / 3600.0)))
                        cible_pct = 96.0 * (elapsed_hours / 168.0)
                        delta = util_7d - cible_pct
                        rem_days = int(rem_7d_sec // 86400)
                        rem_hours = int((rem_7d_sec % 86400) // 3600)
                        return {
                            "source": "api_oauth",
                            "util_5h": float(fh.get("utilization") or 0.0),
                            "reset_5h": str(fh.get("resets_at") or ""),
                            "util_7d": util_7d,
                            "reset_7d": str(sd.get("resets_at") or ""),
                            "reste_7d": f"{rem_days}j{rem_hours:02d}h",
                            "cible_96": round(cible_pct, 1),
                            "delta_7d": round(delta, 1),
                        }
        except Exception:
            pass

    search_dirs = [brain_dir] if brain_dir else [Path.home() / ".gemini" / "antigravity" / "brain"]
    latest_snapshot: Optional[Dict[str, Any]] = None

    for bdir in search_dirs:
        if not bdir or not bdir.is_dir():
            continue
        for tfile in bdir.glob("*/.system_generated/logs/transcript.jsonl"):
            try:
                txt = tfile.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            matches_5h = list(re.finditer(r'QUOTA_SESSION_5H:\s*([\d\.]+)%\s*\((?:reset\s*([^,]+),\s*)?reste\s*([^\)]+)\)', txt))
            matches_7d = list(re.finditer(r'QUOTA_WEEK_7D:\s*([\d\.]+)%\s*\((?:reset\s*([^,]+),\s*)?reste\s*([^|]+)\|\s*cible_96%:\s*([\d\.]+)%\s*\|\s*delta:\s*([^\)]+)\)', txt))

            if matches_5h and matches_7d:
                m5 = matches_5h[-1]
                m7 = matches_7d[-1]
                util_5h = float(m5.group(1))
                util_7d = float(m7.group(1))
                cible_96 = float(m7.group(4))
                delta_str = m7.group(5).replace("%", "").strip()
                delta_val = float(delta_str) if delta_str else (util_7d - cible_96)
                latest_snapshot = {
                    "source": "transcript_snapshot",
                    "util_5h": util_5h,
                    "reset_5h": m5.group(2) or "",
                    "reste_5h": m5.group(3) or "",
                    "util_7d": util_7d,
                    "reset_7d": m7.group(2) or "",
                    "reste_7d": m7.group(3) or "",
                    "cible_96": cible_96,
                    "delta_7d": round(delta_val, 1),
                }

    if latest_snapshot:
        return latest_snapshot

    return {
        "source": "default_baseline",
        "util_5h": 0.0,
        "reset_5h": "",
        "reste_5h": "",
        "util_7d": 0.0,
        "reset_7d": "",
        "reste_7d": "",
        "cible_96": 0.0,
        "delta_7d": 0.0,
    }


def compute_quota_pace(
    claude_quotas: Dict[str, Any],
    agy_quotas: Optional[Dict[str, Any]],
    subagent_counts: Dict[str, int],
    total_antigravity_turns: int,
    inherit_turns: int,
) -> Dict[str, Any]:
    """
    Calcule la cadence des quotas pour les 3 piliers :
    1. Antigravity Crédits 3P (Claude Opus 5.5 / Sonnet 5.5)
    2. Claude Code (Anthropic Opus medium)
    3. Antigravity Gemini Models (Pro / Flash)
    """
    # 1. Claude Code Cadence
    delta_7d = float(claude_quotas.get("delta_7d", 0.0))
    util_5h = float(claude_quotas.get("util_5h", 0.0))

    if delta_7d < -10.0:
        claude_badge = "🟢 ACCÉLÉRER"
        claude_diag = "Consommation nettement sous la trajectoire cible 96% : marge disponible très confortable avant le reset hebdomadaire."
    elif -10.0 <= delta_7d <= 10.0:
        claude_badge = "✅ RYTHME OPTIMAL"
        claude_diag = "Cadence hebdomadaire parfaitement alignée sur la trajectoire linéaire visant ~96% au reset."
    else:
        claude_badge = "🟠 RALENTIR"
        claude_diag = "Consommation supérieure à la trajectoire cible : risque de plafonnement avant l'échéance de reset hebdomadaire."

    session_5h_alert = "⚠️ SATURATION (>=85%)" if util_5h >= 85.0 else "✅ NORMALE"

    # 2. Antigravity 3P (Claude Opus 5.5) Cadence
    buckets = agy_quotas.get("buckets", {}) if agy_quotas else {}
    b_3p_w = buckets.get("3p-weekly", {})
    b_3p_5h = buckets.get("3p-5h", {})
    delta_3p = float(b_3p_w.get("delta", 0.0))
    util_3p_5h = float(b_3p_5h.get("used_pct", 0.0))
    util_3p_w = float(b_3p_w.get("used_pct", 0.0))

    if delta_3p < -5.0:
        agy_3p_badge = "🟢 ACCÉLÉRER"
        agy_3p_diag = f"Crédits Claude Opus 5.5 Antigravity sous la cible ({b_3p_w.get('delta_str', '')}) : utiliser en priorité via `agy --model claude-opus-5-5-medium`."
    elif -5.0 <= delta_3p <= 5.0:
        agy_3p_badge = "✅ RYTHME OPTIMAL"
        agy_3p_diag = f"Consommation des crédits Claude Opus 5.5 Antigravity alignée sur la trajectoire optimale."
    else:
        agy_3p_badge = "🟠 RALENTIR"
        agy_3p_diag = f"Consommation des crédits Claude Opus 5.5 Antigravity en avance (+{delta_3p:.1f}%) : basculer sur Claude Code ou Gemini."

    # 3. Antigravity Gemini Models Cadence
    b_gem_w = buckets.get("gemini-weekly", {})
    b_gem_5h = buckets.get("gemini-5h", {})
    delta_gem = float(b_gem_w.get("delta", 0.0))
    util_gem_5h = float(b_gem_5h.get("used_pct", 0.0))
    util_gem_w = float(b_gem_w.get("used_pct", 0.0))

    if delta_gem < -5.0:
        gemini_badge = "🟢 ACCÉLÉRER"
        gemini_diag = "Quotas Gemini confortables sous la trajectoire cible hebdomadaire."
    elif -5.0 <= delta_gem <= 5.0:
        gemini_badge = "✅ RYTHME OPTIMAL"
        gemini_diag = "Rythme Gemini équilibré."
    else:
        gemini_badge = "🟠 RALENTIR"
        gemini_diag = f"Quotas Gemini élevés (+{delta_gem:.1f}%) : modérer l'usage des modèles Pro."

    tot_sub = subagent_counts.get("flash", 0) + subagent_counts.get("inherit", 0)
    inherit_ratio = (subagent_counts.get("inherit", 0) / tot_sub * 100.0) if tot_sub > 0 else 0.0

    return {
        "claude_code": {
            "badge": claude_badge,
            "diagnosis": claude_diag,
            "session_5h_util": util_5h,
            "session_5h_status": session_5h_alert,
            "week_7d_util": claude_quotas.get("util_7d", 0.0),
            "week_7d_cible_96": claude_quotas.get("cible_96", 0.0),
            "week_7d_delta": delta_7d,
            "reset_7d": claude_quotas.get("reset_7d", ""),
            "reste_7d": claude_quotas.get("reste_7d", ""),
        },
        "antigravity_3p": {
            "badge": agy_3p_badge,
            "diagnosis": agy_3p_diag,
            "session_5h_util": util_3p_5h,
            "session_5h_reste": b_3p_5h.get("reste", ""),
            "week_7d_util": util_3p_w,
            "week_7d_cible_96": b_3p_w.get("cible_96", 0.0),
            "week_7d_delta": delta_3p,
            "reset_7d": b_3p_w.get("reset_local", ""),
            "reste_7d": b_3p_w.get("reste", ""),
        },
        "antigravity_gemini": {
            "badge": gemini_badge,
            "diagnosis": gemini_diag,
            "session_5h_util": util_gem_5h,
            "session_5h_reste": b_gem_5h.get("reste", ""),
            "week_7d_util": util_gem_w,
            "week_7d_cible_96": b_gem_w.get("cible_96", 0.0),
            "week_7d_delta": delta_gem,
            "reset_7d": b_gem_w.get("reset_local", ""),
            "reste_7d": b_gem_w.get("reste", ""),
            "inherit_subagent_ratio_pct": round(inherit_ratio, 1),
            "inherit_turns": inherit_turns,
            "total_turns": total_antigravity_turns,
        },
    }


def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def format_tokens(n: int) -> str:
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}k"
    return f"{n / 1_000_000:.2f}M"


def generate_markdown_report(
    since_dt: datetime,
    tot_sessions: int,
    tot_turns: int,
    tot_tokens: int,
    tot_bytes: int,
    cat_model_stats: Dict[str, Dict[str, Dict[str, Any]]],
    subagent_counts: Dict[str, int],
    claude_stats: Dict[str, Any],
    quota_pace: Dict[str, Any],
    anomalies: Dict[str, int],
    top_convs: List[ConversationStats],
) -> str:
    lines = []
    lines.append(f"# 📊 Rapport Télémétrique des Tokens, Sessions & Quotas")
    lines.append(f"\n> **Période d'analyse** : depuis `{since_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}`  \n")
    lines.append(f"> **Activité consolidée** : {tot_sessions} sessions Antigravity + {claude_stats['total_runs']} runs autonomes ({claude_stats['claude_runs']} claude CLI, {claude_stats['agy_runs']} agy) | Tokens : {format_tokens(tot_tokens + claude_stats['total_tokens'])}\n")
    lines.append("\n---\n")

    # Section 1 : Trajectoire des Quotas Tripartite
    lines.append("## 🎯 1. Calculateur de Trajectoire des Quotas Tripartite (`--quota-pace`)\n")
    a3p = quota_pace["antigravity_3p"]
    cp = quota_pace["claude_code"]
    gem = quota_pace["antigravity_gemini"]

    lines.append(f"### 1. Antigravity Crédits 3P (Claude Opus 5.5 / Sonnet 5.5)\n")
    lines.append(f"- **Indicateur de rythme** : `{a3p['badge']}`")
    lines.append(f"- **Diagnostic** : {a3p['diagnosis']}")
    lines.append(f"- **Quota Session (5h)** : `{a3p['session_5h_util']}%` (reste `{a3p['session_5h_reste']}`)")
    lines.append(f"- **Quota Semaine (7j)** : `{a3p['week_7d_util']}%` (Cible 96% : `{a3p['week_7d_cible_96']}%` | Delta : `{a3p['week_7d_delta']:+0.1f}%` | Reset : `{a3p['reset_7d']}`, reste `{a3p['reste_7d']}`)\n")

    lines.append(f"### 2. Claude Code (Anthropic OAuth Opus medium)\n")
    lines.append(f"- **Indicateur de rythme** : `{cp['badge']}`")
    lines.append(f"- **Diagnostic** : {cp['diagnosis']}")
    lines.append(f"- **Quota Session (5h)** : `{cp['session_5h_util']}%` ({cp['session_5h_status']})")
    lines.append(f"- **Quota Semaine (7j)** : `{cp['week_7d_util']}%` (Cible 96% : `{cp['week_7d_cible_96']}%` | Delta : `{cp['week_7d_delta']:+0.1f}%` | Reset : `{cp['reset_7d']}`, reste `{cp['reste_7d']}`)\n")

    lines.append(f"### 3. Antigravity Gemini Models (Pro / Flash)\n")
    lines.append(f"- **Indicateur de rythme** : `{gem['badge']}`")
    lines.append(f"- **Diagnostic** : {gem['diagnosis']}")
    lines.append(f"- **Quota 5h / Weekly** : 5h `{gem['session_5h_util']}%` | Weekly `{gem['week_7d_util']}%` (Cible : `{gem['week_7d_cible_96']}%` | Delta : `{gem['week_7d_delta']:+0.1f}%`)")
    lines.append(f"- **Ratio Sous-agents Inherit** : `{gem['inherit_subagent_ratio_pct']}%` (Cible : `10 - 15 %`)\n")

    lines.append("---\n")

    # Section 2 : Répartition
    lines.append("## ⚖️ 2. Répartition & Arbitrage des Modèles\n")
    tot_sub_ag = subagent_counts.get("flash", 0) + subagent_counts.get("inherit", 0)
    flash_pct = (subagent_counts.get("flash", 0) / tot_sub_ag * 100.0) if tot_sub_ag > 0 else 0.0
    inh_pct = (subagent_counts.get("inherit", 0) / tot_sub_ag * 100.0) if tot_sub_ag > 0 else 0.0

    lines.append("| Modèle / Pilier | Rôle & Usage Clé | Volume / Sessions | Ratio Réel | Cible Recommandée |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    lines.append(f"| **Gemini Flash** | Extraction factuelle, éclaireurs, code guidé sans risque | {subagent_counts.get('flash', 0)} sessions | **{flash_pct:.1f}%** | `~85 - 90 %` |")
    lines.append(f"| **Gemini Inherit** | Rédaction humaine/académique, synthèse, supervision | {subagent_counts.get('inherit', 0)} sessions | **{inh_pct:.1f}%** | `~10 - 15 %` |")
    lines.append(f"| **Claude Opus (Antigravity agy)** | Code délicat/critique, sous-agents Opus inclus | {claude_stats['agy_runs']} runs | Inclus Antigravity | Prioritaire sous cible 96% |")
    lines.append(f"| **Claude Code (Anthropic CLI)** | Runs longs, architecture complète autonome | {claude_stats['claude_runs']} runs | Autonome | Selon quota 5h/7j |")
    lines.append("\n---\n")

    # Section 3 : Activité Antigravity
    lines.append("## 📈 3. Activité Détaillée par Catégorie Antigravity\n")
    lines.append("| Catégorie | Modèle | Sessions | Tours LLM | Input Tokens | Cache Tokens | Output Tokens | Total Tokens | Logs |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    standard_cats = ["ROOT", "eclaireur", "executant", "auditeur-alignement", "superviseur-projet", "self", "image-generator", "unknown"]
    existing_cats = sorted(cat_model_stats.keys(), key=lambda x: standard_cats.index(x) if x in standard_cats else 99)

    for cat in existing_cats:
        mod_dict = cat_model_stats[cat]
        for mod in sorted(mod_dict.keys()):
            data = mod_dict[mod]
            lines.append(
                f"| `{cat}` | `{mod}` | {data['sessions']} | {data['planner_turns']} | "
                f"{format_tokens(data['input_tokens'])} | {format_tokens(data['cache_read_tokens'])} | "
                f"{format_tokens(data['output_tokens'])} | **{format_tokens(data['total_tokens'])}** | {format_bytes(data['full_size_bytes'])} |"
            )

    lines.append("\n---\n")

    # Section 4 : Anomalies
    lines.append("## 🚨 4. Anomalies & Frictions Détectées\n")
    lines.append(f"- **Sous-agents hors budget (>20 tours éclaireur/audit, >35 tours exécutant)** : `{anomalies['subagents_budget_exceeded']}`")
    lines.append(f"- **Sessions ROOT > 80 tours LLM (recommandation /handover ou /compact)** : `{anomalies['root_long_sessions']}`")
    lines.append(f"- **Erreurs d'outils (`status == ERROR`)** : `{anomalies['total_tool_errors']}`")
    lines.append(f"- **Réveils cron 'Auto-check' post-ARTEFACT (oubli de manage_task kill)** : `{anomalies['total_cron_post_artefact']}`\n")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI enrichie de télémétrie des tokens, sessions et quotas Antigravity & Claude Code."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Filtre les conversations modifiées au cours des N derniers jours (défaut: 7).",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Date ISO de début (ex: 2026-10-15T00:00:00Z ou 2026-10-15). Écrase --days.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Nombre de conversations les plus coûteuses à afficher (défaut: 10).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie structurée en JSON.",
    )
    parser.add_argument(
        "--brain-dir",
        type=str,
        default=None,
        help="Chemin alternatif vers le dossier brain (défaut: ~/.gemini/antigravity/brain).",
    )
    parser.add_argument(
        "--claude-log-dir",
        type=str,
        default=None,
        help="Chemin alternatif vers le dossier des runs Claude (défaut: ~/.claude/antigravity-runs).",
    )
    parser.add_argument(
        "--quota-pace",
        action="store_true",
        help="Calcule et affiche le diagnostic de cadence des quotas (🟢 ACCÉLÉRER / ✅ OPTIMAL / 🟠 RALENTIR).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Chemin de sauvegarde du rapport Markdown complet.",
    )

    args = parser.parse_args()

    now_utc = datetime.now(timezone.utc)
    if args.since:
        since_str = args.since.replace("Z", "+00:00")
        try:
            since_dt = datetime.fromisoformat(since_str)
            if since_dt.tzinfo is None:
                since_dt = since_dt.replace(tzinfo=timezone.utc)
        except ValueError as e:
            sys.stderr.write(f"Erreur: Format de date invalide pour --since: {args.since} ({e})\n")
            sys.exit(1)
    else:
        since_dt = now_utc - timedelta(days=args.days)

    brain_dir = Path(args.brain_dir) if args.brain_dir else Path.home() / ".gemini" / "antigravity" / "brain"
    claude_log_dir = Path(args.claude_log_dir) if args.claude_log_dir else Path.home() / ".claude" / "antigravity-runs"

    if not brain_dir.is_dir():
        # Fallback sur antigravity-cli brain si existe
        cli_brain = Path.home() / ".gemini" / "antigravity-cli" / "brain"
        if cli_brain.is_dir():
            brain_dir = cli_brain
        else:
            sys.stderr.write(f"Erreur: Dossier introuvable: {brain_dir}\n")
            sys.exit(1)

    registry = parse_subagent_registry(brain_dir)

    active_conversations: List[ConversationStats] = []
    for conv_dir in brain_dir.iterdir():
        if not conv_dir.is_dir():
            continue
        tfile = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if not tfile.exists():
            tfile = conv_dir / "transcript.jsonl"
            if not tfile.exists():
                continue

        try:
            mtime = datetime.fromtimestamp(tfile.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue

        if mtime >= since_dt:
            stat = analyze_conversation(conv_dir, registry)
            if stat:
                active_conversations.append(stat)

    cat_model_stats: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(lambda: defaultdict(lambda: {
        "sessions": 0,
        "planner_turns": 0,
        "steps": 0,
        "input_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "full_size_bytes": 0,
        "tool_errors": 0,
        "cron_post_artefact": 0,
        "budget_exceeded": 0,
    }))

    for c in active_conversations:
        entry = cat_model_stats[c.category][c.model]
        entry["sessions"] += 1
        entry["planner_turns"] += c.planner_turns
        entry["steps"] += c.steps
        entry["input_tokens"] += c.input_tokens
        entry["cache_read_tokens"] += c.cache_read_tokens
        entry["output_tokens"] += c.output_tokens
        entry["total_tokens"] += c.total_tokens
        entry["full_size_bytes"] += c.full_size_bytes
        entry["tool_errors"] += c.tool_errors
        entry["cron_post_artefact"] += c.cron_post_artefact
        if c.budget_exceeded:
            entry["budget_exceeded"] += 1

    subagent_counts = {"flash": 0, "inherit": 0, "unknown": 0}
    eclaireur_counts = {"flash": 0, "inherit": 0, "unknown": 0}
    executant_counts = {"flash": 0, "inherit": 0, "unknown": 0}

    for c in active_conversations:
        if c.category != "ROOT":
            subagent_counts[c.model] = subagent_counts.get(c.model, 0) + 1
        if c.category == "eclaireur":
            eclaireur_counts[c.model] = eclaireur_counts.get(c.model, 0) + 1
        elif c.category == "executant":
            executant_counts[c.model] = executant_counts.get(c.model, 0) + 1

    def calc_ratio(counts: Dict[str, int]) -> float:
        total = counts["flash"] + counts["inherit"]
        return (counts["flash"] / total * 100.0) if total > 0 else 0.0

    subagent_budget_exceeded = sum(
        1 for c in active_conversations
        if c.category in ("eclaireur", "auditeur-alignement", "executant") and c.budget_exceeded
    )
    root_long_sessions = sum(1 for c in active_conversations if c.category == "ROOT" and c.budget_exceeded)
    total_tool_errors = sum(c.tool_errors for c in active_conversations)
    total_cron_post_artefact = sum(c.cron_post_artefact for c in active_conversations)

    sorted_convs = sorted(active_conversations, key=lambda x: x.total_tokens, reverse=True)
    top_convs = sorted_convs[:args.top]

    tot_sessions = len(active_conversations)
    tot_turns = sum(c.planner_turns for c in active_conversations)
    tot_in_tk = sum(c.input_tokens for c in active_conversations)
    tot_cache_tk = sum(c.cache_read_tokens for c in active_conversations)
    tot_out_tk = sum(c.output_tokens for c in active_conversations)
    tot_tokens = sum(c.total_tokens for c in active_conversations)
    tot_bytes = sum(c.full_size_bytes for c in active_conversations)

    # Télémétrie Claude Code & Antigravity
    claude_stats = parse_claude_runs(claude_log_dir=claude_log_dir, since_dt=since_dt)
    claude_quotas = extract_latest_claude_quotas(brain_dir=brain_dir)
    agy_quotas = fetch_agy_quotas()
    inherit_turns = sum(c.planner_turns for c in active_conversations if c.model == "inherit")

    quota_pace = compute_quota_pace(
        claude_quotas=claude_quotas,
        agy_quotas=agy_quotas,
        subagent_counts=subagent_counts,
        total_antigravity_turns=tot_turns,
        inherit_turns=inherit_turns,
    )

    anomalies_dict = {
        "subagents_budget_exceeded": subagent_budget_exceeded,
        "root_long_sessions": root_long_sessions,
        "total_tool_errors": total_tool_errors,
        "total_cron_post_artefact": total_cron_post_artefact,
    }

    if args.json:
        out_data = {
            "summary": {
                "since": since_dt.isoformat(),
                "days_requested": args.days if not args.since else None,
                "total_conversations": tot_sessions,
                "total_planner_turns": tot_turns,
                "total_input_tokens": tot_in_tk,
                "total_cache_read_tokens": tot_cache_tk,
                "total_output_tokens": tot_out_tk,
                "total_tokens": tot_tokens,
                "total_transcript_full_bytes": tot_bytes,
            },
            "claude_and_agy_runs": claude_stats,
            "quota_pace": quota_pace,
            "ratios": {
                "subagents_overall": {
                    "flash": subagent_counts["flash"],
                    "inherit": subagent_counts["inherit"],
                    "unknown": subagent_counts["unknown"],
                    "flash_pct": round(calc_ratio(subagent_counts), 1),
                },
            },
            "anomalies": anomalies_dict,
        }
        print(json.dumps(out_data, indent=2, ensure_ascii=False))
        if args.out:
            Path(args.out).write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return

    # Sortie Texte Tabulaire
    print("=" * 96)
    print(f"📊 TÉLÉMÉTRIE ANTIGRAVITY & CLAUDE CODE — Période : depuis {since_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Antigravity : {tot_sessions} sess. | {tot_turns} tours | {format_tokens(tot_tokens)} tk  ||  Runs autonomes : {claude_stats['total_runs']} ({claude_stats['claude_runs']} claude CLI, {claude_stats['agy_runs']} agy) | {format_tokens(claude_stats['total_tokens'])} tk")
    print("=" * 96)
    print()

    # Section Quota Pace Tripartite
    print("🎯 CALCULATEUR DE TRAJECTOIRE DES QUOTAS TRIPARTITE (--quota-pace)")
    a3p = quota_pace["antigravity_3p"]
    cp = quota_pace["claude_code"]
    gem = quota_pace["antigravity_gemini"]

    print(f"  1. Antigravity Crédits 3P (Claude Opus 5.5) : {a3p['badge']} -> {a3p['diagnosis']}")
    print(f"     - Quota 5h : {a3p['session_5h_util']}% (reste {a3p['session_5h_reste']})")
    print(f"     - Quota 7j : {a3p['week_7d_util']}% (Cible 96%: {a3p['week_7d_cible_96']}% | Delta: {a3p['week_7d_delta']:+0.1f}%) | Reset: {a3p['reset_7d']} ({a3p['reste_7d']})")

    print(f"  2. Claude Code (Anthropic Opus medium)     : {cp['badge']} -> {cp['diagnosis']}")
    print(f"     - Quota 5h : {cp['session_5h_util']}% ({cp['session_5h_status']})")
    print(f"     - Quota 7j : {cp['week_7d_util']}% (Cible 96%: {cp['week_7d_cible_96']}% | Delta: {cp['week_7d_delta']:+0.1f}%) | Reset: {cp['reset_7d']} ({cp['reste_7d']})")

    print(f"  3. Antigravity Gemini Models (Pro / Flash) : {gem['badge']} -> {gem['diagnosis']}")
    print(f"     - Quota 5h : {gem['session_5h_util']}% (reste {gem['session_5h_reste']}) | Quota Weekly: {gem['week_7d_util']}% (Cible: {gem['week_7d_cible_96']}%, Delta: {gem['week_7d_delta']:+0.1f}%)")
    print(f"     - Ratio Sous-agents Inherit : {gem['inherit_subagent_ratio_pct']}% [Cible ~10-15%]")
    print()

    print(f"{'Catégorie':<20} {'Modèle':<12} {'Sess.':>6} {'Tours (Moy)':>12} {'Input Tk':>10} {'Cache Tk':>10} {'Output Tk':>10} {'Total Tk':>10}")
    print("-" * 105)

    standard_cats = ["ROOT", "eclaireur", "executant", "auditeur-alignement", "superviseur-projet", "self", "image-generator", "unknown"]
    existing_cats = sorted(cat_model_stats.keys(), key=lambda x: standard_cats.index(x) if x in standard_cats else 99)

    for cat in existing_cats:
        mod_dict = cat_model_stats[cat]
        for mod in sorted(mod_dict.keys()):
            data = mod_dict[mod]
            sess = data["sessions"]
            turns = data["planner_turns"]
            avg_turns = turns / sess if sess > 0 else 0
            in_tk = format_tokens(data["input_tokens"])
            c_tk = format_tokens(data["cache_read_tokens"])
            out_tk = format_tokens(data["output_tokens"])
            t_tk = format_tokens(data["total_tokens"])
            t_disp = f"{turns} ({avg_turns:.1f})"
            print(f"{cat:<20} {mod:<12} {sess:>6} {t_disp:>12} {in_tk:>10} {c_tk:>10} {out_tk:>10} {t_tk:>10}")

    if claude_stats["total_runs"] > 0:
        c_dur_disp = f"{claude_stats['total_runs']} ({claude_stats['avg_duration_sec']:.0f}s)"
        print(f"{'runs-autonomes':<20} {'claude/agy':<12} {claude_stats['total_runs']:>6} {c_dur_disp:>12} {format_tokens(claude_stats['input_tokens']):>10} {format_tokens(claude_stats['cache_tokens']):>10} {format_tokens(claude_stats['output_tokens']):>10} {format_tokens(claude_stats['total_tokens']):>10}")

    print("-" * 105)
    print()

    print("⚖️  RÉPARTITION & ARBITRAGE DES MODÈLES")
    tot_sub_fi = subagent_counts.get("flash", 0) + subagent_counts.get("inherit", 0)
    f_pct = (subagent_counts.get("flash", 0) / tot_sub_fi * 100.0) if tot_sub_fi > 0 else 0.0
    inh_pct = (subagent_counts.get("inherit", 0) / tot_sub_fi * 100.0) if tot_sub_fi > 0 else 0.0
    print(f"  • Gemini Flash   : {subagent_counts.get('flash', 0)} sessions ({f_pct:.1f}%) [Cible ~85-90%]")
    print(f"  • Gemini Inherit : {subagent_counts.get('inherit', 0)} sessions ({inh_pct:.1f}%) [Cible ~10-15%]")
    print(f"  • Claude/Agy     : {claude_stats['total_runs']} runs autonomes ({claude_stats['agy_runs']} agy Opus 5.5, {claude_stats['claude_runs']} claude CLI | {claude_stats['success_rate_pct']}% succès)")
    print()

    if args.out:
        md_content = generate_markdown_report(
            since_dt=since_dt,
            tot_sessions=tot_sessions,
            tot_turns=tot_turns,
            tot_tokens=tot_tokens,
            tot_bytes=tot_bytes,
            cat_model_stats=cat_model_stats,
            subagent_counts=subagent_counts,
            claude_stats=claude_stats,
            quota_pace=quota_pace,
            anomalies=anomalies_dict,
            top_convs=top_convs,
        )
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md_content, encoding="utf-8")
        print(f"📄 Rapport Markdown sauvegardé : {out_path}")


if __name__ == "__main__":
    main()
