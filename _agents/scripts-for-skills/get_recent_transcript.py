#!/usr/bin/env python3
"""
get_recent_transcript.py — Découpage temporel automatique et copie 1-clic.

Fonctionnalités :
- Détection automatique du fichier live_session.md local.
- Extraction chirurgicale des segments des N dernières minutes (défaut : 15 min).
- Support du format complet [YYYY-MM-DD HH:MM:SS] et legacy [HH:MM:SS].
- Écriture dans dernieres_15_minutes.md (local, hors coffre VoiceNotes).
- Copie automatique dans le presse-papier Windows avec intégrité UTF-8 parfaite.
- Support du mode --relative-to-last pour tester ou rejouer une session terminée.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import List, Tuple, Optional

# Assure l'encodage UTF-8 sous Windows pour la console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def copy_to_clipboard(text: str) -> bool:
    """
    Copie le texte dans le presse-papier Windows en préservant l'intégrité UTF-8 des caractères accentués.
    Utilise PowerShell Set-Clipboard via un fichier temporaire encodé en UTF-8.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
    try:
        tmp.write(text)
        tmp.close()
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"Set-Clipboard -Value (Get-Content -Raw -LiteralPath '{tmp.name}' -Encoding UTF8)",
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except Exception as exc:
        sys.stderr.write(f"[ATTENTION] Échec de copie dans le presse-papier : {exc}\n")
        return False
    finally:
        if os.path.exists(tmp.name):
            try:
                os.unlink(tmp.name)
            except OSError:
                pass


class TranscriptSegment:
    """Représente un segment individuel de transcription horodaté."""
    def __init__(self, timestamp: datetime, raw_timestamp_str: str, text: str):
        self.timestamp = timestamp
        self.raw_timestamp_str = raw_timestamp_str
        self.text = text.strip()

    def __repr__(self) -> str:
        return f"<Segment [{self.raw_timestamp_str}] {self.text[:30]}...>"


DEFAULT_LOCAL_SESSION_FILE = Path(__file__).resolve().parent / "live_session.md"
DEFAULT_LOCAL_EXTRACT_FILE = Path(__file__).resolve().parent / "dernieres_15_minutes.md"
ALT_CODE_SESSION_FILE = Path(r"C:\Users\hjamet\Documents\code\live-whisper\live_session.md")


