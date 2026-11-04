#!/usr/bin/env python3
"""
apply_task_commit_rename.py — Renommage chirurgical de l'outil MCP remember -> task_commit
et alignement advance_sync -> project_sync dans la gouvernance _agents/ d'Obsidian.
"""

import argparse
import difflib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CANONICAL_TARGET_FILES = [
    "_agents/rules/superviseur-aveugle.md",
    "_agents/rules/sous-agents.md",
    "_agents/rules/zero-trust.md",
    "_agents/rules/task-tracking.md",
    "_agents/agents/superviseur-projet.md",
    "_agents/skills/advance/SKILL.md",
    "_agents/skills/dream/SKILL.md",
    "_agents/skills/one-shot/SKILL.md",
    "_agents/skills/project-memory/SKILL.md",
]


def transform_markdown_content(text: str, filename: str = "") -> str:
    """
    Applique les transformations de renommage avec préservation stricte du sens,
    sans faux positifs et avec idempotence absolue.
    """
    # 1. Exception historique zero-trust (exemple concret réel du 29/10/2026)
    if "pydantic_settings` de `mcp-cli call aivc remember`" in text:
        text = text.replace(
            "pydantic_settings` de `mcp-cli call aivc remember`",
            "pydantic_settings` de `mcp-cli call aivc task_commit (anciennement remember)`",
        )
    elif "warnings pydantic_settings de mcp-cli call aivc remember" in text:
        text = text.replace(
            "warnings pydantic_settings de mcp-cli call aivc remember",
            "warnings pydantic_settings de mcp-cli call aivc task_commit (anciennement remember)",
        )

    # 2. CLI, arguments et noms de fichiers
    text = text.replace("mcp-cli call aivc remember", "mcp-cli call aivc task_commit")
    text = text.replace("remember_payload.json", "task_commit_payload.json")
    text = text.replace("advance_sync.py", "project_sync.py")

    # 3. Code inline et syntaxe entre parenthèses
    text = re.sub(r"(?<!anciennement )`remember`", "`task_commit`", text)
    text = re.sub(r"\(remember\)", "(task_commit)", text)

    # 4. Expressions clés en français / gouvernance AIVC
    text = re.sub(r"\bvia remember\b", "via task_commit", text)
    text = re.sub(r"\bseul AIVC remember\b", "seul AIVC task_commit", text)
    text = re.sub(
        r"\bappel(?:s)? (?:MCP )?remember\b",
        lambda m: m.group(0).replace("remember", "task_commit"),
        text,
    )
    text = re.sub(
        r"\b(?:appeler|appelle|appels|appelant|d'appeler)\b remember\b",
        lambda m: m.group(0).replace("remember", "task_commit"),
        text,
    )
    text = re.sub(
        r"\b(?:chaque|à chaque)\b remember\b",
        lambda m: m.group(0).replace("remember", "task_commit"),
        text,
    )
    text = re.sub(
        r"\b(?:un|le|du|au|dans le)\b remember\b",
        lambda m: m.group(0).replace("remember", "task_commit"),
        text,
    )
    text = re.sub(r"\bremember AIVC\b", "task_commit AIVC", text)
    text = re.sub(r"\bdans remember\b", "dans task_commit", text)
    text = re.sub(r"\bde remember\b", "de task_commit", text)
    text = re.sub(r"\bsur remember\b", "sur task_commit", text)
    text = re.sub(r"\b1 remember\b", "1 task_commit", text)

    return text


def find_target_files(vault_dir: Path) -> List[Tuple[Path, str]]:
    """
    Localise les fichiers cibles soit via chemins relatifs _agents/...
    soit directement si vault_dir est déjà _agents ou .agents.
    """
    targets: List[Tuple[Path, str]] = []
    seen = set()

    for rel_path in CANONICAL_TARGET_FILES:
        p1 = vault_dir / rel_path
        if p1.is_file() and p1.resolve() not in seen:
            targets.append((p1, rel_path))
            seen.add(p1.resolve())
            continue

        stripped_rel = re.sub(r"^[_.]agents[\\/]", "", rel_path)
        p2 = vault_dir / stripped_rel
        if p2.is_file() and p2.resolve() not in seen:
            targets.append((p2, rel_path))
            seen.add(p2.resolve())
            continue

        p3 = vault_dir / ".agents" / stripped_rel
        if p3.is_file() and p3.resolve() not in seen:
            targets.append((p3, f".agents/{stripped_rel}"))
            seen.add(p3.resolve())
            continue

    # Chercher tout autre fichier .md sous _agents/ ou .agents/ qui contiendrait "mcp-cli call aivc remember"
    search_dirs = []
    if (vault_dir / "_agents").is_dir():
        search_dirs.append(vault_dir / "_agents")
    elif (vault_dir / ".agents").is_dir():
        search_dirs.append(vault_dir / ".agents")
    elif vault_dir.name in ("_agents", ".agents"):
        search_dirs.append(vault_dir)

    for sdir in search_dirs:
        for md_file in sdir.rglob("*.md"):
            if md_file.resolve() in seen:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                if "mcp-cli call aivc remember" in content:
                    rel = str(md_file.relative_to(vault_dir)).replace("\\", "/")
                    targets.append((md_file, rel))
                    seen.add(md_file.resolve())
            except OSError:
                pass

    return targets


