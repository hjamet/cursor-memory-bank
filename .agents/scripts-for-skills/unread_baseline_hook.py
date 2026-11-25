#!/usr/bin/env python3
"""
unread_baseline_hook.py — Capture automatique zéro-outil des baselines pré-édition
dans `_agents/unread_baselines.json` pour SlideFlow (Antigravity + Claude Code).

Invariants (Solution B Dirty-Only + Rasoir d'Ockham) :
- Zéro appel d'outil manuel requis par les agents : fonctionne de façon transparente
  sur PreToolUse / PostToolUse (Antigravity `_agents/hooks.json` + `~/.gemini/config/hooks.json`
  et Claude Code `~/.claude/settings.json`).
- Zéro daemon permanent, zéro cache fantôme, zéro faux positif sur les éditions d'Henri
  dans Obsidian (PC 1, PC 2 ou mobile), 100 % fonctionnel même Obsidian fermé & Multi-PC.
- PreToolUse : avant toute écriture/édition (`edit_file`, `write_file`, `Edit`, `Write`,
  ou `run_command` ciblant un `.md` du coffre), capture l'état exact sur disque (ou `""`
  pour une nouvelle note) uniquement si la note n'est pas déjà sale (préserve le diff
  cumulatif et `seenSlides`).
- PostToolUse : purge immédiatement l'entrée (0 octet) si le fichier final (hors frontmatter)
  est identique à la baseline (ex. édition uniquement du frontmatter YAML, no-op ou échec
  d'édition sur une note propre).
- Verrouillage inter-processus dans `%TEMP%` (zéro fichier temporaire dans le coffre sync).
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

BASELINES_REL_PATH = "_agents/unread_baselines.json"
EXCLUDED_PREFIXES = (
    "_agents/",
    ".obsidian/",
    ".git/",
    ".trash/",
    "templates/",
    ".pytest_cache/",
    ".playwright-mcp/",
    "virtual:",
    "scratch:",
    "~/",
)
EXCLUDED_EXACT_LOWER = {
    "🎯 projets.md",
}

FILE_EDIT_TOOLS = {
    "edit_file",
    "write_file",
    "replace_file_content",
    "multi_replace_file_content",
    "write_to_file",
    "edit",
    "write",
    "multiedit",
}

SHELL_TOOLS = {
    "run_command",
    "bash",
}

SELF_MANAGED_SCRIPTS = (
    "project_memory_cli.py",
    "doc_version_cli.py",
    "unread_baseline_hook.py",
)

PATH_ARG_KEYS = (
    "Path",
    "TargetFile",
    "AbsolutePath",
    "path",
    "file_path",
    "target_file",
)

MD_PATH_REGEX = re.compile(
    r"""(?:"([^"\r\n]+?\.md)"|'([^'\r\n]+?\.md)'|([^\s"'`<>|;&()]+\.md))""",
    re.IGNORECASE,
)

