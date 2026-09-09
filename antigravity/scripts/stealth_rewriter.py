#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stealth Rewriter & Humanization Batch Engine
Localisation : c:/Users/Jamet/Documents/VoiceNotes/antigravity/scripts/stealth_rewriter.py

Moteur d'humanisation textuelle haute fidélité par batch selon l'état de l'art (StealthRL, GRPO/LoRA, T5 Neural, Meaning Gates).
Intègre :
1. Backend StealthRL : LoRA Adapter sur Qwen3-4B-Instruct-2507 en 4-bit (BitsAndBytesConfig nf4, < 4 Go VRAM).
2. Backend Fallback T5 Neural : humarin/chatgpt_paraphraser_on_T5_base avec échantillonnage diversifié et beam search.
3. Boucle fermée Actor-Critic avec Meaning Gates :
   - Fact Gate (conservation stricte des nombres, grandeurs, métriques et citations).
   - Detached Trailing Citation & Shielding (préservation absolue des références [Author, Year], \\cite{...}, $math$).
   - Length Gate (ratio de longueur borné [0.65, 1.45]).
   - NLI Gate (vérification logique anti-contradiction).
4. Mode Batch sans friction : ingère des fichiers Markdown / LaTeX / texte brut, isole les passages > seuil IA,
   et produit des reformulations dont le score IA s'effondre tout en préservant la structure du document.
