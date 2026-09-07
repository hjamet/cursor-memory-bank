#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Detector Engine (7-Component Unified SOTA Bagging & Binoculars Ensemble)
Moteur Détecteur IA Multi-Modèles Haute Précision & GPU-Accelerated (Architecture Cohort Staged Waterfall < 8 Go VRAM)
Localisation : c:/Users/Jamet/Documents/VoiceNotes/antigravity/scripts/ai_detector.py

Combine 7 acteurs algorithmiques SOTA complémentaires selon la doctrine Zero-Trust et Fail-Stop :
1. Binoculars Gemma-4-E2B (35%)   : google/gemma-4-E2B (Observer) + google/gemma-4-E2B-it (Performer) [Leader Incontesté]
2. DeBERTa-v3 RAID SOTA (15%)      : desklib/ai-text-detector-v1.01 (Benchmark RAID Leader)
3. ModernBERT Long-Context (15%)  : GeorgeDrayson/modernbert-ai-detection-raid-mage (8192 tokens natifs, MAGE & RAID)
4. TMR RoBERTa Anti-Paraph. (12%) : Oxidane/tmr-ai-text-detector (Focal Loss & Hard-Negative Mining sur RAID)
5. DeBERTa-v3 Academic (10%)      : desklib/ai-text-detector-academic-v1.01 (Spécialisé Corpus Scientifique & Papiers)
6. XLM-RoBERTa Multilingue (7%)   : yaya36095/xlm-roberta-text-detector (Cross-lingual Robustness)
7. Stylométrie & Entropie (6%)    : Burstiness CV, TTR, Maas, Entropie de Shannon, Buzzwords

Architecture d'Exécution en 3 Cohortes Séquentielles (Plafond VRAM < 8 Go garanti) :
- Cohorte 1 : Les 5 encodeurs en FP16 (~2.7 Go VRAM) -> inférence chunks + heatmaps -> déchargement total.
- Cohorte 2 : Module Binoculars Gemma-4-E2B en 4-bit séquentiel (~2.6 Go VRAM) -> déchargement total.
- Cohorte 3 : Moteur Stylométrique & Entropique (CPU, 0 Mo VRAM).
- Fusion Bayésienne : Somme pondérée renormalisée à 1.0.

Seuil de conformité académique : P(AI) < 0.10 (10%)
Doctrine Fail-Stop : Tout échec d'un composant obligatoire interrompt immédiatement l'exécution.
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


# ============================================================================
# 0. GESTION DU TOKEN HUGGING FACE & FAIL-STOP
# ============================================================================