UNVALIDATED_HEADING_RE = re.compile(
    r"\[(?:À\s+VALIDER|A\s+VALIDER|RECONÇUE\s*/\s*DURCIE|RECONCUE\s*/\s*DURCIE|À\s+RELIRE|A\s+RELIRE|TO\s+VALIDATE|PENDING\s+REVIEW)\]",
    re.IGNORECASE,
)
HEADING_LINE_RE = re.compile(r"^(#{1,6})\s+(.+)$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def strip_unvalidated_sections(text: str) -> str:
    """
    Removes any Markdown heading section whose title carries an explicit unvalidated
    review tag (`[À VALIDER]`, `[RECONÇUE / DURCIE]`, etc.), along with its body and
    nested sub-headings, so unvalidated items are NEVER baked into a freshly captured
    SlideFlow baseline and always appear as positive `<ins>` diffs until Henri validates them.
    """
    if not text or not UNVALIDATED_HEADING_RE.search(text):
        return text

    lines = text.replace("\r\n", "\n").split("\n")
    out: List[str] = []
    skip_level: Optional[int] = None
    in_fence_char = ""
    in_fence_len = 0

    for line in lines:
        if not in_fence_char:
            m_open = FENCE_OPEN_RE.match(line)
            if m_open and not (m_open.group(1)[0] == "`" and "`" in m_open.group(2)):
                in_fence_char = m_open.group(1)[0]
                in_fence_len = len(m_open.group(1))
                if skip_level is None:
                    out.append(line)
                continue
        else:
            if re.match(rf"^ {{0,3}}{re.escape(in_fence_char)}{{{in_fence_len},}}[ \t]*$", line):
                in_fence_char = ""
                in_fence_len = 0
            if skip_level is None:
                out.append(line)
            continue

        m_head = HEADING_LINE_RE.match(line)
        if m_head:
            lvl = len(m_head.group(1))
            title = m_head.group(2)
            if skip_level is not None and lvl <= skip_level:
                skip_level = None
            if skip_level is None:
                if UNVALIDATED_HEADING_RE.search(title):
                    skip_level = lvl
                    continue
                out.append(line)
            continue

        if skip_level is None:
            out.append(line)

    return "\n".join(out)


def get_vault_root() -> Path:
    env_dir = os.environ.get("VOICENOTES_DIR")
    if env_dir:
        return Path(env_dir).resolve()
    # Script lives at <VaultRoot>/_agents/scripts-for-skills/unread_baseline_hook.py
    script_based = Path(__file__).resolve().parents[2]
    if (script_based / "_agents").is_dir():
        return script_based
    return (Path.home() / "Documents" / "VoiceNotes").resolve()


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\r?\n[\s\S]*?\r?\n---\r?\n*", "", text.lstrip())


def is_trackable_rel_path(rel_path: str) -> bool:
    if not rel_path:
        return False
    norm = rel_path.replace("\\", "/").lstrip("/")
    lower = norm.lower()
    if not lower.endswith(".md"):
        return False
    if Path(norm).is_absolute() or ":" in norm:
        return False
    if lower in EXCLUDED_EXACT_LOWER:
        return False
    basename = norm.rsplit("/", 1)[-1]
    if basename.startswith("🤖"):
        return False
    for pref in EXCLUDED_PREFIXES:
        if lower.startswith(pref):
            return False
    return True


def resolve_trackable_target(
    raw_path: str, vault_root: Path, cwd: Optional[str] = None
) -> Optional[Tuple[str, Path]]:
    if not raw_path or not isinstance(raw_path, str):
        return None
    cleaned = raw_path.strip().strip('"').strip("'")
    if not cleaned or cleaned.startswith(("virtual:", "scratch:", "http://", "https://")):
        return None

    try:
        if cleaned.startswith("~/") or cleaned == "~":
            cand = Path(cleaned).expanduser()
        else:
            cand = Path(cleaned)
            if not cand.is_absolute():
                base = Path(cwd) if cwd else vault_root
                cand_cwd = base / cand
                if cand_cwd.exists() or str(base).lower().startswith(str(vault_root).lower()):
                    cand = cand_cwd
                else:
                    cand = vault_root / cand
        resolved = cand.resolve()
    except OSError:
        return None

    try:
        rel_posix = resolved.relative_to(vault_root).as_posix()
    except ValueError:
        res_posix = resolved.as_posix()
        vr_posix = vault_root.as_posix()
        if res_posix.lower().startswith(vr_posix.lower() + "/"):
            rel_posix = res_posix[len(vr_posix) + 1 :]
        else:
            return None

    if not is_trackable_rel_path(rel_posix):
        return None
    return rel_posix, resolved


@contextmanager
def baselines_lock(timeout_s: float = 4.0, stale_s: float = 10.0) -> Iterator[None]:
    lock_path = Path(tempfile.gettempdir()) / "slideflow_unread_baselines.lock"
    deadline = time.monotonic() + timeout_s
    fd: Optional[int] = None

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, f"{os.getpid()} {time.time():.3f}".encode("ascii"))
            break
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age > stale_s:
                    lock_path.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timeout acquiring lock {lock_path}")
            time.sleep(0.015)

    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            lock_path.unlink(missing_ok=True)
        except OSError:
            pass


def load_baselines(baselines_path: Path) -> Dict[str, Any]:
    if not baselines_path.exists():
        return {"version": 1, "notes": {}}
    raw = baselines_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("notes"), dict):
        raise ValueError(f"Format invalide dans {baselines_path}: clé 'notes' attendue.")
    data.setdefault("version", 1)
    return data


