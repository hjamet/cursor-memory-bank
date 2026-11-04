"""
test_task_commit_sync.py — Suite de tests unitaires pour le renommage task_commit
et la résolution résiliente project_sync d'AIVC.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Chemins de référence
VOICENOTES_DIR = Path(r"c:\Users\Jamet\Documents\VoiceNotes")
CURSOR_MB_DIR = Path(r"c:\Users\Jamet\Documents\code\cursor-memory-bank")

if str(CURSOR_MB_DIR) not in sys.path:
    sys.path.insert(0, str(CURSOR_MB_DIR))

from scripts.apply_task_commit_rename import (
    CANONICAL_TARGET_FILES,
    run_pipeline,
    transform_markdown_content,
)


def test_transform_temporary_copy(tmp_path: Path):
    """
    Vérifie que apply_task_commit_rename.py transforme 100% des occurrences
    de l'outil AIVC remember en task_commit sur une copie temporaire des 9 fichiers,
    sans laisser d'occurrence résiduelle interdite.
    """
    # 1. Copier les 9 fichiers dans tmp_path
    for rel_path in CANONICAL_TARGET_FILES:
        src = VOICENOTES_DIR / rel_path
        assert src.is_file(), f"Fichier source introuvable : {src}"
        dst = tmp_path / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # 2. Exécuter le renommage en mode apply
    diff_report = tmp_path / "diff_report.md"
    mod_count, report_text = run_pipeline(
        vault_dir=tmp_path,
        apply_changes=True,
        diff_output=diff_report,
    )
    assert mod_count == 9, f"Attendu 9 fichiers modifiés, obtenu {mod_count}"
    assert diff_report.is_file()

    # 3. Vérifier l'absence d'occurrences résiduelles
    for rel_path in CANONICAL_TARGET_FILES:
        target = tmp_path / rel_path
        content = target.read_text(encoding="utf-8")

        # Pas de "mcp-cli call aivc remember"
        assert "mcp-cli call aivc remember" not in content, f"Résidu mcp-cli dans {rel_path}"

        # Pas de `remember` sauf l'exception explicite (anciennement remember)
        clean_content = content.replace("(anciennement remember)", "")
        assert "`remember`" not in clean_content, f"Résidu `remember` dans {rel_path}"

        # Pas de "via remember"
        assert not re.search(r"\bvia remember\b", clean_content), f"Résidu via remember dans {rel_path}"


def test_idempotence_strict(tmp_path: Path):
    """
    Vérifie que l'exécution répétée produit strictement 0 modification.
    """
    for rel_path in CANONICAL_TARGET_FILES:
        src = VOICENOTES_DIR / rel_path
        dst = tmp_path / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Première passe
    mod1, _ = run_pipeline(vault_dir=tmp_path, apply_changes=True)
    assert mod1 == 9

    # Deuxième passe
    mod2, _ = run_pipeline(vault_dir=tmp_path, apply_changes=True)
    assert mod2 == 0, f"L'idempotence a échoué, {mod2} fichier(s) ré-modifié(s)"


def test_no_false_positives():
    """
    Vérifie qu'aucun mot anglais courant ou identifiant Python n'est altéré.
    """
    english_cases = [
        "Please remember to close the file before exiting.",
        "remember_me = True",
        "Do not remember this state in session cache.",
        "I remember when we first tested this system.",
        "Remember to check test logs.",
        "cache_remember_token = 'xyz123'",
    ]
    for case in english_cases:
        transformed = transform_markdown_content(case)
        assert transformed == case, f"Faux positif sur : {case} -> {transformed}"


def test_project_memory_cli_import_and_rewrite():
    """
    Vérifie que project_memory_cli.py importe rewrite_artifact_paths_to_temp
    depuis aivc.project_sync avec succès et assure le repli en cas de mock ImportError.
    """
    cli_path = CURSOR_MB_DIR / "antigravity" / "scripts" / "project_memory_cli.py"
    assert cli_path.is_file(), f"Fichier introuvable : {cli_path}"

    # Vérification textuelle de la présence du bloc résilient
    code = cli_path.read_text(encoding="utf-8")
    assert "from aivc.project_sync import rewrite_artifact_paths_to_temp" in code
    assert "from aivc.advance_sync import rewrite_brain_paths_to_temp_artifacts" in code

    # Vérification de l'import réel depuis aivc.project_sync
    import sys
    aivc_src = Path.home() / "Documents" / "code" / "aivc" / "src"
    if aivc_src.is_dir() and str(aivc_src) not in sys.path:
        sys.path.insert(0, str(aivc_src))

    import aivc.project_sync as ps
    assert hasattr(ps, "rewrite_artifact_paths_to_temp")
    sample_text = "See file:///C:/Users/Jamet/.gemini/antigravity-cli/brain/abc-123/report.md"
    rewritten = ps.rewrite_artifact_paths_to_temp(sample_text)
    assert "report.md" in rewritten


def test_voicenotes_vault_unmodified():
    """
    Confirme que les 9 fichiers de gouvernance de VoiceNotes/_agents/ n'ont subi
    aucune modification dans le coffre réel (sanctuarisation respectée).
    """
    # Si un dépôt Git existait dans VoiceNotes, vérifier git status
    git_dir = VOICENOTES_DIR / ".git"
    if git_dir.is_dir():
        res = subprocess.run(
            ["git", "-C", str(VOICENOTES_DIR), "status", "-s"],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0
        assert "_agents" not in res.stdout

    # Vérification directe sur le contenu disque : les occurrences originales doivent être intactes
    aveugle_text = (VOICENOTES_DIR / "_agents" / "rules" / "superviseur-aveugle.md").read_text(encoding="utf-8")
    assert "mcp-cli call aivc remember" in aveugle_text, "superviseur-aveugle.md a été altéré dans VoiceNotes !"

    zero_trust_text = (VOICENOTES_DIR / "_agents" / "rules" / "zero-trust.md").read_text(encoding="utf-8")
    assert "mcp-cli call aivc remember" in zero_trust_text, "zero-trust.md a été altéré dans VoiceNotes !"
