#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Detector Engine (5-Model Lightweight SOTA Bagging Ensemble)
Moteur Détecteur IA Multi-Modèles Haute Précision & GPU-Accelerated (< 500 Mo par modèle)
Localisation : c:/Users/Jamet/Documents/VoiceNotes/antigravity/scripts/ai_detector.py

Combine 5 acteurs algorithmiques SOTA complémentaires ultra-légers :
1. DeBERTa-v3 RAID SOTA (30%) : desklib/ai-text-detector-v1.01 (Benchmark RAID Leader)
2. ModernBERT Long-Context (25%) : GeorgeDrayson/modernbert-ai-detection-raid-mage (8192 tokens natifs, MAGE & RAID)
3. TMR RoBERTa Anti-Paraphrase (20%) : Oxidane/tmr-ai-text-detector (Focal Loss & Hard-Negative Mining sur RAID)
4. Fast-DetectGPT Zéro-Shot (15%) : Courbure conditionnelle analytique via EleutherAI/gpt-neo-125m (ou gpt2)
5. Stylométrie & Entropie (10%) : Burstiness CV, TTR, Maas, Entropie de Shannon, Buzzwords

Formule d'ensemble normalisée avec renormalisation bayésienne dynamique :
  P(AI) = (0.30*S_DeBERTa + 0.25*S_ModernBERT + 0.20*S_TMR + 0.15*S_FastDetect + 0.10*S_Stylo) / sum(W_actifs)
Seuil de conformité académique : P(AI) < 0.10 (10%)

Usage CLI ultra-simple :
  python antigravity/scripts/ai_detector.py "Texte direct à analyser..."
  python antigravity/scripts/ai_detector.py chemin/vers/fichier.tex (ou .md)
  python antigravity/scripts/ai_detector.py file.md --json
