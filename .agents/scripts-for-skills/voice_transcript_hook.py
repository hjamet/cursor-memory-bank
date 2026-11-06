#!/usr/bin/env python3
"""
Hook PreInvocation pour Antigravity : Détection et injection du transcript vocal brut non filtré.

Ce hook intercepte les échanges vocaux entre l'utilisateur et l'agent vocal intermédiaire (`talker`).
Lorsque le `talker` a répondu de manière autonome sans réveiller l'agent principal,
ou lorsqu'il a tronqué/résumé les propos de l'utilisateur (ligne `user:` sans timestamp),
le hook extrait le dialogue complet et les clips audio originaux depuis `transcript_full.jsonl`
et les injecte sous forme de message éphémère (`ephemeralMessage`) dans le contexte du modèle principal.
"""

import json
import os
import re
import sys


def parse_talker_agent_context(content: str):
    """
    Extrait et découpe le bloc <talker_agent_context>...</talker_agent_context>.
    """
    m = re.search(r"<talker_agent_context>(.*?)</talker_agent_context>", content, re.DOTALL)
    if not m:
        return None, []
    raw_tac = m.group(1).strip()

    pattern = re.compile(
        r'^(?:\[(?P<timestamp>[^\]]+)\]\s+)?(?P<speaker>user|talker):\s*"(?P<text>.*?)"(?=\s*(?:^\[|^(?:user|talker):|\Z))',
        re.MULTILINE | re.DOTALL,
    )

    entries = []
    for match in pattern.finditer(raw_tac):
        ts = match.group("timestamp")
        speaker = match.group("speaker")
        text = match.group("text").replace('\\"', '"')
        entries.append({
            "timestamp": ts,
            "speaker": speaker,
            "text": text,
            "is_synthetic": (ts is None and speaker == "user"),
        })
    return raw_tac, entries


def should_inject_unfiltered_transcript(entries: list) -> bool:
    """
    Vérifie si des messages ont été filtrés, tronqués ou accumulés sans réveil préalable.
    """
    if not entries:
        return False

    user_entries = [e for e in entries if e["speaker"] == "user"]
    user_timestamped = [e for e in user_entries if not e["is_synthetic"]]
    user_synthetic = [e for e in user_entries if e["is_synthetic"]]

    # 1. Filtre ou résumé synthétique généré par le talker (user: "..." sans timestamp)
    if user_synthetic:
        return True

    # 2. Multiples répliques utilisateur accumulées avant le réveil de l'agent
    if len(user_timestamped) > 1:
        return True

    # 3. Multiples réponses du talker dans le contexte du tour
    talker_entries = [e for e in entries if e["speaker"] == "talker"]
    if len(talker_entries) > 1:
        return True

    # 4. Échange intercalé : talker ayant répondu entre deux prises de parole utilisateur
    user_indices = [i for i, e in enumerate(entries) if e["speaker"] == "user"]
    talker_indices = [i for i, e in enumerate(entries) if e["speaker"] == "talker"]
    for t_idx in talker_indices:
        if user_indices and t_idx > user_indices[0] and t_idx < user_indices[-1]:
            return True

    return False


def build_ephemeral_message(raw_tac: str, entries: list, media: list) -> str:
    """
    Construit le message éphémère contenant le JSON brut exact.
    """
    dialogue = []
    media_idx = 0
    for e in entries:
        item = {
            "timestamp": e["timestamp"],
            "speaker": e["speaker"],
            "text": e["text"],
            "is_synthetic_summary": e["is_synthetic"],
        }
        if e["speaker"] == "user" and not e["is_synthetic"] and media_idx < len(media):
            item["audio_clip"] = media[media_idx].get("uri")
            media_idx += 1
        dialogue.append(item)

    summary_entries = [e["text"] for e in entries if e["is_synthetic"]]
    synthetic_summary = summary_entries[0] if summary_entries else None

    payload_data = {
        "dialogue": dialogue,
        "synthetic_summary": synthetic_summary,
        "media": media,
        "raw_talker_agent_context": raw_tac,
    }

    json_str = json.dumps(payload_data, ensure_ascii=False, indent=2)

    return (
        "[MODE VOCAL — TRANSCRIPT BRUT NON FILTRÉ]\n"
        "Des échanges vocaux ont été interceptés ou filtrés par l'agent vocal intermédiaire (`talker`) avant ce réveil.\n"
        "Voici le dialogue intégral exact (répliques horodatées `user` et `talker`) et les clips audio originaux :\n\n"
        "```json\n"
        f"{json_str}\n"
        "```\n\n"
        "Consigne : Traite la totalité des demandes et propos réels de l'utilisateur décrits ci-dessus, sans te limiter au résumé tronqué ou à la dernière phrase transmise par le talker."
    )


