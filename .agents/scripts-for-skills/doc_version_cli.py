"""
doc_version_cli.py — Pont CLI officiel pour exécuter doc-version-mcp directement en ligne de commande.
Permet d'exécuter commit_document, get_diff_artifact, restore_commit, list_commits, prune_commits, record_git_pull_event en CLI directe.
"""

import sys
import os
import argparse
import json
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _setup_environment():
    """
    Résolution dynamique et portable du package doc_version_mcp.
    1. Tente d'importer doc_version_mcp directement si installé.
    2. Sinon, cherche dynamiquement dans les chemins candidats.
    3. Ajoute le dossier src et le virtualenv associé à sys.path si trouvés.
    4. En cas d'échec total, affiche un message d'erreur avec la commande d'installation.
    """
    try:
        import doc_version_mcp
        return
    except ImportError:
        pass

    candidates = []
    env_src = os.environ.get("DOC_VERSION_SRC", "").strip()
    if env_src:
        candidates.append(Path(env_src))
    candidates.append(Path.home() / "Documents" / "code" / "doc-version-mcp" / "src")
    candidates.append(Path(r"C:\Users\hjamet\Documents\code\doc-version-mcp\src"))

    found = False
    for candidate in candidates:
        if candidate and candidate.exists() and (candidate / "doc_version_mcp").is_dir():
            cand_str = str(candidate.resolve())
            if cand_str not in sys.path:
                sys.path.insert(0, cand_str)

            # Inclusion du site-packages d'un .venv éventuel dans le repo parent
            # pour résoudre les dépendances tierces (ex: fastmcp) si invoqué avec le python système
            root_dir = candidate.parent
            venv_site_packages = [
                root_dir / ".venv" / "Lib" / "site-packages",
                root_dir / ".venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages",
            ]
            for sp in venv_site_packages:
                if sp.exists() and str(sp.resolve()) not in sys.path:
                    sys.path.insert(0, str(sp.resolve()))

            try:
                import doc_version_mcp
                found = True
                break
            except ImportError:
                continue

    if not found:
        print(
            "Erreur: Impossible de localiser ou d'importer 'doc_version_mcp'.\n"
            "Veuillez installer doc-version-mcp en exécutant dans PowerShell :\n"
            "  irm https://raw.githubusercontent.com/hjamet/doc-version-mcp/main/install.ps1 | iex\n"
            "Ou définir la variable d'environnement DOC_VERSION_SRC pointant vers le dossier 'src'.",
            file=sys.stderr,
        )
        sys.exit(1)


_setup_environment()

# Moteur StealthRL colocalisé : get_diff_artifact réécrit automatiquement la prose modifiée via ce script
os.environ.setdefault("DOC_VERSION_STEALTH_SCRIPT", str(Path(__file__).resolve().with_name("stealth_rewriter.py")))

try:
    from doc_version_mcp.server import (
        commit_document,
        record_style_audit,
        get_diff_artifact,
        restore_commit,
        list_commits,
        prune_commits,
        record_git_pull_event,
    )
except ImportError as e:
    print(f"Erreur d'importation de doc_version_mcp.server: {e}", file=sys.stderr)
    print("Veuillez installer doc-version-mcp en exécutant dans PowerShell :", file=sys.stderr)
    print("  irm https://raw.githubusercontent.com/hjamet/doc-version-mcp/main/install.ps1 | iex", file=sys.stderr)
    sys.exit(1)


def cmd_commit(args):
    content = ""
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8", errors="replace")
    elif args.content:
        content = args.content

    style_audit = getattr(args, "style_audit", "")

    res = commit_document(
        target=args.target,
        message=args.message,
        content=content,
        author=args.author,
        mode=args.mode,
        is_pinned=args.pinned,
        style_audit=style_audit if style_audit else None,
    )
    print(res)


def cmd_diff(args):
    content = ""
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8", errors="replace")
    elif args.content:
        content = args.content

    allowed_terms = getattr(args, "allowed_terms", "")
    language = getattr(args, "language", "en")
    context_mode = getattr(args, "context_mode", "general")
    return_content = getattr(args, "return_content", False)
    run_stealth = getattr(args, "run_stealth", False)
    pdf_path = getattr(args, "pdf_path", None)
    res = get_diff_artifact(
        target=args.target,
        diff_explanation=args.explanation,
        content=content,
        from_commit_id=args.from_commit,
        to_commit_id=args.to_commit,
        mode=args.mode,
        brain_dir=args.brain_dir,
        artifact_name=args.artifact_name,
        allowed_terms=allowed_terms,
        language=language,
        context_mode=context_mode,
        return_content=return_content,
        run_stealth=run_stealth,
        pdf_path=pdf_path,
    )
    print(res)


def cmd_restore(args):
    res = restore_commit(
        commit_id=args.commit_id,
        target=args.target,
        dry_run=args.dry_run,
    )
    print(res)


def cmd_list(args):
    res = list_commits(
        target=args.target,
        limit=args.limit,
        mode=args.mode,
    )
    print(res)


def cmd_prune(args):
    res = prune_commits(
        ttl_days=args.ttl_days,
        max_size_mb=args.max_size_mb,
        keep_baselines=args.keep_baselines,
    )
    print(res)


def cmd_git_pull_event(args):
    res = record_git_pull_event(
        repo_path=args.repo_path,
        autostash=args.autostash,
    )
    print(res)


