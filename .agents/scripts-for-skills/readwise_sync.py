#!/usr/bin/env python3
"""
readwise_sync.py — Synchronisation locale de documents et surlignages vers Readwise & Reader.

Comportement nominal :
1. Convertit le Markdown local en HTML propre.
2. Téléverse le document dans Reader API v3 (POST /api/v3/save/) avec URL synthétique déterministe.
3. Crée le surlignage ancré dans Reader v3 (POST /api/v3/save/ avec parent_id et content).
4. Synchronise le surlignage dans Readwise v2 (POST /api/v2/highlights/).
5. Échoue immédiatement (Fail-Fast) avec une exception explicite en cas d'erreur.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import markdown
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_readwise_token() -> str:
    """Récupère le jeton Readwise depuis l'environnement ou les configurations locales."""
    # 1. Variable d'environnement
    token = os.environ.get("READWISE_TOKEN") or os.environ.get("READWISE_ACCESS_TOKEN")
    if token and token.strip():
        return token.strip()

    # 2. Plugin Obsidian Readwise Official
    obsidian_data = Path(r"C:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\readwise-official\data.json")
    if obsidian_data.exists():
        with open(obsidian_data, "r", encoding="utf-8") as f:
            data = json.load(f)
            t = data.get("token")
            if t and isinstance(t, str) and t.strip():
                return t.strip()

    # 3. Dossier utilisateur standard ~/.config/readwise/token
    config_token = Path.home() / ".config" / "readwise" / "token"
    if config_token.exists():
        t = config_token.read_text(encoding="utf-8").strip()
        if t:
            return t

    raise RuntimeError(
        "Jeton Readwise introuvable. Configurez READWISE_TOKEN ou vérifiez "
        "C:\\Users\\hjamet\\Documents\\VoiceNotes\\.obsidian\\plugins\\readwise-official\\data.json"
    )


def build_headers(token: str) -> dict:
    return {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }


def make_synthetic_url(file_path: Path, title: str) -> str:
    """Génère une URL synthétique déterministe pour dédoublonnage dans Reader."""
    norm_name = re.sub(r"[^a-zA-Z0-9_\-]+", "-", file_path.stem.lower()).strip("-")
    content_hash = hashlib.sha256(file_path.as_posix().encode("utf-8")).hexdigest()[:8]
    return f"https://obsidian.local/{norm_name}-{content_hash}"


def extract_title(content: str, file_path: Path) -> str:
    for line in content.splitlines():
        line_s = line.strip()
        if line_s.startswith("# "):
            return line_s[2:].strip()
    return file_path.stem


def clean_highlight_text(raw_text: str) -> tuple[str, bool]:
    """Nettoie le texte d'un surlignage issu d'une ligne Markdown."""
    cleaned = raw_text.strip()
    is_heading = False
    if cleaned.startswith("#"):
        is_heading = True
        cleaned = re.sub(r"^#+\s*", "", cleaned).strip()
    elif cleaned.startswith("- ") or cleaned.startswith("* "):
        cleaned = cleaned[2:].strip()
    return cleaned, is_heading


