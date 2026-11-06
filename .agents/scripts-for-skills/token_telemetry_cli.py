#!/usr/bin/env python3
"""
CLI de télémétrie des tokens, sessions et anomalies Antigravity.
Analyse les transcripts dans ~/.gemini/antigravity/brain pour quantifier
l'activité des conversations principales et des sous-agents.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configuration de l'encodage de sortie pour Windows PowerShell / CMD
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


# Poids empiriques exacts en % de quota par 1M tokens
# (mesurés via RetrieveUserQuotaSummary forceRefresh=true / agy.exe /usage) :
# - Inherit (Gemini 4 Argon) :
#     5h     : input = 1.000 % / 1M, cache_read = 0.050 % / 1M (5 % = 1/20 de input), output = 5.000 % / 1M (5x input)
#     weekly : input = 0.250 % / 1M, cache_read = 0.0125 % / 1M (5 % = 1/20 de input), output = 1.250 % / 1M (5x input)
# - Flash (Gemini 3.8 Flash) :
#     5h     : input = 0.125 % / 1M, cache_read = 0.0125 % / 1M (10 % = 1/10 de input), output = 0.625 % / 1M (5x input)
#     weekly : input = 0.03125 % / 1M, cache_read = 0.003125 % / 1M (10 % = 1/10 de input), output = 0.15625 % / 1M (5x input)
QUOTA_5H_PCT_PER_1M: Dict[str, Tuple[float, float, float]] = {
    "inherit": (1.000, 0.050, 5.000),
    "flash": (0.125, 0.0125, 0.625),
    "unknown": (1.000, 0.050, 5.000),
}
WEEKLY_TO_5H_RATIO = 4.0


def compute_quota_pct(
    model: str,
    input_tokens: int,
    cache_read_tokens: int,
    output_tokens: int,
) -> Tuple[float, float]:
    """Calcule l'estimation réelle en (% quota 5h, % quota hebdomadaire 7j)."""
    w_in, w_cache, w_out = QUOTA_5H_PCT_PER_1M.get(model, QUOTA_5H_PCT_PER_1M["unknown"])
    q_5h = (
        input_tokens * w_in
        + cache_read_tokens * w_cache
        + output_tokens * w_out
    ) / 1_000_000.0
    q_weekly = q_5h / WEEKLY_TO_5H_RATIO
    return q_5h, q_weekly


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
    quota_5h_pct: float
    quota_weekly_pct: float
    full_size_bytes: int
    tool_errors: int
    cron_post_artefact: int
    budget_exceeded: bool


def clean_str(val: Any) -> str:
    """Nettoie les guillemets et espaces superflus d'une chaîne ou valeur brute."""
    if val is None:
        return ""
    s = str(val).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s


def normalize_model(model_raw: str) -> str:
    """Normalise le nom du modèle vers flash, inherit ou unknown."""
    m = model_raw.lower()
    if "flash" in m:
        return "flash"
    if "inherit" in m or "argon" in m or "sonnet" in m or "opus" in m or "gpt" in m or "pro" in m or "auto" in m:
        return "inherit"
    return "unknown"


def normalize_category(type_name_raw: str, default: str = "unknown") -> str:
    """Normalise la catégorie de conversation vers les catégories canoniques."""
    t = type_name_raw.lower().strip()
    if "eclaireur" in t or "éclaireur" in t:
        return "eclaireur"
    if "executant" in t or "exécutant" in t:
        return "executant"
    if "auditeur" in t or "audit" in t:
        return "auditeur-alignement"
    if "superviseur-projet" in t or "superviseur_projet" in t:
        return "superviseur-projet"
    if "image" in t:
        return "image-generator"
    if "self" in t:
        return "self"
    if "root" in t:
        return "ROOT"
    return default


def parse_subagent_registry(brain_dir: Path) -> Dict[str, SubagentInfo]:
    """
    Scanne les transcripts de brain pour répertorier les sous-agents
    invoqués via invoke_subagent et cartographier leurs métadonnées.
    """
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

                # Extraction des spécifications des sous-agents
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

            # Recherche séquentielle des conversationId dans les résultats suivants
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
    """
    Déduit par heuristique la catégorie, le modèle et le rôle d'une conversation
    lorsque l'invocation parente est antérieure à la fenêtre de scan.
    """
    # 1. Vérification des artefacts résiduels dans scratch/
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

    # 2. Vérification des premiers messages échangés
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

    # 3. Vérification de conversation racine directe (USER input au départ)
    for line in lines[:3]:
        source = line.get("source")
        msg_type = line.get("type")
        if source == "USER" or msg_type == "USER_INPUT":
            return "ROOT", "inherit", "Conversation principale (ROOT)"

    return "unknown", "unknown", "Inconnu"