def cmd_record_style_audit(args):
    iterations = ""
    if getattr(args, "iterations_file", ""):
        iterations = Path(args.iterations_file).read_text(encoding="utf-8", errors="replace")
    elif getattr(args, "iterations", ""):
        iterations = args.iterations

    res = record_style_audit(
        commit_id=args.commit_id,
        target=args.target,
        iterations=iterations,
        summary=args.summary,
    )
    print(res)


def main():
    parser = argparse.ArgumentParser(description="doc-version-mcp CLI bridge")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: commit
    p_commit = subparsers.add_parser("commit", help="Commit snapshot to CAS")
    p_commit.add_argument("--target", required=True, help="Target file path or virtual identifier")
    p_commit.add_argument("--message", required=True, help="Commit message")
    p_commit.add_argument("--content", default="", help="Literal content")
    p_commit.add_argument("--content-file", default="", help="Path to content file")
    p_commit.add_argument("--author", default="agent", help="Author name")
    p_commit.add_argument("--mode", default="draft", choices=["paper", "draft"], help="Operating mode")
    p_commit.add_argument("--pinned", action="store_true", help="Pin snapshot")
    p_commit.add_argument("--style-audit", default="", help="Style audit JSON or summary string")
    p_commit.set_defaults(func=cmd_commit)

    # Subcommand: record-style-audit
    p_audit = subparsers.add_parser("record-style-audit", help="Record avoid-ai-writing style audit for a commit")
    p_audit.add_argument("--commit-id", required=True, help="Commit ID to attach style audit to")
    p_audit.add_argument("--target", default="", help="Target file path or virtual identifier")
    p_audit.add_argument("--iterations", default="", help="JSON string of iterations")
    p_audit.add_argument("--iterations-file", default="", help="Path to JSON file containing iterations")
    p_audit.add_argument("--summary", default="", help="Synthetic summary label")
    p_audit.set_defaults(func=cmd_record_style_audit)

    # Subcommand: diff
    p_diff = subparsers.add_parser("diff", help="Generate diff artifact")
    p_diff.add_argument("--target", required=True, help="Target file path or virtual identifier")
    p_diff.add_argument("--explanation", default="", help="Concise diff explanation")
    p_diff.add_argument("--content", default="", help="New literal content")
    p_diff.add_argument("--content-file", default="", help="Path to new content file")
    p_diff.add_argument("--from-commit", default="", help="Base commit ID (SHA-256)")
    p_diff.add_argument("--to-commit", default="", help="Target commit ID")
    p_diff.add_argument("--mode", default="draft", choices=["paper", "draft"], help="Operating mode")
    p_diff.add_argument("--brain-dir", default="", help="Brain directory to write artifact")
    p_diff.add_argument("--artifact-name", default="", help="Base name of output artifact")
    p_diff.add_argument("--allowed-terms", default="", help="Comma-separated list of whitelisted/arbitrated terms")
    p_diff.add_argument("--language", default="en", help="Language for style check (en, fr, auto, latex)")
    p_diff.add_argument("--context-mode", default="general", help="Style check context mode (general, technical)")
    p_diff.add_argument("--return-content", action="store_true", help="Include artifact_content in returned JSON")
    p_diff.add_argument("--run-stealth", dest="run_stealth", action="store_true", default=False, help="Force execution of StealthRL (disabled by default)")
    p_diff.add_argument("--no-stealth", "--no-run-stealth", dest="run_stealth", action="store_false", help="Disable StealthRL")
    p_diff.add_argument("--pdf-path", default=None, help="Explicit path to compiled PDF")
    p_diff.set_defaults(func=cmd_diff)

    # Subcommand: restore
    p_restore = subparsers.add_parser("restore", help="Restore document snapshot from CAS")
    p_restore.add_argument("--commit-id", required=True, help="Commit ID to restore (SHA-256)")
    p_restore.add_argument("--target", default="", help="Target file path to write to (optional)")
    p_restore.add_argument("--dry-run", action="store_true", help="Preview restore without modifying disk")
    p_restore.set_defaults(func=cmd_restore)

    # Subcommand: list
    p_list = subparsers.add_parser("list", help="List CAS commits")
    p_list.add_argument("--target", default="", help="Filter by target file path or identifier")
    p_list.add_argument("--limit", type=int, default=10, help="Maximum number of commits to list")
    p_list.add_argument("--mode", default="", help="Filter by mode (paper, draft)")
    p_list.set_defaults(func=cmd_list)

    # Subcommand: prune
    p_prune = subparsers.add_parser("prune", help="Prune expired CAS commits and regulate storage")
    p_prune.add_argument("--ttl-days", type=int, default=14, help="Retention period in days before pruning")
    p_prune.add_argument("--max-size-mb", type=int, default=500, help="Maximum storage size in MB")
    p_prune.add_argument("--no-keep-baselines", dest="keep_baselines", action="store_false", help="Do not protect pinned baselines")
    p_prune.set_defaults(keep_baselines=True, func=cmd_prune)

    # Subcommand: git-pull-event
    p_pull = subparsers.add_parser("git-pull-event", help="Safely sync git repo via pull --rebase and detect conflicts")
    p_pull.add_argument("--repo-path", required=True, help="Path to local git repository")
    p_pull.add_argument("--no-autostash", dest="autostash", action="store_false", help="Disable git autostash")
    p_pull.set_defaults(autostash=True, func=cmd_git_pull_event)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