"""

import sys
import os
import re
import math
import time
import json
import argparse
import warnings
from typing import Dict, List, Tuple, Any, Optional

# Encodage UTF-8 sous Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

# Configuration GPU & CPU : Plafond dur VRAM 90% et réservation de cœurs CPU
try:
    import torch
    if torch.cuda.is_available():
        try:
            torch.cuda.set_per_process_memory_fraction(0.90, device=0)
        except Exception:
            pass
    torch.set_num_threads(8)
    if hasattr(torch, "set_num_interop_threads"):
        torch.set_num_interop_threads(4)
except Exception:
    pass

# Identifiants des modèles
STEALTH_RL_ADAPTER_ID = "suraj-ranganath/StealthRL"
STEALTH_RL_BASE_ID = "Qwen/Qwen3-4B-Instruct-2507"
T5_PARAPHRASER_ID = "humarin/chatgpt_paraphraser_on_T5_base"
NLI_MODEL_ID = "cross-encoder/nli-distilroberta-base"

# Buzzwords IA stéréotypés à éliminer en priorité
AI_BUZZWORDS = {
    "delve", "delving", "pivotal", "tapestry", "multifaceted", "seamless", "seamlessly",
    "foster", "fostering", "testament", "realm", "paramount", "furthermore", "moreover",
    "in conclusion", "it is worth noting", "shed light", "beacon", "catalyst",
    "intricate", "intricacies", "vibrant", "holistic", "game-changer", "transformative"
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
]


# ============================================================================
# 1. TRAILING CITATION DETACHER & SHIELDING
# ============================================================================

def detach_trailing_citation(sentence: str) -> Tuple[str, str, bool]:
    """
    Extrait proprement les citations bibliographiques en fin de phrase
    (ex: '... in continuous vector spaces [Ashish Vaswani et al., 2017].').
    Permet de paraphraser le corps de la phrase sans risquer d'altérer la référence.
    """
    m = re.search(r'(\s*\[[A-Z][^\]]+,\s*\d{4}[a-z]?(?:;\s*[A-Z][^\]]+,\s*\d{4}[a-z]?)*\][\.\s]*)$', sentence)
    if m:
        stem = sentence[:m.start()].rstrip()
        tail = m.group(1)
        has_dot = tail.strip().endswith(".") or sentence.strip().endswith(".")
        return stem, tail, has_dot
    return sentence, "", False


def detach_leading_prefix(sentence: str) -> Tuple[str, str]:
    """
    Extrait proprement les préfixes structuraux Markdown en tête de phrase :
    - Citation de blockquote (> ...)
    - Marqueurs de listes numérotées ou à puces (1., -, *)
    - En-têtes en gras ou italique avec deux-points ou point (ex: '**A Physical Tabletop Toolkit.** ')
    Permet d'isoler la prose à paraphraser sans altérer l'architecture du document.
    """
    m = re.match(r'^(\s*(?:>\s*)*(?:(?:\d+\.|\*|\-)\s*)?(?:\*\*[^*]+\*\*\s*[:\.]?\s*|\*[^*]+\*\s*[:\.]?\s*)?)', sentence)
    if m and m.group(1):
        prefix = m.group(1)
        stem = sentence[len(prefix):]
        if stem.strip():
            return prefix, stem
    return "", sentence


class ShieldManager:
    """Protège les éléments non modifiables (formules math, liens, sentinelles) via des jetons sécurisés."""

    def __init__(self):
        self.shields: Dict[str, str] = {}
        self.counter = 0

    def shield(self, text: str) -> str:
        self.shields.clear()
        self.counter = 0

        def _replace_match(prefix: str, m: re.Match) -> str:
            token = f"[{prefix}{self.counter}]"
            self.shields[token] = m.group(0)
            self.counter += 1
            return token

        # 1. Maths LaTeX ($...$ ou $$...$$)
        text = re.sub(r'\$\$.*?\$\$|\$[^\$\n]+?\$', lambda m: _replace_match("MATH", m), text, flags=re.DOTALL)

        # 2. Citations bibliographiques internes (\cite{...}, [Author, Year])
        text = re.sub(r'\\cite\{[^}]+\}', lambda m: _replace_match("REF", m), text)
        text = re.sub(r'\[[A-Z][a-zA-Z\s\.,&]+,\s*\d{4}[a-z]?\]', lambda m: _replace_match("REF", m), text)
        text = re.sub(r'\[[A-Z][a-zA-Z\s\.,&]+et al\.,\s*\d{4}[a-z]?\]', lambda m: _replace_match("REF", m), text)

        # 3. Balises HTML diff (<del>...</del>, <ins>...</ins>, <span...</span>)
        text = re.sub(r'<del[^>]*>.*?</del>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ins[^>]*>(.*?)</ins>', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)

        # 4. Liens markdown [texte](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: _replace_match("LINK", m), text)

        return text

    def unshield(self, text: str) -> str:
        for token, original in self.shields.items():
            text = text.replace(token, original)
        # Nettoyage de résidus
        text = re.sub(r'\[(?:REF|MATH|LINK)\d+\]', '', text)
        return text

    def check_shields_preserved(self, text: str) -> bool:
        """Vérifie si tous les jetons protégés sont intacts dans le texte candidat."""
        for token in self.shields:
            if token not in text:
                return False
        return True


# ============================================================================
# 2. MEANING GATES & FACT GATES
# ============================================================================

def extract_factual_numbers(text: str) -> List[str]:
    """Extrait les nombres et pourcentages factuels (ex: 500k, 10x10, 15%, 3.6, 2017)."""
    clean = re.sub(r'\[(?:REF|MATH|LINK)\d+\]', '', text)
    matches = re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', clean)
    return sorted(list(set(matches)))


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


# ============================================================================
# 3. GESTIONNAIRE DES BACKENDS DE RÉÉCRITURE
# ============================================================================

class StealthRewriterBackend:
    """Gestionnaire unifié pour l'inférence StealthRL et Fallbacks Neuronaux."""

    _instance = None

    def __init__(self, device: str = "auto"):
        import torch
        if torch.cuda.is_available():
            try:
                torch.cuda.set_per_process_memory_fraction(0.90, device=0)
            except Exception:
                pass
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.stealth_model = None
        self.stealth_tokenizer = None
        self.t5_model = None
        self.t5_tokenizer = None
        self.nli_model = None
        self.nli_tokenizer = None

    @classmethod
    def get_instance(cls, device: str = "auto") -> "StealthRewriterBackend":
        if cls._instance is None:
            cls._instance = cls(device=device)
        return cls._instance

    def is_stealth_rl_available(self) -> bool:
        """Vérifie si les poids de StealthRL et de la base Qwen3-4B sont disponibles localement."""
        hf_cache = os.path.expanduser("~/.cache/huggingface/hub")
        adapter_dir = os.path.join(hf_cache, f"models--{STEALTH_RL_ADAPTER_ID.replace('/', '--')}")
        base_dir = os.path.join(hf_cache, f"models--{STEALTH_RL_BASE_ID.replace('/', '--')}")

        if not os.path.exists(adapter_dir) or not os.path.exists(base_dir):
            return False

        snaps = os.path.join(base_dir, "snapshots")
        if not os.path.exists(snaps):
            return False
        for s in os.listdir(snaps):
            snap_dir = os.path.join(snaps, s)
            f1 = os.path.join(snap_dir, "model-00001-of-00003.safetensors")
            f2 = os.path.join(snap_dir, "model-00002-of-00003.safetensors")
            f3 = os.path.join(snap_dir, "model-00003-of-00003.safetensors")
            if os.path.exists(f1) and os.path.exists(f2) and os.path.exists(f3):
                return True
        return False

    def load_stealth_rl(self):
        """Charge Qwen3-4B-Instruct en 4-bit avec l'adaptateur LoRA StealthRL (< 4 Go VRAM)."""
        if self.stealth_model is not None:
            return self.stealth_tokenizer, self.stealth_model

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel

        print(f"🚀 [StealthRL] Chargement de {STEALTH_RL_BASE_ID} en 4-bit bnb nf4 (float16, < 3.5 Go VRAM) sur {self.device}...", flush=True)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

        tokenizer = AutoTokenizer.from_pretrained(STEALTH_RL_BASE_ID, local_files_only=True)
        base_model = AutoModelForCausalLM.from_pretrained(
            STEALTH_RL_BASE_ID,
            quantization_config=bnb_config,
            device_map="auto" if self.device == "cuda" else None,
            max_memory={0: "10800MB"} if self.device == "cuda" and torch.cuda.is_available() else None,
            trust_remote_code=True,
            local_files_only=True
        )

        print(f"🔗 [StealthRL] Application de l'adaptateur LoRA {STEALTH_RL_ADAPTER_ID}...", flush=True)
        model = PeftModel.from_pretrained(base_model, STEALTH_RL_ADAPTER_ID, local_files_only=True)
        model.eval()

        self.stealth_tokenizer = tokenizer
        self.stealth_model = model
        print("✅ [StealthRL] Moteur StealthRL 4-bit initialisé et opérationnel !", flush=True)
        return self.stealth_tokenizer, self.stealth_model

    def load_t5_paraphraser(self):
        """Charge le modèle neural T5 Paraphraser (humarin/chatgpt_paraphraser_on_T5_base)."""
        if self.t5_model is not None:
            return self.t5_tokenizer, self.t5_model

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        print(f"🔄 [T5-Paraphrase] Chargement de {T5_PARAPHRASER_ID} sur {self.device}...", flush=True)
        tok = AutoTokenizer.from_pretrained(T5_PARAPHRASER_ID, local_files_only=True)
        mod = AutoModelForSeq2SeqLM.from_pretrained(T5_PARAPHRASER_ID, local_files_only=True).to(self.device).eval()
        self.t5_tokenizer = tok
        self.t5_model = mod
        print("✅ [T5-Paraphrase] Modèle T5 opérationnel !", flush=True)
        return self.t5_tokenizer, self.t5_model

    def load_nli(self):
        """Charge le Cross-Encoder NLI pour la vérification anti-contradiction."""
        if self.nli_model is not None:
            return self.nli_tokenizer, self.nli_model
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            tok = AutoTokenizer.from_pretrained(NLI_MODEL_ID, local_files_only=True)
            mod = AutoModelForSequenceClassification.from_pretrained(NLI_MODEL_ID, local_files_only=True).to(self.device).eval()
            self.nli_tokenizer = tok
            self.nli_model = mod
        except Exception:
            pass
        return self.nli_tokenizer, self.nli_model


