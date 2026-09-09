#!/usr/bin/env python3
"""
Project Memory CLI
------------------
High-performance CLI interface for Obsidian project-memory plugin.
Calculates project scores, lists urgent tasks, logs session feedback,
extracts roadmap checkboxes, completes tasks, cleans orphan entries,
supports multi-scale agile milestone tracking (universal milestone parser),
and manages Pomodoro sessions with dynamic temporal recency malus.
Official and nominal Pomodoro duration is dynamically loaded from data.json
(settings.pomodoroDuration, default 60m), with --duration serving as an
exceptional optional override.
Uses data.json and a persistent incremental mtime cache for sub-millisecond to
low-millisecond execution even on large Obsidian vaults.
"""

import os
import sys
import json
import math
import re
import time
import shutil
import argparse
from datetime import datetime, date, time as dt_time, timedelta, timezone
from dataclasses import dataclass
from typing import Optional, Union, List, Any, Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_vault_dir(start_dir):
    curr = start_dir
    while curr and os.path.dirname(curr) != curr:
        if os.path.exists(os.path.join(curr, ".obsidian")):
            return curr
        if os.path.exists(os.path.join(curr, "VoiceNotes", ".obsidian")):
            return os.path.join(curr, "VoiceNotes")
        curr = os.path.dirname(curr)
    candidate = os.path.abspath(os.path.join(start_dir, "..", "VoiceNotes"))
    if os.path.exists(os.path.join(candidate, ".obsidian")):
        return candidate
    return os.path.abspath(os.path.join(start_dir, "..", ".."))


VAULT_DIR = find_vault_dir(SCRIPT_DIR)
DATA_JSON_PATH = os.path.join(VAULT_DIR, ".obsidian", "plugins", "project-memory", "data.json")
CACHE_PATH = os.path.join(VAULT_DIR, ".obsidian", "plugins", "project-memory", ".project_cache.json")
ACTIVE_POMODORO_PATH = os.path.join(VAULT_DIR, ".obsidian", "plugins", "project-memory", ".active_pomodoro.json")

EXCLUDED_DIRS = {
    ".obsidian", ".git", ".trash", ".claude", ".cursor",
    ".smart-env", ".pytest_cache", "attachments", "thumbnails",
    "excalidraw", "antigravity", "voicenotes", "readwise",
    "test_output_vault", "rattrapage_aib_pack", "templates",
    "tests", "agents", ".agents"
}

SYSTEM_FILES = {"agents.md", "readme.md", "claude.md", "gemini.md"}

DEFAULT_SETTINGS = {
    "projectTags": "todo, project",
    "archiveTag": "done",
    "rotationBonus": 0.3,
    "rapprochmentFactor": 0.2,
    "recencyPenaltyWeight": 0.5,
    "pomodoroDuration": 60,
    "deadlineProperty": "deadline",
    "milestoneProperty": "milestone"
}

DAY_NAMES_MAP = {
    # French
    "lundi": 0, "lun": 0, "lu": 0,
    "mardi": 1, "mar": 1, "ma": 1,
    "mercredi": 2, "mer": 2, "me": 2,
    "jeudi": 3, "jeu": 3, "je": 3,
    "vendredi": 4, "ven": 4, "ve": 4,
    "samedi": 5, "sam": 5, "sa": 5,
    "dimanche": 6, "dim": 6, "di": 6,
    # English
    "monday": 0, "mon": 0, "mo": 0,
    "tuesday": 1, "tue": 1, "tu": 1,
    "wednesday": 2, "wed": 2, "we": 2,
    "thursday": 3, "thu": 3, "th": 3,
    "friday": 4, "fri": 4, "fr": 4,
    "saturday": 5, "sat": 5, "sa": 5,
    "sunday": 6, "sun": 6, "su": 6,
}

CRON_SHORTCUTS = {
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@workdays": "0 9 * * 1-5",
    "@weekdays": "0 9 * * 1-5",
}


@dataclass
class MilestoneResolution:
    raw_expression: str
    target_datetime: Optional[datetime]
    days_remaining: float
    urgency_factor: float
    recurrence_type: str  # 'fixed_date' | 'day_recurrence' | 'cron' | 'iso_interval' | 'multi' | 'invalid'
    is_overdue: bool
    is_cycle_satisfied: bool
    cycle_id: str
    human_readable: str
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_expression": self.raw_expression,
            "target_datetime": self.target_datetime.isoformat() if self.target_datetime else None,
            "days_remaining": self.days_remaining,
            "urgency_factor": self.urgency_factor,
            "recurrence_type": self.recurrence_type,
            "is_overdue": self.is_overdue,
            "is_cycle_satisfied": self.is_cycle_satisfied,
            "cycle_id": self.cycle_id,
            "human_readable": self.human_readable,
            "error": self.error,
        }


