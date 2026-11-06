#!/usr/bin/env python3
"""
Hook PreInvocation pour Antigravity : Détection des coupures/omissions vocales du talker
et injection des répliques intermédiaires user: dans <talker_agent_context>.

Approche Fail-Fast, ultra-légère et 0 token de bruit quand tout a été lu :
1. Ne déclenche la logique vocale que si le tour courant est un tour vocal (<talker_agent_context>).
2. Détecte si des phrases (>= 25 caractères) des PLANNER_RESPONSE d'Argon depuis l'avant-dernier
   USER_INPUT n'ont pas été lues par le talker (coupure '-' ou saut/omission) et injecte une alerte
   compacte plafonnée à 600 caractères max uniquement en cas d'omission réelle.
3. Extrait les répliques intermédiaires user: précédant la dernière réplique user: (en ignorant
   les phrases-tremplins pures comme "réveille argon", "réveille aaron", "crée le fichier",
   "enregistre ça dans un fichier") pour contrer la Règle 3 de <voice_instructions>.
"""

import json
import os
import re
import sys


WAKE_PHRASES_PATTERN = re.compile(
    r"\b(?:"
    r"r[eé]veille(?:r|z)?\s+(?:argon|aaron)|"
    r"cr[eé]e(?:r|z)?(?:\s+moi|\s*-\s*moi)?\s+le\s+fichier|"
    r"enregistre(?:r|z)?(?:\s+[cç]a)?\s+dans\s+un\s+fichier|"
    r"enregistre(?:r|z)?\s+le\s+fichier|"
    r"s\s*'?\s*il\s+te\s+pla[iî]t|"
    r"stp|merci|alors|du\s+coup|bon|ok|voil[aà]|euh"
    r")\b",
    re.IGNORECASE,
)


def clean_markdown(text: str) -> str:
    """Retire les liens Markdown et le formatage léger pour comparer le texte parlé."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    s = re.sub(r"[*_`#]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def normalize_text(text: str) -> str:
    """Normalise en minuscules, sans ponctuation et avec espaces unifiés."""
    s = clean_markdown(text).lower()
    s = s.replace("œ", "oe").replace("æ", "ae")
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip()


def is_pure_wake_phrase(text: str) -> bool:
    """
    Retourne True si la réplique user: est uniquement une phrase-tremplin de réveil
    ("Réveille Argon, s'il te plaît", "Crée le fichier", "Enregistre ça dans un fichier").
    """
    norm = normalize_text(text)
    if not norm:
        return True
    cleaned = WAKE_PHRASES_PATTERN.sub(" ", norm)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return len(cleaned) < 5


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
    Extrait les répliques [timestamp] user: "..." qui précèdent la dernière réplique user:
    (ou qui ont été remplacées par une ligne synthétique user: sans timestamp),
    en ignorant les phrases-tremplins pures ("réveille argon", "crée le fichier", etc.).
    """
    if not entries:
        return []

    media = media or []
    real_user_entries = [e for e in entries if e["speaker"] == "user" and not e["is_synthetic"]]
    if not real_user_entries:
        return []

    # Alignement des clips audio/wav attachés
    num_user = len(real_user_entries)
    num_media = len(media)
    offset = max(0, num_user - num_media) if num_media > 0 else num_user

    enriched_user_entries = []
    for i, e in enumerate(real_user_entries):
        audio_uri = None
        if num_media > 0 and i >= offset and (i - offset) < num_media:
            audio_uri = media[i - offset].get("uri")
        enriched_user_entries.append({
            "timestamp": e["timestamp"],
            "text": e["text"],
            "audio_uri": audio_uri,
        })

    has_synthetic_summary = any(e["is_synthetic"] for e in entries)
    if has_synthetic_summary:
        candidates = enriched_user_entries
    else:
        if len(enriched_user_entries) <= 1:
            return []
        candidates = enriched_user_entries[:-1]

    return [u for u in candidates if not is_pure_wake_phrase(u["text"])]


