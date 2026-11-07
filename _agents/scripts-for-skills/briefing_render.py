"""Check that a Markdown briefing fits in N printed A4 pages (no file delivered).

Used by the `briefing` skill (_agents/skills/briefing/SKILL.md). The deliverable
is the Markdown note itself (printed by Henri from Obsidian); this script only
estimates its printed length.

Pipeline: Markdown (YAML frontmatter stripped) -> HTML with print CSS (@page A4),
Mermaid blocks rendered with mermaid.js (CDN) -> PDF via headless Chrome/Edge in
a temporary directory deleted afterwards -> page count via pypdf. Mermaid syntax
errors are detected in the rendered DOM.

Usage:
    python briefing_render.py "<briefing.md>" [--max-pages 2]

Exit codes: 0 = page count <= max; 1 = too many pages, emoji or Mermaid syntax
error; 2 = browser missing, rendering failure or Mermaid not loaded. Prints:
    OK pages=2 max=2 words=812
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown
from pypdf import PdfReader

BROWSER_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# Pictographs / emoji blocks: forbidden in briefings (print in B&W, formal tone).
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")

CSS = """
@page { size: A4; margin: 13mm 14mm 13mm 14mm; }
html { font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; color: #000; }
body { margin: 0; line-height: 1.28; }
h1 { font-size: 14pt; margin: 0 0 2pt 0; }
h1 + p { margin-top: 0; font-size: 9.5pt; }
h2 { font-size: 11pt; margin: 8pt 0 3pt 0; padding-bottom: 1pt;
     border-bottom: 0.8pt solid #000; break-after: avoid; page-break-after: avoid; }
h3 { font-size: 10pt; margin: 5pt 0 2pt 0; break-after: avoid; page-break-after: avoid; }
p, ul, ol { margin: 2pt 0 3pt 0; }
ul, ol { padding-left: 14pt; }
li { margin: 0 0 1pt 0; }
table { width: 100%; border-collapse: collapse; margin: 3pt 0 4pt 0; font-size: 9.5pt; }
thead { display: table-header-group; }
tr, li, h3 + ul { break-inside: avoid; page-break-inside: avoid; }
th, td { border: 0.6pt solid #444; padding: 2pt 4pt; vertical-align: top; text-align: left; }
th { font-weight: 700; background: #fff; border-bottom: 1.2pt solid #000; }
hr { border: 0; border-top: 0.6pt solid #444; margin: 5pt 0; }
code { font-family: Consolas, monospace; font-size: 9pt; }
.notes { min-height: 45mm; border: 0.6pt solid #444; break-inside: avoid; }
"""


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\r\n")
    return text


def find_browser() -> str:
    for candidate in BROWSER_CANDIDATES:
        if Path(candidate).is_file():
            return candidate
    raise FileNotFoundError("No Chrome/Edge executable found in: " + "; ".join(BROWSER_CANDIDATES))


MERMAID_JS = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"
MERMAID_BLOCK_RE = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.S)
MERMAID_ERROR_MARKERS = ("Syntax error in text", "Parse error")


def build_html(md_text: str, title: str) -> str:
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists", "fenced_code"])
    has_mermaid = bool(MERMAID_BLOCK_RE.search(body))
    body = MERMAID_BLOCK_RE.sub(r'<pre class="mermaid">\1</pre>', body)
    script = (
        f"<script src='{MERMAID_JS}'></script>"
        "<script>mermaid.initialize({startOnLoad:true, theme:'neutral'});</script>"
        if has_mermaid
        else ""
    )
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{CSS}</style></head><body>{body}{script}</body></html>"
    )


def run_browser(html: str, timeout_s: int) -> tuple[int, str]:
    """Print the HTML to a PDF in a temporary directory (deleted on return).

    Returns (page_count, rendered_dom). Nothing is written outside the temp dir.
    """
    browser = find_browser()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "briefing.html"
        pdf_path = Path(tmp) / "briefing.pdf"
        html_path.write_text(html, encoding="utf-8")
        base = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--virtual-time-budget=15000",
            f"--user-data-dir={Path(tmp) / 'profile'}",
        ]
        dom = subprocess.run(
            base + ["--dump-dom", html_path.as_uri()],
            check=True, timeout=timeout_s, capture_output=True, text=True, encoding="utf-8",
        ).stdout
        subprocess.run(
            base + ["--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
            check=True, timeout=timeout_s, capture_output=True,
        )
        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            raise RuntimeError("Browser exited but no PDF was written")
        pages = len(PdfReader(str(pdf_path)).pages)
    return pages, dom


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=60, help="Browser timeout in seconds")
    args = parser.parse_args()

    md_path: Path = args.markdown_file.resolve()
    md_text = strip_frontmatter(md_path.read_text(encoding="utf-8-sig"))

    emojis = sorted(set(EMOJI_RE.findall(md_text)))
    if emojis:
        print(f"FAIL emoji found: {' '.join(emojis)}")
        return 1

    html = build_html(md_text, md_path.stem)
    try:
        pages, dom = run_browser(html, args.timeout)
    except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR render failed: {exc}")
        return 2

    if "class=\"mermaid\"" in html and "<svg" not in dom:
        print("ERROR mermaid not rendered (no network access to the CDN?)")
        return 2
    if any(marker in dom for marker in MERMAID_ERROR_MARKERS):
        print("FAIL mermaid syntax error")
        return 1

    words = len(re.findall(r"\w+", md_text))
    status = "OK" if pages <= args.max_pages else "FAIL"
    print(f"{status} pages={pages} max={args.max_pages} words={words}")
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