class UniversalMilestoneParser:
    """
    Universal Milestone Parser supporting:
    - Fixed ISO dates/datetimes ('2026-08-28', '2026-08-28T10:00', '2026-08-28 14:30:00+02:00')
    - Day recurrence in FR & EN ('mercredi', 'wednesday', 'every wednesday', 'tous les vendredis')
    - Periodicity & Time ('mercredi@3', 'mercredi@14', 'mercredi@14:00', 'vendredi à 10h30')
    - Cron recurrence syntax & shortcuts ('0 10 * * 3', '* * * * WED', '@weekly', '@daily')
    - ISO 8601 repeating intervals ('R/2026-08-26/P7D', 'R5/2026-08-26T10:00:00/P1W', 'R/PT12H')
    - Multi-value milestone declarations (['mardi', 'jeudi'] or '2026-08-28, 2026-09-04')
    - Cycle clearance handling via last_satisfied_date
    """

    def __init__(self, default_lambda: float = 0.3):
        self.default_lambda = default_lambda

    def parse(
        self,
        milestone_input: Union[str, List[Any], Dict[str, Any]],
        now: Optional[datetime] = None,
        last_satisfied_date: Optional[Union[str, datetime]] = None,
        lambda_factor: Optional[float] = None
    ) -> MilestoneResolution:
        if now is None:
            now = datetime.now()

        lam = lambda_factor if lambda_factor is not None else self.default_lambda

        # Parse last satisfied date
        last_sat_dt: Optional[datetime] = None
        if last_satisfied_date:
            if isinstance(last_satisfied_date, datetime):
                last_sat_dt = last_satisfied_date
            elif isinstance(last_satisfied_date, str) and last_satisfied_date.strip():
                try:
                    last_sat_dt = datetime.fromisoformat(last_satisfied_date.replace("Z", "+00:00"))
                    if last_sat_dt.tzinfo is not None and now.tzinfo is None:
                        last_sat_dt = last_sat_dt.replace(tzinfo=None)
                except Exception:
                    pass

        # Handle list or comma-separated milestones
        if isinstance(milestone_input, list):
            resolutions = [
                self.parse(item, now=now, last_satisfied_date=last_sat_dt, lambda_factor=lam)
                for item in milestone_input if item
            ]
            valid_res = [r for r in resolutions if r.target_datetime is not None]
            if not valid_res:
                return MilestoneResolution(
                    raw_expression=str(milestone_input),
                    target_datetime=None,
                    days_remaining=float('inf'),
                    urgency_factor=0.0,
                    recurrence_type='multi',
                    is_overdue=False,
                    is_cycle_satisfied=False,
                    cycle_id='',
                    human_readable='No valid milestones in list',
                    error='All elements failed parsing'
                )
            best_res = max(valid_res, key=lambda r: r.urgency_factor)
            return MilestoneResolution(
                raw_expression=str(milestone_input),
                target_datetime=best_res.target_datetime,
                days_remaining=best_res.days_remaining,
                urgency_factor=best_res.urgency_factor,
                recurrence_type='multi',
                is_overdue=best_res.is_overdue,
                is_cycle_satisfied=best_res.is_cycle_satisfied,
                cycle_id=best_res.cycle_id,
                human_readable=f"Multi: {best_res.human_readable} (selected from {len(valid_res)} milestones)"
            )

        expr = str(milestone_input).strip()
        if not expr:
            return MilestoneResolution(
                raw_expression="",
                target_datetime=None,
                days_remaining=float('inf'),
                urgency_factor=0.0,
                recurrence_type='invalid',
                is_overdue=False,
                is_cycle_satisfied=False,
                cycle_id='',
                human_readable='Empty milestone expression'
            )

        # If comma-separated multi string (e.g. "mercredi, 2026-08-28") and not cron
        if "," in expr and not self._is_cron_pattern(expr):
            sub_items = [p.strip() for p in expr.split(",") if p.strip()]
            if len(sub_items) > 1:
                return self.parse(sub_items, now=now, last_satisfied_date=last_sat_dt, lambda_factor=lam)

        # 1. Check Cron Shortcut or Syntax
        cron_expr = CRON_SHORTCUTS.get(expr.lower()) or (expr if self._is_cron_pattern(expr) else None)
        if cron_expr:
            return self._parse_cron(expr, cron_expr, now, last_sat_dt, lam)

        # 2. Check ISO 8601 Repeating Interval: R[n]/start/duration
        if expr.upper().startswith("R"):
            iso_res = self._parse_iso_interval(expr, now, last_sat_dt, lam)
            if iso_res:
                return iso_res

        # 3. Check Fixed ISO Date / Datetime
        iso_fixed_dt = self._try_parse_iso_date(expr)
        if iso_fixed_dt:
            return self._resolve_fixed_date(expr, iso_fixed_dt, now, last_sat_dt, lam)

        # 4. Check Day Recurrence (FR & EN)
        day_res = self._try_parse_day_recurrence(expr, now, last_sat_dt, lam)
        if day_res:
            return day_res

        # 5. Fallback / Unrecognized
        return MilestoneResolution(
            raw_expression=expr,
            target_datetime=None,
            days_remaining=float('inf'),
            urgency_factor=0.0,
            recurrence_type='invalid',
            is_overdue=False,
            is_cycle_satisfied=False,
            cycle_id='',
            human_readable=f"Invalid milestone format: '{expr}'",
            error=f"Cannot parse milestone expression: '{expr}'"
        )

    def _is_cron_pattern(self, expr: str) -> bool:
        parts = expr.strip().split()
        if len(parts) != 5:
            return False
        cron_pattern = r'^[0-9\*\/,\-\?a-zA-Z]+$'
        return all(re.match(cron_pattern, p) for p in parts)

    def _parse_cron(
        self,
        raw_expr: str,
        cron_pattern: str,
        now: datetime,
        last_sat_dt: Optional[datetime],
        lam: float
    ) -> MilestoneResolution:
        parts = cron_pattern.split()
        min_spec, hour_spec, dom_spec, mon_spec, dow_spec = parts

        # 1. Find most recent past occurrence (within last 366 days)
        past_target: Optional[datetime] = None
        for day_offset in range(0, -366, -1):
            check_date = (now + timedelta(days=day_offset)).date()
            if not self._match_cron_field(mon_spec, check_date.month, 1, 12):
                continue
            if not self._match_cron_field(dom_spec, check_date.day, 1, 31):
                continue
            dow_cron = (check_date.weekday() + 1) % 7
            if not self._match_cron_dow(dow_spec, dow_cron):
                continue

            target_hours = self._expand_cron_field(hour_spec, 0, 23)
            target_mins = self._expand_cron_field(min_spec, 0, 59)

            for h in sorted(target_hours, reverse=True):
                for m in sorted(target_mins, reverse=True):
                    cand_dt = datetime.combine(check_date, dt_time(h, m))
                    if cand_dt <= now:
                        past_target = cand_dt
                        break
                if past_target:
                    break
            if past_target:
                break

        # Check if past occurrence was satisfied
        if past_target:
            past_sat = False
            if last_sat_dt and (last_sat_dt >= past_target or last_sat_dt.date() >= past_target.date()):
                past_sat = True
            if not past_sat:
                diff_sec = (past_target - now).total_seconds()
                days_rem = diff_sec / 86400.0
                return MilestoneResolution(
                    raw_expression=raw_expr,
                    target_datetime=past_target,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=1.0,
                    recurrence_type='cron',
                    is_overdue=True,
                    is_cycle_satisfied=False,
                    cycle_id=f"cron_{past_target.strftime('%Y-%m-%d_%H%M')}",
                    human_readable=f"Cron {raw_expr} (OVERDUE by {abs(days_rem):.1f}d): target was {past_target.strftime('%A %Y-%m-%d at %H:%M')}"
                )

        # 2. Find next future occurrence
        found_target: Optional[datetime] = None
        cycle_satisfied = False

        for day_offset in range(366):
            check_date = (now + timedelta(days=day_offset)).date()
            if not self._match_cron_field(mon_spec, check_date.month, 1, 12):
                continue
            if not self._match_cron_field(dom_spec, check_date.day, 1, 31):
                continue

            dow_cron = (check_date.weekday() + 1) % 7
            if not self._match_cron_dow(dow_spec, dow_cron):
                continue

            target_hours = self._expand_cron_field(hour_spec, 0, 23)
            target_mins = self._expand_cron_field(min_spec, 0, 59)

            for h in sorted(target_hours):
                for m in sorted(target_mins):
                    cand_dt = datetime.combine(check_date, dt_time(h, m))
                    if cand_dt <= now:
                        continue

                    if last_sat_dt and (last_sat_dt >= cand_dt or last_sat_dt.date() >= cand_dt.date()):
                        cycle_satisfied = True
                        continue

                    found_target = cand_dt
                    break
                if found_target:
                    break
            if found_target:
                break

        if not found_target:
            return MilestoneResolution(
                raw_expression=raw_expr,
                target_datetime=None,
                days_remaining=float('inf'),
                urgency_factor=0.0,
                recurrence_type='cron',
                is_overdue=False,
                is_cycle_satisfied=cycle_satisfied,
                cycle_id='',
                human_readable=f"Cron {raw_expr}: No future occurrence within 1 year"
            )

        diff = (found_target - now).total_seconds() / 86400.0
        days_rem = max(0.0, diff)
        urgency = 0.0 if cycle_satisfied else math.exp(-lam * days_rem)
        cycle_id = f"cron_{found_target.strftime('%Y-%m-%d_%H%M')}"
        status_str = " (validé)" if cycle_satisfied else ""

        return MilestoneResolution(
            raw_expression=raw_expr,
            target_datetime=found_target,
            days_remaining=round(days_rem, 3),
            urgency_factor=round(urgency, 4),
            recurrence_type='cron',
            is_overdue=False,
            is_cycle_satisfied=cycle_satisfied,
            cycle_id=cycle_id,
            human_readable=f"Next cron trigger{status_str}: {found_target.strftime('%A %Y-%m-%d at %H:%M')}"
        )

    def _match_cron_field(self, spec: str, val: int, min_val: int, max_val: int) -> bool:
        if spec in ("*", "?"):
            return True
        allowed = self._expand_cron_field(spec, min_val, max_val)
        return val in allowed

    def _match_cron_dow(self, spec: str, dow_val: int) -> bool:
        if spec in ("*", "?"):
            return True
        word_map = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
        spec_clean = spec.lower()
        for w, v in word_map.items():
            spec_clean = spec_clean.replace(w, str(v))
        allowed = self._expand_cron_field(spec_clean, 0, 7)
        if 7 in allowed:
            allowed.add(0)
        return dow_val in allowed

    def _expand_cron_field(self, spec: str, min_val: int, max_val: int) -> set:
        res = set()
        for part in spec.split(","):
            if part in ("*", "?"):
                return set(range(min_val, max_val + 1))
            if "/" in part:
                subparts = part.split("/")
                step = int(subparts[1])
                start_range = range(min_val, max_val + 1) if subparts[0] in ("*", "") else range(int(subparts[0]), max_val + 1)
                for val in start_range:
                    if (val - (min_val if subparts[0] in ("*", "") else int(subparts[0]))) % step == 0:
                        res.add(val)
            elif "-" in part:
                start, end = map(int, part.split("-"))
                res.update(range(start, end + 1))
            else:
                try:
                    res.add(int(part))
                except ValueError:
                    pass
        return res

    def _try_parse_iso_date(self, expr: str) -> Optional[datetime]:
        pattern = r'^(\d{4}-\d{2}-\d{2})(?:[T\s](\d{2}:\d{2}(?::\d{2})?))?(?:\s*([+-]\d{2}:?\d{2}|Z))?$'
        m = re.match(pattern, expr.strip())
        if not m:
            return None

        date_part, time_part, _ = m.groups()
        try:
            d = date.fromisoformat(date_part)
            if time_part:
                t_elements = [int(p) for p in time_part.split(":")]
                if len(t_elements) == 2:
                    t = dt_time(t_elements[0], t_elements[1], 0)
                else:
                    t = dt_time(t_elements[0], t_elements[1], t_elements[2])
            else:
                t = dt_time(23, 59, 59)
            return datetime.combine(d, t)
        except Exception:
            return None

    def _resolve_fixed_date(
        self,
        raw_expr: str,
        target_dt: datetime,
        now: datetime,
        last_sat_dt: Optional[datetime],
        lam: float
    ) -> MilestoneResolution:
        diff_sec = (target_dt - now).total_seconds()
        days_rem = diff_sec / 86400.0
        is_overdue = days_rem < 0.0

        is_satisfied = False
        if last_sat_dt and (last_sat_dt >= target_dt or last_sat_dt.date() >= target_dt.date()):
            is_satisfied = True

        if is_satisfied:
            urgency = 0.0
        elif is_overdue:
            urgency = 1.0
        else:
            urgency = math.exp(-lam * days_rem)

        cycle_id = f"fixed_{target_dt.strftime('%Y-%m-%d')}"
        status_str = " (validée)" if is_satisfied else (" (en retard)" if is_overdue else "")
        return MilestoneResolution(
            raw_expression=raw_expr,
            target_datetime=target_dt,
            days_remaining=round(days_rem, 3),
            urgency_factor=round(urgency, 4),
            recurrence_type='fixed_date',
            is_overdue=is_overdue and not is_satisfied,
            is_cycle_satisfied=is_satisfied,
            cycle_id=cycle_id,
            human_readable=f"Fixed Milestone: {target_dt.strftime('%Y-%m-%d %H:%M')}{status_str}"
        )

    def _try_parse_day_recurrence(
        self,
        expr: str,
        now: datetime,
        last_sat_dt: Optional[datetime],
        lam: float
    ) -> Optional[MilestoneResolution]:
        clean = expr.strip().lower()
        clean = re.sub(r'^(every|tous\s+les|chaque|each)\s+', '', clean)
        clean = re.sub(r's$', '', clean)

        interval_weeks = 1
        m_interval = re.search(r'@(\d+)$', clean)
        if m_interval:
            parsed_n = int(m_interval.group(1))
            if parsed_n >= 1:
                interval_weeks = parsed_n
                clean = clean[:m_interval.start()].strip()

        # Match time / periodicity specifiers like @14, @3, @14:00, at 14:00, à 10h30, 14h00, 14h
        m_time = re.search(r'(?:at|@|\s+à|\s+a)?\s*(\d{1,2})(?:[h:](\d{2})(?::(\d{2}))?|h)?$', clean)
        target_time = dt_time(23, 59, 59)
        if m_time:
            h = int(m_time.group(1))
            m = int(m_time.group(2) or 0)
            s = int(m_time.group(3) or 0)
            if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59:
                target_time = dt_time(h, m, s)
                clean = clean[:m_time.start()].strip()

        if clean not in DAY_NAMES_MAP:
            return None

        target_weekday = DAY_NAMES_MAP[clean]
        current_weekday = now.weekday()

        days_ahead = (target_weekday - current_weekday) % 7
        today = now.date()

        if days_ahead == 0:
            target_dt_today = datetime.combine(today, target_time)
            is_sat = False
            if last_sat_dt and (last_sat_dt >= target_dt_today or last_sat_dt.date() >= today):
                is_sat = True

            if is_sat:
                target_dt = target_dt_today + timedelta(days=interval_weeks * 7)
                diff_sec = (target_dt - now).total_seconds()
                days_rem = max(0.0, diff_sec / 86400.0)
                urgency = 0.0
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=target_dt,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=round(urgency, 4),
                    recurrence_type='day_recurrence',
                    is_overdue=False,
                    is_cycle_satisfied=True,
                    cycle_id=f"weekly_W{target_dt.strftime('%V')}_{clean.upper()}",
                    human_readable=f"Recurring {clean.capitalize()} (validé): next {target_dt.strftime('%A %Y-%m-%d at %H:%M')}"
                )
            elif now > target_dt_today:
                # Target was earlier today without satisfaction -> overdue!
                diff_sec = (target_dt_today - now).total_seconds()
                days_rem = diff_sec / 86400.0
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=target_dt_today,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=1.0,
                    recurrence_type='day_recurrence',
                    is_overdue=True,
                    is_cycle_satisfied=False,
                    cycle_id=f"weekly_W{target_dt_today.strftime('%V')}_{clean.upper()}",
                    human_readable=f"Recurring {clean.capitalize()} (OVERDUE today): target was {target_dt_today.strftime('%H:%M')}"
                )
            else:
                # Target is later today
                diff_sec = (target_dt_today - now).total_seconds()
                days_rem = max(0.0, diff_sec / 86400.0)
                urgency = 1.0
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=target_dt_today,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=round(urgency, 4),
                    recurrence_type='day_recurrence',
                    is_overdue=False,
                    is_cycle_satisfied=False,
                    cycle_id=f"weekly_W{target_dt_today.strftime('%V')}_{clean.upper()}",
                    human_readable=f"Recurring {clean.capitalize()}: today at {target_dt_today.strftime('%H:%M')}"
                )
        else:
            # days_ahead > 0: check if previous occurrence was satisfied
            t_prev = datetime.combine(today - timedelta(days=7 - days_ahead), target_time)
            t_next = datetime.combine(today + timedelta(days=days_ahead), target_time)

            is_prev_sat = False
            if last_sat_dt and (last_sat_dt >= t_prev or last_sat_dt.date() >= t_prev.date()):
                is_prev_sat = True

            if not is_prev_sat:
                # Previous milestone was NOT satisfied -> OVERDUE!
                diff_sec = (t_prev - now).total_seconds()
                days_rem = diff_sec / 86400.0
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=t_prev,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=1.0,
                    recurrence_type='day_recurrence',
                    is_overdue=True,
                    is_cycle_satisfied=False,
                    cycle_id=f"weekly_W{t_prev.strftime('%V')}_{clean.upper()}",
                    human_readable=f"Recurring {clean.capitalize()} (OVERDUE by {abs(days_rem):.1f}d): target was {t_prev.strftime('%A %Y-%m-%d at %H:%M')}"
                )
            else:
                # Previous milestone satisfied -> advance to next upcoming occurrence
                curr_target = t_next
                is_cycle_sat = False
                while last_sat_dt and (last_sat_dt >= curr_target or last_sat_dt.date() >= curr_target.date()):
                    is_cycle_sat = True
                    curr_target = curr_target + timedelta(days=interval_weeks * 7)

                diff_sec = (curr_target - now).total_seconds()
                days_rem = max(0.0, diff_sec / 86400.0)
                urgency = 0.0 if is_cycle_sat else math.exp(-lam * days_rem)
                status_str = " (validé)" if is_cycle_sat else ""
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=curr_target,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=round(urgency, 4),
                    recurrence_type='day_recurrence',
                    is_overdue=False,
                    is_cycle_satisfied=is_cycle_sat,
                    cycle_id=f"weekly_W{curr_target.strftime('%V')}_{clean.upper()}",
                    human_readable=f"Recurring {clean.capitalize()}{status_str}: next {curr_target.strftime('%A %Y-%m-%d at %H:%M')}"
                )

    def _parse_iso_interval(
        self,
        expr: str,
        now: datetime,
        last_sat_dt: Optional[datetime],
        lam: float
    ) -> Optional[MilestoneResolution]:
        pattern = r'^R(\d*)\/(?:([^/]+)\/)?(P(?:[0-9YMWD]+)?(?:T[0-9HMS]+)?)$'
        m = re.match(pattern, expr.strip(), re.IGNORECASE)
        if not m:
            return None

        max_reps_str, start_str, duration_str = m.groups()
        max_reps = int(max_reps_str) if max_reps_str else None

        duration_delta = self._parse_iso_duration(duration_str)
        if not duration_delta or duration_delta.total_seconds() <= 0:
            return None

        start_dt = self._try_parse_iso_date(start_str) if start_str else now
        if not start_dt:
            start_dt = now

        curr_dt = start_dt
        rep_count = 0
        past_target = None
        found_target = None
        cycle_satisfied = False

        while True:
            if max_reps is not None and rep_count >= max_reps:
                break
            if curr_dt <= now:
                past_target = curr_dt
            else:
                if last_sat_dt and (last_sat_dt >= curr_dt or last_sat_dt.date() >= curr_dt.date()):
                    cycle_satisfied = True
                else:
                    found_target = curr_dt
                    break
            curr_dt += duration_delta
            rep_count += 1
            if rep_count > 1000:
                break

        # Check if past target was satisfied
        if past_target:
            past_sat = False
            if last_sat_dt and (last_sat_dt >= past_target or last_sat_dt.date() >= past_target.date()):
                past_sat = True
            if not past_sat:
                diff_sec = (past_target - now).total_seconds()
                days_rem = diff_sec / 86400.0
                return MilestoneResolution(
                    raw_expression=expr,
                    target_datetime=past_target,
                    days_remaining=round(days_rem, 3),
                    urgency_factor=1.0,
                    recurrence_type='iso_interval',
                    is_overdue=True,
                    is_cycle_satisfied=False,
                    cycle_id=f"interval_{past_target.strftime('%Y%m%d_%H%M')}",
                    human_readable=f"ISO interval {expr} (OVERDUE by {abs(days_rem):.1f}d): target was {past_target.strftime('%Y-%m-%d %H:%M')}"
                )

        if not found_target:
            return MilestoneResolution(
                raw_expression=expr,
                target_datetime=None,
                days_remaining=float('inf'),
                urgency_factor=0.0,
                recurrence_type='iso_interval',
                is_overdue=False,
                is_cycle_satisfied=cycle_satisfied,
                cycle_id='',
                human_readable=f"ISO interval {expr} completed all {max_reps} repetitions"
            )

        diff_sec = (found_target - now).total_seconds()
        days_rem = max(0.0, diff_sec / 86400.0)
        urgency = 0.0 if cycle_satisfied else math.exp(-lam * days_rem)
        cycle_id = f"interval_{found_target.strftime('%Y%m%d_%H%M')}"
        status_str = " (validé)" if cycle_satisfied else ""

        return MilestoneResolution(
            raw_expression=expr,
            target_datetime=found_target,
            days_remaining=round(days_rem, 3),
            urgency_factor=round(urgency, 4),
            recurrence_type='iso_interval',
            is_overdue=False,
            is_cycle_satisfied=cycle_satisfied,
            cycle_id=cycle_id,
            human_readable=f"Next ISO interval target{status_str}: {found_target.strftime('%Y-%m-%d %H:%M')}"
        )

    def _parse_iso_duration(self, dur_str: str) -> Optional[timedelta]:
        m = re.match(
            r'^P(?:(?P<weeks>\d+)W)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$',
            dur_str.upper()
        )
        if not m:
            return None
        parts = m.groupdict()
        weeks = int(parts.get('weeks') or 0)
        days = int(parts.get('days') or 0) + weeks * 7
        hours = int(parts.get('hours') or 0)
        minutes = int(parts.get('minutes') or 0)
        seconds = int(parts.get('seconds') or 0)
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def parse_milestone_target(raw_milestone, last_satisfied_str=None, now_dt=None) -> MilestoneResolution:
    """
    Top-level helper parsing any raw milestone expression into a MilestoneResolution.
    """
    parser = UniversalMilestoneParser(default_lambda=0.3)
    return parser.parse(raw_milestone, now=now_dt, last_satisfied_date=last_satisfied_str)