def run_pipeline(
    vault_dir: Path,
    apply_changes: bool = False,
    diff_output: Optional[Path] = None,
    updated_cli_source: Optional[Path] = None,
) -> Tuple[int, str]:
    """
    Exécute le pipeline de détection, calcul des diffs et application conditionnelle.
    Retourne (nombre_de_fichiers_modifiés, rapport_diff_markdown).
    """
    targets = find_target_files(vault_dir)
    diff_blocks: List[str] = []
    modified_count = 0

    mode_str = "APPLY (Modifications appliquées sur le disque)" if apply_changes else "DRY-RUN (Lecture seule, aucune modification)"

    report_lines = [
        "# Rapport de Diff — Renommage `remember` -> `task_commit` & Alignement `project_sync`",
        "",
        f"- **Date d'exécution** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Mode** : {mode_str}",
        f"- **Répertoire cible** : `{vault_dir}`",
        f"- **Nombre de fichiers cibles inspectés** : {len(targets)}",
        "",
    ]

    for file_path, rel_label in targets:
        try:
            original_text = file_path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"[ERREUR] Impossible de lire {file_path}: {e}", file=sys.stderr)
            continue

        new_text = transform_markdown_content(original_text, filename=file_path.name)
        if new_text != original_text:
            modified_count += 1
            orig_lines = original_text.splitlines(keepends=True)
            new_lines = new_text.splitlines(keepends=True)
            diff = difflib.unified_diff(
                orig_lines,
                new_lines,
                fromfile=f"a/{rel_label}",
                tofile=f"b/{rel_label}",
                lineterm="",
            )
            diff_text = "".join(diff)
            diff_blocks.append(f"### `{rel_label}`\n\n```diff\n{diff_text}\n```\n")

            if apply_changes:
                file_path.write_text(new_text, encoding="utf-8")
                print(f"[APPLY] Modifié : {file_path}")
            else:
                print(f"[DRY-RUN] À modifier : {file_path}")

    # Gestion de project_memory_cli.py si demandé et présent
    cli_candidates = [
        vault_dir / "_agents" / "scripts-for-skills" / "project_memory_cli.py",
        vault_dir / ".agents" / "scripts-for-skills" / "project_memory_cli.py",
        vault_dir / "scripts-for-skills" / "project_memory_cli.py",
    ]
    target_cli = None
    for cand in cli_candidates:
        if cand.is_file():
            target_cli = cand
            break

    if target_cli and updated_cli_source and updated_cli_source.is_file():
        source_text = updated_cli_source.read_text(encoding="utf-8")
        target_text = target_cli.read_text(encoding="utf-8")
        if source_text != target_text:
            modified_count += 1
            diff = difflib.unified_diff(
                target_text.splitlines(keepends=True),
                source_text.splitlines(keepends=True),
                fromfile=f"a/{target_cli.name}",
                tofile=f"b/{target_cli.name}",
                lineterm="",
            )
            diff_blocks.append(f"### `{target_cli.name}`\n\n```diff\n{''.join(diff)}\n```\n")
            if apply_changes:
                shutil.copy2(updated_cli_source, target_cli)
                print(f"[APPLY] Mis à jour : {target_cli} depuis {updated_cli_source}")
            else:
                print(f"[DRY-RUN] À mettre à jour : {target_cli} depuis {updated_cli_source}")

    report_lines.append(f"## Synthèse : {modified_count} fichier(s) modifié(s)\n")
    if diff_blocks:
        report_lines.extend(diff_blocks)
    else:
        report_lines.append("_Aucune modification détectée (fichiers déjà à jour ou aucun changement requis)._\n")

    full_report = "\n".join(report_lines)

    if diff_output:
        diff_output.parent.mkdir(parents=True, exist_ok=True)
        diff_output.write_text(full_report, encoding="utf-8")
        print(f"[RAPPORT] Rapport généré dans : {diff_output}")

    return modified_count, full_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Renommage de l'outil AIVC remember vers task_commit dans _agents/."
    )
    parser.add_argument(
        "--vault-dir",
        type=Path,
        default=Path(r"c:\Users\Jamet\Documents\VoiceNotes"),
        help="Chemin vers le vault Obsidian ou dossier _agents (défaut: c:\\Users\\Jamet\\Documents\\VoiceNotes)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Appliquer réellement les modifications aux fichiers sur le disque.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode simulation en lecture seule (actif par défaut si --apply n'est pas spécifié).",
    )
    parser.add_argument(
        "--diff-output",
        type=Path,
        default=None,
        help="Chemin où écrire le rapport Markdown complet des diffs unifiés.",
    )
    parser.add_argument(
        "--project-memory-source",
        type=Path,
        default=None,
        help="Chemin vers la version mise à jour de project_memory_cli.py.",
    )

    args = parser.parse_args()
    apply_mode = bool(args.apply)

    # Résolution de la source de project_memory_cli.py
    cli_source = args.project_memory_source
    if cli_source is None:
        cand_sources = [
            Path(r"C:\Users\Jamet\.gemini\antigravity-cli\brain\f26aba91-5383-4dd3-ac8e-a736047a5b7c\project_memory_cli_updated.py"),
            Path(r"c:\Users\Jamet\Documents\code\cursor-memory-bank\antigravity\scripts\project_memory_cli.py"),
        ]
        for c in cand_sources:
            if c.is_file():
                cli_source = c
                break

    mod_count, _ = run_pipeline(
        vault_dir=args.vault_dir,
        apply_changes=apply_mode,
        diff_output=args.diff_output,
        updated_cli_source=cli_source,
    )
    print(f"[TERMINE] {mod_count} fichier(s) concerné(s).")


if __name__ == "__main__":
    main()