"""

import sys
import os
import re
import math
import json
import argparse
import warnings
from typing import Dict, List, Tuple, Any, Optional

# Assurer l'encodage UTF-8 sous Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suppression préventive des warnings et messages verbeux
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

# Contournement préventif du bug Dynamo / torch.compile sur Python 3.12+ (requis pour ModernBERT)
try:
    import torch
    if hasattr(torch, "compile"):
        def _safe_compile(*args, **kwargs):
            if args and callable(args[0]):
                return args[0]
            return lambda fn: fn
        try:
            @torch.compile
            def _dummy_compile_test(x): return x
        except Exception:
            torch.compile = _safe_compile
except Exception:
    pass

try:
    import transformers
    transformers.logging.set_verbosity_error()
except Exception:
    pass

# Identifiants des modèles Hugging Face (< 500 Mo chacun)
DEBERTA_RAID_ID = "desklib/ai-text-detector-v1.01"
MODERNBERT_ID = "GeorgeDrayson/modernbert-ai-detection-raid-mage"
TMR_ROBERTA_ID = "Oxidane/tmr-ai-text-detector"
GPT_NEO_ID = "EleutherAI/gpt-neo-125m"
GPT2_ID = "gpt2"

# Poids nominaux de la Nouvelle Armada SOTA Légère (Total = 1.00)
NOMINAL_WEIGHTS = {
    "deberta_raid": 0.30,
    "modernbert_long": 0.25,
    "tmr_roberta": 0.20,
    "fast_detectgpt": 0.15,
    "stylometric_entropy": 0.10,
}

# Buzzwords / N-grammes surreprésentés dans les sorties IA
AI_BUZZWORDS = {
    "furthermore", "moreover", "additionally", "in conclusion", "it is important to note",
    "it is worth noting", "delve", "tapestry", "pivotal", "seamlessly", "multifaceted",
    "paramount", "underscores", "interplay", "holistic", "testament", "crucial",
    "beacon", "foster", "garner", "harness", "intertwined", "linchpin", "myriad",
    "nexus", "nuanced", "plethora", "spearhead", "trailblazing", "unwavering",
    "vibrant", "revolutionize", "game-changer", "meticulously", "realm", "ever-evolving"
}


# ============================================================================
# 1. ARCHITECTURE DESKLIB CUSTOM MODEL (DeBERTa-v3 RAID)
# ============================================================================

try:
    from transformers import PreTrainedModel, AutoConfig, AutoModel
    import torch.nn as nn

    class DesklibAIDetectionModel(PreTrainedModel):
        """Architecture spécifique Desklib avec base DeBERTa-v3 et tête de régression linéaire."""
        config_class = AutoConfig

        def __init__(self, config):
            super().__init__(config)
            self.model = AutoModel.from_config(config)
            self.classifier = nn.Linear(config.hidden_size, 1)
            self.init_weights()

        def forward(self, input_ids, attention_mask=None, labels=None, **kwargs):
            outputs = self.model(input_ids, attention_mask=attention_mask)
            last_hidden_state = outputs[0]
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
            sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
            sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
            pooled_output = sum_embeddings / sum_mask
            logits = self.classifier(pooled_output)
            return type("ModelOutput", (), {"logits": logits})()
except Exception:
    DesklibAIDetectionModel = None


# ============================================================================
# 2. NETTOYAGE ET SEGMENTATION DU TEXTE (LaTeX, Markdown, Texte Brut)
# ============================================================================

def clean_latex(text: str) -> str:
    """Nettoie le balisage LaTeX pour extraire le texte brut."""
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\$\$.*?\$\$', ' ', text, flags=re.DOTALL)
    text = re.sub(r'\\\[.*?\\\]', ' ', text, flags=re.DOTALL)
    text = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', ' ', text)
    text = re.sub(r'\\begin\{(equation|align|table|figure|tikzpicture|tabular)\*?\}.*?\\end\{\1\*?\}', ' ', text, flags=re.DOTALL)
    text = re.sub(r'\\(cite|citep|citet|ref|eqref|label|pageref)\{[^}]*\}', '', text)
    text = re.sub(r'\\(textbf|textit|emph|underline|section|subsection|subsubsection|paragraph)\{([^}]*)\}', r'\2', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    text = text.replace('{', '').replace('}', '')
    return text


def clean_markdown(text: str) -> str:
    """Nettoie le balisage Markdown pour extraire le texte brut."""
    text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'^\s*#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', text)
    text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
    return text


def clean_raw_text(text: str, filename: Optional[str] = None) -> str:
    """Nettoie intelligemment le texte selon son format ou son extension."""
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.tex', '.latex'):
            return clean_latex(text)
        elif ext in ('.md', '.markdown'):
            return clean_markdown(text)

    if '\\begin{' in text or '\\section' in text or '\\cite' in text:
        text = clean_latex(text)
    if '```' in text or re.search(r'^\s*#{1,6}\s', text, flags=re.MULTILINE):
        text = clean_markdown(text)

    return text


def split_into_paragraphs(text: str) -> List[str]:
    """Découpe un texte en paragraphes non vides."""
    raw_paras = re.split(r'\n\s*\n+', text.strip())
    paras = [p.strip() for p in raw_paras if p.strip()]
    return paras if paras else [text.strip()]


def split_into_sentences(text: str) -> List[str]:
    """
    Découpeur de phrases robuste préservant les abréviations scientifiques
    (e.g., i.e., et al., Prof., Dr., Fig., Eq., etc.).
    """
    abbrs = ["e.g.", "i.e.", "et al.", "Prof.", "Dr.", "Fig.", "Eq.", "vs.", "approx.", "dept.", "cf.", "al."]
    protected = text
    mapping = {}
    for i, ab in enumerate(abbrs):
        placeholder = f"__ABBR_{i}__"
        if ab in protected:
            protected = protected.replace(ab, placeholder)
            mapping[placeholder] = ab

    # Protection des décimales
    protected = re.sub(r'(\d+)\.(\d+)', r'\1__DOT__\2', protected)
    raw_sents = re.split(r'(?<=[.!?])\s+', protected)

    sentences = []
    for s in raw_sents:
        for placeholder, orig in mapping.items():
            s = s.replace(placeholder, orig)
        s = s.replace("__DOT__", ".")
        s = s.strip()
        if s:
            sentences.append(s)

    return sentences if sentences else [text.strip()]


# ============================================================================
# 3. MODEL MANAGER & HARDWARE INFERENCE (GPU ACCELERATION)
# ============================================================================

class ModelManager:
    """
    Gestionnaire Singleton avec chargement paresseux et priorité GPU (CUDA).
    Accélération native pour GPU NVIDIA RTX 3060 et fallback CPU gracieux.
    Tous les modèles de l'armada sont ultra-légers (< 500 Mo chacun).
    """
    _instance = None

    def __init__(self, device_override: Optional[str] = None):
        if device_override:
            self.device = device_override
        else:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                self.device = "cpu"

        # Modèle 1 : DeBERTa-v3 RAID SOTA (30%)
        self._deberta_tok = None
        self._deberta_mod = None
        self._deberta_available = True

        # Modèle 2 : ModernBERT Long-Context (25%)
        self._modernbert_tok = None
        self._modernbert_mod = None
        self._modernbert_available = True

        # Modèle 3 : TMR RoBERTa Anti-Paraphrase (20%)
        self._tmr_tok = None
        self._tmr_mod = None
        self._tmr_available = True

        # Modèle 4 : Causal LM pour Fast-DetectGPT (15%)
        self._lm_tok = None
        self._lm_mod = None
        self._lm_available = True

    @classmethod
    def get_instance(cls, device_override: Optional[str] = None) -> "ModelManager":
        if cls._instance is None:
            cls._instance = ModelManager(device_override)
        elif device_override and cls._instance.device != device_override:
            cls._instance = ModelManager(device_override)
        return cls._instance

    def get_deberta_raid(self):
        """Charge DeBERTa-v3 RAID (desklib/ai-text-detector-v1.01)."""
        if self._deberta_mod is None and self._deberta_available and DesklibAIDetectionModel is not None:
            try:
                from transformers import AutoTokenizer
                self._deberta_tok = AutoTokenizer.from_pretrained(DEBERTA_RAID_ID)
                self._deberta_mod = DesklibAIDetectionModel.from_pretrained(
                    DEBERTA_RAID_ID
                ).to(self.device).eval()
            except Exception:
                self._deberta_available = False
                self._deberta_tok, self._deberta_mod = None, None
        return self._deberta_tok, self._deberta_mod

    def get_modernbert(self):
        """Charge ModernBERT Long-Context (GeorgeDrayson/modernbert-ai-detection-raid-mage)."""
        if self._modernbert_mod is None and self._modernbert_available:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self._modernbert_tok = AutoTokenizer.from_pretrained(MODERNBERT_ID)
                self._modernbert_mod = AutoModelForSequenceClassification.from_pretrained(
                    MODERNBERT_ID
                ).to(self.device).eval()
            except Exception:
                self._modernbert_available = False
                self._modernbert_tok, self._modernbert_mod = None, None
        return self._modernbert_tok, self._modernbert_mod

    def get_tmr_roberta(self):
        """Charge TMR RoBERTa Anti-Paraphrase (Oxidane/tmr-ai-text-detector)."""
        if self._tmr_mod is None and self._tmr_available:
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self._tmr_tok = AutoTokenizer.from_pretrained(TMR_ROBERTA_ID)
                self._tmr_mod = AutoModelForSequenceClassification.from_pretrained(
                    TMR_ROBERTA_ID
                ).to(self.device).eval()
            except Exception:
                self._tmr_available = False
                self._tmr_tok, self._tmr_mod = None, None
        return self._tmr_tok, self._tmr_mod

    def get_causal_lm(self):
        """Charge GPT-Neo-125M ou GPT-2 pour Fast-DetectGPT."""
        if self._lm_mod is None and self._lm_available:
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                lm_id = GPT_NEO_ID
                try:
                    self._lm_tok = AutoTokenizer.from_pretrained(lm_id)
                    self._lm_mod = AutoModelForCausalLM.from_pretrained(lm_id).to(self.device).eval()
                except Exception:
                    lm_id = GPT2_ID
                    self._lm_tok = AutoTokenizer.from_pretrained(lm_id)
                    self._lm_mod = AutoModelForCausalLM.from_pretrained(lm_id).to(self.device).eval()
            except Exception:
                self._lm_available = False
                self._lm_tok, self._lm_mod = None, None
        return self._lm_tok, self._lm_mod


# ============================================================================
# 4. LES 5 ACTEURS ALGORITHMIQUES SOTA DU BAGGING LÉGER
# ============================================================================

# --- 1. DeBERTa-v3 RAID SOTA (30%) ---
def score_deberta_raid(text: str, manager: ModelManager) -> Optional[Dict[str, Any]]:
    """Évalue la probabilité IA via DeBERTa-v3 RAID SOTA (desklib)."""
    tok, mod = manager.get_deberta_raid()
    if mod is None:
        return None

    import torch
    words = text.split()
    chunks = []
    chunk_size = 250
    overlap = 50
    if len(words) <= 300:
        chunks = [text]
    else:
        for i in range(0, len(words), chunk_size - overlap):
            c_text = " ".join(words[i:i + chunk_size])
            if c_text.strip():
                chunks.append(c_text)

    scores = []
    for c in chunks:
        inp = tok(c, return_tensors="pt", truncation=True, max_length=512).to(manager.device)
        with torch.no_grad():
            out = mod(**inp).logits
            p_ai = float(torch.sigmoid(out)[0][0].item())
            scores.append(p_ai)

    mean_s = sum(scores) / len(scores) if scores else 0.0
    max_s = max(scores) if scores else 0.0
    blended = 0.75 * mean_s + 0.25 * max_s

    return {
        "score": float(blended),
        "mean_score": float(mean_s),
        "max_score": float(max_s),
        "model_id": DEBERTA_RAID_ID
    }


# --- 2. ModernBERT Long-Context (25%) ---
def score_modernbert_long(text: str, manager: ModelManager) -> Optional[Dict[str, Any]]:
    """Évalue la probabilité IA via ModernBERT Long-Context (GeorgeDrayson, 8192 tokens natifs)."""
    tok, mod = manager.get_modernbert()
    if mod is None:
        return None

    import torch
    words = text.split()
    chunks = []
    chunk_size = 1500
    overlap = 200
    if len(words) <= 2000:
        chunks = [text]
    else:
        for i in range(0, len(words), chunk_size - overlap):
            c_text = " ".join(words[i:i + chunk_size])
            if c_text.strip():
                chunks.append(c_text)

    scores = []
    for c in chunks:
        inp = tok(c, return_tensors="pt", truncation=True, max_length=4096).to(manager.device)
        with torch.no_grad():
            out = mod(**inp).logits
            p_ai = float(torch.softmax(out, dim=-1)[0][1].item())
            scores.append(p_ai)

    mean_s = sum(scores) / len(scores) if scores else 0.0
    max_s = max(scores) if scores else 0.0
    blended = 0.75 * mean_s + 0.25 * max_s

    return {
        "score": float(blended),
        "mean_score": float(mean_s),
        "max_score": float(max_s),
        "model_id": MODERNBERT_ID
    }


# --- 3. TMR RoBERTa Anti-Paraphrase (20%) ---
def score_tmr_roberta(text: str, manager: ModelManager) -> Optional[Dict[str, Any]]:
    """Évalue la probabilité IA via TMR RoBERTa Anti-Paraphrase (Oxidane, Hard-Negative Mining sur RAID)."""
    tok, mod = manager.get_tmr_roberta()
    if mod is None:
        return None

    import torch
    words = text.split()
    chunks = []
    chunk_size = 250
    overlap = 50
    if len(words) <= 300:
        chunks = [text]
    else:
        for i in range(0, len(words), chunk_size - overlap):
            c_text = " ".join(words[i:i + chunk_size])
            if c_text.strip():
                chunks.append(c_text)

    scores = []
    for c in chunks:
        inp = tok(c, return_tensors="pt", truncation=True, max_length=512, padding=True).to(manager.device)
        with torch.no_grad():
            out = mod(**inp).logits
            p_ai = float(torch.softmax(out, dim=-1)[0][1].item())
            scores.append(p_ai)

    mean_s = sum(scores) / len(scores) if scores else 0.0
    max_s = max(scores) if scores else 0.0
    blended = 0.70 * mean_s + 0.30 * max_s

    return {
        "score": float(blended),
        "mean_score": float(mean_s),
        "max_score": float(max_s),
        "model_id": TMR_ROBERTA_ID
    }


# --- 4. Fast-DetectGPT Zéro-Shot (15%) ---
def score_fast_detectgpt(text: str, manager: ModelManager) -> Optional[Dict[str, Any]]:
    """
    Calcule la courbure conditionnelle analytique de Fast-DetectGPT (Bao et al., 2023)
    sans échantillonnage de perturbations coûteux.
    """
    tok, model = manager.get_causal_lm()
    if model is None:
        return None

    import torch
    words = text.split()
    chunks = []
    chunk_size = 250
    overlap = 50
    if len(words) <= 300:
        chunks = [text]
    else:
        for i in range(0, len(words), chunk_size - overlap):
            c_text = " ".join(words[i:i + chunk_size])
            if c_text.strip():
                chunks.append(c_text)

    chunk_curvatures = []
    chunk_ppls = []
    chunk_ranks = []

    for c in chunks:
        tokens = tok.encode(c, return_tensors="pt", truncation=True, max_length=512).to(manager.device)
        if tokens.shape[1] < 5:
            continue

        with torch.no_grad():
            outputs = model(tokens)
            logits = outputs.logits[0, :-1, :]  # (T-1, V)
        labels = tokens[0, 1:]                  # (T-1)

        log_probs = torch.log_softmax(logits, dim=-1)
        probs = torch.softmax(logits, dim=-1)
        target_log_probs = log_probs.gather(dim=-1, index=labels.unsqueeze(-1)).squeeze(-1)

        # Perplexité
        nll = -target_log_probs.mean().item()
        ppl = math.exp(min(nll, 20.0))
        chunk_ppls.append(ppl)

        # Fast-DetectGPT Courbure et Discrepancy
        mu = (probs * log_probs).sum(dim=-1)
        var = (probs * (log_probs ** 2)).sum(dim=-1) - (mu ** 2)
        var = torch.clamp(var, min=1e-8)

        discrepancy = target_log_probs - mu
        total_var = var.sum()
        std = torch.sqrt(total_var)
        curvature = (discrepancy.sum() / std).item() if std > 0 else 0.0
        chunk_curvatures.append(curvature)

        # Rangs des tokens réels
        sorted_idx = torch.argsort(logits, dim=-1, descending=True)
        ranks = (sorted_idx == labels.unsqueeze(-1)).nonzero()[:, 1].float()
        mean_rank = ranks.mean().item() if len(ranks) > 0 else 100.0
        chunk_ranks.append(mean_rank)

    if not chunk_curvatures:
        return {"score": 0.10, "ppl": 50.0, "curvature": -1.0, "mean_rank": 200.0}

    avg_curv = sum(chunk_curvatures) / len(chunk_curvatures)
    avg_ppl = sum(chunk_ppls) / len(chunk_ppls)
    avg_rank = sum(chunk_ranks) / len(chunk_ranks)

    s_curv = 1.0 / (1.0 + math.exp(-(avg_curv - 0.5) * 1.5))
    s_ppl = 1.0 / (1.0 + math.exp((avg_ppl - 25.0) / 10.0))
    s_rank = 1.0 / (1.0 + math.exp((avg_rank - 50.0) / 30.0))

    s_prob = 0.50 * s_curv + 0.30 * s_ppl + 0.20 * s_rank
    s_prob = max(0.0, min(1.0, s_prob))

    return {
        "score": float(s_prob),
        "ppl": float(round(avg_ppl, 2)),
        "curvature": float(round(avg_curv, 3)),
        "mean_rank": float(round(avg_rank, 1))
    }


# --- 5. Stylométrie & Entropie (10%) ---
def score_stylometric(text: str) -> Dict[str, Any]:
    """
    Calcule les métriques stylométriques pures :
    - Burstiness (Coefficient de variation CV des longueurs de phrase)
    - Entropie de Shannon normalisée
    - Diversité lexicale (TTR, Root-TTR, Maas)
    - Buzzwords IA
    """
    sentences = split_into_sentences(text)
    words = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', text.lower())
    n_words = len(words)
    n_sents = len(sentences)

    if n_words < 6 or n_sents == 0:
        return {
            "score": 0.05,
            "cv_len": 0.80,
            "mean_sent_len": 10.0,
            "ttr": 0.90,
            "norm_entropy": 0.90,
            "buzzword_ratio": 0.0,
            "buzzwords_found": []
        }

    # 1. Burstiness (Longueur des phrases)
    sent_lens = [len(re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s)) for s in sentences]
    sent_lens = [l for l in sent_lens if l > 0]
    if not sent_lens:
        sent_lens = [n_words]

    mean_sent_len = sum(sent_lens) / len(sent_lens)
    variance_sent_len = sum((l - mean_sent_len) ** 2 for l in sent_lens) / len(sent_lens)
    std_sent_len = math.sqrt(variance_sent_len)
    cv_len = (std_sent_len / mean_sent_len) if mean_sent_len > 0 else 0.0

    # 2. Diversité lexicale (TTR, Root-TTR, Maas)
    unique_words = set(words)
    ttr = len(unique_words) / n_words
    root_ttr = len(unique_words) / math.sqrt(n_words)
    maas = (math.log(n_words) - math.log(len(unique_words))) / (math.log(n_words) ** 2) if n_words > 1 and len(unique_words) > 1 else 0.0

    # 3. Entropie de Shannon des mots
    from collections import Counter
    word_counts = Counter(words)
    probs = [c / n_words for c in word_counts.values()]
    word_entropy = -sum(p * math.log2(p) for p in probs)
    max_entropy = math.log2(n_words) if n_words > 1 else 1.0
    norm_entropy = word_entropy / max_entropy if max_entropy > 0 else 1.0

    # 4. Buzzwords IA
    found_buzz = [w for w in words if w in AI_BUZZWORDS]
    text_lower = text.lower()
    for phrase in ["in conclusion", "it is important to note", "it is worth noting"]:
        if phrase in text_lower:
            found_buzz.append(phrase)

    buzzword_ratio = len(found_buzz) / n_words

    # Évaluation stylométrique
    s_burst = max(0.0, min(1.0, (0.70 - cv_len) / 0.50))
    s_buzz = min(1.0, buzzword_ratio * 40.0)
    s_unif = 1.0 if (14.0 <= mean_sent_len <= 26.0 and cv_len < 0.30) else 0.0
    s_ent = max(0.0, min(1.0, 1.0 - abs(norm_entropy - 0.85) * 5.0)) if cv_len < 0.35 else 0.0

    s_stylo = 0.40 * s_burst + 0.35 * s_buzz + 0.15 * s_unif + 0.10 * s_ent
    s_stylo = max(0.0, min(1.0, s_stylo))

    return {
        "score": float(round(s_stylo, 4)),
        "cv_len": float(round(cv_len, 3)),
        "mean_sent_len": float(round(mean_sent_len, 1)),
        "ttr": float(round(ttr, 3)),
        "root_ttr": float(round(root_ttr, 2)),
        "maas": float(round(maas, 3)),
        "norm_entropy": float(round(norm_entropy, 3)),
        "buzzword_ratio": float(round(buzzword_ratio, 4)),
        "buzzwords_found": list(set(found_buzz))
    }


# ============================================================================
# 5. UNIFIED 5-MODEL BAGGING ENSEMBLE ENGINE & HEATMAP
# ============================================================================

def analyze_text(
    text: str,
    filename: Optional[str] = None,
    device_override: Optional[str] = None,
    fast_mode: bool = False,
    compliance_threshold: float = 0.10
) -> Dict[str, Any]:
    """
    Exécute l'analyse SOTA Bagging légère à 5 modèles :
    1. Nettoyage et segmentation structurelle (LaTeX / Markdown)
    2. Inférence des 5 acteurs SOTA (DeBERTa 30%, ModernBERT 25%, TMR RoBERTa 20%, Fast-DetectGPT 15%, Stylométrie 10%)
    3. Renormalisation dynamique et fusion Bayésienne d'ensemble
    4. Heatmap diagnostique phrase par phrase avec indicateurs 🟢 / 🟠 / 🔴 / ⚪
    """
    clean_txt = clean_raw_text(text, filename)
    manager = ModelManager.get_instance(device_override)

    words_count = len(clean_txt.split())
    if words_count < 5:
        p_ai = 0.05
        return {
            "global_score": {
                "p_ai": p_ai,
                "p_ai_percent": round(p_ai * 100, 1),
                "verdict": "INDETERMINE",
                "verdict_icon": "⚪",
                "status_label": "Texte trop court (< 5 mots)",
                "is_compliant": True,
                "compliance_threshold": compliance_threshold
            },
            "breakdown": {},
            "text_stats": {
                "char_count": len(clean_txt),
                "word_count": words_count,
                "sentence_count": 1,
                "paragraph_count": 1
            },
            "paragraphs": [],
            "device": manager.device
        }

    # Inférence des 5 modèles
    results_models: Dict[str, Any] = {}
    active_weights: Dict[str, float] = {}

    # 1. DeBERTa-v3 RAID SOTA (30%)
    deberta_res = score_deberta_raid(clean_txt, manager)
    if deberta_res is not None:
        results_models["deberta_raid"] = deberta_res
        active_weights["deberta_raid"] = NOMINAL_WEIGHTS["deberta_raid"]

    # 2. ModernBERT Long-Context (25%)
    modernbert_res = score_modernbert_long(clean_txt, manager)
    if modernbert_res is not None:
        results_models["modernbert_long"] = modernbert_res
        active_weights["modernbert_long"] = NOMINAL_WEIGHTS["modernbert_long"]

    # 3. TMR RoBERTa Anti-Paraphrase (20%)
    tmr_res = score_tmr_roberta(clean_txt, manager)
    if tmr_res is not None:
        results_models["tmr_roberta"] = tmr_res
        active_weights["tmr_roberta"] = NOMINAL_WEIGHTS["tmr_roberta"]

    # 4. Fast-DetectGPT Zéro-Shot (15%)
    if not fast_mode:
        fast_res = score_fast_detectgpt(clean_txt, manager)
        if fast_res is not None:
            results_models["fast_detectgpt"] = fast_res
            active_weights["fast_detectgpt"] = NOMINAL_WEIGHTS["fast_detectgpt"]

    # 5. Stylométrie & Entropie (10%)
    stylo_res = score_stylometric(clean_txt)
    results_models["stylometric_entropy"] = stylo_res
    active_weights["stylometric_entropy"] = NOMINAL_WEIGHTS["stylometric_entropy"]

    # Renormalisation bayésienne dynamique des poids actifs
    total_weight = sum(active_weights.values())
    if total_weight > 0:
        weighted_sum = sum(active_weights[k] * results_models[k]["score"] for k in active_weights)
        p_ai = weighted_sum / total_weight
    else:
        p_ai = stylo_res["score"]

    p_ai = max(0.0, min(1.0, p_ai))

    # Verdict
    if p_ai < compliance_threshold:
        verdict = "HUMAIN"
        verdict_icon = "✅"
        status_label = f"Conforme (< {int(compliance_threshold*100)}%)"
    elif p_ai < 0.40:
        verdict = "SUSPECT"
        verdict_icon = "⚠️"
        status_label = "Suspect (10% - 40%)"
    else:
        verdict = "ALERTE IA"
        verdict_icon = "🔴"
        status_label = "Alerte IA (>= 40%)"

    # --- Cartographie Paragraphes & Phrases ---
    paragraphs = split_into_paragraphs(clean_txt)
    paragraph_diagnostics = []

    all_sentences_with_meta = []
    for p_idx, para in enumerate(paragraphs):
        sents = split_into_sentences(para)
        for s_idx, sent in enumerate(sents):
            all_sentences_with_meta.append((p_idx, s_idx, sent))

    sent_scores = []
    if all_sentences_with_meta:
        batch_texts = [s[2] for s in all_sentences_with_meta]
        import torch

        # Évaluation neuronale rapide par ModernBERT
        tok_m, mod_m = manager.get_modernbert()
        if mod_m is not None:
            inp_m = tok_m(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=256).to(manager.device)
            with torch.no_grad():
                out_m = mod_m(**inp_m).logits
                p_m_list = torch.softmax(out_m, dim=-1)[:, 1].tolist()
        else:
            p_m_list = [0.0] * len(batch_texts)

        # Évaluation neuronale par TMR RoBERTa
        tok_t, mod_t = manager.get_tmr_roberta()
        if mod_t is not None:
            inp_t = tok_t(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=256).to(manager.device)
            with torch.no_grad():
                out_t = mod_t(**inp_t).logits
                p_t_list = torch.softmax(out_t, dim=-1)[:, 1].tolist()
        else:
            p_t_list = [0.0] * len(batch_texts)

        for i, (p_idx, s_idx, s_text) in enumerate(all_sentences_with_meta):
            pm = p_m_list[i]
            pt = p_t_list[i]

            if mod_m is not None and mod_t is not None:
                s_enc_sent = 0.55 * pm + 0.45 * pt
            elif mod_m is not None:
                s_enc_sent = pm
            elif mod_t is not None:
                s_enc_sent = pt
            else:
                s_enc_sent = 0.0

            words_s = re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s_text.lower())
            buzz_s = sum(1 for w in words_s if w in AI_BUZZWORDS)
            s_stylo_sent = min(1.0, (buzz_s / max(len(words_s), 1)) * 30.0) if words_s else 0.0

            p_ai_sent = 0.70 * s_enc_sent + 0.30 * s_stylo_sent

            if len(words_s) < 4:
                tag = "SKIP"
                tag_icon = "⚪"
            elif p_ai_sent < 0.15:
                tag = "HUMAIN"
                tag_icon = "🟢"
            elif p_ai_sent < 0.45:
                tag = "SUSPECT"
                tag_icon = "🟠"
            else:
                tag = "ALERTE"
                tag_icon = "🔴"

            sent_scores.append({
                "para_idx": p_idx,
                "sent_idx": s_idx,
                "text": s_text,
                "p_ai": float(round(p_ai_sent, 4)),
                "p_ai_percent": float(round(p_ai_sent * 100, 1)),
                "tag": tag,
                "tag_icon": tag_icon,
                "buzzwords_count": buzz_s
            })

    for p_idx, para in enumerate(paragraphs):
        para_sents = [s for s in sent_scores if s["para_idx"] == p_idx]
        if para_sents:
            valid_sents = [s for s in para_sents if s["tag"] != "SKIP"]
            if valid_sents:
                para_p_ai = sum(s["p_ai"] for s in valid_sents) / len(valid_sents)
            else:
                para_p_ai = sum(s["p_ai"] for s in para_sents) / len(para_sents)
        else:
            para_p_ai = 0.0

        if para_p_ai < 0.15:
            p_tag = "HUMAIN"
            p_icon = "🟢"
        elif para_p_ai < 0.45:
            p_tag = "SUSPECT"
            p_icon = "🟠"
        else:
            p_tag = "ALERTE"
            p_icon = "🔴"

        paragraph_diagnostics.append({
            "para_idx": p_idx + 1,
            "text": para,
            "p_ai": float(round(para_p_ai, 4)),
            "p_ai_percent": float(round(para_p_ai * 100, 1)),
            "tag": p_tag,
            "tag_icon": p_icon,
            "sentences": para_sents
        })

    # Mise en forme du breakdown
    breakdown_formatted = {}
    for k, v in results_models.items():
        nom_w = NOMINAL_WEIGHTS[k]
        eff_w = (active_weights[k] / total_weight) if total_weight > 0 else 0.0
        breakdown_formatted[k] = {
            "nominal_weight": nom_w,
            "effective_weight": float(round(eff_w, 3)),
            "score": float(round(v["score"], 4)),
            "score_percent": float(round(v["score"] * 100, 1)),
            "details": v
        }

    return {
        "global_score": {
            "p_ai": float(round(p_ai, 4)),
            "p_ai_percent": float(round(p_ai * 100, 1)),
            "verdict": verdict,
            "verdict_icon": verdict_icon,
            "status_label": status_label,
            "is_compliant": bool(p_ai < compliance_threshold),
            "compliance_threshold": compliance_threshold
        },
        "breakdown": breakdown_formatted,
        "text_stats": {
            "char_count": len(clean_txt),
            "word_count": words_count,
            "sentence_count": len(all_sentences_with_meta),
            "paragraph_count": len(paragraphs)
        },
        "paragraphs": paragraph_diagnostics,
        "device": manager.device
    }


# ============================================================================
# 6. CONSOLE FORMATTING & ULTRA-READABLE HEATMAP
# ============================================================================

def format_console_report(results: Dict[str, Any], show_heatmap: bool = True) -> str:
    """Met en forme le rapport console synthétique et ultra-lisible."""
    g = results["global_score"]
    b = results["breakdown"]
    st = results["text_stats"]

    lines = []
    lines.append("=" * 80)
    lines.append(" 🧠 MOTEUR DÉTECTEUR IA — NOUVELLE ARMADA SOTA LÉGÈRE 5 MODÈLES (< 500 Mo)")
    lines.append("=" * 80)

    # 1. Résumé synthétique
    lines.append(f"\n📊 SCORE GLOBAL P(AI) : {g['p_ai_percent']:.1f}% | VERDICT : {g['verdict_icon']} {g['verdict']} [{g['status_label']}]")
    lines.append(f"   Périphérique : {results['device'].upper()} | Mots : {st['word_count']} | Phrases : {st['sentence_count']} | Paragraphes : {st['paragraph_count']}")

    # 2. Breakdown des 5 acteurs SOTA
    lines.append("\n" + "-" * 80)
    lines.append("🔬 DÉCOMPOSITION DE L'ARMADA SOTA (5 MODÈLES LÉGERS) :")
    lines.append("-" * 80)

    labels_map = {
        "deberta_raid": ("DeBERTa-v3 RAID SOTA", "30%"),
        "modernbert_long": ("ModernBERT Long-Context", "25%"),
        "tmr_roberta": ("TMR RoBERTa Anti-Paraphrase", "20%"),
        "fast_detectgpt": ("Fast-DetectGPT Zéro-Shot", "15%"),
        "stylometric_entropy": ("Stylométrie & Entropie", "10%"),
    }

    idx = 1
    for key, (label, def_weight) in labels_map.items():
        if key in b:
            m = b[key]
            eff_w = m["effective_weight"] * 100
            score_p = m["score_percent"]
            details = m.get("details", {})
            extra = ""
            if key == "deberta_raid":
                extra = f"(Modèle: {DEBERTA_RAID_ID})"
            elif key == "modernbert_long":
                extra = f"(Modèle: {MODERNBERT_ID}, 8192 tokens)"
            elif key == "tmr_roberta":
                extra = f"(Modèle: {TMR_ROBERTA_ID}, Hard-Negative Mining)"
            elif key == "fast_detectgpt":
                extra = f"(PPL: {details.get('ppl', 0):.1f}, Courbure: {details.get('curvature', 0):.2f})"
            elif key == "stylometric_entropy":
                extra = f"(CV: {details.get('cv_len', 0):.2f}, TTR: {details.get('ttr', 0):.2f}, Buzzwords: {len(details.get('buzzwords_found', []))})"

            lines.append(f"  {idx}. [{eff_w:4.1f}%] {label:<28} : {score_p:5.1f}%  {extra}")
            idx += 1

    # 3. Cartographie / Heatmap phrase par phrase
    if show_heatmap and results.get("paragraphs"):
        lines.append("\n" + "-" * 80)
        lines.append("🗺️  CARTOGRAPHIE HEATMAP (PHRASE PAR PHRASE) :")
        lines.append("-" * 80)

        for p in results["paragraphs"]:
            lines.append(f"\n📑 Paragraphe {p['para_idx']} — Score P(AI) : {p['tag_icon']} {p['p_ai_percent']:.1f}% [{p['tag']}]")
            for s in p["sentences"]:
                tag_label = f"{s['tag']:<7} {s['p_ai_percent']:4.1f}%"
                lines.append(f"   {s['tag_icon']} [{tag_label}] {s['text']}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


# ============================================================================
# 7. CLI POINT D'ENTRÉE ULTRA-SIMPLE (ZÉRO ARGUMENT REQUIS)
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Moteur Détecteur IA Multi-Modèles SOTA (Armada Légère 5 Modèles < 500 Mo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python antigravity/scripts/ai_detector.py "Texte direct à analyser..."
  python antigravity/scripts/ai_detector.py draft.md
  python antigravity/scripts/ai_detector.py paper.tex --json
  cat draft.txt | python antigravity/scripts/ai_detector.py
        """
    )
    parser.add_argument("input", nargs="?", help="Texte direct ou chemin vers un fichier (.tex, .md, .txt)")
    parser.add_argument("--json", action="store_true", help="Sortie JSON structurée pour sous-agents")
    parser.add_argument("--no-heatmap", action="store_true", help="Masquer la heatmap détaillée phrase par phrase")
    parser.add_argument("--threshold", type=float, default=0.10, help="Seuil de conformité (défaut : 0.10 / 10%%)")
    parser.add_argument("--device", type=str, choices=["auto", "cpu", "cuda"], default="auto", help="Périphérique d'inférence (défaut: auto avec priorité CUDA GPU)")
    parser.add_argument("--fast", action="store_true", help="Mode rapide (omission du Causal LM Fast-DetectGPT)")

    args = parser.parse_args()

    raw_text = None
    filename = None

    if args.input:
        if os.path.isfile(args.input):
            filename = args.input
            try:
                with open(args.input, "r", encoding="utf-8", errors="replace") as f:
                    raw_text = f.read()
            except Exception as e:
                print(f"Erreur de lecture du fichier '{args.input}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            raw_text = args.input
    elif not sys.stdin.isatty():
        raw_text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(0)

    if not raw_text or not raw_text.strip():
        print("Erreur : Aucun texte fourni à analyser.", file=sys.stderr)
        sys.exit(1)

    device_override = None if args.device == "auto" else args.device

    results = analyze_text(
        text=raw_text,
        filename=filename,
        device_override=device_override,
        fast_mode=args.fast,
        compliance_threshold=args.threshold
    )

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_console_report(results, show_heatmap=not args.no_heatmap))


if __name__ == "__main__":
    main()
