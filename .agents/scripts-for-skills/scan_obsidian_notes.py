#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_obsidian_notes.py - Helper script to scan Obsidian vault for notes modified since last_sync_timestamp.
Extracts rich structural context (titles, frontmatter metadata, callouts, key sections, transcripts, todos).
"""

import os
import sys
import re
import json
import argparse
import random
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_VAULT_DIR = str(Path(__file__).resolve().parent.parent.parent)
DEFAULT_STATE_FILE = str(Path(__file__).resolve().parent.parent / "memory" / "morning_sync_state.json")
DEFAULT_MAX_CHARS = 2500
EXCLUDE_DIRS = {".obsidian", ".agents", "_agents", ".git", "antigravity", "_attachments"}
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf",
    ".webp", ".mp3", ".wav", ".m4a", ".mp4", ".mov", ".zip"
}


def parse_timestamp(ts_val):
    if ts_val is None:
        return 0.0
    if isinstance(ts_val, (int, float)):
        return float(ts_val)
    if isinstance(ts_val, str):
        ts_val = ts_val.strip()
        if not ts_val:
            return 0.0
        try:
            return float(ts_val)
        except ValueError:
            pass
        try:
            dt = datetime.fromisoformat(ts_val)
            return dt.timestamp()
        except ValueError:
            pass
    return 0.0


def get_last_sync_timestamp(state_file):
    if not os.path.exists(state_file):
        return 0.0, None
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_ts = data.get("last_sync_timestamp")
            return parse_timestamp(raw_ts), raw_ts
    except Exception as e:
        print(f"Warning: Error reading state file {state_file}: {e}", file=sys.stderr)
        return 0.0, None


def parse_frontmatter(content):
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            current_list_key = None
            for line in fm_text.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                # Handle list item (- item)
                if stripped.startswith("- ") and current_list_key:
                    item_val = stripped[2:].strip(" \"'")
                    if item_val:
                        if not isinstance(meta.get(current_list_key), list):
                            meta[current_list_key] = []
                        meta[current_list_key].append(item_val)
                    continue
                # Handle key: value
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    k = k.strip().lower()
                    v = v.strip().strip(" \"'")
                    current_list_key = k
                    if v:
                        if v.startswith("[") and v.endswith("]"):
                            items = [x.strip(" \"'") for x in v[1:-1].split(",") if x.strip()]
                            meta[k] = items
                        else:
                            meta[k] = v
                    else:
                        meta[k] = []
                elif stripped.startswith("#"):
                    # Inline hashtags in frontmatter (e.g. #idée #todo)
                    tags = [t.strip("#") for t in stripped.split() if t.startswith("#")]
                    if "tags" not in meta:
                        meta["tags"] = []
                    meta["tags"].extend(tags)
    return meta, body


def get_file_snippet(file_path, max_chars=DEFAULT_MAX_CHARS):
    """
    Extracts rich structural context from an Obsidian markdown file:
    - Frontmatter metadata (tags, status, priority, dates)
    - Main title (# Title)
    - Callout blocks (> [!NOTE], > [!IMPORTANT], etc.)
    - Key sections (## Summary, ## Transcript, ## Retranscription, ## Accès, ## Roadmap, etc.)
    - Pending Todos (- [ ] ...)
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return "", {}, [], [], os.path.splitext(os.path.basename(file_path))[0]

    meta, body = parse_frontmatter(content)

    # 1. Tags extraction (frontmatter + body hashtags)
    tags = set()
    if isinstance(meta.get("tags"), list):
        tags.update([str(t).lower().strip("#") for t in meta["tags"]])
    elif isinstance(meta.get("tags"), str):
        tags.add(meta["tags"].lower().strip("#"))

    for m in re.finditer(r"(?:^|\s)#([a-zA-Z0-9_\u00C0-\u017F/-]+)", body):
        t = m.group(1).lower()
        if t not in ("---", "!", ""):
            tags.add(t)

    # 2. Title extraction
    title_match = re.search(r"^#\s+(.+)$", body, re.M)
    if not title_match:
        title_match = re.search(r"^#\s+(.+)$", content, re.M)
    title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(file_path))[0]

    # 3. Callout blocks extraction (> [!NOTE], > [!IMPORTANT], etc.)
    callout_matches = re.finditer(r">\s*\[!([A-Za-z]+)\]([^\n]*)(?:\n>[^\n]*)*", body, re.M)
    callouts = []
    for cm in callout_matches:
        full_co = cm.group(0)
        co_type = cm.group(1).upper()
        lines = [re.sub(r"^>\s*", "", l) for l in full_co.splitlines()]
        if lines and lines[0].startswith(f"[!{cm.group(1)}]"):
            first_line_rest = lines[0][len(f"[!{cm.group(1)}]") :].strip()
            lines = ([first_line_rest] if first_line_rest else []) + lines[1:]
        clean_text = "\n".join([l for l in lines if l.strip()])
        if clean_text:
            callouts.append((co_type, clean_text))

    # 4. Todos extraction (- [ ] ...)
    todos = [line.strip() for line in body.splitlines() if line.strip().startswith("- [ ]")]

    # 5. Sections extraction (##, ###)
    sections = {}
    current_sec = None
    current_lines = []
    for line in body.splitlines():
        h_match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if h_match:
            if current_sec:
                sections[current_sec] = "\n".join(current_lines).strip()
            current_sec = h_match.group(2).strip()
            current_lines = []
        elif current_sec is not None:
            current_lines.append(line)
    if current_sec:
        sections[current_sec] = "\n".join(current_lines).strip()

    # 6. Compose rich structured snippet
    parts = []

    # Title & metadata header
    header_line = f"# {title}"
    meta_badges = []
    if meta.get("status"):
        meta_badges.append(f"Status: {meta['status']}")
    if meta.get("priority"):
        meta_badges.append(f"Priority: {meta['priority']}")
    if tags:
        tag_list = sorted(list(tags))
        tag_preview = ", ".join(tag_list[:8]) + (f" (+{len(tag_list)-8} tags)" if len(tag_list) > 8 else "")
        meta_badges.append(f"Tags: {tag_preview}")
    if meta_badges:
        header_line += f" ({', '.join(meta_badges)})"
    parts.append(header_line)

    # Callouts (up to 2 critical callouts)
    for co_type, co_text in callouts[:2]:
        preview = co_text if len(co_text) <= 400 else co_text[:400] + "..."
        parts.append(f"📌 [{co_type}]\n{preview}")

    # Important sections (Summary, Transcript, Access, Contacts, Context, Roadmap, etc.)
    priority_sec_keywords = [
        "summary", "résumé", "synthese", "synthèse", "objectif", "contexte", "context",
        "transcript", "retranscription", "transcription", "accès", "identifiant",
        "contact", "décision", "arbitrage", "action", "roadmap", "feuille de route"
    ]

    added_sections = 0
    for sec_name, sec_content in sections.items():
        sec_lower = sec_name.lower()
        if any(k in sec_lower for k in priority_sec_keywords):
            lines = [l for l in sec_content.splitlines() if l.strip()]
            if lines:
                preview = "\n".join(lines[:10])
                if len(preview) > 600:
                    preview = preview[:600] + "..."
                parts.append(f"## {sec_name}\n{preview}")
                added_sections += 1
                if added_sections >= 4:
                    break

    # Pending Todos
    if todos:
        todo_sample = todos[:8]
        more = f"\n... (+ {len(todos)-8} autres tâches en attente)" if len(todos) > 8 else ""
        parts.append(f"## Tâches en attente ({len(todos)}):\n" + "\n".join(todo_sample) + more)

    # Fallback to body content if note is unstructured
    if added_sections == 0 and not todos and not callouts:
        raw_lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
        if raw_lines:
            body_preview = "\n".join(raw_lines[:12])
            if len(body_preview) > 800:
                body_preview = body_preview[:800] + "..."
            parts.append(body_preview)

    snippet = "\n\n".join(parts)
    if len(snippet) > max_chars:
        snippet = snippet[:max_chars] + "..."

    return snippet, meta, sorted(list(tags)), todos, title


def get_archaeology_state(state_file):
    if not os.path.exists(state_file):
        return {}, []
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data, data.get("archaeology_visited", [])
    except Exception as e:
        print(f"Warning: Error reading state file {state_file}: {e}", file=sys.stderr)
        return {}, []


def save_archaeology_state(state_file, state_data, visited_list):
    state_data["archaeology_visited"] = visited_list
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Error saving archaeology state to {state_file}: {e}", file=sys.stderr)


def scan_active_notes_with_graph(vault_dir, exclude_dirs, max_chars=DEFAULT_MAX_CHARS):
    """
    Scans all active notes in vault (excluding done notes, autonomous 🤖 notes, and system dirs),
    extracts wikilinks [[Target|Alias]] (ignoring media attachments),
    and computes total degree = in_degree + out_degree for each note.
    """
    active_notes = []
    rel_map = {}
    stem_map = {}

    if not os.path.exists(vault_dir):
        print(f"Error: Vault directory {vault_dir} does not exist", file=sys.stderr)
        return active_notes

    for root, dirs, files in os.walk(vault_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not file.lower().endswith(".md"):
                continue
            if file.startswith("🤖"):
                continue

            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            meta, body = parse_frontmatter(content)
            tags = set()
            if isinstance(meta.get("tags"), list):
                tags.update([str(t).lower().strip("#") for t in meta["tags"]])
            elif isinstance(meta.get("tags"), str):
                tags.add(meta["tags"].lower().strip("#"))
            for m in re.finditer(r"(?:^|\s)#([a-zA-Z0-9_\u00C0-\u017F/-]+)", body):
                t = m.group(1).lower()
                if t not in ("---", "!", ""):
                    tags.add(t)

            # Exclude done / archived notes
            if "done" in tags or "projet-fini" in tags:
                continue
            if str(meta.get("status", "")).lower() in ("done", "archived", "termine", "terminé"):
                continue

            title_match = re.search(r"^#\s+(.+)$", body, re.M) or re.search(r"^#\s+(.+)$", content, re.M)
            title = title_match.group(1).strip() if title_match else os.path.splitext(file)[0]
            if title.startswith("🤖"):
                continue

            rel_path = os.path.relpath(full_path, vault_dir).replace("\\", "/")
            stem = os.path.splitext(file)[0]
            stem_lower = stem.lower()
            rel_no_ext = os.path.splitext(rel_path)[0].replace("\\", "/").lower()

            try:
                mtime = os.path.getmtime(full_path)
            except Exception:
                mtime = 0.0
            mtime_iso = datetime.fromtimestamp(mtime).astimezone().isoformat() if mtime > 0 else ""

            # Extraire les wikilinks bruts [[Cible|Alias]]
            raw_links = re.findall(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", content)
            cleaned_links = set()
            for lk in raw_links:
                lk_s = lk.strip()
                ext = os.path.splitext(lk_s)[1].lower()
                if ext in IGNORED_EXTENSIONS:
                    continue
                cleaned_links.add(lk_s)

            note_entry = {
                "path": full_path,
                "relative_path": rel_path,
                "filename": file,
                "stem": stem,
                "stem_lower": stem_lower,
                "rel_no_ext": rel_no_ext,
                "mtime": mtime,
                "mtime_iso": mtime_iso,
                "title": title,
                "tags": sorted(list(tags)),
                "raw_links": cleaned_links
            }
            active_notes.append(note_entry)
            rel_map[rel_no_ext] = note_entry
            if stem_lower not in stem_map:
                stem_map[stem_lower] = []
            stem_map[stem_lower].append(note_entry)

    # Résolution des wikilinks et construction du graphe
    incoming = {n["relative_path"]: set() for n in active_notes}
    outgoing = {n["relative_path"]: set() for n in active_notes}

    for note in active_notes:
        src_path = note["relative_path"]
        for lk in note["raw_links"]:
            lk_norm = lk.replace("\\", "/").rstrip("/")
            lk_no_ext = os.path.splitext(lk_norm)[0].lower() if lk_norm.lower().endswith(".md") else lk_norm.lower()
            target_note = None
            if lk_no_ext in rel_map:
                target_note = rel_map[lk_no_ext]
            else:
                base_lk = os.path.basename(lk_no_ext).lower()
                candidates = stem_map.get(base_lk, [])
                if len(candidates) == 1:
                    target_note = candidates[0]
                elif len(candidates) > 1:
                    target_note = candidates[0]
            if target_note and target_note["relative_path"] != src_path:
                tgt_path = target_note["relative_path"]
                outgoing[src_path].add(tgt_path)
                incoming[tgt_path].add(src_path)

    # Calcul des degrés
    for note in active_notes:
        p = note["relative_path"]
        note["in_degree"] = len(incoming[p])
        note["out_degree"] = len(outgoing[p])
        note["degree"] = note["in_degree"] + note["out_degree"]
        del note["raw_links"]
        del note["stem"]
        del note["stem_lower"]
        del note["rel_no_ext"]

    return active_notes


def populate_note_snippet(note, max_chars=DEFAULT_MAX_CHARS):
    if "snippet" not in note:
        snippet, meta, tags, todos, title = get_file_snippet(note["path"], max_chars=max_chars)
        note["snippet"] = snippet
        note["status"] = meta.get("status")
        note["priority"] = meta.get("priority")
        note["todos_count"] = len(todos)
        note["todos"] = todos


def scan_notes(vault_dir, cut_timestamp, exclude_dirs, max_chars=DEFAULT_MAX_CHARS):
    modified_notes = []
    if not os.path.exists(vault_dir):
        print(f"Error: Vault directory {vault_dir} does not exist", file=sys.stderr)
        return modified_notes

    for root, dirs, files in os.walk(vault_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if not file.lower().endswith(".md"):
                continue

            full_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(full_path)
                if mtime > cut_timestamp:
                    rel_path = os.path.relpath(full_path, vault_dir).replace("\\", "/")
                    mtime_iso = datetime.fromtimestamp(mtime).astimezone().isoformat()
                    snippet, meta, tags, todos, title = get_file_snippet(full_path, max_chars=max_chars)

                    modified_notes.append({
                        "path": full_path,
                        "relative_path": rel_path,
                        "filename": file,
                        "mtime_iso": mtime_iso,
                        "title": title,
                        "tags": tags,
                        "status": meta.get("status"),
                        "priority": meta.get("priority"),
                        "todos_count": len(todos),
                        "todos": todos,
                        "snippet": snippet
                    })
            except Exception as e:
                continue

    # Sort descending by modification time (most recent first)
    modified_notes.sort(key=lambda x: x["mtime_iso"], reverse=True)
    return modified_notes


def main():
    parser = argparse.ArgumentParser(description="Scan Obsidian vault for modified notes since last sync, or graph-based archaeology / random exploration.")
    parser.add_argument("--vault-dir", default=DEFAULT_VAULT_DIR, help="Path to Obsidian vault root")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE, help="Path to morning sync state JSON file")
    parser.add_argument("--since", type=str, help="Override timestamp or ISO date string for filtering")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, help="Max snippet length in characters")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output results in structured JSON format")
    parser.add_argument("--least-connected", type=int, default=0, help="Return top N least connected notes in the vault (by total wikilink degree in+out)")
    parser.add_argument("--random-notes", type=int, default=0, help="Return M randomly sampled active notes from the vault")
    parser.add_argument("--update-state", action="store_true", help="Update archaeology_visited in morning_sync_state.json")

    args = parser.parse_args()

    # Graph exploration / archaeology mode
    if args.least_connected > 0 or args.random_notes > 0:
        active_notes = scan_active_notes_with_graph(args.vault_dir, EXCLUDE_DIRS, max_chars=args.max_chars)
        selected_least = []
        selected_random = []

        if args.least_connected > 0:
            state_data, visited_list = get_archaeology_state(args.state_file)
            visited_set = set(visited_list)
            all_sorted = sorted(active_notes, key=lambda x: (x["degree"], x["mtime"]))
            unvisited = [n for n in all_sorted if n["relative_path"] not in visited_set]
            if not unvisited and all_sorted:
                visited_list = []
                visited_set = set()
                unvisited = all_sorted
            selected_least = unvisited[:args.least_connected]
            for n in selected_least:
                populate_note_snippet(n, max_chars=args.max_chars)
            if args.update_state:
                new_visited = visited_list + [n["relative_path"] for n in selected_least]
                save_archaeology_state(args.state_file, state_data, new_visited)

        if args.random_notes > 0:
            k = min(args.random_notes, len(active_notes))
            selected_random = random.sample(active_notes, k) if k > 0 else []
            for n in selected_random:
                populate_note_snippet(n, max_chars=args.max_chars)

        if args.output_json:
            out = {}
            if args.least_connected > 0:
                out["least_connected"] = selected_least
            if args.random_notes > 0:
                out["random_notes"] = selected_random
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            if args.least_connected > 0:
                print(f"=== Least Connected Notes ({len(selected_least)}) ===")
                for idx, note in enumerate(selected_least, 1):
                    print(f"[{idx}] {note['relative_path']} (Degree: {note['degree']} | In: {note['in_degree']} | Out: {note['out_degree']} | Modified: {note['mtime_iso']})")
                    badges = []
                    if note.get("status"):
                        badges.append(f"Status: {note['status']}")
                    if note.get("priority"):
                        badges.append(f"Priority: {note['priority']}")
                    if note.get("todos_count"):
                        badges.append(f"Todos: {note['todos_count']} pending")
                    if badges:
                        print(f"    Info: {' | '.join(badges)}")
                    if note.get("snippet"):
                        indented = "\n".join("    " + l for l in note["snippet"].splitlines())
                        print(f"    --- Snippet ---")
                        print(indented)
                        print(f"    ----------------")
                    print()

            if args.random_notes > 0:
                print(f"=== Random Sampled Notes ({len(selected_random)}) ===")
                for idx, note in enumerate(selected_random, 1):
                    print(f"[{idx}] {note['relative_path']} (Degree: {note.get('degree', 0)} | Modified: {note['mtime_iso']})")
                    badges = []
                    if note.get("status"):
                        badges.append(f"Status: {note['status']}")
                    if note.get("priority"):
                        badges.append(f"Priority: {note['priority']}")
                    if note.get("todos_count"):
                        badges.append(f"Todos: {note['todos_count']} pending")
                    if badges:
                        print(f"    Info: {' | '.join(badges)}")
                    if note.get("snippet"):
                        indented = "\n".join("    " + l for l in note["snippet"].splitlines())
                        print(f"    --- Snippet ---")
                        print(indented)
                        print(f"    ----------------")
                    print()
        return

    # Standard mode: modified notes since last sync
    if args.since:
        cut_ts = parse_timestamp(args.since)
        raw_ts = args.since
    else:
        cut_ts, raw_ts = get_last_sync_timestamp(args.state_file)

    results = scan_notes(args.vault_dir, cut_ts, EXCLUDE_DIRS, max_chars=args.max_chars)

    if args.output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        since_desc = raw_ts if raw_ts else (datetime.fromtimestamp(cut_ts).astimezone().isoformat() if cut_ts > 0 else "beginning of time")
        print(f"Scanned vault '{args.vault_dir}' for notes modified since {since_desc}")
        print(f"Found {len(results)} modified note(s):\n")
        for idx, note in enumerate(results, 1):
            print(f"[{idx}] {note['relative_path']} (Modified: {note['mtime_iso']})")
            badges = []
            if note.get("status"):
                badges.append(f"Status: {note['status']}")
            if note.get("priority"):
                badges.append(f"Priority: {note['priority']}")
            if note.get("todos_count"):
                badges.append(f"Todos: {note['todos_count']} pending")
            if badges:
                print(f"    Info: {' | '.join(badges)}")
            if note.get("snippet"):
                indented = "\n".join("    " + l for l in note["snippet"].splitlines())
                print(f"    --- Snippet ---")
                print(indented)
                print(f"    ----------------")
            print()


if __name__ == "__main__":
    main()