def resolve_hf_token(token_arg: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Résout et valide le token Hugging Face selon la doctrine Fail-Stop.
    Ordre de recherche :
    1. Argument explicite CLI (--hf-token)
    2. Variable d'environnement HF_TOKEN
    3. antigravity/.hf_token
    4. Cache standard ~/.cache/huggingface/token
    """
    if token_arg and token_arg.strip():
        tok = token_arg.strip()
        os.environ["HF_TOKEN"] = tok
        return tok

    env_tok = os.environ.get("HF_TOKEN")
    if env_tok and env_tok.strip():
        return env_tok.strip()

    # Local antigravity/.hf_token
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.normpath(os.path.join(curr_dir, "..", ".hf_token"))
        if os.path.isfile(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                tok = f.read().strip()
                if tok:
                    os.environ["HF_TOKEN"] = tok
                    return tok
    except Exception:
        pass

    # ~/.cache/huggingface/token
    try:
        cache_path = os.path.expanduser("~/.cache/huggingface/token")
        if os.path.isfile(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                tok = f.read().strip()
                if tok:
                    os.environ["HF_TOKEN"] = tok
                    return tok
    except Exception:
        pass

    if required:
        raise RuntimeError(
            "❌ [FAIL-STOP] Token Hugging Face introuvable !\n"
            "La doctrine Fail-Stop exige un token Hugging Face pour l'accès aux modèles de l'armada.\n"
            "Veuillez définir la variable d'environnement HF_TOKEN, renseigner 'antigravity/.hf_token', "
            "ou utiliser '--hf-token <token>'."
        )
    return None


# Identifiants officiels de l'Armada SOTA à 7 Composants
DEBERTA_RAID_ID = "desklib/ai-text-detector-v1.01"
MODERNBERT_ID = "GeorgeDrayson/modernbert-ai-detection-raid-mage"
TMR_ROBERTA_ID = "Oxidane/tmr-ai-text-detector"
DEBERTA_ACADEMIC_ID = "desklib/ai-text-detector-academic-v1.01"
XLM_ROBERTA_ID = "yaya36095/xlm-roberta-text-detector"
BINOCULARS_OBSERVER_ID = "google/gemma-4-E2B"
BINOCULARS_PERFORMER_ID = "google/gemma-4-E2B-it"

# Poids nominaux officiels de l'Armada SOTA (Total = 1.00 / 100%) - Option 2 : Leader Incontesté Binoculars
NOMINAL_WEIGHTS = {
    "binoculars_gemma": 0.35,    # 1. Binoculars via Gemma-4-E2B (Leader Causal & Géométrique Incontesté)
    "deberta_raid": 0.15,        # 2. DeBERTa-v3 RAID SOTA (Benchmark RAID Leader)
    "modernbert_long": 0.15,     # 3. ModernBERT Long-Context (8192 ctx, MAGE & RAID)
    "tmr_roberta": 0.12,         # 4. TMR RoBERTa Anti-Paraphrase (Focal Loss & Hard-Negatives)
    "deberta_academic": 0.10,    # 5. DeBERTa-v3 Academic SOTA (Corpus Scientifique)
    "xlm_roberta": 0.07,         # 6. XLM-RoBERTa Multilingue (Cross-lingual Robustness)
    "stylometric_entropy": 0.06, # 7. Moteur Stylométrique & Entropique (Garde-fou non-neural)
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
# 1. ARCHITECTURE DESKLIB CUSTOM MODEL (DeBERTa-v2/v3 RAID & Academic)
# ============================================================================

try:
    from transformers import PreTrainedModel, AutoConfig, AutoModel
    import torch.nn as nn

    class DesklibAIDetectionModel(PreTrainedModel):
        """
        Architecture spécifique Desklib avec base DeBERTa-v2/v3 et tête de régression linéaire.
        Correctif L120 appliqué : .to(last_hidden_state.dtype) pour compatibilité native FP16/BF16.
        """
        config_class = AutoConfig

        def __init__(self, config):
            super().__init__(config)
            self.model = AutoModel.from_config(config)
            self.classifier = nn.Linear(config.hidden_size, 1)
            if hasattr(self, "post_init"):
                self.post_init()
            else:
                self.init_weights()

        def forward(self, input_ids, attention_mask=None, labels=None, **kwargs):
            outputs = self.model(input_ids, attention_mask=attention_mask)
            last_hidden_state = outputs[0]
            # Alignement strict sur le dtype de last_hidden_state (support FP16/BF16 sans crash)
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).to(last_hidden_state.dtype)
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
    # Extraire uniquement le corps du document si \begin{document} est présent (ignorer préambule et packages)
    m_doc = re.search(r'\\begin\{document\}(.*?)(?:\\end\{document\}|\\bibliography\{|$)', text, flags=re.DOTALL)
    if m_doc:
        text = m_doc.group(1)

    # 1. Expand custom macros
    text = re.sub(r'\\llmgame\b', 'LATENT SPACE', text)
    text = re.sub(r'\\levelbadge\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\citet\{[^}]*\}', 'prior work', text)

    text = re.sub(r'\$\$.*?\$\$', ' ', text, flags=re.DOTALL)
    text = re.sub(r'\\\[.*?\\\]', ' ', text, flags=re.DOTALL)

    def _clean_math(m):
        raw_m = m.group(1).strip()
        cleaned = re.sub(r'[{}\\]', '', raw_m)
        cleaned = cleaned.replace('approx', '~').replace('times', 'x').replace('cdot', '*').replace('operatorname', '')
        if len(cleaned.split()) <= 5:
            return f" {cleaned} "
        return ' '

    text = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', _clean_math, text)
    text = re.sub(r'\\begin\{(equation|align|table|figure|tikzpicture|tabular|minipage)\*?\}.*?\\end\{\1\*?\}', ' ', text, flags=re.DOTALL)
    text = re.sub(r'\\(cite|citep|ref|eqref|label|pageref)\{[^}]*\}', '', text)
    # Supprimer les commandes d'en-tête et macro-métadonnées
    text = re.sub(r'\\(title|author|affiliation|institution|email|def|newcommand|renewcommand)\{[^}]*\}', '', text)
    text = re.sub(r'\\(textbf|textit|emph|underline)\{([^}]*)\}', r'\2', text)
    text = re.sub(r'\\(section|subsection|subsubsection)\*?\{[^}]*\}', '', text)
    text = re.sub(r'\\begin\{[a-zA-Z*]+\}(?:\[[^\]]*\])?', ' ', text)
    text = re.sub(r'\\end\{[a-zA-Z*]+\}', ' ', text)
    text = re.sub(r'\\item(?:\s*\[[^\]]*\])?', ' ', text)
    text = re.sub(r'\\paragraph\*?\{([^}]*)\}', r'\1 ', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    text = text.replace('{', '').replace('}', '')
    return text


def clean_markdown(text: str) -> str:
    """Nettoie le balisage Markdown pour extraire le texte brut."""
    text = re.sub(r'```.*?```', ' ', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'^\s*#+\s+.*$', '', text, flags=re.MULTILINE)
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
    paras = [p.strip() for p in raw_paras if p.strip() and len(p.strip().split()) >= 8]
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
# 3. MODEL MANAGER (COHORT STAGED WATERFALL & FAIL-STOP GPU)
# ============================================================================

class ModelManager:
    """
    Gestionnaire avec cycle de vie par cohorte (Staged Waterfall)
    et gestion chirurgicale de la mémoire VRAM pour GPU 8 Go (RTX 3060/3070/4060).
    """
    _instance = None

    def __init__(
        self,
        device_override: Optional[str] = None,
        hf_token: Optional[str] = None,
        local_files_only: bool = False,
        keep_loaded: Optional[bool] = None
    ):
        if device_override:
            self.device = device_override
        else:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                self.device = "cpu"

        import torch
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.bfloat16_supported = torch.cuda.is_available() and torch.cuda.is_bf16_supported() if self.device == "cuda" else False
        self.causal_dtype = torch.bfloat16 if self.bfloat16_supported else self.torch_dtype
        self.hf_token = hf_token
        self.local_files_only = local_files_only

        # Détection intelligente VRAM
        total_vram_gb = 0.0
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            except Exception:
                total_vram_gb = 0.0
        self.total_vram_gb = total_vram_gb

        # Si GPU VRAM >= 8 Go, conserver en mémoire par défaut
        if keep_loaded is not None:
            self.keep_loaded = keep_loaded
        else:
            self.keep_loaded = True if (self.device == "cuda" and total_vram_gb >= 8.0) else True

        # Cohorte 1 : 5 Encodeurs
        self._deberta_tok = None
        self._deberta_mod = None
        self._modernbert_tok = None
        self._modernbert_mod = None
        self._tmr_tok = None
        self._tmr_mod = None
        self._deberta_acad_tok = None
        self._deberta_acad_mod = None
        self._xlm_tok = None
        self._xlm_mod = None

        # Cohorte 2 : Binoculars Gemma-4-E2B (Observer & Performer)
        self._bino_obs_tok = None
        self._bino_obs_mod = None
        self._bino_perf_tok = None
        self._bino_perf_mod = None

    @classmethod
    def get_instance(
        cls,
        device_override: Optional[str] = None,
        hf_token: Optional[str] = None,
        local_files_only: bool = False,
        keep_loaded: Optional[bool] = None
    ) -> "ModelManager":
        if cls._instance is None:
            cls._instance = ModelManager(device_override, hf_token, local_files_only, keep_loaded)
        elif device_override and cls._instance.device != device_override:
            cls._instance = ModelManager(device_override, hf_token, local_files_only, keep_loaded)
        elif hf_token and cls._instance.hf_token != hf_token:
            cls._instance.hf_token = hf_token
        cls._instance.local_files_only = local_files_only
        if keep_loaded is not None:
            cls._instance.keep_loaded = keep_loaded
        return cls._instance

    def get_deberta_raid(self):
        if self._deberta_mod is None:
            from transformers import AutoTokenizer
            self._deberta_tok = AutoTokenizer.from_pretrained(
                DEBERTA_RAID_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            self._deberta_mod = DesklibAIDetectionModel.from_pretrained(
                DEBERTA_RAID_ID, token=self.hf_token, torch_dtype=self.torch_dtype, local_files_only=self.local_files_only
            ).to(self.device).eval()
        return self._deberta_tok, self._deberta_mod

    def get_modernbert(self):
        if self._modernbert_mod is None:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self._modernbert_tok = AutoTokenizer.from_pretrained(
                MODERNBERT_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            self._modernbert_mod = AutoModelForSequenceClassification.from_pretrained(
                MODERNBERT_ID, token=self.hf_token, torch_dtype=self.torch_dtype, local_files_only=self.local_files_only
            ).to(self.device).eval()
        return self._modernbert_tok, self._modernbert_mod

    def get_tmr_roberta(self):
        if self._tmr_mod is None:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self._tmr_tok = AutoTokenizer.from_pretrained(
                TMR_ROBERTA_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            self._tmr_mod = AutoModelForSequenceClassification.from_pretrained(
                TMR_ROBERTA_ID, token=self.hf_token, torch_dtype=self.torch_dtype, local_files_only=self.local_files_only
            ).to(self.device).eval()
        return self._tmr_tok, self._tmr_mod

    def get_deberta_academic(self):
        if self._deberta_acad_mod is None:
            from transformers import AutoTokenizer
            self._deberta_acad_tok = AutoTokenizer.from_pretrained(
                DEBERTA_ACADEMIC_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            self._deberta_acad_mod = DesklibAIDetectionModel.from_pretrained(
                DEBERTA_ACADEMIC_ID, token=self.hf_token, torch_dtype=self.torch_dtype, local_files_only=self.local_files_only
            ).to(self.device).eval()
        return self._deberta_acad_tok, self._deberta_acad_mod

    def get_xlm_roberta(self):
        if self._xlm_mod is None:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self._xlm_tok = AutoTokenizer.from_pretrained(
                XLM_ROBERTA_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            self._xlm_mod = AutoModelForSequenceClassification.from_pretrained(
                XLM_ROBERTA_ID, token=self.hf_token, torch_dtype=self.torch_dtype, local_files_only=self.local_files_only
            ).to(self.device).eval()
        return self._xlm_tok, self._xlm_mod

    def unload_encoders(self):
        """Libère intégralement les 5 encodeurs de la mémoire VRAM."""
        import gc
        import torch
        self._deberta_mod = None
        self._deberta_tok = None
        self._modernbert_mod = None
        self._modernbert_tok = None
        self._tmr_mod = None
        self._tmr_tok = None
        self._deberta_acad_mod = None
        self._deberta_acad_tok = None
        self._xlm_mod = None
        self._xlm_tok = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def get_binoculars_observer(self):
        """Charge et met en cache persistant le modèle Observer (google/gemma-4-E2B)."""
        if self._bino_obs_mod is None:
            import torch
            from transformers import AutoTokenizer
            try:
                from transformers import Gemma4ForConditionalGeneration as GemmaModelClass
            except ImportError:
                try:
                    from transformers import AutoModelForCausalLM as GemmaModelClass
                except ImportError:
                    from transformers import AutoModel as GemmaModelClass

            self._bino_obs_tok = AutoTokenizer.from_pretrained(
                BINOCULARS_OBSERVER_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            if not self._bino_obs_tok.pad_token:
                self._bino_obs_tok.pad_token = self._bino_obs_tok.eos_token or "<pad>"

            quant_config = None
            if self.device == "cuda":
                try:
                    import bitsandbytes
                    from transformers import BitsAndBytesConfig
                    quant_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.bfloat16 if self.bfloat16_supported else torch.float16,
                        bnb_4bit_quant_type="nf4",
                    )
                except Exception:
                    quant_config = None

            load_kwargs_obs = {"token": self.hf_token, "local_files_only": self.local_files_only}
            if quant_config is not None:
                load_kwargs_obs["quantization_config"] = quant_config
                load_kwargs_obs["device_map"] = {"": self.device}
            else:
                load_kwargs_obs["torch_dtype"] = self.causal_dtype

            self._bino_obs_mod = GemmaModelClass.from_pretrained(BINOCULARS_OBSERVER_ID, **load_kwargs_obs)
            if quant_config is None:
                self._bino_obs_mod = self._bino_obs_mod.to(self.device)
            self._bino_obs_mod.eval()
        return self._bino_obs_tok, self._bino_obs_mod

    def get_binoculars_performer(self):
        """Charge et met en cache persistant le modèle Performer (google/gemma-4-E2B-it)."""
        if self._bino_perf_mod is None:
            import torch
            from transformers import AutoTokenizer
            try:
                from transformers import Gemma4ForConditionalGeneration as GemmaModelClass
            except ImportError:
                try:
                    from transformers import AutoModelForCausalLM as GemmaModelClass
                except ImportError:
                    from transformers import AutoModel as GemmaModelClass

            self._bino_perf_tok = AutoTokenizer.from_pretrained(
                BINOCULARS_PERFORMER_ID, token=self.hf_token, local_files_only=self.local_files_only
            )
            if not self._bino_perf_tok.pad_token:
                self._bino_perf_tok.pad_token = self._bino_perf_tok.eos_token or "<pad>"

            quant_config = None
            if self.device == "cuda":
                try:
                    import bitsandbytes
                    from transformers import BitsAndBytesConfig
                    quant_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.bfloat16 if self.bfloat16_supported else torch.float16,
                        bnb_4bit_quant_type="nf4",
                    )
                except Exception:
                    quant_config = None

            load_kwargs_perf = {"token": self.hf_token, "local_files_only": self.local_files_only}
            if quant_config is not None:
                load_kwargs_perf["quantization_config"] = quant_config
                load_kwargs_perf["device_map"] = {"": self.device}
            else:
                load_kwargs_perf["torch_dtype"] = self.causal_dtype

            self._bino_perf_mod = GemmaModelClass.from_pretrained(BINOCULARS_PERFORMER_ID, **load_kwargs_perf)
            if quant_config is None:
                self._bino_perf_mod = self._bino_perf_mod.to(self.device)
            self._bino_perf_mod.eval()
        return self._bino_perf_tok, self._bino_perf_mod

    def unload_binoculars(self):
        """Libère intégralement le duo Binoculars de la mémoire VRAM."""
        import gc
        import torch
        self._bino_obs_mod = None
        self._bino_obs_tok = None
        self._bino_perf_mod = None
        self._bino_perf_tok = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def unload_all(self):
        """Libère l'ensemble des encodeurs et du duo Binoculars de la mémoire VRAM."""
        self.unload_encoders()
        self.unload_binoculars()


# ============================================================================
# 4. INFÉRENCE DES MODÈLES SOTA (COHORTE 1, 2, 3)
# ============================================================================

# --- 1. DeBERTa-v3 RAID SOTA (20%) ---
def score_deberta_raid(text: str, manager: ModelManager) -> Dict[str, Any]:
    """Évalue la probabilité IA via DeBERTa-v3 RAID SOTA (desklib)."""
    tok, mod = manager.get_deberta_raid()
    if mod is None:
        raise RuntimeError(f"Échec de chargement du modèle {DEBERTA_RAID_ID}")

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


# --- 2. ModernBERT Long-Context (20%) ---
def score_modernbert_long(text: str, manager: ModelManager) -> Dict[str, Any]:
    """Évalue la probabilité IA via ModernBERT Long-Context (GeorgeDrayson, 8192 tokens natifs)."""
    tok, mod = manager.get_modernbert()
    if mod is None:
        raise RuntimeError(f"Échec de chargement du modèle {MODERNBERT_ID}")

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


# --- 3. TMR RoBERTa Anti-Paraphrase (15%) ---
def score_tmr_roberta(text: str, manager: ModelManager) -> Dict[str, Any]:
    """Évalue la probabilité IA via TMR RoBERTa Anti-Paraphrase (Oxidane, Hard-Negative Mining sur RAID)."""
    tok, mod = manager.get_tmr_roberta()
    if mod is None:
        raise RuntimeError(f"Échec de chargement du modèle {TMR_ROBERTA_ID}")

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


# --- 4. DeBERTa-v3 Academic SOTA (15%) ---
def score_deberta_academic(text: str, manager: ModelManager) -> Dict[str, Any]:
    """Évalue la probabilité IA via DeBERTa-v3 Academic SOTA (desklib/ai-text-detector-academic-v1.01)."""
    tok, mod = manager.get_deberta_academic()
    if mod is None:
        raise RuntimeError(f"Échec de chargement du modèle {DEBERTA_ACADEMIC_ID}")

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
        "model_id": DEBERTA_ACADEMIC_ID
    }


