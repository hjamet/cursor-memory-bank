#!/usr/bin/env python3
"""
Hook PreInvocation pour Antigravity : Détection et injection des répliques vocales brutes non filtrées.

Ce hook intercepte les échanges vocaux entre l'utilisateur et l'agent vocal intermédiaire (`talker`).
Lorsque le `talker` a répondu de manière autonome sans réveiller l'agent principal,
ou lorsqu'il a tronqué/résumé les propos de l'utilisateur (ligne `user:` sans timestamp),
le hook extrait chirurgicalement ces répliques exactes de l'utilisateur et leurs clips audio
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


def extract_filtered_user_utterances(entries: list, media: list = None) -> list:
    """
    Extrait uniquement les répliques [timestamp] user: "..." qui ont été :
    1. filtrées/résumées par une ligne synthétique user: "..." sans horodatage,
    OU
    2. suivies d'une réponse de l'agent vocal intermédiaire (`talker`).
    """
    if not entries:
        return []

    media = media or []
    user_entries = []
    media_idx = 0
    for idx, e in enumerate(entries):
        if e["speaker"] == "user" and not e["is_synthetic"]:
            audio_uri = media[media_idx].get("uri") if media_idx < len(media) else None
            user_entries.append((idx, e, audio_uri))
            media_idx += 1

    has_synthetic_summary = any(e["is_synthetic"] for e in entries)
    talker_indices = [idx for idx, e in enumerate(entries) if e["speaker"] == "talker"]

    selected = []
    for idx, e, audio_uri in user_entries:
        is_filtered_by_summary = has_synthetic_summary
        has_talker_reply_after = any(t_idx > idx for t_idx in talker_indices)

        if is_filtered_by_summary or has_talker_reply_after:
            selected.append({
                "timestamp": e["timestamp"],
                "text": e["text"],
                "audio_uri": audio_uri,
            })

    return selected


def build_compact_ephemeral_message(utterances: list) -> str:
    """
    Construit un message éphémère court et direct listant uniquement les répliques
    exactes d'Henri et leurs fichiers audio associés, sans dupliquer tout le bloc.
    """
    lines = [
        "[MODE VOCAL — RÉPLIQUES UTILISATEUR NON TRANSMISES OU RÉSUMÉES]",
        "Les répliques suivantes de l'utilisateur ont été filtrées, résumées ou traitées de façon autonome par l'agent vocal (`talker`) :",
        "",
    ]
    for u in utterances:
        ts_part = f"**[{u['timestamp']}]** " if u.get("timestamp") else ""
        lines.append(f"- {ts_part}\"{u['text']}\"")
        if u.get("audio_uri"):
            lines.append(f"  Clip audio : `{u['audio_uri']}`")
    lines.append("")
    lines.append("Consigne : Traite l'ensemble de ces demandes et propos réels de l'utilisateur ci-dessus.")

    return "\n".join(lines)


def find_new_user_steps(transcript_path: str, last_step_index: int | None = None) -> list:
    """
    Parcourt le transcript pour trouver tous les steps USER_INPUT postérieurs à last_step_index.
    Si last_step_index est None, considère qu'aucun step n'a encore été traité (retourne tous les steps USER_INPUT).
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return []

    cutoff = -1 if last_step_index is None else last_step_index
    user_steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                step_idx = data.get("step_index")
                if step_idx is not None and step_idx > cutoff:
                    user_steps.append(data)
                elif step_idx is None and last_step_index is None:
                    user_steps.append(data)

    return user_steps


def main():
    if sys.stdin:
        sys.stdin.reconfigure(encoding="utf-8")
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8")

    raw_input = sys.stdin.read()
    if not raw_input.strip():
        sys.stdout.write("{}\n")
        return

    payload = json.loads(raw_input)

    transcript_path = payload.get("transcriptPath", "")
    artifact_dir = payload.get("artifactDirectoryPath", "")
    last_user_input = payload.get("lastUserInput", "")

    # Privilégier transcript_full.jsonl dans le même répertoire s'il existe
    candidate_full = ""
    if transcript_path:
        dir_name = os.path.dirname(transcript_path)
        candidate_full = os.path.join(dir_name, "transcript_full.jsonl")

    target_path = candidate_full if (candidate_full and os.path.isfile(candidate_full)) else transcript_path

    # Lecture du curseur (last_step_index)
    cursor_file = None
    last_step_index = None
    if artifact_dir:
        scratch_dir = os.path.join(artifact_dir, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        cursor_file = os.path.join(scratch_dir, "voice_hook_cursor.json")
        if os.path.isfile(cursor_file):
            with open(cursor_file, "r", encoding="utf-8") as cf:
                cursor_data = json.load(cf)
                last_step_index = cursor_data.get("last_step_index")

    # Recherche des nouveaux steps USER_INPUT
    new_steps = []
    if target_path and os.path.isfile(target_path):
        new_steps = find_new_user_steps(target_path, last_step_index)

    # Si aucun step lu depuis le fichier mais que lastUserInput contient <talker_agent_context>
    if not new_steps and "<talker_agent_context>" in last_user_input:
        new_steps = [{"step_index": None, "content": last_user_input, "media": []}]

    if not new_steps:
        sys.stdout.write("{}\n")
        return

    all_filtered_utterances = []
    max_step_index = last_step_index

    for step in new_steps:
        step_idx = step.get("step_index")
        if step_idx is not None:
            if max_step_index is None or step_idx > max_step_index:
                max_step_index = step_idx

        content = step.get("content", "")
        media = step.get("media", [])
        if "<talker_agent_context>" not in content:
            continue

        _, entries = parse_talker_agent_context(content)
        filtered = extract_filtered_user_utterances(entries, media)
        if filtered:
            all_filtered_utterances.extend(filtered)

    # Mise à jour du curseur pour ne jamais re-scanner les steps déjà inspectés
    if cursor_file and max_step_index is not None:
        with open(cursor_file, "w", encoding="utf-8") as cf:
            json.dump({"last_step_index": max_step_index}, cf, indent=2)

    if not all_filtered_utterances:
        sys.stdout.write("{}\n")
        return

    ephemeral_msg = build_compact_ephemeral_message(all_filtered_utterances)
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
