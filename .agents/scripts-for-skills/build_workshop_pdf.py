#!/usr/bin/env python3
"""
build_workshop_pdf.py — Moteur de conversion Markdown -> LaTeX -> PDF pour les ateliers AIB (HEC Lausanne).

Conçu selon des critères stricts :
1. Intégrité textuelle absolue (Zero Hallucination / Zero Omission)
2. Résolution native des images Obsidian (_attachments) avec détection des captions
3. Rendu élégant des Callouts Obsidian (WARNING, IMPORTANT, NOTE, TIP) en tcolorbox
4. Boîtes interactives dédiées pour les checkpoints Wooclap
5. Formatage propre des blocs de code (SQL, Text) avec coloration syntaxique
6. Checklists de validation avec cases à cocher $\\square$ / $\\boxtimes$
7. Typographie institutionnelle HEC Lausanne (A4, fancyhdr, palette bleu nuit / ardoise)
8. Compilation multi-passes (xelatex / pdflatex) et packaging Moodle (PDF + assets + ZIP).
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration & Constantes
# ---------------------------------------------------------------------------

DEFAULT_MARKDOWN = Path(
    r"C:\Users\hjamet\Documents\VoiceNotes\enseignements\aib2026\ateliers\A2_Activity_RAG_Socratic_SQL_Chatflow.md"
)
DEFAULT_OUTPUT_DIR = Path(
    r"C:\Users\hjamet\Documents\code\aib-material\aib-course-material\activite_2_rag\moodle_upload"
)
DEFAULT_ATTACHMENTS_DIR = Path(
    r"C:\Users\hjamet\Documents\VoiceNotes\_attachments\ateliers"
)
DEFAULT_AUX_FILES = [
    Path(r"C:\Users\hjamet\Documents\code\aib-material\aib-course-material\activite_2_rag\sales_schema.sql.txt"),
    Path(r"C:\Users\hjamet\Documents\code\aib-material\aib-course-material\activite_2_rag\sql_documentation.txt"),
    Path(r"C:\Users\hjamet\Documents\code\aib-material\aib-course-material\activite_2_rag\oceanographic_ecosystem_study.pdf"),
]


# ---------------------------------------------------------------------------
# Parser Markdown & Générateur LaTeX
# ---------------------------------------------------------------------------

class MarkdownToLatexConverter:
    def __init__(self, md_path: Path, attachments_dir: Path, engine: str = "xelatex"):
        self.md_path = md_path
        self.attachments_dir = attachments_dir
        self.engine = engine.lower()
        self.title = "Activity 2: Retrieval-Augmented Generation (RAG) & Socratic SQL Chatflow"
        self.author = "Prof. Dr. Yash Raj Shrestha & Henri Jamet"
        self.institution = "HEC Lausanne — Artificial Intelligence in Business (AIB 2026)"

    def format_inline(self, text: str) -> str:
        """
        Formate une ligne de texte Markdown inline en LaTeX sécurisé :
        - Préserve les maths $...$
        - Protège le code inline `...`
        - Traite les liens [text](url)
        - Échappe les caractères réservés (&, %, _, #, ~, ^)
        - Traite le gras **...** et l'italique *...*
        """
        if not text:
            return ""

        # 1. Extraire et protéger les maths $...$
        math_tokens = []
        def math_sub(m):
            idx = len(math_tokens)
            math_tokens.append(m.group(0))
            return f"QQQMATH{idx}ZZZ"
        text = re.sub(r"\$[^$]+\$", math_sub, text)

        # 2. Extraire et protéger le code inline `...`
        code_tokens = []
        def code_sub(m):
            idx = len(code_tokens)
            c = m.group(1)
            c_esc = (
                c.replace("\\", "\\textbackslash{}")
                .replace("_", "\\_")
                .replace("&", "\\&")
                .replace("%", "\\%")
                .replace("#", "\\#")
                .replace("{", "\\{")
                .replace("}", "\\}")
                .replace("~", "\\textasciitilde{}")
                .replace("^", "\\textasciicircum{}")
            )
            code_tokens.append(f"\\texttt{{{c_esc}}}")
            return f"QQQCODE{idx}ZZZ"
        text = re.sub(r"`([^`]+)`", code_sub, text)

        # 3. Extraire et formater les liens [text](url)
        link_tokens = []
        def link_sub(m):
            idx = len(link_tokens)
            link_text = m.group(1)
            url = m.group(2)
            # Échapper les caractères dans le texte du lien
            lt_esc = self.escape_special_chars(link_text)
            lt_esc = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", lt_esc)
            lt_esc = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", lt_esc)
            link_tokens.append(f"\\href{{{url}}}{{{lt_esc}}}")
            return f"QQQLINK{idx}ZZZ"
        text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", link_sub, text)

        # 4. Échapper les caractères réservés LaTeX sur le texte normal
        text = self.escape_special_chars(text)

        # 5. Convertir le gras **text** et l'italique *text*
        text = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", text)
        text = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", text)

        # 6. Remplacer les emojis pour pdflatex si nécessaire
        if self.engine == "pdflatex":
            text = text.replace("📊", "[Wooclap]")
            text = text.replace("💡", "[Tip]")
            text = text.replace("👉", "->")

        # 7. Restaurer les tokens
        for idx, tok in enumerate(link_tokens):
            text = text.replace(f"QQQLINK{idx}ZZZ", tok)
        for idx, tok in enumerate(code_tokens):
            text = text.replace(f"QQQCODE{idx}ZZZ", tok)
        for idx, tok in enumerate(math_tokens):
            text = text.replace(f"QQQMATH{idx}ZZZ", tok)

        return text

    def escape_special_chars(self, text: str) -> str:
        """Échappe les caractères réservés LaTeX (&, %, #, _, ~, ^)."""
        special = [
            ("&", "\\&"),
            ("%", "\\%"),
            ("#", "\\#"),
            ("_", "\\_"),
            ("~", "\\textasciitilde{}"),
            ("^", "\\textasciicircum{}"),
        ]
        for ch, repl in special:
            text = text.replace(ch, repl)
        return text

    def build_preamble(self) -> str:
        """Génère le préambule LaTeX complet et stylisé."""
        font_setup = ""
        if self.engine == "xelatex":
            font_setup = r"""
\usepackage{fontspec}
\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}[Scale=0.9]
"""
        else:
            font_setup = r"""
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
"""

        return rf"""\documentclass[10pt,a4paper]{{article}}

{font_setup}

\usepackage[left=2cm,right=2cm,top=2.5cm,bottom=2.5cm,headheight=14pt]{{geometry}}
\usepackage{{xcolor}}
\usepackage[most,skins,breakable]{{tcolorbox}}
\usepackage{{listings}}
\usepackage{{graphicx}}
\usepackage{{caption}}
\usepackage{{float}}
\usepackage{{amssymb}}
\usepackage{{enumitem}}
\usepackage{{fancyhdr}}
\usepackage{{titlesec}}
\usepackage{{lastpage}}
\usepackage{{microtype}}
\usepackage{{needspace}}
\usepackage{{hyperref}}

% ---------------------------------------------------------------------------
% Palette de Couleurs Professionnelle (HEC Lausanne / AIB 2026)
% ---------------------------------------------------------------------------
\definecolor{{primary}}{{RGB}}{{20, 45, 85}}       % Deep Navy Blue
\definecolor{{secondary}}{{RGB}}{{43, 108, 176}}   % Academic Slate Blue
\definecolor{{accent}}{{RGB}}{{14, 116, 144}}      % Cyan Deep
\definecolor{{textdark}}{{RGB}}{{30, 41, 59}}      % Slate 800
\definecolor{{textgray}}{{RGB}}{{100, 116, 139}}   % Slate 500

% Callout Borders & Backgrounds (High Contrast HEC Palette)
\definecolor{{warningborder}}{{RGB}}{{180, 83, 9}}    % Deep Amber (Dark Ochre)
\definecolor{{warningbg}}{{RGB}}{{255, 251, 235}}      % Amber 50
\definecolor{{importantborder}}{{RGB}}{{153, 27, 27}}  % Deep Burgundy / Red 800
\definecolor{{importantbg}}{{RGB}}{{254, 242, 242}}    % Red 50
\definecolor{{noteborder}}{{RGB}}{{29, 78, 216}}       % Deep Royal / Navy Blue
\definecolor{{notebg}}{{RGB}}{{239, 246, 255}}         % Blue 50
\definecolor{{tipborder}}{{RGB}}{{4, 120, 87}}         % Forest Green / Emerald 800
\definecolor{{tipbg}}{{RGB}}{{236, 253, 245}}          % Emerald 50

% Wooclap & Milestones
\definecolor{{wooclapborder}}{{RGB}}{{92, 103, 242}}   % Wooclap Purple #5C67F2
\definecolor{{wooclapbg}}{{RGB}}{{245, 246, 255}}      % Light Purple Tint
\definecolor{{milestoneborder}}{{RGB}}{{67, 56, 202}}  % Indigo 700
\definecolor{{milestonebg}}{{RGB}}{{245, 247, 255}}     % Indigo 50

% Code
\definecolor{{codebg}}{{RGB}}{{248, 250, 252}}         % Slate 50
\definecolor{{codeborder}}{{RGB}}{{203, 213, 225}}     % Slate 300
\definecolor{{kwcolor}}{{RGB}}{{30, 64, 175}}          % Blue 800
\definecolor{{commentcolor}}{{RGB}}{{100, 116, 139}}   % Slate 500
\definecolor{{strcolor}}{{RGB}}{{180, 83, 9}}          % Amber 700

% ---------------------------------------------------------------------------
% Configuration des Hyperliens
% ---------------------------------------------------------------------------
\hypersetup{{
    colorlinks=true,
    linkcolor=primary,
    filecolor=secondary,
    urlcolor=secondary,
    pdftitle={{{self.title}}},
    pdfauthor={{{self.author}}},
    pdfsubject={{Artificial Intelligence in Business (AIB 2026)}},
    pdfkeywords={{RAG, Dify Cloud, Google AI Studio, Socratic Tutor, SQL}}
}}

% ---------------------------------------------------------------------------
% En-tête et Pied de Page (fancyhdr)
% ---------------------------------------------------------------------------
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small\color{{secondary}}\textbf{{AIB 2026}} \ \textbullet \ Activity 2: RAG \& Socratic SQL Chatflow}}
\fancyhead[R]{{\small\color{{textgray}} HEC Lausanne}}
\fancyfoot[L]{{\footnotesize\color{{textgray}} Course Instructor: Prof. Dr. Yash Raj Shrestha \& Henri Jamet}}
\fancyfoot[R]{{\footnotesize\color{{primary}}\textbf{{Page \thepage\ of \pageref*{{LastPage}}}}}}
\renewcommand{{\headrulewidth}}{{0.5pt}}
\renewcommand{{\footrulewidth}}{{0.5pt}}

% ---------------------------------------------------------------------------
% Titres de Section Stylisés
% ---------------------------------------------------------------------------
\titleformat{{\section}}
  {{\color{{primary}}\Large\bfseries}}
  {{\thesection}}
  {{0.8em}}
  {{}}
  [\vspace{{0.2em}}\color{{primary}}\titlerule]

\titleformat{{\subsection}}
  {{\color{{secondary}}\large\bfseries}}
  {{\thesubsection}}
  {{0.8em}}
  {{}}

\titleformat{{\subsubsection}}
  {{\color{{textdark}}\normalsize\bfseries}}
  {{\thesubsubsection}}
  {{0.6em}}
  {{}}

% ---------------------------------------------------------------------------
% Environnements Callouts Stylisés (tcolorbox) — High Contrast & No Pagebreak
% ---------------------------------------------------------------------------
\newtcolorbox{{warningbox}}[1][]{{
  enhanced, unbreakable,
  colback=warningbg, colframe=warningborder,
  colbacktitle=warningborder, coltitle=white, fonttitle=\bfseries\sffamily,
  arc=2.5mm, boxrule=1.2pt, left=4mm, right=4mm, top=3mm, bottom=3mm,
  title={{\textbf{{#1}}}}
}}

\newtcolorbox{{importantbox}}[1][]{{
  enhanced, unbreakable,
  colback=importantbg, colframe=importantborder,
  colbacktitle=importantborder, coltitle=white, fonttitle=\bfseries\sffamily,
  arc=2.5mm, boxrule=1.2pt, left=4mm, right=4mm, top=3mm, bottom=3mm,
  title={{\textbf{{#1}}}}
}}

\newtcolorbox{{notebox}}[1][]{{
  enhanced, unbreakable,
  colback=notebg, colframe=noteborder,
  colbacktitle=noteborder, coltitle=white, fonttitle=\bfseries\sffamily,
  arc=2.5mm, boxrule=1.2pt, left=4mm, right=4mm, top=3mm, bottom=3mm,
  title={{\textbf{{#1}}}}
}}

\newtcolorbox{{tipbox}}[1][]{{
  enhanced, unbreakable,
  colback=tipbg, colframe=tipborder,
  colbacktitle=tipborder, coltitle=white, fonttitle=\bfseries\sffamily,
  arc=2.5mm, boxrule=1.2pt, left=4mm, right=4mm, top=3mm, bottom=3mm,
  title={{\textbf{{#1}}}}
}}

\newtcolorbox{{wooclapbox}}[1][]{{
  enhanced, unbreakable,
  colback=wooclapbg, colframe=wooclapborder,
  coltitle=white, fonttitle=\bfseries\sffamily,
  attach boxed title to top left={{xshift=4mm, yshift=-2.5mm}},
  boxed title style={{colback=wooclapborder, arc=1.5mm, boxrule=0pt, left=3mm, right=3mm, top=1mm, bottom=1mm}},
  arc=2.5mm, boxrule=1.5pt, left=4mm, right=4mm, top=4.5mm, bottom=3mm,
  title={{\small\textbf{{LIVE WOOCLAP CHECKPOINT}} #1}}
}}

\newtcolorbox{{milestonebox}}[1][]{{
  enhanced, unbreakable,
  colback=milestonebg, colframe=milestoneborder,
  coltitle=white, fonttitle=\bfseries\sffamily,
  attach boxed title to top left={{xshift=4mm, yshift=-2.5mm}},
  boxed title style={{colback=milestoneborder, arc=1.5mm, boxrule=0pt, left=3mm, right=3mm, top=1mm, bottom=1mm}},
  arc=2.5mm, boxrule=1.5pt, left=4mm, right=4mm, top=4.5mm, bottom=3mm,
  title={{\small\textbf{{PEDAGOGICAL MILESTONE}} \ \textbullet \ #1}}
}}

% ---------------------------------------------------------------------------
% Configuration des Listings de Code
% ---------------------------------------------------------------------------
\lstdefinestyle{{sqlstyle}}{{
  language=SQL,
  basicstyle=\footnotesize\ttfamily,
  keywordstyle=\color{{kwcolor}}\bfseries,
  commentstyle=\color{{commentcolor}}\itshape,
  stringstyle=\color{{strcolor}},
  backgroundcolor=\color{{codebg}},
  frame=single,
  rulecolor=\color{{codeborder}},
  framesep=4pt,
  tabsize=2,
  breaklines=true,
  breakatwhitespace=false,
  showstringspaces=false
}}

\lstdefinestyle{{textstyle}}{{
  basicstyle=\footnotesize\ttfamily,
  backgroundcolor=\color{{codebg}},
  frame=single,
  rulecolor=\color{{codeborder}},
  framesep=4pt,
  tabsize=2,
  breaklines=true,
  breakatwhitespace=false,
  showstringspaces=false
}}

% ---------------------------------------------------------------------------
% Espacement des Listes (enumitem)
% ---------------------------------------------------------------------------
\setlist[itemize]{{leftmargin=1.5em, itemsep=0.2em, topsep=0.25em}}
\setlist[enumerate]{{leftmargin=1.5em, itemsep=0.2em, topsep=0.25em}}

\setlength{{\parskip}}{{0.45em}}
\setlength{{\parindent}}{{0pt}}

\begin{{document}}
"""

    def parse_markdown(self) -> str:
        """Lit la note Markdown et produit le corps du document LaTeX."""
        with open(self.md_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        body = []
        i = 0
        n = len(lines)

        # 1. Ignorer le Frontmatter YAML
        if i < n and lines[i].strip() == "---":
            i += 1
            while i < n and lines[i].strip() != "---":
                i += 1
            if i < n and lines[i].strip() == "---":
                i += 1

        while i < n and not lines[i].strip():
            i += 1

        # 2. En-tête H1 de titre du document
        if i < n and lines[i].startswith("# "):
            title_text = lines[i][2:].strip()
            title_tex = self.format_inline(title_text)
            body.append(r"""
\begin{center}
    {\Huge\bfseries\color{primary} """ + title_tex + r"""}\\[0.8em]
    {\large\color{secondary}\textbf{Artificial Intelligence in Business (AIB 2026)} \ \textbullet \ \textbf{HEC Lausanne}}\\[0.4em]
    {\small\color{textgray} Enterprise AI Architecture \& Pedagogical Governance \ \textbullet \ Prof. Dr. Yash Raj Shrestha \& Henri Jamet}\\[0.6em]
    {\footnotesize\color{textgray}\textit{Laboratory Guide \& Technical Manual --- Dify Cloud \& Google AI Studio Architecture}}
\end{center}
\vspace{0.6em}
\hrule height 1pt
\vspace{1.2em}
""")
            i += 1

        # Pile de gestion des listes imbriquées
        # Chaque élément : dict(env="itemize"|"enumerate", depth=1|2|3)
        list_stack = []

        def close_lists_to_depth(target_depth: int):
            nonlocal list_stack
            while len(list_stack) > target_depth:
                top = list_stack.pop()
                body.append(f"\\end{{{top['env']}}}\n")

        while i < n:
            raw_line = lines[i]
            stripped = raw_line.strip()

            # Ligne vide
            if not stripped:
                i += 1
                continue

            # Pacing reminder Wooclap répété
            if stripped.startswith("*(") and stripped.endswith(")*") and "wooclap.com" in stripped.lower():
                close_lists_to_depth(0)
                clean_reminder = stripped[2:-2].strip()
                reminder_tex = self.format_inline(clean_reminder)
                body.append(f"\\begin{{center}}\\small\\itshape\\color{{secondary}} {reminder_tex}\\end{{center}}\n\n")
                i += 1
                continue

            # Ligne horizontale séparatrice
            if stripped == "---":
                close_lists_to_depth(0)
                body.append("\\vspace{0.6em}\\hrule height 0.5pt\\vspace{0.6em}\n\n")
                i += 1
                continue

            # Titres de sections (H2 à H5)
            if stripped.startswith("## "):
                close_lists_to_depth(0)
                sec_title = stripped[3:].strip()
                sec_title = re.sub(r"^\d+\.\s*", "", sec_title)
                body.append(f"\\section{{{self.format_inline(sec_title)}}}\n")
                i += 1
                continue

            if stripped.startswith("### "):
                close_lists_to_depth(0)
                subsec_title = stripped[4:].strip()
                subsec_title = re.sub(r"^\d+(\.\d+)*\s*", "", subsec_title)
                body.append(f"\\subsection{{{self.format_inline(subsec_title)}}}\n")
                i += 1
                continue

            if stripped.startswith("#### "):
                close_lists_to_depth(0)
                subsubsec_title = stripped[5:].strip()
                is_starred = subsubsec_title.endswith(":")
                if is_starred:
                    body.append(f"\\subsubsection*{{{self.format_inline(subsubsec_title)}}}\n")
                else:
                    body.append(f"\\subsubsection{{{self.format_inline(subsubsec_title)}}}\n")
                i += 1
                continue

            if stripped.startswith("##### "):
                close_lists_to_depth(0)
                par_title = stripped[6:].strip()
                formatted_par_title = self.format_inline(par_title)
                body.append(f"\\par\\vspace{{0.8em}}\\noindent{{\\bfseries {formatted_par_title}}}\\par\\nopagebreak\\vspace{{0.3em}}\n")
                i += 1
                continue

            # Blocs de Code (```lang ... ```)
            if stripped.startswith("```"):
                close_lists_to_depth(0)
                lang = stripped[3:].strip().lower()
                code_lines = []
                i += 1
                while i < n and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < n and lines[i].strip().startswith("```"):
                    i += 1

                code_content = "".join(code_lines)
                style = "sqlstyle" if lang == "sql" else "textstyle"
                # Encapsulation dans une minipage avec noindent et linewidth pour garantir un alignement parfait avec la marge gauche
                body.append(f"\\noindent\\begin{{minipage}}{{\\linewidth}}\n\\begin{{lstlisting}}[style={style}]\n{code_content}\\end{{lstlisting}}\n\\end{{minipage}}\\par\\vspace{{0.8em}}\n\n")
                continue

            # Figures / Images Obsidian: ![[image.png]] ou ![alt](image.png)
            img_match = re.match(r"^!\[\[([^\]]+)\]\]", stripped) or re.match(r"^!\[([^\]]*)\]\(([^\)]+)\)", stripped)
            if img_match:
                close_lists_to_depth(0)
                img_filename = img_match.group(1).strip()
                img_basename = os.path.basename(img_filename)
                img_path = self.attachments_dir / img_basename

                if not img_path.exists():
                    print(f"[AVERTISSEMENT] Image introuvable sur disque: {img_path}")

                img_path_tex = str(img_path).replace("\\", "/")

                caption_text = ""
                if i + 1 < n and lines[i+1].strip().startswith("*") and lines[i+1].strip().endswith("*"):
                    raw_caption = lines[i+1].strip()[1:-1].strip()
                    caption_text = self.format_inline(raw_caption)
                    i += 1

                caption_latex = f"\\caption*{{{caption_text}}}\n" if caption_text else ""
                label_name = re.sub(r"[^a-zA-Z0-9_]", "_", img_basename)

                # Gestion du dimensionnement selon l'image (garde-fous anti-débordement vertical)
                if img_basename == "sql_tutor_img_06.png":
                    img_opts = "width=0.75\\linewidth,height=0.38\\textheight,keepaspectratio"
                elif img_basename == "dify_default_models_setup.png":
                    img_opts = "width=0.82\\linewidth,height=0.40\\textheight,keepaspectratio"
                else:
                    img_opts = "width=0.85\\linewidth,height=0.40\\textheight,keepaspectratio"

                body.append(rf"""\begin{{figure}}[H]
  \centering
  \includegraphics[{img_opts}]{{{img_path_tex}}}
  {caption_latex}  \label{{fig:{label_name}}}
\end{{figure}}
""")
                i += 1
                continue

            # Callouts Obsidian (> [!TYPE])
            if stripped.startswith("> [!"):
                close_lists_to_depth(0)
                m = re.match(r"^>\s*\[!([A-Z]+)\]\s*(.*)$", stripped)
                callout_type = m.group(1) if m else "NOTE"
                callout_header = m.group(2).strip()

                callout_lines = []
                i += 1
                while i < n:
                    raw_cl = lines[i]
                    cl_strip = raw_cl.strip()

                    # 1. Si la ligne marque le début d'un nouveau callout distinct, on s'arrête net !
                    if re.match(r"^>\s*\[!", cl_strip):
                        break

                    # 2. Si la ligne est vide ou est un simple > vide
                    if cl_strip == "" or cl_strip == ">":
                        if i + 1 < n:
                            next_strip = lines[i+1].strip()
                            # Si la ligne suivante ouvre un nouveau callout, on termine le callout courant
                            if re.match(r"^>\s*\[!", next_strip):
                                break
                            # Si la ligne suivante continue le bloc de citation, on conserve le saut de paragraphe interne
                            if next_strip.startswith(">"):
                                callout_lines.append("")
                                i += 1
                                continue
                            else:
                                break
                        else:
                            break

                    # 3. Ligne de citation normale
                    if raw_cl.startswith("> "):
                        callout_lines.append(raw_cl[2:].rstrip("\r\n"))
                    elif raw_cl.startswith(">"):
                        callout_lines.append(raw_cl[1:].rstrip("\r\n"))
                    else:
                        break
                    i += 1

                custom_title = callout_header
                content_start_idx = 0
                if callout_lines:
                    first_line = callout_lines[0].strip()
                    m_title_colon = re.match(r"^\*\*([^*]+)\*\*\s*:\s*(.*)$", first_line)
                    m_title_pure = re.match(r"^\*\*([^*]+)\*\*\s*$", first_line)
                    if m_title_colon:
                        if not custom_title:
                            custom_title = m_title_colon.group(1).strip()
                        rest = m_title_colon.group(2).strip()
                        if rest:
                            callout_lines[0] = rest
                        else:
                            content_start_idx = 1
                    elif m_title_pure:
                        if not custom_title:
                            custom_title = m_title_pure.group(1).strip()
                        content_start_idx = 1

                # Nettoyage des préfixes redondants dans le bandeau de titre
                if custom_title:
                    custom_title = re.sub(r"^(warning|important|note|tip)\s*:\s*", "", custom_title, flags=re.IGNORECASE).strip()

                full_callout_text = "\n".join(callout_lines[content_start_idx:])
                is_wooclap = "wooclap" in custom_title.lower() or "wooclap" in callout_header.lower() or "wooclap.com" in full_callout_text.lower()
                is_milestone = "milestone" in custom_title.lower() or "milestone" in callout_header.lower()

                if is_wooclap:
                    box_env = "wooclapbox"
                    q_match = re.search(r"\[Question\s*(\d+)\]", custom_title + " " + full_callout_text, re.IGNORECASE)
                    box_title_arg = f"[Question {q_match.group(1)}]" if q_match else ""
                elif is_milestone:
                    box_env = "milestonebox"
                    m_match = re.search(r"\[([^\]]+)\]", custom_title)
                    sub = self.format_inline(m_match.group(1).strip()) if m_match else self.format_inline(custom_title)
                    sub = re.sub(r"^(milestone\s*(checkpoint)?)\s*:\s*", "", sub, flags=re.IGNORECASE).strip()
                    box_title_arg = f"[{{{sub}}}]"
                elif callout_type == "WARNING":
                    box_env = "warningbox"
                    t_val = self.format_inline(custom_title) if custom_title else "WARNING"
                    box_title_arg = f"[{{{t_val}}}]"
                elif callout_type == "IMPORTANT":
                    box_env = "importantbox"
                    t_val = self.format_inline(custom_title) if custom_title else "IMPORTANT"
                    box_title_arg = f"[{{{t_val}}}]"
                elif callout_type == "TIP":
                    box_env = "tipbox"
                    t_val = self.format_inline(custom_title) if custom_title else "TIP"
                    box_title_arg = f"[{{{t_val}}}]"
                else:
                    box_env = "notebox"
                    t_val = self.format_inline(custom_title) if custom_title else "NOTE"
                    box_title_arg = f"[{{{t_val}}}]"

                callout_body = self.parse_list_and_text_block(callout_lines[content_start_idx:])
                body.append(f"\\begin{{{box_env}}}{box_title_arg}\n{callout_body}\\end{{{box_env}}}\n\n")
                continue

            # Détection de ligne de liste
            is_checklist, is_bullet, is_num, indent_spaces, item_text, checked, num_val = self.analyze_list_item(raw_line)

            if is_checklist or is_bullet or is_num:
                # Déterminer la profondeur cible (1, 2 ou 3)
                if indent_spaces == 0:
                    target_depth = 1
                elif indent_spaces <= 4:
                    target_depth = 2
                else:
                    target_depth = 3

                req_env = "itemize" if (is_bullet or is_checklist) else "enumerate"

                # Fermer les niveaux en excès
                close_lists_to_depth(target_depth)

                # Ouvrir les niveaux manquants un par un
                while len(list_stack) < target_depth:
                    # Si c'est le niveau cible, on utilise req_env, sinon itemize par défaut
                    env_to_open = req_env if len(list_stack) == target_depth - 1 else "itemize"
                    body.append(f"\\begin{{{env_to_open}}}\n")
                    list_stack.append({"env": env_to_open, "depth": len(list_stack) + 1})

                # Si le niveau actuel a un type différent de l'attendu, on l'ajuste
                if list_stack and list_stack[-1]["env"] != req_env:
                    old = list_stack.pop()
                    body.append(f"\\end{{{old['env']}}}\n\\begin{{{req_env}}}\n")
                    list_stack.append({"env": req_env, "depth": len(list_stack) + 1})

                # Écriture de l'item
                if is_checklist:
                    box_sym = r"$\boxtimes$" if checked else r"$\square$"
                    body.append(f"\\item[{box_sym}] {self.format_inline(item_text)}\n")
                elif is_num and num_val is not None:
                    # Détection si l'item introduit directement un bloc de code
                    need_protection = False
                    if i + 1 < n:
                        next_idx = i + 1
                        while next_idx < n and not lines[next_idx].strip():
                            next_idx += 1
                        if next_idx < n and lines[next_idx].strip().startswith("```"):
                            need_protection = True

                    if need_protection:
                        body.append(f"\\needspace{{7cm}}\n")

                    counter_name = "enumi" if target_depth == 1 else ("enumii" if target_depth == 2 else "enumiii")
                    body.append(f"\\setcounter{{{counter_name}}}{{{num_val - 1}}}\n")
                    body.append(f"\\item {self.format_inline(item_text)}\n")
                else:
                    body.append(f"\\item {self.format_inline(item_text)}\n")

                i += 1
                continue

            # Ligne indentée de continuation dans une liste active
            leading_spaces = len(raw_line) - len(raw_line.lstrip(" "))
            if list_stack and leading_spaces >= 3:
                # C'est une continuation de l'item précédent
                body.append(f"\\par {self.format_inline(stripped)}\n")
                i += 1
                continue

            # Paragraphe normal non indenté
            close_lists_to_depth(0)
            body.append(f"{self.format_inline(stripped)}\n\n")
            i += 1

        close_lists_to_depth(0)
        body.append("\\end{document}\n")

        return self.build_preamble() + "\n".join(body)

    def analyze_list_item(self, line: str):
        """Détecte si une ligne est un élément de liste, calcule son indentation et extrait son contenu."""
        leading_spaces = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        # Checklist: - [ ] ou - [x]
        m_check = re.match(r"^-\s*\[([ xX])\]\s*(.*)$", stripped)
        if m_check:
            checked = m_check.group(1).lower() == "x"
            return True, False, False, leading_spaces, m_check.group(2).strip(), checked, None

        # Bullet ordinaire: - text ou * text
        m_bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        if m_bullet:
            return False, True, False, leading_spaces, m_bullet.group(1).strip(), False, None

        # Numéroté: 1. text
        m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m_num:
            return False, False, True, leading_spaces, m_num.group(2).strip(), False, int(m_num.group(1))

        return False, False, False, leading_spaces, stripped, False, None

    def parse_list_and_text_block(self, lines: list) -> str:
        """Parse un bloc de lignes pouvant contenir du texte et des listes (pour l'intérieur des callouts)."""
        res = []
        list_stack = []

        def close_sublists(target_depth: int):
            nonlocal list_stack
            while len(list_stack) > target_depth:
                top = list_stack.pop()
                res.append(f"\\end{{{top['env']}}}\n")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            is_checklist, is_bullet, is_num, indent_spaces, item_text, checked, num_val = self.analyze_list_item(line)

            if is_checklist or is_bullet or is_num:
                target_depth = 1 if indent_spaces <= 2 else 2
                req_env = "itemize" if (is_bullet or is_checklist) else "enumerate"

                close_sublists(target_depth)

                while len(list_stack) < target_depth:
                    env_to_open = req_env if len(list_stack) == target_depth - 1 else "itemize"
                    res.append(f"\\begin{{{env_to_open}}}\n")
                    list_stack.append({"env": env_to_open, "depth": len(list_stack) + 1})

                if list_stack and list_stack[-1]["env"] != req_env:
                    old = list_stack.pop()
                    res.append(f"\\end{{{old['env']}}}\n\\begin{{{req_env}}}\n")
                    list_stack.append({"env": req_env, "depth": len(list_stack) + 1})

                if is_checklist:
                    box_sym = r"$\boxtimes$" if checked else r"$\square$"
                    res.append(f"\\item[{box_sym}] {self.format_inline(item_text)}\n")
                elif is_num and num_val is not None:
                    counter_name = "enumi" if target_depth == 1 else "enumii"
                    res.append(f"\\setcounter{{{counter_name}}}{{{num_val - 1}}}\n")
                    res.append(f"\\item {self.format_inline(item_text)}\n")
                else:
                    res.append(f"\\item {self.format_inline(item_text)}\n")
                continue

            leading_spaces = len(line) - len(line.lstrip(" "))
            if list_stack and leading_spaces >= 3:
                res.append(f"\\par {self.format_inline(stripped)}\n")
                continue

            close_sublists(0)
            res.append(f"{self.format_inline(stripped)}\n\n")

        close_sublists(0)
        return "".join(res)


# ---------------------------------------------------------------------------
# Pipeline d'Exécution & Packaging Moodle
# ---------------------------------------------------------------------------

def compile_latex(tex_file: Path, engine: str = "xelatex", passes: int = 3) -> bool:
    """Compile le document LaTeX en PDF avec plusieurs passes pour stabiliser la numérotation."""
    workdir = tex_file.parent
    cmd = [engine, "-interaction=nonstopmode", tex_file.name]

    print(f"[*] Compilation LaTeX avec {engine} ({passes} passes)...")
    for p in range(1, passes + 1):
        print(f"  -> Passe {p}/{passes}...")
        res = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            print(f"[ERREUR] Échec de la passe {p} ({engine} code {res.returncode})")
            log_lines = res.stdout.splitlines()
            errors = [line for line in log_lines if line.startswith("!") or "Error:" in line]
            print("\n".join(errors[:10]))
            return False

    pdf_file = tex_file.with_suffix(".pdf")
    if pdf_file.exists():
        print(f"[SUCCÈS] PDF généré : {pdf_file.name} ({pdf_file.stat().st_size:,} octets)")
        return True
    else:
        print("[ERREUR] Le fichier PDF n'a pas été produit.")
        return False


def build_package(
    md_input: Path,
    output_dir: Path,
    attachments_dir: Path,
    engine: str = "xelatex",
    aux_files: list = None,
    keep_tex: bool = True,
    create_zip: bool = True,
) -> dict:
    """Orchestre la conversion complète, la compilation et la préparation du package Moodle."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tex_file = output_dir / f"{md_input.stem}.tex"
    pdf_file = output_dir / f"{md_input.stem}.pdf"

    print(f"[*] Lecture de la note Markdown : {md_input}")
    converter = MarkdownToLatexConverter(md_input, attachments_dir, engine=engine)
    tex_content = converter.parse_markdown()

    print(f"[*] Écriture du fichier LaTeX : {tex_file}")
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(tex_content)

    # Compilation multi-passes
    success = compile_latex(tex_file, engine=engine, passes=3)
    if not success:
        return {"status": "error", "message": "Échec de compilation LaTeX"}

    # Copie des fichiers annexes dans le dossier Moodle
    copied_aux = []
    if aux_files:
        for src in aux_files:
            if src.exists():
                dst = output_dir / src.name
                shutil.copy2(src, dst)
                copied_aux.append(dst)
                print(f"[*] Fichier annexe copié : {dst.name} ({dst.stat().st_size:,} octets)")
            else:
                print(f"[ATTENTION] Fichier annexe introuvable : {src}")

    # Création du package ZIP pour les étudiants
    zip_path = None
    if create_zip:
        zip_path = output_dir / "A2_Package_Moodle_Etudiants.zip"
        print(f"[*] Création de l'archive ZIP Moodle : {zip_path.name}")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if pdf_file.exists():
                zf.write(pdf_file, arcname=pdf_file.name)
            for f in copied_aux:
                zf.write(f, arcname=f.name)
        print(f"[SUCCÈS] Archive ZIP créée : {zip_path.name} ({zip_path.stat().st_size:,} octets)")

    # Nettoyage des fichiers temporaires TeX si souhaité
    if not keep_tex:
        for ext in [".aux", ".log", ".out", ".toc", ".tex"]:
            tmp_f = output_dir / f"{md_input.stem}{ext}"
            if tmp_f.exists():
                tmp_f.unlink()

    return {
        "status": "success",
        "pdf_path": str(pdf_file),
        "pdf_size": pdf_file.stat().st_size,
        "zip_path": str(zip_path) if zip_path else None,
        "copied_aux": [str(f) for f in copied_aux],
        "tex_path": str(tex_file),
    }


def main():
    parser = argparse.ArgumentParser(description="Convertisseur Obsidian Markdown -> PDF pour Ateliers AIB")
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_MARKDOWN, help="Fichier Markdown source")
    parser.add_argument("--output-dir", "-o", type=Path, default=DEFAULT_OUTPUT_DIR, help="Dossier de sortie")
    parser.add_argument("--attachments-dir", "-a", type=Path, default=DEFAULT_ATTACHMENTS_DIR, help="Dossier des images")
    parser.add_argument("--engine", "-e", choices=["xelatex", "pdflatex"], default="xelatex", help="Moteur LaTeX")
    parser.add_argument("--no-zip", action="store_true", help="Ne pas générer d'archive ZIP")
    parser.add_argument("--clean", action="store_true", help="Supprimer les fichiers .tex et auxiliaires")

    args = parser.parse_args()

    res = build_package(
        md_input=args.input,
        output_dir=args.output_dir,
        attachments_dir=args.attachments_dir,
        engine=args.engine,
        aux_files=DEFAULT_AUX_FILES,
        keep_tex=not args.clean,
        create_zip=not args.no_zip,
    )

    if res["status"] == "success":
        print("\n=== RAPPORT DE LIVRAISON MOODLE ATELIER A2 ===")
        print(f"PDF généré     : {res['pdf_path']} ({res['pdf_size']:,} octets)")
        if res.get("zip_path"):
            print(f"Archive ZIP    : {res['zip_path']}")
        print("Fichiers Moodle prêts au déploiement.")
    else:
        print(f"\n[ÉCHEC] {res.get('message')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