# --- 5. XLM-RoBERTa Multilingue (10%) ---
def score_xlm_roberta(text: str, manager: ModelManager) -> Dict[str, Any]:
    """Évalue la probabilité IA via XLM-RoBERTa Multilingue (yaya36095/xlm-roberta-text-detector)."""
    tok, mod = manager.get_xlm_roberta()
    if mod is None:
        raise RuntimeError(f"Échec de chargement du modèle {XLM_ROBERTA_ID}")

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
            # label 1 = AI, label 0 = HUMAN
            p_ai = float(torch.softmax(out, dim=-1)[0][1].item())
            scores.append(p_ai)

    mean_s = sum(scores) / len(scores) if scores else 0.0
    max_s = max(scores) if scores else 0.0
    blended = 0.70 * mean_s + 0.30 * max_s

    return {
        "score": float(blended),
        "mean_score": float(mean_s),
        "max_score": float(max_s),
        "model_id": XLM_ROBERTA_ID
    }


# --- 6. Binoculars via Gemma-4-E2B (35%) ---
def score_binoculars_gemma(
    text: str,
    manager: ModelManager,
    max_tokens: int = 512,
    allow_partial: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Calcule le score Binoculars (Hans et al., ICML 2024) via le duo Gemma-4-E2B :
      Observer : google/gemma-4-E2B
      Performer : google/gemma-4-E2B-it
    Les modèles sont conservés en mémoire GPU (keep_loaded=True) pour une persistance VRAM sans rechargement.
    """
    import torch
    import numpy as np

    try:
        # 1. Observer (google/gemma-4-E2B)
        obs_tok, obs_mod = manager.get_binoculars_observer()
        enc = obs_tok(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_tokens,
            padding=False
        )
        input_ids = enc["input_ids"].to(manager.device)
        attention_mask = enc.get("attention_mask", torch.ones_like(input_ids)).to(manager.device)

        with torch.no_grad():
            out_obs = obs_mod(input_ids=input_ids, attention_mask=attention_mask)
            observer_logits = out_obs.logits.cpu().float()

        # Si VRAM contrainte et keep_loaded désactivé, décharger observer
        if not manager.keep_loaded:
            manager.unload_binoculars()

        # 2. Performer (google/gemma-4-E2B-it)
        perf_tok, perf_mod = manager.get_binoculars_performer()
        with torch.no_grad():
            out_perf = perf_mod(input_ids=input_ids, attention_mask=attention_mask)
            performer_logits = out_perf.logits.cpu().float()

        if not manager.keep_loaded:
            manager.unload_binoculars()

        # 3. Calcul Métrologique Binoculars
        shifted_perf_logits = performer_logits[..., :-1, :].contiguous()
        shifted_labels = input_ids.cpu()[..., 1:].contiguous()
        shifted_mask = attention_mask.cpu()[..., 1:].contiguous()

        ce_loss_fn = torch.nn.CrossEntropyLoss(reduction="none")
        loss = ce_loss_fn(shifted_perf_logits.transpose(1, 2), shifted_labels)
        masked_loss = (loss * shifted_mask).sum() / shifted_mask.sum().clamp(min=1e-8)
        ppl = float(masked_loss.item())

        vocab_size = observer_logits.shape[-1]
        p_proba = torch.softmax(observer_logits, dim=-1).view(-1, vocab_size)
        q_scores = performer_logits.view(-1, vocab_size)

        ce_x = ce_loss_fn(input=q_scores, target=p_proba).view(observer_logits.shape[0], observer_logits.shape[1])
        padding_mask = (input_ids.cpu() != obs_tok.pad_token_id).float()
        x_ppl = float(((ce_x * padding_mask).sum() / padding_mask.sum().clamp(min=1e-8)).item())

        b_score = (ppl / x_ppl) if x_ppl > 0 else 1.0

        # Calibration sigmoïde de probabilité IA
        # B(s) < 0.88 -> Forte probabilité IA (B_score bas)
        theta = 0.88
        sigma = 0.06
        p_ai_bino = 1.0 / (1.0 + math.exp((b_score - theta) / sigma))
        p_ai_bino = max(0.0, min(1.0, p_ai_bino))

        return {
            "score": float(round(p_ai_bino, 4)),
            "b_score": float(round(b_score, 4)),
            "ppl": float(round(ppl, 3)),
            "x_ppl": float(round(x_ppl, 3)),
            "threshold": theta,
            "model_observer": BINOCULARS_OBSERVER_ID,
            "model_performer": BINOCULARS_PERFORMER_ID
        }

    except Exception as e:
        if allow_partial:
            sys.stderr.write(f"⚠️ [AVERTISSEMENT] Binoculars indisponible ({e}). Bascule bayésienne sur les autres composants.\n")
            return None
        raise RuntimeError(
            f"❌ [FAIL-STOP] Échec du module Binoculars Gemma-4-E2B : {e}\n"
            "Conformément à la doctrine Fail-Stop d'Henri, l'exécution est interrompue.\n"
            "Pour autoriser l'exécution sans Binoculars en cas d'anomalie matérielle, spécifiez '--allow-partial'."
        ) from e


# --- 7. Stylométrie & Entropie (10%) ---
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
# 5. ORCHESTRATION DU PIPELINE À 7 COMPOSANTS & HEATMAP
# ============================================================================

def analyze_text(
    text: str,
    filename: Optional[str] = None,
    device_override: Optional[str] = None,
    hf_token: Optional[str] = None,
    allow_partial: bool = False,
    offline: bool = False,
    compliance_threshold: float = 0.10,
    keep_loaded: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Exécute l'analyse SOTA unifiée à 7 composants :
    - Cohorte 1 : Encodeurs FP16 (DeBERTa RAID, ModernBERT, TMR, DeBERTa Academic, XLM) + Heatmap
    - Cohorte 2 : Binoculars Gemma-4-E2B (Observer + Performer) [Obligatoire]
    - Cohorte 3 : Moteur Stylométrique & Entropique (CPU)
    - Fusion Bayésienne dynamique (renormalisation à 1.0)
    Modèles conservés en mémoire GPU (keep_loaded=True) pour inférence ultra-rapide sans rechargement.
    """
    _ = kwargs.pop("fast_mode", None)
    _ = kwargs.pop("fast", None)

    # Validation du token Hugging Face
    resolved_token = resolve_hf_token(hf_token, required=not (allow_partial or offline))

    clean_txt = clean_raw_text(text, filename)
    manager = ModelManager.get_instance(device_override, resolved_token, local_files_only=offline, keep_loaded=keep_loaded)

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

    results_models: Dict[str, Any] = {}
    active_weights: Dict[str, float] = {}

    # ------------------------------------------------------------------------
    # COHORTE 1 : LES 5 ENCODEURS FP16 & CARTOGRAPHIE HEATMAP
    # ------------------------------------------------------------------------
    # 1. DeBERTa-v3 RAID SOTA (15%)
    try:
        deb_raid = score_deberta_raid(clean_txt, manager)
        results_models["deberta_raid"] = deb_raid
        active_weights["deberta_raid"] = NOMINAL_WEIGHTS["deberta_raid"]
    except Exception as e:
        if not allow_partial:
            raise RuntimeError(
                f"❌ [FAIL-STOP] Échec du modèle obligatoire DeBERTa RAID ({DEBERTA_RAID_ID}) : {e}\n"
                "La doctrine Fail-Stop d'Henri interdit tout fallback silencieux ou redistribution arbitraire de poids.\n"
                "Pour autoriser une inférence partielle en cas de composant manquant, utilisez '--allow-partial'."
            ) from e
        sys.stderr.write(f"⚠️ [AVERTISSEMENT] DeBERTa RAID indisponible : {e}\n")

    # 2. ModernBERT Long-Context (15%)
    try:
        mod_long = score_modernbert_long(clean_txt, manager)
        results_models["modernbert_long"] = mod_long
        active_weights["modernbert_long"] = NOMINAL_WEIGHTS["modernbert_long"]
    except Exception as e:
        if not allow_partial:
            raise RuntimeError(
                f"❌ [FAIL-STOP] Échec du modèle obligatoire ModernBERT ({MODERNBERT_ID}) : {e}\n"
                "La doctrine Fail-Stop d'Henri interdit tout fallback silencieux ou redistribution arbitraire de poids.\n"
                "Pour autoriser une inférence partielle en cas de composant manquant, utilisez '--allow-partial'."
            ) from e
        sys.stderr.write(f"⚠️ [AVERTISSEMENT] ModernBERT indisponible : {e}\n")

    # 3. TMR RoBERTa Anti-Paraphrase (12%)
    try:
        tmr_res = score_tmr_roberta(clean_txt, manager)
        results_models["tmr_roberta"] = tmr_res
        active_weights["tmr_roberta"] = NOMINAL_WEIGHTS["tmr_roberta"]
    except Exception as e:
        if not allow_partial:
            raise RuntimeError(
                f"❌ [FAIL-STOP] Échec du modèle obligatoire TMR RoBERTa ({TMR_ROBERTA_ID}) : {e}\n"
                "La doctrine Fail-Stop d'Henri interdit tout fallback silencieux ou redistribution arbitraire de poids.\n"
                "Pour autoriser une inférence partielle en cas de composant manquant, utilisez '--allow-partial'."
            ) from e
        sys.stderr.write(f"⚠️ [AVERTISSEMENT] TMR RoBERTa indisponible : {e}\n")

    # 4. DeBERTa-v3 Academic SOTA (10%)
    try:
        deb_acad = score_deberta_academic(clean_txt, manager)
        results_models["deberta_academic"] = deb_acad
        active_weights["deberta_academic"] = NOMINAL_WEIGHTS["deberta_academic"]
    except Exception as e:
        if not allow_partial:
            raise RuntimeError(
                f"❌ [FAIL-STOP] Échec du modèle obligatoire DeBERTa Academic ({DEBERTA_ACADEMIC_ID}) : {e}\n"
                "La doctrine Fail-Stop d'Henri interdit tout fallback silencieux ou redistribution arbitraire de poids.\n"
                "Pour autoriser une inférence partielle en cas de composant manquant, utilisez '--allow-partial'."
            ) from e
        sys.stderr.write(f"⚠️ [AVERTISSEMENT] DeBERTa Academic indisponible : {e}\n")

    # 5. XLM-RoBERTa Multilingue (7%)
    try:
        xlm_res = score_xlm_roberta(clean_txt, manager)
        results_models["xlm_roberta"] = xlm_res
        active_weights["xlm_roberta"] = NOMINAL_WEIGHTS["xlm_roberta"]
    except Exception as e:
        if not allow_partial:
            raise RuntimeError(
                f"❌ [FAIL-STOP] Échec du modèle obligatoire XLM-RoBERTa ({XLM_ROBERTA_ID}) : {e}\n"
                "La doctrine Fail-Stop d'Henri interdit tout fallback silencieux ou redistribution arbitraire de poids.\n"
                "Pour autoriser une inférence partielle en cas de composant manquant, utilisez '--allow-partial'."
            ) from e
        sys.stderr.write(f"⚠️ [AVERTISSEMENT] XLM-RoBERTa indisponible : {e}\n")

    # --- Cartographie Paragraphes & Phrases (exécutée tant que Cohorte 1 est en VRAM) ---
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

        # Inférence rapide par ModernBERT
        tok_m, mod_m = manager._modernbert_tok, manager._modernbert_mod
        if mod_m is not None and tok_m is not None:
            inp_m = tok_m(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=256).to(manager.device)
            with torch.no_grad():
                out_m = mod_m(**inp_m).logits
                p_m_list = torch.softmax(out_m, dim=-1)[:, 1].tolist()
        else:
            p_m_list = [0.0] * len(batch_texts)

        # Inférence rapide par TMR RoBERTa
        tok_t, mod_t = manager._tmr_tok, manager._tmr_mod
        if mod_t is not None and tok_t is not None:
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
                para_p_ai = 0.0
        else:
            para_p_ai = 0.0

        if para_p_ai < compliance_threshold:
            p_tag = "HUMAIN"
            p_icon = "🟢"
        elif para_p_ai < 0.35:
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

    # DÉCHARGEMENT CONDITIONNEL COHORTE 1 (uniquement si VRAM restreinte < 8 Go et keep_loaded=False)
    if not manager.keep_loaded:
        manager.unload_encoders()

    # ------------------------------------------------------------------------
    # COHORTE 2 : BINOCULARS VIA GEMMA-4-E2B (35% - LEADER INCONTESTÉ OBLIGATOIRE)
    # ------------------------------------------------------------------------
    bino_res = score_binoculars_gemma(clean_txt, manager, allow_partial=allow_partial)
    if bino_res is not None:
        results_models["binoculars_gemma"] = bino_res
        active_weights["binoculars_gemma"] = NOMINAL_WEIGHTS["binoculars_gemma"]

    # ------------------------------------------------------------------------
    # COHORTE 3 : MOTEUR STYLOMÉTRIQUE & ENTROPIQUE (6% - CPU)
    # ------------------------------------------------------------------------
    stylo_res = score_stylometric(clean_txt)
    results_models["stylometric_entropy"] = stylo_res
    active_weights["stylometric_entropy"] = NOMINAL_WEIGHTS["stylometric_entropy"]

    # ------------------------------------------------------------------------
    # FUSION BAYÉSIENNE DYNAMIQUE RENORMALISÉE À 1.0
    # ------------------------------------------------------------------------
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

    # Mise en forme du breakdown
    breakdown_formatted = {}
    for k, v in results_models.items():
        nom_w = NOMINAL_WEIGHTS.get(k, 0.0)
        eff_w = (active_weights[k] / total_weight) if total_weight > 0 else 0.0
        breakdown_formatted[k] = {
            "nominal_weight": nom_w,
            "effective_weight": float(round(eff_w, 3)),
            "score": float(round(v["score"], 4)),
            "score_percent": float(round(v["score"] * 100, 1)),
            "details": v
        }

    # Déchargement final uniquement si keep_loaded est explicitement False
    if not keep_loaded:
        manager.unload_all()

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


def analyze_texts_batch(
    texts: List[str],
    filenames: Optional[List[Optional[str]]] = None,
    device_override: Optional[str] = None,
    hf_token: Optional[str] = None,
    allow_partial: bool = False,
    offline: bool = False,
    compliance_threshold: float = 0.10,
    keep_loaded: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Évalue un lot de textes de manière vectorisée et optimisée sans rechargement de modèles.
    Les 5 encodeurs et le duo Binoculars restent chauds en mémoire GPU tout au long de l'évaluation du lot.
    """
    if not texts:
        return []

    # Validation du token Hugging Face
    resolved_token = resolve_hf_token(hf_token, required=not (allow_partial or offline))
    manager = ModelManager.get_instance(device_override, resolved_token, local_files_only=offline, keep_loaded=keep_loaded)

    if filenames is None:
        filenames = [None] * len(texts)

    results = []
    for txt, fname in zip(texts, filenames):
        res = analyze_text(
            text=txt,
            filename=fname,
            device_override=device_override,
            hf_token=resolved_token,
            allow_partial=allow_partial,
            offline=offline,
            compliance_threshold=compliance_threshold,
            keep_loaded=True,
            **kwargs
        )
        results.append(res)

    if not keep_loaded:
        manager.unload_all()

    return results


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
    lines.append(" 🧠 MOTEUR DÉTECTEUR IA — ARMADA SOTA UNIFIÉE 7 COMPOSANTS")
    lines.append("=" * 80)

    # 1. Résumé synthétique
    lines.append(f"\n📊 SCORE GLOBAL P(AI) : {g['p_ai_percent']:.1f}% | VERDICT : {g['verdict_icon']} {g['verdict']} [{g['status_label']}]")
    lines.append(f"   Périphérique : {results['device'].upper()} | Mots : {st['word_count']} | Phrases : {st['sentence_count']} | Paragraphes : {st['paragraph_count']}")

    # 2. Breakdown des 7 acteurs SOTA
    lines.append("\n" + "-" * 80)
    lines.append("🔬 DÉCOMPOSITION DE L'ARMADA SOTA (7 COMPOSANTS) :")
    lines.append("-" * 80)

    labels_map = {
        "binoculars_gemma": ("Binoculars Gemma-4-E2B", "35%"),
        "deberta_raid": ("DeBERTa-v3 RAID SOTA", "15%"),
        "modernbert_long": ("ModernBERT Long-Context", "15%"),
        "tmr_roberta": ("TMR RoBERTa Anti-Paraphrase", "12%"),
        "deberta_academic": ("DeBERTa-v3 Academic SOTA", "10%"),
        "xlm_roberta": ("XLM-RoBERTa Multilingue", "7%"),
        "stylometric_entropy": ("Stylométrie & Entropie", "6%"),
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
            elif key == "deberta_academic":
                extra = f"(Modèle: {DEBERTA_ACADEMIC_ID}, Academic SOTA)"
            elif key == "xlm_roberta":
                extra = f"(Modèle: {XLM_ROBERTA_ID}, Cross-lingual)"
            elif key == "binoculars_gemma":
                extra = f"(B-Score: {details.get('b_score', 0):.4f}, PPL: {details.get('ppl', 0):.2f}, X-PPL: {details.get('x_ppl', 0):.2f})"
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
# 7. CLI POINT D'ENTRÉE ULTRA-SIMPLE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Moteur Détecteur IA Multi-Modèles SOTA (Armada Unifiée 7 Composants)",
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
    parser.add_argument("--hf-token", type=str, default=None, help="Token Hugging Face pour l'accès aux checkpoints")
    parser.add_argument("--allow-partial", action="store_true", help="Autorise la bascule bayésienne si un composant échoue (désactive le Fail-Stop strict)")
    parser.add_argument("--offline", action="store_true", help="Utilise uniquement les fichiers déjà présents dans le cache Hugging Face local")

    args = parser.parse_args()

    raw_text = None
    filename = None

    if args.input:
        target_path = args.input
        if not os.path.isfile(target_path) and os.path.isfile(os.path.join("..", target_path)):
            target_path = os.path.join("..", target_path)
        if os.path.isfile(target_path):
            filename = target_path
            try:
                with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                    raw_text = f.read()
            except Exception as e:
                print(f"Erreur de lecture du fichier '{target_path}': {e}", file=sys.stderr)
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

    try:
        results = analyze_text(
            text=raw_text,
            filename=filename,
            device_override=device_override,
            hf_token=args.hf_token,
            allow_partial=args.allow_partial,
            offline=args.offline,
            compliance_threshold=args.threshold,
            keep_loaded=True
        )
    except Exception as e:
        sys.stderr.write(f"\n{e}\n")
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_console_report(results, show_heatmap=not args.no_heatmap))


if __name__ == "__main__":
    main()