def analyze_conversation(
    conv_dir: Path,
    registry: Dict[str, SubagentInfo],
    since_dt: Optional[datetime] = None,
) -> Optional[ConversationStats]:
    """Analyse une conversation unique et extrait toutes ses métriques."""
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
    active_steps = 0
    input_tokens = 0
    cache_read_tokens = 0
    output_tokens = 0
    tool_errors = 0
    cron_post_artefact = 0
    seen_artefact = False

    for line in lines:
        if since_dt is not None:
            ts_str = line.get("created_at")
            if ts_str:
                line_dt = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
                if line_dt.tzinfo is None:
                    line_dt = line_dt.replace(tzinfo=timezone.utc)
                if line_dt < since_dt:
                    continue

        active_steps += 1
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

    if since_dt is not None and planner_turns == 0:
        return None

    total_tokens = input_tokens + cache_read_tokens + output_tokens
    quota_5h_pct, quota_weekly_pct = compute_quota_pct(
        model, input_tokens, cache_read_tokens, output_tokens
    )

    # Taille transcript_full.jsonl
    full_file = conv_dir / ".system_generated" / "logs" / "transcript_full.jsonl"
    if full_file.exists():
        full_size_bytes = full_file.stat().st_size
    else:
        full_size_bytes = tfile.stat().st_size

    # Budget cible
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
        steps=active_steps if since_dt is not None else len(lines),
        input_tokens=input_tokens,
        cache_read_tokens=cache_read_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        quota_5h_pct=quota_5h_pct,
        quota_weekly_pct=quota_weekly_pct,
        full_size_bytes=full_size_bytes,
        tool_errors=tool_errors,
        cron_post_artefact=cron_post_artefact,
        budget_exceeded=budget_exceeded,
    )


