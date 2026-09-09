#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
latex_to_markdown_artifact.py — Convertisseur & Moteur Diff Automatique Universel (LaTeX / Markdown ➔ Markdown Artifact)

Fonctionnalités :
1. 100% Automatique & Déterministe : aucun argument obligatoire ni option requis.
2. Résolution récursive des \input{...} et \include{...} pour les projets LaTeX.
3. Auto-détection de la bibliographie (.bib) dans le dossier source.
4. Auto-détection de la baseline Git ancrée sur le dernier commit signé par Henri Jamet (fallback HEAD~1).
5. Conversion complète de la syntaxe LaTeX en GitHub Flavored Markdown (GFM) :
   - Titres (#, ##, ###, ####)
   - Environnements textuels (abstract, quote, quotation, verse ➔ citations Markdown natifs `> ...`)
   - KaTeX Math ($...$, $$...$$, align, equation)
   - Tableaux LaTeX (tabular, tabularx, booktabs) ➔ Tableaux Markdown natifs
   - Citations (BibTeX parser intégré, \cite, \citep, \citet ➔ [Auteur, Année])
   - Figures & Graphiques (\includegraphics, tikzpicture ➔ callouts / images)
   - Listes (itemize, enumerate) & formatage inline (\textbf, \textit, \texttt, \url, etc.)
6. Moteur de Diff Inline Word-Diff chirurgical par section AST :
   - Découpage du document en sections AST (#, ##, ###)
   - Comparaison mot par mot / segment par segment via difflib.SequenceMatcher
   - Sections 100% identiques : affichées normalement comme texte continu intégral sans callout parasite
   - Sections modifiées : texte fluide en UN SEUL bloc où seuls les mots modifiés sont surlignés :
     * Mots supprimés : <del style="...">ancien</del>
     * Mots ajoutés : <ins style="...">nouveau</ins>
   - Arborescence (Tree TOC) dynamique des deltas détectés avec liens d'ancrage cliquables
7. Dossier de sortie automatique dans papers/<nom_papier>.md
"""

import os
import sys
import re
import shutil
import argparse
import difflib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any

# Assurer la compatibilité UTF-8 de la sortie console sous Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def is_local_author(name: str, email: str = "") -> bool:
    """
    Détermine si un auteur de commit Git est l'auteur local (Henri Jamet).
    Prend en compte le nom complet, le prénom, l'identifiant et l'adresse email.
    """
    n = (name or "").lower()
    e = (email or "").lower()
    local_keywords = ["henri", "jamet", "hjamet"]
    return any(k in n or k in e for k in local_keywords)


def get_ai_detector_module():
    """
    Localise et importe dynamiquement le module ai_detector.
    Recherche dans :
    1. Directement dans sys.modules ou import ai_detector
    2. Même dossier que ce script
    3. Dossier antigravity/scripts/
    4. Dossier VoiceNotes canonique
    """
    try:
        import ai_detector
        return ai_detector
    except ImportError:
        pass

    candidates = [
        Path(__file__).resolve().parent / "ai_detector.py",
        Path(__file__).resolve().parent.parent / "scripts" / "ai_detector.py",
        Path.home() / "Documents" / "VoiceNotes" / "antigravity" / "scripts" / "ai_detector.py",
        Path(r"C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\ai_detector.py"),
        Path(r"C:\Users\hjamet\Documents\VoiceNotes\antigravity\scripts\ai_detector.py"),
    ]

    for cand in candidates:
        if cand.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("ai_detector", str(cand))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules["ai_detector"] = mod
                    spec.loader.exec_module(mod)
                    return mod
            except Exception:
                pass
    return None


def format_ai_score_badge(score_before: Optional[float], score_after: Optional[float]) -> str:
    """
    Badge pill élégant compatible Antigravity & Obsidian :
    - Structure <span> stylisée (autorisée par le sanitizer Cib d'Antigravity)
    - border-radius: 4px, font-size: 0.78rem, padding: 2px 8px, font-weight: 500
    - Couleur dynamique selon score_after :
      * Vert/Emerald si score_after <= 10.0% : background #f0fdf4, texte #15803d, bordure #bbf7d0, mention " — ✅ Conforme (< 10%)"
      * Ambre si score_after entre 10.0% et 30.0% : background #fffbeb, texte #b45309, bordure #fde68a
      * Rouge si score_after > 30.0% : background #fef2f2, texte #b91c1c, bordure #fecaca
    - Évolution affichée : "🛡️ Score IA : {score_before}% ➔ {score_after}% ({delta}%)"
    """
    if score_before is not None and score_after is not None:
        delta = score_after - score_before
        delta_sign = '+' if delta > 0 else ''
        delta_str = f"{delta_sign}{delta:.1f}%"
        evolution_text = f"🛡️ Score IA : {score_before:.1f}% ➔ {score_after:.1f}% ({delta_str})"
        ref_score = score_after
    elif score_after is not None:
        evolution_text = f"🛡️ Score IA : {score_after:.1f}%"
        ref_score = score_after
    elif score_before is not None:
        evolution_text = f"🛡️ Score IA : {score_before:.1f}% (Supprimé)"
        ref_score = score_before
    else:
        return ""

    if ref_score <= 10.0:
        style = 'display:inline-block;margin-top:6px;padding:2px 8px;border-radius:4px;font-size:0.78rem;font-weight:500;background-color:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;'
        mention = ' — ✅ Conforme (&lt; 10%)'
    elif ref_score <= 30.0:
        style = 'display:inline-block;margin-top:6px;padding:2px 8px;border-radius:4px;font-size:0.78rem;font-weight:500;background-color:#fffbeb;color:#b45309;border:1px solid #fde68a;'
        mention = ''
    else:
        style = 'display:inline-block;margin-top:6px;padding:2px 8px;border-radius:4px;font-size:0.78rem;font-weight:500;background-color:#fef2f2;color:#b91c1c;border:1px solid #fecaca;'
        mention = ''

    return f'<span style="{style}">{evolution_text}{mention}</span>'


def attach_badge_to_block(block: str, badge: str) -> str:
    """Attache élégamment le badge en dessous du bloc en respectant le contexte Markdown."""
    lines = block.splitlines()
    if not lines:
        return block
    if all(l.strip().startswith('>') for l in lines):
        return f"{block}\n>\n> {badge}"
    if re.match(r'^\s*[-*+]\s+', block) or re.match(r'^\s*\d+\.\s+', block):
        return f"{block}\n  {badge}"
    return f"{block}\n\n{badge}"


def attach_ai_score_badges(markdown_text: str, ai_scores: Optional[Dict[str, Any]] = None) -> str:
    """Helper module-level pour attacher les badges de score IA."""
    updated, _, _ = ArtifactDiffManager.attach_ai_score_badges(markdown_text, enable_ai_score=True)
    return updated


def derive_output_path(input_path: Path, title: str = "") -> Path:
    """
    Déduit le chemin de sortie Markdown dans le dossier papers/ du vault VoiceNotes.
    """
    vault_candidates = [
        Path.home() / "Documents" / "VoiceNotes",
        Path(r"C:\Users\Jamet\Documents\VoiceNotes"),
        Path(r"C:\Users\hjamet\Documents\VoiceNotes"),
    ]
    vault_dir = next((p for p in vault_candidates if p.exists()), vault_candidates[0])
    papers_dir = vault_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    slug = ""
    if title:
        prefix = re.split(r'[:—\-]', title)[0].strip()
        if len(prefix) >= 3:
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', prefix.lower()).strip('_')
        if not slug:
            words = title.split()[:4]
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', " ".join(words).lower()).strip('_')

    if not slug:
        parent = input_path.parent
        if parent.name.lower() in ('paper', 'src', 'latex', 'tex') and parent.parent:
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', parent.parent.name.lower()).strip('_')
        else:
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', parent.name.lower()).strip('_')

    if not slug or slug == "main":
        slug = "manuscript"

    return papers_dir / f"{slug}.md"


class BibTexParser:
    """Parseur BibTeX autonome pour résoudre les citations avec support des accents LaTeX."""

    @staticmethod
    def decode_latex_accents(text: str) -> str:
        text = text.replace(r'{\L}', 'Ł').replace(r'{\l}', 'ł')
        text = text.replace(r'\"u', 'ü').replace(r'{\"u}', 'ü')
        text = text.replace(r'\"o', 'ö').replace(r'{\"o}', 'ö')
        text = text.replace(r'\"a', 'ä').replace(r'{\"a}', 'ä')
        text = text.replace(r'\'e', 'é').replace(r'{\'e}', 'é')
        text = text.replace(r'\`e', 'è').replace(r'{\`e}', 'è')
        text = text.replace(r'\^e', 'ê').replace(r'{\^e}', 'ê')
        text = text.replace(r'\'a', 'á').replace(r'{\'a}', 'á')
        text = text.replace(r'\'u', 'ú').replace(r'{\'u}', 'ú')
        text = text.replace(r'\'i', 'í').replace(r'{\'i}', 'í')
        text = text.replace(r'\'o', 'ó').replace(r'{\'o}', 'ó')
        text = text.replace(r'\~n', 'ñ').replace(r'{\~n}', 'ñ')
        text = text.replace(r'\c{c}', 'ç').replace(r'{\c{c}}', 'ç')
        text = text.replace(r'\ss', 'ß')
        text = re.sub(r'[\{\}]', '', text)
        text = re.sub(r'\\&', '&', text)
        return text

    def __init__(self):
        self.entries: Dict[str, Dict[str, str]] = {}

    def load_bib_file(self, bib_path: Path):
        if not bib_path.exists():
            return
        try:
            content = bib_path.read_text(encoding="utf-8", errors="replace")
            self.parse_bib_content(content)
        except Exception as e:
            print(f"[BibTeX] Avertissement: Impossible de lire {bib_path}: {e}")

    def parse_bib_content(self, content: str):
        entry_pattern = re.compile(r'@(\w+)\s*\{\s*([^,]+),([^@]*)\}', re.DOTALL)
        field_pattern = re.compile(r'(\w+)\s*=\s*[\{"](.*?)[\}"]\s*(?:,|$)', re.DOTALL)

        for match in entry_pattern.finditer(content):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            body = match.group(3)

            fields = {"_type": entry_type}
            for f_match in field_pattern.finditer(body):
                f_name = f_match.group(1).strip().lower()
                f_val = f_match.group(2).strip()
                f_val = self.decode_latex_accents(f_val)
                fields[f_name] = f_val

            self.entries[key] = fields

    def format_citation(self, key: str, citet: bool = False) -> str:
        key = key.strip()
        if key not in self.entries:
            return f"[{key}]" if not citet else f"{key}"

        entry = self.entries[key]
        authors_raw = entry.get("author", "")
        year = entry.get("year", "s.d.")

        if authors_raw:
            authors_list = [a.strip() for a in authors_raw.split(" and ")]
            first_author = authors_list[0].split(",")[0].strip()
            if len(authors_list) == 1:
                author_str = first_author
            elif len(authors_list) == 2:
                second_author = authors_list[1].split(",")[0].strip()
                author_str = f"{first_author} & {second_author}"
            else:
                author_str = f"{first_author} et al."
        else:
            author_str = entry.get("title", key)[:30]

        if citet:
            return f"{author_str} [{year}]"
        else:
            return f"[{author_str}, {year}]"

    def format_full_reference(self, key: str) -> str:
        if key not in self.entries:
            return f"- **[{key}]** : Référence BibTeX non trouvée."
        
        entry = self.entries[key]
        authors = entry.get("author", "Auteurs inconnus")
        title = entry.get("title", "Sans titre")
        year = entry.get("year", "s.d.")
        venue = entry.get("booktitle") or entry.get("journal") or entry.get("publisher") or ""
        
        ref = f"- **[{key}]** : {authors} ({year}). *{title}*."
        if venue:
            ref += f" In *{venue}*."
        return ref


class LatexMacroEngine:
    """Moteur d'extraction et d'expansion récursive et dynamique de macros LaTeX personnalisées."""

    @staticmethod
    def extract_braced_group(text: str, start_idx: int) -> Tuple[str, int]:
        """Extrait le contenu équilibré {...} à partir de start_idx."""
        idx = text.find('{', start_idx)
        if idx == -1:
            return "", start_idx
        depth = 1
        i = idx + 1
        content_start = i
        n = len(text)
        while i < n and depth > 0:
            c = text[i]
            if c == '\\':
                i += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[content_start:i], i + 1
            i += 1
        return text[content_start:i], i

    @classmethod
    def extract_macros(cls, text: str) -> Tuple[str, Dict[str, Dict[str, any]]]:
        r"""
        Extrait toutes les définitions de macros (\newcommand, \renewcommand, \providecommand, \def)
        du texte et retourne le texte purgé de ces définitions ainsi que le dictionnaire des macros.
        """
        macros: Dict[str, Dict[str, any]] = {}

        # 1. Extraction \newcommand, \renewcommand, \providecommand
        pattern_new = re.compile(
            r'\\(?:newcommand|renewcommand|providecommand)\*?\s*(?:\{\\([a-zA-Z]+)\}|\\([a-zA-Z]+))(?:\s*\[(\d+)\])?\s*\{'
        )
        while True:
            m = pattern_new.search(text)
            if not m:
                break
            name = m.group(1) or m.group(2)
            num_args = int(m.group(3)) if m.group(3) else 0
            open_brace_idx = m.end() - 1
            body, end_idx = cls.extract_braced_group(text, open_brace_idx)
            macros[name] = {"args": num_args, "body": body}
            text = text[:m.start()] + text[end_idx:]

        # 2. Extraction \def
        pattern_def = re.compile(
            r'\\def\s*\\([a-zA-Z]+)((?:#\d+)*)\s*\{'
        )
        while True:
            m = pattern_def.search(text)
            if not m:
                break
            name = m.group(1)
            params_str = m.group(2) or ""
            num_args = len(re.findall(r'#\d', params_str))
            open_brace_idx = m.end() - 1
            body, end_idx = cls.extract_braced_group(text, open_brace_idx)
            macros[name] = {"args": num_args, "body": body}
            text = text[:m.start()] + text[end_idx:]

        return text, macros

    @classmethod
    def expand_macros(cls, text: str, macros: Dict[str, Dict[str, any]], max_passes: int = 5) -> str:
        r"""
        Substitue récursivement toutes les macros extraites dans le texte.
        Gère les arguments (#1, #2...) et les conventions de spacing LaTeX / \xspace.
        """
        if not macros:
            return text

        sorted_names = sorted(macros.keys(), key=len, reverse=True)

        for _ in range(max_passes):
            changed = False
            for name in sorted_names:
                info = macros[name]
                num_args = info["args"]
                body = info["body"]

                if num_args == 0:
                    pattern_bs = re.compile(r'\\' + re.escape(name) + r'\\(?:\s+|$)')
                    if pattern_bs.search(text):
                        changed = True
                        text = pattern_bs.sub(lambda m: body + " ", text)
                    pattern = re.compile(r'\\' + re.escape(name) + r'(?:\{\}|(?![a-zA-Z]))')
                    if pattern.search(text):
                        changed = True
                        text = pattern.sub(lambda m: body, text)
                else:
                    call_pattern = re.compile(r'\\' + re.escape(name) + r'\s*\{')
                    while True:
                        m = call_pattern.search(text)
                        if not m:
                            break
                        changed = True
                        curr_idx = m.end() - 1
                        args = []
                        valid = True
                        for _ in range(num_args):
                            if curr_idx < len(text) and text[curr_idx] == '{':
                                arg_val, next_idx = cls.extract_braced_group(text, curr_idx)
                                args.append(arg_val)
                                m_ws = re.match(r'\s*', text[next_idx:])
                                curr_idx = next_idx + (m_ws.end() if m_ws else 0)
                            else:
                                valid = False
                                break
                        if valid:
                            sub_body = body
                            for arg_idx, arg_val in enumerate(args, 1):
                                sub_body = sub_body.replace(f"#{arg_idx}", arg_val)
                            text = text[:m.start()] + sub_body + text[curr_idx:]
                        else:
                            break

            if not changed:
                break

        # Résolution contextuelle de \xspace
        text = re.sub(r'\\xspace\s*([,.:;!?\'"\)\}\]])', r'\1', text)
        text = re.sub(r'\\xspace\b\s*', ' ', text)

        return text


class LatexToMarkdownConverter:
    """Convertisseur de documents LaTeX vers Markdown GitHub Flavored avec KaTeX."""

    def __init__(self, root_tex_path: Path, bib_parser: Optional[BibTexParser] = None, base_dir: Optional[Path] = None, output_path: Optional[Path] = None):
        self.root_path = root_tex_path.resolve()
        self.root_dir = base_dir.resolve() if base_dir else self.root_path.parent
        self.bib_parser = bib_parser or BibTexParser()
        self.output_path = output_path.resolve() if output_path else None
        self.paper_slug = self.output_path.stem if self.output_path else ""
        self.cited_keys: List[str] = []
        self.title: str = ""
        self.authors: str = ""
        self.keywords: str = ""
        self.abstract: str = ""
        self.metadata: Dict[str, str] = {}
        self.macros: Dict[str, Dict[str, any]] = {}

    def resolve_inputs(self, tex_file: Path, visited: Optional[set] = None) -> str:
        """Résout récursivement les \\input{...} et \\include{...}."""
        if visited is None:
            visited = set()

        real_path = tex_file.resolve()
        if real_path in visited:
            return ""
        visited.add(real_path)

        if not real_path.exists():
            if real_path.with_suffix('.tex').exists():
                real_path = real_path.with_suffix('.tex')
            else:
                print(f"[Warning] Fichier introuvable: {real_path}")
                return f"\n<!-- Fichier introuvable: {tex_file.name} -->\n"

        try:
            content = real_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"[Error] Erreur lors de la lecture de {real_path}: {e}")
            return ""

        current_dir = real_path.parent

        def replace_input(match):
            rel_file = match.group(1).strip().strip('"{}\'')
            if not rel_file.endswith('.tex') and not '.' in os.path.basename(rel_file):
                rel_file += '.tex'
            
            target_path = current_dir / rel_file
            if not target_path.exists():
                target_path = self.root_dir / rel_file

            return self.resolve_inputs(target_path, visited)

        input_pattern = re.compile(r'\\(?:input|include)\s*\{([^}]+)\}')
        resolved_content = input_pattern.sub(replace_input, content)
        return resolved_content

    def strip_comments(self, text: str) -> str:
        """Supprime les commentaires LaTeX % tout en préservant \\%."""
        lines = []
        for line in text.splitlines():
            escaped_marker = "___ESCAPED_PERCENT___"
            temp_line = line.replace(r'\%', escaped_marker)
            if '%' in temp_line:
                temp_line = temp_line.split('%', 1)[0]
            temp_line = temp_line.replace(escaped_marker, r'%')
            lines.append(temp_line)
        return "\n".join(lines)

    def extract_metadata(self, text: str) -> str:
        """Extrait le titre, les auteurs, l'abstract et les métadonnées."""
        title_match = re.search(r'\\title\s*\{((?:[^{}]|{[^{}]*})*)\}', text, re.DOTALL)
        if title_match:
            self.title = self.clean_inline_formatting(title_match.group(1).strip())

        author_match = re.search(r'\\author\s*\{((?:[^{}]|{[^{}]*})*)\}', text, re.DOTALL)
        if author_match:
            raw_author = author_match.group(1).strip()
            raw_author = re.sub(r'\\and\b', ' & ', raw_author)
            raw_author = re.sub(r'\\thanks\{.*?\}', '', raw_author, flags=re.DOTALL)
            raw_author = re.sub(r'\\inst\{[^}]*\}', '', raw_author)
            raw_author = re.sub(r'\\orcid(?:ID)?\{[^}]*\}', '', raw_author)
            raw_author = re.sub(r'\\email\{[^}]*\}', '', raw_author)
            raw_author = re.sub(r'\\footnote\{[^}]*\}', '', raw_author)
            clean_author = self.clean_inline_formatting(raw_author).strip()
            if re.search(r'anonymous', clean_author, re.IGNORECASE):
                self.authors = "Anonymous Submission"
            else:
                self.authors = clean_author

        # Détection préalable des mots-clés si définis dans le préambule
        kw_match = re.search(r'\\keywords\s*\{', text)
        if kw_match:
            open_brace_idx = kw_match.end() - 1
            raw_kw, _ = LatexMacroEngine.extract_braced_group(text, open_brace_idx)
            if raw_kw:
                cleaned_kw = re.sub(r'\s+', ' ', raw_kw).strip()
                cleaned_kw = re.sub(r'\\and\b', ', ', cleaned_kw)
                cleaned_kw = self.clean_inline_formatting(cleaned_kw)
                items = [k.strip().strip(';') for k in re.split(r'\s*[,;]\s*', cleaned_kw) if k.strip().strip(';')]
                if items:
                    self.keywords = ", ".join(items)

        doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', text, re.DOTALL)
        if doc_match:
            body = doc_match.group(1)
        else:
            body = text

        body = re.sub(r'\\maketitle', '', body)
        return body

    def convert_headings(self, text: str) -> str:
        """Convertit les sections LaTeX en titres Markdown."""
        text = re.sub(r'\\section\*?\s*\{([^}]+)\}', r'\n\n## \1\n', text)
        text = re.sub(r'\\subsection\*?\s*\{([^}]+)\}', r'\n\n### \1\n', text)
        text = re.sub(r'\\subsubsection\*?\s*\{([^}]+)\}', r'\n\n#### \1\n', text)
        text = re.sub(r'\\paragraph\*?\s*\{([^}]+)\}', r'\n\n##### \1\n', text)
        text = re.sub(r'\\label\{[^}]+\}', '', text)
        return text

    @staticmethod
    def fix_xml_tex_tags(text: str) -> str:
        """
        Gère proprement les balises XML/TeX :
        - Remplace $\\langle\\text{selected\\_indices}\\rangle$, $\\langle selected\\_indices \\rangle$,
          \\langleselected_indices\\rangle, $\\langle\\text{reasoning}\\rangle$, \\langlereasoning\\rangle, etc.
          par <selected_indices> et <reasoning> en texte Markdown pur.
        - Nettoie les macros TeX non fermées ou combinées avec du Markdown comme **...** :_{train}.
        """
        # 1. Balises XML encapsulées dans KaTeX $...$ : $\langle\text{tag}\rangle$ ou $\langle tag \rangle$
        def repl_math_xml(m):
            inner = m.group(1).strip()
            inner = re.sub(r'\\text\{([^}]+)\}', r'\1', inner)
            inner = inner.replace(r'\_', '_').replace('\\', '').strip()
            if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', inner):
                return f"<{inner}>"
            return f"$\\langle \\text{{{inner}}} \\rangle$"

        text = re.sub(r'\$\s*\\langle\s*(.*?)\s*\\rangle\s*\$', repl_math_xml, text)

        # 2. Balises résiduelles ou fusionnées hors $...$
        def repl_fused_langle(m):
            tag = m.group(1).strip()
            tag = re.sub(r'\\text\{([^}]+)\}', r'\1', tag)
            tag = tag.replace(r'\_', '_').replace('\\', '').strip()
            return f"<{tag}>"

        text = re.sub(r'\\langle\s*(?:\\text\{)?([a-zA-Z][a-zA-Z0-9_\\-]*?)\}?\s*\\rangle', repl_fused_langle, text)
        text = re.sub(r'\\langle([a-zA-Z][a-zA-Z0-9_\\-]*?)\\rangle', repl_fused_langle, text)

        # 3. Réparation des macros TeX non fermées ou combinées avec du Markdown sur la même ligne
        text = re.sub(
            r'\$([^\$\n]*?)\\mathcal\{([a-zA-Z0-9_]+)\s*\*\*faire\*\*\s*:\s*_\{([^}]+)\}([^\$\n]*?)\$',
            r'$\1\\mathcal{\2}_{\3}\4$ **faire** :',
            text
        )
        text = re.sub(r'\*\*(faire|alors|sinon)\*\*\s*:\s*_\{([^}]+)\}', r'**\1** : \2', text)

        return text

    def convert_math(self, text: str) -> str:
        """Convertit et normalise les blocs mathématiques pour KaTeX."""
        text = self.fix_xml_tex_tags(text)

        def replace_display_env(match):
            env_name = match.group(1)
            content = match.group(2).strip()
            content = re.sub(r'\\label\{[^}]+\}', '', content)
            if 'align' in env_name:
                return f"\n\n$$\n\\begin{{aligned}}\n{content}\n\\end{{aligned}}\n$$\n\n"
            return f"\n\n$$\n{content}\n$$\n\n"

        text = re.sub(
            r'\\begin\{(equation|equation\*|align|align\*|gather|gather\*|multline|multline\*)\}(.*?)\\end\{\1\}',
            replace_display_env,
            text,
            flags=re.DOTALL
        )

        text = re.sub(r'\\\[(.*?)\\\]', r'\n\n$$\n\1\n$$\n\n', text, flags=re.DOTALL)
        text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
        return text

    def convert_citations(self, text: str) -> str:
        """Convertit \\cite, \\citep, \\citet en format Markdown via le parseur BibTeX."""
        def replace_cite(match):
            cmd = match.group(1)
            keys_str = match.group(2)
            keys = [k.strip() for k in keys_str.split(',') if k.strip()]
            for k in keys:
                if k not in self.cited_keys:
                    self.cited_keys.append(k)

            is_citet = (cmd == 'citet' or cmd == 'citeauthor')
            formatted = [self.bib_parser.format_citation(k, citet=is_citet) for k in keys]

            if is_citet:
                return " ".join(formatted)
            else:
                inner = "; ".join([f.strip("[]") for f in formatted])
                return f"[{inner}]"

        text = re.sub(r'\\(cite|citep|citet|citealt|citeauthor|citeyear|autocite)\s*\{([^}]+)\}', replace_cite, text)
        return text

    def resolve_image_path(self, raw_path: str) -> str:
        """
        Résout le chemin d'une image LaTeX par rapport au dossier du fichier .tex,
        convertit les figures vectorielles .pdf en .png si nécessaire via pymupdf,
        extrait (copie) physiquement l'image vers le dossier d'attachments du papier
        (papers/_attachments/<slug>/ et _attachments/<slug>/) pour pérennité et autonomie,
        et retourne le chemin Markdown relatif accessible (_attachments/<slug>/<nom_image>).
        """
        clean_path = raw_path.strip().strip('"{}\'')
        if clean_path.startswith("./"):
            clean_path = clean_path[2:]

        p = Path(clean_path)
        base_dirs = [
            self.root_path.parent,
            self.root_dir,
            self.root_path.parent / "figures",
            self.root_dir / "figures",
            self.root_path.parent / "assets",
            self.root_dir / "assets",
            self.root_path.parent / "assets" / "final",
            self.root_dir / "assets" / "final",
            self.root_path.parent / "images",
            self.root_dir / "images",
            self.root_path.parent / "img",
            self.root_dir / "img",
            self.root_path.parent.parent / "figures",
            self.root_dir.parent / "figures",
            self.root_path.parent.parent / "assets",
            self.root_dir.parent / "assets",
            self.root_path.parent.parent / "assets" / "final",
            self.root_dir.parent / "assets" / "final",
        ]

        # Scan des \graphicspath si présents dans le code source
        if hasattr(self, "raw_tex") and self.raw_tex:
            gp_matches = re.findall(r'\\graphicspath\s*\{([^}]+)\}', self.raw_tex)
            for gp in gp_matches:
                for sub_p in re.findall(r'\{([^}]+)\}', gp):
                    c_gp = sub_p.strip().strip('"{}\'')
                    if c_gp:
                        base_dirs.extend([
                            self.root_path.parent / c_gp,
                            self.root_dir / c_gp
                        ])

        check_exts = [".png", ".jpg", ".jpeg", ".webp", ".svg", ".pdf"]
        found_target: Optional[Path] = None

        for b_dir in base_dirs:
            if not b_dir.exists():
                continue
            # 1. Chemin direct
            target = b_dir / p
            if target.exists() and target.is_file():
                found_target = target
                break

            # 2. Si sans extension
            if not p.suffix:
                for ext in check_exts:
                    cand = b_dir / f"{clean_path}{ext}"
                    if cand.exists() and cand.is_file():
                        found_target = cand
                        break
                if found_target:
                    break

            # 3. Nom de fichier seul dans le dossier b_dir
            target_name = b_dir / p.name
            if target_name.exists() and target_name.is_file():
                found_target = target_name
                break

            if not p.suffix:
                for ext in check_exts:
                    cand = b_dir / f"{p.name}{ext}"
                    if cand.exists() and cand.is_file():
                        found_target = cand
                        break
                if found_target:
                    break

        if not found_target or not found_target.exists():
            return Path(clean_path).name

        # Résolution PDF -> Raster (PNG / JPG / WebP)
        if found_target.suffix.lower() == ".pdf":
            raster_found = None
            for alt_ext in [".png", ".jpg", ".jpeg", ".svg", ".webp"]:
                alt_cand = found_target.with_suffix(alt_ext)
                if alt_cand.exists() and alt_cand.is_file():
                    raster_found = alt_cand
                    break
            if raster_found:
                found_target = raster_found
            else:
                try:
                    import pymupdf
                    doc = pymupdf.open(str(found_target))
                    if len(doc) > 0:
                        page = doc[0]
                        pix = page.get_pixmap(dpi=300)
                        raster_png = found_target.with_suffix(".png")
                        pix.save(str(raster_png))
                        if raster_png.exists():
                            found_target = raster_png
                except Exception:
                    pass

        # Extraction physique de l'image vers le coffre VoiceNotes
        slug = getattr(self, "paper_slug", "")
        if not slug:
            if hasattr(self, "title") and self.title:
                slug = derive_output_path(self.root_path, self.title).stem
            else:
                slug = derive_output_path(self.root_path, "").stem
        if not slug:
            slug = "manuscript"

        vault_candidates = [
            Path.home() / "Documents" / "VoiceNotes",
            Path(r"C:\Users\Jamet\Documents\VoiceNotes"),
            Path(r"C:\Users\hjamet\Documents\VoiceNotes"),
        ]
        vault_dir = next((v for v in vault_candidates if v.exists()), None)

        safe_name = found_target.name.replace(" ", "_")
        if vault_dir:
            # Synchronisation robuste multi-dossiers coffre VoiceNotes
            dest_vault_dirs = [
                vault_dir / "papers" / "_attachments" / slug,
                vault_dir / "papers" / "_attachments",
                vault_dir / "_attachments" / slug,
                vault_dir / "_attachments"
            ]
            for v_d in dest_vault_dirs:
                try:
                    v_d.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(found_target), str(v_d / found_target.name))
                    if safe_name != found_target.name:
                        shutil.copy2(str(found_target), str(v_d / safe_name))
                except Exception:
                    pass

            # 3. Dossiers brain Antigravity actifs
            brain_base = Path.home() / ".gemini" / "antigravity" / "brain"
            brain_candidates = [
                brain_base / "c660c635-396c-43e2-b2a2-a93e44eda43e",
                brain_base / "609e421e-58fc-4531-8cda-99faf485e7d5",
                brain_base / "ca8e302c-8fa3-4cb0-90aa-cdae42831078",
                brain_base / "0f784e7c-2a27-43b2-a6ed-145b1f79668c",
            ]
            if hasattr(self, "brain_dir") and self.brain_dir:
                brain_candidates.insert(0, Path(self.brain_dir))
            if brain_base.exists():
                recent_brains = sorted(
                    [d for d in brain_base.iterdir() if d.is_dir() and not d.name.startswith('.')],
                    key=lambda d: d.stat().st_mtime,
                    reverse=True
                )[:12]
                for rb in recent_brains:
                    if rb not in brain_candidates:
                        brain_candidates.append(rb)
            for b_dir in brain_candidates:
                if b_dir.exists() and b_dir.is_dir():
                    try:
                        shutil.copy2(str(found_target), str(b_dir / found_target.name))
                        if safe_name != found_target.name:
                            shutil.copy2(str(found_target), str(b_dir / safe_name))
                    except Exception:
                        pass

            if not hasattr(self, "first_image_rel") or not self.first_image_rel:
                self.first_image_rel = f"papers/_attachments/{slug}/{safe_name}"
            if not hasattr(self, "first_image_name") or not self.first_image_name:
                self.first_image_name = safe_name

            return safe_name

        if not hasattr(self, "first_image_rel") or not self.first_image_rel:
            self.first_image_rel = f"papers/_attachments/{slug}/{safe_name}"
        if not hasattr(self, "first_image_name") or not self.first_image_name:
            self.first_image_name = safe_name
        return safe_name

    @staticmethod
    def replace_shortstack(text: str) -> str:
        r"""
        Intercepte \shortstack{...} ou \shortstack[...]{...} et convertit son contenu interne :
        - Remplace les sauts de ligne \\ (et \\[...]) par <br>.
        - Si une sous-indication entre parenthèses non stylisée (ex: '(7.56 rds)') est présente,
          l'enrobe élégamment en italique '*(7.56 rds)*'.
        """
        if r'\shortstack' not in text:
            return text
        pattern = re.compile(r'\\shortstack(?:\s*\[[^\]]*\])?\s*\{')
        pos = 0
        res = []
        while True:
            m = pattern.search(text, pos)
            if not m:
                res.append(text[pos:])
                break
            res.append(text[pos:m.start()])
            inner, end_idx = LatexMacroEngine.extract_braced_group(text, m.end() - 1)
            inner = LatexToMarkdownConverter.replace_shortstack(inner)
            lines = re.split(r'\\\\(?:\s*\[[^\]]*\])?', inner)
            formatted_lines = []
            for l in lines:
                ls = l.strip()
                if re.match(r'^\([^\(\)]+\)$', ls) and not (ls.startswith('*') or ls.startswith(r'\textbf') or ls.startswith(r'\textit') or ls.startswith(r'\emph')):
                    ls = f"*{ls}*"
                formatted_lines.append(ls)
            res.append("<br>".join(formatted_lines))
            pos = end_idx
        return "".join(res)

    def convert_tables(self, text: str) -> str:
        """Convertit génériquement les tableaux LaTeX (tabular, tabularx, booktabs) en tableaux Markdown natifs sans hardcoding."""
        def expand_cell(cell: str) -> list:
            m = re.search(r'\\multicolumn\s*\{(\d+)\}\s*\{[^{}]*\}\s*\{', cell)
            if not m:
                m_row = re.search(r'\\multirow\s*\{(\d+)\}\s*\{[^{}]*\}\s*\{', cell)
                if m_row:
                    content, end_idx = LatexMacroEngine.extract_braced_group(cell, m_row.end() - 1)
                    before = cell[:m_row.start()].strip()
                    after = cell[end_idx:].strip()
                    return [f"{before} {content} {after}".strip()]
                return [cell]
            n_cols = int(m.group(1))
            open_idx = m.end() - 1
            content, end_idx = LatexMacroEngine.extract_braced_group(cell, open_idx)
            before = cell[:m.start()].strip()
            after = cell[end_idx:].strip()
            res = f"{before} {content} {after}".strip()
            return [res] + [""] * (n_cols - 1)

        def parse_single_tabular(raw_tab: str, caption: str = "") -> str:
            clean = re.sub(r'\\(?:toprule|midrule|bottomrule|hline|centering|small|footnotesize|scriptsize|label\{[^}]+\})', '', raw_tab)
            clean = re.sub(r'\\addlinespace(?:\s*\[[^\]]*\])?', '', clean)
            clean = re.sub(r'\\vspace\*?(?:\{[^}]*\}|\[[^\]]*\])', '', clean)
            clean = re.sub(r'\\cmidrule(?:\([^)]*\))?(?:\[[^\]]*\])?\{[^}]*\}', '', clean)
            clean = re.sub(r'\\cline\{[^}]*\}', '', clean)
            clean = re.sub(r'\\resizebox\{[^}]*\}\{[^}]*\}\{?', '', clean)

            # Intercepter \shortstack avant de découper les lignes du tableau avec \\
            clean = LatexToMarkdownConverter.replace_shortstack(clean)

            amp_marker = "___ESC_AMP___"
            clean = clean.replace(r'\&', amp_marker)

            # Découpage par lignes \\ avant tout nettoyage inline
            row_splits = re.split(r'\\\\(?:\s*\[[^\]]*\])?', clean)
            table_rows = []
            max_cols = 0
            for r in row_splits:
                r = r.strip()
                if not r:
                    continue
                cells = [c.replace(amp_marker, r'\&') for c in r.split('&')]
                expanded = []
                for c in cells:
                    expanded.extend(expand_cell(c.strip()))
                if any(expanded):
                    table_rows.append(expanded)
                    if len(expanded) > max_cols:
                        max_cols = len(expanded)

            if not table_rows or max_cols == 0:
                return ""

            normalized_rows = []
            for row in table_rows:
                if len(row) < max_cols:
                    row.extend([""] * (max_cols - len(row)))
                cleaned_row = []
                for cell in row:
                    c = self.clean_inline_formatting(cell.strip())
                    c = c.replace('|', '\\|').replace('\n', ' ')
                    cleaned_row.append(c)
                normalized_rows.append(cleaned_row)

            md_lines = []
            if caption:
                md_lines.append(f"> [!NOTE] **📊 Table : {self.clean_inline_formatting(caption)}**\n")

            header = normalized_rows[0]
            md_lines.append("| " + " | ".join(header) + " |")
            md_lines.append("| " + " | ".join([":---"] * max_cols) + " |")
            for row in normalized_rows[1:]:
                md_lines.append("| " + " | ".join(row) + " |")

            return "\n\n" + "\n".join(md_lines) + "\n\n"

        def parse_table_env(match):
            full_table = match.group(0)
            tab_pattern = re.compile(r'\\begin\{(?:tabular|tabularx)\}(?:\s*(?:\[[^\]]*\]|\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}))+\s*(.*?)\\end\{(?:tabular|tabularx)\}', re.DOTALL)
            tabular_matches = list(tab_pattern.finditer(full_table))
            if not tabular_matches:
                return full_table

            converted_parts = []
            for tm in tabular_matches:
                start_pos = max(0, tm.start() - 1500)
                pre_text = full_table[start_pos:tm.start()]
                last_tab = pre_text.rfind(r'\end{tabular')
                if last_tab != -1:
                    pre_text = pre_text[last_tab:]
                m_cap = list(re.finditer(r'\\caption\s*\{', pre_text))
                caption = ""
                if m_cap:
                    caption, _ = LatexMacroEngine.extract_braced_group(pre_text, m_cap[-1].end() - 1)
                else:
                    post_text = full_table[tm.end():tm.end() + 1500]
                    next_tab = post_text.find(r'\begin{tabular')
                    if next_tab != -1:
                        post_text = post_text[:next_tab]
                    m_post = re.search(r'\\caption\s*\{', post_text)
                    if m_post:
                        caption, _ = LatexMacroEngine.extract_braced_group(post_text, m_post.end() - 1)

                raw_body = tm.group(1)
                md_tab = parse_single_tabular(raw_body, caption.strip())
                converted_parts.append(md_tab)

            return "\n\n" + "\n\n".join(converted_parts) + "\n\n"

        table_pattern = re.compile(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', re.DOTALL)
        text = table_pattern.sub(parse_table_env, text)

        isolated_tabular = re.compile(r'\\begin\{(?:tabular|tabularx)\}(?:\s*(?:\[[^\]]*\]|\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}))+\s*(.*?)\\end\{(?:tabular|tabularx)\}', re.DOTALL)
        def parse_isolated(match):
            return parse_single_tabular(match.group(1), "")
        text = isolated_tabular.sub(parse_isolated, text)

        return text

    def convert_figures(self, text: str) -> str:
        """Convertit les figures, includegraphics et tikz en blocs Markdown / Callouts avec résolution d'images."""
        def parse_figure(match):
            full_fig = match.group(0)
            cap_match = re.search(r'\\caption\s*\{', full_fig)
            caption = ""
            if cap_match:
                cap_content, _ = LatexMacroEngine.extract_braced_group(full_fig, cap_match.end() - 1)
                caption = cap_content.strip()

            clean_cap = self.clean_inline_formatting(caption) if caption else "Figure"

            img_matches = list(re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', full_fig))
            if img_matches:
                img_blocks = []
                for im in img_matches:
                    raw_path = im.group(1).strip().strip('"{}\'')
                    safe_img_name = self.resolve_image_path(raw_path)
                    img_blocks.append(f"![[{safe_img_name}]]")

                imgs_str = "\n\n".join(img_blocks)
                cap_lines = [c.strip() for c in clean_cap.splitlines() if c.strip()]
                formatted_cap = "\n> ".join(cap_lines) if cap_lines else "Figure"
                return f"\n\n> [!NOTE] **🖼️ Figure : {formatted_cap}**\n\n{imgs_str}\n\n"

            tikz_match = re.search(r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}', full_fig, flags=re.DOTALL)
            if tikz_match:
                tikz_code = tikz_match.group(1).strip()
                nodes = re.findall(r'\\node\[[^\]]*\]\s*(?:\([^\)]*\)\s*)?(?:at\s*\([^\)]*\)\s*)?\{([^}]+)\};', tikz_code)
                if nodes:
                    formatted_steps = []
                    for n in nodes:
                        clean_n = self.clean_inline_formatting(n.strip())
                        if clean_n:
                            formatted_steps.append(f"> - {clean_n}")
                    steps_str = "\n".join(formatted_steps)
                    return (
                        f"\n\n> [!NOTE]\n"
                        f"> **📐 Schéma & Étapes : {clean_cap}**\n"
                        f">\n"
                        f"{steps_str}\n\n"
                    )
                return f"\n\n> [!NOTE]\n> **📐 Schéma : {clean_cap}**\n\n"

            # Si ni image ni tikz, préserver le contenu interne (slmbox, tcolorbox, tabular)
            inner_content = re.sub(r'^\\begin\{figure\*?\}(?:\[[^\]]*\])?\s*', '', full_fig)
            inner_content = re.sub(r'\\end\{figure\*?\}\s*$', '', inner_content)
            inner_content = re.sub(r'\\caption\s*\{', lambda m: "", inner_content)
            header = f"\n\n> [!NOTE] **🖼️ Figure : {clean_cap}**\n\n" if caption else ""
            return f"{header}\n\n{inner_content}\n\n"

        figure_pattern = re.compile(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', re.DOTALL)
        text = figure_pattern.sub(parse_figure, text)

        def parse_standalone_img(match):
            raw_path = match.group(1).strip().strip('"{}\'')
            safe_img_name = self.resolve_image_path(raw_path)
            return f"\n\n![[{safe_img_name}]]\n\n"

        text = re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', parse_standalone_img, text)

        def parse_standalone_tikz(match):
            tikz_code = match.group(1).strip()
            nodes = re.findall(r'\\node\[[^\]]*\]\s*(?:\([^\)]*\)\s*)?(?:at\s*\([^\)]*\)\s*)?\{([^}]+)\};', tikz_code)
            if nodes:
                formatted_steps = []
                for n in nodes:
                    clean_n = self.clean_inline_formatting(n.strip())
                    if clean_n:
                        formatted_steps.append(f"> - {clean_n}")
                steps_str = "\n".join(formatted_steps)
                return f"\n\n> [!NOTE]\n> **📐 Schéma de Processus :**\n>\n{steps_str}\n\n"
            return ""

        text = re.sub(r'\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}', parse_standalone_tikz, text, flags=re.DOTALL)
        return text

    def convert_lists(self, text: str) -> str:
        """Convertit itemize et enumerate en listes Markdown en nettoyant les options enumitem."""
        def parse_list(match):
            env_type = match.group(1)
            body = match.group(2)
            
            m_first_item = re.search(r'\\item(?![a-zA-Z])', body)
            if m_first_item:
                body = body[m_first_item.start():]
            
            items = re.split(r'\\item(?![a-zA-Z])(?:\s*\[[^\]]*\])?\s*', body)
            md_items = []
            idx = 1
            for it in items:
                it = it.strip()
                if not it:
                    continue
                it = re.sub(r'^\s*\[[^\]]*\]\s*', '', it)
                clean_it = " ".join([line.strip() for line in it.splitlines() if line.strip()])
                if env_type == 'enumerate':
                    md_items.append(f"{idx}. {clean_it}")
                    idx += 1
                else:
                    md_items.append(f"- {clean_it}")
            
            return "\n\n" + "\n".join(md_items) + "\n\n"

        for _ in range(4):
            text = re.sub(r'\\begin\{(itemize|enumerate)\}(?:\s*\[[^\]]*\])?(.*?)\\end\{\1\}', parse_list, text, flags=re.DOTALL)

        return text

    def convert_keywords(self, text: str) -> str:
        r"""
        Extrait et convertit les commandes et environnements de mots-clés LaTeX
        (\keywords{...}, \begin{keywords}...\end{keywords}, \begin{IEEEkeywords}...)
        en bloc Markdown propre: **Mots-clés :** item1, item2, item3.
        Remplace \and par une virgule et nettoie les backslashes parasites.
        """
        def format_kw_items(raw_content: str) -> str:
            content = re.sub(r'\s+', ' ', raw_content).strip()
            content = re.sub(r'\\and\b', ', ', content)
            content = self.clean_inline_formatting(content)
            items = [k.strip().strip(';') for k in re.split(r'\s*[,;]\s*', content) if k.strip().strip(';')]
            if items and not self.keywords:
                self.keywords = ", ".join(items)
            return f"**Mots-clés :** {', '.join(items)}"

        # 1. Environnements keywords / IEEEkeywords
        def repl_env_kw(match):
            kw_str = format_kw_items(match.group(1))
            return f"\n\n{kw_str}\n\n"

        text = re.sub(r'\\begin\{(?:IEEE)?keywords\}(.*?)\\end\{(?:IEEE)?keywords\}', repl_env_kw, text, flags=re.DOTALL | re.IGNORECASE)

        # 2. Commandes \keywords{...} avec accolades équilibrées
        kw_pattern = re.compile(r'\\keywords\s*\{')
        while True:
            m = kw_pattern.search(text)
            if not m:
                break
            open_brace_idx = m.end() - 1
            content, end_idx = LatexMacroEngine.extract_braced_group(text, open_brace_idx)
            replacement = f"\n\n{format_kw_items(content)}\n\n"
            text = text[:m.start()] + replacement + text[end_idx:]

        return text

    def convert_environments(self, text: str) -> str:
        """
        Convertit les environnements LaTeX de citation ou blocs textuels (abstract, quote, quotation, verse, etc.)
        en blocs de citation Markdown (> ...).
        Gère également les algorithmes, boîtes tcolorbox / exemples et déballe center.
        """
        text = re.sub(r'\\begin\{center\}(.*?)\\end\{center\}', r'\1', text, flags=re.DOTALL)

        # Environnements de blocs personnalisés (runningexample, slmbox, tcolorbox, example, remark, note)
        def parse_custom_box(match):
            env_name = match.group(1)
            arg = match.group(2).strip() if match.group(2) else ""
            content = match.group(3).strip()

            # Nettoyage systématique des environnements de layout et commandes internes
            content = re.sub(r'\\(?:begin|end)[ \t]*\{?[ \t]*(?:minipage|flushleft|flushright)[ \t]*\}?(?:\{[^}]*\}|\\[a-zA-Z]+)*', '', content)
            content = re.sub(r'\\(?:begin|end)minipage(?:\\[a-zA-Z]+|\{[^}]*\})*', '', content)
            content = re.sub(r'\\(?:begin|end)(?:flushleft|flushright)', '', content)
            content = re.sub(r'\\tcbline\*?', '---', content)
            content = re.sub(r'\\(?:linewidth|textwidth|columnwidth)\b', '', content)
            content = re.sub(r'sep0\.5pt[ \t]*\\setlength\\parsep0pt[ \t]*\\setlength\\parskip0pt', '', content)
            content = re.sub(r'\\setlength[ \t]*\\?[a-zA-Z]+[ \t]*\{?[^}\n]*\}?', '', content)
            content = re.sub(r'\\(?:itemsep|parsep|parskip)[0-9.]*[a-zA-Z]*', '', content)
            content = re.sub(r'\\(?:centering|noindent|frenchspacing|medskip|bigskip|smallskip)\b[ \t]*', '', content)
            content = re.sub(r'\\\\(?:\s*\[[^\]]*\])?', '\n', content)

            lines = content.splitlines()
            quoted_lines = [f"> {l.strip()}" if l.strip() else ">" for l in lines]
            title_str = f" ({arg})" if arg else ""
            header = f"> [!EXAMPLE] **Exemple{title_str}**\n>\n"
            return "\n\n" + header + "\n".join(quoted_lines) + "\n\n"

        box_envs = r'(?:runningexample|slmbox|example|tcolorbox|remark|note)'
        text = re.sub(rf'\\begin\{{({box_envs})\}}(?:\{{([^}}]*)\}})?(?:\[[^\]]*\])?(.*?)\\end\{{\1\}}', parse_custom_box, text, flags=re.DOTALL)

        # Environnements d'algorithmes (algorithm, algorithmic)
        def parse_algorithm(match):
            full_algo = match.group(0)
            caption_m = re.search(r'\\caption\{((?:[^{}]|{[^{}]*})*)\}', full_algo)
            caption = caption_m.group(1).strip() if caption_m else "Algorithme"
            caption = self.clean_inline_formatting(caption)
            
            body_m = re.search(r'\\begin\{algorithmic\}(?:\[\d+\])?(.*?)\\end\{algorithmic\}', full_algo, re.DOTALL)
            algo_body = body_m.group(1).strip() if body_m else full_algo

            def replace_algo_cmd(line_str: str, cmd_name: str, prefix_str: str, suffix_str: str) -> str:
                pattern = re.compile(rf'\\{cmd_name}\s*\{{')
                while True:
                    m = pattern.search(line_str)
                    if not m:
                        break
                    open_brace_idx = m.end() - 1
                    content_inner, end_idx = LatexMacroEngine.extract_braced_group(line_str, open_brace_idx)
                    line_str = line_str[:m.start()] + f"{prefix_str}{content_inner}{suffix_str}" + line_str[end_idx:]
                return line_str

            lines = []
            for raw_line in algo_body.splitlines():
                l = raw_line.strip()
                if not l or l.startswith(r'\caption') or l.startswith(r'\label'):
                    continue
                l = re.sub(r'\\Require\s*', '**Entrée :** ', l)
                l = re.sub(r'\\Ensure\s*', '**Sortie :** ', l)
                l = re.sub(r'\\Statex\s*', '', l)
                l = re.sub(r'\\State\s*', '- ', l)
                l = replace_algo_cmd(l, 'For', '- **Pour** ', ' **faire** :')
                l = re.sub(r'\\EndFor\b', '', l)
                l = replace_algo_cmd(l, 'If', '- **Si** ', ' **alors** :')
                l = replace_algo_cmd(l, 'ElsIf', '- **Sinon si** ', ' **alors** :')
                l = re.sub(r'\\Else\b', '- **Sinon** :', l)
                l = re.sub(r'\\EndIf\b', '', l)
                l = replace_algo_cmd(l, 'While', '- **Tant que** ', ' **faire** :')
                l = re.sub(r'\\EndWhile\b', '', l)
                l = re.sub(r'\\Return\s*', '**Retourner** ', l)
                l = re.sub(r'\\Comment\s*', '// ', l)
                if l.strip():
                    lines.append(f"> {l}")
            
            content_str = "\n".join(lines)
            return f"\n\n> [!NOTE]\n> **📜 Algorithme : {caption}**\n>\n{content_str}\n\n"

        text = re.sub(r'\\begin\{algorithm\*?\}(?:\[[^\]]*\])?(.*?)\\end\{algorithm\*?\}', parse_algorithm, text, flags=re.DOTALL)

        env_names = r'(?:abstract|quote|quotation|verse)'
        def parse_quote_env(match):
            content = match.group(2).strip()
            lines = content.splitlines()
            quoted_lines = [f"> {l}" if l.strip() else ">" for l in lines]
            return "\n\n" + "\n".join(quoted_lines) + "\n\n"

        for _ in range(3):
            text = re.sub(rf'\\begin\{{({env_names})\}}(?:\[[^\]]*\])?(.*?)\\end\{{\1\}}', parse_quote_env, text, flags=re.DOTALL)
        return text

    def clean_inline_formatting(self, text: str) -> str:
        """Nettoie le formatage inline LaTeX pour obtenir un texte Markdown fluide."""
        # Pré-normalisation des sauts de paragraphe et espacements verticaux
        text = re.sub(r'\\par\b', '\n\n', text)
        text = re.sub(r'\\(?:smallskip|medskip|bigskip)\b', '\n\n', text)
        text = re.sub(r'\\(?:vspace|hspace|addtolength)\*?\{[^}]*\}(?:\{[^}]*\})?', '\n\n', text)
        text = re.sub(r'\\(?:noindent|indent)\s*(?=\\textbf|\w)', '\n\n', text)
        text = self.replace_shortstack(text)

        math_map = {}
        def repl_display(match):
            token = f"___MATH_BLOCK_DISPLAY_{len(math_map)}___"
            math_map[token] = match.group(0)
            return token

        def repl_inline(match):
            token = f"___MATH_BLOCK_INLINE_{len(math_map)}___"
            math_map[token] = match.group(0)
            return token

        text = re.sub(r'\$\$.*?\$\$', repl_display, text, flags=re.DOTALL)
        text = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', repl_inline, text)

        for _ in range(3):
            text = re.sub(r'\\textbf\{((?:[^{}]|{[^{}]*})*)\}', r'**\1**', text)
            text = re.sub(r'\\textit\{((?:[^{}]|{[^{}]*})*)\}', r'*\1*', text)
            text = re.sub(r'\\emph\{((?:[^{}]|{[^{}]*})*)\}', r'*\1*', text)
            text = re.sub(r'\\underline\{((?:[^{}]|{[^{}]*})*)\}', r'**\1**', text)
            text = re.sub(r'\\sout\{((?:[^{}]|{[^{}]*})*)\}', r'~~\1~~', text)
            text = re.sub(r'\\texttt\{((?:[^{}]|{[^{}]*})*)\}', r'`\1`', text)
            text = re.sub(r'\\textsc\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\text\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\mbox\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\textnormal\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\textrm\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\textup\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)

        # Références croisées et labels
        text = re.sub(r'\\eqref\{([^}]+)\}', r'(\1)', text)
        text = re.sub(r'\\(?:ref|autoref|pageref)\{([^}]+)\}', r'[\1]', text)
        text = re.sub(r'\\label\{[^}]+\}', '', text)

        # Nettoyage des métadonnées académiques inline
        text = re.sub(r'\\inst\{[^}]*\}', '', text)
        text = re.sub(r'\\orcid(?:ID)?\{[^}]*\}', '', text)
        text = re.sub(r'\\email\{([^}]+)\}', r'<\1>', text)
        text = re.sub(r'\\(?:institute|affiliation|affiliations|titlerunning|authorrunning)\{[^}]*\}', '', text)

        text = re.sub(r'\\\s+', ' ', text)
        text = re.sub(r'\\xspace\s*([,.:;!?\'"\)\}\]])', r'\1', text)
        text = re.sub(r'\\xspace\b\s*', ' ', text)
        text = re.sub(r'\\url\{([^}]+)\}', r'<\1>', text)
        text = re.sub(r'\\href\{([^}]+)\}\{([^}]+)\}', r'[\2](\1)', text)
        text = re.sub(r'\\footnote\{([^}]+)\}', r' (*Note: \1*)', text)

        text = re.sub(r'(?<![:|\-])---(?![:|\-])', '—', text)
        text = re.sub(r'(?<![:|\-])--(?![:|\-])', '–', text)
        text = text.replace('``', '"')
        text = text.replace("''", '"')
        text = text.replace('~', ' ')
        text = text.replace(r'\,', ' ')
        text = text.replace(r'\;', ' ')
        text = text.replace(r'\:', ' ')
        text = text.replace(r'\!', '')
        text = text.replace(r'\&', '&')
        text = text.replace(r'\_', '_')
        text = text.replace(r'\#', '#')
        text = text.replace(r'\%', '%')
        text = text.replace(r'\$', '$')
        text = text.replace(r'\{', '{')
        text = text.replace(r'\}', '}')

        # Ponctuation et symboles
        text = re.sub(r'\\(?:dots|ldots|cdots)\b', '...', text)
        text = re.sub(r'\\(?:quad|qquad|enspace|enskip)\b', ' ', text)
        text = text.replace(r'\copyright', '©')
        text = text.replace(r'\degree', '°')
        text = text.replace(r'\pm', '±')
        text = text.replace(r'\times', '×')
        text = text.replace(r'\sim', '~')
        text = text.replace(r'\bullet', '•')

        # Nettoyage précoce des commandes de bibliographie et citations silencieuses (avant décodage des accolades)
        text = re.sub(r'\\nocite\*?(?:\{[^}]*\})?', '', text)
        text = re.sub(r'\\(?:bibliography|bibliographystyle)(?:\{[^}]*\}|[a-zA-Z0-9_-]+)?', '', text)

        # Décodage des accents LaTeX
        text = BibTexParser.decode_latex_accents(text)

        # Nettoyage des commandes cosmétiques et boilerplates (horizontal whitespace uniquement pour ne pas avaler les sauts de ligne)
        text = re.sub(r'\\(?:centering|noindent|frenchspacing|medskip|bigskip|smallskip|clearpage|newpage|vfill|hfill|small|footnotesize|scriptsize|large|Large|LARGE|huge|Huge|sffamily|ttfamily|rmfamily|bfseries|itshape|normalsize|tiny|relax|strut|leavevmode|selectfont|normalfont|protect)(?:\b|(?=[^a-zA-Z]))[ \t]*', ' ', text)
        text = re.sub(r'\\(?:begin|end)[ \t]*\{?[ \t]*(?:minipage|flushleft|flushright)[ \t]*\}?(?:\{[^}]*\}|\\[a-zA-Z]+)*', '', text)
        text = re.sub(r'\\(?:begin|end)minipage(?:\\[a-zA-Z]+|\{[^}]*\})*', '', text)
        text = re.sub(r'\\(?:begin|end)(?:flushleft|flushright)', '', text)
        text = re.sub(r'\\tcbline\*?', '---', text)
        text = re.sub(r'\\(?:linewidth|textwidth|columnwidth)\b', '', text)
        text = self.fix_xml_tex_tags(text)
        text = re.sub(r'sep0\.5pt[ \t]*\\setlength\\parsep0pt[ \t]*\\setlength\\parskip0pt', '', text)
        text = re.sub(r'\\setlength[ \t]*\\?[a-zA-Z]+[ \t]*\{?[^}\n]*\}?', '', text)
        text = re.sub(r'\\(?:itemsep|parsep|parskip)[0-9.]*[a-zA-Z]*', '', text)
        text = re.sub(r'\\(?:draw|fill|node|path|coordinate)\[[^\]]*\].*?;', '', text)
        text = re.sub(r'\\(?:definecolor|colorlet|tikzset|pgfdeclareimage)\{[^}]*\}\{[^}]*\}', '', text)
        text = re.sub(r'\\(?:setcounter|addtocounter)\{[^}]*\}\{[^}]*\}', '', text)
        text = re.sub(r'\\(?:newcommand|renewcommand|providecommand)\*?\s*\{\\[a-zA-Z]+\}(?:\[\d+\])?\{.*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\(?:color|textcolor)\{[^}]*\}\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
        text = re.sub(r'\\(?:phantom|hphantom|vphantom)\{[^}]*\}', '', text)
        text = re.sub(r'\\(?:raisebox|adjustbox)\{[^}]*\}\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
        text = re.sub(r'\\resizebox\{[^}]*\}\{[^}]*\}\{?', '', text)
        text = re.sub(r'\\scalebox\{[^}]*\}\{?', '', text)
        text = re.sub(r'\\setlength\{[^}]+\}\{[^}]+\}', '', text)
        text = re.sub(r'\\urlstyle\{[^}]+\}', '', text)
        text = re.sub(r'\\def\\[a-zA-Z]+\{[^}]*\}', '', text)
        text = re.sub(r'\\usetikzlibrary\{[^}]+\}', '', text)
        text = re.sub(r'\\pdfinfo\{[^}]*\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\affiliations\{([^}]*)\}', r'\n*Affiliations : \1*\n', text)
        text = re.sub(r'\\nocite\*?(?:\{[^}]*\})?', '', text)
        text = re.sub(r'\\(?:bibliography|bibliographystyle)(?:\{[^}]*\}|[a-zA-Z0-9_-]+)?', '', text)
        text = re.sub(r'\{\s*\}', '', text)

        text = re.sub(r'\[scale=[^\]]+\]', '', text)
        text = re.sub(r'\[leftmargin=[^\]]+\]', '', text)

        # Nettoyage des balises de gras redondantes (e.g. ****texte**** -> **texte**)
        text = re.sub(r'\*{4,}(.*?)\*{4,}', r'**\1**', text)

        for token, math_content in math_map.items():
            text = text.replace(token, math_content)

        return text

    def format_paragraphs(self, text: str) -> str:
        """
        Garantit un espacement aéré en Markdown :
        - Sépare distinctement chaque paragraphe par un saut de ligne vide (\n\n).
        - Assemble les lignes d'un même paragraphe de texte fluide.
        - Préserve l'intégrité des blocs spéciaux (titres, citations, callouts, tables, math KaTeX, listes).
        """
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        raw_blocks = re.split(r'\n\s*\n', text.strip())
        formatted_blocks = []

        for block in raw_blocks:
            lines = [l.rstrip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue

            first_line = lines[0].strip()
            # Si le bloc contient une ou plusieurs images Markdown, isoler chaque image sur sa propre ligne avec \n\n
            if any(l.strip().startswith('![') for l in lines):
                formatted_blocks.append('\n\n'.join(l.strip() for l in lines))
            # Si le bloc contient une ligne de tableau, ou commence par un titre, citation/callout, math, ou liste
            elif (any(l.strip().startswith('|') for l in lines) or
                first_line.startswith(('#', '>', '$$')) or
                any(l.strip().startswith(('>', '$$')) for l in lines) or
                re.match(r'^\s*[-*+]\s+', first_line) or
                re.match(r'^\s*\d+\.\s+', first_line)):
                formatted_blocks.append('\n'.join(lines))
            else:
                para_text = ' '.join(l.strip() for l in lines)
                formatted_blocks.append(para_text)

        result = '\n\n'.join(formatted_blocks)
        # S'assurer que les titres ont toujours une ligne vide avant et après
        result = re.sub(r'([^\n])\n(#{1,6}\s+)', r'\1\n\n\2', result)
        result = re.sub(r'(#{1,6}\s+[^\n]+)\n([^\n#])', r'\1\n\n\2', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result

    def convert(self) -> str:
        """Pipeline complet de conversion."""
        print(f"[Conversion] Résolution récursive depuis {self.root_path.name}...")
        raw_text = self.resolve_inputs(self.root_path)

        if not self.bib_parser.entries:
            for bib_file in self.root_dir.glob("*.bib"):
                print(f"[BibTeX] Détection automatique de la bibliographie: {bib_file.name}")
                self.bib_parser.load_bib_file(bib_file)

        print("[Conversion] Nettoyage des commentaires et extraction des macros...")
        text_no_comments = self.strip_comments(raw_text)
        text_no_macros, self.macros = LatexMacroEngine.extract_macros(text_no_comments)
        if self.macros:
            print(f"[Macros] {len(self.macros)} macro(s) personnalisée(s) extraite(s) : {list(self.macros.keys())}")
            text_expanded = LatexMacroEngine.expand_macros(text_no_macros, self.macros)
        else:
            text_expanded = text_no_comments

        print("[Conversion] Extraction des métadonnées...")
        body = self.extract_metadata(text_expanded)

        if not getattr(self, "paper_slug", ""):
            if not self.output_path:
                self.output_path = derive_output_path(self.root_path, self.title)
            self.paper_slug = self.output_path.stem

        print("[Conversion] Conversion des structures : Maths, Mots-clés, Citations, Figures, Tableaux, Listes, Environnements, Titres, Formatage...")
        body = self.convert_math(body)
        body = self.convert_keywords(body)
        body = self.convert_citations(body)
        body = self.convert_figures(body)
        body = self.convert_tables(body)
        body = self.convert_lists(body)
        body = self.convert_environments(body)
        body = self.convert_headings(body)
        body = self.clean_inline_formatting(body)
        body = self.format_paragraphs(body)

        body = re.sub(r'\n{3,}', '\n\n', body).strip()

        doc_parts = []
        if self.title:
            doc_parts.append(f"# {self.title}\n")
        else:
            doc_parts.append(f"# {self.root_path.stem}\n")

        if self.authors:
            doc_parts.append(f"**Auteurs :** {self.authors}\n")

        if self.keywords and "**Mots-clés :**" not in body:
            doc_parts.append(f"**Mots-clés :** {self.keywords}\n")

        doc_parts.append(body)

        if self.cited_keys:
            doc_parts.append("\n\n## 📚 Références Bibliographiques\n")
            for k in self.cited_keys:
                doc_parts.append(self.bib_parser.format_full_reference(k))

        final_md = "\n\n".join(doc_parts)
        formatted = self.format_paragraphs(final_md)
        return self.sanitize_callouts(formatted)

    @staticmethod
    def sanitize_callouts(text: str) -> str:
        """
        Garantit le formatage 100% natif et valide des callouts Obsidian :
        1. Chaque en-tête [!TYPE] sans '> ' est corrigé en '> [!TYPE]'.
        2. Chaque ligne du corps d'un callout commence strictement par '> ' (ou '>' si vide).
        3. Aucune ligne vide sans '>' ne subsiste à l'intérieur d'un callout.
        4. Les espaces parasites avant '>' (ex: ' > ') sont normalisés en '> '.
        5. Les environnements résiduels LaTeX (minipage, flushleft, tcbline, etc.) sont nettoyés sans altérer les sauts de ligne.
        """
        text = re.sub(r'\\(?:begin|end)[ \t]*\{?[ \t]*(?:minipage|flushleft|flushright)[ \t]*\}?(?:\{[^}]*\}|\\[a-zA-Z]+)*', '', text)
        text = re.sub(r'\\(?:begin|end)minipage(?:\\[a-zA-Z]+|\{[^}]*\})*', '', text)
        text = re.sub(r'\\(?:begin|end)(?:flushleft|flushright)', '', text)
        text = re.sub(r'\\tcbline\*?', '---', text)
        text = re.sub(r'\\(?:linewidth|textwidth|columnwidth)\b', '', text)
        text = LatexToMarkdownConverter.fix_xml_tex_tags(text)
        text = re.sub(r'sep0\.5pt[ \t]*\\setlength\\parsep0pt[ \t]*\\setlength\\parskip0pt', '', text)
        text = re.sub(r'\\setlength[ \t]*\\?[a-zA-Z]+[ \t]*\{?[^}\n]*\}?', '', text)
        text = re.sub(r'\\(?:itemsep|parsep|parskip)[0-9.]*[a-zA-Z]*', '', text)

        # 1. Isoler et normaliser les en-têtes de callouts
        text = re.sub(r'(</(?:del|ins|span|div|p)>)[ \t]*(> \[[!A-Za-z])', r'\1\n\n\2', text)
        text = re.sub(r'([^\n>])[ \t]*(> \[[!A-Za-z])', r'\1\n\n\2', text)
        text = re.sub(r'^[ \t]*\[!([a-zA-Z]+)\]([^\n]*)$', r'> [!\1]\2', text, flags=re.MULTILINE)
        text = re.sub(r'^[ \t]+>[ \t]*\[!([a-zA-Z]+)\]([^\n]*)$', r'> [!\1]\2', text, flags=re.MULTILINE)

        lines = text.splitlines()
        out_lines = []
        in_callout = False
        
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()
            
            # Détection du début d'un callout
            m_start = re.match(r'^>\s*\[!([a-zA-Z]+)\]\s*(.*)$', stripped)
            if m_start:
                in_callout = True
                c_type = m_start.group(1).upper()
                c_title = m_start.group(2).strip()
                out_lines.append(f"> [!{c_type}] {c_title}" if c_title else f"> [!{c_type}]")
                i += 1
                continue

            if in_callout:
                # Fin du callout sur titre markdown ou séparateur horizontal
                if re.match(r'^#{1,6}\s+', stripped) or re.match(r'^---+$', stripped):
                    in_callout = False
                    out_lines.append(line)
                    i += 1
                    continue

                # Si un NOUVEAU callout commence
                if re.match(r'^>\s*\[!([a-zA-Z]+)\]', stripped) or re.match(r'^\[!([a-zA-Z]+)\]', stripped):
                    m_new = re.match(r'^>?\s*\[!([a-zA-Z]+)\]\s*(.*)$', stripped)
                    c_type = m_new.group(1).upper()
                    c_title = m_new.group(2).strip()
                    out_lines.append(f"> [!{c_type}] {c_title}" if c_title else f"> [!{c_type}]")
                    i += 1
                    continue

                # Si la ligne commence par '>'
                if stripped.startswith('>'):
                    cleaned_line = re.sub(r'^\s*>\s*', '', line).strip()
                    while cleaned_line.startswith('>'):
                        cleaned_line = re.sub(r'^>\s*', '', cleaned_line).strip()
                    if cleaned_line:
                        out_lines.append(f"> {cleaned_line}")
                    else:
                        out_lines.append(">")
                    i += 1
                    continue

                # Si la ligne est vide
                if stripped == '':
                    has_subsequent_quote = False
                    for j in range(i + 1, min(i + 20, n)):
                        next_str = lines[j].strip()
                        if not next_str:
                            continue
                        if re.match(r'^#{1,6}\s+', next_str) or re.match(r'^---+$', next_str):
                            has_subsequent_quote = False
                            break
                        if re.match(r'^>?\s*\[!([a-zA-Z]+)\]', next_str):
                            has_subsequent_quote = False
                            break
                        if next_str.startswith('>'):
                            has_subsequent_quote = True
                            break
                        else:
                            break

                    if has_subsequent_quote:
                        out_lines.append(">")
                    else:
                        in_callout = False
                        out_lines.append("")
                    i += 1
                    continue

                # Si la ligne de texte n'a pas de '>', est-elle orpheline dans le callout ?
                has_subsequent_quote = False
                for j in range(i + 1, min(i + 10, n)):
                    next_str = lines[j].strip()
                    if not next_str:
                        continue
                    if re.match(r'^#{1,6}\s+', next_str) or re.match(r'^---+$', next_str):
                        break
                    if re.match(r'^>?\s*\[!([a-zA-Z]+)\]', next_str):
                        break
                    if next_str.startswith('>'):
                        has_subsequent_quote = True
                        break
                    else:
                        break

                if has_subsequent_quote:
                    out_lines.append(f"> {stripped}")
                    i += 1
                    continue
                else:
                    in_callout = False
                    out_lines.append(line)
                    i += 1
                    continue
            else:
                out_lines.append(line)
                i += 1

        result = '\n'.join(out_lines)
        result = re.sub(r'(?:\n>){3,}', '\n>\n>', result)
        return result



class SectionBlock:
    """Représentation d'une section Markdown pour le moteur AST diff."""
    def __init__(self, heading: str, level: int, title: str, lines: List[str]):
        self.heading = heading  # Ligne de titre brute, ex: "### General Info" ou ""
        self.level = level      # 1, 2, 3, etc. (0 pour le préambule)
        self.title = title      # Titre nettoyé, ex: "General Info"
        self.lines = lines      # Lignes de contenu sous le titre

    @property
    def normalized_title(self) -> str:
        """Normalise le titre de section pour l'alignement (ignore numérotation, émojis et casse)."""
        cleaned = re.sub(r'^[0-9\.\s\-\:\#]+', '', self.title.lower())
        cleaned = re.sub(r'[^\w\s]', '', cleaned)
        return ' '.join(cleaned.split())


def find_image_source(
    img_name: str,
    vault_dir: Optional[Path] = None,
    repo_dir: Optional[Path] = None,
    input_path: Optional[Path] = None,
    slug: str = ""
) -> Optional[Path]:
    """Recherche exhaustive de la source d'une image dans le dépôt et le coffre."""
    clean_name = img_name.strip().strip('"{}\'')
    base_name = Path(clean_name).name
    stem = Path(clean_name).stem

    search_dirs = [
        vault_dir / "papers" / "_attachments" / slug if vault_dir and slug else None,
        vault_dir / "papers" / "_attachments" if vault_dir else None,
        vault_dir / "_attachments" / slug if vault_dir and slug else None,
        vault_dir / "_attachments" if vault_dir else None,
        repo_dir / "assets" / "final" if repo_dir else None,
        repo_dir / "assets" if repo_dir else None,
        repo_dir / "figures" if repo_dir else None,
        repo_dir / "figures" / "cards" if repo_dir else None,
        repo_dir / "figures" / "modern" if repo_dir else None,
        repo_dir / "figures" / "isna_assets" if repo_dir else None,
        repo_dir if repo_dir else None,
        input_path.parent / "assets" / "final" if input_path else None,
        input_path.parent / "assets" if input_path else None,
        input_path.parent / "figures" if input_path else None,
        input_path.parent / "figures" / "cards" if input_path else None,
        input_path.parent / "figures" / "modern" if input_path else None,
        input_path.parent / "figures" / "isna_assets" if input_path else None,
        input_path.parent if input_path else None,
        input_path.parent.parent / "assets" / "final" if input_path and input_path.parent else None,
        input_path.parent.parent / "assets" if input_path and input_path.parent else None,
        input_path.parent.parent / "figures" if input_path and input_path.parent else None,
    ]
    valid_dirs = [d for d in search_dirs if d and d.exists() and d.is_dir()]

    # 1. Correspondance exacte
    for sd in valid_dirs:
        cand = sd / base_name
        if cand.exists() and cand.is_file():
            return cand

    # 2. Si l'extension est .pdf ou raster équivalent
    for sd in valid_dirs:
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
            cand = sd / f"{stem}{ext}"
            if cand.exists() and cand.is_file():
                return cand

    # 3. Si le fichier .pdf existe, convertir en .png via pymupdf
    for sd in valid_dirs:
        cand_pdf = sd / f"{stem}.pdf"
        if cand_pdf.exists() and cand_pdf.is_file():
            try:
                import pymupdf
                doc = pymupdf.open(str(cand_pdf))
                if len(doc) > 0:
                    page = doc[0]
                    pix = page.get_pixmap(dpi=300)
                    raster_png = cand_pdf.with_suffix(".png")
                    pix.save(str(raster_png))
                    if raster_png.exists():
                        return raster_png
            except Exception:
                pass

    # 4. Correspondance insensible à la casse et avec espaces <-> underscores
    normalized_targets = {
        base_name.lower(),
        base_name.lower().replace(" ", "_"),
        base_name.lower().replace("_", " "),
        stem.lower(),
        stem.lower().replace(" ", "_"),
        stem.lower().replace("_", " ")
    }
    for sd in valid_dirs:
        try:
            for f in sd.iterdir():
                if f.is_file():
                    f_name_lower = f.name.lower()
                    f_stem_lower = f.stem.lower()
                    if f_name_lower in normalized_targets or f_stem_lower in normalized_targets:
                        return f
                    if f.stem.lower().replace(" ", "_") == stem.lower().replace(" ", "_"):
                        return f
        except Exception:
            pass

    return None


def clean_obsidian_manuscript(text: str) -> str:
    """
    Nettoie intégralement le texte pour la note du coffre Obsidian :
    1. Supprime tout badge de score IA (<span ...>🛡️ Score IA : ...</span>)
    2. Remplace <ins...>texte</ins> par texte pur (contenu final 'after')
    3. Supprime intégralement tout <del...>texte</del> (suppressions purgées)
    4. Supprime tout span de mise en valeur de diff (background-color, etc.)
    5. Supprime toute section 'Arborescence des Modifications Détectées'
    """
    # 1. Supprimer le bloc de synthèse des diffs si présent
    text = re.sub(r'## 🔄 Synthèse des Changements & Diffs Récents.*?(?=(?:\n---+\s*\n|\n#[^#]|\Z))', '', text, flags=re.DOTALL)
    text = re.sub(r'\n---+\s*\n(?=#)', '\n\n', text)

    # 1bis. Supprimer toute balise <style> résiduelle
    text = re.sub(r'<style\b[^>]*>.*?</style>\s*', '', text, flags=re.DOTALL)

    # 2. Supprimer TOUS les badges Score IA (sur une seule ligne, jamais multi-lignes)
    text = re.sub(r'>?\s*<span\b[^>]*>[^<\n]*?Score IA[^<\n]*?</span>[ \t]*\n?', '', text)

    # 3. Remplacer <ins...>...</ins> par son contenu intérieur
    while re.search(r'<ins\b[^>]*>(.*?)</ins>', text, flags=re.DOTALL):
        text = re.sub(r'<ins\b[^>]*>(.*?)</ins>', r'\1', text, flags=re.DOTALL)

    # 4. Supprimer <del...>...</del>
    while re.search(r'<del\b[^>]*>.*?</del>', text, flags=re.DOTALL):
        text = re.sub(r'<del\b[^>]*>.*?</del>', '', text, flags=re.DOTALL)

    # 5. Supprimer les spans de surlignage de couleur résiduels
    while re.search(r'<span\b[^>]*style="[^"]*(?:background-color|text-decoration|#dcfce7|#fee2e2|#dbeafe|#ffedd5)[^"]*"[^>]*>(.*?)</span>', text, flags=re.DOTALL):
        text = re.sub(r'<span\b[^>]*style="[^"]*(?:background-color|text-decoration|#dcfce7|#fee2e2|#dbeafe|#ffedd5)[^"]*"[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)

    text = re.sub(r'<span style="background-color:[^"]*">(.*?)</span>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<span style="[^"]*text-decoration:[^"]*">(.*?)</span>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'</?(?:ins|del)\b[^>]*>', '', text)

    text = re.sub(r'\n{3,}', '\n\n', text).strip() + "\n"
    return text


def format_images_for_obsidian(
    markdown_text: str,
    vault_dir: Optional[Path],
    slug: str,
    repo_dir: Optional[Path] = None,
    input_path: Optional[Path] = None
) -> str:
    """
    Formate toutes les images pour la note du coffre Obsidian :
    1. Chaque image devient strictement un wikilink natif Obsidian ![[safe_name]].
    2. Chaque image est isolée sur sa propre ligne avec un double saut de ligne \n\n.
    3. Les fichiers sources sont copiés physiquement dans papers/_attachments/<slug>/ et papers/_attachments/.
    """
    img_exts = r'\.(?:png|jpg|jpeg|webp|svg|gif|bmp|pdf)'

    def ensure_vault_copy(img_name: str) -> str:
        clean = Path(img_name.strip().strip('"{}\'')).name
        safe = clean.replace(" ", "_")
        if not re.search(img_exts, safe, re.IGNORECASE):
            return clean
        src_file = find_image_source(img_name, vault_dir=vault_dir, repo_dir=repo_dir, input_path=input_path, slug=slug)
        if src_file and src_file.exists() and vault_dir:
            dest_dirs = [
                vault_dir / "papers" / "_attachments" / slug,
                vault_dir / "papers" / "_attachments",
                vault_dir / "_attachments" / slug,
                vault_dir / "_attachments"
            ]
            for d in dest_dirs:
                try:
                    d.mkdir(parents=True, exist_ok=True)
                    target = d / safe
                    if not target.exists() or target.stat().st_size != src_file.stat().st_size:
                        shutil.copy2(str(src_file), str(target))
                    if safe != clean:
                        shutil.copy2(str(src_file), str(d / clean))
                except Exception:
                    pass
        return safe

    # Remplacer les images standard Markdown ![alt](src) par ![[safe_name]]
    def replace_md_to_wikilink(m):
        src = m.group(2).strip()
        if not re.search(img_exts, src, re.IGNORECASE):
            return m.group(0)
        clean_src = re.sub(r'^file:///?', '', src)
        clean_src = clean_src.split('?')[0].split('#')[0]
        img_name = Path(clean_src).name
        safe_name = ensure_vault_copy(img_name)
        return f"\n\n![[{safe_name}]]\n\n"

    # Normaliser les wikilinks existants ![[...]] pour s'assurer qu'ils sont sur leur propre ligne avec \n\n
    def normalize_wikilink(m):
        inner = m.group(1).strip()
        parts = inner.split('|')
        img_path = parts[0].strip()
        img_name = Path(img_path).name
        if not re.search(img_exts, img_name, re.IGNORECASE):
            return m.group(0)
        safe_name = ensure_vault_copy(img_name)
        return f"\n\n![[{safe_name}]]\n\n"

    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_to_wikilink, markdown_text)
    text = re.sub(r'!\[\[(.*?)\]\]', normalize_wikilink, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def format_images_for_brain(
    markdown_text: str,
    brain_target: Path,
    slug: str,
    vault_dir: Optional[Path] = None,
    repo_dir: Optional[Path] = None,
    input_path: Optional[Path] = None
) -> str:
    """
    Formate toutes les images pour l'artéfact de session Brain Antigravity :
    1. Les images sources sont copiées physiquement dans brain_target / safe_name.
    2. Dans le texte, chaque image pointe vers :
       ![caption](file:///C:/Users/hjamet/.gemini/antigravity/brain/<conversation-id>/<safe_name>)
    3. Chaque balise d'image est isolée sur sa propre ligne avec un double saut de ligne \n\n.
    """
    img_exts = r'\.(?:png|jpg|jpeg|webp|svg|gif|bmp|pdf)'
    brain_target.mkdir(parents=True, exist_ok=True)
    b_posix = brain_target.resolve().as_posix().lstrip('/')

    def copy_to_brain(img_name: str) -> str:
        clean = Path(img_name.strip().strip('"{}\'')).name
        safe = clean.replace(" ", "_")
        target_file = brain_target / safe
        target_orig = brain_target / clean

        src_file = find_image_source(img_name, vault_dir=vault_dir, repo_dir=repo_dir, input_path=input_path, slug=slug)
        if src_file and src_file.exists():
            try:
                if not target_file.exists() or target_file.stat().st_size != src_file.stat().st_size:
                    shutil.copy2(str(src_file), str(target_file))
                if safe != clean:
                    shutil.copy2(str(src_file), str(target_orig))
            except Exception:
                pass
        return safe

    def replace_wikilink_brain(m):
        inner = m.group(1).strip()
        parts = inner.split('|')
        img_path = parts[0].strip()
        alt = parts[1].strip() if len(parts) > 1 else Path(img_path).stem.replace('_', ' ')
        img_name = Path(img_path).name
        if not re.search(img_exts, img_name, re.IGNORECASE):
            return m.group(0)

        safe_name = copy_to_brain(img_name)
        alt_clean = " ".join(alt.split()) if alt else Path(safe_name).stem.replace('_', ' ')
        img_url = f"file:///{b_posix}/{safe_name}"
        return f"\n\n![{alt_clean}]({img_url})\n\n"

    def replace_md_brain(m):
        alt = m.group(1).strip()
        src = m.group(2).strip()
        if not re.search(img_exts, src, re.IGNORECASE):
            return m.group(0)

        clean_src = re.sub(r'^file:///?', '', src)
        clean_src = clean_src.split('?')[0].split('#')[0]
        img_name = Path(clean_src).name

        safe_name = copy_to_brain(img_name)
        alt_clean = " ".join(alt.split()) if alt else Path(safe_name).stem.replace('_', ' ')
        img_url = f"file:///{b_posix}/{safe_name}"
        return f"\n\n![{alt_clean}]({img_url})\n\n"

    text = re.sub(r'!\[\[(.*?)\]\]', replace_wikilink_brain, markdown_text, flags=re.DOTALL)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_md_brain, text, flags=re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


class ArtifactDiffManager:
    """Gestionnaire de Diffs chirurgicaux en Inline Word-Diff fluide et certification Anti-IA."""

    DIFF_SUMMARY_HEADER = "## 🔄 Synthèse des Changements & Diffs Récents"
    USER_COMMENTS_HEADER = "## 💬 Commentaires & Retours d'Arbitrage"

    # Style Auteur Local (Henri Jamet) : vert doux épuré sans gras ni soulignement
    DEL_STYLE_LOCAL = 'style="background-color:#fee2e2; color:#991b1b; text-decoration:line-through; padding:1px 3px; border-radius:3px;"'
    INS_STYLE_LOCAL = 'style="background-color:#dcfce7; color:#166534; font-weight:normal; text-decoration:none; -webkit-text-decoration:none; text-decoration-line:none; padding:1px 3px; border-radius:3px;"'

    # Style Collaborateurs (Stergios, James, Isna...) : bleu ciel pour ajouts, ambre pour suppressions
    DEL_STYLE_COLLAB = 'style="background-color:#ffedd5; color:#9a3412; text-decoration:line-through; padding:1px 3px; border-radius:3px;"'
    INS_STYLE_COLLAB = 'style="background-color:#dbeafe; color:#1e40af; font-weight:normal; text-decoration:none; -webkit-text-decoration:none; text-decoration-line:none; padding:1px 3px; border-radius:3px;"'

    DEL_STYLE = DEL_STYLE_LOCAL
    INS_STYLE = INS_STYLE_LOCAL

    LATENT_SPACE_DEFAULT_SYNTHESIS = """- **James (Arnéra)** :
  - **Section(s) impactée(s)** : Section 1 (*Introduction*), Section 4 (*The LLM Network Game*), Tableau 1 (*Pedagogical Mapping*), mécaniques de déplacement et économie des jetons de calcul.
  - **Intention didactique / méthodologique** : Introduction incisive sur l'analogie de la « boîte noire » en classe secondaire (*« a prompt goes in, text comes out, compute bills abstracted »*), formalisation didactique des règles physiques sur grille orthogonale $10 \\times 10$, boucle de manche en 5 étapes, contraintes d'infrastructure tangibles (upkeep de mémoire, coût de calcul par bond de vecteur) et clarification des paliers de cartes SLM/LLM.
  - **Mode de conciliation** : Intégration mot à mot de ses reformulations didactiques dans l'introduction et préservation intégrale des mécaniques de cartes et des règles de scoring, intégrées harmonieusement avec notre modélisation mathématique du compromis capacité/coût.
- **Stergios (Konstantinidis)** :
  - **Section(s) impactée(s)** : Résumé (*Abstract*), Introduction (Section 1), et Section 4.1 (*Game Overview and Setup / Victory Conditions*).
  - **Intention didactique / méthodologique** : Dédoublonnage et clarification de l'introduction (3 paragraphes concis au lieu de 5 redondants, chaque concept n'apparaît qu'une seule fois), simplification de la terminologie pour les enseignants du secondaire (*movement cards*, *printed board*, minuscules pour *language models*), et intégration des visuels réels des cartes et jetons dans le papier.
  - **Mode de conciliation** : Validation et adoption complète de la structure épurée et de la terminologie accessible de Stergios, tout en maintenant nos contributions théoriques et empiriques (simulation Monte Carlo 500k).
- **Henri Jamet & Antigravity** :
  - **Section(s) impactée(s)** : Section 3.4 (*Game Balance Verification via In-Silico Simulation*), Figure 3 composite 1x3, calibration Section 6, cadrage AAAI-26 et audit anti-IA.
  - **Intention didactique / méthodologique** : Calibration numérique à grande échelle ($N=500{,}000$ parties, $2{,}000{,}000$ manches d'équipes), modélisation des disparités d'accès au calcul (fracture d'infrastructure et courbes de Lorenz/Gini), calibration de la cible de victoire ($R=3$, 4U / 5VP, durée $3.6 \\pm 0.6$ rounds) et certification stricte du style académique (score IA $\\le 10\\%$, format 8 pages).
  - **Mode de conciliation** : Alignement de la modélisation numérique sur les règles physiques épurées par Stergios et James, garantissant une cohérence totale entre simulation in-silico et expérience de jeu sur table."""

    SECTION_ALIASES = {
        'the llm network game': 'the latent space',
        'game overview and setup': 'game overview and components',
        'economy scoring and victory objective': 'economy tolerance and scoring',
        'the 5step round loop': 'the 5phase gameplay loop',
        'expansion modules': 'modular architectural expansions',
        'game calibration via largescale monte carlo simulation': 'game balance verification via insilico simulation',
    }

    @classmethod
    def find_matching_section(
        cls,
        norm_title: str,
        sec_map: Dict[str, List[SectionBlock]],
        used_secs: Set[SectionBlock]
    ) -> Optional[SectionBlock]:
        """Recherche intelligente d'une section correspondante (exacte, alias sémantiques canoniques ou fuzzy)."""
        # 1. Correspondance exacte
        if norm_title in sec_map:
            for cand in sec_map[norm_title]:
                if cand not in used_secs:
                    return cand

        # 2. Correspondance par dictionnaire d'alias sémantiques (aller et retour)
        rev_aliases = {v: k for k, v in cls.SECTION_ALIASES.items()}
        alias = cls.SECTION_ALIASES.get(norm_title) or rev_aliases.get(norm_title)
        if alias and alias in sec_map:
            for cand in sec_map[alias]:
                if cand not in used_secs:
                    return cand

        # 3. Correspondance floue (SequenceMatcher ratio et recouvrement Jaccard de tokens)
        best_cand = None
        best_score = 0.0
        norm_tokens = set(norm_title.split())
        for title, cand_list in sec_map.items():
            cand_tokens = set(title.split())
            ratio = difflib.SequenceMatcher(None, norm_title, title).ratio()
            jaccard = len(norm_tokens & cand_tokens) / max(len(norm_tokens | cand_tokens), 1)
            comb = max(ratio, jaccard)
            if comb > 0.55 and comb > best_score:
                for cand in cand_list:
                    if cand not in used_secs:
                        best_cand = cand
                        best_score = comb
        return best_cand

    @classmethod
    def split_into_sections(cls, text: str) -> List[SectionBlock]:
        """Découpe un texte Markdown en une liste de sections AST."""
        lines = text.splitlines()
        sections: List[SectionBlock] = []
        curr_heading = ""
        curr_level = 0
        curr_title = "Préambule"
        curr_lines: List[str] = []

        for line in lines:
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                if curr_lines or curr_heading:
                    sections.append(SectionBlock(curr_heading, curr_level, curr_title, curr_lines))
                curr_heading = line
                curr_level = len(match.group(1))
                curr_title = match.group(2).strip()
                curr_lines = []
            else:
                curr_lines.append(line)

        if curr_lines or curr_heading:
            sections.append(SectionBlock(curr_heading, curr_level, curr_title, curr_lines))

        return sections

    @classmethod
    def extract_manuscript_body(cls, content: str) -> str:
        """
        Extrait le texte brut du manuscrit de la version précédente en :
        1. Ignorant les métadonnées de tête et la section de commentaires d'arbitrage
        2. Ignorant le bloc de synthèse de diffs en tête
        3. Supprimant tout contenu supprimé : balises <del>...</del> et anciens callouts [!CAUTION] / [!FAILURE]
        4. Conservant tout contenu ajouté : déballant <ins>...</ins> et anciens callouts [!TIP] / [!SUCCESS]
        """
        text = content
        text = re.sub(r'^---\n.*?\n---\n?', '', text, flags=re.DOTALL)
        text = re.sub(r'<!--.*?-->\n?', '', text)

        if cls.USER_COMMENTS_HEADER in text:
            text = text.split(cls.USER_COMMENTS_HEADER)[0]

        if cls.DIFF_SUMMARY_HEADER in text:
            parts = text.split(cls.DIFF_SUMMARY_HEADER, 1)
            after = parts[1]
            sep_match = re.search(r'\n---\s*\n', after)
            if sep_match:
                text = after[sep_match.end():]
            else:
                next_h2 = re.search(r'\n##\s+', after)
                if next_h2:
                    text = after[next_h2.start():]

        # Nettoyage des anciens callouts résiduels d'abstract en dur si présents
        text = re.sub(r'>\s*\[!NOTE\]\s*\n>\s*\*\*📄 Résumé / Abstract\*\*\s*:\s*\n?', '', text)

        # Nettoyage du callout de conciliation collaborative si présent (format multi-lignes robuste)
        text = re.sub(
            r'>\s*\[!NOTE\]\s*\n>\s*\*\*🔄\s*Synthèse des Travaux Récents & Conciliation Collaborative\*\*.*?(?=(?:\n(?!>))|\Z)',
            '',
            text,
            flags=re.DOTALL
        )

        # Nettoyage des bannières parasites : Certification Anti-IA et Baseline Git
        text = re.sub(
            r'>\s*\[!(?:TIP|CAUTION)\]\s*\n>\s*(?:🛡️|🚨)\s*\*\*.*?(?=(?:\n(?!>))|\Z)',
            '',
            text,
            flags=re.DOTALL
        )
        text = re.sub(
            r'>\s*\[!NOTE\]\s*\n>\s*\*\*Baseline Git validée à jour.*?(?=(?:\n(?!>))|\Z)',
            '',
            text,
            flags=re.DOTALL
        )
        # Nettoyage des badges IA éventuels (anciens et nouveaux formats)
        text = re.sub(r'<span\b[^>]*>(?:🛡️|🚨|⚠️)\s*(?:Score IA|P\(AI\))\s*:?.*?</span>\s*', '', text)

        # Nettoyage des callouts résiduels de sections supprimées
        text = re.sub(r'>\s*\[!CAUTION\]\s*🔴\s*Section Supprimée\s*:.*?(?=(?:\n(?!>))|\Z)', '', text, flags=re.DOTALL)

        # 1. Supprimer le texte balisé en suppression (<del>...</del> et span résiduel)
        text = re.sub(r'<del\b[^>]*>.*?</del>', '', text, flags=re.DOTALL)
        text = re.sub(r'<span\b[^>]*style="[^"]*#fee2e2[^"]*"[^>]*>.*?</span>', '', text, flags=re.DOTALL)

        # 2. Déballer le texte balisé en ajout (<ins>...</ins> et span résiduel)
        text = re.sub(r'<ins\b[^>]*>(.*?)</ins>', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'<span\b[^>]*style="[^"]*#dcfce7[^"]*"[^>]*>(.*?)</span>', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'</?span[^>]*>', '', text)

        lines = text.splitlines()
        clean_lines = []
        in_failure_callout = False
        in_success_callout = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('> [!CAUTION]') or stripped.startswith('> [!FAILURE]') or stripped.startswith('> [!FAIL]') or stripped.startswith('> [!DANGER]'):
                in_failure_callout = True
                in_success_callout = False
                continue
            elif stripped.startswith('> [!TIP]') or stripped.startswith('> [!SUCCESS]') or stripped.startswith('> [!CHECK]') or stripped.startswith('> [!DONE]'):
                if 'Certification Anti-IA' in stripped:
                    clean_lines.append(line)
                    continue
                in_success_callout = True
                in_failure_callout = False
                continue

            if in_failure_callout:
                if stripped.startswith('>'):
                    continue
                else:
                    in_failure_callout = False

            if in_success_callout:
                if stripped.startswith('>'):
                    clean_line = re.sub(r'^>\s?', '', line)
                    clean_lines.append(clean_line)
                    continue
                else:
                    in_success_callout = False

            clean_lines.append(line)

        # Nettoyage des espaces doubles consécutifs laissés par les suppressions inline
        result_lines = [re.sub(r'[ \t]{2,}', ' ', l) for l in clean_lines]
        body = "\n".join(result_lines).strip()
        return cls.clean_residual_latex(body)

    @classmethod
    def clean_residual_latex(cls, text: str) -> str:
        """
        Nettoie et normalise tout résidu de syntaxe ou balisage LaTeX (environnements, commandes de mise en page,
        balises de pure forme) afin que les comparaisons différentielles portent exclusivement sur le texte de fond.
        """
        if not text:
            return ""

        # Extraction et expansion dynamique de macros résiduelles éventuelles
        text_no_macros, residual_macros = LatexMacroEngine.extract_macros(text)
        if residual_macros:
            text = LatexMacroEngine.expand_macros(text_no_macros, residual_macros)
        else:
            text = text_no_macros

        # 1. Normalisation des environnements de citation résiduels en blockquotes Markdown
        env_quote_pattern = re.compile(r'\\begin\{(?:quote|quotation|verse)\}\s*(.*?)\s*\\end\{(?:quote|quotation|verse)\}', re.DOTALL)
        def repl_quote(match):
            inner = match.group(1).strip()
            lines = inner.splitlines()
            return "\n\n" + "\n".join([f"> {l}" if l.strip() else ">" for l in lines]) + "\n\n"

        text = env_quote_pattern.sub(repl_quote, text)

        # 2. Déballage des environnements de mise en page pure
        text = re.sub(r'\\begin\{center\}\s*(.*?)\s*\\end\{center\}', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{abstract\}\s*(.*?)\s*\\end\{abstract\}', r'\1', text, flags=re.DOTALL)

        # 3. Suppression absolue de TOUTES les balises d'environnement LaTeX résiduelles
        text = re.sub(r'\\(?:begin|end)\{[^}]+\}', '', text)

        # 4. Normalisation des items de liste LaTeX en Markdown
        text = re.sub(r'\\item(?:\s*\[[^\]]*\])?\s*', '- ', text)

        # 5. Formatage inline LaTeX -> Markdown
        for _ in range(3):
            text = re.sub(r'\\textbf\{((?:[^{}]|{[^{}]*})*)\}', r'**\1**', text)
            text = re.sub(r'\\textit\{((?:[^{}]|{[^{}]*})*)\}', r'*\1*', text)
            text = re.sub(r'\\emph\{((?:[^{}]|{[^{}]*})*)\}', r'*\1*', text)
            text = re.sub(r'\\texttt\{((?:[^{}]|{[^{}]*})*)\}', r'`\1`', text)
            text = re.sub(r'\\textsc\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\text\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)
            text = re.sub(r'\\underline\{((?:[^{}]|{[^{}]*})*)\}', r'\1', text)

        # 6. Suppression des commandes de pure forme et mise en page
        text = re.sub(r'\\label\{[^}]+\}', '', text)
        text = re.sub(r'\\(?:centering|noindent|frenchspacing|medskip|bigskip|smallskip|clearpage|newpage|vfill|hfill|small|footnotesize|scriptsize|large|Large|LARGE|huge|Huge|sffamily|ttfamily|rmfamily|bfseries|itshape)\b', '', text)
        text = re.sub(r'\\(?:vspace|hspace|setlength|addtolength)\*?\{[^}]*\}(?:\{[^}]*\})?', '', text)
        text = re.sub(r'\\(?:toprule|midrule|bottomrule|hline|addlinespace|cmidrule(?:\[[^\]]*\])?\{[^}]*\})', '', text)
        text = re.sub(r'\\(?:newcommand|renewcommand|providecommand)\*?\s*\{\\[a-zA-Z]+\}(?:\[\d+\])?\{.*?\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\nocite\*?(?:\{[^}]*\})?', '', text)
        text = re.sub(r'\\(?:bibliography|bibliographystyle)(?:\{[^}]*\}|[a-zA-Z0-9_-]+)?', '', text)
        text = re.sub(r'\\(?:draw|fill|node|path|coordinate)\[[^\]]*\].*?;', '', text)

        # 7. Nettoyage des commandes résiduelles isolées sans arguments
        text = re.sub(r'\\(?:textbf|textit|emph|texttt|textsc|centering|noindent)\b', '', text)

        # 8. Nettoyage de la ponctuation LaTeX et spacing
        text = re.sub(r'\\xspace\s*([,.:;!?\'"\)\}\]])', r'\1', text)
        text = re.sub(r'\\xspace\b\s*', ' ', text)
        text = text.replace('~', ' ')
        text = text.replace(r'\,', ' ')
        text = text.replace(r'\&', '&')
        text = text.replace(r'\_', '_')
        text = text.replace(r'\#', '#')
        text = text.replace(r'\%', '%')
        text = text.replace('``', '"').replace("''", '"')
        text = re.sub(r'(?<![:|\-])---(?![:|\-])', '—', text)
        text = re.sub(r'(?<![:|\-])--(?![:|\-])', '–', text)

        # 9. Nettoyage des backslashes en fin de ligne ou dans les tableaux
        text = re.sub(r'\\+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\\+\s*\|', '|', text)

        # 10. Nettoyage des lignes de séparation résiduelles isolées
        text = re.sub(r'^\s*---\s*$', '', text, flags=re.MULTILINE)

        # 11. Espaces multiples et sauts de ligne
        text = re.sub(r'[ \t]{2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @classmethod
    def wrap_inline_block(cls, text: str, tag: str, style: str, extra_attrs: str = "") -> str:
        """Enrobe le texte dans <tag style="..." extra_attrs>...</tag> en préservant les préfixes Markdown structurels (> , -, *, 1.)."""
        lines = text.splitlines(keepends=True)
        wrapped_lines = []
        full_attrs = f"{style} {extra_attrs}".strip() if extra_attrs else style
        for line in lines:
            line_ending = "\n" if line.endswith("\n") else ""
            content = line[:-1] if line_ending else line

            prefix = ""
            m_quote = re.match(r'^(>+\s*)', content)
            m_list = re.match(r'^(\s*[-*+]\s+|\s*\d+\.\s+)', content)
            if m_quote:
                prefix = m_quote.group(1)
                content = content[len(prefix):]
            elif m_list:
                prefix = m_list.group(1)
                content = content[len(prefix):]

            if content.strip():
                wrapped_lines.append(f"{prefix}<{tag} {full_attrs}><span {style}>{content}</span></{tag}>{line_ending}")
            else:
                wrapped_lines.append(f"{prefix}{content}{line_ending}")
        return "".join(wrapped_lines)

    @classmethod
    def format_del(cls, text: str, is_collab: bool = False, author: str = "", style: Optional[str] = None) -> str:
        """Enrobe le texte supprimé dans une balise <del> stylisée, en respectant les paragraphes."""
        if not text:
            return ""
        if '![' in text and '](' in text:
            return ""
        leading_ws = text[:len(text) - len(text.lstrip(' '))]
        trailing_ws = text[len(text.rstrip(' ')):]
        core = text.strip(' ')
        if not core:
            return text

        active_style = style or (cls.DEL_STYLE_COLLAB if is_collab else cls.DEL_STYLE_LOCAL)
        extra = f'title="Supprimé par {author}"' if (is_collab and author) else ""

        if '\n\n' in core:
            paras = core.split('\n\n')
            wrapped_paras = []
            for p in paras:
                if p.strip():
                    wrapped_paras.append(cls.wrap_inline_block(p, "del", active_style, extra))
                else:
                    wrapped_paras.append(p)
            return leading_ws + '\n\n'.join(wrapped_paras) + trailing_ws

        return leading_ws + cls.wrap_inline_block(core, "del", active_style, extra) + trailing_ws

    @classmethod
    def format_ins(cls, text: str, is_collab: bool = False, author: str = "", style: Optional[str] = None) -> str:
        """Enrobe le texte ajouté dans une balise <ins> stylisée, en respectant les paragraphes."""
        if not text:
            return ""
        if '![' in text and '](' in text:
            return text
        leading_ws = text[:len(text) - len(text.lstrip(' '))]
        trailing_ws = text[len(text.rstrip(' ')):]
        core = text.strip(' ')
        if not core:
            return text

        active_style = style or (cls.INS_STYLE_COLLAB if is_collab else cls.INS_STYLE_LOCAL)
        if 'text-decoration:none' not in active_style.replace(' ', ''):
            active_style = active_style.replace('style="', 'style="text-decoration:none; -webkit-text-decoration:none; text-decoration-line:none; ')
        extra = f'title="Ajouté par {author}"' if (is_collab and author) else ""

        if '\n\n' in core:
            paras = core.split('\n\n')
            wrapped_paras = []
            for p in paras:
                if p.strip():
                    wrapped_paras.append(cls.wrap_inline_block(p, "ins", active_style, extra))
                else:
                    wrapped_paras.append(p)
            return leading_ws + '\n\n'.join(wrapped_paras) + trailing_ws

        return leading_ws + cls.wrap_inline_block(core, "ins", active_style, extra) + trailing_ws

    @classmethod
    def format_callout(cls, callout_type: str, title: str, lines: List[str]) -> List[str]:
        """Formate proprement un bloc de lignes dans un callout GitHub Markdown."""
        clean_lines = [l for l in lines if l.strip() and not l.startswith('<!--')]
        if not clean_lines:
            return []
        
        result = [f"> [!{callout_type}] {title}"]
        for line in clean_lines:
            result.append(f"> {line}" if line.strip() else ">")
        result.append("")
        return result

    @classmethod
    def has_substantive_words(cls, text: str) -> bool:
        """
        Vérifie si le texte contient au moins un mot lisible de fond (alphanumérique),
        en éliminant toutes les balises LaTeX, Markdown, HTML, ponctuation et espaces.
        Garantit que le diff ne porte QUE sur le texte de fond et JAMAIS sur la forme.
        """
        if not text:
            return False
        # Supprimer les balises / environnements LaTeX résiduels
        t = re.sub(r'\\(?:begin|end)[ \t]*\{?[ \t]*(?:minipage|flushleft|flushright)[ \t]*\}?(?:\{[^}]*\}|\\[a-zA-Z]+)*', ' ', text)
        t = re.sub(r'\\(?:begin|end)minipage(?:\\[a-zA-Z]+|\{[^}]*\})*', ' ', t)
        t = re.sub(r'\\(?:begin|end)(?:flushleft|flushright)', ' ', t)
        t = re.sub(r'\\tcbline\*?', ' ', t)
        t = re.sub(r'\\(?:linewidth|textwidth|columnwidth)\b', ' ', t)
        t = re.sub(r'\\(?:begin|end)\{[^}]*\}', ' ', t)
        t = re.sub(r'\\[a-zA-Z]+(?:\*|\b)(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', t)
        t = re.sub(r'\\[a-zA-Z]+', ' ', t)
        # Supprimer balises HTML
        t = re.sub(r'<[^>]+>', ' ', t)
        # Supprimer balises Markdown et ponctuation / séparateurs
        t = re.sub(r'[\s>\*\_`#\-\+\|~=:;,\.!\?\(\)\[\]\{\}\\\/\'\"«»“”–—\^]+', ' ', t)
        return bool(re.search(r'\w', t))

    @classmethod
    def mask_figures_in_text(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extrait les blocs de figures (callouts [!NOTE] de figures/schémas et images autonomes)
        et les remplace par des marqueurs atomiques ___MD_FIGURE_BLOCK_{id}___.
        Garantit qu'aucune balise <ins> ou <del> n'est insérée autour des liens d'images Markdown ![](...)
        ou dans les en-têtes de callouts, ce qui briserait le rendu visuel dans Obsidian et CommonMark.
        """
        figure_map: Dict[str, str] = {}
        lines = text.splitlines(keepends=True)
        out_lines: List[str] = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            # 1. Détection des callouts de figures ou schémas
            is_fig_callout = False
            s = line.strip()
            if s.startswith('> [!NOTE]') and ('🖼️ Figure' in s or '📐 Schéma' in s):
                is_fig_callout = True
            elif s.startswith('> [!NOTE]') and i + 1 < n and ('📐 Schéma' in lines[i+1] or '🖼️ Figure' in lines[i+1]):
                is_fig_callout = True

            if is_fig_callout:
                fig_lines = [line]
                i += 1
                while i < n:
                    curr = lines[i]
                    curr_s = curr.strip()
                    if curr_s.startswith('> [!'):
                        break
                    if curr_s.startswith('>') or not curr_s:
                        fig_lines.append(curr)
                        if not curr_s and i + 1 < n and not lines[i+1].strip().startswith('>'):
                            i += 1
                            break
                        i += 1
                    else:
                        break

                token = f"___MD_FIGURE_BLOCK_{len(figure_map)}___"
                suffix = "\n" if fig_lines and fig_lines[-1].endswith("\n") else ""
                figure_map[token] = "".join(fig_lines)
                out_lines.append(token + suffix)
                continue

            # 2. Détection d'image Markdown autonome (![...](...) ou ![[...]])
            if re.match(r'^\s*!\[[^\]]*\]\([^\)]+\)\s*$', line) or re.match(r'^\s*!\[\[[^\]]+\]\]\s*$', line):
                token = f"___MD_FIGURE_BLOCK_{len(figure_map)}___"
                suffix = "\n" if line.endswith("\n") else ""
                figure_map[token] = line
                out_lines.append(token + suffix)
                i += 1
                continue

            out_lines.append(line)
            i += 1

        return "".join(out_lines), figure_map

    @classmethod
    def mask_tables_in_text(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Extrait les blocs de tableaux Markdown dans un texte (y compris dans les callouts)
        et les remplace par des marqueurs atomiques ___MD_TABLE_BLOCK_{id}___.
        """
        table_map: Dict[str, str] = {}
        lines = text.splitlines(keepends=True)
        out_lines: List[str] = []
        i = 0
        n = len(lines)

        def is_table_candidate(l: str) -> bool:
            s = l.strip()
            if s.startswith('>'):
                s = s.lstrip('>').strip()
            return s.startswith('|') and s.endswith('|') and '|' in s[1:]

        while i < n:
            if is_table_candidate(lines[i]):
                tbl_lines = []
                while i < n and is_table_candidate(lines[i]):
                    tbl_lines.append(lines[i])
                    i += 1

                has_sep = any(re.search(r'\|\s*:?-{2,}:?\s*\|', l) for l in tbl_lines)
                if has_sep and len(tbl_lines) >= 2:
                    token = f"___MD_TABLE_BLOCK_{len(table_map)}___"
                    suffix = "\n" if tbl_lines[-1].endswith("\n") else ""
                    table_map[token] = "".join(tbl_lines)
                    out_lines.append(token + suffix)
                else:
                    out_lines.extend(tbl_lines)
            else:
                out_lines.append(lines[i])
                i += 1

        return "".join(out_lines), table_map

    @classmethod
    def sanitize_table_pipes_in_diff(cls, lines: List[str]) -> List[str]:
        """
        Garantit qu'aucune balise <ins> ou <del> n'est insérée à l'intérieur
        des séparateurs de colonnes Markdown (| :--- | :--- |) ou ne coupe des colonnes.
        """
        cleaned_lines = []
        for l in lines:
            if re.search(r'\|\s*:?-{2,}:?\s*\|', l):
                clean_l = re.sub(r'</?(?:ins|del)[^>]*>', '', l)
                cleaned_lines.append(clean_l)
            elif l.strip().startswith('|') or (l.strip().startswith('>') and '|' in l):
                clean_l = re.sub(r'(<(?:ins|del)[^>]*>)([^<]*?)\|([^<]*?)(<\/(?:ins|del)>)', r'\1\2\4 | \1\3\4', l)
                cleaned_lines.append(clean_l)
            else:
                cleaned_lines.append(l)
        return cleaned_lines

    @classmethod
    def diff_section_lines(
        cls,
        old_lines: List[str],
        new_lines: List[str],
        is_collab: bool = False,
        author_name: str = "",
        head_lines: Optional[List[str]] = None
    ) -> Tuple[List[str], int, int, int, int]:
        """
        Compare chirurgicalement les lignes d'une section spécifique :
        - Diff Structuré pour les Tableaux Markdown : isolation des tableaux au niveau structurel,
          zéro balise <ins> ou <del> à l'intérieur des séparateurs (| :--- |) ou coupant les pipes.
          Si un tableau a changé, la nouvelle version propre du tableau est affichée intégralement.
        - Diff Inline Word-Diff chirurgical pour les paragraphes et textes hors tableaux.
        - Coloration différentielle : Local Henri (vert épuré/rouge) vs Collaborateurs (bleu/ambre).
        - Conciliation 3-voies si head_lines est fourni :
          * Ajout présent dans head_text : Collaborateur (bleu ciel #dbeafe)
          * Ajout absent de head_text : Henri Jamet local (vert #dcfce7)
          * Suppression présente dans head_text : Henri Jamet local (rouge #fee2e2)
          * Suppression absente de head_text : Collaborateur (ambre #ffedd5)
        Retourne : (clean_lines, local_add, local_del, collab_add, collab_del)
        """
        old_text = "\n".join(old_lines)
        new_text = "\n".join(new_lines)
        head_text = "\n".join(head_lines) if head_lines is not None else None

        # Vérification d'égalité stricte (sans les espaces de fin)
        if old_text.strip() == new_text.strip():
            return list(new_lines), 0, 0, 0, 0

        # Section sans mots substantifs des deux côtés
        if not cls.has_substantive_words(old_text) and not cls.has_substantive_words(new_text):
            return list(new_lines), 0, 0, 0, 0

        # Section entièrement nouvelle
        if not old_text.strip() or not cls.has_substantive_words(old_text):
            if not cls.has_substantive_words(new_text):
                return list(new_lines), 0, 0, 0, 0
            new_masked, new_tables = cls.mask_tables_in_text(new_text)
            new_masked, new_figures = cls.mask_figures_in_text(new_masked)
            blocks = re.split(r'(\n\s*\n+)', new_masked)
            out_blocks = []
            loc_add = 0
            col_add = 0
            for b in blocks:
                if not b.strip():
                    out_blocks.append(b)
                elif re.match(r'^\s*#{1,6}\s', b):
                    out_blocks.append(b)
                elif any(tok in b for tok in list(new_tables.keys()) + list(new_figures.keys())):
                    out_blocks.append(b)
                elif cls.has_substantive_words(b):
                    if head_text is not None:
                        if b.strip() in head_text:
                            col_add += 1
                            out_blocks.append(cls.format_ins(b, is_collab=True, author=author_name))
                        else:
                            loc_add += 1
                            out_blocks.append(cls.format_ins(b, is_collab=False, author="Henri Jamet"))
                    elif is_collab:
                        col_add += 1
                        out_blocks.append(cls.format_ins(b, is_collab=True, author=author_name))
                    else:
                        loc_add += 1
                        out_blocks.append(cls.format_ins(b, is_collab=False, author="Henri Jamet"))
                else:
                    out_blocks.append(b)
            res_text = "".join(out_blocks)
            for tok, tbl in new_tables.items():
                res_text = res_text.replace(tok, tbl)
            for tok, fig in new_figures.items():
                res_text = res_text.replace(tok, fig)
            return res_text.splitlines(), max(1, loc_add) if (loc_add > 0 or col_add == 0) else 0, 0, col_add, 0

        # Section entièrement vidée
        if not new_text.strip() or not cls.has_substantive_words(new_text):
            del_count = len([l for l in old_lines if cls.has_substantive_words(l)])
            if head_text is not None:
                if old_text.strip() in head_text:
                    return [cls.format_del(old_text, is_collab=False, author="Henri Jamet")], 0, del_count, 0, 0
                else:
                    return [cls.format_del(old_text, is_collab=True, author=author_name)], 0, 0, 0, del_count
            elif is_collab:
                return [cls.format_del(old_text, is_collab=True, author=author_name)], 0, 0, 0, del_count
            else:
                return [cls.format_del(old_text, is_collab=False, author="Henri Jamet")], 0, del_count, 0, 0

        # 1. Isolation structurelle des tableaux Markdown
        old_masked, old_tables = cls.mask_tables_in_text(old_text)
        new_masked, new_tables = cls.mask_tables_in_text(new_text)

        # 2. Isolation structurelle des figures et images Markdown
        old_masked, old_figures = cls.mask_figures_in_text(old_masked)
        new_masked, new_figures = cls.mask_figures_in_text(new_masked)

        # 3. Harmonisation des tokens pour les tableaux strictement identiques
        token_substitutions_old = {}
        token_substitutions_new = {}
        identical_table_content = {}
        modified_tables_new = {}
        modified_tables_old = {}

        used_old_tokens = set()
        identical_counter = 0
        diff_counter = 0

        for new_tok, new_str in new_tables.items():
            matched_old_tok = None
            for old_tok, old_str in old_tables.items():
                if old_tok not in used_old_tokens and old_str.strip() == new_str.strip():
                    matched_old_tok = old_tok
                    break
            if matched_old_tok is not None:
                used_old_tokens.add(matched_old_tok)
                ident_token = f"___MD_TABLE_IDENTICAL_{identical_counter}___"
                identical_counter += 1
                token_substitutions_old[matched_old_tok] = ident_token
                token_substitutions_new[new_tok] = ident_token
                identical_table_content[ident_token] = new_str
            else:
                mod_token = f"___MD_TABLE_NEW_{diff_counter}___"
                diff_counter += 1
                token_substitutions_new[new_tok] = mod_token
                modified_tables_new[mod_token] = new_str

        for old_tok, old_str in old_tables.items():
            if old_tok not in used_old_tokens:
                mod_token = f"___MD_TABLE_OLD_{diff_counter}___"
                diff_counter += 1
                token_substitutions_old[old_tok] = mod_token
                modified_tables_old[mod_token] = old_str

        for old_tok, rep in token_substitutions_old.items():
            old_masked = old_masked.replace(old_tok, rep)
        for new_tok, rep in token_substitutions_new.items():
            new_masked = new_masked.replace(new_tok, rep)

        # 4. Harmonisation des tokens pour les figures strictement identiques
        fig_substitutions_old = {}
        fig_substitutions_new = {}
        identical_figure_content = {}
        modified_figures_new = {}
        modified_figures_old = {}

        used_old_fig_tokens = set()
        ident_fig_counter = 0
        diff_fig_counter = 0

        for new_tok, new_str in new_figures.items():
            matched_old_tok = None
            for old_tok, old_str in old_figures.items():
                if old_tok not in used_old_fig_tokens and old_str.strip() == new_str.strip():
                    matched_old_tok = old_tok
                    break
            if matched_old_tok is not None:
                used_old_fig_tokens.add(matched_old_tok)
                ident_token = f"___MD_FIGURE_IDENTICAL_{ident_fig_counter}___"
                ident_fig_counter += 1
                fig_substitutions_old[matched_old_tok] = ident_token
                fig_substitutions_new[new_tok] = ident_token
                identical_figure_content[ident_token] = new_str
            else:
                mod_token = f"___MD_FIGURE_NEW_{diff_fig_counter}___"
                diff_fig_counter += 1
                fig_substitutions_new[new_tok] = mod_token
                modified_figures_new[mod_token] = new_str

        for old_tok, old_str in old_figures.items():
            if old_tok not in used_old_fig_tokens:
                mod_token = f"___MD_FIGURE_OLD_{diff_fig_counter}___"
                diff_fig_counter += 1
                fig_substitutions_old[old_tok] = mod_token
                modified_figures_old[mod_token] = old_str

        for old_tok, rep in fig_substitutions_old.items():
            old_masked = old_masked.replace(old_tok, rep)
        for new_tok, rep in fig_substitutions_new.items():
            new_masked = new_masked.replace(new_tok, rep)

        # Tokenisation fine préservant KaTeX, commentaires, tableaux et figures atomiques, ponctuation, mots et espaces
        token_pattern = re.compile(
            r'___MD_TABLE_[A-Z0-9_]+___|___MD_FIGURE_[A-Z0-9_]+___|\$\$.*?\$\$|(?<!\$)\$(?!\$)(?:\\.|[^\$\\\n])+(?<!\$)\$(?!\$)|<!--.*?-->|\s+|\w+|[^\w\s]',
            re.DOTALL | re.UNICODE
        )
        old_tokens = token_pattern.findall(old_masked)
        new_tokens = token_pattern.findall(new_masked)

        matcher = difflib.SequenceMatcher(None, old_tokens, new_tokens)
        result_parts: List[str] = []
        local_add = 0
        local_del = 0
        collab_add = 0
        collab_del = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                chunk = "".join(new_tokens[j1:j2])
                for t_tok, t_str in identical_table_content.items():
                    if t_tok in chunk:
                        chunk = chunk.replace(t_tok, t_str)
                for f_tok, f_str in identical_figure_content.items():
                    if f_tok in chunk:
                        chunk = chunk.replace(f_tok, f_str)
                result_parts.append(chunk)

            elif tag == 'delete':
                del_chunk = "".join(old_tokens[i1:i2])
                for t_tok, t_str in list(modified_tables_old.items()):
                    if t_tok in del_chunk:
                        del_chunk = del_chunk.replace(t_tok, "")
                        if head_text is not None:
                            if t_str.strip() in head_text:
                                local_del += 1
                            else:
                                collab_del += 1
                        elif is_collab:
                            collab_del += 1
                        else:
                            local_del += 1
                for f_tok, f_str in list(modified_figures_old.items()):
                    if f_tok in del_chunk:
                        del_chunk = del_chunk.replace(f_tok, "")
                        if head_text is not None:
                            if f_str.strip() in head_text:
                                local_del += 1
                            else:
                                collab_del += 1
                        elif is_collab:
                            collab_del += 1
                        else:
                            local_del += 1
                if cls.has_substantive_words(del_chunk):
                    if head_text is not None:
                        if del_chunk.strip() in head_text:
                            local_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))
                        else:
                            collab_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                    elif is_collab:
                        collab_del += 1
                        result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                    else:
                        local_del += 1
                        result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))

            elif tag == 'insert':
                add_chunk = "".join(new_tokens[j1:j2])
                has_tbl = False
                for t_tok, t_str in list(modified_tables_new.items()):
                    if t_tok in add_chunk:
                        add_chunk = add_chunk.replace(t_tok, t_str)
                        if head_text is not None:
                            if t_str.strip() in head_text:
                                collab_add += 1
                            else:
                                local_add += 1
                        elif is_collab:
                            collab_add += 1
                        else:
                            local_add += 1
                        has_tbl = True

                has_fig = False
                for f_tok, f_str in list(modified_figures_new.items()):
                    if f_tok in add_chunk:
                        add_chunk = add_chunk.replace(f_tok, f_str)
                        if head_text is not None:
                            if f_str.strip() in head_text:
                                collab_add += 1
                            else:
                                local_add += 1
                        elif is_collab:
                            collab_add += 1
                        else:
                            local_add += 1
                        has_fig = True

                if has_tbl or has_fig:
                    result_parts.append(add_chunk)
                elif cls.has_substantive_words(add_chunk):
                    if head_text is not None:
                        if add_chunk.strip() in head_text:
                            collab_add += 1
                            result_parts.append(cls.format_ins(add_chunk, is_collab=True, author=author_name))
                        else:
                            local_add += 1
                            result_parts.append(cls.format_ins(add_chunk, is_collab=False, author="Henri Jamet"))
                    elif is_collab:
                        collab_add += 1
                        result_parts.append(cls.format_ins(add_chunk, is_collab=True, author=author_name))
                    else:
                        local_add += 1
                        result_parts.append(cls.format_ins(add_chunk, is_collab=False, author="Henri Jamet"))
                else:
                    result_parts.append(add_chunk)

            elif tag == 'replace':
                del_chunk = "".join(old_tokens[i1:i2])
                add_chunk = "".join(new_tokens[j1:j2])

                has_tbl_old = False
                for t_tok, t_str in list(modified_tables_old.items()):
                    if t_tok in del_chunk:
                        del_chunk = del_chunk.replace(t_tok, "")
                        if head_text is not None:
                            if t_str.strip() in head_text:
                                local_del += 1
                            else:
                                collab_del += 1
                        elif is_collab:
                            collab_del += 1
                        else:
                            local_del += 1
                        has_tbl_old = True

                has_tbl_new = False
                for t_tok, t_str in list(modified_tables_new.items()):
                    if t_tok in add_chunk:
                        add_chunk = add_chunk.replace(t_tok, t_str)
                        if head_text is not None:
                            if t_str.strip() in head_text:
                                collab_add += 1
                            else:
                                local_add += 1
                        elif is_collab:
                            collab_add += 1
                        else:
                            local_add += 1
                        has_tbl_new = True

                has_fig_old = False
                for f_tok, f_str in list(modified_figures_old.items()):
                    if f_tok in del_chunk:
                        del_chunk = del_chunk.replace(f_tok, "")
                        if head_text is not None:
                            if f_str.strip() in head_text:
                                local_del += 1
                            else:
                                collab_del += 1
                        elif is_collab:
                            collab_del += 1
                        else:
                            local_del += 1
                        has_fig_old = True

                has_fig_new = False
                for f_tok, f_str in list(modified_figures_new.items()):
                    if f_tok in add_chunk:
                        add_chunk = add_chunk.replace(f_tok, f_str)
                        if head_text is not None:
                            if f_str.strip() in head_text:
                                collab_add += 1
                            else:
                                local_add += 1
                        elif is_collab:
                            collab_add += 1
                        else:
                            local_add += 1
                        has_fig_new = True

                if has_tbl_old or has_tbl_new or has_fig_old or has_fig_new:
                    if cls.has_substantive_words(del_chunk):
                        if head_text is not None:
                            if del_chunk.strip() in head_text:
                                local_del += 1
                                result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))
                            else:
                                collab_del += 1
                                result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                        elif is_collab:
                            collab_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                        else:
                            local_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))
                    result_parts.append(add_chunk)
                else:
                    del_has_words = cls.has_substantive_words(del_chunk)
                    add_has_words = cls.has_substantive_words(add_chunk)

                    if del_has_words:
                        if head_text is not None:
                            if del_chunk.strip() in head_text:
                                local_del += 1
                                result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))
                            else:
                                collab_del += 1
                                result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                        elif is_collab:
                            collab_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=True, author=author_name))
                        else:
                            local_del += 1
                            result_parts.append(cls.format_del(del_chunk, is_collab=False, author="Henri Jamet"))

                    if add_has_words:
                        if head_text is not None:
                            if add_chunk.strip() in head_text:
                                collab_add += 1
                                result_parts.append(cls.format_ins(add_chunk, is_collab=True, author=author_name))
                            else:
                                local_add += 1
                                result_parts.append(cls.format_ins(add_chunk, is_collab=False, author="Henri Jamet"))
                        elif is_collab:
                            collab_add += 1
                            result_parts.append(cls.format_ins(add_chunk, is_collab=True, author=author_name))
                        else:
                            local_add += 1
                            result_parts.append(cls.format_ins(add_chunk, is_collab=False, author="Henri Jamet"))
                    else:
                        result_parts.append(add_chunk)

        diff_text = "".join(result_parts)
        for ident_tok, ident_str in identical_figure_content.items():
            diff_text = diff_text.replace(ident_tok, ident_str)
        for mod_tok, mod_str in modified_figures_new.items():
            diff_text = diff_text.replace(mod_tok, mod_str)
        raw_lines = diff_text.splitlines()
        clean_lines = cls.sanitize_table_pipes_in_diff(raw_lines)
        return clean_lines, local_add, local_del, collab_add, collab_del

    @classmethod
    def generate_diff_annotated_body(
        cls,
        old_text: str,
        new_text: str,
        is_collab: bool = False,
        author_name: str = "",
        head_text: Optional[str] = None
    ) -> Tuple[str, str, int, List[str]]:
        """
        Moteur AST Diff par section avec différenciation d'auteur :
        - Vert doux (#dcfce7) / Rouge doux (#fee2e2) : Modifications locales d'Henri Jamet (non commitées)
        - Bleu ciel (#dbeafe) / Ambre doux (#ffedd5) : Modifications des collaborateurs (Stergios, James, Isna...)
        1. Découpe en sections AST (#, ##, ###)
        2. Aligne les sections par titre normalisé
        3. Applique diff_section_lines sur chaque section
        4. Génère le corps annoté et la Tree TOC bicolore
        """
        old_sections = cls.split_into_sections(old_text)
        new_sections = cls.split_into_sections(new_text)

        head_sec_map: Dict[str, List[SectionBlock]] = {}
        if head_text and head_text.strip() != new_text.strip() and head_text.strip() != old_text.strip():
            head_sections = cls.split_into_sections(head_text)
            for sec in head_sections:
                norm = sec.normalized_title
                if norm not in head_sec_map:
                    head_sec_map[norm] = []
                head_sec_map[norm].append(sec)

        # Indexer les anciennes sections par titre normalisé
        old_sec_map: Dict[str, List[SectionBlock]] = {}
        for sec in old_sections:
            norm = sec.normalized_title
            if norm not in old_sec_map:
                old_sec_map[norm] = []
            old_sec_map[norm].append(sec)

        used_old_secs: Set[SectionBlock] = set()
        used_head_secs: Set[SectionBlock] = set()
        total_diff_count = 0
        section_stats: Dict[str, Dict[str, int]] = {}
        annotated_document_lines: List[str] = []

        for new_sec in new_sections:
            norm = new_sec.normalized_title
            matching_head = cls.find_matching_section(norm, head_sec_map, used_head_secs)
            if matching_head:
                used_head_secs.add(matching_head)

            matching_old = cls.find_matching_section(norm, old_sec_map, used_old_secs)
            if matching_old:
                used_old_secs.add(matching_old)

            # Section display name
            sec_display_name = new_sec.title if new_sec.title != "Préambule" else "Introduction & Préambule"

            # Ajouter l'en-tête de section s'il existe
            if new_sec.heading:
                annotated_document_lines.append(new_sec.heading)
                annotated_document_lines.append("")

            b_lines = matching_old.lines if matching_old is not None else []
            h_lines = matching_head.lines if matching_head is not None else None
            c_lines = new_sec.lines

            sec_lines, l_add, l_del, c_add, c_del = cls.diff_section_lines(
                b_lines, c_lines,
                is_collab=is_collab,
                author_name=author_name,
                head_lines=h_lines
            )
            annotated_document_lines.extend(sec_lines)
            annotated_document_lines.append("")

            diff_cnt = l_add + l_del + c_add + c_del
            if diff_cnt > 0:
                total_diff_count += diff_cnt
                section_stats[sec_display_name] = {
                    "local_add": l_add,
                    "local_del": l_del,
                    "collab_add": c_add,
                    "collab_del": c_del
                }

        # Traiter les sections supprimées (présentes dans old mais absentes dans new)
        for old_sec in old_sections:
            if old_sec not in used_old_secs and old_sec.title != "Préambule":
                if not cls.has_substantive_words("\n".join(old_sec.lines)):
                    continue
                del_count = len([l for l in old_sec.lines if cls.has_substantive_words(l)])
                if del_count > 0:
                    total_diff_count += del_count

        # Génération de la Tree TOC
        tree_lines = []
        if total_diff_count > 0 and section_stats:
            sec_items = list(section_stats.items())
            for idx, (sec_name, stats) in enumerate(sec_items):
                is_last = (idx == len(sec_items) - 1)
                branch = "└──" if is_last else "├──"
                anchor = re.sub(r'[^a-zA-Z0-9\s\-]+', '', sec_name).strip().lower().replace(' ', '-')

                l_add = stats.get("local_add", 0)
                l_del = stats.get("local_del", 0)
                c_add = stats.get("collab_add", 0)
                c_del = stats.get("collab_del", 0)

                stat_parts = []
                if l_add > 0:
                    stat_parts.append(f"🟢 +{l_add}")
                if l_del > 0:
                    stat_parts.append(f"🔴 -{l_del}")
                if c_add > 0:
                    stat_parts.append(f"🔵 +{c_add}")
                if c_del > 0:
                    stat_parts.append(f"🟠 -{c_del}")

                stat_str = " / ".join(stat_parts) if stat_parts else "0 delta"
                badge = ""
                if (c_add > 0 or c_del > 0) and author_name:
                    badge = f" *[{author_name}]*"
                tree_lines.append(f"> {branch} 📍 **[{sec_name}](#{anchor})** *({stat_str})*{badge}<br>")
        else:
            # Mode Évaluation / Sommaire AST exhaustif de l'état actuel
            valid_secs = [s for s in new_sections if s.title != "Préambule" and (s.heading or cls.has_substantive_words("\n".join(s.lines)))]
            for idx, sec in enumerate(valid_secs):
                is_last = (idx == len(valid_secs) - 1)
                branch = "└──" if is_last else "├──"
                sec_name = sec.title if sec.title != "Préambule" else "Introduction & Préambule"
                anchor = re.sub(r'[^a-zA-Z0-9\s\-]+', '', sec_name).strip().lower().replace(' ', '-')
                tree_lines.append(f"> {branch} 📍 **[{sec_name}](#{anchor})**<br>")

        tree_toc = "\n".join(tree_lines)
        annotated_body = "\n".join(annotated_document_lines)

        # Nettoyer les sauts de lignes consécutifs
        annotated_body = re.sub(r'\n{3,}', '\n\n', annotated_body).strip()

        return annotated_body, tree_toc, total_diff_count, list(section_stats.keys())

    @classmethod
    def validate_revisions_up_to_line(cls, text: str, commit_line: int) -> Tuple[str, int, int]:
        """
        Valide chirurgicalement les révisions antérieures à la ligne commit_line (1-indexed) :
        - Lignes < commit_line :
          * Accepte les ajouts (<ins style="...">texte</ins> ➔ texte)
          * Élimine les suppressions (<del style="...">texte</del> ➔ "")
          * Purge les callouts de sections supprimées (> [!CAUTION] 🔴 Section Supprimée...)
        - Lignes >= commit_line :
          * Préserve strictement les balises <ins> et <del> pour examen ultérieur.
        Retourne (texte_mis_a_jour, nb_deltas_valides, nb_deltas_restants).
        """
        lines = text.splitlines()
        validated_lines: List[str] = []
        in_deleted_callout = False
        val_count = 0
        rem_count = 0

        for idx, line in enumerate(lines):
            line_num = idx + 1
            if line_num < commit_line:
                s = line.strip()
                if s.startswith("> [!CAUTION]") and "🔴 Section Supprimée" in s:
                    in_deleted_callout = True
                    val_count += 1
                    continue
                if in_deleted_callout:
                    if s.startswith(">") or not s:
                        continue
                    else:
                        in_deleted_callout = False

                ins_matches = re.findall(r'<ins\b[^>]*>(.*?)</ins>', line, flags=re.DOTALL)
                del_matches = re.findall(r'<del\b[^>]*>(.*?)</del>', line, flags=re.DOTALL)
                val_count += (len(ins_matches) + len(del_matches))

                clean_line = re.sub(r'<del\b[^>]*>.*?</del>', '', line)
                clean_line = re.sub(r'<span\b[^>]*style="[^"]*#fee2e2[^"]*"[^>]*>.*?</span>', '', clean_line)
                clean_line = re.sub(r'<ins\b[^>]*>(.*?)</ins>', r'\1', clean_line)
                clean_line = re.sub(r'<span\b[^>]*style="[^"]*#dcfce7[^"]*"[^>]*>(.*?)</span>', r'\1', clean_line)
                clean_line = re.sub(r'</?span[^>]*>', '', clean_line)
                clean_line = re.sub(r'[ \t]{2,}', ' ', clean_line)
                validated_lines.append(clean_line)
            else:
                in_deleted_callout = False
                ins_matches = re.findall(r'<ins\b[^>]*>(.*?)</ins>', line, flags=re.DOTALL)
                del_matches = re.findall(r'<del\b[^>]*>(.*?)</del>', line, flags=re.DOTALL)
                rem_count += (len(ins_matches) + len(del_matches))
                validated_lines.append(line)

        updated_text = "\n".join(validated_lines)

        if rem_count == 0:
            if cls.DIFF_SUMMARY_HEADER in updated_text:
                parts = updated_text.split(cls.DIFF_SUMMARY_HEADER, 1)
                after = parts[1]
                sep_match = re.search(r'\n---\s*\n', after)
                if sep_match:
                    updated_text = parts[0] + after[sep_match.end():]
                else:
                    next_h = re.search(r'\n#{1,3}\s+', after)
                    if next_h:
                        updated_text = parts[0] + after[next_h.start():]

        return updated_text, val_count, rem_count

    @classmethod
    def extract_paragraph_diff_texts(cls, para: str) -> Tuple[str, str]:
        """
        Extrait text_before (texte d'origine épuré des ajouts) et text_after (texte révisé épuré des suppressions)
        d'un paragraphe ou bloc Markdown contenant des balises de diff inline.
        """
        # 0. Supprimer le badge de score IA s'il est déjà présent
        cleaned = re.sub(
            r'(?:^>*\s*)?<span\b[^>]*>(?:🛡️|🚨|⚠️)\s*(?:Score IA|P\(AI\))\s*:?.*?</span>\s*',
            '',
            para,
            flags=re.MULTILINE
        )

        # tb : Texte avant modification (baseline Git d'origine)
        # On supprime tous les ajouts (<ins>...</ins> ou spans verts #dcfce7)
        tb = cleaned
        tb = re.sub(r'<ins\b[^>]*>.*?</ins>', '', tb, flags=re.DOTALL)
        tb = re.sub(r'<span\b[^>]*style="[^"]*#dcfce7[^"]*"[^>]*>.*?</span>', '', tb, flags=re.DOTALL)
        tb = re.sub(r'<span\b[^>]*#dcfce7[^>]*>.*?</span>', '', tb, flags=re.DOTALL)

        # On déballe les suppressions (qui faisaient partie du texte original)
        tb = re.sub(r'<del\b[^>]*>(.*?)</del>', r'\1', tb, flags=re.DOTALL)
        tb = re.sub(r'<span\b[^>]*style="[^"]*#fee2e2[^"]*"[^>]*>(.*?)</span>', r'\1', tb, flags=re.DOTALL)
        tb = re.sub(r'<span\b[^>]*#fee2e2[^>]*>(.*?)</span>', r'\1', tb, flags=re.DOTALL)
        tb = re.sub(r'</?(?:span|del|ins|br)\b[^>]*>', '', tb)
        tb = re.sub(r'(?m)^\s*(?:[-*+]|\d+\.)\s*$', '', tb)
        tb = re.sub(r'\n+', ' ', tb)
        tb = re.sub(r'[ \t]{2,}', ' ', tb).strip()

        # ta : Texte après modification (texte révisé courant)
        # On supprime toutes les suppressions (<del>...</del> ou spans rouges #fee2e2)
        ta = cleaned
        ta = re.sub(r'<del\b[^>]*>.*?</del>', '', ta, flags=re.DOTALL)
        ta = re.sub(r'<span\b[^>]*style="[^"]*#fee2e2[^"]*"[^>]*>.*?</span>', '', ta, flags=re.DOTALL)
        ta = re.sub(r'<span\b[^>]*#fee2e2[^>]*>.*?</span>', '', ta, flags=re.DOTALL)

        # On déballe les ajouts (qui font partie du texte révisé)
        ta = re.sub(r'<ins\b[^>]*>(.*?)</ins>', r'\1', ta, flags=re.DOTALL)
        ta = re.sub(r'<span\b[^>]*style="[^"]*#dcfce7[^"]*"[^>]*>(.*?)</span>', r'\1', ta, flags=re.DOTALL)
        ta = re.sub(r'<span\b[^>]*#dcfce7[^>]*>(.*?)</span>', r'\1', ta, flags=re.DOTALL)
        ta = re.sub(r'</?(?:span|del|ins|br)\b[^>]*>', '', ta)
        ta = re.sub(r'(?m)^\s*(?:[-*+]|\d+\.)\s*$', '', ta)
        ta = re.sub(r'(?m)^\s*[-*+]\s+(?=[A-Z])', '', ta)
        ta = re.sub(r'(?m)^\s*\d+\.\s+(?=[A-Z])', '', ta)
        ta = re.sub(r'\s+\b\d+\.\s*(?=[A-Z])', '', ta)
        ta = re.sub(r'\n+', ' ', ta)
        ta = re.sub(r'[ \t]{2,}', ' ', ta).strip()

        return tb, ta

    @classmethod
    def find_source_location(
        cls,
        text: str,
        file_cache: Any = None,
        repo_dir: Optional[Path] = None,
        source_file_path: Optional[Path] = None,
        included_files: Optional[List[Path]] = None
    ) -> Tuple[str, Optional[int]]:
        """
        Localise le fichier source .tex/.md et le numéro de ligne approximatif (1-indexed)
        pour un paragraphe modifié donné.
        """
        if not isinstance(file_cache, dict):
            actual_repo = file_cache if isinstance(file_cache, Path) else repo_dir
            actual_src = repo_dir if isinstance(repo_dir, Path) else source_file_path
            cache: Dict[Path, List[str]] = {}
            target_files: List[Path] = []
            if actual_src and actual_src.exists():
                target_files.append(actual_src)
            if included_files:
                for f in included_files:
                    if f.exists() and f not in target_files:
                        target_files.append(f)
            if actual_repo and actual_repo.exists() and not target_files:
                target_files.extend(list(actual_repo.glob("**/*.tex")))
            for tf in target_files:
                try:
                    cache[tf] = tf.read_text(encoding="utf-8", errors="replace").splitlines()
                except Exception:
                    pass
            file_cache = cache
            repo_dir = actual_repo

        if not file_cache or not text:
            return "Source LaTeX", None

        clean_target = re.sub(r'[*_#`~\[\]\(\)<>]', ' ', text)
        words = [w.lower() for w in re.findall(r'[a-zA-ZÀ-ÿ0-9_]{3,}', clean_target)]
        if not words:
            try:
                first_f = next(iter(file_cache.keys()))
                rel = first_f.relative_to(repo_dir).as_posix() if repo_dir else first_f.name
            except Exception:
                rel = first_f.name
            return rel, None

        shingles = []
        shingle_len = min(4, len(words))
        for i in range(len(words) - shingle_len + 1):
            shingles.append(" ".join(words[i:i + shingle_len]))

        best_file = None
        best_line = None
        best_score = 0

        for fpath, lines in file_cache.items():
            for l_idx, line in enumerate(lines, 1):
                line_clean = re.sub(r'%.*$', '', line).strip()
                if not line_clean:
                    continue
                line_clean = line_clean.lower()

                matched_shingles = sum(1 for sh in shingles if sh in line_clean)
                if matched_shingles > 0:
                    score = matched_shingles * 10
                    if score > best_score:
                        best_score = score
                        best_file = fpath
                        best_line = l_idx
                    continue

                line_words = set(re.findall(r'[a-zA-ZÀ-ÿ0-9_]{3,}', line_clean))
                matched_words = sum(1 for w in words[:15] if w in line_words)
                if matched_words >= 3:
                    score = matched_words
                    if score > best_score:
                        best_score = score
                        best_file = fpath
                        best_line = l_idx

        if best_file:
            try:
                rel_name = best_file.relative_to(repo_dir).as_posix() if repo_dir else best_file.name
            except Exception:
                rel_name = best_file.name
            return rel_name, best_line

        try:
            first_file = next(iter(file_cache.keys()))
            rel_name = first_file.relative_to(repo_dir).as_posix() if repo_dir else first_file.name
        except Exception:
            rel_name = first_file.name
        return rel_name, None

    @classmethod
    def attach_ai_score_badges(
        cls,
        annotated_body: str,
        enable_ai_score: bool = True,
        source_file_path: Optional[Path] = None,
        included_files: Optional[List[Path]] = None,
        repo_dir: Optional[Path] = None
    ) -> Tuple[str, int, List[Dict[str, Any]]]:
        """
        Analyse les paragraphes modifiés dans le corps annoté, évalue leur score IA avant/après
        via ai_detector en mode batch ultra-rapide (sans réinitialiser les modèles),
        insère un badge élégant sous chaque paragraphe modifié, et collecte les paragraphes
        défaillants (score_after > 10.0%) pour le rapport de conformité IA.
        """
        if not enable_ai_score or not annotated_body:
            return annotated_body, 0, []

        ai_mod = get_ai_detector_module()
        if ai_mod is None:
            print("ℹ️ [AIDetector] Module ai_detector non disponible, badges ignorés.")
            return annotated_body, 0, []

        source_files = []
        if source_file_path and source_file_path.exists():
            source_files.append(source_file_path)
        if included_files:
            for f in included_files:
                if f.exists() and f not in source_files:
                    source_files.append(f)
        if not source_files and source_file_path and source_file_path.parent.exists():
            p_dir = source_file_path.parent
            source_files.extend(list(p_dir.glob("*.tex")))
            source_files.extend(list(p_dir.glob("*.md")))
        if not source_files and repo_dir and repo_dir.exists():
            source_files.extend(list(repo_dir.glob("**/*.tex")))

        file_lines_cache: Dict[Path, List[str]] = {}
        for f in source_files:
            try:
                file_lines_cache[f] = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                pass

        blocks = re.split(r'(\n\s*\n+)', annotated_body)
        candidates = []
        in_bibliography = False
        current_section = "Introduction & Préambule"

        for idx in range(0, len(blocks), 2):
            block = blocks[idx]
            # Vérification de changement de section
            for line in block.splitlines():
                m_h = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
                if m_h:
                    current_section = m_h.group(2).strip()
                if re.search(r'^#{1,4}\s+.*(?:références|references|bibliograph)', line, re.IGNORECASE):
                    in_bibliography = True
                elif in_bibliography and re.match(r'^#{1,3}\s+', line):
                    in_bibliography = False

            if in_bibliography:
                continue

            # Ignorer les blocs techniques / titres / citations d'alerte / commentaires / code / tableaux / style / images
            if re.match(r'^\s*#{1,6}\s', block):
                continue
            if re.match(r'^\s*>\s*\[!', block):
                continue
            if block.strip().startswith('<!--') or block.strip().startswith('```') or block.strip().startswith('<style'):
                continue
            if re.match(r'^\s*[-*+]\s+\*\*\[', block):
                continue
            if block.strip().startswith('|') and '|' in block.strip()[1:]:
                continue
            if block.strip().startswith('![') and '](' in block:
                continue

            has_diff_tags = any(tag in annotated_body for tag in ('#fee2e2', '#dcfce7', '#dbeafe', '#ffedd5', '<del', '<ins'))
            if has_diff_tags:
                # Vérifier si le bloc contient des balises de diff
                if not any(tag in block for tag in ('#fee2e2', '#dcfce7', '#dbeafe', '#ffedd5', '<del', '<ins')):
                    continue

                tb, ta = cls.extract_paragraph_diff_texts(block)
                wb = len(re.findall(r'\b\w+\b', tb))
                wa = len(re.findall(r'\b\w+\b', ta))
                cb = len(tb.strip())
                ca = len(ta.strip())

                valid_b = (wb >= 6 and cb >= 40)
                valid_a = (wa >= 6 and ca >= 40)
            else:
                # Mode Évaluation de l'état actuel (sans balises de diff)
                clean_ta = re.sub(r'<[^>]+>', '', block).strip()
                clean_lines = [re.sub(r'^>\s?', '', l) for l in clean_ta.splitlines()]
                ta = " ".join(l.strip() for l in clean_lines if l.strip())
                tb = ""
                wa = len(re.findall(r'\b\w+\b', ta))
                ca = len(ta)
                valid_b = False
                valid_a = (wa >= 6 and ca >= 40)

            if not valid_b and not valid_a:
                continue

            candidates.append({
                'block_idx': idx,
                'raw_block': block,
                'text_before': tb,
                'text_after': ta,
                'valid_b': valid_b,
                'valid_a': valid_a,
                'section': current_section,
            })

        if not candidates:
            return annotated_body, 0, []

        texts_to_score = set()
        for c in candidates:
            if c['valid_b'] and c['text_before']:
                texts_to_score.add(c['text_before'])
            if c['valid_a'] and c['text_after']:
                texts_to_score.add(c['text_after'])

        print(f"🛡️ [AIDetector] Évaluation différentielle par lot de {len(candidates)} paragraphes modifiés ({len(texts_to_score)} textes)...")

        scores_cache: Dict[str, float] = {}
        try:
            if hasattr(ai_mod, "analyze_texts_batch"):
                texts_list = list(texts_to_score)
                batch_res = ai_mod.analyze_texts_batch(texts_list, allow_partial=False, keep_loaded=True, offline=True)
                for t_item, r_item in zip(texts_list, batch_res):
                    scores_cache[t_item] = float(r_item['global_score']['p_ai_percent'])
            else:
                for text_item in texts_to_score:
                    res = ai_mod.analyze_text(text_item, allow_partial=False, keep_loaded=True, offline=True)
                    scores_cache[text_item] = float(res['global_score']['p_ai_percent'])
        except Exception as e:
            print(f"⚠️ [AIDetector] Erreur lors de l'inférence du détecteur IA : {e}")
            return annotated_body, 0, []

        badges_applied = 0
        failing_paragraphs = []

        for c in candidates:
            idx = c['block_idx']
            orig_block = c['raw_block']
            score_b = scores_cache.get(c['text_before']) if c['valid_b'] else None
            score_a = scores_cache.get(c['text_after']) if c['valid_a'] else None

            badge_html = format_ai_score_badge(score_b, score_a)
            if badge_html:
                blocks[idx] = attach_badge_to_block(orig_block, badge_html)
                badges_applied += 1

            if score_a is not None and score_a > 10.0:
                src_file, approx_line = cls.find_source_location(c['text_after'], file_lines_cache, repo_dir)
                clean_text = re.sub(r'\s+', ' ', c['text_after']).strip()
                snippet = clean_text[:140] + "..." if len(clean_text) > 140 else clean_text
                failing_paragraphs.append({
                    'section': c['section'],
                    'file': src_file,
                    'line': approx_line,
                    'score_after': score_a,
                    'score_before': score_b,
                    'snippet': snippet,
                    'full_text': c['text_after'],
                })

        updated_body = "".join(blocks)
        print(f"✅ [AIDetector] {badges_applied} badges de score IA attachés avec succès.")
        return updated_body, badges_applied, failing_paragraphs

    @classmethod
    def inject_explanation_callout(cls, body: str, explanation: str) -> str:
        """
        Injecte le callout de conciliation collaborative TOUT EN HAUT de la note,
        avant même le titre H1 (# Titre...), juste après le frontmatter YAML s'il existe.
        Supprime tout ancien callout de synthèse pour éviter les doublons.
        """
        if not explanation or not explanation.strip():
            return body

        # Formater les lignes du callout
        lines = explanation.strip().splitlines()
        callout_lines = [
            "> [!NOTE]",
            "> **🔄 Synthèse des Travaux Récents & Conciliation Collaborative**",
            ">"
        ]
        for l in lines:
            if l.strip():
                callout_lines.append(f"> {l}")
            else:
                callout_lines.append(">")
        callout_str = "\n".join(callout_lines) + "\n\n"

        # Supprimer tout ancien callout de synthèse (peu importe son emplacement)
        pattern = r'>\s*\[!NOTE\]\s*\n>\s*\*\*🔄\s*Synthèse des Travaux Récents & Conciliation Collaborative\*\*.*?(?=(?:\n(?!>))|\Z)'
        clean_body = re.sub(pattern, '', body, flags=re.DOTALL)
        clean_body = re.sub(r'\n{3,}', '\n\n', clean_body).strip()

        # Insertion tout en haut : après frontmatter YAML (--- ... ---) et commentaires HTML (<!-- ... -->)
        fm_match = re.match(r'^(---\n.*?\n---\n*)', clean_body, re.DOTALL)
        if fm_match:
            frontmatter_part = fm_match.group(1).rstrip() + "\n\n"
            rest = clean_body[fm_match.end():].lstrip()
            meta_match = re.match(r'^((?:<!--.*?-->\n*)+)', rest, re.DOTALL)
            if meta_match:
                meta_part = meta_match.group(1).rstrip() + "\n\n"
                content_after = rest[meta_match.end():].lstrip()
                return f"{frontmatter_part}{meta_part}{callout_str}{content_after}"
            else:
                return f"{frontmatter_part}{callout_str}{rest}"
        else:
            meta_match = re.match(r'^((?:<!--.*?-->\n*)+)', clean_body, re.DOTALL)
            if meta_match:
                meta_part = meta_match.group(1).rstrip() + "\n\n"
                content_after = clean_body[meta_match.end():].lstrip()
                return f"{meta_part}{callout_str}{content_after}"
            else:
                return f"{callout_str}{clean_body}"

    @classmethod
    def merge_and_update(
        cls,
        target_path: Path,
        new_markdown: str,
        baseline_content: Optional[str] = None,
        input_path: Optional[Path] = None,
        repo_dir: Optional[Path] = None,
        baseline_commit: Optional[str] = None,
        first_image_rel: Optional[str] = None,
        enable_ai: bool = True,
        compliance_threshold: float = 0.10,
        explanation: Optional[str] = None,
        is_collab: bool = False,
        author_name: str = "",
        head_text: Optional[str] = None
    ) -> Tuple[str, str, Dict[str, any]]:
        """Fusionne la nouvelle version avec la baseline différentielle."""
        stats = {
            "is_new": True,
            "diff_count": 0,
            "modified_sections": [],
            "ai_scored_count": 0,
            "failing_ai_paragraphs": [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Récupération ou préservation de l'explication collaborative
        active_explanation = explanation
        if (not active_explanation or not active_explanation.strip()) and target_path.exists():
            try:
                prev_text = target_path.read_text(encoding="utf-8", errors="replace")
                m_exp = re.search(
                    r'>\s*\[!NOTE\]\s*\n>\s*\*\*🔄\s*Synthèse des Travaux Récents & Conciliation Collaborative\*\*.*?(?=(?:\n(?!>))|\Z)',
                    prev_text,
                    flags=re.DOTALL
                )
                if m_exp:
                    raw_callout = m_exp.group(0)
                    m_header = re.search(
                        r'>\s*\[!NOTE\]\s*\n>\s*\*\*🔄\s*Synthèse des Travaux Récents & Conciliation Collaborative\*\*(?:\s*:)?\s*\n?',
                        raw_callout
                    )
                    if m_header:
                        b_lines = raw_callout[m_header.end():].splitlines()
                        unprefixed = [re.sub(r'^>\s?', '', l) for l in b_lines]
                        candidate_exp = "\n".join(unprefixed).strip()
                        # Si l'explication existante est déjà structurée par auteur, on la conserve
                        if "- **James" in candidate_exp or "- **Stergios" in candidate_exp:
                            active_explanation = candidate_exp
            except Exception:
                pass

        # Si l'explication existante est l'ancien paragraphe non structuré ou si aucune explication n'est présente pour latent_space :
        if (not active_explanation or not active_explanation.strip() or ("- **James" not in active_explanation and "- **Stergios" not in active_explanation)) and ("latent_space" in target_path.stem.lower() or "aaai" in str(target_path).lower()):
            active_explanation = cls.LATENT_SPACE_DEFAULT_SYNTHESIS

        diff_block = ""
        body_to_render = new_markdown

        old_content = ""
        if baseline_content:
            old_content = baseline_content
            stats["is_new"] = False
        elif target_path.exists():
            stats["is_new"] = False
            try:
                old_content = target_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print(f"[DiffEngine] Erreur de lecture du fichier existant {target_path}: {e}")

        if old_content:
            try:
                cleaned_old_for_diff = cls.extract_manuscript_body(old_content)
                cleaned_new_for_diff = cls.extract_manuscript_body(new_markdown.strip())
                cleaned_head_for_diff = cls.extract_manuscript_body(head_text.strip()) if head_text else None

                annotated_body, tree_toc, diff_count, mod_sections = cls.generate_diff_annotated_body(
                    cleaned_old_for_diff,
                    cleaned_new_for_diff,
                    is_collab=is_collab,
                    author_name=author_name,
                    head_text=cleaned_head_for_diff
                )
                stats["diff_count"] = diff_count
                stats["modified_sections"] = mod_sections

                if diff_count > 0:
                    doc_title = target_path.stem.replace('_', ' ').upper()
                    diff_block = (
                        f"{cls.DIFF_SUMMARY_HEADER}\n\n"
                        f"> [!IMPORTANT]\n"
                        f"> **🌳 Arborescence des Modifications Détectées ({diff_count} deltas) :**\n"
                        f">\n"
                        f"> 📂 **{doc_title}**<br>\n"
                        f"{tree_toc}\n\n"
                        f"---\n\n"
                    )
                    if enable_ai:
                        try:
                            annotated_body, ai_badge_count, failing_paras = cls.attach_ai_score_badges(
                                annotated_body,
                                enable_ai_score=True,
                                source_file_path=input_path,
                                included_files=[],
                                repo_dir=repo_dir
                            )
                            stats["ai_scored_count"] = ai_badge_count
                            stats["failing_ai_paragraphs"] = failing_paras
                        except Exception as e_ai:
                            print(f"⚠️ [AIDetector] Évaluation stylistique ignorée ({e_ai}). Poursuite de la génération du manuscrit.")
                    body_to_render = annotated_body
                else:
                    doc_title = target_path.stem.replace('_', ' ').upper()
                    diff_block = (
                        f"## 📑 Structure & Sommaire AST du Manuscrit\n\n"
                        f"> [!NOTE]\n"
                        f"> **🌳 Arborescence des Sections AST (État Actuel) :**\n"
                        f">\n"
                        f"> 📂 **{doc_title}**<br>\n"
                        f"{tree_toc}\n\n"
                        f"---\n\n"
                    )
                    if enable_ai:
                        try:
                            annotated_body, ai_badge_count, failing_paras = cls.attach_ai_score_badges(
                                new_markdown,
                                enable_ai_score=True,
                                source_file_path=input_path,
                                included_files=[],
                                repo_dir=repo_dir
                            )
                            stats["ai_scored_count"] = ai_badge_count
                            stats["failing_ai_paragraphs"] = failing_paras
                        except Exception as e_ai:
                            print(f"⚠️ [AIDetector] Évaluation stylistique ignorée ({e_ai}). Poursuite de la génération du manuscrit.")
                    body_to_render = annotated_body
            except Exception as e:
                print(f"[DiffEngine] Erreur lors de la comparaison de diff: {e}")
                diff_block = ""
                body_to_render = new_markdown

        ai_cert_block = ""

        # 1. Frontmatter YAML pour Obsidian
        frontmatter = ""
        if first_image_rel:
            frontmatter = f"---\nImage: \"[[{first_image_rel}]]\"\n---\n"
        elif target_path.exists():
            try:
                prev_text = target_path.read_text(encoding="utf-8", errors="replace")
                fm_match = re.match(r'^(---\n.*?\n---\n)', prev_text, re.DOTALL)
                if fm_match:
                    frontmatter = fm_match.group(1)
            except Exception:
                pass

        # 2. Métadonnées d'en-tête
        artifact_name = target_path.stem.upper()
        meta_lines = [f"<!-- ARTIFACT: {artifact_name}_MANUSCRIPT -->"]
        if input_path:
            meta_lines.append(f"<!-- SOURCE_FILE: {input_path.as_posix()} -->")
        if repo_dir:
            meta_lines.append(f"<!-- REPO_DIR: {repo_dir.as_posix()} -->")
        if baseline_commit:
            meta_lines.append(f"<!-- BASELINE_COMMIT: {baseline_commit[:8]} -->")
        meta_lines.append(f"<!-- Generated at: {stats['timestamp']} -->\n\n")
        meta_header = "\n".join(meta_lines)

        # 3. Assemblage du modèle pour le Brain Antigravity (avec diffs, arborescence et badges IA)
        brain_document_template = (
            f"{frontmatter}"
            f"{meta_header}"
            f"{ai_cert_block}"
            f"{diff_block}"
            f"{body_to_render.rstrip()}\n"
        )
        brain_document_template = LatexToMarkdownConverter.sanitize_callouts(brain_document_template)

        if active_explanation:
            brain_document_template = cls.inject_explanation_callout(brain_document_template, active_explanation)
            stats["has_explanation"] = True
        else:
            stats["has_explanation"] = False

        # 4. Assemblage de la version propre pour le coffre Obsidian (0 diff, 0 badge IA, wikilinks ![[...]], images copiées dans le vault)
        slug = target_path.stem
        vault_candidates = [
            Path.home() / "Documents" / "VoiceNotes",
            Path(r"C:\Users\Jamet\Documents\VoiceNotes"),
            Path(r"C:\Users\hjamet\Documents\VoiceNotes"),
        ]
        vault_dir = next((v for v in vault_candidates if v.exists()), None)

        obsidian_document = (
            f"{frontmatter}"
            f"{meta_header}"
            f"{new_markdown.rstrip()}\n"
        )
        obsidian_document = LatexToMarkdownConverter.sanitize_callouts(obsidian_document)

        if active_explanation:
            obsidian_document = cls.inject_explanation_callout(obsidian_document, active_explanation)

        obsidian_document = clean_obsidian_manuscript(obsidian_document)
        obsidian_document = format_images_for_obsidian(
            markdown_text=obsidian_document,
            vault_dir=vault_dir,
            slug=slug,
            repo_dir=repo_dir,
            input_path=input_path
        )

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(obsidian_document, encoding="utf-8")
        print(f"📄 [Obsidian Note] Note propre générée sans diff ni badges IA dans : {target_path}")

        return obsidian_document, brain_document_template, stats


def check_for_conflict_markers(repo_dir: Path, target_path: Optional[Path] = None) -> List[Tuple[Path, int]]:
    """
    Scanne les fichiers source pertinents (.tex, .bib, .md, .sty) du dépôt
    à la recherche de vrais marqueurs de conflit Git (<<<<<<< / ======= / >>>>>>> en début de ligne).
    Retourne une liste de tuples (chemin_fichier, nombre_conflits).
    """
    conflicted: List[Tuple[Path, int]] = []
    checked_paths: Set[Path] = set()
    candidate_files: List[Path] = []

    if target_path and target_path.exists() and target_path.is_file():
        candidate_files.append(target_path)
        checked_paths.add(target_path.resolve())

    ignored_dir_names = {".git", "scratch", "node_modules", ".venv", ".agent", ".agents", "agents", "antigravity"}

    for ext in ("*.tex", "*.bib", "*.md", "*.sty"):
        for p in repo_dir.rglob(ext):
            resolved = p.resolve()
            if resolved in checked_paths:
                continue
            parts = set(resolved.parts)
            if ignored_dir_names.intersection(parts):
                continue
            candidate_files.append(p)
            checked_paths.add(resolved)

    git_conflict_pattern = re.compile(r'^<{7}(?:\s.*)?$', re.MULTILINE)
    git_end_pattern = re.compile(r'^>{7}(?:\s.*)?$', re.MULTILINE)

    for f in candidate_files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if git_conflict_pattern.search(content) and git_end_pattern.search(content):
                count = len(git_conflict_pattern.findall(content))
                conflicted.append((f, count))
        except Exception:
            pass

    return conflicted


def display_conflict_banner_and_exit(conflicted_files: List[str], details: Optional[str] = None) -> None:
    """
    Affiche un bandeau d'alerte rouge capital contenant les instructions mot à mot d'Henri :
    « 🚨 [ACTION AGENT CRITIQUE : CONFLIT GIT DÉTECTÉ LORS DU PULL]
    RÈGLE D'OR : Les modifications apportées par les collaborateurs sont STRICTEMENT PRIORITAIRES et ne doivent JAMAIS être supprimées !
    Consigne de résolution : Identifie précisément l'intention de leur modification et concilie astucieusement notre travail et le leur pour préserver les deux apports.
    OBLIGATION DE REPORTING : Tu DOIS formuler un retour explicatif détaillé à Henri précisant ce qui a été récupéré, ce qui a été concilié et comment. »
    Puis quitte avec le code d'erreur 3.
    """
    banner_width = 86
    box_top = "╔" + "═" * (banner_width - 2) + "╗"
    box_mid = "╠" + "═" * (banner_width - 2) + "╣"
    box_bot = "╚" + "═" * (banner_width - 2) + "╝"

    print("\n" + box_top)
    print("║  🚨 [ACTION AGENT CRITIQUE : CONFLIT GIT DÉTECTÉ LORS DU PULL]".ljust(banner_width - 1) + "║")
    print(box_mid)
    print("║  RÈGLE D'OR : Les modifications apportées par les collaborateurs sont".ljust(banner_width - 1) + "║")
    print("║  STRICTEMENT PRIORITAIRES et ne doivent JAMAIS être supprimées !".ljust(banner_width - 1) + "║")
    print("║".ljust(banner_width - 1) + "║")
    print("║  Consigne de résolution : Identifie précisément l'intention de leur".ljust(banner_width - 1) + "║")
    print("║  modification et concilie astucieusement notre travail et le leur pour".ljust(banner_width - 1) + "║")
    print("║  préserver les deux apports.".ljust(banner_width - 1) + "║")
    print("║".ljust(banner_width - 1) + "║")
    print("║  OBLIGATION DE REPORTING : Tu DOIS formuler un retour explicatif détaillé à".ljust(banner_width - 1) + "║")
    print("║  Henri précisant ce qui a été récupéré, ce qui a été concilié et comment.".ljust(banner_width - 1) + "║")
    print(box_bot)

    if conflicted_files:
        print("\n📁 Fichiers en conflit détectés :")
        for cf in conflicted_files:
            print(f"   🔴 {cf}")

    if details:
        clean_details = details.strip()
        if len(clean_details) > 800:
            clean_details = clean_details[:800] + "\n   [...]"
        print(f"\nℹ️ Détails Git :\n{clean_details}")

    print("\n🛠️ PROTOCOLE DE RÉSOLUTION OBLIGATOIRE POUR L'AGENT :")
    print("   1. Ouvre immédiatement les fichiers en conflit ci-dessus.")
    print("   2. Analyse l'intention des co-auteurs : leurs apports sont strictement prioritaires.")
    print("   3. Concilie astucieusement leur texte et le nôtre sans supprimer leurs modifications.")
    print("   4. Supprime tous les marqueurs Git (<<<<<<<, =======, >>>>>>>) et valide la syntaxe LaTeX.")
    print("   5. Effectue 'git add <fichiers>' et finalise l'opération ('git rebase --continue' ou 'git commit').")
    print("   6. Relance le script de conversion pour certifier la synchronisation.")
    print("   7. Formule un rapport explicatif détaillé à Henri dans le chat sur les éléments conciliés.\n")
    print("=" * banner_width)
    sys.exit(3)


def git_sync_pull(repo_dir: Path, target_file: Optional[Path] = None) -> None:
    """
    Synchronise systématiquement le dépôt Git avec le remote au démarrage via :
        git pull --rebase --autostash
    
    - Détecte et affiche les nouveaux commits et fichiers touchés par les collaborateurs.
    - Détecte tout conflit Git ou marqueur résiduel et affiche le bandeau critique d'Henri avant d'interrompre avec exit code 3.
    """
    print(f"🔄 [Git Sync] Vérification du dépôt Git : {repo_dir}")

    # 1. Vérification préalable : conflits non résolus existants ?
    try:
        status_res = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if status_res.returncode == 0:
            unmerged = [
                line[3:].strip() for line in status_res.stdout.splitlines()
                if line[:2] in ("UU", "AA", "UD", "DU", "DD", "AU", "UA")
            ]
            if unmerged:
                display_conflict_banner_and_exit(unmerged, "Des fichiers non fusionnés (unmerged) sont présents dans le dépôt.")
    except Exception:
        pass

    pre_markers = check_for_conflict_markers(repo_dir, target_file)
    if pre_markers:
        display_conflict_banner_and_exit(
            [f"{f} ({cnt} marqueur(s))" for f, cnt in pre_markers],
            "Des marqueurs de conflit Git (<<<<<<<) sont présents dans les fichiers du dépôt."
        )

    # 2. Vérifier si un remote est configuré
    try:
        remote_res = subprocess.run(
            ["git", "-C", str(repo_dir), "remote"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if remote_res.returncode != 0 or not remote_res.stdout.strip():
            print("ℹ️ [Git Sync] Aucun dépôt remote configuré. Synchronisation distante ignorée.")
            return
    except Exception as e:
        print(f"ℹ️ [Git Sync] Impossible de vérifier les remotes ({e}). Synchronisation ignorée.")
        return

    # 3. Enregistrer l'état HEAD avant pull
    head_before = None
    try:
        rev_res = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if rev_res.returncode == 0:
            head_before = rev_res.stdout.strip()
    except Exception:
        pass

    # 4. Vérifier s'il y a des commits distants à intégrer
    try:
        fetch_res = subprocess.run(
            ["git", "-C", str(repo_dir), "fetch"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if fetch_res.returncode == 0:
            rev_upstream = subprocess.run(
                ["git", "-C", str(repo_dir), "rev-list", "HEAD..@{u}", "--count"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if rev_upstream.returncode == 0 and rev_upstream.stdout.strip() == "0":
                print("ℹ️ [Git Sync] Branche locale déjà à jour avec le remote (0 commit distant en attente).")
                return
    except Exception:
        pass

    # 5. Exécuter git pull --rebase --autostash
    print("📥 [Git Sync] Exécution de : git pull --rebase --autostash...")
    pull_failed = False
    pull_output = ""
    try:
        pull_res = subprocess.run(
            ["git", "-C", str(repo_dir), "pull", "--rebase", "--autostash"],
            capture_output=True,
            text=True,
            timeout=60
        )
        pull_output = (pull_res.stdout + "\n" + pull_res.stderr).strip()
        if pull_res.returncode != 0:
            pull_failed = True
    except subprocess.TimeoutExpired:
        print("⚠️ [Git Sync] Timeout (60s) dépassé lors du pull. Poursuite en mode local.")
        return
    except Exception as ge:
        print(f"⚠️ [Git Sync] Erreur lors de l'exécution du pull ({ge}). Poursuite en mode local.")
        return

    # 5. Détection de conflits post-pull
    unmerged_files: List[str] = []
    try:
        st_res = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if st_res.returncode == 0:
            unmerged_files = [
                line[3:].strip() for line in st_res.stdout.splitlines()
                if line[:2] in ("UU", "AA", "UD", "DU", "DD", "AU", "UA")
            ]
    except Exception:
        pass

    post_markers = check_for_conflict_markers(repo_dir, target_file)
    marker_files = [f"{f} ({cnt} marqueur(s))" for f, cnt in post_markers]

    is_conflict = (
        (pull_failed and any(k in pull_output.lower() for k in ("conflict", "could not apply", "failed to merge", "patch failed")))
        or bool(unmerged_files)
        or bool(post_markers)
    )

    if is_conflict:
        conflicted_all = list(dict.fromkeys(unmerged_files + marker_files))
        display_conflict_banner_and_exit(conflicted_all, pull_output)

    if pull_failed:
        # Échec sans conflit (ex: problème réseau, hôte inaccessible, auth)
        print(f"⚠️ [Git Sync] Avertissement pull distant (non-bloquant) :\n   {pull_output.splitlines()[-1] if pull_output else 'Erreur inconnue'}")
        print("ℹ️ [Git Sync] Poursuite du traitement avec l'état local actuel.")
        return

    # 6. Succès du pull : Détecter et afficher les modifications rapatriées
    head_after = None
    try:
        rev_after = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if rev_after.returncode == 0:
            head_after = rev_after.stdout.strip()
    except Exception:
        pass

    if head_before and head_after and head_before != head_after:
        new_commits_str = ""
        try:
            log_res = subprocess.run(
                ["git", "-C", str(repo_dir), "log", f"{head_before}..{head_after}", "--pretty=format:* %h - %an (%ar): %s"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10
            )
            if log_res.returncode == 0:
                new_commits_str = log_res.stdout.strip()
        except Exception:
            pass

        if not new_commits_str:
            try:
                log_u = subprocess.run(
                    ["git", "-C", str(repo_dir), "log", "-n", "5", "--pretty=format:* %h - %an (%ar): %s"],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10
                )
                if log_u.returncode == 0:
                    new_commits_str = log_u.stdout.strip()
            except Exception:
                pass

        files_changed_str = ""
        try:
            diff_res = subprocess.run(
                ["git", "-C", str(repo_dir), "diff", "--name-status", f"{head_before}", f"{head_after}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if diff_res.returncode == 0:
                files_changed_str = diff_res.stdout.strip()
        except Exception:
            pass

        box_width = 86
        c_top = "┌" + "─" * (box_width - 2) + "┐"
        c_mid = "├" + "─" * (box_width - 2) + "┤"
        c_bot = "└" + "─" * (box_width - 2) + "┘"

        print("\n" + c_top)
        print("│ 📥 [GIT SYNC] NOUVELLES MODIFICATIONS DÉTECTÉES (COLLABORATEURS)".ljust(box_width - 1) + "│")
        print(c_mid)
        print("│ Des modifications distantes ont été rapatriées avec succès lors du pull :".ljust(box_width - 1) + "│")
        print("│".ljust(box_width - 1) + "│")
        print("│ 📝 Commits & Auteurs :".ljust(box_width - 1) + "│")
        if new_commits_str:
            for c_line in new_commits_str.splitlines()[:10]:
                print(f"│   {c_line}")
        else:
            print("│   * Commits intégrés via rebase.".ljust(box_width - 1) + "│")
        print("│".ljust(box_width - 1) + "│")
        print("│ 📁 Fichiers touchés :".ljust(box_width - 1) + "│")
        if files_changed_str:
            for f_line in files_changed_str.splitlines()[:10]:
                print(f"│   {f_line}")
        else:
            print("│   (Arborescence mise à jour)".ljust(box_width - 1) + "│")
        print("│".ljust(box_width - 1) + "│")
        print("│ 💡 RÈGLE D'OR DOCTRINALE :".ljust(box_width - 1) + "│")
        print("│   Les modifications apportées par les collaborateurs sont STRICTEMENT".ljust(box_width - 1) + "│")
        print("│   PRIORITAIRES et ne doivent JAMAIS être supprimées !".ljust(box_width - 1) + "│")
        print("│   Concilie astucieusement notre travail et le leur sans perte de substance.".ljust(box_width - 1) + "│")
        print("│   Tu DOIS formuler un retour explicatif à Henri sur ce qui a été récupéré.".ljust(box_width - 1) + "│")
        print(c_bot + "\n")
    else:
        print("📥 [Git Sync] Synchronisation réussie : le dépôt est déjà à jour avec le remote.")


def print_ai_compliance_report(failing_paragraphs: List[Dict[str, Any]], total_scored: int) -> None:
    """Affiche le rapport de conformité IA à l'attention directe de l'agent."""
    if failing_paragraphs:
        print("\n================================================================================")
        print("🚨 [ACTION AGENT REQUISE : REFORMULATION OBLIGATOIRE — SEUIL P(IA) > 10% NON RESPECTÉ]")
        print("================================================================================")
        print(f"⚠️  Attention : Le seuil strict P(IA) <= 10.0% n'est pas respecté pour {len(failing_paragraphs)} paragraphe(s) modifié(s) sur {total_scored}.")
        print("\n📋 Détail des paragraphes défaillants à réviser chirurgicalement :")
        print("--------------------------------------------------------------------------------")
        for idx, item in enumerate(failing_paragraphs, 1):
            line_str = f"~ligne {item['line']}" if item.get('line') else "ligne non résolue"
            if item.get('score_before') is not None:
                score_ev = f"{item['score_before']:.1f}% ➔ {item['score_after']:.1f}%"
            else:
                score_ev = f"{item['score_after']:.1f}%"
            print(f"[{idx}] Section : {item['section']}")
            print(f"    Fichier source : {item['file']} ({line_str})")
            print(f"    Score P(IA) actuel : {item['score_after']:.1f}% (évolution: {score_ev})")
            print(f"    Extrait textuel : \"{item['snippet']}\"")
            print("--------------------------------------------------------------------------------")
        print("\n🛑 CONSIGNE IMPÉRATIVE POUR L'AGENT :")
        print("L'agent NE DOIT PAS s'arrêter ni déclarer sa tâche terminée. Il doit réécrire")
        print("chirurgicalement ces paragraphes dans le code source LaTeX (en mandant Claude Opus /")
        print("protocole reformulate-human pour éliminer les marqueurs IA), puis relancer immédiatement :")
        print("    python antigravity/scripts/latex_to_markdown_artifact.py --diff")
        print("================================================================================\n")
    elif total_scored > 0:
        print("\n================================================================================")
        print("✅ [CERTIFICATION IA CONFORME] 100% des paragraphes modifiés respectent le seuil strict P(IA) <= 10.0%.")
        print("================================================================================\n")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convertisseur & Moteur Diff AST 100% Automatique (LaTeX ➔ Note miroir Obsidian papers/<nom>.md).\n\n"
            "Ce script ne requiert AUCUN argument ni option. Il fonctionne de manière entièrement automatique et déterministe :\n"
            "  1. Détection du fichier source : cherche automatiquement 'main.tex' (dans ./ ou ./paper/) ou accepte un chemin en argument unique.\n"
            "  2. Détection de la bibliographie : scanne le dossier du fichier source pour charger automatiquement tout fichier .bib présent.\n"
            "  3. Baseline Git automatique : ancre la comparaison AST sur le dernier commit signé par Henri Jamet (fallback sur HEAD~1).\n"
            "  4. Note miroir Obsidian : déduit le nom du papier et écrit directement dans VoiceNotes/papers/<nom_papier>.md."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "latex_file",
        nargs="?",
        default=None,
        help="Chemin du fichier LaTeX cible (ou .md). Si omis, cherche automatiquement 'main.tex' dans le répertoire courant ou dans './paper/'."
    )
    parser.add_argument(
        "--diff",
        type=str,
        metavar="EXPLANATION",
        default=None,
        help="Générer la vue différentielle avec l'explication obligatoire"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Valider la révision, sceller la baseline Git et pousser sur Overleaf (RÉSERVÉ EXCLUSIVEMENT À LA VALIDATION EXPLICITE D'HENRI)."
    )
    parser.add_argument(
        "--line",
        type=int,
        default=None,
        help="Numéro de ligne optionnel pour la validation granulaire ligne par ligne lors de --commit."
    )
    parser.add_argument(
        "--brain-dir",
        type=str,
        default=None,
        help="Dossier brain spécifique pour synchroniser l'artéfact Markdown Antigravity."
    )
    parser.add_argument(
        "--collab",
        action="store_true",
        help="Forcer le mode collaborateur (diff bleu ciel / ambre)."
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Forcer le mode auteur local (diff vert doux / rouge doux)."
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        help="Spécifier explicitement un commit Git (ou hash, ou chemin de fichier) servant de baseline différentielle."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Forcer le mode évaluation propre sans diffs (texte actuel avec badges IA et sommaire AST)."
    )

    args = parser.parse_args()
    if not hasattr(args, "input_file"):
        args.input_file = args.latex_file

    # Extraction et validation de l'explication obligatoire lors de l'appel à --diff
    diff_explanation = None
    if args.diff is not None:
        if not args.diff.strip():
            print("\n" + "=" * 80)
            print("❌ [ERREUR : ARGUMENT OBLIGATOIRE MANQUANT]")
            print("L'explication est obligatoire avec le flag --diff :")
            print("Usage : python latex_to_markdown_artifact.py paper/main.tex --diff \"Explication de la révision...\"")
            print("=" * 80 + "\n")
            sys.exit(1)
        diff_explanation = args.diff.strip()

    # 1. Détection automatique du fichier source
    if args.latex_file:
        input_path = Path(args.latex_file).resolve()
    else:
        cwd = Path.cwd().resolve()
        candidates = [
            cwd / "main.tex",
            cwd / "paper" / "main.tex",
        ]
        found = None
        for c in candidates:
            if c.exists():
                found = c
                break
        if not found:
            tex_files = list(cwd.glob("*.tex"))
            if len(tex_files) == 1:
                found = tex_files[0]
        if not found:
            print("❌ Erreur : Aucun fichier source spécifié et 'main.tex' introuvable dans le répertoire courant ni dans './paper/'.")
            print("Usage : python latex_to_markdown_artifact.py [chemin_main.tex]")
            sys.exit(1)
        input_path = found.resolve()

    if not input_path.exists():
        print(f"❌ Erreur : Le fichier d'entrée '{input_path}' n'existe pas.")
        sys.exit(1)

    print("=" * 70)
    print("🚀 DÉMARRAGE DU CONVERTISSEUR & MOTEUR DIFF AUTOMATIQUE")
    print(f"📂 Entrée source : {input_path}")

    is_markdown = input_path.suffix.lower() in ('.md', '.markdown')

    doc_title = ""
    cited_keys_count = 0

    # Détection du dépôt Git
    tex_dir = input_path.parent
    search_dirs = [tex_dir, tex_dir.parent]
    repo_dir = None
    for d in search_dirs:
        if (d / ".git").exists():
            repo_dir = d
            break
    if not repo_dir:
        try:
            res_root = subprocess.run(
                ["git", "-C", str(tex_dir), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res_root.returncode == 0 and res_root.stdout.strip():
                repo_dir = Path(res_root.stdout.strip())
        except Exception:
            pass

    # Synchronisation Git systématique au démarrage (git pull --rebase --autostash)
    if repo_dir:
        git_sync_pull(repo_dir, input_path)

    if is_markdown:
        print("📄 Format détecté : Markdown (.md)")
        raw_md = input_path.read_text(encoding="utf-8", errors="replace")
        
        title_match = re.search(r'^#\s+(.+)$', raw_md, re.MULTILINE)
        if title_match:
            doc_title = title_match.group(1).strip()
        else:
            fm_title = re.search(r'^title:\s*["\']?([^"\']+)["\']?', raw_md, re.MULTILINE)
            if fm_title:
                doc_title = fm_title.group(1).strip()

        converted_md = raw_md
    else:
        print("📐 Format détecté : LaTeX (.tex)")

        # 2. Auto-détection de la bibliographie (.bib)
        bib_parser = BibTexParser()
        bib_files = list(input_path.parent.glob("*.bib"))
        if not bib_files and input_path.parent.parent != input_path.parent:
            bib_files = list(input_path.parent.parent.glob("*.bib"))

        if bib_files:
            for bib_file in bib_files:
                print(f"📚 [BibTeX Auto] Bibliographie détectée et chargée : {bib_file.name}")
                bib_parser.load_bib_file(bib_file)
        else:
            print("ℹ️ [BibTeX Auto] Aucun fichier .bib détecté dans le répertoire.")

        converter = LatexToMarkdownConverter(input_path, bib_parser=bib_parser)
        converted_md = converter.convert()
        doc_title = converter.title
        cited_keys_count = len(converter.cited_keys)

    # 3. Auto-détection du fichier miroir Obsidian
    output_path = derive_output_path(input_path, doc_title)

    # 4. Auto-détection ou spécification explicite de la Baseline Git
    baseline_content = None
    effective_git_baseline = None

    if args.commit:
        if args.line is not None:
            if not output_path.exists():
                print(f"❌ Erreur : La note miroir '{output_path}' n'existe pas pour exécuter le commit granulaire.")
                sys.exit(1)

            print("=" * 70)
            print(f"🔒 [Commit Granulaire] Validation des révisions jusqu'à la ligne {args.line}...")
            print(f"📄 Note miroir cible : {output_path}")

            existing_md = output_path.read_text(encoding="utf-8", errors="replace")
            updated_md, val_cnt, rem_cnt = ArtifactDiffManager.validate_revisions_up_to_line(existing_md, args.line)
            output_path.write_text(updated_md, encoding="utf-8")
            print(f"✅ [Note Miroir] Lignes 1 à {args.line - 1} validées ({val_cnt} deltas intégrés, {rem_cnt} restants).")

            effective_git_baseline = None
            if repo_dir:
                try:
                    subprocess.run(["git", "-C", str(repo_dir), "add", "-u"], check=True)
                    subprocess.run(["git", "-C", str(repo_dir), "add", "figures/", "assets/"], check=False)
                    diff_staged = subprocess.run(["git", "-C", str(repo_dir), "diff", "--cached", "--quiet"])
                    if diff_staged.returncode != 0:
                        commit_msg = f"review(paper): validate revisions up to line {args.line}"
                        subprocess.run(
                            ["git", "-C", str(repo_dir), "commit", "-m", commit_msg, '--author=Henri Jamet <42291955+hjamet@users.noreply.github.com>'],
                            check=True
                        )
                        print(f"📦 [Git Commit] Commit créé : {commit_msg}")
                        push_res = subprocess.run(["git", "-C", str(repo_dir), "push"], capture_output=True, text=True)
                        if push_res.returncode == 0:
                            print("🚀 [Git Push] Modifications poussées avec succès vers le remote.")
                        else:
                            print(f"ℹ️ [Git Push] {push_res.stderr.strip() or push_res.stdout.strip()}")
                    else:
                        print("ℹ️ [Git Commit] Aucune modification LaTeX en attente dans le dépôt.")

                    res_head = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
                    effective_git_baseline = res_head.stdout.strip()
                    print(f"✅ [Git Baseline] Nouvelle baseline active : {effective_git_baseline[:8]}")
                except Exception as ce:
                    print(f"⚠️ [Git Commit] Erreur lors du commit Git : {ce}")

            print("=" * 70)
            print("✅ VALIDATION GRANULAIRE TERMINÉE AVEC SUCCÈS")
            print(f"📄 Note miroir : {output_path}")
            print(f"📍 Ligne pivot : {args.line}")
            print(f"📊 Deltas validés : {val_cnt} | Deltas restants : {rem_cnt}")
            if effective_git_baseline:
                print(f"📦 Baseline Git : {effective_git_baseline[:8]}")
            print("=" * 70)
            sys.exit(0)
        else:
            if not repo_dir:
                print("❌ Erreur : Aucun dépôt Git détecté pour valider le commit baseline.")
            else:
                print("=" * 70)
                print("🔒 [Git Commit Baseline] Validation et commit de l'état actuel comme nouvelle baseline...")
                try:
                    status_res = subprocess.run(["git", "-C", str(repo_dir), "status", "--porcelain"], capture_output=True, text=True, check=True)
                    if status_res.stdout.strip():
                        subprocess.run(["git", "-C", str(repo_dir), "add", "-u"], check=True)
                        subprocess.run(["git", "-C", str(repo_dir), "add", "figures/", "assets/"], check=False)
                        commit_msg = "feat(paper): validate current manuscript state as baseline"
                        subprocess.run(
                            ["git", "-C", str(repo_dir), "commit", "-m", commit_msg, '--author=Henri Jamet <42291955+hjamet@users.noreply.github.com>'],
                            check=True
                        )
                        print("📦 [Git Commit Baseline] Nouveau commit créé avec succès.")
                    else:
                        print("ℹ️ [Git Commit Baseline] Arbre de travail propre, validation du HEAD actuel.")

                    res_head = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
                    effective_git_baseline = res_head.stdout.strip()
                    baseline_content = converted_md
                    print(f"✅ [Git Commit Baseline] Baseline officielle validée : {effective_git_baseline[:8]}")

                    push_res = subprocess.run(["git", "-C", str(repo_dir), "push"], capture_output=True, text=True)
                    if push_res.returncode == 0:
                        print("🚀 [Git Push] Modifications poussées avec succès vers le remote Overleaf.")
                    else:
                        print(f"ℹ️ [Git Push] {push_res.stderr.strip() or push_res.stdout.strip()}")
                except Exception as ce:
                    print(f"⚠️ [Git Commit Baseline] Erreur lors du commit baseline : {ce}")
    elif getattr(args, "baseline", None):
        target_rev = args.baseline.strip()
        print(f"📦 [Git Baseline Manuelle] Baseline spécifiée par l'utilisateur : {target_rev}")
        # 1. Vérifier si c'est un fichier direct sur le disque
        base_file_cand = Path(target_rev)
        if not base_file_cand.is_absolute() and tex_dir:
            if (tex_dir / base_file_cand).exists():
                base_file_cand = tex_dir / base_file_cand
        if base_file_cand.exists() and base_file_cand.is_file():
            raw_baseline = base_file_cand.read_text(encoding="utf-8", errors="replace")
            print(f"📦 [Git Baseline Fichier] Lecture directe depuis {base_file_cand} ({len(raw_baseline)} caractères)")
            if base_file_cand.suffix.lower() in ('.tex', '.latex'):
                base_converter = LatexToMarkdownConverter(base_file_cand, bib_parser=bib_parser if not is_markdown else None, base_dir=input_path.parent)
                baseline_content = base_converter.convert()
            else:
                baseline_content = raw_baseline
            effective_git_baseline = target_rev
        else:
            # 2. C'est une révision Git
            rel_file = input_path.resolve().relative_to(repo_dir.resolve()).as_posix() if repo_dir else input_path.name
            raw_baseline = None

            # Essayer d'abord dans le repo courant
            if repo_dir:
                try:
                    git_cmd = ["git", "-C", str(repo_dir), "show", f"{target_rev}:{rel_file}"]
                    res = subprocess.run(git_cmd, capture_output=True, check=True)
                    raw_baseline = res.stdout.decode('utf-8', errors='replace')
                    print(f"📦 [Git Baseline] Version {target_rev[:8] if len(target_rev) > 8 else target_rev} extraite avec succès depuis git ({len(raw_baseline)} caractères)")
                except Exception:
                    pass

            # Si échec, chercher dans les sous-modules ou dépôts frères connus
            if not raw_baseline:
                known_git_dirs = [
                    Path.home() / "Documents" / "code" / "llm-as-recommender" / ".git" / "modules" / "paper" / "wise-2026-llm-as-a-recommender",
                    Path.home() / "Documents" / "code" / "llm-as-recommender" / ".git" / "modules" / "paper-overleaf",
                    Path.home() / "Documents" / "code" / "llm-as-recommender" / ".git",
                ]
                if repo_dir:
                    known_git_dirs.append(repo_dir / ".git")

                for g_dir in known_git_dirs:
                    if g_dir.exists():
                        for test_path in [rel_file, input_path.name, f"paper/{input_path.name}"]:
                            try:
                                git_cmd = ["git", f"--git-dir={g_dir}", f"--work-tree={repo_dir or tex_dir}", "show", f"{target_rev}:{test_path}"]
                                res = subprocess.run(git_cmd, capture_output=True, check=True)
                                if res.stdout:
                                    raw_baseline = res.stdout.decode('utf-8', errors='replace')
                                    print(f"📦 [Git Baseline Cross-Repo] Version {target_rev[:8] if len(target_rev) > 8 else target_rev} extraite depuis {g_dir.name} ({len(raw_baseline)} caractères)")
                                    break
                            except Exception:
                                continue
                    if raw_baseline:
                        break

            if raw_baseline:
                if not is_markdown:
                    scratch_dir = Path.home() / "Documents" / "VoiceNotes" / "antigravity" / "scratch"
                    scratch_dir.mkdir(parents=True, exist_ok=True)
                    clean_rev_str = re.sub(r'[^a-zA-Z0-9_-]', '_', target_rev)
                    tmp_base_tex = scratch_dir / f"_baseline_{clean_rev_str}_{input_path.name}"
                    tmp_base_tex.write_text(raw_baseline, encoding="utf-8")
                    base_converter = LatexToMarkdownConverter(tmp_base_tex, bib_parser=bib_parser if not is_markdown else None, base_dir=input_path.parent)
                    baseline_content = base_converter.convert()
                    print(f"🔄 [Git Baseline] Conversion LaTeX ➔ Markdown de la baseline {target_rev[:8] if len(target_rev) > 8 else target_rev} réussie")
                else:
                    baseline_content = raw_baseline
                effective_git_baseline = target_rev
            else:
                print(f"⚠️ [Git Baseline] Impossible d'extraire la révision git '{target_rev}' pour {rel_file}")
    elif repo_dir and (args.diff is not None or getattr(args, "baseline", None)) and not getattr(args, "clean", False):
        target_rev = None
        if output_path.exists():
            try:
                prev_text = output_path.read_text(encoding="utf-8", errors="replace")
                m_base = re.search(r'<!--\s*BASELINE_COMMIT:\s*([a-zA-Z0-9_-]+)\s*-->', prev_text)
                if m_base:
                    saved_base = m_base.group(1).strip()
                    if saved_base and saved_base.lower() != "none":
                        target_rev = saved_base
                        print(f"📦 [Git Baseline Preserved] Baseline précédente conservée depuis l'artéfact : {target_rev[:8]}")
            except Exception:
                pass

        if not target_rev:
            try:
                res_author = subprocess.run(
                    ["git", "-C", str(repo_dir), "log", '--author=Henri Jamet', "-n", "1", '--format=%H'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                author_commit = res_author.stdout.strip()
                if res_author.returncode == 0 and author_commit:
                    target_rev = author_commit
                    print(f"📦 [Git Baseline Auto] Dernier commit d'Henri Jamet détecté : {target_rev[:8]}")
                else:
                    print("⚠️ [Git Baseline Auto] Aucun commit d'Henri Jamet trouvé dans l'historique, fallback sur HEAD~1")
                    target_rev = "HEAD~1"
            except Exception as e_author:
                print(f"⚠️ [Git Baseline Auto] Erreur recherche commit Henri Jamet ({e_author}), fallback sur HEAD~1")
                target_rev = "HEAD~1"

        try:
            rel_file = input_path.resolve().relative_to(repo_dir.resolve()).as_posix()
            git_cmd = ["git", "-C", str(repo_dir), "show", f"{target_rev}:{rel_file}"]
            res = subprocess.run(git_cmd, capture_output=True, check=True)
            raw_baseline = res.stdout.decode('utf-8', errors='replace')
            print(f"📦 [Git Baseline] Version {target_rev[:8] if len(target_rev) > 8 else target_rev} extraite avec succès depuis git ({len(raw_baseline)} caractères)")

            if not is_markdown:
                scratch_dir = Path.home() / "Documents" / "VoiceNotes" / "antigravity" / "scratch"
                scratch_dir.mkdir(parents=True, exist_ok=True)
                clean_rev_str = re.sub(r'[^a-zA-Z0-9_-]', '_', target_rev)
                tmp_base_tex = scratch_dir / f"_baseline_{clean_rev_str}_{input_path.name}"
                tmp_base_tex.write_text(raw_baseline, encoding="utf-8")
                base_converter = LatexToMarkdownConverter(tmp_base_tex, bib_parser=bib_parser if not is_markdown else None, base_dir=input_path.parent)
                baseline_content = base_converter.convert()
                print(f"🔄 [Git Baseline] Conversion LaTeX ➔ Markdown de la baseline {target_rev[:8] if len(target_rev) > 8 else target_rev} réussie")
            else:
                baseline_content = raw_baseline
            effective_git_baseline = target_rev
        except Exception as e:
            if target_rev not in ("HEAD", "HEAD~0"):
                try:
                    git_cmd_head = ["git", "-C", str(repo_dir), "show", f"HEAD:{rel_file}"]
                    res_head = subprocess.run(git_cmd_head, capture_output=True, check=True)
                    raw_baseline = res_head.stdout.decode('utf-8', errors='replace')
                    print(f"📦 [Git Baseline Fallback] Repli sur HEAD réussi pour {rel_file} ({len(raw_baseline)} caractères)")
                    if not is_markdown:
                        scratch_dir = Path.home() / "Documents" / "VoiceNotes" / "antigravity" / "scratch"
                        scratch_dir.mkdir(parents=True, exist_ok=True)
                        tmp_base_tex = scratch_dir / f"_baseline_HEAD_{input_path.name}"
                        tmp_base_tex.write_text(raw_baseline, encoding="utf-8")
                        base_converter = LatexToMarkdownConverter(tmp_base_tex, bib_parser=bib_parser if not is_markdown else None, base_dir=input_path.parent)
                        baseline_content = base_converter.convert()
                    else:
                        baseline_content = raw_baseline
                    effective_git_baseline = "HEAD"
                except Exception:
                    print(f"⚠️ [Git Baseline] Impossible d'extraire la révision git ({target_rev} ni HEAD) pour {rel_file}: {e}")
            else:
                print(f"⚠️ [Git Baseline] Impossible d'extraire la révision git {target_rev}: {e}")
    else:
        # Mode Évaluation de l'Article dans son État Actuel (Normal / Clean)
        if repo_dir:
            try:
                res_head = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
                effective_git_baseline = res_head.stdout.strip()
                print(f"📦 [Mode Évaluation Actuel] Baseline ancrée sur le commit HEAD : {effective_git_baseline[:8]}")
            except Exception:
                effective_git_baseline = "HEAD"
        baseline_content = converted_md

    print(f"🎯 Sortie Markdown : {output_path}")
    if effective_git_baseline:
        print(f"⚖️ Baseline Git : {effective_git_baseline[:8] if len(effective_git_baseline) > 8 else effective_git_baseline}")
    print("=" * 70)

    print("\n🔍 Comparaison différentielle AST...")

    # Détection automatique de l'auteur et de l'état 3-voies (Baseline -> Collab -> Working Tree / Local Henri)
    is_collab = False
    author_name = ""
    head_content = None

    if getattr(args, "collab", False):
        is_collab = True
        author_name = "Collaborateur"
    elif getattr(args, "local", False):
        is_collab = False
        author_name = "Henri Jamet"
    elif repo_dir and effective_git_baseline:
        try:
            rel_file = input_path.resolve().relative_to(repo_dir.resolve()).as_posix()
            res_diff_worktree = subprocess.run(
                ["git", "-C", str(repo_dir), "diff", "HEAD", "--", rel_file],
                capture_output=True, encoding="utf-8", errors="replace"
            )
            is_dirty = bool(res_diff_worktree.stdout.strip())

            # Partitionnement fin des commits récents par auteur
            collab_authors = []
            collab_commits = []
            local_commits = []

            if effective_git_baseline not in ("HEAD", "HEAD~0"):
                res_log = subprocess.run(
                    ["git", "-C", str(repo_dir), "log", f"{effective_git_baseline}..HEAD", "--format=%H|%an|%ae", "--", rel_file],
                    capture_output=True, encoding="utf-8", errors="replace"
                )
                for line in res_log.stdout.splitlines():
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        c_hash = parts[0]
                        c_an = parts[1].strip()
                        c_ae = parts[2].strip() if len(parts) > 2 else ""
                        if is_local_author(c_an, c_ae):
                            local_commits.append((c_hash, c_an, c_ae))
                        else:
                            norm_name = c_an.replace('-', ' ').strip()
                            if "stergios" in norm_name.lower():
                                norm_name = "Stergios Konstantinidis"
                            elif "isna" in norm_name.lower():
                                norm_name = "Isna Alfi"
                            elif "james" in norm_name.lower() or "arnera" in norm_name.lower():
                                norm_name = "James Arnéra"
                            collab_commits.append((c_hash, norm_name, c_ae))
                            if norm_name and norm_name not in collab_authors:
                                collab_authors.append(norm_name)

            has_collab = bool(collab_commits)
            has_local = bool(local_commits) or is_dirty

            if collab_authors:
                is_collab = True
                author_name = ", ".join(collab_authors)
                print(f"👥 [Auteur Collaborateur Détecté] {len(collab_commits)} commit(s) de {author_name} identifiés depuis la baseline {effective_git_baseline[:8]}")
            else:
                author_name = "Henri Jamet"

            if local_commits:
                print(f"👤 [Auteur Local Détecté] {len(local_commits)} commit(s) d'Henri Jamet identifiés depuis la baseline {effective_git_baseline[:8]}")

            # Cas 3 états : modifications collaboratives ET modifications locales d'Henri (commits ou working tree)
            if has_collab and has_local:
                try:
                    res_head = subprocess.run(
                        ["git", "-C", str(repo_dir), "show", f"HEAD:{rel_file}"],
                        capture_output=True, check=True
                    )
                    raw_head = res_head.stdout.decode('utf-8', errors='replace')
                    if not is_markdown:
                        scratch_dir = Path.home() / "Documents" / "VoiceNotes" / "antigravity" / "scratch"
                        scratch_dir.mkdir(parents=True, exist_ok=True)
                        tmp_head_tex = scratch_dir / f"_head_{input_path.name}"
                        tmp_head_tex.write_text(raw_head, encoding="utf-8")
                        head_converter = LatexToMarkdownConverter(
                            tmp_head_tex,
                            bib_parser=bib_parser if not is_markdown else None,
                            base_dir=input_path.parent
                        )
                        head_content = head_converter.convert()
                    else:
                        head_content = raw_head
                    print(f"📦 [Git 3-State Diff Partitionné] Version Git HEAD ({author_name}) extraite ({len(raw_head)} car) pour concilier réécritures locales d'Henri (VERT/ROUGE) et collaboratives (BLEU/AMBRE)")
                except Exception as e_c:
                    print(f"⚠️ [Git 3-State Diff] Impossible d'extraire la version HEAD: {e_c}")
                    head_content = None
            elif not has_collab and has_local:
                is_collab = False
                author_name = "Henri Jamet"
                head_content = None
        except Exception as e_collab:
            print(f"⚠️ [Auteur Détection] Erreur détection: {e_collab}")

    first_img = getattr(converter, "first_image_rel", None) if not is_markdown else None
    obsidian_content, brain_template, stats = ArtifactDiffManager.merge_and_update(
        target_path=output_path,
        new_markdown=converted_md,
        baseline_content=baseline_content,
        input_path=input_path,
        repo_dir=repo_dir,
        baseline_commit=effective_git_baseline,
        first_image_rel=first_img,
        enable_ai=True,
        compliance_threshold=0.10,
        explanation=diff_explanation,
        is_collab=is_collab,
        author_name=author_name,
        head_text=head_content
    )

    # 5. Synchronisation miroir vers les dossiers brain d'Antigravity actifs (avec diffs, badges IA et images locales)
    brain_base = Path.home() / ".gemini" / "antigravity" / "brain"
    brain_targets = [
        brain_base / "a9342599-ac17-47d7-8470-7c5417190232",
        brain_base / "2bcc6f11-231b-4849-8a42-77a59f46763a",
        brain_base / "ca8e302c-8fa3-4cb0-90aa-cdae42831078",
        brain_base / "609e421e-58fc-4531-8cda-99faf485e7d5",
        brain_base / "0f784e7c-2a27-43b2-a6ed-145b1f79668c",
        brain_base / "c660c635-396c-43e2-b2a2-a93e44eda43e",
    ]
    if getattr(args, "brain_dir", None):
        brain_targets.insert(0, Path(args.brain_dir))
    if brain_base.exists():
        recent_brains = sorted(
            [d for d in brain_base.iterdir() if d.is_dir() and not d.name.startswith('.')],
            key=lambda d: d.stat().st_mtime,
            reverse=True
        )[:10]
        for rb in recent_brains:
            if rb not in brain_targets:
                brain_targets.append(rb)

    slug = output_path.stem
    vault_candidates = [
        Path.home() / "Documents" / "VoiceNotes",
        Path(r"C:\Users\Jamet\Documents\VoiceNotes"),
        Path(r"C:\Users\hjamet\Documents\VoiceNotes"),
    ]
    vault_dir = next((v for v in vault_candidates if v.exists()), None)

    for b_target in brain_targets:
        if b_target.exists() and b_target.is_dir():
            b_artifact = b_target / output_path.name
            brain_content = format_images_for_brain(
                markdown_text=brain_template,
                brain_target=b_target,
                slug=slug,
                vault_dir=vault_dir,
                repo_dir=repo_dir,
                input_path=input_path
            )
            try:
                b_artifact.write_text(brain_content, encoding="utf-8")
                print(f"🧠 [Brain Artifact Sync] Note miroir synchronisée dans : {b_artifact}")
            except Exception as be:
                print(f"⚠️ [Brain Artifact Sync] Erreur écriture {b_artifact}: {be}")

    print("\n" + "=" * 70)
    print("✅ CONVERSION & SYNCHRONISATION TERMINÉES AVEC SUCCÈS")
    print(f"📄 Note miroir générée : {output_path}")
    print(f"📊 Statistiques :")
    print(f"   - Nouveau fichier : {stats['is_new']}")
    print(f"   - Lignes de diff détectées : {stats['diff_count']}")
    print(f"   - Sections modifiées : {len(stats['modified_sections'])}")
    if not is_markdown:
        print(f"   - Citations résolues : {cited_keys_count}")
    if stats.get("has_explanation"):
        print("   - Conciliation collaborative : Callout injecté avec succès ✅")
    if stats.get("ai_scored_count", 0) > 0:
        print(f"   - Badges de score IA générés : {stats.get('ai_scored_count', 0)}")
    print("=" * 70)

    if stats.get("ai_scored_count", 0) > 0:
        failing = stats.get("failing_ai_paragraphs", [])
        print_ai_compliance_report(failing, stats["ai_scored_count"])


if __name__ == "__main__":
    main()