def is_sentence_read(sent: str, talker_norm: str, talker_words_set: set, has_cutoff: bool = False) -> bool:
    """
    Vérifie si une phrase d'Argon (>= 25 caractères) a été lue dans le texte concaténé des talker:.
    Considérée comme lue si >= 60 % de ses mots significatifs (>= 4 lettres) ou une sous-chaîne
    de 5 mots consécutifs apparaît dans talker_norm (et qu'en cas de coupure '-', la seconde moitié
    de la phrase n'a pas été tronquée).
    """
    if not talker_norm:
        return False

    sn = normalize_text(sent)
    words = sn.split()
    if not words:
        return True

    sig_words = [w for w in words if len(w) >= 4]

    # Si une ligne talker: se termine par '-', vérifier que la seconde moitié de la phrase a bien été prononcée
    if has_cutoff and len(sig_words) >= 4:
        second_half = sig_words[len(sig_words) // 2 :]
        second_half_ratio = sum(1 for w in second_half if w in talker_words_set) / len(second_half)
        if second_half_ratio < 0.50:
            return False

    # Sous-chaîne de 5 mots consécutifs présente dans talker_norm
    if len(words) >= 5:
        for k in range(len(words) - 4):
            if " ".join(words[k : k + 5]) in talker_norm:
                return True

    # Au moins 60 % des mots significatifs (>= 4 lettres) présents dans talker_words_set
    if not sig_words:
        return sn in talker_norm
    matched = sum(1 for w in sig_words if w in talker_words_set)
    return (matched / len(sig_words)) >= 0.60


def extract_unread_planner_sentences(planner_texts: list, entries: list) -> list:
    """
    Découpe les PLANNER_RESPONSE d'Argon depuis l'avant-dernier USER_INPUT en phrases
    et retourne celles (>= 25 caractères) qui n'ont pas été lues par le talker.
    """
    if not planner_texts:
        return []

    talker_lines = [e["text"] for e in entries if e["speaker"] == "talker" and e.get("text")]
    has_cutoff = any(t.rstrip().endswith("-") for t in talker_lines)
    talker_norm = normalize_text(" ".join(talker_lines))
    talker_words_set = set(talker_norm.split()) if talker_norm else set()

    unread = []
    for text in planner_texts:
        if not text or not text.strip():
            continue
        raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
        for raw_sent in raw_sentences:
            clean_sent = clean_markdown(raw_sent)
            if len(clean_sent) < 25:
                continue
            if not is_sentence_read(clean_sent, talker_norm, talker_words_set, has_cutoff):
                unread.append(clean_sent)

    return unread


def build_unread_alert(unread_sentences: list, max_len: int = 3500) -> str:
    """
    Construit l'alerte compacte de coupure/omission vocale plafonnée à 3500 caractères max.
    """
    if not unread_sentences:
        return ""

    prefix = (
        "[COUPURE / OMISSION VOCALE DÉTECTÉE : Henri n'a PAS entendu ces phrases "
        "de ton tour précédent (interruption ou oubli du talker). Redonne-lui "
        "uniquement les informations importantes manquantes : « "
    )
    suffix = " »]"
    available = max_len - len(prefix) - len(suffix)

    joined = " ".join(s.strip() for s in unread_sentences if s.strip())
    if len(joined) > available:
        joined = joined[: available - 1].rstrip() + "…"

    return f"{prefix}{joined}{suffix}"


def build_compact_ephemeral_message(utterances: list) -> str:
    """
    Construit un message éphémère court et direct listant uniquement les répliques
    intermédiaires exactes d'Henri et leurs fichiers audio associés.
    """
    if not utterances:
        return ""

    lines = [
        "[MODE VOCAL — RÉPLIQUES INTERMÉDIAIRES UTILISATEUR DANS <talker_agent_context>]",
        "Par dérogation à la Règle 3 de <voice_instructions>, réponds aussi à ces répliques d'Henri qui précèdent la dernière ligne du bloc :",
        "",
    ]
    for u in utterances:
        ts_part = f"**[{u['timestamp']}]** " if u.get("timestamp") else ""
        lines.append(f"- {ts_part}\"{u['text']}\"")
        if u.get("audio_uri"):
            lines.append(f"  Clip audio : `{u['audio_uri']}`")

    return "\n".join(lines)


def load_transcript_steps(transcript_path: str) -> list:
    """Charge tous les steps JSONL du fichier transcript."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return []

    steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            steps.append(json.loads(line))
    return steps


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

    candidate_full = ""
    if transcript_path:
        dir_name = os.path.dirname(transcript_path)
        candidate_full = os.path.join(dir_name, "transcript_full.jsonl")

    target_path = candidate_full if (candidate_full and os.path.isfile(candidate_full)) else transcript_path

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

    all_steps = load_transcript_steps(target_path)
    ui_positions = [i for i, s in enumerate(all_steps) if s.get("type") == "USER_INPUT"]

    # Si lastUserInput contient <talker_agent_context> et n'est pas encore le dernier USER_INPUT du transcript
    if "<talker_agent_context>" in last_user_input:
        last_recorded_content = all_steps[ui_positions[-1]].get("content", "") if ui_positions else ""
        if parse_talker_agent_context(last_recorded_content)[0] != parse_talker_agent_context(last_user_input)[0]:
            next_idx = ((all_steps[-1].get("step_index") or 0) + 1) if all_steps else 0
            all_steps.append({
                "type": "USER_INPUT",
                "step_index": next_idx,
                "content": last_user_input,
                "media": [],
            })
            ui_positions.append(len(all_steps) - 1)

    if not ui_positions:
        sys.stdout.write("{}\n")
        return

    curr_ui_pos = ui_positions[-1]
    curr_step = all_steps[curr_ui_pos]
    curr_step_idx = curr_step.get("step_index")

    # Si ce tour USER_INPUT a déjà été inspecté lors d'une invocation précédente du même tour
    if last_step_index is not None and curr_step_idx is not None and curr_step_idx <= last_step_index:
        sys.stdout.write("{}\n")
        return

    if cursor_file and curr_step_idx is not None:
        with open(cursor_file, "w", encoding="utf-8") as cf:
            json.dump({"last_step_index": curr_step_idx}, cf, indent=2)

    curr_content = curr_step.get("content", "")
    if "<talker_agent_context>" not in curr_content:
        sys.stdout.write("{}\n")
        return

    _, entries = parse_talker_agent_context(curr_content)
    if not entries:
        sys.stdout.write("{}\n")
        return

    # 1. Détection des phrases d'Argon non lues depuis l'avant-dernier USER_INPUT
    planner_texts = []
    if len(ui_positions) >= 2:
        prev_ui_pos = ui_positions[-2]
        planner_texts = [
            s.get("content", "")
            for s in all_steps[prev_ui_pos + 1 : curr_ui_pos]
            if s.get("type") == "PLANNER_RESPONSE" and s.get("content", "").strip()
        ]

    unread_sentences = extract_unread_planner_sentences(planner_texts, entries)
    unread_alert = build_unread_alert(unread_sentences)

    # 2. Extraction des répliques intermédiaires user: précédant la dernière réplique user:
    filtered_utterances = extract_filtered_user_utterances(entries, curr_step.get("media", []))
    utterances_msg = build_compact_ephemeral_message(filtered_utterances)

    parts = [p for p in (unread_alert, utterances_msg) if p]
    if not parts:
        sys.stdout.write("{}\n")
        return

    result = {
        "injectSteps": [
            {
                "ephemeralMessage": "\n\n".join(parts)
            }
        ]
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