def load_data(data_path=DATA_JSON_PATH):
    if not os.path.exists(data_path):
        return {
            "settings": DEFAULT_SETTINGS.copy(),
            "stats": {"projects": {}, "globalStats": {"totalReviews": 0, "totalPomodoroTime": 0}}
        }
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "settings" not in data:
        data["settings"] = DEFAULT_SETTINGS.copy()
    else:
        for k, v in DEFAULT_SETTINGS.items():
            if k not in data["settings"]:
                data["settings"][k] = v

    if "stats" not in data:
        data["stats"] = {"projects": {}, "globalStats": {"totalReviews": 0, "totalPomodoroTime": 0}}
    if "projects" not in data["stats"]:
        data["stats"]["projects"] = {}
    if "globalStats" not in data["stats"]:
        data["stats"]["globalStats"] = {"totalReviews": 0, "totalPomodoroTime": 0}
    return data


def save_data(data, data_path=DATA_JSON_PATH):
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    temp_path = data_path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_path, data_path)


def load_cache(cache_path=CACHE_PATH):
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache, cache_path=CACHE_PATH):
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        tmp = cache_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        os.replace(tmp, cache_path)
    except Exception:
        pass


def load_active_pomodoro(active_path=ACTIVE_POMODORO_PATH):
    if os.path.exists(active_path):
        try:
            with open(active_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_active_pomodoro(pomodoro_info, active_path=ACTIVE_POMODORO_PATH):
    try:
        os.makedirs(os.path.dirname(active_path), exist_ok=True)
        tmp = active_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(pomodoro_info, f, indent=2, ensure_ascii=False)
        os.replace(tmp, active_path)
    except Exception:
        pass


def clear_active_pomodoro(active_path=ACTIVE_POMODORO_PATH):
    try:
        if os.path.exists(active_path):
            os.remove(active_path)
    except Exception:
        pass


def is_pid_alive(pid):
    if not pid or pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if not handle:
                return False
            exit_code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
            kernel32.CloseHandle(handle)
            return exit_code.value == STILL_ACTIVE
        except Exception:
            return True
    else:
        try:
            os.kill(int(pid), 0)
            return True
        except (OSError, ProcessLookupError):
            return False


def record_work_session(
    data,
    rel_path,
    elapsed_minutes,
    target_minutes=None,
    is_interrupted=False,
    data_path=DATA_JSON_PATH
):
    """
    Enregistre une session de travail (complète ou interrompue proportionnellement) dans data.json :
    - Calcule le ratio r = T_elapsed / T_target
    - Enregistre la session dans recentWorkDates avec son ratio et sa durée
    - Incrémente les statistiques globales (globalStats.totalPomodoroTime += T_elapsed)
    - Applique la rotation des bonus (+0.3 * r aux autres projets, réinitialisation proportionnelle)
    - Valide le jalon synchrone si r >= 0.5 ou session complète
    """
    stats = data.setdefault("stats", {}).setdefault("projects", {})
    global_stats = data.setdefault("stats", {}).setdefault("globalStats", {"totalReviews": 0, "totalPomodoroTime": 0})
    settings = data.setdefault("settings", {})
    rot_inc = float(settings.get("rotationBonus", 0.3))

    if target_minutes is None:
        # Comportement officiel et nominal : durée cible définie dans settings.pomodoroDuration (data.json)
        target_minutes = float(settings.get("pomodoroDuration", 60))

    ratio = min(1.0, max(0.0, elapsed_minutes / target_minutes)) if target_minutes > 0 else 1.0

    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()

    matched_key = None
    for k in stats.keys():
        if k == rel_path or os.path.basename(k) == os.path.basename(rel_path) or k.endswith(rel_path):
            matched_key = k
            break
    if not matched_key:
        matched_key = rel_path

    if matched_key not in stats:
        proj = {
            "rotationBonus": 0.0,
            "totalReviews": 0,
            "lastReviewDate": "",
            "reviewHistory": [],
            "recentWorkDates": []
        }
        stats[matched_key] = proj
    else:
        proj = stats[matched_key]

    # Purge des sessions de plus de 6 heures
    existing_work = proj.get("recentWorkDates", [])
    valid_dates = []
    for item in existing_work:
        d_str = item.get("date") if isinstance(item, dict) else str(item)
        d_dt = parse_iso_datetime(d_str)
        if d_dt:
            delta_h = (now_dt - d_dt).total_seconds() / 3600.0
            if -0.05 <= delta_h < 6.0:
                valid_dates.append(item)

    # N'ajoute la session que si la durée est significative (> 2 secondes)
    if elapsed_minutes > 0.03:
        if is_interrupted or ratio < 0.99:
            session_entry = {
                "date": now_iso,
                "ratio": round(ratio, 4),
                "duration_minutes": round(elapsed_minutes, 2),
                "target_minutes": round(target_minutes, 2),
                "interrupted": is_interrupted
            }
        else:
            session_entry = now_iso
        valid_dates.append(session_entry)

    proj["recentWorkDates"] = valid_dates

    # Validation du jalon si au moins 50% du pomodoro a été accompli ou si complet
    if ratio >= 0.5 or not is_interrupted:
        proj["lastSatisfiedMilestoneDate"] = now_iso

    # Gestion proportionnelle du bonus de rotation
    if ratio >= 0.8:
        proj["rotationBonus"] = 0.0
    else:
        current_bonus = float(proj.get("rotationBonus", 0.0))
        proj["rotationBonus"] = round(max(0.0, current_bonus * (1.0 - ratio)), 3)

    for p_key, p_val in stats.items():
        if p_key != matched_key:
            p_val["rotationBonus"] = round(float(p_val.get("rotationBonus", 0.0)) + rot_inc * ratio, 3)

    # Accumulation du temps dans les stats globales
    prev_pomodoro_time = float(global_stats.get("totalPomodoroTime", 0))
    global_stats["totalPomodoroTime"] = round(prev_pomodoro_time + elapsed_minutes, 2)

    save_data(data, data_path)
    return matched_key, ratio


def parse_iso_datetime(dt_str_or_obj):
    """
    Robust ISO datetime parser supporting UTC strings with 'Z', '+00:00', dict entries with 'date', and microseconds.
    """
    if not dt_str_or_obj:
        return None
    if isinstance(dt_str_or_obj, dict):
        dt_str = dt_str_or_obj.get("date")
    else:
        dt_str = dt_str_or_obj
    if not dt_str:
        return None
    try:
        s = str(dt_str).strip()
        if s.endswith("Z") or s.endswith("z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def compute_temporal_recency_malus(recent_work_dates, pre_score, rf, weight, now_dt=None):
    """
    Calculates the temporal recency malus based on active work sessions in the last 6 hours.
    Supports proportional work session entries (ratio r in [0, 1]).
    For each session i within 6h:
      k_i = r_i * (1.0 - (delta_t_i / 6.0))
      K = sum(k_i)
    Malus = K * rf * weight * max(0.0, pre_score - 1.0)
    Returns: (malus, K, valid_dates_within_6h)
    """
    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    if not recent_work_dates:
        return 0.0, 0.0, []

    k_sum = 0.0
    valid_dates = []

    for item in recent_work_dates:
        ratio = 1.0
        if isinstance(item, dict):
            d_str = item.get("date", "")
            raw_ratio = item.get("ratio", item.get("weight", 1.0))
            try:
                ratio = float(raw_ratio)
            except (ValueError, TypeError):
                ratio = 1.0
        else:
            d_str = str(item)

        d_dt = parse_iso_datetime(d_str)
        if not d_dt:
            continue
        delta_hours = (now_dt - d_dt).total_seconds() / 3600.0
        if -0.05 <= delta_hours < 6.0:
            delta_h = max(0.0, delta_hours)
            k_i = ratio * (1.0 - (delta_h / 6.0))
            k_sum += k_i
            valid_dates.append(item)

    if pre_score is None or pre_score <= 1.0 or k_sum <= 0.0:
        return 0.0, round(k_sum, 4), valid_dates

    malus = k_sum * float(rf) * float(weight) * max(0.0, float(pre_score) - 1.0)
    return round(malus, 3), round(k_sum, 4), valid_dates


def parse_markdown_file(file_path, content=None, parse_checkboxes=True):
    """
    Parses a markdown file in a single fast pass for frontmatter, tags, checkboxes, and content.
    Returns: (frontmatter_dict, tags_set, checkboxes_list, content_str)
    """
    try:
        if content is None:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
    except Exception:
        return {}, set(), [], ""

    frontmatter = {}
    tags = set()
    checkboxes = []

    lines = content.splitlines()
    body_lines = lines

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_raw = parts[1]
            body_lines = parts[2].splitlines()
            current_list_key = None

            for line in fm_raw.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if ":" in stripped and not stripped.startswith("-"):
                    k, v = stripped.split(":", 1)
                    k_str = k.strip().lower()
                    v_str = v.strip().strip("\"'")
                    frontmatter[k_str] = v_str
                    current_list_key = k_str

                    if k_str in ("tags", "tag"):
                        if v_str.startswith("[") and v_str.endswith("]"):
                            items = v_str[1:-1].split(",")
                            for item in items:
                                t = item.strip().strip("\"'").lstrip("#")
                                if t:
                                    tags.add(t.lower())
                            current_list_key = None
                        elif v_str:
                            items = v_str.split(",")
                            for item in items:
                                t = item.strip().strip("\"'").lstrip("#")
                                if t:
                                    tags.add(t.lower())
                            current_list_key = None
                elif current_list_key and stripped.startswith("-"):
                    item_val = stripped[1:].strip().strip("\"'")
                    if current_list_key in ("tags", "tag"):
                        t = item_val.lstrip("#")
                        if t:
                            tags.add(t.lower())
                    else:
                        existing = frontmatter.get(current_list_key)
                        if isinstance(existing, list):
                            existing.append(item_val)
                        elif existing:
                            frontmatter[current_list_key] = [existing, item_val]
                        else:
                            frontmatter[current_list_key] = [item_val]
                elif not stripped.startswith("-"):
                    current_list_key = None

    # Inline tags `#tag`
    if "#" in content:
        inline_tags = re.findall(r'(?:^|[^\w#])#([a-zA-Z0-9_\-\/]+)', content)
        for tag in inline_tags:
            tags.add(tag.lower())

    # Checkboxes `[ ]` and `[x]`
    if parse_checkboxes and "[" in content and "]" in content:
        for idx, line in enumerate(body_lines, 1):
            if "[" in line and "]" in line:
                m = re.match(r'^\s*[-*+]\s+\[([ xX])\]\s+(.*)$', line)
                if m:
                    is_completed = m.group(1).lower() == 'x'
                    text = m.group(2).strip()
                    checkboxes.append({
                        "line": idx,
                        "completed": is_completed,
                        "text": text,
                        "raw": line
                    })

    return frontmatter, tags, checkboxes, content


def sync_vault_cache(vault_dir=VAULT_DIR, cache_path=CACHE_PATH, fast_mode=False):
    """
    Synchronizes the fast metadata cache with disk state using incremental mtime checks.
    Only modified files are re-read and parsed.
    """
    cache = load_cache(cache_path)
    if fast_mode and cache:
        return cache

    cache_dirty = False
    valid_paths = set()

    for root, dirs, files in os.walk(vault_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in EXCLUDED_DIRS]
        for f in files:
            if f.endswith(".md") and f.lower() not in SYSTEM_FILES:
                abs_p = os.path.join(root, f)
                rel_p = os.path.relpath(abs_p, vault_dir).replace("\\", "/")
                valid_paths.add(rel_p)
                try:
                    mt = os.path.getmtime(abs_p)
                except OSError:
                    continue

                cached = cache.get(rel_p)
                if not cached or cached.get("mtime") != mt or "milestone" not in cached:
                    fm, tags, _, _ = parse_markdown_file(abs_p, parse_checkboxes=False)
                    deadline = str(fm.get("deadline") or fm.get("due") or "")
                    m_val = fm.get("milestone") or fm.get("milestones") or fm.get("jalon") or ""
                    milestone = ", ".join(m_val) if isinstance(m_val, list) else str(m_val)
                    cache[rel_p] = {
                        "mtime": mt,
                        "tags": list(tags),
                        "deadline": deadline,
                        "milestone": str(milestone)
                    }
                    cache_dirty = True

    # Purge deleted files from cache
    deleted = [k for k in cache if k not in valid_paths]
    if deleted:
        for k in deleted:
            cache.pop(k, None)
        cache_dirty = True

    if cache_dirty:
        save_cache(cache, cache_path)

    return cache


def find_project_file(vault_dir, project_path_or_name, data=None):
    """
    Resolves relative path or project title to absolute path in vault.
    """
    clean_target = project_path_or_name.strip().replace("\\", "/").lower()
    if clean_target.endswith(".md"):
        clean_target_no_ext = clean_target[:-3]
    else:
        clean_target_no_ext = clean_target

    candidate_abs = os.path.join(vault_dir, project_path_or_name.replace("/", os.sep))
    if not candidate_abs.endswith(".md") and os.path.exists(candidate_abs + ".md") and os.path.isfile(candidate_abs + ".md"):
        candidate_abs = candidate_abs + ".md"
        rel = os.path.relpath(candidate_abs, vault_dir).replace("\\", "/")
        return rel, candidate_abs

    if os.path.exists(candidate_abs) and os.path.isfile(candidate_abs):
        rel = os.path.relpath(candidate_abs, vault_dir).replace("\\", "/")
        return rel, candidate_abs

    if data:
        stats_projects = data.get("stats", {}).get("projects", {})
        candidates = []
        for rel_path in stats_projects.keys():
            rel_lower = rel_path.lower()
            title_lower = os.path.splitext(os.path.basename(rel_path))[0].lower()
            if rel_lower == clean_target or rel_lower == clean_target + ".md" or title_lower == clean_target_no_ext:
                abs_p = os.path.join(vault_dir, rel_path.replace("/", os.sep))
                if os.path.exists(abs_p):
                    return rel_path, abs_p
            if clean_target_no_ext in title_lower or clean_target_no_ext in rel_lower:
                abs_p = os.path.join(vault_dir, rel_path.replace("/", os.sep))
                if os.path.exists(abs_p):
                    candidates.append((rel_path, abs_p))
        if candidates:
            return candidates[0]

    # Search in cache (.project_cache.json)
    cache = load_cache()
    if cache:
        candidates = []
        for rel_path in cache.keys():
            rel_lower = rel_path.lower()
            title_lower = os.path.splitext(os.path.basename(rel_path))[0].lower()
            if rel_lower == clean_target or rel_lower == clean_target + ".md" or title_lower == clean_target_no_ext:
                abs_p = os.path.join(vault_dir, rel_path.replace("/", os.sep))
                if os.path.exists(abs_p):
                    return rel_path, abs_p
            if clean_target_no_ext in title_lower or clean_target_no_ext in rel_lower:
                abs_p = os.path.join(vault_dir, rel_path.replace("/", os.sep))
                if os.path.exists(abs_p):
                    candidates.append((rel_path, abs_p))
        if candidates:
            return candidates[0]

    # Search directly in notes/ folder
    for sub in ["notes", ""]:
        direct_p = os.path.join(vault_dir, sub, project_path_or_name if project_path_or_name.endswith(".md") else project_path_or_name + ".md")
        if os.path.exists(direct_p) and os.path.isfile(direct_p):
            rel = os.path.relpath(direct_p, vault_dir).replace("\\", "/")
            return rel, direct_p

    return project_path_or_name, candidate_abs


def scan_projects(vault_dir, data, cache=None, fast_mode=False, now_dt=None):
    """
    Reads active projects from data.json and unindexed project notes via fast cache.
    Calculates multi-scale temporal urgency (Deadline + Agile Milestone) and recency malus.
    """
    if cache is None:
        cache = sync_vault_cache(vault_dir, fast_mode=fast_mode)

    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    stats_projects = data.get("stats", {}).get("projects", {})
    settings = data.get("settings", {})

    raw_tags = settings.get("projectTags", "todo, project")
    project_tags = [t.strip().lstrip("#").lower() for t in raw_tags.split(",") if t.strip()]

    archive_tag = settings.get("archiveTag", "done").strip().lstrip("#").lower()
    done_tags = {"done", "projet-fini", archive_tag}
    deadline_prop = settings.get("deadlineProperty", "deadline").lower()
    milestone_prop = settings.get("milestoneProperty", "milestone").lower()

    rf = float(settings.get("rapprochementFactor") or settings.get("rapprochmentFactor") or 0.2)
    recency_weight = float(settings.get("recencyPenaltyWeight", 0.5))

    projects = []
    known_paths = set()

    # 1. Projects from data.json
    for rel_path, proj_stat in stats_projects.items():
        abs_path = os.path.join(vault_dir, rel_path.replace("/", os.sep))
        norm_rel = rel_path.replace("\\", "/")

        cached = cache.get(norm_rel)
        if cached and "milestone" in cached:
            tags = set(cached.get("tags", []))
            deadline_str = cached.get("deadline", "")
            milestone_str = cached.get("milestone", "")
        else:
            if not os.path.exists(abs_path):
                continue
            fm, tags_set, _, _ = parse_markdown_file(abs_path, parse_checkboxes=False)
            tags = tags_set
            deadline_str = str(fm.get(deadline_prop) or fm.get("deadline") or fm.get("due") or "")
            m_val = fm.get(milestone_prop) or fm.get("milestone") or fm.get("milestones") or fm.get("jalon") or ""
            milestone_str = ", ".join(m_val) if isinstance(m_val, list) else str(m_val)

        has_project_tag = any(pt in tags or any(t.startswith(pt + "/") for t in tags) for pt in project_tags)
        has_archive_tag = any(at in tags or any(t.startswith(at + "/") for t in tags) for at in done_tags)

        if not has_project_tag or has_archive_tag:
            continue

        total_reviews = int(proj_stat.get("totalReviews", 0))
        raw_score = proj_stat.get("currentScore")
        if total_reviews == 0 or raw_score is None:
            current_score = None
        else:
            current_score = float(raw_score)

        review_history = proj_stat.get("reviewHistory", [])
        last_action = review_history[-1].get("action") if review_history else ""

        # Skip finished projects
        if (current_score is not None and current_score == 0) or last_action == "finished":
            continue

        rotation_bonus = float(proj_stat.get("rotationBonus", 0.0))
        last_review_date = proj_stat.get("lastReviewDate", "")
        title = os.path.splitext(os.path.basename(rel_path))[0]

        # 1. Strategic Deadline Pressure: P_deadline = exp(-0.1 * dt)
        if not deadline_str:
            deadline_str = proj_stat.get("deadline", "")

        p_deadline = 0.0
        deadline_urgency = 0.0
        if deadline_str and current_score is not None:
            try:
                d_date = datetime.strptime(str(deadline_str)[:10], "%Y-%m-%d").date()
                today = now_dt.date() if isinstance(now_dt, datetime) else datetime.now().date()
                days_left = (d_date - today).days
                p_deadline = math.exp(-0.1 * days_left) if days_left > 0 else 1.0
            except Exception:
                pass

        # 2. Agile Milestone Pressure: P_milestone = exp(-0.3 * dt)
        if not milestone_str:
            milestone_str = proj_stat.get("milestone", "")

        last_sat_milestone = proj_stat.get("lastSatisfiedMilestoneDate") or proj_stat.get("last_satisfied_milestone_date")

        p_milestone = 0.0
        milestone_res = None
        if milestone_str and current_score is not None:
            milestone_res = parse_milestone_target(
                milestone_str,
                last_satisfied_str=last_sat_milestone,
                now_dt=now_dt.replace(tzinfo=None) if now_dt and now_dt.tzinfo else now_dt
            )
            if milestone_res and milestone_res.target_datetime:
                p_milestone = milestone_res.urgency_factor

        # 3. Non-Cumulative Temporal Pressure Envelope: P_eff = max(P_deadline, P_milestone)
        p_eff = max(p_deadline, p_milestone)

        # 4. Affine Convex Combination Priority Mapping: gap = 100 - (base + rot)
        rem = 0.0
        milestone_urgency = 0.0
        if current_score is not None:
            rem = max(0.0, 100.0 - (current_score + rotation_bonus))
            deadline_urgency = rem * p_deadline
            milestone_urgency = rem * p_milestone

        temporal_urgency = rem * p_eff
        pre_score = (current_score + rotation_bonus + temporal_urgency) if current_score is not None else None

        recent_work_dates = proj_stat.get("recentWorkDates", [])
        temporal_malus, k_factor, valid_dates = compute_temporal_recency_malus(
            recent_work_dates, pre_score, rf, recency_weight, now_dt=now_dt
        )

        effective_score = max(1.0, min(100.0, pre_score - temporal_malus)) if pre_score is not None else None

        known_paths.add(norm_rel)
        projects.append({
            "rel_path": norm_rel,
            "title": title,
            "base_score": current_score,
            "rotation_bonus": rotation_bonus,
            "deadline_urgency": deadline_urgency,
            "milestone_urgency": milestone_urgency,
            "p_deadline": round(p_deadline, 4),
            "p_milestone": round(p_milestone, 4),
            "p_eff": round(p_eff, 4),
            "temporal_urgency": temporal_urgency,
            "pre_score": pre_score,
            "temporal_malus": temporal_malus,
            "k_factor": k_factor,
            "active_sessions_count": len(valid_dates),
            "recent_work_dates": valid_dates,
            "effective_score": effective_score,
            "deadline": str(deadline_str) if deadline_str else "",
            "milestone": str(milestone_str) if milestone_str else "",
            "milestone_resolution": milestone_res.to_dict() if milestone_res else None,
            "milestone_target": milestone_res.target_datetime.isoformat() if (milestone_res and milestone_res.target_datetime) else None,
            "last_satisfied_milestone_date": last_sat_milestone or "",
            "total_reviews": total_reviews,
            "last_review_date": last_review_date,
            "review_history": review_history,
            "full_path": abs_path
        })

    # 2. Check unindexed active project notes from cache
    for rel_p, cached in cache.items():
        if rel_p in known_paths:
            continue
        tags = set(cached.get("tags", []))
        has_project_tag = any(pt in tags or any(t.startswith(pt + "/") for t in tags) for pt in project_tags)
        has_archive_tag = any(at in tags or any(t.startswith(at + "/") for t in tags) for at in done_tags)

        if has_project_tag and not has_archive_tag:
            abs_p = os.path.join(vault_dir, rel_p.replace("/", os.sep))
            title = os.path.splitext(os.path.basename(rel_p))[0]
            deadline_str = cached.get("deadline", "")
            milestone_str = cached.get("milestone", "")
            known_paths.add(rel_p)
            projects.append({
                "rel_path": rel_p,
                "title": title,
                "base_score": None,
                "rotation_bonus": 0.0,
                "deadline_urgency": 0.0,
                "milestone_urgency": 0.0,
                "p_deadline": 0.0,
                "p_milestone": 0.0,
                "p_eff": 0.0,
                "temporal_urgency": 0.0,
                "pre_score": None,
                "temporal_malus": 0.0,
                "k_factor": 0.0,
                "active_sessions_count": 0,
                "recent_work_dates": [],
                "effective_score": None,
                "deadline": str(deadline_str) if deadline_str else "",
                "milestone": str(milestone_str) if milestone_str else "",
                "milestone_resolution": None,
                "milestone_target": None,
                "last_satisfied_milestone_date": "",
                "total_reviews": 0,
                "last_review_date": "",
                "review_history": [],
                "full_path": abs_p
            })

    # Sort matching Obsidian plugin review modal priority:
    # 1. Unreviewed projects (totalReviews == 0) first (alphabetical by title)
    # 2. Reviewed projects (totalReviews > 0) by effective score descending
    # Secondary tie-breaker: base_score descending, then title alphabetical
    projects.sort(key=lambda p: (
        0 if p["total_reviews"] == 0 else 1,
        -p["effective_score"] if (p["total_reviews"] > 0 and p["effective_score"] is not None) else 0.0,
        -p["base_score"] if (p["total_reviews"] > 0 and p.get("base_score") is not None) else 0.0,
        p["title"].lower()
    ))
    return projects


def format_project_table(projects):
    lines = []
    header = f"{'Rank':<5} {'Title':<32} {'Eff.Score':<10} {'Base':<6} {'Rot.':<6} {'Dead.Urg':<9} {'Milest.Urg':<10} {'Malus(K)':<11} {'Deadline':<11} {'Milestone':<14} {'Reviews':<7}"
    lines.append(header)
    lines.append("-" * len(header))
    for idx, p in enumerate(projects, 1):
        title = p["title"]
        if len(title) > 30:
            title = title[:27] + "..."
        rev_str = "NEW" if p["total_reviews"] == 0 else str(p["total_reviews"])
        eff_str = f"{p['effective_score']:.2f}" if p['effective_score'] is not None else "N/A"
        base_str = f"{p['base_score']:.1f}" if p['base_score'] is not None else "N/A"
        rot_str = f"{p['rotation_bonus']:.1f}" if p['rotation_bonus'] is not None else "0.0"
        dead_urg_str = f"{p['deadline_urgency']:.2f}" if p.get('deadline_urgency') is not None else "0.00"
        mile_urg_str = f"{p['milestone_urgency']:.2f}" if p.get('milestone_urgency') is not None else "0.00"

        if p.get("temporal_malus") is not None and p.get("temporal_malus", 0.0) > 0:
            malus_str = f"-{p['temporal_malus']:.1f}({p.get('k_factor', 0.0):.1f})"
        else:
            malus_str = "0.0(0.0)"

        deadline_disp = p.get("deadline") or "N/A"
        if len(deadline_disp) > 10:
            deadline_disp = deadline_disp[:10]

        milestone_disp = p.get("milestone") or "N/A"
        if len(milestone_disp) > 13:
            milestone_disp = milestone_disp[:11] + ".."

        line = f"{idx:<5} {title:<32} {eff_str:<10} {base_str:<6} {rot_str:<6} {dead_urg_str:<9} {mile_urg_str:<10} {malus_str:<11} {deadline_disp:<11} {milestone_disp:<14} {rev_str:<7}"
        lines.append(line)
    return "\n".join(lines)


def clean_orphans(vault_dir=VAULT_DIR, data_path=DATA_JSON_PATH, cache_path=CACHE_PATH, dry_run=False):
    """
    Scans stats.projects in data.json and removes orphaned entries whose files no longer exist on disk.
    """
    data = load_data(data_path)
    stats_projects = data.get("stats", {}).get("projects", {})
    orphans = []

    for rel_path in list(stats_projects.keys()):
        abs_p = os.path.join(vault_dir, rel_path.replace("/", os.sep).replace("\\", os.sep))
        if not os.path.exists(abs_p) or not os.path.isfile(abs_p):
            orphans.append(rel_path)

    if orphans and not dry_run:
        backup_path = data_path + ".bak_clean_orphans"
        try:
            shutil.copy2(data_path, backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup file: {e}", file=sys.stderr)

        for orphan in orphans:
            stats_projects.pop(orphan, None)

        save_data(data, data_path)

        cache = load_cache(cache_path)
        cache_dirty = False
        for orphan in orphans:
            norm_rel = orphan.replace("\\", "/")
            if norm_rel in cache:
                cache.pop(norm_rel, None)
                cache_dirty = True
            if orphan in cache:
                cache.pop(orphan, None)
                cache_dirty = True

        if cache_dirty:
            save_cache(cache, cache_path)

    return orphans


def cmd_clean_orphans(args, data_path=DATA_JSON_PATH, cache_path=CACHE_PATH):
    dry_run = getattr(args, "dry_run", False)
    as_json = getattr(args, "json", False)

    orphans = clean_orphans(VAULT_DIR, data_path=data_path, cache_path=cache_path, dry_run=dry_run)

    if as_json:
        print(json.dumps({
            "dry_run": dry_run,
            "orphans_count": len(orphans),
            "orphans": orphans
        }, indent=2, ensure_ascii=False))
    else:
        mode_str = "[DRY-RUN] " if dry_run else ""
        if not orphans:
            print(f"✨ {mode_str}Aucune note orpheline détectée dans data.json. Tout est propre !")
        else:
            action_str = "détectée(s) (non supprimée(s))" if dry_run else "purgée(s) de data.json et du cache"
            print(f"🧹 {mode_str}{len(orphans)} note(s) orpheline(s) {action_str} :")
            for o in orphans:
                print(f"  - {o}")
            if not dry_run:
                print(f"💾 Backup de sécurité créé : {data_path}.bak_clean_orphans")


def cmd_list(args, data):
    if getattr(args, "clean_orphans", False):
        orphans = clean_orphans(VAULT_DIR, DATA_JSON_PATH, CACHE_PATH, dry_run=False)
        if orphans and not getattr(args, "json", False):
            print(f"🧹 Purge automatique : {len(orphans)} note(s) orpheline(s) nettoyée(s).")
        data = load_data(DATA_JSON_PATH)

    fast_mode = getattr(args, "fast", False)
    projects = scan_projects(VAULT_DIR, data, fast_mode=fast_mode)
    top_n = getattr(args, "top", None)
    if top_n is None and getattr(args, "n", None) is not None:
        top_n = args.n

    unreviewed = [p for p in projects if p["total_reviews"] == 0]
    reviewed = [p for p in projects if p["total_reviews"] > 0]

    show_unreviewed_only = getattr(args, "unreviewed", False) or getattr(args, "new", False)
    show_reviewed_only = getattr(args, "reviewed", False)

    if show_unreviewed_only:
        unreviewed_disp = unreviewed[:top_n] if top_n is not None and top_n > 0 else unreviewed
        reviewed_disp = []
    elif show_reviewed_only:
        unreviewed_disp = []
        reviewed_disp = reviewed[:top_n] if top_n is not None and top_n > 0 else reviewed
    else:
        unreviewed_disp = unreviewed[:top_n] if top_n is not None and top_n > 0 else unreviewed
        reviewed_disp = reviewed[:top_n] if top_n is not None and top_n > 0 else reviewed

    if getattr(args, "json", False):
        if show_unreviewed_only:
            out = [dict(p, full_path=None) for p in unreviewed_disp]
            for cp in out: cp.pop("full_path", None)
            print(json.dumps(out, indent=2, ensure_ascii=False))
        elif show_reviewed_only:
            out = [dict(p, full_path=None) for p in reviewed_disp]
            for cp in out: cp.pop("full_path", None)
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            unrev_out = [dict(p, full_path=None) for p in unreviewed_disp]
            for cp in unrev_out: cp.pop("full_path", None)
            rev_out = [dict(p, full_path=None) for p in reviewed_disp]
            for cp in rev_out: cp.pop("full_path", None)
            print(json.dumps({
                "unreviewed": unrev_out,
                "reviewed": rev_out,
                "total_unreviewed": len(unreviewed),
                "total_reviewed": len(reviewed)
            }, indent=2, ensure_ascii=False))
    else:
        if show_unreviewed_only:
            print(f"=== 🆕 Unreviewed Projects ({len(unreviewed)} projects awaiting initial evaluation) ===")
            print(format_project_table(unreviewed_disp) if unreviewed_disp else "  (No unreviewed projects)")
        elif show_reviewed_only:
            print(f"=== 🔥 Reviewed Active Projects ({len(reviewed)} projects sorted by urgency) ===")
            print(format_project_table(reviewed_disp) if reviewed_disp else "  (No reviewed active projects)")
        else:
            print(f"=== 🆕 Unreviewed Projects ({len(unreviewed)} awaiting initial evaluation, showing {len(unreviewed_disp)}) ===")
            print(format_project_table(unreviewed_disp) if unreviewed_disp else "  (No unreviewed projects)")
            print()
            print(f"=== 🔥 Top Urgent Reviewed Projects ({len(reviewed)} active projects, showing {len(reviewed_disp)}) ===")
            print(format_project_table(reviewed_disp) if reviewed_disp else "  (No reviewed projects)")


def cmd_get(args, data):
    target = args.project_path
    rel_path, abs_path = find_project_file(VAULT_DIR, target, data)

    if not os.path.exists(abs_path):
        if getattr(args, "json", False):
            print(json.dumps({"error": f"Project note not found for '{target}'"}))
        else:
            print(f"Error: Project note file not found for '{target}'.")
        sys.exit(1)

    fm, tags, checkboxes, content = parse_markdown_file(abs_path)
    stats = data.get("stats", {}).get("projects", {}).get(rel_path, {})
    settings = data.get("settings", {})
    deadline_prop = settings.get("deadlineProperty", "deadline").lower()
    milestone_prop = settings.get("milestoneProperty", "milestone").lower()

    total_reviews = int(stats.get("totalReviews", 0))
    raw_score = stats.get("currentScore")
    if total_reviews == 0 or raw_score is None:
        base_score = None
    else:
        base_score = float(raw_score)

    rotation_bonus = float(stats.get("rotationBonus", 0.0))
    deadline_val = fm.get(deadline_prop) or fm.get("deadline") or fm.get("due") or ""
    if not deadline_val:
        deadline_val = stats.get("deadline", "")

    p_deadline = 0.0
    deadline_urgency = 0.0
    if deadline_val and base_score is not None:
        try:
            d_date = datetime.strptime(str(deadline_val)[:10], "%Y-%m-%d").date()
            today = datetime.now().date()
            days_left = (d_date - today).days
            p_deadline = math.exp(-0.1 * days_left) if days_left > 0 else 1.0
        except Exception:
            pass

    m_val = fm.get(milestone_prop) or fm.get("milestone") or fm.get("milestones") or fm.get("jalon") or ""
    milestone_val = ", ".join(m_val) if isinstance(m_val, list) else str(m_val)
    if not milestone_val:
        milestone_val = stats.get("milestone", "")

    last_sat_milestone = stats.get("lastSatisfiedMilestoneDate") or stats.get("last_satisfied_milestone_date")

    p_milestone = 0.0
    milestone_res = None
    if milestone_val and base_score is not None:
        milestone_res = parse_milestone_target(milestone_val, last_satisfied_str=last_sat_milestone)
        if milestone_res and milestone_res.target_datetime:
            p_milestone = milestone_res.urgency_factor

    p_eff = max(p_deadline, p_milestone)

    rem = 0.0
    milestone_urgency = 0.0
    if base_score is not None:
        rem = max(0.0, 100.0 - (base_score + rotation_bonus))
        deadline_urgency = rem * p_deadline
        milestone_urgency = rem * p_milestone

    temporal_urgency = rem * p_eff
    pre_score = (base_score + rotation_bonus + temporal_urgency) if base_score is not None else None

    recent_work_dates = stats.get("recentWorkDates", [])
    rf = float(settings.get("rapprochementFactor") or settings.get("rapprochmentFactor") or 0.2)
    recency_weight = float(settings.get("recencyPenaltyWeight", 0.5))

    temporal_malus, k_factor, valid_dates = compute_temporal_recency_malus(
        recent_work_dates, pre_score, rf, recency_weight
    )
    effective_score = max(1.0, min(100.0, pre_score - temporal_malus)) if pre_score is not None else None

    proj_info = {
        "rel_path": rel_path,
        "title": os.path.splitext(os.path.basename(rel_path))[0],
        "base_score": base_score,
        "rotation_bonus": rotation_bonus,
        "deadline_urgency": deadline_urgency,
        "milestone_urgency": milestone_urgency,
        "p_deadline": round(p_deadline, 4),
        "p_milestone": round(p_milestone, 4),
        "p_eff": round(p_eff, 4),
        "temporal_urgency": temporal_urgency,
        "pre_score": pre_score,
        "temporal_malus": temporal_malus,
        "k_factor": k_factor,
        "active_sessions_count": len(valid_dates),
        "recent_work_dates": valid_dates,
        "effective_score": effective_score,
        "deadline": str(deadline_val),
        "milestone": str(milestone_val),
        "milestone_resolution": milestone_res.to_dict() if milestone_res else None,
        "last_satisfied_milestone_date": last_sat_milestone or "",
        "total_reviews": total_reviews,
        "last_review_date": stats.get("lastReviewDate", ""),
        "review_history": stats.get("reviewHistory", []),
        "checkboxes": checkboxes,
        "frontmatter": fm,
        "tags": list(tags)
    }

    if getattr(args, "json", False):
        clean_p = dict(proj_info)
        clean_p.pop("full_path", None)
        print(json.dumps(clean_p, indent=2, ensure_ascii=False))
    else:
        print(f"=== Project Details: {proj_info['title']} ===")
        print(f"Path:                     {proj_info['rel_path']}")
        eff_str = f"{proj_info['effective_score']:.2f}" if proj_info['effective_score'] is not None else "N/A"
        base_str = f"{proj_info['base_score']:.1f}" if proj_info['base_score'] is not None else "N/A"
        pre_str = f"{proj_info['pre_score']:.2f}" if proj_info['pre_score'] is not None else "N/A"
        print(f"Effective Score:          {eff_str}")
        print(f"Base Score:               {base_str}")
        print(f"Rotation Bonus:           {proj_info['rotation_bonus']:.1f}")
        print(f"Deadline Urgency:         {proj_info['deadline_urgency']:.2f} (P_dead={proj_info.get('p_deadline', 0.0):.3f})")
        print(f"Milestone Urgency:        {proj_info['milestone_urgency']:.2f} (P_mile={proj_info.get('p_milestone', 0.0):.3f})")
        print(f"Temporal Pressure P_eff:  {proj_info.get('p_eff', 0.0):.3f} (max(P_dead, P_mile))")
        print(f"Pre-Score (avant malus):  {pre_str}")
        malus_str = f"-{proj_info['temporal_malus']:.2f} (K={proj_info['k_factor']:.2f}, {proj_info['active_sessions_count']} session(s) < 6h)"
        print(f"Temporal Recency Malus:   {malus_str}")
        print(f"Deadline:                 {proj_info['deadline'] or 'N/A'}")

        mile_disp = proj_info.get('milestone') or 'N/A'
        if milestone_res and milestone_res.target_datetime:
            sat_str = " [Cycle Satisfied]" if milestone_res.is_cycle_satisfied else ""
            mile_disp = f"{mile_disp} (next: {milestone_res.target_datetime.strftime('%Y-%m-%d %H:%M')}, {milestone_res.days_remaining:.1f}d remaining, P={milestone_res.urgency_factor:.3f}{sat_str})"
        print(f"Milestone:                {mile_disp}")
        print(f"Total Reviews:            {proj_info['total_reviews']}")
        print(f"Last Review Date:         {proj_info['last_review_date'] or 'N/A'}")
        if last_sat_milestone:
            print(f"Last Satisfied Milestone: {last_sat_milestone}")
        if proj_info['recent_work_dates']:
            disp_dates = []
            for d in proj_info['recent_work_dates']:
                if isinstance(d, dict):
                    ratio = float(d.get('ratio', d.get('weight', 1.0)))
                    dur = float(d.get('duration_minutes', 0.0))
                    intr = " (interrompu)" if d.get('interrupted') else ""
                    disp_dates.append(f"{d.get('date', 'N/A')} [r={ratio:.2f}, {dur:.1f}m{intr}]")
                else:
                    disp_dates.append(str(d))
            print(f"Recent Sessions (<6h):    {', '.join(disp_dates)}")

        print("\n--- Review History ---")
        history = proj_info.get("review_history", [])
        if not history:
            print("No review history recorded yet.")
        else:
            for entry in history[-5:]:
                print(f"  [{entry.get('date', 'N/A')}] Action: {entry.get('action', 'N/A'):<12} Score After: {entry.get('scoreAfter', 0):.2f}")

        print("\n--- Roadmap Tasks ---")
        checkboxes = proj_info.get("checkboxes", [])
        pending = [c for c in checkboxes if not c["completed"]]
        completed = [c for c in checkboxes if c["completed"]]

        print(f"Pending Tasks ({len(pending)}):")
        if not pending:
            print("  (None)")
        else:
            for c in pending:
                print(f"  [ ] {c['text']} (line {c['line']})")

        print(f"Completed Tasks ({len(completed)}):")
        if not completed:
            print("  (None)")
        else:
            for c in completed:
                print(f"  [x] {c['text']} (line {c['line']})")


def update_note_frontmatter_archived(abs_path, settings):
    raw_tags = settings.get("projectTags", "todo, project")
    project_tags = [t.strip().lstrip("#").lower() for t in raw_tags.split(",") if t.strip()]
    archive_tag = settings.get("archiveTag", "done").strip().lstrip("#").lower()

    if not os.path.exists(abs_path):
        return

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        fm_raw = parts[1] if len(parts) >= 2 else ""
        body = parts[2] if len(parts) >= 3 else ""

        fm_lines = fm_raw.splitlines()
        new_fm_lines = []
        existing_tags = []
        in_tags_list = False

        for line in fm_lines:
            s = line.strip()
            if not s:
                continue
            if s.startswith("tags:"):
                v = s[5:].strip()
                if v.startswith("[") and v.endswith("]"):
                    items = [i.strip().strip('"\'').lstrip("#") for i in v[1:-1].split(",") if i.strip()]
                    existing_tags.extend(items)
                    in_tags_list = False
                elif v:
                    val_clean = v.strip('"\'').lstrip("#")
                    existing_tags.append(val_clean)
                    in_tags_list = False
                else:
                    in_tags_list = True
            elif in_tags_list:
                if s.startswith("- "):
                    t_val = s[2:].strip().strip('"\'').lstrip("#")
                    if t_val:
                        existing_tags.append(t_val)
                elif ":" in s:
                    in_tags_list = False
                    new_fm_lines.append(line)
            else:
                new_fm_lines.append(line)

        final_tags = []
        for t in existing_tags:
            if t.lower() not in project_tags and t.lower() not in [ft.lower() for ft in final_tags]:
                final_tags.append(t)
        if archive_tag not in [ft.lower() for ft in final_tags]:
            final_tags.append(archive_tag)

        tags_line = f"tags: [{', '.join(final_tags)}]"
        new_fm_lines.insert(0, tags_line)

        body_prefix = "" if body.startswith("\n") else "\n"
        new_content = "---\n" + "\n".join(new_fm_lines) + "\n---" + body_prefix + body
    else:
        new_fm = f"---\ntags: [{archive_tag}]\n---\n\n"
        new_content = new_fm + content

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated note frontmatter tags for '{abs_path}' (archived with tag '{archive_tag}').")


def strip_project_tags(abs_path, settings):
    raw_tags = settings.get("projectTags", "todo, project")
    project_tags = [t.strip().lstrip("#").lower() for t in raw_tags.split(",") if t.strip()]

    if not os.path.exists(abs_path):
        return

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        fm_raw = parts[1] if len(parts) >= 2 else ""
        body = parts[2] if len(parts) >= 3 else ""

        fm_lines = fm_raw.splitlines()
        new_fm_lines = []
        existing_tags = []
        in_tags_list = False

        for line in fm_lines:
            s = line.strip()
            if not s:
                continue
            if s.startswith("tags:"):
                v = s[5:].strip()
                if v.startswith("[") and v.endswith("]"):
                    items = [i.strip().strip('"\'').lstrip("#") for i in v[1:-1].split(",") if i.strip()]
                    existing_tags.extend(items)
                    in_tags_list = False
                elif v:
                    val_clean = v.strip('"\'').lstrip("#")
                    existing_tags.append(val_clean)
                    in_tags_list = False
                else:
                    in_tags_list = True
            elif in_tags_list:
                if s.startswith("- "):
                    t_val = s[2:].strip().strip('"\'').lstrip("#")
                    if t_val:
                        existing_tags.append(t_val)
                elif ":" in s:
                    in_tags_list = False
                    new_fm_lines.append(line)
            else:
                new_fm_lines.append(line)

        final_tags = [t for t in existing_tags if t.lower() not in project_tags]
        if final_tags:
            tags_line = f"tags: [{', '.join(final_tags)}]"
            new_fm_lines.insert(0, tags_line)

        # Also strip inline project tags from body
        for pt in project_tags:
            body = re.sub(rf'(?i)(^|\s)#{re.escape(pt)}\b', r'\1', body)

        body_prefix = "" if body.startswith("\n") else "\n"
        new_content = "---\n" + "\n".join(new_fm_lines) + "\n---" + body_prefix + body
    else:
        new_content = content
        for pt in project_tags:
            new_content = re.sub(rf'(?i)(^|\s)#{re.escape(pt)}\b', r'\1', new_content)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated note frontmatter for '{abs_path}' (stripped project tags, marked as non-projet).")


def normalize_action(action_str):
    """
    Cleans and normalizes action string:
    - Strips whitespace and parenthesized/bracketed suffixes like '(Recommandé)', '[Recommandé]', '(recommended)'
    - Handles case-insensitivity and accents
    - Maps French and English aliases to canonical action names:
      'less-often', 'ok', 'more-often', 'emergency', 'finished', 'non-projet'
    """
    if not action_str:
        return ""
    # Strip parenthetical/bracketed annotations e.g. (Recommandé), [Recommandé], (Recommended)
    cleaned = re.sub(r'[\(\[\{].*?[\)\]\}]', '', str(action_str)).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned_lower = cleaned.lower()

    aliases = {
        "ok": "ok",
        "a l'aise": "less-often",
        "à l'aise": "less-often",
        "al'aise": "less-often",
        "alaise": "less-often",
        "a l aise": "less-often",
        "aise": "less-often",
        "à l'aise (recommandé)": "less-often",
        "less-often": "less-often",
        "less often": "less-often",
        "less_often": "less-often",
        "moins souvent": "less-often",
        "moins-souvent": "less-often",
        "moins_souvent": "less-often",
        "stress": "more-often",
        "stresse": "more-often",
        "stressé": "more-often",
        "stressee": "more-often",
        "more-often": "more-often",
        "more often": "more-often",
        "more_often": "more-often",
        "plus souvent": "more-often",
        "plus-souvent": "more-often",
        "plus_souvent": "more-often",
        "emergency": "emergency",
        "urgence": "emergency",
        "urgent": "emergency",
        "finished": "finished",
        "termine": "finished",
        "terminé": "finished",
        "done": "finished",
        "fini": "finished",
        "non-projet": "non-projet",
        "non projet": "non-projet",
        "non_projet": "non-projet",
        "non-project": "non-projet",
        "not-a-project": "non-projet",
        "pas un projet": "non-projet",
    }
    return aliases.get(cleaned_lower, cleaned_lower)


def compute_feedback_score(current_score, action, rf):
    act = normalize_action(action)
    try:
        new_score = float(act)
    except ValueError:
        if act in ("finished", "non-projet", "non_projet", "non-project", "not-a-project"):
            return 0.0
        baseline = current_score if current_score is not None else 50.0
        if act == "less-often":
            new_score = baseline - rf * (baseline - 1.0)
        elif act == "ok":
            new_score = baseline
        elif act in ("more-often", "emergency"):
            new_score = baseline + rf * (100.0 - baseline)
        else:
            raise ValueError(f"Unknown action '{action}'. Options: ok, less-often, more-often, finished, emergency, non-projet, or numeric score (1-100).")

    if act not in ("finished", "non-projet", "non_projet", "non-project", "not-a-project"):
        new_score = max(1.0, min(100.0, new_score))

    return round(new_score, 3)


def apply_feedback(project_path, action, worked, data):
    stats = data.setdefault("stats", {}).setdefault("projects", {})
    global_stats = data.setdefault("stats", {}).setdefault("globalStats", {"totalReviews": 0, "totalPomodoroTime": 0})
    settings = data.setdefault("settings", {})

    rel_path, abs_path = find_project_file(VAULT_DIR, project_path, data)

    matched_key = None
    for k in stats.keys():
        if k == rel_path or os.path.basename(k) == os.path.basename(rel_path) or k.endswith(rel_path):
            matched_key = k
            break
    if not matched_key:
        matched_key = rel_path

    if matched_key not in stats:
        proj = {
            "rotationBonus": 0.0,
            "totalReviews": 0,
            "lastReviewDate": "",
            "reviewHistory": [],
            "recentWorkDates": []
        }
        stats[matched_key] = proj
    else:
        proj = stats[matched_key]

    total_reviews = int(proj.get("totalReviews", 0))
    raw_score = proj.get("currentScore")
    current_score = float(raw_score) if (total_reviews > 0 and raw_score is not None) else None

    rf = float(settings.get("rapprochementFactor") or settings.get("rapprochmentFactor") or 0.2)
    act = normalize_action(action)

    new_score = compute_feedback_score(current_score, action, rf)
    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()

    proj["currentScore"] = new_score
    proj["lastReviewDate"] = now_iso
    proj.setdefault("reviewHistory", []).append({
        "date": now_iso,
        "action": act,
        "scoreAfter": new_score
    })
    if len(proj.get("reviewHistory", [])) > 100:
        proj["reviewHistory"] = proj["reviewHistory"][-100:]

    rot_inc = float(settings.get("rotationBonus", 0.3))

    # Always increment totalReviews and globalStats totalReviews on review/feedback
    proj["totalReviews"] = total_reviews + 1
    global_stats["totalReviews"] = global_stats.get("totalReviews", 0) + 1

    if worked:
        # Update recentWorkDates: purge older than 6h and push current session
        existing_work = proj.get("recentWorkDates", [])
        valid_dates = []
        for d_str in existing_work:
            d_dt = parse_iso_datetime(d_str)
            if d_dt:
                delta_h = (now_dt - d_dt).total_seconds() / 3600.0
                if -0.05 <= delta_h < 6.0:
                    valid_dates.append(d_str)
        valid_dates.append(now_iso)
        proj["recentWorkDates"] = valid_dates

        # Set lastSatisfiedMilestoneDate to mark milestone cycle as satisfied
        proj["lastSatisfiedMilestoneDate"] = now_iso

        # Reset rotationBonus for current project, increment all other projects
        proj["rotationBonus"] = 0.0
        for p_key, p_val in stats.items():
            if p_key != matched_key:
                p_val["rotationBonus"] = round(float(p_val.get("rotationBonus", 0.0)) + rot_inc, 3)
    else:
        # Metacognitive review only: keep recentWorkDates and lastSatisfiedMilestoneDate intact,
        # do NOT modify rotationBonus for current or other projects.
        pass

    data_path = os.path.join(VAULT_DIR, ".obsidian", "plugins", "project-memory", "data.json")
    cache_path = os.path.join(VAULT_DIR, ".obsidian", "plugins", "project-memory", ".project_cache.json")
    cache = load_cache(cache_path)
    cache_dirty = False
    norm_rel = rel_path.replace("\\", "/")

    if act == "finished":
        update_note_frontmatter_archived(abs_path, settings)
        stats.pop(matched_key, None)
        if norm_rel in cache:
            cache.pop(norm_rel, None)
            cache_dirty = True
        if matched_key in cache:
            cache.pop(matched_key, None)
            cache_dirty = True

        save_data(data, data_path)
        if cache_dirty:
            save_cache(cache, cache_path)

        print(f"Feedback saved for '{matched_key}': action='finished', project purged from data.json")
        return matched_key, 0.0

    if act in ("non-projet", "non_projet", "non-project", "not-a-project"):
        strip_project_tags(abs_path, settings)
        stats.pop(matched_key, None)
        if norm_rel in cache:
            cache.pop(norm_rel, None)
            cache_dirty = True
        if matched_key in cache:
            cache.pop(matched_key, None)
            cache_dirty = True

        save_data(data, data_path)
        if cache_dirty:
            save_cache(cache, cache_path)

        print(f"Feedback saved for '{matched_key}': action='non-projet', project stripped of tags and purged from active projects.")
        return matched_key, 0.0

    save_data(data, data_path)
    mode_str = "work session" if worked else "review only"
    print(f"Feedback ({mode_str}) saved for '{matched_key}': action='{act}', new_score={new_score:.2f}")

    return matched_key, new_score


def cmd_feedback(args, data):
    action = getattr(args, "action", None) or getattr(args, "pos_action", None)
    if not action:
        print("Error: Action is required. Use --action <action> or pass action as positional argument.")
        print("Options: ok, less-often, more-often, finished, emergency, non-projet, or numeric score (1-100)")
        sys.exit(1)

    # Feedback represents a work session by default (worked=True), recording recentWorkDates and recency penalty.
    # To perform a review-only update without recording work, use --no-work / --review-only.
    worked = not bool(
        getattr(args, "no_work", False) or getattr(args, "review_only", False) or getattr(args, "not_worked", False)
    )
    apply_feedback(args.project_path, action, worked, data)


def cmd_set_score(args, data):
    worked = bool(getattr(args, "worked", False))
    apply_feedback(args.project_path, str(args.score), worked, data)


def cmd_complete_task(args, data):
    target = args.project_path
    task_text = args.task_text.strip()

    rel_path, abs_path = find_project_file(VAULT_DIR, target, data)

    if not os.path.exists(abs_path):
        print(f"Error: Project note file not found for '{target}'.")
        sys.exit(1)

    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    found = False
    new_lines = []

    for line in lines:
        if not found and re.match(r'^\s*[-*+]\s+\[ \]\s+', line):
            if task_text.lower() in line.lower():
                line = re.sub(r'(\s*[-*+]\s+)\[ \]', r'\1[x]', line, count=1)
                found = True
                print(f"Checked task in '{rel_path}': {line.strip()}")
        new_lines.append(line)

    if not found:
        print(f"Warning: Pending task matching '{task_text}' not found in '{rel_path}'.")
        print("Available pending tasks:")
        _, _, checkboxes, _ = parse_markdown_file(abs_path)
        pending = [c for c in checkboxes if not c["completed"]]
        if not pending:
            print("  (No pending tasks found in file)")
        else:
            for p in pending:
                print(f"  - [ ] {p['text']}")
        sys.exit(1)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

    apply_feedback(target, "ok", worked=True, data=data)


def cmd_work(args, data):
    """
    Démarre une session Pomodoro active sur un projet.

    Comportement officiel et nominal :
    La durée de travail est pilotée par la configuration globale d'Obsidian lue
    directement dans data.json (settings.pomodoroDuration, nominal : 60 min).
    Il s'agit du comportement par défaut officiel et nominal (et non d'un simple fallback).
    L'argument --duration (-d) constitue un override optionnel et exceptionnel.
    """
    rel_path, abs_path = find_project_file(VAULT_DIR, args.project_path, data)
    if not os.path.exists(abs_path):
        print(f"Error: Project note file not found for '{args.project_path}'.", flush=True)
        sys.exit(1)

    # Vérifie si un Pomodoro est déjà actif
    active = load_active_pomodoro()
    if active and active.get("status") == "running":
        active_pid = active.get("pid")
        if is_pid_alive(active_pid) and active_pid != os.getpid():
            active_title = active.get("title", active.get("rel_path", "Inconnu"))
            print(f"⚠️ Une session Pomodoro est déjà en cours d'exécution pour '{active_title}' (PID {active_pid}).", flush=True)
            print("💡 Vous pouvez l'interrompre proprement via : `python antigravity/scripts/project_memory_cli.py stop-work`", flush=True)
            sys.exit(1)
        else:
            # Nettoyage d'un lock orphelin
            clear_active_pomodoro()

    # Comportement officiel et nominal : durée par défaut issue de settings.pomodoroDuration (data.json).
    # L'argument --duration est un override optionnel exceptionnel.
    duration_min = float(args.duration) if args.duration is not None else float(data.get("settings", {}).get("pomodoroDuration", 60))
    total_seconds = int(duration_min * 60)
    title = os.path.splitext(os.path.basename(rel_path))[0]
    now_dt = datetime.now(timezone.utc)
    start_time = time.time()

    pomodoro_state = {
        "pid": os.getpid(),
        "rel_path": rel_path,
        "title": title,
        "start_iso": now_dt.isoformat(),
        "start_timestamp": start_time,
        "target_duration_minutes": duration_min,
        "target_duration_seconds": total_seconds,
        "status": "running"
    }
    save_active_pomodoro(pomodoro_state)

    interrupted = False
    stop_reason = "normal"

    def signal_handler(signum, frame):
        nonlocal interrupted, stop_reason
        interrupted = True
        stop_reason = "signal"

    original_sigint = None
    original_sigterm = None
    try:
        import signal
        original_sigint = signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, "SIGTERM"):
            original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass

    print(f"⏱️ Session Pomodoro démarrée pour '{title}' ({duration_min:.0f} min)...", flush=True)
    step_sec = 30

    try:
        for elapsed_sec in range(0, total_seconds + 1, step_sec):
            if interrupted:
                break

            # Vérifie si le fichier actif a été modifié par stop-work
            active_cur = load_active_pomodoro()
            if not active_cur or active_cur.get("status") != "running":
                interrupted = True
                stop_reason = "external_command"
                break

            remaining_sec = max(0, total_seconds - elapsed_sec)
            remaining_min = math.ceil(remaining_sec / 60)
            pct = int((elapsed_sec / total_seconds) * 100) if total_seconds > 0 else 100
            bar_len = 15
            filled = int(bar_len * elapsed_sec / total_seconds) if total_seconds > 0 else bar_len
            bar = "█" * filled + "░" * (bar_len - filled)
            m_rem = remaining_sec // 60
            s_rem = remaining_sec % 60
            print(f"⏳ [{bar}] {pct:3d}% | Temps restant : {m_rem:02d}:{s_rem:02d} ({remaining_min} min)", flush=True)

            if remaining_sec > 0:
                sleep_target = min(step_sec, remaining_sec)
                sleep_end = time.time() + sleep_target
                while time.time() < sleep_end and not interrupted:
                    active_cur = load_active_pomodoro()
                    if not active_cur or active_cur.get("status") != "running":
                        interrupted = True
                        stop_reason = "external_command"
                        break
                    time.sleep(min(0.5, max(0.05, sleep_end - time.time())))

    except (KeyboardInterrupt, SystemExit):
        interrupted = True
        stop_reason = "keyboard_interrupt"
    finally:
        # Restauration des signaux
        try:
            import signal
            if original_sigint is not None:
                signal.signal(signal.SIGINT, original_sigint)
            if original_sigterm is not None and hasattr(signal, "SIGTERM"):
                signal.signal(signal.SIGTERM, original_sigterm)
        except Exception:
            pass

    actual_elapsed_sec = max(0.0, time.time() - start_time)
    actual_elapsed_min = actual_elapsed_sec / 60.0

    clear_active_pomodoro()
    data = load_data(DATA_JSON_PATH)

    if interrupted:
        effective_elapsed_min = min(float(duration_min), actual_elapsed_min)
        ratio = min(1.0, max(0.0, effective_elapsed_min / duration_min)) if duration_min > 0 else 0.0

        matched_key, _ = record_work_session(
            data,
            rel_path,
            elapsed_minutes=effective_elapsed_min,
            target_minutes=duration_min,
            is_interrupted=True,
            data_path=DATA_JSON_PATH
        )

        m_el = int(effective_elapsed_min)
        s_el = int((effective_elapsed_min - m_el) * 60)

        updated_projects = scan_projects(VAULT_DIR, data)
        target_p = next((p for p in updated_projects if p["rel_path"] == rel_path or p["title"] == title), None)

        print(flush=True)
        print("============================================================", flush=True)
        print(f"🛑 POMODORO INTERROMPU pour '{title}'", flush=True)
        print("============================================================", flush=True)
        print(f"⏱️ Temps réellement écoulé : {m_el:02d}:{s_el:02d} ({effective_elapsed_min:.2f} min / {duration_min:.0f} min)", flush=True)
        print(f"📊 Ratio d'accomplissement (r) : {ratio * 100:.1f}%", flush=True)
        print(f"📈 Total Pomodoro global : {data.get('stats', {}).get('globalStats', {}).get('totalPomodoroTime', 0):.2f} min (+{effective_elapsed_min:.2f} min)", flush=True)
        if target_p:
            eff_disp = f"{target_p['effective_score']:.2f}" if target_p['effective_score'] is not None else "N/A"
            malus_disp = f"-{target_p['temporal_malus']:.2f} (K={target_p['k_factor']:.2f})" if target_p.get('temporal_malus') else "0.00"
            print(f"🎯 Score effectif mis à jour : {eff_disp} [Malus temporel proportionnel : {malus_disp}]", flush=True)
        print("============================================================", flush=True)
        print(flush=True)
        print("🤖 CONSIGNES ANTIGRAVITY POST-INTERRUPTION :", flush=True)
        print(f"1. 📝 Bilan intermédiaire : Faire le point sur ce qui a été accompli durant ces {effective_elapsed_min:.1f} minutes de travail sur '{title}'.", flush=True)
        print(f"2. 💬 Feedback optionnel : Si la session était significative, sonder Henri via `ask_question` pour ajuster le score via `feedback`.", flush=True)
        return

    # Fin normale
    matched_key, _ = record_work_session(
        data,
        rel_path,
        elapsed_minutes=float(duration_min),
        target_minutes=duration_min,
        is_interrupted=False,
        data_path=DATA_JSON_PATH
    )

    all_projects = scan_projects(VAULT_DIR, data)
    other_projects = [
        p for p in all_projects
        if p["rel_path"] != rel_path and p["full_path"] != abs_path and p["title"] != title
    ]
    other_projects.sort(key=lambda p: (
        -p["effective_score"] if p.get("effective_score") is not None else 0.0,
        -p["base_score"] if (p.get("base_score") is not None) else 0.0,
        p["title"].lower()
    ))
    top3 = other_projects[:3]

    print("============================================================", flush=True)
    print(f"🎉 POMODORO TERMINÉ pour '{title}' ({duration_min:.0f} min)", flush=True)
    print("============================================================", flush=True)
    print(flush=True)
    print("🤖 CONSIGNES ANTIGRAVITY POST-POMODORO (Handover Agent) :", flush=True)
    print(f"1. ☕ Pause & Récupération : Informer Henri que la session sur '{title}' est terminée et l'encourager explicitement à prendre une vraie pause de 5 minutes (s'étirer, s'hydrater, quitter l'écran).", flush=True)
    print("2. 📊 Évaluation Objective & Réaliste (Anti-biais d'optimisme & Anti-nihilisme optimiste) :", flush=True)
    print(f"   - Évaluer objectivement le travail accompli et la trajectoire restante pour '{title}'.", flush=True)
    print("   - Mesurer si le rythme actuel garantit de respecter l'échéance/jalon avec une marge de sécurité (sans optimisme béat ni fatalisme).", flush=True)
    print("   - Déterminer la recommandation de score/rythme la plus juste parmi : [\"À l'aise\", \"OK\", \"Stressé\", \"Terminé\"].", flush=True)
    print("3. 💬 Évaluation Interactive via ask_question (Stress & Confort) :", flush=True)
    print("   - Déclencher l'outil interactif ask_question pour sonder le ressenti d'Henri (niveau de confort, charge mentale, blocages éventuels).", flush=True)
    print("   - Présenter les 4 options dans l'ordre canonique : [\"À l'aise\", \"OK\", \"Stressé\", \"Terminé\"], en apposant le suffixe '(Recommandé)' à l'option préconisée (ex: 'OK (Recommandé)').", flush=True)
    print("   - Enregistrer ensuite le choix final en exécutant : `python antigravity/scripts/project_memory_cli.py feedback <projet> --action <action>`.", flush=True)
    print("4. 🎯 Suggestion des 3 Prochains Projets :", flush=True)
    print("   - Présenter à Henri les 3 projets suivants recommandés selon l'algorithme d'urgence dynamique :", flush=True)
    if not top3:
        print("     (Aucun autre projet actif détecté dans le vault)", flush=True)
    else:
        for idx, p in enumerate(top3, 1):
            deadline_info = f" | 📅 Deadline: {p['deadline']}" if p.get("deadline") else ""
            milestone_info = f" | 🚩 Milestone: {p['milestone']}" if p.get("milestone") else ""
            eff_info = f"{p['effective_score']:.2f}" if p.get("effective_score") is not None else "N/A"
            malus_info = f" (Malus -{p['temporal_malus']:.1f})" if p.get("temporal_malus", 0) > 0 else ""
            print(f"     {idx}. {p['title']} [Score: {eff_info}{malus_info}{deadline_info}{milestone_info}]", flush=True)
    print("   - Proposer d'enchaîner directement sur l'un d'eux après sa pause.", flush=True)


def cmd_stop_work(args, data):
    active = load_active_pomodoro()
    as_json = getattr(args, "json", False)
    target_project = getattr(args, "project_path", None)
    manual_elapsed = getattr(args, "elapsed", None)

    if not active or active.get("status") != "running":
        if target_project and manual_elapsed is not None:
            # Enregistrement manuel d'une session sans daemon actif
            rel_path, abs_path = find_project_file(VAULT_DIR, target_project, data)
            title = os.path.splitext(os.path.basename(rel_path))[0]
            # Comportement officiel et nominal : durée cible par défaut issue de settings.pomodoroDuration (data.json)
            # L'argument --target-duration est un override exceptionnel.
            target_min = float(args.target_duration) if getattr(args, "target_duration", None) else float(data.get("settings", {}).get("pomodoroDuration", 60))
            elapsed_min = float(manual_elapsed)
            ratio = min(1.0, max(0.0, elapsed_min / target_min)) if target_min > 0 else 0.0

            matched_key, _ = record_work_session(
                data,
                rel_path,
                elapsed_minutes=elapsed_min,
                target_minutes=target_min,
                is_interrupted=True,
                data_path=DATA_JSON_PATH
            )
            if as_json:
                print(json.dumps({
                    "status": "stopped",
                    "manual": True,
                    "project": title,
                    "rel_path": rel_path,
                    "elapsed_minutes": elapsed_min,
                    "target_minutes": target_min,
                    "ratio": ratio
                }, indent=2, ensure_ascii=False))
            else:
                print(f"🛑 Session de travail manuelle enregistrée pour '{title}' ({elapsed_min:.2f} min / {target_min:.0f} min, ratio r={ratio:.2%}).")
            return

        if as_json:
            print(json.dumps({"status": "no_active_pomodoro", "message": "Aucune session Pomodoro active en cours."}, indent=2, ensure_ascii=False))
        else:
            print("ℹ️ Aucune session Pomodoro active n'est actuellement en cours d'exécution.")
        return

    # Session active détectée
    rel_path = active.get("rel_path")
    title = active.get("title", os.path.splitext(os.path.basename(rel_path))[0])
    start_ts = float(active.get("start_timestamp", time.time()))
    target_min = float(active.get("target_duration_minutes", 25))
    pid = active.get("pid")

    now_t = time.time()
    elapsed_sec = max(0.0, now_t - start_ts)
    elapsed_min = float(manual_elapsed) if manual_elapsed is not None else (elapsed_sec / 60.0)
    effective_elapsed_min = min(target_min, elapsed_min)
    ratio = min(1.0, max(0.0, effective_elapsed_min / target_min)) if target_min > 0 else 0.0

    # Marque la session comme stopped pour que la boucle work se termine
    active["status"] = "stopped"
    save_active_pomodoro(active)

    # Notifie / termine le processus daemon si distinct
    if pid and is_pid_alive(pid) and pid != os.getpid():
        try:
            import signal
            if sys.platform == "win32":
                os.kill(int(pid), signal.SIGTERM)
            else:
                os.kill(int(pid), signal.SIGINT)
        except Exception:
            pass

    # Enregistrement direct de la session
    matched_key, _ = record_work_session(
        data,
        rel_path,
        elapsed_minutes=effective_elapsed_min,
        target_minutes=target_min,
        is_interrupted=True,
        data_path=DATA_JSON_PATH
    )

    clear_active_pomodoro()

    updated_projects = scan_projects(VAULT_DIR, data)
    target_p = next((p for p in updated_projects if p["rel_path"] == rel_path or p["title"] == title), None)

    m_el = int(effective_elapsed_min)
    s_el = int((effective_elapsed_min - m_el) * 60)

    if as_json:
        out = {
            "status": "stopped",
            "project": title,
            "rel_path": rel_path,
            "elapsed_minutes": round(effective_elapsed_min, 2),
            "target_minutes": round(target_min, 2),
            "ratio": round(ratio, 4),
            "effective_score": target_p.get("effective_score") if target_p else None,
            "temporal_malus": target_p.get("temporal_malus") if target_p else 0.0,
            "k_factor": target_p.get("k_factor") if target_p else 0.0,
            "global_pomodoro_time": data.get("stats", {}).get("globalStats", {}).get("totalPomodoroTime", 0)
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print("============================================================", flush=True)
        print(f"🛑 Session Pomodoro interrompue avec succès pour '{title}' !", flush=True)
        print("============================================================", flush=True)
        print(f"⏱️ Durée cible : {target_min:.0f} min", flush=True)
        print(f"⏳ Temps réellement écoulé : {m_el:02d}:{s_el:02d} ({effective_elapsed_min:.2f} min)", flush=True)
        print(f"📊 Ratio d'accomplissement (r) : {ratio * 100:.1f}%", flush=True)
        print(f"📈 Total Pomodoro global : {data.get('stats', {}).get('globalStats', {}).get('totalPomodoroTime', 0):.2f} min (+{effective_elapsed_min:.2f} min)", flush=True)
        if target_p:
            eff_disp = f"{target_p['effective_score']:.2f}" if target_p['effective_score'] is not None else "N/A"
            malus_disp = f"-{target_p['temporal_malus']:.2f} (K={target_p['k_factor']:.2f})" if target_p.get('temporal_malus') else "0.00"
            print(f"🎯 Score effectif mis à jour : {eff_disp} [Malus temporel proportionnel : {malus_disp}]", flush=True)
        print("============================================================", flush=True)


def cmd_status_work(args, data):
    active = load_active_pomodoro()
    as_json = getattr(args, "json", False)

    if not active or active.get("status") != "running":
        if as_json:
            print(json.dumps({"status": "idle", "active": False}, indent=2, ensure_ascii=False))
        else:
            print("💤 Aucune session Pomodoro en cours (idle).")
        return

    pid = active.get("pid")
    if pid and not is_pid_alive(pid):
        clear_active_pomodoro()
        if as_json:
            print(json.dumps({"status": "idle", "active": False, "stale_cleaned": True}, indent=2, ensure_ascii=False))
        else:
            print("💤 Aucune session Pomodoro en cours (le processus précédent s'est terminé).")
        return

    rel_path = active.get("rel_path")
    title = active.get("title", os.path.splitext(os.path.basename(rel_path))[0])
    start_ts = float(active.get("start_timestamp", time.time()))
    target_min = float(active.get("target_duration_minutes", 25))

    now_t = time.time()
    elapsed_sec = max(0.0, now_t - start_ts)
    elapsed_min = elapsed_sec / 60.0
    remaining_sec = max(0.0, (target_min * 60.0) - elapsed_sec)
    remaining_min = remaining_sec / 60.0
    pct = int(min(100.0, (elapsed_sec / (target_min * 60.0)) * 100)) if target_min > 0 else 100

    bar_len = 15
    filled = int(bar_len * (pct / 100.0))
    bar = "█" * filled + "░" * (bar_len - filled)

    m_el = int(elapsed_min)
    s_el = int(elapsed_sec % 60)
    m_rem = int(remaining_min)
    s_rem = int(remaining_sec % 60)

    if as_json:
        out = {
            "status": "running",
            "active": True,
            "pid": pid,
            "project": title,
            "rel_path": rel_path,
            "start_iso": active.get("start_iso"),
            "elapsed_minutes": round(elapsed_min, 2),
            "remaining_minutes": round(remaining_min, 2),
            "target_minutes": round(target_min, 2),
            "progress_percent": pct
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print("============================================================", flush=True)
        print(f"⏱️ Session Pomodoro Active : '{title}'", flush=True)
        print("============================================================", flush=True)
        print(f"⏳ Progression : [{bar}] {pct}%", flush=True)
        print(f"⏱️ Écoulé : {m_el:02d}:{s_el:02d} ({elapsed_min:.1f} min) / {target_min:.0f} min", flush=True)
        print(f"⌛ Restant : {m_rem:02d}:{s_rem:02d} ({remaining_min:.1f} min)", flush=True)
        print(f"⚙️ PID : {pid}", flush=True)
        print("💡 Pour interrompre proprement : `python antigravity/scripts/project_memory_cli.py stop-work`", flush=True)
        print("============================================================", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Project Memory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # list / priority / top
    list_parser = subparsers.add_parser("list", aliases=["priority", "top"], help="List active projects sorted by score")
    list_parser.add_argument("--top", "-n", type=int, help="Limit output to top N projects")
    list_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    list_parser.add_argument("--unreviewed", "--new", action="store_true", help="List only unreviewed projects awaiting initial evaluation")
    list_parser.add_argument("--reviewed", action="store_true", help="List only evaluated/reviewed projects sorted by score")
    list_parser.add_argument("--fast", action="store_true", help="Fast mode using existing cache without filesystem scan")
    list_parser.add_argument("--clean-orphans", action="store_true", help="Nettoie d'abord les notes orphelines de data.json avant de lister")

    # clean-orphans
    clean_parser = subparsers.add_parser("clean-orphans", help="Nettoie les projets de data.json dont les fichiers n'existent plus sur le disque")
    clean_parser.add_argument("--dry-run", action="store_true", help="Simule le nettoyage sans modifier data.json ni le cache")
    clean_parser.add_argument("--json", action="store_true", help="Sortie au format JSON")

    # get
    get_parser = subparsers.add_parser("get", help="Get project details and roadmap tasks")
    get_parser.add_argument("project_path", help="Relative path or name of project note")
    get_parser.add_argument("--json", action="store_true", help="Output in JSON format")

    # feedback
    fb_parser = subparsers.add_parser("feedback", help="Log review feedback for a project")
    fb_parser.add_argument("project_path", help="Relative path or name of project note")
    fb_parser.add_argument("pos_action", nargs="?", help="Action: ok, less-often, more-often, finished, emergency, non-projet")
    fb_parser.add_argument("--action", "-a", help="Action to perform")
    fb_parser.add_argument("--worked", "-w", action="store_true", default=True, help="Record a work session with recency penalty (Default: True)")
    fb_parser.add_argument("--no-work", "--not-worked", "--review-only", dest="no_work", action="store_true", help="Explicitly mark as review-only without recording a work session.")

    # complete-task
    comp_parser = subparsers.add_parser("complete-task", help="Check off a task in a project note")
    comp_parser.add_argument("project_path", help="Relative path or name of project note")
    comp_parser.add_argument("task_text", help="Text snippet of the task to mark completed")

    # set-score
    set_score_parser = subparsers.add_parser("set-score", help="Set explicit urgency score (1-100) for a project")
    set_score_parser.add_argument("project_path", help="Relative path or name of project note")
    set_score_parser.add_argument("score", type=float, help="Explicit score between 1.0 and 100.0")
    set_score_parser.add_argument("--worked", "-w", action="store_true", default=False, help="Set ONLY if user actively worked on the project during this session (Default: False)")

    # work
    work_parser = subparsers.add_parser("work", help="Démarre une session Pomodoro active sur un projet (durée nominale configurée dans data.json)")
    work_parser.add_argument("project_path", help="Chemin relatif ou nom du projet")
    work_parser.add_argument("--duration", "-d", type=int, help="Override optionnel exceptionnel de durée en minutes (comportement officiel et nominal : pomodoroDuration de data.json)")

    # stop-work / cancel-work / stop
    stop_parser = subparsers.add_parser("stop-work", aliases=["cancel-work", "stop"], help="Interrompt proprement la session Pomodoro en cours et enregistre le temps proportionnel")
    stop_parser.add_argument("project_path", nargs="?", help="Chemin ou nom du projet (optionnel si une session active est détectée)")
    stop_parser.add_argument("--elapsed", "-e", type=float, help="Temps réellement écoulé en minutes (outrepasse le calcul chronométré automatique)")
    stop_parser.add_argument("--target-duration", "-d", type=float, help="Durée cible en minutes (si enregistrement manuel)")
    stop_parser.add_argument("--json", action="store_true", help="Sortie au format JSON")

    # status-work / active-pomodoro / status
    status_parser = subparsers.add_parser("status-work", aliases=["active-pomodoro", "status"], help="Affiche l'état de la session Pomodoro en cours")
    status_parser.add_argument("--json", action="store_true", help="Sortie au format JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    data = load_data(DATA_JSON_PATH)

    if args.command in ("list", "priority", "top"):
        cmd_list(args, data)
    elif args.command == "clean-orphans":
        cmd_clean_orphans(args, DATA_JSON_PATH, CACHE_PATH)
    elif args.command == "get":
        cmd_get(args, data)
    elif args.command == "feedback":
        cmd_feedback(args, data)
    elif args.command == "set-score":
        cmd_set_score(args, data)
    elif args.command == "complete-task":
        cmd_complete_task(args, data)
    elif args.command == "work":
        cmd_work(args, data)
    elif args.command in ("stop-work", "cancel-work", "stop"):
        cmd_stop_work(args, data)
    elif args.command in ("status-work", "active-pomodoro", "status"):
        cmd_status_work(args, data)


if __name__ == "__main__":
    main()