def find_active_log_file(file_arg: Optional[str] = None, notes_dir: Optional[Path] = None) -> Path:
    """
    Localise le fichier de session actif :
    1. Chemin explicite si fourni (--file).
    2. live_session.md dans le répertoire de travail courant.
    3. live_session.md canonique dans le même dossier que le script :
       C:\\Users\\hjamet\\Documents\\VoiceNotes\\_agents\\scripts-for-skills\\live_session.md.
    4. live_session.md dans C:\\Users\\hjamet\\Documents\\code\\live-whisper\\live_session.md.
    5. Fallback legacy : Live Session *.md si explicitement recherché.
    """
    if file_arg:
        target = Path(file_arg).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Fichier de session spécifié introuvable : {target}")
        return target

    # 1. Vérification dans le répertoire courant
    cwd_candidate = Path.cwd().resolve() / "live_session.md"
    if cwd_candidate.exists() and cwd_candidate.stat().st_size > 0:
        return cwd_candidate

    # 2. Vérification dans le dossier canonique du script
    if DEFAULT_LOCAL_SESSION_FILE.exists() and DEFAULT_LOCAL_SESSION_FILE.stat().st_size > 0:
        return DEFAULT_LOCAL_SESSION_FILE

    # 3. Vérification de l'emplacement dans code/live-whisper/
    if ALT_CODE_SESSION_FILE.exists() and ALT_CODE_SESSION_FILE.stat().st_size > 0:
        return ALT_CODE_SESSION_FILE

    # Si DEFAULT_LOCAL_SESSION_FILE existe même s'il vient d'être initialisé (en-tête seul)
    if DEFAULT_LOCAL_SESSION_FILE.exists():
        return DEFAULT_LOCAL_SESSION_FILE

    # 3. Fallback éventuel sur notes_dir si spécifié explicitement
    if notes_dir and notes_dir.exists():
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_file = notes_dir / f"Live Session {today_str}.md"
        if today_file.exists() and today_file.stat().st_size > 0:
            return today_file

        session_files = sorted(
            notes_dir.glob("Live Session *.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if session_files:
            return session_files[0]

    raise FileNotFoundError(
        f"Aucun fichier de session local 'live_session.md' trouvé dans {Path.cwd()} ou {DEFAULT_LOCAL_SESSION_FILE}. "
        "Assurez-vous que le transcripteur live a bien été démarré."
    )


def parse_transcript_file(file_path: Path) -> List[TranscriptSegment]:
    """Parse le fichier markdown de session et extrait tous les segments horodatés."""
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier de session introuvable : {file_path}")

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Déduction de la date par défaut depuis le nom de fichier
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
    default_date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

    # Regex pour capturer l'horodatage en début de bloc
    timestamp_pattern = re.compile(
        r"^(?:\*\*\[|\[)(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}|\d{2}:\d{2}:\d{2})\](?:\*\*|\])?\s*(.*)$"
    )

    segments: List[TranscriptSegment] = []
    current_ts: Optional[datetime] = None
    current_ts_str: Optional[str] = None
    current_text_parts: List[str] = []

    for line in lines:
        match = timestamp_pattern.match(line.strip())
        if match:
            if current_ts is not None and current_text_parts:
                full_text = " ".join(current_text_parts).strip()
                if full_text:
                    segments.append(TranscriptSegment(current_ts, current_ts_str, full_text))

            raw_ts = match.group(1).strip()
            text_part = match.group(2).strip()

            if len(raw_ts) == 8:  # Format legacy HH:MM:SS
                dt_str = f"{default_date_str} {raw_ts}"
                current_ts = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            else:  # Format YYYY-MM-DD HH:MM:SS
                current_ts = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S")

            current_ts_str = raw_ts
            current_text_parts = [text_part] if text_part else []
        else:
            stripped = line.strip()
            if current_ts is not None and stripped and not stripped.startswith("---") and not stripped.startswith("#"):
                current_text_parts.append(stripped)

    if current_ts is not None and current_text_parts:
        full_text = " ".join(current_text_parts).strip()
        if full_text:
            segments.append(TranscriptSegment(current_ts, current_ts_str, full_text))

    return segments


def extract_recent_segments(
    segments: List[TranscriptSegment],
    minutes: float = 15.0,
    reference_time: Optional[datetime] = None,
    relative_to_last: bool = False,
) -> Tuple[List[TranscriptSegment], datetime, datetime]:
    """
    Filtre les segments sur la fenêtre temporelle demandée.
    Retourne (segments_filtrés, cutoff_time, ref_time).
    """
    if not segments:
        now = reference_time or datetime.now()
        return [], now - timedelta(minutes=minutes), now

    if reference_time is not None:
        ref_time = reference_time
    elif relative_to_last:
        ref_time = max(s.timestamp for s in segments)
    else:
        ref_time = datetime.now()

    cutoff_time = ref_time - timedelta(minutes=minutes)
    upper_bound = ref_time + timedelta(seconds=30)

    matched = [s for s in segments if cutoff_time <= s.timestamp <= upper_bound]
    matched.sort(key=lambda s: s.timestamp)
    return matched, cutoff_time, ref_time


def resolve_output_path(output_arg: Optional[str] = None) -> Path:
    """
    Résout le chemin d'écriture de l'extrait :
    1. Chemin explicite si spécifié (--output).
    2. Emplacement local canonique dans le même dossier que le script :
       C:\\Users\\hjamet\\Documents\\VoiceNotes\\_agents\\scripts-for-skills\\dernieres_15_minutes.md.
    """
    if output_arg:
        target = Path(output_arg).resolve()
    else:
        target = DEFAULT_LOCAL_EXTRACT_FILE

    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def generate_markdown_output(
    segments: List[TranscriptSegment],
    source_file: Path,
    cutoff_time: datetime,
    ref_time: datetime,
    minutes_requested: float,
) -> str:
    """Formate l'extrait au format Markdown local."""
    start_str = cutoff_time.strftime("%Y-%m-%d %H:%M:%S")
    end_str = ref_time.strftime("%Y-%m-%d %H:%M:%S")
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = len(segments)

    header = (
        f"---\n"
        f"type: live-extract\n"
        f"title: \"Extrait Live - Dernières {int(minutes_requested)} minutes\"\n"
        f"date: \"{now_iso}\"\n"
        f"window_start: \"{start_str}\"\n"
        f"window_end: \"{end_str}\"\n"
        f"minutes_requested: {minutes_requested}\n"
        f"segments_count: {count}\n"
        f"source_file: \"{source_file.name}\"\n"
        f"tags:\n"
        f"  - live-extract\n"
        f"---\n\n"
        f"# 🎙️ Extrait Live — Dernières {int(minutes_requested)} minutes\n\n"
        f"> **Plage horaire** : du `{start_str}` au `{end_str}`  \n"
        f"> **Fichier source** : `{source_file.resolve()}`  \n"
        f"> **Volume capturé** : {count} segment(s)\n\n"
        f"---\n\n"
        f"## 📝 Transcription Brute\n\n"
    )

    if not segments:
        body = "_Aucun segment transcrit trouvé dans cet intervalle temporel._\n"
    else:
        blocks = [f"**[{s.raw_timestamp_str}]** {s.text}" for s in segments]
        body = "\n\n".join(blocks) + "\n"

    return header + body


def main():
    parser = argparse.ArgumentParser(description="Extraction 1-clic des 15 dernières minutes de transcription live")
    parser.add_argument("--minutes", type=float, default=15.0, help="Nombre de minutes à isoler (défaut : 15)")
    parser.add_argument("--file", type=str, default=None, help="Chemin explicite du fichier de transcription live à lire (défaut : live_session.md local)")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Chemin de sortie du fichier markdown extrait (défaut : dernieres_15_minutes.md local)",
    )
    parser.add_argument(
        "--notes-dir",
        type=str,
        default=None,
        help=argparse.SUPPRESS,  # Obsolète : conservé pour rétro-compatibilité
    )
    parser.add_argument("--no-clipboard", action="store_true", help="Désactiver la copie dans le presse-papier")
    parser.add_argument("--reference-time", type=str, default=None, help="Heure de référence (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument(
        "--relative-to-last",
        action="store_true",
        help="Calculer les N minutes par rapport au dernier segment enregistré plutôt qu'à l'heure système",
    )

    args = parser.parse_args()

    # Résolution du fichier de session et de sortie
    notes_dir = Path(args.notes_dir) if args.notes_dir else None
    source_path = find_active_log_file(file_arg=args.file, notes_dir=notes_dir)
    out_path = resolve_output_path(args.output)

    print(f"[INFO] Lecture du fichier source : {source_path}")

    # Parsing
    segments = parse_transcript_file(source_path)
    print(f"[INFO] {len(segments)} segments trouvés au total dans la session.")

    # Détermination de l'heure de référence
    ref_dt = None
    if args.reference_time:
        try:
            ref_dt = datetime.strptime(args.reference_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            ref_dt = datetime.fromisoformat(args.reference_time)

    # Filtrage
    matched, cutoff_time, ref_time = extract_recent_segments(
        segments=segments,
        minutes=args.minutes,
        reference_time=ref_dt,
        relative_to_last=args.relative_to_last,
    )

    start_str = cutoff_time.strftime("%H:%M:%S")
    end_str = ref_time.strftime("%H:%M:%S")
    print(f"[INFO] Fenêtre temporelle retenue : {start_str} -> {end_str} ({args.minutes} min)")
    print(f"[INFO] Segments filtrés correspondants : {len(matched)}")

    # Construction du document Markdown
    md_content = generate_markdown_output(
        segments=matched,
        source_file=source_path,
        cutoff_time=cutoff_time,
        ref_time=ref_time,
        minutes_requested=args.minutes,
    )

    # Écriture dans le fichier de sortie
    out_path.write_text(md_content, encoding="utf-8")

    # Texte brut pour le presse-papier
    if matched:
        clipboard_text = "\n\n".join(f"[{s.raw_timestamp_str}] {s.text}" for s in matched)
    else:
        clipboard_text = f"[Aucun segment audio enregistré entre {start_str} et {end_str}]"

    # Copie dans le presse-papier
    if not args.no_clipboard:
        copy_to_clipboard(clipboard_text)

    print(
        f"\nExtrait des {int(args.minutes)} dernières minutes copié dans le presse-papier "
        f"et enregistré dans {out_path} !"
    )


if __name__ == "__main__":
    main()