def format_bytes(n: int) -> str:
    """Formatte une quantité d'octets de façon lisible."""
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def format_tokens(n: int) -> str:
    """Formatte un nombre de tokens de façon lisible (ex: 12.4k, 1.25M)."""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}k"
    return f"{n / 1_000_000:.2f}M"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI de télémétrie des tokens, sessions et anomalies Antigravity."
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

    args = parser.parse_args()

    # Détermination de la date seuil
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
    if not brain_dir.is_dir():
        sys.stderr.write(f"Erreur: Dossier introuvable: {brain_dir}\n")
        sys.exit(1)

    # 1. Cartographie globale des sous-agents
    registry = parse_subagent_registry(brain_dir)

    # 2. Analyse des conversations actives dans la fenêtre temporelle
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
            stat = analyze_conversation(conv_dir, registry, since_dt=since_dt)
            if stat:
                active_conversations.append(stat)

    # 3. Agrégations par Catégorie et Modèle
    cat_model_stats: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(lambda: defaultdict(lambda: {
        "sessions": 0,
        "planner_turns": 0,
        "steps": 0,
        "input_tokens": 0,
        "cache_read_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "quota_5h_pct": 0.0,
        "quota_weekly_pct": 0.0,
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
        entry["quota_5h_pct"] += c.quota_5h_pct
        entry["quota_weekly_pct"] += c.quota_weekly_pct
        entry["full_size_bytes"] += c.full_size_bytes
        entry["tool_errors"] += c.tool_errors
        entry["cron_post_artefact"] += c.cron_post_artefact
        if c.budget_exceeded:
            entry["budget_exceeded"] += 1

    # Ratios Flash vs Inherit
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

    # Anomalies
    subagent_budget_exceeded = sum(
        1 for c in active_conversations
        if c.category in ("eclaireur", "auditeur-alignement", "executant") and c.budget_exceeded
    )
    root_long_sessions = sum(1 for c in active_conversations if c.category == "ROOT" and c.budget_exceeded)
    total_tool_errors = sum(c.tool_errors for c in active_conversations)
    total_cron_post_artefact = sum(c.cron_post_artefact for c in active_conversations)

    # Top conversations par coût réel en quota (quota_weekly_pct)
    sorted_convs = sorted(active_conversations, key=lambda x: x.quota_weekly_pct, reverse=True)
    top_convs = sorted_convs[:args.top]

    # Totaux globaux
    tot_sessions = len(active_conversations)
    tot_turns = sum(c.planner_turns for c in active_conversations)
    tot_in_tk = sum(c.input_tokens for c in active_conversations)
    tot_cache_tk = sum(c.cache_read_tokens for c in active_conversations)
    tot_out_tk = sum(c.output_tokens for c in active_conversations)
    tot_tokens = sum(c.total_tokens for c in active_conversations)
    tot_q5h = sum(c.quota_5h_pct for c in active_conversations)
    tot_q7d = sum(c.quota_weekly_pct for c in active_conversations)
    tot_bytes = sum(c.full_size_bytes for c in active_conversations)

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
                "total_quota_5h_pct": round(tot_q5h, 4),
                "total_quota_weekly_pct": round(tot_q7d, 4),
                "total_transcript_full_bytes": tot_bytes,
            },
            "breakdown_by_category_model": {
                cat: {
                    mod: {
                        **vals,
                        "quota_5h_pct": round(vals["quota_5h_pct"], 4),
                        "quota_weekly_pct": round(vals["quota_weekly_pct"], 4),
                        "avg_turns": round(vals["planner_turns"] / vals["sessions"], 1) if vals["sessions"] > 0 else 0.0,
                        "avg_steps": round(vals["steps"] / vals["sessions"], 1) if vals["sessions"] > 0 else 0.0,
                        "avg_quota_5h_pct": round(vals["quota_5h_pct"] / vals["sessions"], 4) if vals["sessions"] > 0 else 0.0,
                        "avg_quota_weekly_pct": round(vals["quota_weekly_pct"] / vals["sessions"], 4) if vals["sessions"] > 0 else 0.0,
                    }
                    for mod, vals in mod_dict.items()
                }
                for cat, mod_dict in cat_model_stats.items()
            },
            "ratios": {
                "subagents_overall": {
                    "flash": subagent_counts["flash"],
                    "inherit": subagent_counts["inherit"],
                    "unknown": subagent_counts["unknown"],
                    "flash_pct": round(calc_ratio(subagent_counts), 1),
                },
                "eclaireur": {
                    "flash": eclaireur_counts["flash"],
                    "inherit": eclaireur_counts["inherit"],
                    "unknown": eclaireur_counts["unknown"],
                    "flash_pct": round(calc_ratio(eclaireur_counts), 1),
                },
                "executant": {
                    "flash": executant_counts["flash"],
                    "inherit": executant_counts["inherit"],
                    "unknown": executant_counts["unknown"],
                    "flash_pct": round(calc_ratio(executant_counts), 1),
                },
            },
            "anomalies": {
                "subagents_budget_exceeded": subagent_budget_exceeded,
                "root_long_sessions_gt_80_turns": root_long_sessions,
                "tool_errors_total": total_tool_errors,
                "cron_post_artefact_total": total_cron_post_artefact,
            },
            "top_conversations": [
                {
                    "conversation_id": c.conversation_id,
                    "category": c.category,
                    "model": c.model,
                    "role": c.role,
                    "parent_id": c.parent_id,
                    "planner_turns": c.planner_turns,
                    "steps": c.steps,
                    "total_tokens": c.total_tokens,
                    "input_tokens": c.input_tokens,
                    "cache_read_tokens": c.cache_read_tokens,
                    "output_tokens": c.output_tokens,
                    "quota_5h_pct": round(c.quota_5h_pct, 4),
                    "quota_weekly_pct": round(c.quota_weekly_pct, 4),
                    "tool_errors": c.tool_errors,
                    "cron_post_artefact": c.cron_post_artefact,
                    "full_size_bytes": c.full_size_bytes,
                    "budget_exceeded": c.budget_exceeded,
                }
                for c in top_convs
            ],
        }
        print(json.dumps(out_data, indent=2, ensure_ascii=False))
        return

    # Sortie Texte Tabulaire
    print("=" * 125)
    print(f"📊 TÉLÉMÉTRIE ANTIGRAVITY — Période : depuis {since_dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(
        f"Total conversations : {tot_sessions} | Tours LLM : {tot_turns} | Tokens : {format_tokens(tot_tokens)} "
        f"| Quota réel estimé : {tot_q5h:.2f}% (5h) / {tot_q7d:.2f}% (7j) | Logs : {format_bytes(tot_bytes)}"
    )
    print("=" * 125)
    print()

    print(
        f"{'Catégorie':<20} {'Modèle':<8} {'Sess.':>5} {'Tours (Moy)':>12} {'Étapes':>6} "
        f"{'Input Tk':>9} {'Cache Tk':>9} {'Output Tk':>9} {'Quota 5h (Moy)':>17} {'Quota 7j (Moy)':>17} {'Logs':>8}"
    )
    print("-" * 130)

    standard_cats = ["ROOT", "eclaireur", "executant", "auditeur-alignement", "superviseur-projet", "self", "image-generator", "unknown"]
    existing_cats = sorted(cat_model_stats.keys(), key=lambda x: standard_cats.index(x) if x in standard_cats else 99)

    for cat in existing_cats:
        mod_dict = cat_model_stats[cat]
        for mod in sorted(mod_dict.keys()):
            data = mod_dict[mod]
            sess = data["sessions"]
            turns = data["planner_turns"]
            avg_turns = turns / sess if sess > 0 else 0
            steps = data["steps"]
            avg_steps = steps / sess if sess > 0 else 0
            in_tk = format_tokens(data["input_tokens"])
            c_tk = format_tokens(data["cache_read_tokens"])
            out_tk = format_tokens(data["output_tokens"])
            q5 = data["quota_5h_pct"]
            q7 = data["quota_weekly_pct"]
            avg_q5 = q5 / sess if sess > 0 else 0.0
            avg_q7 = q7 / sess if sess > 0 else 0.0
            size = format_bytes(data["full_size_bytes"])

            t_disp = f"{turns} ({avg_turns:.1f})"
            q5_disp = f"{q5:.2f}% ({avg_q5:.3f}%)"
            q7_disp = f"{q7:.2f}% ({avg_q7:.3f}%)"
            print(
                f"{cat:<20} {mod:<8} {sess:>5} {t_disp:>12} {avg_steps:>6.1f} "
                f"{in_tk:>9} {c_tk:>9} {out_tk:>9} {q5_disp:>17} {q7_disp:>17} {size:>8}"
            )

    print("-" * 130)
    tot_q5_disp = f"{tot_q5h:.2f}%"
    tot_q7_disp = f"{tot_q7d:.2f}%"
    print(
        f"{'TOTAL':<29} {tot_sessions:>5} {tot_turns:>12} {'-':>6} "
        f"{format_tokens(tot_in_tk):>9} {format_tokens(tot_cache_tk):>9} {format_tokens(tot_out_tk):>9} "
        f"{tot_q5_disp:>17} {tot_q7_disp:>17} {format_bytes(tot_bytes):>8}"
    )
    print()

    # Ratios Flash vs Inherit
    print("⚖️  RATIOS FLASH vs INHERIT (Sous-agents)")
    def format_ratio_str(counts: Dict[str, int], target: str) -> str:
        f = counts.get("flash", 0)
        inh = counts.get("inherit", 0)
        unk = counts.get("unknown", 0)
        f_pct = calc_ratio(counts)
        tot_fi = f + inh
        inh_pct = (100.0 - f_pct) if tot_fi > 0 else 0.0
        unk_str = f" | {unk} unknown" if unk > 0 else ""
        return f"{f} flash ({f_pct:.1f}%) | {inh} inherit ({inh_pct:.1f}%){unk_str} [{target}]"

    print(f"  • Global sous-agents : {format_ratio_str(subagent_counts, 'Cible ~85-90% flash')}")
    print(f"  • Éclaireurs         : {format_ratio_str(eclaireur_counts, 'Cible 100% flash')}")
    print(f"  • Exécutants         : {format_ratio_str(executant_counts, 'Cible 100% flash')}")
    print()

    # Anomalies & Frictions
    print("🚨 ANOMALIES & FRICTIONS DÉTECTÉES")
    print(f"  • Sous-agents hors budget (>20 tours éclaireur/audit, >35 tours exécutant) : {subagent_budget_exceeded}")
    print(f"  • Sessions ROOT > 80 tours LLM (recommandation /handover ou /compact)      : {root_long_sessions}")
    print(f"  • Erreurs d'outils (status == 'ERROR')                                     : {total_tool_errors}")
    print(f"  • Réveils cron 'Auto-check' post-ARTEFACT (oubli de manage_task kill)     : {total_cron_post_artefact}")
    print()

    # Top conversations
    print(f"🏆 TOP {len(top_convs)} DES CONVERSATIONS LES PLUS COÛTEUSES (triées par Quota 7j réel)")
    print(f"{'Conv ID':<38} {'Catégorie':<18} {'Modèle':<8} {'Tours':>6} {'Quota 5h':>9} {'Quota 7j':>9} {'Tokens (Tot)':>12} {'Err':>4} {'Rôle / Sujet':<24}")
    print("-" * 135)
    for c in top_convs:
        role_disp = c.role[:22] + ".." if len(c.role) > 24 else c.role
        print(
            f"{c.conversation_id:<38} {c.category:<18} {c.model:<8} {c.planner_turns:>6} "
            f"{c.quota_5h_pct:>8.3f}% {c.quota_weekly_pct:>8.3f}% {format_tokens(c.total_tokens):>12} {c.tool_errors:>4} {role_disp:<24}"
        )
    print()


if __name__ == "__main__":
    main()
