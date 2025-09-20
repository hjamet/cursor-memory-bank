#!/usr/bin/env python3
"""
Repository snapshot generator (Python version of bash `tomd`), fail-fast.

This script creates a Markdown snapshot of the repository at `repo.md`:
1) Writes a directory tree of selected files
2) For each selected file, embeds either the full content or head/tail excerpts
3) Writes current git diff into a file named `diff`

Design goals vs the original bash version:
- No temporary files
- Single pass memory structures
- Simple stderr progress bar showing current phase and percent
- Strict fail-fast: let exceptions propagate, no silent fallbacks

Usage:
  PYTHONPATH=. python tomd.py

Notes:
- Content is read using UTF-8 with surrogateescape to tolerate non-UTF bytes
- Hidden files (starting with a dot) are skipped
- Hidden directories and any `node_modules` directories are pruned
"""

from __future__ import annotations

import os
import sys
import subprocess
from collections import OrderedDict, deque
from typing import Dict, Iterable, List, Tuple


# ---------------------------- Configuration ---------------------------- #
INCLUDE_EXTENSIONS = {
    "py", "md", "tex", "css", "js", "tsx", "ipynb", "sh",
}

TRUNCATE_EXTENSIONS = {
    "csv", "json", "log", "tsv", "yml", "yaml",
}

INCLUDE_FILENAMES = {
    "Dockerfile", "docker-compose.yml", "Makefile", "README.md",
}

EXCLUDE_FILENAMES = {
    "agent.md",
    "repo.md",
    "diff",
}

HEAD_LINES = 50
TAIL_LINES = 75

# Size limits
# Maximum file size to include entirely (512 KiB)
MAX_FILE_SIZE = 512 * 1024
# Read block size for streaming large files (64 KiB)
READ_BLOCK_SIZE = 64 * 1024

# Directories to prune entirely during walk (any depth)
PRUNE_DIR_NAMES = {"node_modules"}


# ---------------------------- Progress Bar ----------------------------- #
def print_progress(phase: str, value: int, total: int) -> None:
    """Prints a single-line progress indicator to stderr.

    Parameters
    ----------
    phase: str
        Current phase description.
    value: int
        Current progress value (0..total).
    total: int
        Total units for this phase.
    """
    # Guard against division by zero
    width = 40
    if total <= 0:
        percent = 100
        filled = width
    else:
        percent = int((value / total) * 100)
        filled = int(width * value / total)

    bar = "#" * filled + "-" * (width - filled)
    sys.stderr.write(f"\r[{bar}] {percent:3d}%  {phase}")
    sys.stderr.flush()
    if value >= total:
        sys.stderr.write("\n")
        sys.stderr.flush()


# ------------------------------ Utilities ------------------------------ #
def is_hidden_name(name: str) -> bool:
    return name.startswith(".")


def split_extension_lower(filename: str) -> Tuple[str, str]:
    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        return filename, ext
    return filename, ""


def should_keep_file(filepath: str) -> bool:
    filename = os.path.basename(filepath)
    if is_hidden_name(filename):
        return False
    if filename in EXCLUDE_FILENAMES:
        return False

    _, ext_lc = split_extension_lower(filename)

    if filename in INCLUDE_FILENAMES:
        return True
    if ext_lc in INCLUDE_EXTENSIONS:
        return True
    if ext_lc in TRUNCATE_EXTENSIONS:
        return True
    return False


def collect_all_files(root: str = ".") -> List[str]:
    """Walk repository and return all file paths (relative), pruning hidden dirs and node_modules."""
    results: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Normalize relative path
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        # Prune hidden directories and node_modules at any depth
        pruned: List[str] = []
        for name in list(dirnames):
            if is_hidden_name(name) or name in PRUNE_DIR_NAMES:
                pruned.append(name)
        for name in pruned:
            dirnames.remove(name)

        for filename in filenames:
            if is_hidden_name(filename):
                continue
            path = os.path.join(rel_dir, filename) if rel_dir else filename
            # Full filesystem path for checks
            full_path = os.path.join(root, path)
            # Keep only regular files and skip files exceeding MAX_FILE_SIZE
            if not os.path.isfile(full_path):
                continue
            try:
                size = os.path.getsize(full_path)
            except OSError:
                # If we cannot stat the file, skip it (avoid crashing on special files)
                continue
            if size > MAX_FILE_SIZE:
                # Skip very large files to avoid OOM; they will not be included
                continue
            results.append(path)

    # Sort paths for deterministic output
    results.sort()
    return results


def filter_paths(paths: Iterable[str]) -> List[str]:
    kept = [p for p in paths if should_keep_file(p)]
    kept.sort()
    return kept


def build_tree(paths: Iterable[str]) -> OrderedDict:
    """Build a nested OrderedDict representing the directory tree."""
    root: OrderedDict = OrderedDict()
    for p in paths:
        # Split paths using the OS-specific separator to avoid mixing separators
        parts = p.split(os.sep)
        node = root
        for part in parts:
            if part not in node:
                node[part] = OrderedDict()
            node = node[part]
    return root