def save_baselines(baselines_path: Path, data: Dict[str, Any]) -> None:
    baselines_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = baselines_path.with_name(f".{baselines_path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp_path.replace(baselines_path)


def extract_targets_from_payload(
    payload: Dict[str, Any], vault_root: Path
) -> Tuple[str, str, List[Tuple[str, Path]], bool]:
    """
    Returns (event_name, tool_name, [(rel_path, abs_path), ...], allow_new_file).
    Supports both Antigravity (`hookEventName` + `toolCall`) and Claude Code
    (`hook_event_name` + `tool_name` + `tool_input`).
    """
    cwd = payload.get("cwd")
    if isinstance(payload.get("toolCall"), dict):
        event_name = str(payload.get("hookEventName") or "PreToolUse")
        tc = payload["toolCall"]
        tool_name = str(tc.get("name") or "")
        args = tc.get("args") if isinstance(tc.get("args"), dict) else {}
    else:
        event_name = str(payload.get("hook_event_name") or "PreToolUse")
        tool_name = str(payload.get("tool_name") or "")
        args = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}

    tool_lower = tool_name.lower()
    targets: List[Tuple[str, Path]] = []
    seen_rel: set[str] = set()

    if tool_lower in FILE_EDIT_TOOLS:
        for key in PATH_ARG_KEYS:
            val = args.get(key)
            if isinstance(val, str) and val.strip():
                resolved = resolve_trackable_target(val, vault_root, cwd)
                if resolved and resolved[0] not in seen_rel:
                    seen_rel.add(resolved[0])
                    targets.append(resolved)
        return event_name, tool_name, targets, True

    if tool_lower in SHELL_TOOLS:
        cmd = str(args.get("CommandLine") or args.get("command") or "")
        if not cmd or ".md" not in cmd.lower():
            return event_name, tool_name, [], False
        cmd_lower = cmd.lower()
        if any(s in cmd_lower for s in SELF_MANAGED_SCRIPTS):
            return event_name, tool_name, [], False
        for m in MD_PATH_REGEX.finditer(cmd):
            raw_cand = m.group(1) or m.group(2) or m.group(3) or ""
            resolved = resolve_trackable_target(raw_cand, vault_root, cwd)
            if resolved and resolved[0] not in seen_rel:
                seen_rel.add(resolved[0])
                targets.append(resolved)
        return event_name, tool_name, targets, True

    return event_name, tool_name, [], False


def handle_pre_tool_use(
    vault_root: Path,
    tool_name: str,
    targets: List[Tuple[str, Path]],
    allow_new_file: bool,
) -> None:
    if not targets:
        return
    baselines_path = (vault_root / BASELINES_REL_PATH).resolve()
    now_iso = datetime.now(timezone.utc).isoformat()

    with baselines_lock():
        data = load_baselines(baselines_path)
        notes = data["notes"]
        changed = False

        for rel_path, abs_path in targets:
            if rel_path in notes:
                continue
            if abs_path.is_file():
                baseline_text = abs_path.read_text(encoding="utf-8", errors="replace")
            elif allow_new_file:
                baseline_text = ""
            else:
                continue

            notes[rel_path] = {
                "baseline": baseline_text,
                "updatedAt": now_iso,
                "updatedBy": "agent",
                "summary": f"Auto-captured before {tool_name}",
                "seenSlides": {},
            }
            changed = True

        if changed:
            save_baselines(baselines_path, data)


def handle_post_tool_use(
    vault_root: Path, targets: List[Tuple[str, Path]]
) -> None:
    if not targets:
        return
    baselines_path = (vault_root / BASELINES_REL_PATH).resolve()
    if not baselines_path.exists():
        return

    with baselines_lock():
        data = load_baselines(baselines_path)
        notes = data["notes"]
        changed = False

        for rel_path, abs_path in targets:
            entry = notes.get(rel_path)
            if not entry:
                continue
            baseline_text = entry.get("baseline", "")
            if not abs_path.is_file():
                if baseline_text == "":
                    del notes[rel_path]
                    changed = True
                continue
            disk_text = abs_path.read_text(encoding="utf-8", errors="replace")
            if strip_frontmatter(disk_text).strip() == strip_frontmatter(baseline_text).strip():
                del notes[rel_path]
                changed = True
                continue
            # Ensure freshly captured baselines never swallow explicit `[À VALIDER]` sections
            if not entry.get("seenSlides") and entry.get("updatedBy") == "agent":
                cleaned_baseline = strip_unvalidated_sections(baseline_text)
                if cleaned_baseline != baseline_text:
                    entry["baseline"] = cleaned_baseline
                    changed = True

        if changed:
            save_baselines(baselines_path, data)


def main() -> int:
    raw_stdin = sys.stdin.read()
    if not raw_stdin.strip():
        print(json.dumps({"decision": "allow"}))
        return 0

    payload = json.loads(raw_stdin)
    is_antigravity = isinstance(payload.get("toolCall"), dict) or "hookEventName" in payload
    vault_root = get_vault_root()
    event_name, tool_name, targets, allow_new_file = extract_targets_from_payload(
        payload, vault_root
    )

    if event_name == "PreToolUse":
        handle_pre_tool_use(vault_root, tool_name, targets, allow_new_file)
        print(json.dumps({"decision": "allow"} if is_antigravity else {}))
        return 0

    if event_name == "PostToolUse":
        handle_post_tool_use(vault_root, targets)
        print("{}")
        return 0

    print(json.dumps({"decision": "allow"} if is_antigravity else {}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
