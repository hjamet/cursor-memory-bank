#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stealth Rewriter & Humanization Batch Engine (Doctrine FAIL-FAST Stricte)
Localisation : c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/stealth_rewriter.py

Moteur d'humanisation textuelle haute fidélité par paragraphe selon l'état de l'art (StealthRL GRPO, open-humanizer-4b, Meaning Gates).
Architecture FAIL-FAST stricte : ZÉRO flag de contournement, ZÉRO fallback silencieux, inférence exclusive sur Qwen3-4B en bfloat16 natif.
"""

import sys
import os
import re
import math
import time
import json
import argparse
import warnings
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Tuple, Any, Optional

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

import torch
if torch.cuda.is_available():
    vram_total_bytes = torch.cuda.get_device_properties(0).total_memory
    vram_total_gb = vram_total_bytes / (1024 ** 3)
    if vram_total_gb >= 10.5:
        torch.cuda.set_per_process_memory_fraction(0.90, device=0)
torch.set_num_threads(8)
if hasattr(torch, "set_num_interop_threads"):
    torch.set_num_interop_threads(4)

# Identifiants des modèles (FAIL-FAST : Modèle StealthRL exclusif, zéro fallback)
STEALTH_RL_ADAPTER_ID = "suraj-ranganath/StealthRL"
# OPEN_HUMANIZER_ADAPTER_ID est None par défaut car 'akhaliq/open-humanizer-4b' sur HF Hub
# a un adapter_model.safetensors corrompu (40 octets vide). Configurable via STEALTH_SECONDARY_ADAPTER.
OPEN_HUMANIZER_ADAPTER_ID = os.environ.get("STEALTH_SECONDARY_ADAPTER", None)
STEALTH_RL_BASE_ID = "Qwen/Qwen3-4B-Instruct-2507"
NLI_MODEL_ID = "cross-encoder/nli-distilroberta-base"

# Buzzwords IA stéréotypés à éliminer en priorité (SOTA 2025-2026 anti-GPTZero)
AI_BUZZWORDS = {
    "delve", "delving", "pivotal", "tapestry", "multifaceted", "seamless", "seamlessly",
    "foster", "fostering", "testament", "realm", "paramount", "furthermore", "moreover",
    "in conclusion", "it is worth noting", "shed light", "beacon", "catalyst",
    "intricate", "intricacies", "vibrant", "holistic", "game-changer", "transformative",
    "predominantly", "comparatively", "foundational", "underscores", "interplay",
    "showcase", "showcases"
}

# Remplacements déterministes d'adoucissement stylistique
HEURISTIC_SWAPS = [
    (r"\bFurthermore\b", "In addition"),
    (r"\bMoreover\b", "Also"),
    (r"\bIt is worth noting that\b", "Notably,"),
    (r"\bIn conclusion\b", "Overall"),
    (r"\bdelve into\b", "examine"),
    (r"\bdelves into\b", "examines"),
    (r"\bpivotal\b", "central"),
    (r"\btapestry of\b", "diversity of"),
    (r"\bmultifaceted\b", "complex"),
    (r"\bseamlessly\b", "smoothly"),
    (r"\bfoster\b", "support"),
    (r"\bfostering\b", "supporting"),
    (r"\ba testament to\b", "evidence of"),
    (r"\bparamount\b", "crucial"),
    (r"\bpredominantly\b", "largely"),
    (r"\bcomparatively\b", "relatively"),
    (r"\bfoundational\b", "fundamental"),
    (r"\bshowcase\b", "demonstrate"),
    (r"\bshowcases\b", "demonstrates"),
    (r"\s*--\s*", ", "),
    (r"\s*—\s*", ", "),
]


# ============================================================================
# 1. SHIELDING (MATHS, CITATIONS, LIENS)
# ============================================================================

_SHIELD_TOKEN_RE = re.compile(r"\[(?:REF|MATH|LINK|TEX|CMT)\d+\]")


class ShieldManager:
    """Protège les éléments non modifiables (formules math, liens, sentinelles) via des jetons sécurisés."""

    def __init__(self):
        self.shields: Dict[str, str] = {}
        self.counter = 0
        self.last_shielded_text: str = ""

    def shield(self, text: str) -> str:
        self.shields.clear()
        self.counter = 0

        def _replace_match(prefix: str, m: re.Match) -> str:
            token = f"[{prefix}{self.counter}]"
            self.shields[token] = m.group(0)
            self.counter += 1
            return token

        # 0. Commentaires LaTeX (% non échappé jusqu'en fin de ligne)
        text = re.sub(r'(?<!\\)%[^\n]*', lambda m: _replace_match("CMT", m), text)

        # 1. Maths LaTeX ($...$ ou $$...$$)
        text = re.sub(r'\$\$.*?\$\$|\$[^\$\n]+?\$', lambda m: _replace_match("MATH", m), text, flags=re.DOTALL)

        # 2. Citations bibliographiques internes (\cite{...}, [Author, Year])
        text = re.sub(r'\\cite[tp]?\*?\{[^}]+\}', lambda m: _replace_match("REF", m), text)

        # 2bis. Macros LaTeX avec options/arguments (\textsf{...}, \ref{...}, \looseness=-1, Table~\ref{...})
        text = re.sub(
            r'~?\\[a-zA-Z@]+\*?(?:\[[^\]]*\])*(?:\{(?:[^{}]|\{[^{}]*\})*\})*(?:=-?\d+(?:\.\d+)?)?',
            lambda m: _replace_match("TEX", m), text
        )
        # 2ter. Caractères échappés LaTeX (\%, \&, \_, \#, \$, contrôle d'espace "\ ", \\)
        text = re.sub(r'\\[%&_#$ ,;!{}\\]', lambda m: _replace_match("TEX", m), text)
        text = re.sub(r'\[[A-Z][a-zA-Z\s\.,&]+,\s*\d{4}[a-z]?\]', lambda m: _replace_match("REF", m), text)
        text = re.sub(r'\[[A-Z][a-zA-Z\s\.,&]+et al\.,\s*\d{4}[a-z]?\]', lambda m: _replace_match("REF", m), text)

        # 3. Balises HTML diff (<del>...</del>, <ins>...</ins>, <span...</span>)
        text = re.sub(r'<del[^>]*>.*?</del>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ins[^>]*>(.*?)</ins>', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)

        # 4. Liens markdown [texte](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: _replace_match("LINK", m), text)

        self.last_shielded_text = text
        return text

    def unshield(self, text: str) -> str:
        # Remplacement en une passe via regex précompilée O(N)
        text = _SHIELD_TOKEN_RE.sub(lambda m: self.shields.get(m.group(0), ""), text)
        return text

    def check_shields_preserved(self, text: str) -> bool:
        """Vérifie si tous les jetons protégés sont intacts dans le texte candidat."""
        for token in self.shields:
            if token not in text:
                return False
        return True

    def repair_candidate_shields(self, shielded_source: str, candidate: str) -> str:
        """
        Répare et normalise les jetons blindés dans un candidat généré avant vérification ShieldTokens.
        1. Normalise les variantes typographiques pour toutes les clés de self.shields :
           [ MATH0 ], [MATH 0], (MATH0), ou MATH0 (sans crochets) -> [MATH0].
        2. Restaure les [MATHk] numériques déblindés par le LLM ($50$ -> 50).
        3. Réinsère les [REFk] ou [TEXk] omis par le LLM.
        """
        repaired = candidate

        # 1. Normalisation typographique pour toutes les clés de self.shields
        for token in self.shields:
            name = token.strip("[]")  # ex: MATH0, REF1, TEX2
            m_parts = re.match(r'^([A-Z]+)(\d+)$', name)
            if m_parts:
                pfx, num = m_parts.group(1), m_parts.group(2)
                var_pat = rf'\[\s*{pfx}\s*{num}\s*\]|\(\s*{pfx}\s*{num}\s*\)'
                repaired = re.sub(var_pat, token, repaired)
                # Jeton nu sans crochets
                repaired = re.sub(rf'(?<!\[)\b{pfx}{num}\b(?!\])', token, repaired)
            else:
                repaired = re.sub(rf'\[\s*{re.escape(name)}\s*\]|\(\s*{re.escape(name)}\s*\)', token, repaired)
                repaired = re.sub(rf'(?<!\[)\b{re.escape(name)}\b(?!\])', token, repaired)

        # 2. Si un token [MATHk] vaut un simple nombre entre dollars (^\$(\d+(?:\.\d+)?\%?)\$$)
        # et manque dans repaired mais que le nombre nu y figure
        for token, raw_val in self.shields.items():
            if token.startswith("[MATH") and token not in repaired and token in shielded_source:
                m_num = re.match(r'^\$(\d+(?:\.\d+)?%?)\$$', raw_val.strip())
                if m_num:
                    bare_num = m_num.group(1)
                    esc_num = re.escape(bare_num)
                    repaired = re.sub(rf'(?<![\$\d])\b{esc_num}\b(?![\$\d])', token, repaired, count=1)

        # 3. Si un token [REFk] ou [TEXk] présent dans shielded_source a été omis par le LLM
        for token in self.shields:
            if (token.startswith("[REF") or token.startswith("[TEX")) and token in shielded_source and token not in repaired:
                is_end_of_sent = bool(re.search(rf'{re.escape(token)}\s*[\.;]', shielded_source))
                if is_end_of_sent and re.search(r'[\.;]\s*$', repaired):
                    repaired = re.sub(r'([\.;]\s*)$', rf' {token}\1', repaired, count=1)
                elif is_end_of_sent and re.search(r'[\.;]', repaired):
                    pos = max(repaired.rfind('.'), repaired.rfind(';'))
                    repaired = repaired[:pos] + f" {token}" + repaired[pos:]
                else:
                    src_tokens = _SHIELD_TOKEN_RE.findall(shielded_source)
                    inserted = False
                    if token in src_tokens:
                        idx_in_src = src_tokens.index(token)
                        if idx_in_src > 0 and src_tokens[idx_in_src - 1] in repaired:
                            prev_t = src_tokens[idx_in_src - 1]
                            repaired = repaired.replace(prev_t, f"{prev_t} {token}", 1)
                            inserted = True
                        elif idx_in_src < len(src_tokens) - 1 and src_tokens[idx_in_src + 1] in repaired:
                            next_t = src_tokens[idx_in_src + 1]
                            repaired = repaired.replace(next_t, f"{token} {next_t}", 1)
                            inserted = True
                    if not inserted:
                        repaired = f"{repaired.rstrip()} {token}."

        return repaired


# ============================================================================
# 2. MEANING GATES & FACT GATES
# ============================================================================

def extract_factual_numbers(text: str) -> List[str]:
    """Extrait les nombres et pourcentages factuels (ex: 500k, 10x10, 15%, 3.6, 2017)."""
    clean = re.sub(r'\[(?:REF|MATH|LINK|TEX|CMT)\d+\]', '', text)
    matches = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', clean)
    return sorted(list(set(matches)))


_WORD_TO_NUM = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "fifteen": "15", "twenty": "20",
    "twenty-six": "26", "thirty": "30", "forty": "40", "fifty": "50", "hundred": "100"
}
_NUM_TO_WORD = {v: k for k, v in _WORD_TO_NUM.items()}


def restore_spelled_numbers(original: str, candidate: str) -> str:
    """
    Si l'original contient un chiffre (ex: 30, 6) que le modèle a écrit en toutes lettres (thirty, six)
    ou omis devant son substantif d'ancrage (ex: '30 On models' -> 'On models'), rétablit le chiffre.
    """
    orig_nums = extract_factual_numbers(original)
    cand_nums = extract_factual_numbers(candidate)
    missing = [n for n in orig_nums if n not in cand_nums]
    out = candidate
    for m_num in missing:
        word = _NUM_TO_WORD.get(m_num)
        if word and re.search(rf'\b{re.escape(word)}\b', out, flags=re.IGNORECASE):
            out = re.sub(rf'\b{re.escape(word)}\b', m_num, out, count=1, flags=re.IGNORECASE)
            continue
        # Recherche du bigramme ou monogramme suivant immédiatement m_num dans original (ex: "30 On models")
        m_ctx2 = re.search(rf'\b{re.escape(m_num)}\s+([A-Za-zÀ-ÿ][\w-]*\s+[A-Za-zÀ-ÿ][\w-]*)', original)
        if m_ctx2 and re.search(rf'(?<!\d\s)\b{re.escape(m_ctx2.group(1))}\b', out):
            out = re.sub(rf'(?<!\d\s)\b({re.escape(m_ctx2.group(1))})\b', rf'{m_num} \1', out, count=1)
            continue
        m_ctx = re.search(rf'\b{re.escape(m_num)}\s+([A-Za-zÀ-ÿ][\w-]*)', original)
        if m_ctx and re.search(rf'(?<!\d\s)\b{re.escape(m_ctx.group(1))}\b', out):
            out = re.sub(rf'(?<!\d\s)\b({re.escape(m_ctx.group(1))})\b', rf'{m_num} \1', out, count=1)
    return out


def check_fact_gate(original: str, candidate: str) -> Tuple[bool, str]:
    """Fact Gate : Vérifie que tous les nombres clés de l'original sont conservés."""
    orig_nums = extract_factual_numbers(original)
    cand_nums = extract_factual_numbers(candidate)
    missing = [n for n in orig_nums if n not in cand_nums]
    if missing:
        return False, f"Chiffres manquants : {', '.join(missing)}"
    return True, "Chiffres préservés"