def find_latest_user_step(transcript_path: str):
    """
    Lit rapidement la fin du fichier transcript pour trouver le dernier step USER_INPUT.
    """
    if not os.path.isfile(transcript_path):
        return None

    file_size = os.path.getsize(transcript_path)
    # Lire au plus les 128 derniers Ko pour rester sous 1-2 ms
    chunk_size = min(file_size, 131072)
    with open(transcript_path, "rb") as f:
        f.seek(file_size - chunk_size)
        raw_bytes = f.read()

    lines = raw_bytes.decode("utf-8", errors="replace").splitlines()
    for l in reversed(lines):
        line = l.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                return data
        except Exception:
            continue

    # Repli si non trouvé dans les 128 Ko (fichier avec steps très volumineux)
    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        last_step = None
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    last_step = data
            except Exception:
                continue
        return last_step


def main():
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.stdout.write("{}\n")
            return
        payload = json.loads(raw_input)
    except Exception as e:
        sys.stderr.write(f"voice_transcript_hook error parsing stdin: {e}\n")
        sys.stdout.write("{}\n")
        return

    # Si c'est une invocation ultérieure d'un même tour (ex. appel d'outil), ignorer
    if payload.get("invocationNum", 1) > 1:
        sys.stdout.write("{}\n")
        return

    transcript_path = payload.get("transcriptPath", "")
    artifact_dir = payload.get("artifactDirectoryPath", "")
    last_user_input = payload.get("lastUserInput", "")

    # Privilégier transcript_full.jsonl dans le même répertoire s'il existe
    candidate_full = ""
    if transcript_path:
        dir_name = os.path.dirname(transcript_path)
        candidate_full = os.path.join(dir_name, "transcript_full.jsonl")

    target_path = candidate_full if (candidate_full and os.path.isfile(candidate_full)) else transcript_path

    latest_user_step = None
    if target_path and os.path.isfile(target_path):
        latest_user_step = find_latest_user_step(target_path)

    content = ""
    media = []
    step_idx = None

    if latest_user_step:
        content = latest_user_step.get("content", "")
        media = latest_user_step.get("media", [])
        step_idx = latest_user_step.get("step_index")

    # Si le step lu ne contient pas <talker_agent_context>, vérifier lastUserInput en secours
    if "<talker_agent_context>" not in content and "<talker_agent_context>" in last_user_input:
        content = last_user_input

    if "<talker_agent_context>" not in content:
        sys.stdout.write("{}\n")
        return

    # Gestion du curseur pour ne pas réinjecter sur le même step_index
    cursor_file = None
    if artifact_dir and step_idx is not None:
        scratch_dir = os.path.join(artifact_dir, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        cursor_file = os.path.join(scratch_dir, "voice_hook_cursor.json")
        if os.path.isfile(cursor_file):
            try:
                with open(cursor_file, "r", encoding="utf-8") as cf:
                    cursor_data = json.load(cf)
                    if cursor_data.get("last_step_index") == step_idx:
                        sys.stdout.write("{}\n")
                        return
            except Exception:
                pass

    raw_tac, entries = parse_talker_agent_context(content)
    if not should_inject_unfiltered_transcript(entries):
        sys.stdout.write("{}\n")
        return

    # Mettre à jour le curseur
    if cursor_file and step_idx is not None:
        try:
            with open(cursor_file, "w", encoding="utf-8") as cf:
                json.dump({"last_step_index": step_idx}, cf)
        except Exception:
            pass

    ephemeral_msg = build_ephemeral_message(raw_tac, entries, media)
    result = {
        "injectSteps": [
            {
                "ephemeralMessage": ephemeral_msg
            }
        ]
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
