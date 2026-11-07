#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
harpy_entity_validator.py — Moteur de validation et d'assemblage des fiches d'entités Harpy (v3).
Localisation : c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/harpy_entity_validator.py

Valide et assemble une fiche d'entité JDR selon le format canonique en 5 blocs d'Henri (v3) :
1. Image de l'entité (![[...]])
2. Description externe (code text, <= 100 caractères stricts, apparence physique pure)
3. Ouverture MJ & Secrets détaillés :
   - '## 🎭 Comment l'improviser ?' : description d'aide à l'improvisation (mots en **gras**, infos dévoilables)
   - '## 🗝️ Qui est-il vraiment ?' : tout ce que le MJ doit savoir (histoire, origine, motivations, secrets, >= 350 car.)
   - '## 🔒 Quels sont les secrets MJ, l'inventaire et les coulisses de [Nom] ?' : sections détaillées H3
4. Description joueurs (code markdown, 1 ou 2 paragraphes riches, >= 450 caractères, synesthésies,
   détails d'ambiance et style compatibles avec le moment et le lieu du scénario, sans secrets, angle aléatoire via --tirage)
5. Fiche mécanique Harpy (code text, texte pur strict, émojis, zéro markdown, <= 70 car./ligne)

Doctrine Fail-Fast & Zéro Mention de Sources :
- Interdiction formelle de toute mention de source dans la note produite (p. XX, module, transcript,
  voicenote, "canon", "proposition MJ") -> la traçabilité est réservée au rapport d'agent.
- Bloc 4 rigoureusement borné à 1 ou 2 paragraphes et >= 450 caractères.
- Paragraphe 2 (résumé de fond MJ) rigoureusement borné à >= 350 caractères.
- Tout écart interrompt immédiatement le script avec un code retour 1 et des messages explicites.
"""

import sys
import os
import re
import json
import argparse
import difflib
import subprocess
import unicodedata
import shutil
import random
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set

# Encodage UTF-8 strict sous Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

import yaml


# ============================================================================
# 1. CONSTANTES & MOTS-CLÉS DE VALIDATION
# ============================================================================

MAX_DESCRIPTION_EXTERNE_CHARS = 100
MIN_DESCRIPTION_JOUEURS_CHARS = 450
MIN_RESUME_MJ_CHARS = 350
DEFAULT_MAX_HARPY_LINE_LENGTH = 70
DEFAULT_NEURAL_AI_THRESHOLD = 0.10  # Seuil pour l'option neurale explicite --use-neural-ai

# ============================================================================
# LISTES DE TIRAGE ALÉATOIRE D'ANGLES NARRATIFS (--tirage)
# ============================================================================

TIRAGE_SENS_DOMINANTS = [
    "Ouïe & acoustique (grincement d'acier poli, respiration rauque, claquement de pas pesants, timbre de voix sourd)",
    "Odorat & effluves (encens froid de sanctuaire, cuir noirci et suif, relents métalliques d'huile d'armure)",
    "Toucher & température (lourdeur accablante de l'air, contact rugueux du fer trempé, froid minéral de la pierre)",
    "Vue & contrastes d'ombre (ombres portées tranchantes sous une lumière crue, éclat terne du métal poli, pupilles fixes)",
    "Synesthésie sensorielle (cliquetis d'armes perçu comme une brûlure froide, odeur de poussière à tonalité acide)"
]

TIRAGE_POINTS_DE_VUE = [
    "En contre-plongée (silhouette surélevée sur une estrade, un chariot ou un perron, toisant l'observateur)",
    "À hauteur d'yeux en face-à-face (confrontation frontale directe, fixité du regard à hauteur d'homme)",
    "De biais / profil décalé (découverte par une perspective oblique, posture asymétrique captée au tournant)",
    "Regard périphérique capté par surprise (présence lourde qui s'impose au champ de vision avant d'être fixée)"
]

TIRAGE_DISTANCES = [
    "Distance d'observation / sécurité (10 à 15 mètres, silhouette générale, port d'armes et lourdeur de la stature)",
    "Moyenne portée (4 à 6 mètres, travail du harnois, qualité des étoffes, reflets sur les pièces de cuir et d'acier)",
    "Proximité immédiate (2 à 3 mètres, souffle perceptible, tension musculaire et micro-mouvements des doigts)"
]

TIRAGE_MOMENTS_LUMIERE = [
    "Lumière crue et poussiéreuse de début d'après-midi (chaleur lourde, réverbération sur le métal, poussière en suspension)",
    "Pénombre étouffée de torches vacillantes (lueurs tremblantes découpant des reflets rouges sur le fer)",
    "Éclat de midi (contours nets, ombres courtes découpées à la verticale, absence d'artifice)",
    "Brume humide ou froidure matinale (air dense, gouttelettes condensées sur le métal, silhouette émergeant du voile)"
]

TIRAGE_DETAILS_INATTENDUS = [
    "Usure singulière ou rivet dépareillé sur un harnois ou un équipement par ailleurs rigoureusement entretenu",
    "Immobilité anormale / fixité statuaire démentant la nervosité ou le vacarme environnant",
    "Accessoire rituel discret, symbole patiné ou clé en fer suspendue à portée de main immédiate",
    "Rythme respiratoire lent et régulier contrastant crûment avec l'agitation des subordonnés",
    "Trace de suie incrustée ou rayure profonde sur une pièce maîtresse d'armure"
]

TIRAGE_RYTHMES_PHRASE = [
    "Staccato (phrases courtes, percutantes, attaques directes sans conjonctions superflues)",
    "Période descriptive ample (deux phrases riches équilibrant sensations matérielles et atmosphère)",
    "Attaque par un détail sensoriel brut, suivie d'un élargissement atmosphérique sur l'entourage",
    "Alternance cadence vive / cadence lourde (rythme syncopé entre tension et immobilité)"
]

def tirer_angles_narratifs() -> Dict[str, str]:
    """Tire au sort un angle d'entrée pour stimuler l'écriture aléatoire du Bloc 4."""
    return {
        "sens_dominant": random.choice(TIRAGE_SENS_DOMINANTS),
        "point_de_vue": random.choice(TIRAGE_POINTS_DE_VUE),
        "distance": random.choice(TIRAGE_DISTANCES),
        "moment_lumiere": random.choice(TIRAGE_MOMENTS_LUMIERE),
        "detail_inattendu": random.choice(TIRAGE_DETAILS_INATTENDUS),
        "rythme_phrase": random.choice(TIRAGE_RYTHMES_PHRASE),
    }

# ============================================================================
# RÈGLE DRY : IMPORT DES RÈGLES DE STYLE CANONIQUES DEPUIS style_guard.py
# ============================================================================

def _resolve_and_import_style_guard():
    """
    Résout le module canonique doc_version_mcp.style_guard et importe NODE_HARD_BLOCKER_TYPES
    et FR_MECHANICAL_TRANSITIONS directement à la source.
    Échec bloquant immédiat (Fail-Fast, aucun repli silencieux) si le module est introuvable.
    """
    candidates = [
        Path.home() / "Documents" / "code" / "doc-version-mcp" / "src",
    ]
    env_path = os.environ.get("DOC_VERSION_MCP_SRC")
    if env_path and Path(env_path).is_dir():
        candidates.insert(0, Path(env_path))

    target_src = None
    for cand in candidates:
        if (cand / "doc_version_mcp" / "style_guard.py").is_file():
            target_src = cand
            break

    if target_src is None:
        raise RuntimeError(
            "Échec Règle DRY : Impossible de localiser 'doc_version_mcp.style_guard'. "
            "Le validateur Harpy exige l'import direct des définitions canoniques de doc-version-mcp."
        )

    str_src = str(target_src.resolve())
    if str_src not in sys.path:
        sys.path.insert(0, str_src)

    try:
        from doc_version_mcp.style_guard import check_style as _IMPORTED_CHECK_STYLE
        return _IMPORTED_CHECK_STYLE
    except Exception as e:
        raise RuntimeError(f"Erreur critique lors de l'import depuis doc_version_mcp.style_guard : {e}")

# Import canonique strict DRY depuis doc_version_mcp.style_guard
check_style = _resolve_and_import_style_guard()

# Motifs Markdown strictement interdits dans le bloc texte pur Harpy (Bloc 5)
FORBIDDEN_HARPY_PATTERNS = [
    (r"\|", "Tableau Markdown (caractère pipe '|')"),
    (r"\*\*", "Gras Markdown ('**')"),
    (r"__", "Gras Markdown ('__')"),
    (r"^\s*#+\s+", "Titre Markdown ('#')"),
    (r"`", "Backtick de code ('`')"),
    (r"\[\[.*?\]\]", "Wikilink Obsidian ('[[...]]')"),
    (r"\[.*?\]\(.*?\)", "Lien Markdown standard ('[texte](url)')"),
    (r"^\s*>\s*", "Citation Markdown ('>')"),
    (r"^\s*-\s*\[[ xX]\]", "Case à cocher Markdown ('- [ ]')"),
]

# Mots-clés de rôle, classe, faction, fonction et comportement interdits dans le Bloc 2 (Description externe)
FORBIDDEN_EXTERNAL_DESC_KEYWORDS = [
    # Classes & rôles de jeu
    "prêtre", "prêtresse", "clerc", "paladin", "mage", "magicien", "sorcier", "ensorceleur",
    "druide", "moine", "barde", "roublard", "voleur", "guerrier", "chevalier", "novice",
    "inquisiteur", "assassin", "soldat", "garde", "capitaine", "seigneur", "chef", "meneur",
    "parrain", "commandant", "mercenaire", "brigand", "bandit", "archer", "tireur",
    # Factions, divinités & religions
    "asmodéus", "asmodeus", "iomedae", "sarenrae", "torag", "abadar", "zon-kuthon",
    "ordre du chevalet", "chevalier infernal", "chevaliers infernaux", "culte", "secte",
    "diable", "démon", "infernal", "infernale", "bâtards d'érèbe", "enfants de couronne",
    # Fonctions narratives, actions & comportements
    "convoi", "prisonnier", "escorte", "détention", "cellulaire",
    "mène", "dirige", "commande", "transporte", "surveille",
    "combat", "fanatique", "loyal", "chaotique", "mauvais", "neutre", "bon",
    "traître", "espion"
]

# Mots-clés déclencheurs d'alerte pour traquer les fuites de secrets dans la description joueurs (Bloc 4)
SECRET_LEAK_KEYWORDS = [
    "secret", "coulisse", "complot", "traître", "trahison", "espion",
    "citadelle de rivad", "mandat secret",
    "menottes", "cellulaire", "sabotage dd", "volonté dd", "réflexes dd",
    "alignement", "loyal mauvais", "chaotique mauvais", "fp 1/", "dv"
]

# Motifs de mentions de sources formellement interdits dans toute la note (v3)
FORBIDDEN_SOURCE_PATTERNS = [
    (r"(?i)\(proposition\s+mj\)", "Mention de métadonnée '(proposition MJ)'"),
    (r"(?i)\bproposition\s+mj\b", "Mention de source 'proposition MJ'"),
    (r"(?i)\(canon\)", "Mention de métadonnée '(canon)'"),
    (r"(?i)\bcanonique\b", "Mention de terme métatextuel 'canonique'"),
    (r"(?i)\bmodule\b", "Mention de source 'module'"),
    (r"(?i)\btranscript\b", "Mention de source 'transcript'"),
    (r"(?i)\bvoicenote\b", "Mention de source 'voicenote'"),
    (r"(?i)\bp\.\s*\d+\b", "Mention de numéro de page 'p. XX'"),
    (r"(?i)\bpages?\s*\d+\b", "Mention de pagination 'page XX'"),
]

# Marqueurs de scène contextuelle déconseillés dans le Bloc 4 (Description Joueurs)
# Règle d'Henri : "Les descriptions pour les joueurs doivent toujours être générales, elles ne doivent pas être liées à un contexte spécifique."
SCENE_CONTEXT_MARKERS = [
    # 1. Moments de la journée
    (r"(?i)\b(?:à\s+l'|dès\s+l')?aube\b", "moment de la journée ('aube')"),
    (r"(?i)\b(?:au\s+|ce\s+)?matin(?:ale?s?)?\b", "moment de la journée ('matin')"),
    (r"(?i)\b(?:ce\s+|en\s+|début\s+d')?après-midi\b", "moment de la journée ('après-midi')"),
    (r"(?i)\b(?:au\s+)?crépuscule\b", "moment de la journée ('crépuscule')"),
    (r"(?i)\b(?:à\s+la\s+)?nuit\s+tombante\b", "moment de la journée ('nuit tombante')"),
    (r"(?i)\bce\s+soir\b", "moment de la journée ('ce soir')"),
    (r"(?i)\bplein\s+midi\b", "moment de la journée ('plein midi')"),

    # 2. Météo et conditions atmosphériques ponctuelles
    (r"(?i)\b(?:dans\s+la\s+|épaisse\s+)?brume(?:use)?\b", "météo ponctuelle ('brume')"),
    (r"(?i)\b(?:sous\s+la\s+|fine\s+)?pluie\b", "météo ponctuelle ('pluie')"),
    (r"(?i)\bsoleil\s+cuisant\b", "météo ponctuelle ('soleil cuisant')"),
    (r"(?i)\bchaleur\s+(?:lourde|écrasante)\b", "météo ponctuelle ('chaleur lourde')"),
    (r"(?i)\baverse\b", "météo ponctuelle ('averse')"),
    (r"(?i)\btempête\b", "météo ponctuelle ('tempête')"),
    (r"(?i)\bbrouillard\b", "météo ponctuelle ('brouillard')"),

    # 3. Situations narratives en cours / actions immédiates d'une scène
    (r"(?i)\ben\s+ce\s+moment\b", "situation immédiate en cours ('en ce moment')"),
    (r"(?i)\battend\s+l'assaut\b", "situation immédiate en cours ('attend l\\'assaut')"),
    (r"(?i)\b(?:est\s+)?tapi(?:e|s|es)?\b", "situation immédiate en cours ('tapi')"),
    (r"(?i)\bguette(?:nt)?\b", "situation immédiate en cours ('guette')"),
    (r"(?i)\bactuellement\b", "situation immédiate en cours ('actuellement')"),
    (r"(?i)\bse\s+cache(?:nt)?\b", "situation immédiate en cours ('se cache')"),
    (r"(?i)\bembusqu(?:é|ée|és|ées)\b", "situation immédiate en cours ('embusqué')"),
    (r"(?i)\bbuissons?\s+d'épines\b", "lieu contextuel de scène ('buissons d\\'épines')"),
]


def check_scene_context_markers(desc: str) -> List[str]:
    """
    Détecte les marqueurs de scène spécifiques (moment de la journée, météo ponctuelle, situation en cours)
    dans la description pour les joueurs (Bloc 4).
    Retourne une liste de messages d'AVERTISSEMENT (jamais bloquants).
    Règle d'Henri : « Les descriptions pour les joueurs doivent toujours être générales, elles ne doivent pas être liées à un contexte spécifique ».
    """
    warnings: List[str] = []
    if not desc or not desc.strip():
        return warnings

    for pattern, label in SCENE_CONTEXT_MARKERS:
        for match in re.finditer(pattern, desc):
            term = match.group(0).strip()
            msg = (
                f"Marqueur de scène contextuelle détecté [{label}] : '{term}'. "
                f"Règle d'Henri : « Les descriptions pour les joueurs doivent toujours être générales, "
                f"elles ne doivent pas être liées à un contexte spécifique »."
            )
            warnings.append(msg)

    return list(dict.fromkeys(warnings))


# ============================================================================
# 2. CHARGEMENT DU FICHIER SOURCE
# ============================================================================

def load_input_data(filepath: str) -> Dict[str, Any]:
    """Charge les données d'entrée depuis un fichier YAML ou JSON."""
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Fichier d'entrée introuvable : {filepath}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in [".yaml", ".yml"]:
        data = yaml.safe_load(content)
    elif suffix == ".json":
        data = json.loads(content)
    else:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = yaml.safe_load(content)

    if not isinstance(data, dict):
        raise ValueError("Le fichier d'entrée doit contenir un dictionnaire/objet à la racine.")

    return data


# ============================================================================
# 3. CONTRÔLES DE VALIDATION (FAIL-FAST)
# ============================================================================

def validate_forbidden_source_mentions(data: Any, path: str = "document") -> List[str]:
    """
    Vérifie qu'aucune mention de source (page, module, transcript, voicenote, canon, proposition MJ)
    n'est présente dans les données de la note produite.
    La vérification des sources reste obligatoire pour l'agent, mais dans son rapport, pas dans la note.
    """
    errors: List[str] = []
    if isinstance(data, str):
        for pattern, label in FORBIDDEN_SOURCE_PATTERNS:
            match = re.search(pattern, data)
            if match:
                snippet = data[max(0, match.start() - 25):min(len(data), match.end() + 25)].replace("\n", " ")
                errors.append(
                    f"[{path}] Mention de source interdite détectée [{label}] : '...{snippet}...' "
                    f"-> Aucune mention de source ne doit figurer dans la note finale (traçabilité réservée au rapport)."
                )
    elif isinstance(data, dict):
        for k, v in data.items():
            errors.extend(validate_forbidden_source_mentions(v, path=f"{path}.{k}"))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            errors.extend(validate_forbidden_source_mentions(item, path=f"{path}[{idx}]"))
    return errors


def validate_description_externe(
    desc: Optional[str],
    data: Dict[str, Any],
    max_len: int = MAX_DESCRIPTION_EXTERNE_CHARS
) -> Tuple[bool, int, List[str], List[str]]:
    """
    Vérifie la description externe (Bloc 2) :
    - Longueur <= max_len caractères stricts.
    - Apparence physique visible pure exclusivement.
    - Interdiction formelle du nom de l'entité.
    - Interdiction formelle des cibles de wikilinks du document.
    - Interdiction formelle des mots-clés de rôle, fonction, faction, comportement.
    - Détection et avertissement sur les noms propres potentiels.
    Retourne (est_valide, nombre_caracteres, erreurs, avertissements).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not desc or not desc.strip():
        errors.append("La description externe (Bloc 2) est vide ou manquante.")
        return False, 0, errors, warnings

    clean = desc.strip()
    count = len(clean)

    # 1. Longueur
    if count > max_len:
        errors.append(
            f"Description externe trop longue : {count} caractères (maximum strict autorisé : {max_len} caractères). "
            f"Dépassement de {count - max_len} caractère(s)."
        )

    clean_lower = clean.lower()

    # 2. Interdiction du nom de l'entité
    entity_name = str(data.get("nom", "")).strip()
    if entity_name:
        entity_parts = [p.strip() for p in re.split(r"[\s'-]+", entity_name) if len(p.strip()) >= 3]
        for part in entity_parts:
            pattern = rf"\b{re.escape(part.lower())}\b"
            if re.search(pattern, clean_lower):
                errors.append(
                    f"Nom de l'entité interdit dans la description externe : '{part}'. "
                    f"La description externe ne doit mentionner STRICTEMENT que l'apparence physique visible."
                )

    # 3. Interdiction des cibles de wikilinks du document
    raw_doc_text = json.dumps(data, ensure_ascii=False)
    wikilink_matches = re.findall(r"\[\[(.*?)\]\]", raw_doc_text)
    forbidden_targets: Set[str] = set()
    for wm in wikilink_matches:
        target_raw = wm.split("|")[0].split("#")[0].strip()
        target_name = Path(target_raw).stem.strip()
        if target_name and len(target_name) >= 3 and not target_name.endswith((".png", ".jpg", ".jpeg", ".webp")):
            for p in re.split(r"[\s'-]+", target_name):
                if len(p) >= 4 and p.lower() not in {"pour", "avec", "dans", "site", "chariot", "blindé", "pont"}:
                    forbidden_targets.add(p.lower())

    for tgt in forbidden_targets:
        pattern = rf"\b{re.escape(tgt)}\b"
        if re.search(pattern, clean_lower):
            errors.append(
                f"Mention de l'entité liée interdite dans la description externe : '{tgt}'. "
                f"La description externe ne doit donner aucune information de lore, lieu ou personnage lié."
            )

    # 4. Interdiction des mots-clés de fonction, faction, statut, comportement
    for kw in FORBIDDEN_EXTERNAL_DESC_KEYWORDS:
        pattern = rf"\b{re.escape(kw)}\b"
        if re.search(pattern, clean_lower):
            errors.append(
                f"Terme de rôle, faction ou comportement interdit détecté : '{kw}'. "
                f"La description externe ne doit décrire STRICTEMENT que l'apparence physique visible (âge, corpulence, armure/vêtements visibles)."
            )

    # 5. Détection des noms propres potentiels (mots capitalisés en milieu de phrase)
    sentences = re.split(r'[.!?]+', clean)
    for s in sentences:
        s_words = [w for w in re.findall(r'\b[a-zA-ZÀ-ÿ-]+\b', s.strip()) if w]
        if len(s_words) > 1:
            for w in s_words[1:]:
                if w[0].isupper() and w.lower() not in {"d'", "l'", "un", "une", "le", "la", "les"}:
                    warnings.append(
                        f"Nom propre potentiel détecté dans la description externe : '{w}'. "
                        f"Vérifier qu'il ne s'agit pas d'un nom de personnage, lieu ou faction."
                    )

    is_valid = len(errors) == 0
    return is_valid, count, errors, warnings


def validate_bloc_harpy(bloc: Optional[str], max_line_len: int = DEFAULT_MAX_HARPY_LINE_LENGTH) -> Tuple[bool, List[str]]:
    """
    Vérifie que le bloc Harpy (Bloc 5) ne contient AUCUNE syntaxe Markdown
    et respecte la longueur maximale de ligne (<= 70 car.).
    Les apostrophes (' et ’), tirets et le symbole '↳' sont pleinement autorisés.
    """
    errors: List[str] = []
    if not bloc or not bloc.strip():
        errors.append("Le bloc de statistiques Harpy (Bloc 5) est vide ou manquant.")
        return False, errors

    lines = bloc.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        # Vérification des motifs Markdown interdits
        for pattern, label in FORBIDDEN_HARPY_PATTERNS:
            if re.search(pattern, line):
                errors.append(f"Ligne {idx} : Syntaxe Markdown interdite détectée [{label}] -> '{line[:50]}...'")

        # Vérification de la longueur de ligne
        if len(stripped) > max_line_len:
            errors.append(
                f"Ligne {idx} : Ligne trop longue ({len(stripped)} car. > {max_line_len} max) -> '{line[:50]}...'"
            )

    return len(errors) == 0, errors


def extract_ouverture_paragraphs(data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extrait les deux paragraphes d'ouverture de la note :
    1. aide_improvisation (aide à l'improvisation avec mots importants en gras)
    2. resume_mj (résumé de qui est l'entité, son histoire et ses secrets pour le MJ)
    Supporte les formats racine, sous 'ouverture_mj' ou sous 'secrets_mj'.
    """
    aide_impro = ""
    resume_mj = ""

    # 1. Vérification à la racine
    if "aide_improvisation" in data and str(data["aide_improvisation"]).strip():
        aide_impro = str(data["aide_improvisation"]).strip()
    if "resume_mj" in data and str(data["resume_mj"]).strip():
        resume_mj = str(data["resume_mj"]).strip()

    # 2. Vérification sous 'ouverture_mj'
    ouv = data.get("ouverture_mj", {})
    if isinstance(ouv, dict):
        if not aide_impro and "aide_improvisation" in ouv:
            aide_impro = str(ouv["aide_improvisation"]).strip()
        if not resume_mj and "resume_mj" in ouv:
            resume_mj = str(ouv["resume_mj"]).strip()

    # 3. Vérification sous 'secrets_mj'
    sec = data.get("secrets_mj", {})
    if isinstance(sec, dict):
        if not aide_impro and "aide_improvisation" in sec:
            aide_impro = str(sec["aide_improvisation"]).strip()
        if not resume_mj and "resume_mj" in sec:
            resume_mj = str(sec["resume_mj"]).strip()

    return aide_impro, resume_mj


def validate_ouverture_mj(
    aide_impro: str,
    resume_mj: str,
    desc_joueurs: str,
    min_resume_len: int = MIN_RESUME_MJ_CHARS
) -> Tuple[bool, List[str]]:
    """
    Valide les deux paragraphes d'ouverture de la note (v3) :
    - Paragraphe 1 (aide improvisation) : non vide, mots importants en **gras**,
      zéro secret divulgué, distinct de la description joueurs.
    - Paragraphe 2 (résumé MJ) : non vide, longueur >= min_resume_len (défaut : 350 car.),
      résume l'identité réelle, l'origine, les motivations et les secrets profonds.
    """
    errors: List[str] = []

    # Paragraphe 1 : aide improvisation
    if not aide_impro:
        errors.append(
            "Le paragraphe 1 d'ouverture (aide à l'improvisation MJ) est manquant. "
            "Renseigner 'aide_improvisation' avec les éléments dévoilables et mots importants en **gras**."
        )
    else:
        # Vérification des mots en gras
        if not re.search(r"\*\*.*?\*\*", aide_impro):
            errors.append(
                "Le paragraphe 1 d'aide à l'improvisation doit mettre en valeur les mots les plus importants en **gras**."
            )
        # Vérification de fuites de secrets
        aide_lower = aide_impro.lower()
        for kw in SECRET_LEAK_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", aide_lower):
                errors.append(
                    f"Fuite de secret détectée dans le paragraphe 1 d'aide à l'improvisation : '{kw}' "
                    f"-> Ce paragraphe ne doit contenir que des informations dévoilables aux joueurs."
                )
        # Vérification qu'il est distinct de la description joueurs
        if desc_joueurs and aide_impro.strip() == desc_joueurs.strip():
            errors.append(
                "Le paragraphe 1 d'aide à l'improvisation est identique à la description joueurs du Bloc 4. "
                "Il doit adopter d'autres adjectifs et une autre structure."
            )

    # Paragraphe 2 : résumé MJ
    if not resume_mj:
        errors.append(
            "Le paragraphe 2 d'ouverture (résumé de fond pour le MJ) est manquant. "
            "Renseigner 'resume_mj' résumant qui est l'entité, d'où elle vient, ce qu'elle veut et ses secrets."
        )
    else:
        count_resume = len(resume_mj.strip())
        if count_resume < min_resume_len:
            errors.append(
                f"Le paragraphe 2 d'ouverture (résumé MJ) est trop court : {count_resume} caractères "
                f"(minimum strict requis : {min_resume_len} caractères). "
                f"Détailler qui est véritablement ce personnage, d'où il vient, ce qu'il veut et ses secrets profonds."
            )

    return len(errors) == 0, errors


def validate_description_joueurs(
    desc: Optional[str],
    secrets_data: Any,
    min_chars: int = MIN_DESCRIPTION_JOUEURS_CHARS,
    forbidden_terms: Optional[List[str]] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Vérifie la description pour les joueurs (Bloc 4, v3) :
    - Non vide.
    - Composée de 1 ou 2 paragraphes stricts.
    - Longueur minimale >= min_chars (défaut : 450 caractères).
    - Aucune fuite de secret.
    - Détecte et remonte les marqueurs de scène contextuelle en AVERTISSEMENTS (jamais bloquants).
    """
    errors: List[str] = []
    warnings: List[str] = []
    if not desc or not desc.strip():
        errors.append("La description joueurs (Bloc 4) est vide ou manquante.")
        return False, errors, warnings

    clean_desc = desc.strip()

    # 1. Contrôle du nombre de paragraphes (1 ou 2 paragraphes stricts)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean_desc) if p.strip()]
    if len(paragraphs) < 1 or len(paragraphs) > 2:
        errors.append(
            f"Description joueurs (Bloc 4) non conforme : {len(paragraphs)} paragraphe(s) détecté(s). "
            f"Le format v3 exige rigoureusement 1 ou 2 paragraphes."
        )

    # 2. Contrôle de longueur minimale (>= 450 caractères)
    count = len(clean_desc)
    if count < min_chars:
        errors.append(
            f"Description joueurs (Bloc 4) trop courte : {count} caractères (minimum strict requis : {min_chars} caractères). "
            f"Développer davantage l'ambiance, les détails visibles, couleurs, matières et synesthésies."
        )

    # 3. Contrôle de fuite de secrets
    clean_lower = clean_desc.lower()
    test_keywords = list(SECRET_LEAK_KEYWORDS)
    if forbidden_terms:
        test_keywords.extend([t.lower() for t in forbidden_terms if t.strip()])

    for kw in test_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", clean_lower):
            errors.append(f"Fuite suspecte détectée dans la description joueurs : mention du terme secret '{kw}'.")

    # 4. Avertissements contextuels (Marqueurs de scène : moment, météo, action immédiate)
    # Règle d'Henri : « les descriptions pour les joueurs doivent toujours être générales, elles ne doivent pas être liées à un contexte spécifique »
    scene_warnings = check_scene_context_markers(clean_desc)
    warnings.extend(scene_warnings)

    return len(errors) == 0, errors, warnings


# ============================================================================
# 4. GESTION DES WIKILINKS & CORRESPONDANCES APPROXIMATIVES (LIENS MORTS)
# ============================================================================

def index_vault(vault_dir: str) -> Tuple[Dict[str, Dict[str, Any]], Set[str]]:
    """
    Indexe l'ensemble des notes Markdown, alias frontmatter et pièces jointes du coffre.
    Retourne (notes_lookup, attachments_set).
    notes_lookup associe chaque clé normalisée (stem, rel_path, alias) à ses métadonnées.
    """
    vault_path = Path(vault_dir)
    notes_lookup: Dict[str, Dict[str, Any]] = {}
    attachments_set: Set[str] = set()

    for root, dirs, files in os.walk(vault_dir, followlinks=False):
        for f in files:
            full_p = Path(root) / f
            try:
                rel_str = str(full_p.relative_to(vault_path)).replace("\\", "/")
            except ValueError:
                rel_str = f

            norm_name = unicodedata.normalize("NFC", f.lower())
            norm_rel = unicodedata.normalize("NFC", rel_str.lower())

            if f.lower().endswith(".md"):
                stem = full_p.stem
                norm_stem = unicodedata.normalize("NFC", stem.lower())
                norm_rel_no_ext = norm_rel[:-3] if norm_rel.endswith(".md") else norm_rel

                # Extraction des alias du frontmatter YAML
                aliases: List[str] = []
                try:
                    with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                        header_chunk = "".join([fp.readline() for _ in range(40)])
                    fm_match = re.match(r"^---\s*\n(.*?)\n---", header_chunk, re.DOTALL)
                    if fm_match:
                        fm_text = fm_match.group(1)
                        alias_match = re.search(r"aliases?:\s*(?:\[(.*?)\]|(.*?)(?=\n\w+:|$))", fm_text, re.DOTALL)
                        if alias_match:
                            raw_a = alias_match.group(1) or alias_match.group(2)
                            if raw_a:
                                for item in raw_a.splitlines():
                                    item = item.strip().strip("-").strip().strip('"\'')
                                    if item and not item.startswith("["):
                                        for sub in item.split(","):
                                            sub = sub.strip().strip('"\'')
                                            if sub:
                                                aliases.append(sub)
                except OSError:
                    pass

                entry = {
                    "stem": stem,
                    "rel_path": rel_str,
                    "rel_no_ext": rel_str[:-3] if rel_str.endswith(".md") else rel_str,
                    "aliases": aliases
                }

                notes_lookup[norm_stem] = entry
                notes_lookup[norm_rel_no_ext] = entry
                notes_lookup[norm_rel] = entry
                for a in aliases:
                    norm_a = unicodedata.normalize("NFC", a.lower())
                    notes_lookup[norm_a] = entry
            else:
                attachments_set.add(norm_name)
                attachments_set.add(norm_rel)

    return notes_lookup, attachments_set


def validate_vault_wikilinks(
    data: Dict[str, Any],
    vault_dir: Optional[str]
) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    """
    Vérifie chaque Wikilink [[...]] du document.
    En cas de lien mort, recherche les correspondances les plus proches sur les noms et alias du frontmatter,
    et formule les 3 actions recommandées pour l'agent.
    """
    errors: List[str] = []
    dead_links_report: List[Dict[str, Any]] = []

    if not vault_dir:
        return True, errors, dead_links_report

    vault_path = Path(vault_dir)
    if not vault_path.is_dir():
        errors.append(f"Le dossier du coffre spécifié est invalide : {vault_dir}")
        return False, errors, dead_links_report

    notes_lookup, attachments_set = index_vault(vault_dir)

    raw_text = json.dumps(data, ensure_ascii=False)
    matches = re.findall(r"\[\[(.*?)\]\]", raw_text)

    searchable_keys = list(notes_lookup.keys())

    for m in matches:
        target = m.split("|")[0].split("#")[0].strip()
        norm_target = unicodedata.normalize("NFC", target.lower().replace("\\", "/"))

        # Pièces jointes (images)
        if norm_target.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
            target_base = Path(norm_target).name
            if norm_target not in attachments_set and target_base not in attachments_set:
                errors.append(f"Fichier image introuvable dans le coffre : [[{m}]]")
            continue

        target_no_ext = norm_target[:-3] if norm_target.endswith(".md") else norm_target
        target_stem = unicodedata.normalize("NFC", Path(norm_target).stem.lower())

        if norm_target in notes_lookup or target_no_ext in notes_lookup or target_stem in notes_lookup:
            continue

        # LIEN MORT DÉTECTÉ : Recherche des correspondances approximatives
        close_keys = difflib.get_close_matches(target_stem, searchable_keys, n=3, cutoff=0.45)
        suggestions: List[Dict[str, str]] = []
        for ck in close_keys:
            cand = notes_lookup[ck]
            suggestions.append({
                "match_name": cand["stem"],
                "rel_path": cand["rel_path"],
                "aliases": ", ".join(cand["aliases"]) if cand["aliases"] else "aucun"
            })

        dead_link_info = {
            "link": m,
            "target": target,
            "suggestions": suggestions
        }
        dead_links_report.append(dead_link_info)

        msg_lines = [
            f"Lien mort détecté : [[{m}]] -> aucune note correspondante trouvée dans le coffre."
        ]
        if suggestions:
            msg_lines.append("   🔍 Notes existantes les plus proches :")
            for s in suggestions:
                msg_lines.append(f"      - '{s['match_name']}' (chemin: {s['rel_path']}, alias: {s['aliases']})")
            top = suggestions[0]
            msg_lines.append(
                f"   💡 Actions recommandées à l'agent :\n"
                f"      1. [Corriger le lien] Si coquille, remplacer par [[{top['rel_path'][:-3]}|{target}]]\n"
                f"      2. [Ajouter un alias] Si terme légitime, ajouter '{target}' dans les alias de [[{top['match_name']}]]\n"
                f"      3. [Créer l'entité] Si PNJ/lieu nouveau, créer la fiche manquante dans le coffre."
            )
        else:
            msg_lines.append(
                f"   💡 Action recommandée à l'agent :\n"
                f"      -> Créer l'entité manquante '[[{target}]]' dans le sous-dossier approprié du coffre."
            )

        errors.append("\n".join(msg_lines))

    return len(errors) == 0, errors, dead_links_report


# ============================================================================
# 5. DÉTECTION D'IA & AUDIT DE STYLE (MOTEUR OFFICIEL AVOID-AI-WRITING / /DRAFT)
# ============================================================================

def find_detect_js_script() -> Path:
    """
    Résout le chemin canonique vers detect.js de avoid-ai-writing.
    Échec bloquant immédiat (Fail-Fast) si le fichier est introuvable.
    """
    env_override = os.environ.get("AVOID_AI_WRITING_DETECT_JS")
    if env_override and Path(env_override).is_file():
        return Path(env_override).resolve()

    candidates = [
        Path(__file__).resolve().parent / "avoid-ai-writing" / "skills" / "ai-writing-detector" / "scripts" / "detect.js",
        Path.home() / "Documents" / "VoiceNotes" / "_agents" / "scripts-for-skills" / "avoid-ai-writing" / "skills" / "ai-writing-detector" / "scripts" / "detect.js"
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()

    raise FileNotFoundError(
        "Script detect.js de avoid-ai-writing introuvable. "
        "Le moteur de détection IA déterministe officiel requiert 'detect.js'."
    )


def run_avoid_ai_writing_check(
    text: str,
    label: str,
    context_mode: str = "general"
) -> Tuple[bool, List[str], List[str], Dict[str, Any]]:
    """
    Exécute le détecteur déterministe canonique via style_guard (avoid-ai-writing / detect.js + fr_ai_patterns).
    Aligne rigoureusement le critère de conformité sur style_guard (respect du budget de soft warnings).
    Retourne (is_compliant, errors, warnings, raw_data).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not text or not text.strip():
        return True, errors, warnings, {}

    # Exécution du moteur canonique unifié via style_guard avec langue française explicite
    style_res = check_style(text, language="fr", context_mode=context_mode)

    # 1. Traitement des alertes remontées par style_guard
    for hb in style_res.hard_blockers:
        hb_type = str(hb.get("type", "")).lower()
        hb_term = str(hb.get("term", "")).strip()
        hb_sug = str(hb.get("suggestion", "") or "").strip()
        sug_suffix = f" (suggestion: {hb_sug})" if hb_sug else ""
        errors.append(f"Hard Blocker IA [{hb_type}] détecté : '{hb_term}'{sug_suffix}")

    for sw in style_res.soft_warnings:
        sw_type = str(sw.get("type", "")).lower()
        sw_term = str(sw.get("term", "")).strip()
        sw_sug = str(sw.get("suggestion", "") or "").strip()
        sug_suffix = f" (suggestion: {sw_sug})" if sw_sug else ""
        warnings.append(f"Alerte stylistique [{sw_type}] : '{sw_term}'{sug_suffix}")

    # 2. Critère d'échec unifié avec style_guard : respect du budget de soft warnings
    if not style_res.passed:
        if not style_res.hard_blockers and len(style_res.soft_warnings) > style_res.budget_max:
            errors.append(
                f"Budget d'avertissements stylistiques dépassé : "
                f"{len(style_res.soft_warnings)} avertissements > budget max autorisé de {style_res.budget_max}"
            )

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))

    # is_compliant est strictement True si style_res.passed (verdict PASS ou WARN dans le budget)
    is_compliant = style_res.passed and len(errors) == 0
    raw_data = {
        "verdict": style_res.verdict,
        "passed": style_res.passed,
        "word_count": style_res.word_count,
        "budget_max": style_res.budget_max,
        "language": style_res.detected_language,
        "hard_blockers": style_res.hard_blockers,
        "soft_warnings": style_res.soft_warnings
    }
    return is_compliant, errors, warnings, raw_data


def run_neural_ai_detection(
    text: str,
    label: str,
    threshold: float = DEFAULT_NEURAL_AI_THRESHOLD,
    scripts_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Exécute le script ai_detector.py en mode optionnel explicite (--use-neural-ai).
    """
    if scripts_dir is None:
        scripts_dir = Path(__file__).resolve().parent

    detector_script = scripts_dir / "ai_detector.py"
    if not detector_script.is_file():
        alt = Path(str(Path.home() / "Documents" / "VoiceNotes")) / "_agents" / "scripts-for-skills" / "ai_detector.py"
        if alt.is_file():
            detector_script = alt
        else:
            return {
                "available": False,
                "error": f"Script ai_detector.py introuvable à l'emplacement : {detector_script}",
                "p_ai": 0.0,
                "is_compliant": True,
            }

    cmd = [
        sys.executable,
        str(detector_script),
        text,
        "--allow-partial",
        "--offline",
        "--device", "cpu",
        "--json",
        "--threshold", str(threshold)
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30)
    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "error": "Timeout lors de l'inférence ai_detector.py (>= 30s).",
            "p_ai": 0.0,
            "is_compliant": False
        }
    except Exception as e:
        return {
            "available": True,
            "error": f"Échec de lancement de ai_detector.py : {e}",
            "p_ai": 0.0,
            "is_compliant": False
        }

    stdout_clean = proc.stdout.strip()
    json_match = re.search(r"\{[\s\S]*\}", stdout_clean)
    if not json_match:
        return {
            "available": True,
            "error": f"Sortie JSON invalide de ai_detector.py : {stdout_clean[:200]}",
            "raw_stderr": proc.stderr,
            "p_ai": 0.0,
            "is_compliant": False
        }

    try:
        data = json.loads(json_match.group(0))
        p_ai = data.get("global_score", {}).get("p_ai", 0.0)
        is_compliant = p_ai < threshold
        return {
            "available": True,
            "p_ai": p_ai,
            "p_ai_percent": round(p_ai * 100, 1),
            "verdict": data.get("global_score", {}).get("verdict", "INCONNU"),
            "threshold": threshold,
            "is_compliant": is_compliant,
            "details": data.get("breakdown", {})
        }
    except Exception as e:
        return {
            "available": True,
            "error": f"Erreur de décodage JSON : {e}",
            "p_ai": 0.0,
            "is_compliant": False
        }


# ============================================================================
# 6. ASSEMBLAGE DE LA FICHE EN 5 BLOCS CANONIQUES (v3)
# ============================================================================

def format_secrets_mj(
    secrets: Any,
    nom: str = "l'entité"
) -> str:
    """
    Met en forme les sections détaillées de secrets MJ en Markdown propre avec titres interrogatifs
    selon le paradigme Q/R. Les deux paragraphes d'ouverture (improvisation et vérité) sont placés
    en amont dans assemble_final_markdown avec leurs propres titres H2.
    """
    lines: List[str] = []
    lines.append(f"## 🔒 Quels sont les secrets MJ, l'inventaire et les coulisses de {nom} ?\n")

    if isinstance(secrets, dict):
        mapping_titles = {
            "inventaire": "🎒 Quel est l'inventaire détaillé, l'équipement et les documents portés ?",
            "guide_interpretation": "🎭 Quel est le guide d'interprétation, la posture et les tactiques ?",
            "repliques_types": "💬 Quelles sont les répliques types et sentences favorites ?",
            "secrets_coulisses": "🗝️ Quels sont les secrets inavouables, le statut canonique et les liaisons d'intrigue ?",
            "destin_trajectoire": "⏳ Quel est le destin, la trajectoire narrative et les conditions de mort ?",
        }

        ignored_keys = {"aide_improvisation", "resume_mj"}

        for key, title in mapping_titles.items():
            if key in secrets and secrets[key] and key not in ignored_keys:
                lines.append(f"### {title}\n")
                lines.append(str(secrets[key]).strip())
                lines.append("")

        for key, val in secrets.items():
            if key not in mapping_titles and key not in ignored_keys and val:
                clean_title = key.replace("_", " ").capitalize()
                if not clean_title.endswith("?"):
                    clean_title = f"Quelle est la rubrique {clean_title} ?"
                lines.append(f"### {clean_title}\n")
                lines.append(str(val).strip())
                lines.append("")

    elif isinstance(secrets, str):
        lines.append(secrets.strip())
        lines.append("")

    return "\n".join(lines).strip()


def assemble_final_markdown(data: Dict[str, Any]) -> str:
    """
    Assemble la fiche d'entité Markdown finale dans l'ordre strict des 5 blocs (v3) :
    1. Image ![[...]]
    2. Bloc de code de la description externe (<= 100 car.)
    3. Ouverture MJ & Secrets détaillés :
       - '## 🎭 Comment l'improviser ?' suivi du paragraphe 1 d'aide à l'improvisation (mots en **gras**)
       - '## 🗝️ Qui est-il vraiment ?' (ou '## 🗝️ Quelle est la vérité sur ce lieu ?') suivi du paragraphe 2 (>= 350 car.)
       - '## 🔒 Quels sont les secrets MJ, l'inventaire et les coulisses de {nom} ?' suivi des rubriques H3
    4. Bloc de code Markdown avec description pour les joueurs (1 ou 2 paragraphes, >= 450 car.)
    5. Bloc de code texte pur pour la fiche Harpy
    """
    nom = data.get("nom", "Entité")
    image_raw = data.get("image", "").strip()
    img_basename = Path(image_raw.strip("[]")).name if image_raw else ""
    if image_raw.startswith("[[") and image_raw.endswith("]]"):
        image_tag = f"!{image_raw}"
    elif image_raw:
        image_tag = f"![[{img_basename}]]"
    else:
        image_tag = "<!-- Image non spécifiée -->"

    desc_ext = data.get("description_externe", "").strip()
    aide_impro, resume_mj = extract_ouverture_paragraphs(data)
    secrets_text = format_secrets_mj(data.get("secrets_mj", {}), nom=nom)
    desc_joueurs = data.get("description_joueurs", "").strip()
    bloc_harpy = data.get("bloc_harpy", "").strip()

    # Titres personnalisés ou automatiques selon le type d'entité
    type_entite = str(data.get("type", "")).lower()
    is_lieu = type_entite == "lieu" or "lieu" in str(data.get("systeme", "")).lower()

    titre_impro = str(data.get("titre_improvisation", "")).strip() or (
        "## 🎭 Comment improviser ce lieu ?" if is_lieu else "## 🎭 Comment l'improviser ?"
    )
    titre_verite = str(data.get("titre_verite", "")).strip() or (
        "## 🗝️ Quelle est la vérité sur ce lieu ?" if is_lieu else "## 🗝️ Qui est-il vraiment ?"
    )

    blocks: List[str] = []

    # Frontmatter YAML
    if "frontmatter" in data and isinstance(data["frontmatter"], dict):
        blocks.append("---")
        fm = data["frontmatter"]
        for k, v in fm.items():
            if isinstance(v, list):
                blocks.append(f"{k}:")
                for item in v:
                    blocks.append(f"- {item}")
            elif isinstance(v, dict):
                blocks.append(f"{k}:")
                for subk, subv in v.items():
                    blocks.append(f"  {subk}: {subv}")
            else:
                if isinstance(v, str) and (":" in v or " " in v or "'" in v or v.startswith("[[")):
                    escaped_v = v.replace("'", "''")
                    blocks.append(f"{k}: '{escaped_v}'")
                else:
                    blocks.append(f"{k}: {v}")
        if "Image" not in fm and img_basename:
            blocks.append(f"Image: '[[{img_basename}]]'")
        blocks.append("---")
        blocks.append("")
    elif img_basename:
        escaped_nom = str(nom).replace("'", "''")
        blocks.append("---")
        blocks.append(f"displayName: '{escaped_nom}'")
        blocks.append(f"Image: '[[{img_basename}]]'")
        blocks.append("---")
        blocks.append("")

    # Titre H1
    titre_h1 = str(data.get("titre_h1", "")).strip() or f"# {nom}"
    blocks.append(titre_h1)
    blocks.append("")

    # BLOC 1 : Image sous le H1
    blocks.extend([
        image_tag,
        "",
        # BLOC 2 : Description externe
        "```text",
        desc_ext,
        "```",
        "",
        # OUVERTURE 1 : Comment l'improviser ?
        titre_impro,
        "",
        aide_impro,
        "",
        # OUVERTURE 2 : Qui est-il vraiment ?
        titre_verite,
        "",
        resume_mj,
        "",
        # BLOC 3 : Secrets MJ détaillés
        secrets_text,
        "",
        # BLOC 4 : Description Joueurs
        "```markdown",
        desc_joueurs,
        "```",
        "",
        # BLOC 5 : Fiche Harpy (texte pur)
        "```text",
        bloc_harpy,
        "```",
    ])

    return "\n".join(blocks).strip() + "\n"



# ============================================================================
# 7. POINT D'ENTRÉE PRINCIPAL (CLI)
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Moteur de validation et d'assemblage en 5 blocs pour harpy-entity-creator (v3)."
    )
    parser.add_argument("input", nargs="?", default=None,
                        help="Fichier d'entrée YAML ou JSON structuré (optionnel si --tirage seul)")
    parser.add_argument("-o", "--output", help="Chemin du fichier Markdown généré en sortie")
    parser.add_argument("--tirage", action="store_true",
                        help="Tire au sort un ensemble d'angles narratifs pour stimuler l'écriture du Bloc 4")
    parser.add_argument("--max-desc-len", type=int, default=MAX_DESCRIPTION_EXTERNE_CHARS,
                        help=f"Longueur maximale de la description externe (défaut : {MAX_DESCRIPTION_EXTERNE_CHARS})")
    parser.add_argument("--min-joueurs-len", type=int, default=MIN_DESCRIPTION_JOUEURS_CHARS,
                        help=f"Longueur minimale de la description joueurs (défaut : {MIN_DESCRIPTION_JOUEURS_CHARS})")
    parser.add_argument("--min-resume-len", type=int, default=MIN_RESUME_MJ_CHARS,
                        help=f"Longueur minimale du paragraphe 2 d'ouverture résumé MJ (défaut : {MIN_RESUME_MJ_CHARS})")
    parser.add_argument("--max-line-len", type=int, default=DEFAULT_MAX_HARPY_LINE_LENGTH,
                        help=f"Longueur maximale par ligne dans la fiche Harpy (défaut : {DEFAULT_MAX_HARPY_LINE_LENGTH})")
    parser.add_argument("--vault", default=str(Path.home() / "Documents" / "VoiceNotes"),
                        help="Chemin racine du coffre Obsidian pour vérifier les wikilinks (défaut : Path.home() / 'Documents' / 'VoiceNotes')")
    parser.add_argument("--skip-vault", action="store_true",
                        help="Désactive la vérification de l'existence des wikilinks dans le coffre")
    parser.add_argument("--use-neural-ai", action="store_true",
                        help="Active l'inférence neuronale ai_detector.py en complément (désactivée par défaut)")
    parser.add_argument("--neural-threshold", type=float, default=DEFAULT_NEURAL_AI_THRESHOLD,
                        help=f"Seuil maximal pour le détecteur neuronal ai_detector.py (défaut : {DEFAULT_NEURAL_AI_THRESHOLD})")
    parser.add_argument("--skip-ai", action="store_true",
                        help="Désactive le contrôle de détection d'IA")
    parser.add_argument("--check-only", action="store_true",
                        help="Exécute les contrôles sans générer le fichier de sortie")

    args = parser.parse_args()

    print("=" * 70)
    print(" 🦅 HARPY ENTITY VALIDATOR & ASSEMBLER (v3)")
    print("=" * 70)

    # 0. Gestion de l'option --tirage
    if args.tirage:
        tirage = tirer_angles_narratifs()
        print("\n🎲 TIRAGE ALÉATOIRE D'ANGLES NARRATIFS (BLOC 4) :")
        print(f"  • Sens dominant    : {tirage['sens_dominant']}")
        print(f"  • Point de vue     : {tirage['point_de_vue']}")
        print(f"  • Distance         : {tirage['distance']}")
        print(f"  • Moment / Lumière : {tirage['moment_lumiere']}")
        print(f"  • Détail inattendu : {tirage['detail_inattendu']}")
        print(f"  • Rythme de phrase : {tirage['rythme_phrase']}")
        print("-" * 70)
        if not args.input:
            print("ℹ️ Mode tirage autonome terminé avec succès.")
            sys.exit(0)

    if not args.input:
        sys.stderr.write("❌ Erreur : Un fichier d'entrée YAML ou JSON est requis (sauf en appel autonome --tirage).\n")
        sys.exit(1)

    # 1. Chargement
    try:
        data = load_input_data(args.input)
        print(f"✅ Fichier d'entrée chargé avec succès : {args.input}")
    except Exception as e:
        sys.stderr.write(f"❌ [ÉCHEC CHARGEMENT] {e}\n")
        sys.exit(1)

    has_errors = False
    all_error_messages: List[str] = []

    # 2. Contrôle d'absence de mentions de sources (v3)
    errs_sources = validate_forbidden_source_mentions(data)
    if errs_sources:
        has_errors = True
        for e in errs_sources:
            all_error_messages.append(f"[Mentions de Sources Proscrites] {e}")
            print(f"❌ [Mentions de Sources Proscrites] {e}")
    else:
        print("✅ [Mentions de Sources] Zéro mention de source détectée (aucune référence à page, module, canon ou proposition MJ).")

    # 3. Contrôle Description Externe (Bloc 2)
    desc_ext = data.get("description_externe", "")
    ok_desc, count_desc, errs_desc, warns_desc = validate_description_externe(
        desc_ext, data, max_len=args.max_desc_len
    )
    if not ok_desc:
        has_errors = True
        for e in errs_desc:
            all_error_messages.append(f"[Bloc 2 - Description externe] {e}")
            print(f"❌ [Bloc 2 - Description externe] {e}")
    else:
        print(f"✅ [Bloc 2 - Description externe] Conforme : {count_desc}/{args.max_desc_len} car. (Apparence physique pure).")

    for w in warns_desc:
        print(f"⚠️ [Bloc 2 - Avertissement] {w}")

    # 4. Contrôle Ouverture de Note (Bloc 3 : 2 paragraphes obligatoires avec P2 >= min_resume_len)
    aide_impro, resume_mj = extract_ouverture_paragraphs(data)
    desc_joueurs = data.get("description_joueurs", "")
    ok_ouv, errs_ouv = validate_ouverture_mj(
        aide_impro, resume_mj, desc_joueurs, min_resume_len=args.min_resume_len
    )
    if not ok_ouv:
        has_errors = True
        for e in errs_ouv:
            all_error_messages.append(f"[Bloc 3 - Ouverture de Note] {e}")
            print(f"❌ [Bloc 3 - Ouverture de Note] {e}")
    else:
        print(f"✅ [Bloc 3 - Ouverture de Note] 2 paragraphes conformes (P1 aide impro avec gras, P2 résumé clair MJ : {len(resume_mj.strip())}/{args.min_resume_len} car.).")

    # 5. Contrôle Description Joueurs (Bloc 4 : 1-2 paragraphes, >= 450 car., zéro secret)
    secrets_data = data.get("secrets_mj", {})
    ok_joueurs, errs_joueurs, warns_joueurs = validate_description_joueurs(
        desc_joueurs, secrets_data, min_chars=args.min_joueurs_len
    )
    if not ok_joueurs:
        has_errors = True
        for e in errs_joueurs:
            all_error_messages.append(f"[Bloc 4 - Description joueurs] {e}")
            print(f"❌ [Bloc 4 - Description joueurs] {e}")
    else:
        paragraphs_count = len([p for p in re.split(r"\n\s*\n", desc_joueurs.strip()) if p.strip()])
        print(f"✅ [Bloc 4 - Description joueurs] Conforme : {len(desc_joueurs.strip())} car. ({paragraphs_count} paragraphe(s) >= {args.min_joueurs_len} car., zéro fuite).")

    for w in warns_joueurs:
        print(f"⚠️ [Bloc 4 - Avertissement Marqueur de Scène] {w}")

    # 6. Contrôle Fiche Harpy Texte Pur (Bloc 5)
    bloc_harpy = data.get("bloc_harpy", "")
    ok_harpy, errs_harpy = validate_bloc_harpy(bloc_harpy, max_line_len=args.max_line_len)
    if not ok_harpy:
        has_errors = True
        for e in errs_harpy:
            all_error_messages.append(f"[Bloc 5 - Fiche Harpy] {e}")
            print(f"❌ [Bloc 5 - Fiche Harpy] {e}")
    else:
        print("✅ [Bloc 5 - Fiche Harpy] Texte pur conforme (apostrophes autorisées, sous-lignes '↳' validées, largeurs <= 70 car.).")

    # 7. Contrôle des Wikilinks du Coffre (--vault) avec suggestions pour liens morts
    if not args.skip_vault and args.vault:
        ok_vault, errs_vault, dead_reports = validate_vault_wikilinks(data, args.vault)
        if not ok_vault:
            has_errors = True
            for e in errs_vault:
                all_error_messages.append(f"[Liens Coffre] {e}")
                print(f"❌ [Liens Coffre] {e}")
        else:
            print(f"✅ [Liens Coffre] 100% des wikilinks [[...]] et images existent dans '{args.vault}'.")

    # 8. Détection d'IA (Moteur officiel detect.js de avoid-ai-writing / /draft)
    if not args.skip_ai:
        print("\n🔍 Contrôle Anti-IA déterministe en cours (moteur officiel detect.js de avoid-ai-writing)...")
        try:
            # Audit Bloc 2 (Description externe)
            ok_ai_desc, errs_ai_desc, warns_ai_desc, raw_ai_desc = run_avoid_ai_writing_check(
                desc_ext, "Description externe"
            )
            if not ok_ai_desc:
                has_errors = True
                for e in errs_ai_desc:
                    all_error_messages.append(f"[Anti-IA Bloc 2 - Description externe] {e}")
                    print(f"❌ [Anti-IA Bloc 2 - Description externe] {e}")
            else:
                score_desc = raw_ai_desc.get("score", 0)
                label_desc = raw_ai_desc.get("label", "Clean")
                print(f"✅ [Anti-IA Bloc 2 - Description externe] Conforme detect.js (score: {score_desc}, label: {label_desc}).")

            for w in warns_ai_desc:
                print(f"⚠️ [Anti-IA Bloc 2 - Avertissement] {w}")

            # Audit Bloc 4 (Description joueurs)
            ok_ai_joueurs, errs_ai_joueurs, warns_ai_joueurs, raw_ai_joueurs = run_avoid_ai_writing_check(
                desc_joueurs, "Description joueurs"
            )
            if not ok_ai_joueurs:
                has_errors = True
                for e in errs_ai_joueurs:
                    all_error_messages.append(f"[Anti-IA Bloc 4 - Description joueurs] {e}")
                    print(f"❌ [Anti-IA Bloc 4 - Description joueurs] {e}")
            else:
                score_joueurs = raw_ai_joueurs.get("score", 0)
                label_joueurs = raw_ai_joueurs.get("label", "Clean")
                print(f"✅ [Anti-IA Bloc 4 - Description joueurs] Conforme detect.js (score: {score_joueurs}, label: {label_joueurs}).")

            for w in warns_ai_joueurs:
                print(f"⚠️ [Anti-IA Bloc 4 - Avertissement] {w}")

        except Exception as e:
            # Échec bloquant Fail-Fast si node ou detect.js manque
            has_errors = True
            all_error_messages.append(f"[Anti-IA Déterministe] Échec critique d'exécution : {e}")
            print(f"❌ [Anti-IA Déterministe] Échec critique d'exécution : {e}")

        # Option neuronale complémentaire
        if args.use_neural_ai:
            print(f"\n🧠 Analyse Anti-IA neuronale optionnelle (ai_detector.py, seuil: {args.neural_threshold})...")
            res_neural_desc = run_neural_ai_detection(desc_ext, "Description externe", threshold=args.neural_threshold)
            res_neural_joueurs = run_neural_ai_detection(desc_joueurs, "Description joueurs", threshold=args.neural_threshold)

            if res_neural_desc.get("available") and not res_neural_desc.get("error"):
                print(f"   - Bloc 2 P(IA) = {res_neural_desc['p_ai_percent']}% -> {res_neural_desc['verdict']}")
                if not res_neural_desc["is_compliant"]:
                    has_errors = True
                    all_error_messages.append(
                        f"[Anti-IA Neuronal Bloc 2] Score IA excessif : {res_neural_desc['p_ai_percent']}% > {int(args.neural_threshold*100)}%"
                    )
            elif res_neural_desc.get("error"):
                print(f"   ⚠️ Bloc 2 Neuronal : {res_neural_desc['error']}")

            if res_neural_joueurs.get("available") and not res_neural_joueurs.get("error"):
                print(f"   - Bloc 4 P(IA) = {res_neural_joueurs['p_ai_percent']}% -> {res_neural_joueurs['verdict']}")
                if not res_neural_joueurs["is_compliant"]:
                    has_errors = True
                    all_error_messages.append(
                        f"[Anti-IA Neuronal Bloc 4] Score IA excessif : {res_neural_joueurs['p_ai_percent']}% > {int(args.neural_threshold*100)}%"
                    )
            elif res_neural_joueurs.get("error"):
                print(f"   ⚠️ Bloc 4 Neuronal : {res_neural_joueurs['error']}")
    else:
        print("ℹ️ Contrôle Anti-IA ignoré (--skip-ai activé).")

    # 9. Bilan et Verdict
    print("-" * 70)
    if has_errors:
        sys.stderr.write(f"\n❌ [ÉCHEC VALIDATION] {len(all_error_messages)} erreur(s) détectée(s) :\n")
        for err in all_error_messages:
            sys.stderr.write(f"  • {err}\n")
        sys.exit(1)

    print("🎉 TOUS LES CONTRÔLES SONT VALIDÉS AVEC SUCCÈS (CODE RETOUR 0).")

    if args.check_only:
        sys.exit(0)

    # 10. Assemblage de la Fiche Finale
    final_md = assemble_final_markdown(data)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_md, encoding="utf-8")
        print(f"💾 Fiche Markdown en 5 blocs enregistrée sous : {out_path.resolve()}\n")
    else:
        print("\n" + "=" * 70)
        print(" FICHE ASSEMBLÉE FINALE (5 BLOCS) :")
        print("=" * 70)
        print(final_md)


if __name__ == "__main__":
    main()