def check_length_gate(original: str, candidate: str, min_ratio: float = 0.35, max_ratio: float = 1.55) -> Tuple[bool, str]:
    """Length Gate : Empêche la troncature excessive ou le délayage artificiel (tolère la concision naturelle de StealthRL)."""
    w_orig = len(original.split())
    w_cand = len(candidate.split())
    if w_orig == 0:
        return True, "OK"
    ratio = w_cand / w_orig
    if ratio < min_ratio or ratio > max_ratio:
        return False, f"Ratio de longueur hors-limite ({ratio:.2f})"
    return True, f"Ratio OK ({ratio:.2f})"


def split_sentences_simple(text: str) -> List[str]:
    """Découpe un texte en phrases sans casser les abréviations communes."""
    t = text
    abbrevs = ["e.g.", "i.e.", "et al.", "Fig.", "vs.", "al.", "No.", "Dr.", "Prof."]
    for idx, ab in enumerate(abbrevs):
        t = t.replace(ab, f"__ABBR_{idx}__")

    raw_sents = re.split(r'(?:(?<=[.!?])|(?<=:D)|(?<=:\))|(?<=\^\^))\s+(?=[A-Z0-9"\[])', t)
    sents = []
    for s in raw_sents:
        for idx, ab in enumerate(abbrevs):
            s = s.replace(f"__ABBR_{idx}__", ab)
        if s.strip():
            sents.append(s.strip())
    return sents


def compute_gptzero_risk_score(text: str, ai_score: float = 0.0) -> Dict[str, Any]:
    """
    Calcule le risque de détection par GPTZero et classifieurs SOTA (2025-2026).
    Facteurs pénalisants basés sur la littérature (Xu et al. 2026, Wu et al. 2026, Rydell et al. 2026) :
    1. Faible Burstiness (CV des longueurs de phrases < 0.35) : uniformité typique de RLHF/DPO.
    2. Clauses participiales en fin de phrase (ex: ', leaving...', ', confounding...', ', yielding...').
    3. Doubles tirets ou tirets cadratins ('--' ou '—').
    4. Buzzwords IA (moreover, furthermore, delve, pivotal, realm, testament, predominantly, etc.).
    5. Score issu des encodeurs IA (ModernBERT, TMR RoBERTa, etc.).
    """
    sents = split_sentences_simple(text)
    word_counts = [len(re.findall(r'\b[a-zA-ZÀ-ÿ0-9-]+\b', s)) for s in sents if len(re.findall(r'\b[a-zA-ZÀ-ÿ0-9-]+\b', s)) > 0]

    if not word_counts:
        return {
            "total_risk": 1.0,
            "ai_score": ai_score,
            "burstiness_cv": 0.0,
            "mean_length": 0.0,
            "std_length": 0.0,
            "participial_clauses_count": 0,
            "participial_clauses": [],
            "dashes_count": 0,
            "buzzwords_count": 0,
            "buzzwords": [],
            "penalties": {"burstiness": 0.5, "participial": 0.0, "dashes": 0.0, "buzzwords": 0.0}
        }

    mean_l = sum(word_counts) / len(word_counts)
    if len(word_counts) > 1:
        variance = sum((x - mean_l) ** 2 for x in word_counts) / len(word_counts)
        std_l = math.sqrt(variance)
        cv = std_l / mean_l if mean_l > 0 else 0.0
    else:
        std_l = 0.0
        cv = 0.0

    # Pénalité de burstiness : GPTZero 4.1o exige une forte variance de longueur (CV >= 0.45)
    penalty_burstiness = max(0.0, (0.45 - cv) * 2.0) if len(word_counts) > 1 else 0.45

    # Détection des clauses participiales finales (regex: ',\s+[a-z]+ing\b[^.]*\.?$')
    participial_matches = []
    for s in sents:
        m = re.search(r',\s+([a-z]+ing\b[^.]*\.?)$', s.strip(), flags=re.IGNORECASE)
        if m:
            participial_matches.append(m.group(0))

    # Seule l'accumulation (> 1 par paragraphe) est pénalisée ; couper artificiellement en '. This yields...' déclenche GPTZero 4.1o
    penalty_participial = max(0, len(participial_matches) - 1) * 0.15

    # Doubles tirets ou tirets cadratins
    dashes = re.findall(r'--|—', text)
    penalty_dashes = len(dashes) * 0.30

    # Buzzwords IA
    words_clean = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', text.lower())
    found_buzzwords = [w for w in words_clean if w in AI_BUZZWORDS]
    penalty_buzzwords = len(found_buzzwords) * 0.20

    # Score total de risque
    total_risk = 0.40 * ai_score + penalty_burstiness + penalty_participial + penalty_dashes + penalty_buzzwords

    return {
        "total_risk": round(total_risk, 4),
        "ai_score": round(ai_score, 4),
        "burstiness_cv": round(cv, 4),
        "mean_length": round(mean_l, 2),
        "std_length": round(std_l, 2),
        "participial_clauses_count": len(participial_matches),
        "participial_clauses": participial_matches,
        "dashes_count": len(dashes),
        "buzzwords_count": len(found_buzzwords),
        "buzzwords": found_buzzwords,
        "penalties": {
            "burstiness": round(penalty_burstiness, 4),
            "participial": round(penalty_participial, 4),
            "dashes": round(penalty_dashes, 4),
            "buzzwords": round(penalty_buzzwords, 4),
        }
    }