def upload_document(
    file_path: Path,
    token: str,
    title: str | None = None,
    author: str = "Henri Jamet",
    tags: list[str] | None = None,
    synthetic_url: str | None = None,
) -> tuple[str, str, int, str]:
    """
    Téléverse le document dans Reader API v3 (POST /api/v3/save/).
    Retourne (doc_id, reader_url, http_status, synthetic_url).
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    doc_title = title.strip() if title else extract_title(raw_text, file_path)
    url = synthetic_url or make_synthetic_url(file_path, doc_title)
    html_content = markdown.markdown(raw_text, extensions=["tables", "fenced_code"])

    payload = {
        "url": url,
        "html": html_content,
        "title": doc_title,
        "author": author,
        "should_clean_html": False,
        "tags": tags or [],
    }

    resp = requests.post(
        "https://readwise.io/api/v3/save/",
        headers=build_headers(token),
        json=payload,
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Échec de l'upload du document dans Reader (HTTP {resp.status_code}): {resp.text}"
        )

    data = resp.json()
    doc_id = data.get("id")
    reader_url = data.get("url")
    if not doc_id:
        raise ValueError(f"Réponse API Reader invalide (aucun champ 'id'): {resp.text}")

    return doc_id, reader_url or f"https://read.readwise.io/read/{doc_id}", resp.status_code, url


def create_highlight_reader_v3(
    doc_id: str,
    highlight_text: str,
    token: str,
    tags: list[str] | None = None,
    note: str | None = None,
) -> tuple[str, str, int]:
    """
    Crée un surlignage ancré dans le document Reader (POST /api/v3/save/ avec parent_id).
    Retourne (highlight_id, highlight_url, http_status).
    """
    payload = {
        "parent_id": doc_id,
        "content": highlight_text,
    }
    if note and note.strip():
        payload["notes"] = note.strip()
    if tags:
        payload["tags"] = tags

    resp = requests.post(
        "https://readwise.io/api/v3/save/",
        headers=build_headers(token),
        json=payload,
        timeout=30,
    )
    if resp.status_code != 201:
        raise RuntimeError(
            f"Échec de création du surlignage dans Reader v3 (HTTP {resp.status_code}): {resp.text}"
        )

    data = resp.json()
    hid = data.get("id")
    hurl = data.get("url") or f"https://read.readwise.io/read/{hid}"
    return hid, hurl, resp.status_code


def cmd_save(args: argparse.Namespace) -> None:
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier cible introuvable : {file_path}")

    raw_text = file_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    # Détermination du texte du surlignage
    if args.line is not None:
        line_idx = args.line - 1
        if line_idx < 0 or line_idx >= len(lines):
            raise IndexError(
                f"Ligne {args.line} hors limites (le document compte {len(lines)} lignes)"
            )
        raw_highlight = lines[line_idx]
    elif args.highlight:
        raw_highlight = args.highlight
    else:
        raise ValueError("Spécifiez soit --line <N> soit --highlight '<texte>'")

    clean_text, is_heading = clean_highlight_text(raw_highlight)
    if not clean_text:
        raise ValueError(f"Le texte extrait de la ligne {args.line} est vide")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    token = get_readwise_token()

    doc_title = args.title.strip() if args.title else extract_title(raw_text, file_path)

    # 1. Upload dans Reader v3
    doc_id, doc_reader_url, doc_status, synthetic_url = upload_document(
        file_path=file_path,
        token=token,
        title=doc_title,
        author=args.author,
        tags=tags,
    )

    # 2. Création du highlight ancré dans Reader v3 (synchronisé nativement vers Readwise)
    h_reader_id, h_reader_url, h_reader_status = create_highlight_reader_v3(
        doc_id=doc_id,
        highlight_text=clean_text,
        token=token,
        tags=tags,
        note=args.note,
    )

    result = {
        "status": "success",
        "file": str(file_path),
        "is_heading": is_heading,
        "highlight_text": clean_text,
        "document": {
            "id": doc_id,
            "title": doc_title,
            "url": doc_reader_url,
            "synthetic_url": synthetic_url,
            "http_status": doc_status,
        },
        "highlight_reader": {
            "id": h_reader_id,
            "url": h_reader_url,
            "http_status": h_reader_status,
        },
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"✅ Document téléversé dans Reader (HTTP {doc_status}) : {doc_reader_url}")
        if is_heading:
            print(f"ℹ️ Le surlignage correspond à un titre Markdown (préfixe retiré pour ancrage) : « {clean_text} »")
        print(f"✅ Surlignage ancré dans Reader (HTTP {h_reader_status}) : {h_reader_url} (ID: {h_reader_id})")
        print("ℹ️ Synchronisation native de Reader vers le hub Readwise active (zéro doublon).")


def cmd_list(args: argparse.Namespace) -> None:
    token = get_readwise_token()
    params = {"location": args.location, "limit": args.limit}
    resp = requests.get(
        "https://readwise.io/api/v3/list/",
        headers=build_headers(token),
        params=params,
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Échec de listing Reader (HTTP {resp.status_code}): {resp.text}")
    data = resp.json()
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        results = data.get("results", [])
        print(f"📚 Documents dans '{args.location}' ({len(results)} trouvés) :")
        for item in results:
            print(f"- [{item.get('id')}] {item.get('title') or '(Sans titre)'} -> {item.get('url')}")


def cmd_search(args: argparse.Namespace) -> None:
    token = get_readwise_token()
    params = {"page_size": args.limit}
    resp = requests.get(
        "https://readwise.io/api/v2/highlights/",
        headers=build_headers(token),
        params=params,
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Échec de recherche Readwise (HTTP {resp.status_code}): {resp.text}")
    data = resp.json()
    q = args.query.lower()
    results = [
        h for h in data.get("results", [])
        if q in (h.get("text") or "").lower() or q in (h.get("title") or "").lower()
    ]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"🔍 Surlignages contenant '{args.query}' ({len(results)} trouvés) :")
        for h in results:
            print(f"- « {h.get('text')} » (dans {h.get('title')})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronisation pérenne de documents et surlignages vers Readwise/Reader."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Commande save (défaut)
    save_parser = subparsers.add_parser("save", help="Sauvegarder un document et son surlignage")
    save_parser.add_argument("--file", "-f", required=True, help="Chemin du fichier Markdown")
    save_parser.add_argument("--line", "-l", type=int, help="Numéro de ligne (1-indexé) du surlignage")
    save_parser.add_argument("--highlight", "-H", help="Texte exact du surlignage")
    save_parser.add_argument("--title", "-t", help="Titre explicite du document")
    save_parser.add_argument("--author", "-a", default="Henri Jamet", help="Auteur du document")
    save_parser.add_argument("--tags", help="Tags séparés par des virgules (ex: ecir,recherche)")
    save_parser.add_argument("--note", "-n", help="Note attachée au surlignage")
    save_parser.add_argument("--json", action="store_true", help="Sortie brute JSON")

    # Commande list
    list_parser = subparsers.add_parser("list", help="Lister les documents récents dans Reader")
    list_parser.add_argument("--location", default="new", choices=["new", "later", "archive", "shortlist", "feed"], help="Emplacement dans Reader")
    list_parser.add_argument("--limit", type=int, default=10, help="Nombre maximal de documents")
    list_parser.add_argument("--json", action="store_true", help="Sortie JSON")

    # Commande search
    search_parser = subparsers.add_parser("search", help="Rechercher des surlignages")
    search_parser.add_argument("--query", "-q", required=True, help="Terme de recherche")
    search_parser.add_argument("--limit", type=int, default=50, help="Nombre de surlignages inspectés")
    search_parser.add_argument("--json", action="store_true", help="Sortie JSON")

    args = parser.parse_args()
    if args.command == "save":
        cmd_save(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "search":
        cmd_search(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