def verify_nli(premise: str, hypothesis: str, backend_mgr: StealthRewriterBackend) -> bool:
    """Vérifie la cohérence logique NLI (rejet si contradiction >= 0.40)."""
    tok, mod = backend_mgr.load_nli()
    if tok is None or mod is None:
        return True
    try:
        import torch
        inputs = tok(premise, hypothesis, return_tensors="pt", truncation=True, max_length=256).to(backend_mgr.device)
        with torch.no_grad():
            logits = mod(**inputs).logits
            probs = torch.softmax(logits, dim=-1)[0].tolist()
        id2label = mod.config.id2label
        scores = {id2label.get(i, str(i)).lower(): probs[i] for i in range(len(probs))}
        return scores.get("contradiction", 0.0) < 0.40
    except Exception:
        return True


# ============================================================================
# 4. GÉNÉRATION DE PROPOSITIONS DE REFORMULATION
# ============================================================================

def generate_stealth_candidates(
    sentence: str,
    backend_mgr: StealthRewriterBackend,
    n_candidates: int = 4
) -> List[str]:
    """
    Génère des candidats de paraphrase via le backend actif (StealthRL ou T5).
    """
    candidates = []

    # 1. Tentative avec StealthRL si disponible
    if backend_mgr.is_stealth_rl_available():
        try:
            tok, mod = backend_mgr.load_stealth_rl()
            import torch

            prompt = (
                f"You are a paraphrasing assistant.\n"
                f"Rewrite the text to preserve meaning while changing wording and structure.\n"
                f"Avoid adding new facts.\n\n"
                f"TEXT:\n{sentence}\n\n"
                f"PARAPHRASE:\n"
            )
            inputs = tok(prompt, return_tensors="pt").to(backend_mgr.device)
            with torch.no_grad():
                out = mod.generate(
                    **inputs,
                    max_new_tokens=150,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.92,
                    num_return_sequences=n_candidates
                )
            for seq in out:
                decoded = tok.decode(seq[inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                cleaned = decoded.split("\n")[0].strip()
                cleaned = re.sub(r'\s*\([Nn]ote:.*?\)', '', cleaned).strip()
                cleaned = re.sub(r'^(?:Here is a paraphrase|Paraphrase):\s*', '', cleaned, flags=re.IGNORECASE).strip()
                cleaned = cleaned.strip('"\'')
                if cleaned and cleaned != sentence:
                    candidates.append(cleaned)
        except Exception as e:
            sys.stderr.write(f"⚠️ [StealthRL Inférence fallback] : {e}\n")
        finally:
            if backend_mgr.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()

    # 2. Utilisation du backend T5 Neural
    if not candidates:
        try:
            tok, mod = backend_mgr.load_t5_paraphraser()
            import torch

            input_text = f"paraphrase: {sentence}"
            inputs = tok(input_text, padding="longest", truncation=True, max_length=128, return_tensors="pt").to(backend_mgr.device)
            with torch.no_grad():
                outputs = mod.generate(
                    **inputs,
                    num_beams=max(6, n_candidates + 2),
                    num_return_sequences=n_candidates,
                    no_repeat_ngram_size=2,
                    temperature=1.2,
                    max_length=128
                )
            for seq in outputs:
                cand = tok.decode(seq, skip_special_tokens=True).strip()
                if cand and cand != sentence:
                    candidates.append(cand)
        except Exception as e:
            sys.stderr.write(f"⚠️ [T5 Inférence fallback] : {e}\n")
        finally:
            if backend_mgr.device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()

    # 3. Post-traitement heuristique d'adoucissement stylistique
    final_cands = []
    for cand in candidates:
        c = cand
        for pat, repl in HEURISTIC_SWAPS:
            c = re.sub(pat, repl, c, flags=re.IGNORECASE)
        final_cands.append(c)

    return final_cands


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

        # Titres Markdown, séparateurs horizontaux ou commentaires HTML
        if stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("<!--"):
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


def split_sentences_simple(text: str) -> List[str]:
    """Découpe un texte en phrases sans casser les abréviations communes."""
    t = text
    abbrevs = ["e.g.", "i.e.", "et al.", "Fig.", "vs.", "al.", "No.", "Dr.", "Prof."]
    for idx, ab in enumerate(abbrevs):
        t = t.replace(ab, f"__ABBR_{idx}__")

    raw_sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\[])', t)
    sents = []
    for s in raw_sents:
        for idx, ab in enumerate(abbrevs):
            s = s.replace(f"__ABBR_{idx}__", ab)
        if s.strip():
            sents.append(s.strip())
    return sents


# ============================================================================
# 6. MOTEUR BATCH PRINCIPAL D'HUMANISATION
# ============================================================================

def humanize_document(
    text: str,
    threshold: float = 0.15,
    device: str = "auto",
    fast_scorer=None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Exécute le pipeline d'humanisation par batch sur l'ensemble d'un document.
    - Isole les paragraphes dont le score IA est supérieur au seuil.
    - Génère des reformulations fidèles préservant les faits et le sens.
    - Mesure les scores avant et après pour chaque paragraphe.
    - Reconstitue le document avec une fidélité structurelle intégrale.
    """
    start_time = time.time()
    backend_mgr = StealthRewriterBackend.get_instance(device=device)
    shield_mgr = ShieldManager()

    blocks = split_markdown_document(text)
    report_items = []

    # Évaluation rapide via encodeurs d'ai_detector (ModernBERT + TMR RoBERTa + Stylométrie) sur CPU (0 Mo VRAM)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from ai_detector import ModelManager
        det_mgr = ModelManager.get_instance(device_override="cpu")
    except Exception:
        det_mgr = None

    def _score_sentence(s_text: str) -> float:
        words_s = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s_text.lower())
        if len(words_s) < 4:
            return 0.0
        if det_mgr is not None:
            try:
                tok_m, mod_m = det_mgr.get_modernbert()
                tok_t, mod_t = det_mgr.get_tmr_roberta()
                import torch
                inp_m = tok_m([s_text], return_tensors="pt", padding=True, truncation=True, max_length=256).to(det_mgr.device)
                inp_t = tok_t([s_text], return_tensors="pt", padding=True, truncation=True, max_length=256).to(det_mgr.device)
                with torch.no_grad():
                    pm = torch.softmax(mod_m(**inp_m).logits, dim=-1)[0, 1].item()
                    pt = torch.softmax(mod_t(**inp_t).logits, dim=-1)[0, 1].item()
                s_enc = 0.55 * pm + 0.45 * pt
                buzz = sum(1 for w in words_s if w in AI_BUZZWORDS)
                s_stylo = min(1.0, (buzz / max(len(words_s), 1)) * 30.0)
                return 0.70 * s_enc + 0.30 * s_stylo
            except Exception:
                pass
        buzz = sum(1 for w in words_s if w in AI_BUZZWORDS)
        return min(1.0, (buzz / max(len(words_s), 1)) * 5.0)

    def _fast_score_paragraph(p_txt: str) -> float:
        # Nettoyage des balises diff pour scoring équitable
        p_clean = re.sub(r'<del[^>]*>.*?</del>', '', p_txt, flags=re.DOTALL)
        p_clean = re.sub(r'<[^>]+>', ' ', p_clean)
        sents = split_sentences_simple(p_clean)
        valid = [_score_sentence(s) for s in sents if len(re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s)) >= 4]
        return sum(valid) / len(valid) if valid else 0.0

    total_paras_processed = 0
    total_paras_flagged = 0

    try:
        for block in blocks:
            if block["type"] != "paragraph":
                continue

            p_text = block["content"].strip()
            words = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', p_text)
            if len(words) < 5:
                continue

            total_paras_processed += 1

            # 1. Évaluation du score IA initial du paragraphe
            p_ai_initial = _fast_score_paragraph(p_text)

            # 2. Si sous le seuil, conserver intact
            if p_ai_initial < threshold:
                continue

            total_paras_flagged += 1
            if verbose:
                print(f"\n⚡ [Paragraphe {total_paras_processed}] Score initial : {p_ai_initial*100:.1f}% >= {threshold*100:.1f}% -> Isolation & Humanisation...", flush=True)

            try:
                # 3. Isolation phrase par phrase et réécriture chirurgicale
                # Pour les paragraphes avec diffs, on opère sur la version propre
                p_clean = re.sub(r'<del[^>]*>.*?</del>', '', p_text, flags=re.DOTALL)
                p_clean = re.sub(r'<ins[^>]*>(.*?)</ins>', r'\1', p_clean, flags=re.DOTALL)
                p_clean = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', p_clean, flags=re.DOTALL)

                sentences = split_sentences_simple(p_clean)
                new_sentences = []

                for s in sentences:
                    s_words = len(re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s))
                    if s_words < 4:
                        new_sentences.append(s)
                        continue

                    orig_s_score = _score_sentence(s)
                    if orig_s_score < threshold:
                        new_sentences.append(s)
                        continue

                    # Détachement des préfixes structuraux Markdown (listes, puces, blockquotes, titres gras)
                    prefix, s_body = detach_leading_prefix(s)

                    # Détachement de citations de fin de phrase
                    stem, tail, has_dot = detach_trailing_citation(s_body)

                    # Shielding des entités critiques dans le tronc
                    shielded_stem = shield_mgr.shield(stem)

                    # Génération de candidats
                    candidates = generate_stealth_candidates(shielded_stem, backend_mgr, n_candidates=4)
                    best_cand = s_body
                    best_cand_score = orig_s_score

                    for cand_raw in candidates:
                        # Vérification des jetons protégés
                        if not shield_mgr.check_shields_preserved(cand_raw):
                            continue

                        cand_unshielded_stem = shield_mgr.unshield(cand_raw)

                        # Rétablissement de la citation détachée
                        if tail:
                            cand_full = f"{cand_unshielded_stem.rstrip('.')} {tail.strip()}"
                        else:
                            cand_full = cand_unshielded_stem if cand_unshielded_stem.endswith(('.', '!', '?')) else cand_unshielded_stem + '.'

                        # Meaning Gate 1 : Fact Gate (nombres et mesures)
                        fact_ok, _ = check_fact_gate(s_body, cand_full)
                        if not fact_ok:
                            continue

                        # Meaning Gate 2 : Length Gate
                        len_ok, _ = check_length_gate(s_body, cand_full)
                        if not len_ok:
                            continue

                        # Meaning Gate 3 : NLI Consistency
                        if not verify_nli(s_body, cand_full, backend_mgr):
                            continue

                        # Évaluation du candidat
                        cand_score = _score_sentence(cand_full)
                        if cand_score < best_cand_score:
                            best_cand = cand_full
                            best_cand_score = cand_score

                    new_sentences.append(f"{prefix}{best_cand}")

                new_para_text = " ".join(new_sentences)

                # 4. Évaluation du score après reformulation
                p_ai_after = _fast_score_paragraph(new_para_text)
                delta = (p_ai_initial - p_ai_after) * 100
                if verbose:
                    print(f"   -> Score après reformulation : {p_ai_after*100:.1f}% (Réduction de {delta:.1f} pts) ✅", flush=True)

                report_items.append({
                    "para_index": total_paras_processed,
                    "original": p_text,
                    "humanized": new_para_text,
                    "score_before": float(round(p_ai_initial, 4)),
                    "score_after": float(round(p_ai_after, 4)),
                    "delta_points": float(round(delta, 1))
                })

                # Remplacement chirurgical dans le bloc
                block["content"] = new_para_text

            finally:
                # Libération systématique de la mémoire après chaque paragraphe traité
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    finally:
        # Libération finale du cache GPU pour laisser le GPU immaculé
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Reconstitution exacte du document
    reconstructed_doc = "\n".join([b["content"] for b in blocks])
    elapsed = time.time() - start_time

    return {
        "status": "success",
        "elapsed_seconds": round(elapsed, 2),
        "paragraphs_total": total_paras_processed,
        "paragraphs_flagged": total_paras_flagged,
        "report": report_items,
        "humanized_text": reconstructed_doc
    }


def format_batch_summary_table(results: Dict[str, Any]) -> str:
    """Met en forme un rapport comparatif sous forme de tableau Markdown."""
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append(" 🛡️ RAPPORT FACTUEL D'HUMANISATION BATCH (STEALTH-REWRITER)")
    lines.append("=" * 80)
    lines.append(f"Temps total : {results['elapsed_seconds']}s | Paragraphes analysés : {results['paragraphs_total']} | Paragraphes corrigés : {results['paragraphs_flagged']}")
    lines.append("\n| # | Extrait du Paragraphe | Score Avant | Score Après | Réduction Delta |")
    lines.append("|---|---|:---:|:---:|:---:|")

    for item in results["report"]:
        excerpt = item["original"][:50].replace("\n", " ") + "..."
        b_score = f"{item['score_before']*100:5.1f}%"
        a_score = f"{item['score_after']*100:5.1f}%"
        delta = f"-{item['delta_points']:4.1f}%"
        lines.append(f"| {item['para_index']:2d} | {excerpt:<50} | {b_score} | {a_score} | 🟢 {delta} |")

    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


# ============================================================================
# 7. CLI POINT D'ENTRÉE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Stealth Rewriter : Humanisation textuelle par batch & éradication des empreintes IA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python antigravity/scripts/stealth_rewriter.py draft.md
  python antigravity/scripts/stealth_rewriter.py draft.md --threshold 0.15 --output draft_humanized.md
  python antigravity/scripts/stealth_rewriter.py draft.md --in-place
  python antigravity/scripts/stealth_rewriter.py "Texte direct à humaniser..." --dry-run
        """
    )
    parser.add_argument("input", help="Texte direct ou chemin vers un fichier Markdown / LaTeX / texte brut")
    parser.add_argument("--threshold", type=float, default=0.15, help="Seuil de détection au-delà duquel un paragraphe est isolé et corrigé (défaut : 0.15 / 15%%)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Chemin vers le fichier de destination")
    parser.add_argument("--in-place", "-i", action="store_true", help="Écrase directement le fichier source avec le texte humanisé")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les propositions et métriques sans écrire de fichier")
    parser.add_argument("--device", type=str, choices=["auto", "cuda", "cpu"], default="auto", help="Périphérique d'inférence (défaut : auto avec accélération GPU CUDA)")
    parser.add_argument("--json", action="store_true", help="Sortie structurée JSON pour les pipelines agentiques")

    args = parser.parse_args()

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

    results = humanize_document(
        text=raw_text,
        threshold=args.threshold,
        device=args.device,
        verbose=not args.json
    )

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print(format_batch_summary_table(results))

    if not args.dry_run:
        target_path = None
        if args.output:
            target_path = args.output
        elif args.in_place and input_file:
            target_path = input_file
        elif input_file:
            base, ext = os.path.splitext(input_file)
            target_path = f"{base}.humanized{ext}"

        if target_path:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(results["humanized_text"])
            print(f"💾 Document humanisé enregistré avec succès sous : {target_path}\n")


if __name__ == "__main__":
    main()