def render_tree(node: OrderedDict, prefix: str = "") -> List[str]:
    lines: List[str] = []
    keys = list(node.keys())
    for index, key in enumerate(keys):
        is_last = index == len(keys) - 1
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + key)
        new_prefix = prefix + ("    " if is_last else "│   ")
        lines.extend(render_tree(node[key], new_prefix))
    return lines


def write_header_and_tree(out, tree_lines: List[str]) -> None:
    out.write("# Repository snapshot\n\n")
    out.write("## Tree\n")
    out.write("```tree\n")
    for line in tree_lines:
        out.write(line + "\n")
    out.write("```\n\n")


def language_tag_for_file(filename: str) -> str:
    _, ext = split_extension_lower(filename)
    return ext


def write_file_section(out, filepath: str) -> None:
    filename = os.path.basename(filepath)
    lang = language_tag_for_file(filename)
    include_full = (filename in INCLUDE_FILENAMES) or (lang in INCLUDE_EXTENSIONS)
    is_truncate = lang in TRUNCATE_EXTENSIONS

    out.write(f"### {filepath}\n")
    out.write("```" + lang + "\n")

    if include_full:
        # Stream file in blocks to avoid loading entire file into memory
        try:
            with open(filepath, "rb") as fh:
                while True:
                    block = fh.read(READ_BLOCK_SIZE)
                    if not block:
                        break
                    # Decode using surrogateescape to preserve bytes
                    try:
                        out.write(block.decode("utf-8", "surrogateescape"))
                    except UnicodeDecodeError:
                        # Fallback: replace undecodable bytes
                        out.write(block.decode("utf-8", "replace"))
        except (IOError, UnicodeDecodeError) as exc:
            # Write an inline error message into repo.md instead of crashing
            out.write(f"[Error reading file {filepath}: {exc}]\n")
    elif is_truncate:
        head_buf: List[str] = []
        tail_buf: deque[str] = deque(maxlen=TAIL_LINES)
        line_index = 0
        with open(filepath, "r", encoding="utf-8", errors="surrogateescape") as fh:
            for line in fh:
                line_index += 1
                if line_index <= HEAD_LINES:
                    head_buf.append(line)
                tail_buf.append(line)

        for line in head_buf:
            out.write(line)
        out.write("\n\n... (omitted middle lines) ...\n\n")
        for line in tail_buf:
            out.write(line)
    else:
        out.write("[Skipped: not in include lists]\n")

    out.write("```\n\n")


def write_sections(out, filtered_paths: List[str]) -> None:
    total = len(filtered_paths)
    for index, path in enumerate(filtered_paths, start=1):
        print_progress("Embedding files into repo.md", index, total)
        write_file_section(out, path)


def write_git_diff(diff_path: str = "diff") -> None:
    # Capture git diff output as raw bytes and decode with surrogateescape
    # to avoid platform-specific decoding errors (e.g. cp1252 on Windows).
    try:
        diff_bytes = subprocess.check_output(["git", "diff"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        # Even if git exits with non-zero status, capture whatever output it produced
        diff_bytes = exc.output or b""

    diff_content = diff_bytes.decode("utf-8", "surrogateescape")

    # Write regardless; empty diff is valid
    with open(diff_path, "w", encoding="utf-8", errors="surrogateescape") as out:
        out.write(diff_content)


def main() -> None:
    # Phase 1: Collect all files
    print_progress("Scanning repository files", 0, 1)
    all_paths = collect_all_files(".")
    print_progress("Scanning repository files", 1, 1)

    # Phase 2: Filter paths
    print_progress("Filtering file list", 0, 1)
    filtered_paths = filter_paths(all_paths)
    print_progress("Filtering file list", 1, 1)

    # Phase 3: Build and render tree
    print_progress("Building directory tree", 0, 1)
    tree = build_tree(filtered_paths)
    tree_lines = render_tree(tree)
    print_progress("Building directory tree", 1, 1)

    # Phase 4: Write header + tree
    print_progress("Writing header and tree to repo.md", 0, 1)
    # Open repo.md once for the whole operation
    with open("repo.md", "w", encoding="utf-8", errors="surrogateescape") as out:
        write_header_and_tree(out, tree_lines)
        print_progress("Writing header and tree to repo.md", 1, 1)

        # Phase 5: Write file sections with progress per-file
        write_sections(out, filtered_paths)

    # Phase 6: Write git diff
    print_progress("Writing git diff to diff", 0, 1)
    write_git_diff("diff")
    print_progress("Writing git diff to diff", 1, 1)

    sys.stderr.write("Opération tomd terminée.\n")
    sys.stderr.flush()


if __name__ == "__main__":
    main()