# ============================================================================
# 3. GESTIONNAIRE DU BACKEND STEALTHRL (FAIL-FAST STRICT)
# ============================================================================

class StealthRewriterBackend:
    """Gestionnaire d'inférence StealthRL exclusif (Architecture FAIL-FAST stricte, zéro fallback)."""

    _instance = None

    def __init__(self, device: str = "auto", secondary_adapter_id: Optional[str] = None):
        self.vram_total_gb = 0.0
        if torch.cuda.is_available():
            vram_total_bytes = torch.cuda.get_device_properties(0).total_memory
            self.vram_total_gb = vram_total_bytes / (1024 ** 3)
            if self.vram_total_gb >= 10.5:
                torch.cuda.set_per_process_memory_fraction(0.90, device=0)
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.nli_device = "cpu" if (self.device == "cuda" and self.vram_total_gb < 10.5) else self.device
        self.stealth_model = None
        self.stealth_tokenizer = None
        self.secondary_adapter_id = secondary_adapter_id or OPEN_HUMANIZER_ADAPTER_ID
        self.has_open_humanizer = False
        self.nli_model = None
        self.nli_tokenizer = None

    @classmethod
    def get_instance(cls, device: str = "auto", secondary_adapter_id: Optional[str] = None) -> "StealthRewriterBackend":
        if cls._instance is None:
            cls._instance = cls(device=device, secondary_adapter_id=secondary_adapter_id)
        elif secondary_adapter_id is not None and cls._instance.secondary_adapter_id != secondary_adapter_id:
            cls._instance = cls(device=device, secondary_adapter_id=secondary_adapter_id)
        return cls._instance

    def _resolve_local_snapshot(self, repo_id: Optional[str], required_file: Any) -> Optional[str]:
        """
        Résout le chemin absolu du snapshot local contenant required_file s'il existe dans le cache HF.
        Doctrine FAIL-FAST stricte : si un fichier .safetensors requis est corrompu (< 1000 octets),
        lève immédiatement une RuntimeError au lieu de l'ignorer silencieusement.
        """
        if not repo_id:
            return None
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
        model_cache_dir = os.path.join(hf_cache, f"models--{repo_id.replace('/', '--')}")
        repo_dir = os.path.join(model_cache_dir, "snapshots")
        if not os.path.exists(repo_dir):
            return None

        req_files = (required_file,) if isinstance(required_file, str) else tuple(required_file)
        local_snaps = {}
        for snap in os.listdir(repo_dir):
            snap_path = os.path.join(repo_dir, snap)
            if os.path.isdir(snap_path):
                found = False
                for rf in req_files:
                    f_path = os.path.join(snap_path, rf)
                    if os.path.exists(f_path):
                        f_size = os.path.getsize(f_path)
                        if rf.endswith(".safetensors") and f_size < 1000:
                            raise RuntimeError(
                                f"[FAIL-FAST] Fichier .safetensors corrompu ou incomplet détecté pour '{repo_id}' : "
                                f"'{f_path}' (taille: {f_size} octets < 1000 octets). "
                                "Le snapshot HuggingFace est corrompu. Zéro fallback silencieux autorisé."
                            )
                        found = True
                        break
                if found:
                    local_snaps[snap] = snap_path

        if not local_snaps:
            return None

        return max(local_snaps.values(), key=lambda p: os.path.getmtime(p))

    def load_stealth_rl(self):
        """
        Charge Qwen3-4B-Instruct-2507 en bfloat16 natif (dès >= 7.5 GiB de VRAM, ex. RTX 2000 Ada 8 Go = 7.996 GiB
        ou RTX 3060 12 Go) avec l'adaptateur LoRA StealthRL et l'adaptateur secondaire akhaliq/open-humanizer-4b.
        """
        if self.stealth_model is not None:
            return self.stealth_tokenizer, self.stealth_model

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, AutoConfig
            from peft import PeftModel
        except ImportError as e:
            raise RuntimeError(
                f"[FAIL-FAST] Dépendances manquantes pour StealthRL (torch, transformers, peft) : {e}"
            ) from e

        if not torch.cuda.is_available():
            raise RuntimeError(
                "[FAIL-FAST] GPU CUDA indisponible. StealthRL (Qwen3-4B) requiert impérativement un GPU CUDA. "
                "Zéro fallback autorisé."
            )

        base_source = self._resolve_local_snapshot(STEALTH_RL_BASE_ID, "model.safetensors") or self._resolve_local_snapshot(STEALTH_RL_BASE_ID, ("model.safetensors", "model.safetensors.index.json")) or STEALTH_RL_BASE_ID
        adapter_source = self._resolve_local_snapshot(STEALTH_RL_ADAPTER_ID, "adapter_model.safetensors") or STEALTH_RL_ADAPTER_ID

        try:
            vram_total_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_total_gb = vram_total_bytes / (1024 ** 3)
            use_native_bf16 = vram_total_gb >= 7.5 and torch.cuda.is_bf16_supported()
            tokenizer = AutoTokenizer.from_pretrained(base_source, local_files_only=(base_source != STEALTH_RL_BASE_ID))
            cfg_obj = AutoConfig.from_pretrained(base_source, local_files_only=(base_source != STEALTH_RL_BASE_ID))
            if use_native_bf16:
                print(
                    f"🚀 [StealthRL] Chargement de {STEALTH_RL_BASE_ID} en bfloat16 natif sur cuda:0 (sans dégradation 4-bit NF4, VRAM={vram_total_gb:.2f} GiB)...",
                    file=sys.stderr,
                    flush=True
                )
                load_kwargs = {
                    "device_map": {"": 0},
                    "low_cpu_mem_usage": True,
                    "trust_remote_code": True,
                    "local_files_only": (base_source != STEALTH_RL_BASE_ID),
                    "dtype": torch.bfloat16,
                    "attn_implementation": "sdpa",
                }
            else:
                print(
                    f"🚀 [StealthRL] Chargement de {STEALTH_RL_BASE_ID} en 4-bit bnb nf4 (float16, < 3.5 Go VRAM) sur GPU CUDA...",
                    file=sys.stderr,
                    flush=True
                )
                load_kwargs = {
                    "device_map": "auto",
                    "max_memory": {0: "10800MB"},
                    "trust_remote_code": True,
                    "local_files_only": (base_source != STEALTH_RL_BASE_ID),
                    "dtype": torch.float16,
                    "attn_implementation": "sdpa",
                }
                if not hasattr(cfg_obj, "quantization_config") or cfg_obj.quantization_config is None:
                    load_kwargs["quantization_config"] = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True
                    )

            try:
                base_model = AutoModelForCausalLM.from_pretrained(
                    base_source,
                    **load_kwargs
                )
            except Exception as e_sdpa:
                if "attn_implementation" in load_kwargs:
                    print(f"⚠️ [StealthRL] Fallback attn_implementation 'sdpa' -> 'eager': {e_sdpa}", file=sys.stderr, flush=True)
                    load_kwargs["attn_implementation"] = "eager"
                    base_model = AutoModelForCausalLM.from_pretrained(
                        base_source,
                        **load_kwargs
                    )
                else:
                    raise

            print(f"🔗 [StealthRL] Application de l'adaptateur LoRA principal {STEALTH_RL_ADAPTER_ID} ('stealthrl')...", file=sys.stderr, flush=True)
            if os.path.isdir(adapter_source):
                sf_file = os.path.join(adapter_source, "adapter_model.safetensors")
                if os.path.exists(sf_file) and os.path.getsize(sf_file) < 1000:
                    raise RuntimeError(
                        f"[FAIL-FAST] Fichier safetensors corrompu détecté pour '{STEALTH_RL_ADAPTER_ID}' dans '{adapter_source}' : "
                        f"{sf_file} ({os.path.getsize(sf_file)} octets < 1000 octets)."
                    )
            model = PeftModel.from_pretrained(
                base_model,
                adapter_source,
                adapter_name="stealthrl",
                local_files_only=(adapter_source != STEALTH_RL_ADAPTER_ID)
            )

            sec_adapter_id = self.secondary_adapter_id if hasattr(self, "secondary_adapter_id") and self.secondary_adapter_id else OPEN_HUMANIZER_ADAPTER_ID
            if sec_adapter_id:
                oh_source = self._resolve_local_snapshot(sec_adapter_id, "adapter_model.safetensors") or sec_adapter_id
                if os.path.isdir(oh_source):
                    sf_file = os.path.join(oh_source, "adapter_model.safetensors")
                    if os.path.exists(sf_file) and os.path.getsize(sf_file) < 1000:
                        raise RuntimeError(
                            f"[FAIL-FAST] Fichier safetensors corrompu détecté pour l'adaptateur secondaire '{sec_adapter_id}' dans '{oh_source}' : "
                            f"{sf_file} ({os.path.getsize(sf_file)} octets < 1000 octets)."
                        )
                print(f"🔗 [StealthRL] Chargement de l'adaptateur LoRA secondaire '{sec_adapter_id}' ('open_humanizer')...", file=sys.stderr, flush=True)
                try:
                    model.load_adapter(
                        oh_source,
                        adapter_name="open_humanizer",
                        local_files_only=(oh_source != sec_adapter_id)
                    )
                    self.has_open_humanizer = True
                    print(f"🔗 [StealthRL] Adaptateur LoRA secondaire '{sec_adapter_id}' ('open_humanizer') chargé en VRAM !", file=sys.stderr, flush=True)
                except Exception as e_sec:
                    raise RuntimeError(
                        f"[FAIL-FAST] Échec critique du chargement de l'adaptateur secondaire '{sec_adapter_id}' ({oh_source}) : {e_sec}. "
                        "Zéro fallback silencieux autorisé."
                    ) from e_sec

            model.set_adapter("stealthrl")
            model.eval()
            torch.cuda.empty_cache()

            self.stealth_tokenizer = tokenizer
            self.stealth_model = model
            mode_label = "bfloat16 natif" if use_native_bf16 else "4-bit NF4"
            print(f"✅ [StealthRL] Moteur StealthRL ({mode_label}) initialisé et opérationnel !", file=sys.stderr, flush=True)
            return self.stealth_tokenizer, self.stealth_model
        except Exception as e:
            raise RuntimeError(
                f"[FAIL-FAST] Échec critique du chargement de StealthRL ({STEALTH_RL_BASE_ID} + {STEALTH_RL_ADAPTER_ID}) : {e}. "
                "Zéro fallback autorisé."
            ) from e

    def load_nli(self):
        """Charge le Cross-Encoder NLI pour la vérification anti-contradiction (FAIL-FAST)."""
        if self.nli_model is not None:
            return self.nli_tokenizer, self.nli_model
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            nli_src = self._resolve_local_snapshot(NLI_MODEL_ID, "config.json") or NLI_MODEL_ID
            tok = AutoTokenizer.from_pretrained(nli_src, local_files_only=(nli_src != NLI_MODEL_ID))
            mod = AutoModelForSequenceClassification.from_pretrained(
                nli_src, local_files_only=(nli_src != NLI_MODEL_ID)
            ).to(self.nli_device).eval()
            self.nli_tokenizer = tok
            self.nli_model = mod
            return self.nli_tokenizer, self.nli_model
        except Exception as e:
            raise RuntimeError(f"[FAIL-FAST] Échec du chargement du modèle NLI ({NLI_MODEL_ID}) : {e}") from e


class DesklibAIDetector:
    """Détecteur de risque IA (scoring de stylométrie et motifs RLHF SOTA) avec support par batch."""

    def __init__(self, device: str = "cuda"):
        self.device = device if (device == "cpu" or torch.cuda.is_available()) else "cpu"

    def predict_batch(self, texts: List[str]) -> List[float]:
        """Calcule le score de risque IA pour une liste de textes en une passe optimisée."""
        if not texts:
            return []
        with torch.inference_mode():
            scores = []
            for t in texts:
                risk_info = compute_gptzero_risk_score(t, ai_score=0.0)
                scores.append(float(round(risk_info["total_risk"], 4)))
            return scores

    def predict(self, text: str) -> float:
        return self.predict_batch([text])[0]


class NLIGate:
    """Porte de cohérence logique NLI avec inférence GPU par batch (doctrine FAIL-FAST)."""

    def __init__(self, backend_mgr: StealthRewriterBackend):
        self.backend_mgr = backend_mgr

    def check_batch(self, source: str, candidates: List[str]) -> List[Tuple[bool, float]]:
        """
        Vérifie la cohérence logique NLI en un seul batch GPU.
        Retourne pour chaque candidat : (is_valid: bool, contradiction_score: float).
        Un candidat est valide si score de contradiction < 0.40.
        """
        if not candidates:
            return []
        tok, mod = self.backend_mgr.load_nli()
        device = self.backend_mgr.nli_device
        premises = [source] * len(candidates)
        with torch.inference_mode():
            inputs = tok(
                premises,
                candidates,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=256
            ).to(device)
            logits = mod(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            id2label = mod.config.id2label
            contra_idx = None
            for idx, label in id2label.items():
                if "contra" in label.lower():
                    contra_idx = int(idx)
                    break
            if contra_idx is None:
                contra_idx = 0

            contra_scores = probs[:, contra_idx].tolist()
            results = []
            for score in contra_scores:
                is_valid = bool(score < 0.40)
                results.append((is_valid, float(round(score, 4))))
            return results

    def check(self, source: str, candidate: str) -> Tuple[bool, float]:
        res = self.check_batch(source, [candidate])
        return res[0]


class StealthRewriterPipeline:
    """Pipeline d'humanisation et réécriture furtive StealthRL."""

    def __init__(self, device: str = "auto", secondary_adapter_id: Optional[str] = None):
        self.backend = StealthRewriterBackend.get_instance(device=device, secondary_adapter_id=secondary_adapter_id)
        self.shield_mgr = ShieldManager()
        self.detector = DesklibAIDetector(device=self.backend.device)
        self.nli_gate = NLIGate(self.backend)

    def warmup(self):
        """Préchauffe les modèles en VRAM."""
        self.backend.load_stealth_rl()
        self.backend.load_nli()


def verify_nli(premise: str, hypothesis: str, backend_mgr: StealthRewriterBackend) -> bool:
    """Vérifie la cohérence logique NLI (rejet si contradiction >= 0.40)."""
    gate = NLIGate(backend_mgr)
    is_valid, _ = gate.check(premise, hypothesis)
    return is_valid


# ============================================================================
# 4. GÉNÉRATION DE PROPOSITIONS DE REFORMULATION PAR PARAGRAPHE (FAIL-FAST)
# ============================================================================

def break_participial_and_long_sentences(text: str) -> str:
    """
    Coupe les queues participiales de fin de phrase (', leaving...', ', confounding...', ', yielding...', etc.)
    et scinde les propositions subordonnées longues pour maximiser la burstiness (CV >= 0.45).
    """
    t = text
    for pat, repl in HEURISTIC_SWAPS:
        t = re.sub(pat, repl, t, flags=re.IGNORECASE)

    participial_rewrites = [
        (r',\s+leaving\s+([^.]+?)\s+(under-explored|unexamined|unstudied|untouched|unresolved)\.', r'. Consequently, \1 remains \2.'),
        (r',\s+leaving\s+([^.]+)\.', r'. This leaves \1.'),
        (r',\s+confounding\s+([^.]+)\.', r'. Such designs confound \1.'),
        (r',\s+yielding\s+([^.]+)\.', r'. This protocol yields \1.'),
        (r',\s+providing\s+([^.]+)\.', r'. These results provide \1.'),
        (r',\s+ensuring\s+that\s+([^.]+)\.', r'. This ensures that \1.'),
        (r',\s+ensuring\s+([^.]+)\.', r'. This ensures \1.'),
        (r',\s+highlighting\s+([^.]+)\.', r'. This highlights \1.'),
        (r',\s+allowing\s+([^.]+?)\s+to\s+([^.]+)\.', r'. Thus, \1 can \2.'),
        (r',\s+enabling\s+([^.]+?)\s+to\s+([^.]+)\.', r'. As a result, \1 can \2.'),
        (r',\s+demonstrating\s+([^.]+)\.', r'. This demonstrates \1.'),
        (r',\s+resulting\s+in\s+([^.]+)\.', r'. This results in \1.'),
        (r',\s+while\s+a\s+([^.]+?)\s+(generates|produces|creates)\s+([^.]+)\.', r'. In parallel, a \1 \2 \3.'),
        (r',\s+which\s+(highlights|demonstrates|enables|allows|ensures|reduces|provides|confirms|isolates|shows)\s+', r'. This \1 '),
        (r';\s+(however|consequently|therefore|meanwhile|nonetheless),\s+', lambda m: f". {m.group(1).capitalize()}, "),
    ]
    for pat, repl in participial_rewrites:
        t = re.sub(pat, repl, t, flags=re.IGNORECASE)

    def _split_generic_participial(m: re.Match) -> str:
        verb_ing = m.group(1)
        rest = m.group(2)
        v_low = verb_ing.lower()
        stem_map = {
            "isolating": "isolates",
            "quantifying": "quantifies",
            "comparing": "compares",
            "evaluating": "evaluates",
            "showing": "shows",
            "indicating": "indicates",
            "revealing": "reveals",
            "combining": "combines",
            "integrating": "integrates",
            "enforcing": "enforces",
            "producing": "produces",
            "generating": "generates",
            "creating": "creates",
            "making": "makes",
            "reducing": "reduces",
            "eliminating": "eliminates",
        }
        if v_low in stem_map:
            return f". This {stem_map[v_low]} {rest}"
        return f" and {verb_ing} {rest}"

    t = re.sub(r',\s+([a-zA-Z]+ing)\s+([^.]+\.)$', _split_generic_participial, t)
    return t


def generate_stealth_paragraph_candidates(
    paragraph: str,
    backend_mgr: StealthRewriterBackend,
    shield_mgr: ShieldManager,
    n_candidates: int = 2
) -> List[str]:
    """
    Génère des candidats de paragraphe entier en bfloat16 natif sur GPU via Qwen3-4B-Instruct-2507
    et l'adaptateur LoRA suraj-ranganath/StealthRL (et optionnellement akhaliq/open-humanizer-4b).
    """
    tok, mod = backend_mgr.load_stealth_rl()

    shielded_paragraph = shield_mgr.shield(paragraph)
    candidates: List[str] = []

    def _clean_generated_para(raw_text: str) -> str:
        c = raw_text.strip()
        c = re.sub(r'<think>.*?</think>', '', c, flags=re.DOTALL).strip()
        c = re.sub(r'^```(?:markdown|text)?\s*', '', c)
        c = re.sub(r'\s*```$', '', c).strip()
        c = re.sub(r'^(?:Here is (?:a|the) (?:rewritten|paraphrased) (?:paragraph|text):?|PARAPHRASE:?|REWRITTEN PARAGRAPH:?)\s*', '', c, flags=re.IGNORECASE).strip()
        c = c.strip('"\'')
        c = re.sub(r'\s*\([Nn]ote:.*?\)', '', c).strip()
        first_block = c.split("\n\n")[0].strip()
        lines = [line.strip() for line in first_block.split("\n") if line.strip() and not line.strip().lower().startswith(("note:", "(note:"))]
        c = " ".join(lines)
        for pat, repl in HEURISTIC_SWAPS:
            c = re.sub(pat, repl, c, flags=re.IGNORECASE)
        return c

    try:
        prompt_text_tokens = len(tok.encode(shielded_paragraph, add_special_tokens=False))
        dyn_max_tokens = max(80, min(512, int(prompt_text_tokens * 1.45) + 32))
        eos_ids = [tok.eos_token_id] if tok.eos_token_id is not None else []
        for stop_str in ["<|im_end|>", "<|endoftext|>", "\n\n"]:
            t_ids = tok.encode(stop_str, add_special_tokens=False)
            if len(t_ids) == 1 and t_ids[0] not in eos_ids:
                eos_ids.append(t_ids[0])

        mod.set_adapter("stealthrl")
        user_a = (
            "You are a paraphrasing assistant.\n"
            "Rewrite the text to preserve meaning while changing wording and structure.\n"
            "Vary sentence lengths sharply (mix short 6-10 word sentences with longer sentences). "
            "Keep every number, percentage, acronym, and bracketed token exact. Avoid adding new facts.\n\n"
            f"TEXT:\n{shielded_paragraph}\n\n"
            "PARAPHRASE:"
        )
        prompt_a = tok.apply_chat_template(
            [{"role": "user", "content": user_a}],
            tokenize=False,
            add_generation_prompt=True
        ) if hasattr(tok, "apply_chat_template") else user_a + "\n"
        inputs_a = tok(prompt_a, return_tensors="pt").to(backend_mgr.device)

        if n_candidates <= 3:
            # 1 passe GPU rapide avec StealthRL
            with torch.inference_mode():
                out_a = mod.generate(
                    **inputs_a,
                    max_new_tokens=dyn_max_tokens,
                    do_sample=True,
                    temperature=0.90,
                    top_p=0.95,
                    repetition_penalty=1.12,
                    eos_token_id=eos_ids,
                    pad_token_id=tok.eos_token_id,
                    num_return_sequences=n_candidates
                )
            for seq in out_a:
                dec = tok.decode(seq[inputs_a["input_ids"].shape[1]:], skip_special_tokens=True)
                cleaned = _clean_generated_para(dec)
                if cleaned and cleaned != paragraph:
                    candidates.append(cleaned)
                    split_cand = break_participial_and_long_sentences(cleaned)
                    if split_cand != cleaned and split_cand not in candidates:
                        candidates.append(split_cand)
        else:
            draws_a = n_candidates // 2
            draws_b = n_candidates - draws_a

            with torch.inference_mode():
                out_a = mod.generate(
                    **inputs_a,
                    max_new_tokens=dyn_max_tokens,
                    do_sample=True,
                    temperature=0.90,
                    top_p=0.95,
                    repetition_penalty=1.12,
                    eos_token_id=eos_ids,
                    pad_token_id=tok.eos_token_id,
                    num_return_sequences=draws_a
                )
            for seq in out_a:
                dec = tok.decode(seq[inputs_a["input_ids"].shape[1]:], skip_special_tokens=True)
                cleaned = _clean_generated_para(dec)
                if cleaned and cleaned != paragraph:
                    candidates.append(cleaned)
                    split_cand = break_participial_and_long_sentences(cleaned)
                    if split_cand != cleaned and split_cand not in candidates:
                        candidates.append(split_cand)

            if getattr(backend_mgr, "has_open_humanizer", False):
                # Régime B : open-humanizer sur le paragraphe entier
                mod.set_adapter("open_humanizer")
                if hasattr(tok, "apply_chat_template"):
                    sys_oh = (
                        "You are an expert editor. Rewrite the user's text so it reads like natural "
                        "human writing. Keep every fact, name, date, number, and bracketed token (like [REF0], [MATH0]) "
                        "exactly as given. Remove AI-sounding habits: hedging, filler connectives, trailing participial clauses, "
                        "and uniform sentence rhythm. Mix short direct sentences (6-10 words) with longer sentences. "
                        "Do not add information. Return only the rewritten text."
                    )
                    msgs_b = [
                        {"role": "system", "content": sys_oh},
                        {"role": "user", "content": shielded_paragraph}
                    ]
                    prompt_b = tok.apply_chat_template(
                        msgs_b,
                        tokenize=False,
                        add_generation_prompt=True
                    )
                    inputs_b = tok(prompt_b, return_tensors="pt").to(backend_mgr.device)
                else:
                    inputs_b = inputs_a
            else:
                # Régime B complémentaire : tirage StealthRL avec échantillonnage diversifié
                mod.set_adapter("stealthrl")
                inputs_b = inputs_a

            with torch.inference_mode():
                out_b = mod.generate(
                    **inputs_b,
                    max_new_tokens=dyn_max_tokens,
                    do_sample=True,
                    temperature=0.92,
                    top_p=0.95,
                    repetition_penalty=1.12,
                    eos_token_id=eos_ids,
                    pad_token_id=tok.eos_token_id,
                    num_return_sequences=draws_b
                )
            for seq in out_b:
                dec = tok.decode(seq[inputs_b["input_ids"].shape[1]:], skip_special_tokens=True)
                cleaned = _clean_generated_para(dec)
                if cleaned and cleaned != paragraph:
                    if cleaned not in candidates:
                        candidates.append(cleaned)
                    split_cand = break_participial_and_long_sentences(cleaned)
                    if split_cand != cleaned and split_cand not in candidates:
                        candidates.append(split_cand)

    except Exception as e:
        raise RuntimeError(f"[FAIL-FAST] Échec critique dans generate_stealth_paragraph_candidates : {e}") from e
    finally:
        if 'mod' in locals() and mod is not None and hasattr(mod, "set_adapter"):
            mod.set_adapter("stealthrl")
        if backend_mgr.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()

    if not candidates:
        raise RuntimeError(
            f"[FAIL-FAST] Aucun candidat de paragraphe produit par StealthRL pour : '{paragraph[:80]}...'"
        )

    return candidates


# ============================================================================
# 5. DÉCOUPAGE STRUCTUREL ROBUSTE DU DOCUMENT MARKDOWN
# ============================================================================

def split_markdown_document(text: str) -> List[Dict[str, Any]]:
    """
    Découpe un document Markdown en blocs structurés préservant byte-for-byte
    le frontmatter, les titres, le code, les images, les badges, les listes et les tableaux.
    Seuls les blocs 'paragraph' sont éligibles à l'humanisation.
    """
    blocks = []
    lines = text.split("\n")
    i = 0

    # 1. Frontmatter YAML
    if lines and lines[0].strip() == "---":
        fm_lines = [lines[0]]
        i = 1
        while i < len(lines):
            line = lines[i]
            fm_lines.append(line)
            i += 1
            if line.strip() == "---":
                break
        blocks.append({"type": "frontmatter", "content": "\n".join(fm_lines)})

    current_para = []

    def _flush_para():
        if current_para:
            para_text = "\n".join(current_para)
            if para_text:
                blocks.append({"type": "paragraph", "content": para_text})
            current_para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code blocks (``` ... ```)
        if stripped.startswith("```"):
            _flush_para()
            code_lines = [line]
            i += 1
            while i < len(lines):
                code_lines.append(lines[i])
                if lines[i].strip().startswith("```"):
                    i += 1
                    break
                i += 1
            blocks.append({"type": "code", "content": "\n".join(code_lines)})
            continue

        # Titres Markdown, séparateurs horizontaux, commentaires HTML ou en-têtes d'objet de courriel
        if stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("<!--") or re.match(r'^(?:Subject|Objet)\s*:', stripped, flags=re.IGNORECASE):
            _flush_para()
            blocks.append({"type": "header" if stripped.startswith("#") else "meta", "content": line})
            i += 1
            continue

        # Standalone images (![...](...) ou ![[...]])
        if re.match(r'^\s*!\[.*?\](?:\(.*?\)|\[\[.*?\]\])', stripped) or stripped.startswith("<img"):
            _flush_para()
            blocks.append({"type": "image", "content": line})
            i += 1
            continue

        # Badges HTML standalone (<span style="display:inline-block... ou Score IA)
        if stripped.startswith("<span") and "Score IA" in stripped:
            _flush_para()
            blocks.append({"type": "badge", "content": line})
            i += 1
            continue

        # Bibliographie académique standalone (- **[...]** : ... ou - [...] : ...)
        if re.match(r'^\s*[-*]\s+\*\*\[.*?\]\*\*\s*:', stripped) or re.match(r'^\s*[-*]\s+\[.*?\]\s*:', stripped):
            _flush_para()
            blocks.append({"type": "biblio", "content": line})
            i += 1
            continue

        # Citations de blockquote spéciales ou callouts (> [!NOTE] ...)
        if stripped.startswith("> [!"):
            _flush_para()
            bq_lines = [line]
            i += 1
            while i < len(lines) and (lines[i].strip().startswith(">") or lines[i].strip() == ""):
                bq_lines.append(lines[i])
                i += 1
            blocks.append({"type": "callout", "content": "\n".join(bq_lines)})
            continue

        # Tableaux Markdown (| ... |)
        if stripped.startswith("|") and stripped.endswith("|"):
            _flush_para()
            tbl_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            blocks.append({"type": "table", "content": "\n".join(tbl_lines)})
            continue

        # Ligne vide -> délimiteur de paragraphe
        if not stripped:
            _flush_para()
            blocks.append({"type": "blank", "content": ""})
            i += 1
            continue

        current_para.append(line)
        i += 1

    _flush_para()
    return blocks


# ============================================================================
# 6. MOTEUR PRINCIPAL D'HUMANISATION PAR PARAGRAPHE (BFLOAT16 NATIF)
# ============================================================================

MAX_GENERATION_ROUNDS = 2


def _strip_diff_markup(p_text: str) -> str:
    p_clean = re.sub(r'<del[^>]*>.*?</del>', '', p_text, flags=re.DOTALL)
    p_clean = re.sub(r'<ins[^>]*>(.*?)</ins>', r'\1', p_clean, flags=re.DOTALL)
    return re.sub(r'<span[^>]*>(.*?)</span>', r'\1', p_clean, flags=re.DOTALL)


def humanize_paragraph(
    p_text: str,
    backend_mgr: StealthRewriterBackend,
    shield_mgr: ShieldManager,
    n_candidates: int = 2,
    verbose: bool = True,
    label: str = "",
    is_subblock: bool = False
) -> Dict[str, Any]:
    """
    Réécrit un paragraphe de prose via StealthRL avec garantie de monotonicité stricte (score_after < score_before).
    Sous-découpe automatiquement si > 65 mots et plusieurs phrases pour maximiser le taux de succès sur GPU.
    Un candidat est valide s'il passe ShieldTokens (réparés déterministement), FactGate, LengthGate,
    StyleGate, NLIGate, et MonotonicityGate.
    """
    p_clean = _strip_diff_markup(p_text.strip())
    risk_before = compute_gptzero_risk_score(p_clean, 0.0)

    # Sous-découpage automatique si paragraphe long (> 85 mots et plusieurs phrases)
    sents = split_sentences_simple(p_clean)
    words_total = len(p_clean.split())
    if not is_subblock and words_total > 85 and len(sents) > 1:
        sub_blocks: List[str] = []
        curr_sents: List[str] = []
        curr_words = 0
        for s in sents:
            s_words = len(s.split())
            if curr_sents and (len(curr_sents) >= 3 or curr_words + s_words > 85):
                sub_blocks.append(" ".join(curr_sents))
                curr_sents = [s]
                curr_words = s_words
            else:
                curr_sents.append(s)
                curr_words += s_words
        if curr_sents:
            sub_blocks.append(" ".join(curr_sents))

        if len(sub_blocks) > 1:
            if verbose:
                print(
                    f"\n📦 [{label}] Sous-découpage automatique de {words_total} mots en {len(sub_blocks)} sous-blocs (<= 65 mots chacun)...",
                    file=sys.stderr, flush=True
                )
            reassembled_parts: List[str] = []
            any_changed = False
            total_rounds = 0
            all_rejections: List[str] = []

            for s_idx, sb in enumerate(sub_blocks, 1):
                # Vérification d'arrêt anticipé : si le paragraphe réassemblé est déjà <= 0.20
                if any_changed:
                    probe_text = " ".join(reassembled_parts + sub_blocks[s_idx-1:])
                    if compute_gptzero_risk_score(probe_text, 0.0)["total_risk"] <= 0.20:
                        if verbose:
                            print(f"   -> Risque global déjà <= 0.20 ({compute_gptzero_risk_score(probe_text, 0.0)['total_risk']:.3f}), arrêt anticipé !", file=sys.stderr, flush=True)
                        reassembled_parts.extend(sub_blocks[s_idx-1:])
                        break

                sb_risk = compute_gptzero_risk_score(sb, 0.0)["total_risk"]
                if sb_risk > 0.20:
                    sub_res = humanize_paragraph(
                        p_text=sb,
                        backend_mgr=backend_mgr,
                        shield_mgr=shield_mgr,
                        n_candidates=n_candidates,
                        verbose=verbose,
                        label=f"{label} [bloc {s_idx}/{len(sub_blocks)}]",
                        is_subblock=True
                    )
                    total_rounds += sub_res["rounds"]
                    all_rejections.extend(sub_res["gate_rejections"])
                    if sub_res["status"] == "VALIDÉ" and ((sub_res["risk_after"] < sub_res["risk_before"]) if sub_res["risk_before"] > 0.15 else (sub_res["risk_after"] <= 0.15)):
                        reassembled_parts.append(sub_res["humanized"])
                        any_changed = True
                    else:
                        reassembled_parts.append(sb)
                else:
                    if verbose:
                        print(f"   -> Bloc {s_idx} déjà propre (risque {sb_risk:.3f} <= 0.20)", file=sys.stderr, flush=True)
                    reassembled_parts.append(sb)

            reconstructed = " ".join(reassembled_parts)
            risk_after_full = compute_gptzero_risk_score(reconstructed, 0.0)["total_risk"]

            # Vérification de monotonicité sur le texte réassemblé
            orig_full_r = risk_before["total_risk"]
            if any_changed and ((risk_after_full < orig_full_r) if orig_full_r > 0.15 else (risk_after_full <= 0.15)):
                status = "VALIDÉ"
                humanized = reconstructed
                risk_after = risk_after_full
                ranked = [{"text": humanized, "risk": float(round(risk_after, 4))}]
            else:
                status = "REJET_GATES" if not any_changed else "REJET_MONOTONICITE"
                humanized = p_clean
                risk_after = risk_before["total_risk"]
                ranked = []

            if verbose:
                if status == "VALIDÉ":
                    print(f"   -> ✅ Réassemblage validé : risque {risk_before['total_risk']:.3f} -> {risk_after:.3f}", file=sys.stderr, flush=True)
                else:
                    print(f"   -> ⚠️ Réassemblage conservé original (risque {risk_before['total_risk']:.3f})", file=sys.stderr, flush=True)

            return {
                "original": p_clean,
                "humanized": humanized,
                "candidates_ranked": ranked,
                "status": status,
                "rounds": max(1, total_rounds),
                "gate_rejections": all_rejections,
                "risk_before": float(round(risk_before["total_risk"], 4)),
                "risk_after": float(round(risk_after, 4)),
            }

    valid: List[Tuple[float, str]] = []
    gate_rejections: List[str] = []
    nli_gate = NLIGate(backend_mgr)
    rounds = 0
    max_rounds = 1 if is_subblock else MAX_GENERATION_ROUNDS
    while not valid and rounds < max_rounds:
        rounds += 1
        if verbose:
            print(
                f"\n⚡ [{label}] Tirage {rounds}/{max_rounds} StealthRL "
                f"(risque initial {risk_before['total_risk']:.3f}, CV {risk_before['burstiness_cv']:.2f}, {len(p_clean.split())} mots)...",
                file=sys.stderr, flush=True
            )
        candidates = generate_stealth_paragraph_candidates(
            paragraph=p_clean, backend_mgr=backend_mgr, shield_mgr=shield_mgr, n_candidates=n_candidates
        )
        shielded_source = shield_mgr.last_shielded_text or shield_mgr.shield(p_clean)

        # Phase 1 : Portes CPU rapides (repair_candidate_shields, ShieldTokens, FactGate, LengthGate, StyleGate)
        surviving_cands: List[Tuple[str, Dict[str, Any]]] = []
        for cand_raw in candidates:
            # Réparation déterministe des jetons blindés avant vérification
            cand_raw = shield_mgr.repair_candidate_shields(shielded_source, cand_raw)
            if not shield_mgr.check_shields_preserved(cand_raw):
                gate_rejections.append("ShieldTokens")
                continue
            cand = shield_mgr.unshield(cand_raw)
            cand = restore_spelled_numbers(p_clean, cand)
            fact_ok, reason_fact = check_fact_gate(p_clean, cand)
            if not fact_ok:
                gate_rejections.append(f"FactGate ({reason_fact})")
                continue
            len_ok, reason_len = check_length_gate(p_clean, cand, min_ratio=0.50, max_ratio=1.45)
            if not len_ok:
                gate_rejections.append(f"LengthGate ({reason_len})")
                continue
            cand_risk = compute_gptzero_risk_score(cand, 0.0)
            if cand_risk["buzzwords_count"] > 0 or cand_risk["dashes_count"] > 0:
                gate_rejections.append(f"StyleGate (buzzwords={cand_risk['buzzwords']}, dashes={cand_risk['dashes_count']})")
                continue
            surviving_cands.append((cand, cand_risk))

        # Phase 2 : Porte GPU par batch (NLIGate sur tous les survivants en un seul appel)
        if surviving_cands:
            cand_texts = [c for c, _ in surviving_cands]
            nli_results = nli_gate.check_batch(p_clean, cand_texts)
            for (cand, cand_risk), (is_nli_ok, nli_score) in zip(surviving_cands, nli_results):
                if not is_nli_ok:
                    gate_rejections.append(f"NLIGate (Contradiction {nli_score:.2f})")
                    continue
                r = cand_risk["total_risk"]
                # Monotonicité stricte si risk_before > 0.15, ou maintien en zone verte (<= 0.15) si risk_before <= 0.15
                orig_r = risk_before["total_risk"]
                is_monotonic = (r < orig_r) if orig_r > 0.15 else (r <= 0.15)
                if not is_monotonic:
                    gate_rejections.append(f"MonotonicityGate (cand_risk {r:.3f} vs orig {orig_r:.3f})")
                    continue
                if cand not in [c for _, c in valid]:
                    valid.append((r, cand))

    valid.sort(key=lambda x: x[0])
    ranked = [{"text": c, "risk": float(round(r, 4))} for r, c in valid]
    orig_r = risk_before["total_risk"]
    if ranked and ((ranked[0]["risk"] < orig_r) if orig_r > 0.15 else (ranked[0]["risk"] <= 0.15)):
        status = "VALIDÉ"
        humanized = ranked[0]["text"]
        risk_after = ranked[0]["risk"]
    else:
        status = "REJET_GATES"
        humanized = p_clean
        risk_after = risk_before["total_risk"]

    if verbose:
        if status == "VALIDÉ":
            print(f"   -> ✅ {len(ranked)} candidat(s) valide(s), risque {risk_before['total_risk']:.3f} -> {risk_after:.3f}", file=sys.stderr, flush=True)
        else:
            print(f"   -> ❌ REJET_GATES après {rounds} tirages (motifs : {', '.join(gate_rejections)})", file=sys.stderr, flush=True)

    return {
        "original": p_clean,
        "humanized": humanized,
        "candidates_ranked": ranked,
        "status": status,
        "rounds": rounds,
        "gate_rejections": gate_rejections,
        "risk_before": float(round(risk_before["total_risk"], 4)),
        "risk_after": float(round(risk_after, 4)),
    }


def humanize_document(
    text: str,
    verbose: bool = True,
    secondary_adapter_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Exécute le pipeline d'humanisation sur TOUS les paragraphes de prose d'un document (>= 5 mots),
    sans pré-filtrage heuristique (Backend exclusif StealthRL Qwen3-4B-Instruct-2507 en bfloat16 natif).
    """
    start_time = time.time()
    shield_mgr = ShieldManager()
    backend_mgr = StealthRewriterBackend.get_instance(device="auto", secondary_adapter_id=secondary_adapter_id)

    blocks = split_markdown_document(text)
    report_items = []
    total_paras_processed = 0

    for block in blocks:
        if block["type"] != "paragraph":
            continue
        p_text = block["content"].strip()
        if len(re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', p_text)) < 5:
            continue
        total_paras_processed += 1
        res = humanize_paragraph(p_text, backend_mgr, shield_mgr, verbose=verbose, label=f"Paragraphe {total_paras_processed}")
        report_items.append({
            "para_index": total_paras_processed,
            "original": p_text,
            "humanized": res["humanized"],
            "score_before": res["risk_before"],
            "score_after": res["risk_after"],
            "delta_points": float(round((res["risk_before"] - res["risk_after"]) * 100, 1)),
            "status": res["status"]
        })
        block["content"] = res["humanized"]
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    reconstructed_doc = "\n".join([b["content"] for b in blocks])
    return {
        "status": "success",
        "elapsed_seconds": round(time.time() - start_time, 2),
        "paragraphs_total": total_paras_processed,
        "paragraphs_flagged": sum(1 for r in report_items if r["status"] == "VALIDÉ"),
        "report": report_items,
        "humanized_text": reconstructed_doc
    }


def rewrite_paragraphs_batch(
    paragraphs: List[str],
    pipeline: Optional[StealthRewriterPipeline] = None,
    target_score: float = 0.20,
    n_candidates: int = 2,
    mode: str = "paper",
    engine_mode: str = "cli",
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Réécrit un lot de paragraphes avec court-circuit rapide si le score initial est déjà <= target_score.
    Retourne la structure canonique attendue par le contrat d'interface.
    """
    t_start = time.perf_counter()
    if pipeline is None:
        pipeline = StealthRewriterPipeline()

    rewritten_list: List[str] = []
    stats_list: List[Dict[str, Any]] = []

    for idx, p in enumerate(paragraphs, 1):
        t_p0 = time.perf_counter()
        p_clean = _strip_diff_markup(p.strip())

        # Court-circuit si score initial <= target_score
        initial_score = pipeline.detector.predict(p_clean)
        if initial_score <= target_score:
            elapsed_ms = round((time.perf_counter() - t_p0) * 1000, 2)
            rewritten_list.append(p)
            stats_list.append({
                "status": "ALREADY_CLEAN",
                "changed": False,
                "score_before": float(round(initial_score, 4)),
                "score_after": float(round(initial_score, 4)),
                "attempts": 0,
                "gate_reason": "already_clean",
                "elapsed_ms": elapsed_ms,
                "candidates_ranked": [{"text": p, "risk": float(round(initial_score, 4))}]
            })
            if verbose:
                print(f"⚡ [P{idx}] Score initial {initial_score:.3f} <= cible {target_score:.3f} -> Déjà propre (court-circuit)", file=sys.stderr, flush=True)
            continue

        # Inférence de réécriture via humanize_paragraph
        res = humanize_paragraph(
            p_text=p,
            backend_mgr=pipeline.backend,
            shield_mgr=pipeline.shield_mgr,
            n_candidates=max(2, n_candidates),
            verbose=verbose,
            label=f"P{idx}"
        )
        elapsed_ms = round((time.perf_counter() - t_p0) * 1000, 2)
        is_mono_ok = (res["risk_after"] < res["risk_before"]) if res["risk_before"] > 0.15 else (res["risk_after"] <= 0.15)
        changed = bool(res["status"] == "VALIDÉ" and res["humanized"] != p_clean and is_mono_ok)
        final_text = res["humanized"] if changed else p
        rewritten_list.append(final_text)

        gate_reason = "valid" if changed else (", ".join(res["gate_rejections"]) if res["gate_rejections"] else "no_change")
        stats_list.append({
            "status": res["status"],
            "changed": changed,
            "score_before": float(round(res["risk_before"], 4)),
            "score_after": float(round(res["risk_after"], 4)),
            "attempts": res["rounds"],
            "gate_reason": gate_reason,
            "elapsed_ms": elapsed_ms,
            "candidates_ranked": res.get("candidates_ranked", [{"text": res["humanized"], "risk": res["risk_after"]}])
        })

    total_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
    return {
        "rewritten": rewritten_list,
        "stats": stats_list,
        "total_elapsed_ms": total_elapsed_ms,
        "engine_mode": engine_mode
    }


def humanize_paragraphs_json(
    in_path: str,
    out_path: str,
    target_score: float = 0.20,
    n_candidates: int = 2,
    mode: str = "paper",
    verbose: bool = True
) -> None:
    """
    Mode batch JSON : supporte le format dict {'paragraphs': [...]} ET le format liste [{'id', 'text'}].
    """
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    start_time = time.time()
    pipeline = StealthRewriterPipeline()

    if isinstance(data, dict) and "paragraphs" in data:
        t_score = float(data.get("target_score", target_score))
        n_cands = int(data.get("n_candidates", n_candidates))
        p_mode = str(data.get("mode", mode))
        res = rewrite_paragraphs_batch(
            paragraphs=data["paragraphs"],
            pipeline=pipeline,
            target_score=t_score,
            n_candidates=n_cands,
            mode=p_mode,
            engine_mode="cli",
            verbose=verbose
        )
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"💾 [StealthRL] {len(res['rewritten'])} paragraphe(s) traités en {time.time() - start_time:.1f}s -> {out_path}", file=sys.stderr, flush=True)

    elif isinstance(data, list):
        if not all(isinstance(it, dict) and "id" in it and "text" in it for it in data):
            raise ValueError(f"[FAIL-FAST] Format JSON invalide dans {in_path} : liste de {{'id', 'text'}} attendue.")
        results = []
        for it in data:
            t0 = time.perf_counter()
            p_clean = str(it["text"]).strip()
            initial_risk = compute_gptzero_risk_score(p_clean)
            initial_score = initial_risk["total_risk"]
            if initial_score <= target_score:
                results.append({
                    "id": it["id"],
                    "original": p_clean,
                    "humanized": p_clean,
                    "risk_before": float(round(initial_score, 4)),
                    "risk_after": float(round(initial_score, 4)),
                    "burstiness_cv_before": initial_risk["burstiness_cv"],
                    "burstiness_cv_after": initial_risk["burstiness_cv"],
                    "rounds": 0,
                    "status": "ALREADY_CLEAN",
                    "gate_rejections": [],
                    "candidates_ranked": [{"text": p_clean, "risk": float(round(initial_score, 4))}],
                    "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)
                })
                continue
            res = humanize_paragraph(it["text"], pipeline.backend, pipeline.shield_mgr, n_candidates=max(2, n_candidates), verbose=verbose, label=f"Segment {it['id']}")
            res["id"] = it["id"]
            res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            results.append(res)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 [StealthRL] {len(results)} segment(s) traités en {time.time() - start_time:.1f}s -> {out_path}", file=sys.stderr, flush=True)
    else:
        raise ValueError(f"[FAIL-FAST] Format JSON non reconnu dans {in_path}.")


def format_batch_summary_table(results: Dict[str, Any]) -> str:
    """Met en forme un rapport comparatif sous forme de tableau Markdown."""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append(" 🛡️ RAPPORT FACTUEL D'HUMANISATION BATCH (STEALTH-REWRITER - FAIL-FAST)")
    lines.append("=" * 80)
    lines.append(f"Temps total : {results['elapsed_seconds']}s | Paragraphes analysés : {results['paragraphs_total']} | Paragraphes corrigés : {results['paragraphs_flagged']}")
    lines.append("\n| # | Extrait du Paragraphe | Score Avant | Score Après | Delta | Statut |")
    lines.append("|---|---|:---:|:---:|:---:|:---:|")

    for item in results["report"]:
        excerpt = item["original"][:45].replace("\n", " ") + "..."
        b_score = f"{item['score_before']*100:5.1f}%"
        a_score = f"{item['score_after']*100:5.1f}%"
        delta_val = item['delta_points']
        delta_str = f"-{delta_val:4.1f}%" if delta_val > 0 else f"+{-delta_val:4.1f}%"
        status_label = "🟢 Validé" if item.get("status") == "VALIDÉ" else "⚠️ Rejet / Non amélioré"
        lines.append(f"| {item['para_index']:2d} | {excerpt:<45} | {b_score} | {a_score} | {delta_str} | {status_label} |")

    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


# ============================================================================
# 7. DÉMON HTTP LOCAL PERSISTANT (--serve)
# ============================================================================

def run_daemon_server(
    host: str = "127.0.0.1",
    port: int = 18777,
    idle_timeout: int = 900,
    default_mode: str = "paper",
    default_target_score: float = 0.20,
    default_n_candidates: int = 2
) -> None:
    """
    Lance le serveur démon HTTP persistant avec watchdog d'inactivité et verrou d'inférence GPU.
    """
    print(f"🚀 [StealthDaemon] Initialisation du pipeline GPU sur {host}:{port}...", file=sys.stderr, flush=True)
    pipeline = StealthRewriterPipeline()
    lock = threading.Lock()
    last_activity = time.time()
    stop_event = threading.Event()

    def _async_warmup():
        with lock:
            try:
                pipeline.warmup()
                print(f"✅ [StealthDaemon] Modèles chargés en VRAM, prêt à recevoir des requêtes !", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"⚠️ [StealthDaemon] Warmup différé ({e})", file=sys.stderr, flush=True)

    threading.Thread(target=_async_warmup, daemon=True).start()

    class StealthHTTPHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            nonlocal last_activity
            if self.path == "/health":
                idle_sec = round(time.time() - last_activity, 1)
                payload = {
                    "status": "ok",
                    "service": "stealth_rewriter",
                    "device": pipeline.backend.device,
                    "models_loaded": pipeline.backend.stealth_model is not None,
                    "idle_seconds": idle_sec,
                    "pid": os.getpid()
                }
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            nonlocal last_activity
            if self.path == "/rewrite":
                content_len = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_len).decode("utf-8")
                try:
                    req_data = json.loads(raw_body)
                except Exception as e:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Invalid JSON: {e}"}).encode("utf-8"))
                    return

                paragraphs = req_data.get("paragraphs", [])
                mode = req_data.get("mode", default_mode)
                target_score = float(req_data.get("target_score", default_target_score))
                n_candidates = int(req_data.get("n_candidates", default_n_candidates))

                last_activity = time.time()
                needs_gpu = any(
                    compute_gptzero_risk_score(str(p).strip())["total_risk"] > target_score
                    for p in paragraphs if p and str(p).strip()
                )
                if needs_gpu:
                    with lock:
                        res = rewrite_paragraphs_batch(
                            paragraphs=paragraphs,
                            pipeline=pipeline,
                            target_score=target_score,
                            n_candidates=n_candidates,
                            mode=mode,
                            engine_mode="daemon",
                            verbose=False
                        )
                else:
                    res = rewrite_paragraphs_batch(
                        paragraphs=paragraphs,
                        pipeline=pipeline,
                        target_score=target_score,
                        n_candidates=n_candidates,
                        mode=mode,
                        engine_mode="daemon",
                        verbose=False
                    )
                last_activity = time.time()

                body = json.dumps(res, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            elif self.path == "/shutdown":
                last_activity = time.time()
                payload = {"status": "shutting_down"}
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                print("🛑 [StealthDaemon] Requête /shutdown reçue, arrêt en cours...", file=sys.stderr, flush=True)
                threading.Thread(target=httpd.shutdown).start()

            else:
                self.send_response(404)
                self.end_headers()

    httpd = ThreadingHTTPServer((host, port), StealthHTTPHandler)

    def watchdog_loop():
        while not stop_event.is_set():
            time.sleep(2)
            if time.time() - last_activity > idle_timeout:
                print(f"⏰ [StealthDaemon] Arrêt automatique après {idle_timeout}s d'inactivité.", file=sys.stderr, flush=True)
                httpd.shutdown()
                break

    watchdog_thread = threading.Thread(target=watchdog_loop, daemon=True)
    watchdog_thread.start()

    print(f"👂 [StealthDaemon] Écoute sur http://{host}:{port} (timeout inactivité: {idle_timeout}s)", file=sys.stderr, flush=True)
    try:
        httpd.serve_forever()
    finally:
        stop_event.set()
        httpd.server_close()
        print("👋 [StealthDaemon] Démon arrêté proprement.", file=sys.stderr, flush=True)


# ============================================================================
# 8. CLI POINT D'ENTRÉE (APPEL UNIQUE SANS FLAG DE TRICHE)
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Stealth Rewriter : Humanisation textuelle par paragraphe en bfloat16 natif (sans flag de contournement)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python _agents/scripts-for-skills/stealth_rewriter.py draft.md
  python _agents/scripts-for-skills/stealth_rewriter.py "Texte direct à humaniser..."
  python _agents/scripts-for-skills/stealth_rewriter.py draft.md -o draft_humanized.md
  python _agents/scripts-for-skills/stealth_rewriter.py --paragraphs-json in.json -o out.json
  python _agents/scripts-for-skills/stealth_rewriter.py --serve --host 127.0.0.1 --port 18777 --idle-timeout 900
        """
    )
    parser.add_argument("input", nargs="?", default=None, help="Texte direct ou chemin vers un fichier Markdown / LaTeX / texte brut")
    parser.add_argument("-o", "--output", type=str, default=None, help="Chemin optionnel vers le fichier de destination")
    parser.add_argument("--output-json", type=str, default=None, help="Alias pour -o / --output")
    parser.add_argument("--paragraphs-json", type=str, default=None, help="Mode batch : fichier JSON [{'id', 'text'}] ou {'paragraphs': [...]} (sortie JSON dans -o)")
    parser.add_argument("--mode", type=str, default="paper", choices=["paper", "draft"], help="Mode de réécriture (défaut: paper)")
    parser.add_argument("--target-score", type=float, default=0.20, help="Score de risque cible (défaut: 0.20)")
    parser.add_argument("--n-candidates", type=int, default=2, help="Nombre de candidats par passe (défaut: 2)")
    parser.add_argument("--serve", action="store_true", help="Lance le démon HTTP persistant")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Hôte pour le démon HTTP (défaut: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=18777, help="Port pour le démon HTTP (défaut: 18777)")
    parser.add_argument("--idle-timeout", type=int, default=900, help="Délai d'inactivité en secondes avant arrêt (défaut: 900)")
    parser.add_argument("--secondary-adapter", type=str, default=None, help="Identifiant optionnel d'un adaptateur secondaire LoRA (défaut: None)")

    args = parser.parse_args()

    # Mode démon HTTP persistant
    if args.serve:
        run_daemon_server(
            host=args.host,
            port=args.port,
            idle_timeout=args.idle_timeout,
            default_mode=args.mode,
            default_target_score=args.target_score,
            default_n_candidates=args.n_candidates
        )
        return

    out_target = args.output or args.output_json

    if args.paragraphs_json:
        if not out_target:
            parser.error("--paragraphs-json exige -o/--output ou --output-json (fichier JSON de sortie).")
        humanize_paragraphs_json(
            in_path=args.paragraphs_json,
            out_path=out_target,
            target_score=args.target_score,
            n_candidates=args.n_candidates,
            mode=args.mode,
            verbose=True
        )
        return

    if not args.input:
        parser.error("input requis (texte ou fichier) hors modes --serve et --paragraphs-json.")

    raw_text = None
    input_file = None

    if os.path.isfile(args.input):
        input_file = args.input
        try:
            with open(args.input, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"Erreur de lecture du fichier '{args.input}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        raw_text = args.input

    if not raw_text or not raw_text.strip():
        print("Erreur : Aucun texte fourni à humaniser.", file=sys.stderr)
        sys.exit(1)

    try:
        results = humanize_document(
            text=raw_text,
            verbose=True,
            secondary_adapter_id=args.secondary_adapter
        )
    except RuntimeError as e:
        print(f"\n❌ [FAIL-FAST CRITIQUE] {e}\n", file=sys.stderr)
        sys.exit(1)

    print(format_batch_summary_table(results), file=sys.stderr)

    target_path = out_target if out_target else input_file
    if target_path:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(results["humanized_text"])
        print(f"💾 Document humanisé enregistré sous : {target_path}\n", file=sys.stderr)

    print(results["humanized_text"])


if __name__ == "__main__":
    main()
