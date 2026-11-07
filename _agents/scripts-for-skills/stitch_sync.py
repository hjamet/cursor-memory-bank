#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stitch_sync.py — Continuous Stitch Sync Diff Engine for sci-family-app
Google Stitch MCP Synchronizer & Step-by-Step Review Iterator (One-by-One Review)

Architecture native Git :
    1. Téléchargement des maquettes Stitch dans le sanctuaire 'stitch/' (sans git add immédiat).
    2. Consultation pas-à-pas des modifications écran par écran via --next.
    3. Intégration chirurgicale dans frontend/src/ puis acquittement via --ack stitch/<fichier> (git add).
    4. Commit automatique de clôture une fois tous les écrans acquittés.
    5. Mode simulation (--dry-run) pour inspecter les deltas distants sans altérer le dépôt.

Usage canonique :
    python stitch_sync.py [--dry-run]
    python stitch_sync.py --fetch [--project <projectId>] [--dry-run]
    python stitch_sync.py --status
    python stitch_sync.py --next
    python stitch_sync.py --ack stitch/<fichier>.html
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import re
import time
import glob
import zipfile
import shutil
import argparse
import unicodedata
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

DEFAULT_PROJECT_ID = os.getenv("STITCH_PROJECT_ID", "4484682917577566744")
DEFAULT_MCP_CONFIG = os.getenv("MCP_CONFIG_PATH", r"C:\Users\hjamet\.config\mcp\mcp_servers.json")
DEFAULT_COOKIES_PATHS = [
    r"C:\Users\hjamet\.gemini\stitch_cookies.json",
    os.path.expanduser(r"~\.gemini\stitch_cookies.json"),
    os.path.expanduser(r"~\.config\mcp\stitch_cookies.json"),
]

README_SANCTUARY_WARNING = """# ⚠️ AVERTISSEMENT : SANCTUAIRE DE DESIGN STITCH BRUT

⚠️ AVERTISSEMENT : CE DOSSIER EST UN SANCTUAIRE DE DESIGN STITCH BRUT. INTERDICTION FORMELLE ET ABSOLUE POUR TOUT AGENT OU DÉVELOPPEUR DE LE MODIFIER MANUELLEMENT OU DE L'UTILISER DIRECTEMENT EN PRODUCTION (RUNTIME). IL EST EXCLUSIVEMENT ALIMENTÉ PAR STITCH_SYNC.PY ET SERT DE BASE DE DIFF VERSIONNÉE PAR GIT POUR LES MISES À JOUR.

- **Source de Vérité Design** : Google Stitch (`https://stitch.withgoogle.com`)
- **Script Alimentateur** : `stitch_sync.py` (ou `_agents/scripts-for-skills/stitch_sync.py`)
- **Règle d'Intégration** : L'agent ou le développeur consulte `git diff` sur ce dossier et reporte chirurgicalement les modifications nécessaires dans le code applicatif (`frontend/src/`, etc.) sans jamais altérer ce dossier.
"""


def slugify(text: str) -> str:
    """Génère un slug propre pour nom de fichier sans caractères spéciaux ni accents."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    slug = re.sub(r'[-\s]+', '_', text)
    return slug.strip('_') or 'screen'


def find_git_root(target_path: str = None) -> Path:
    """Détecte automatiquement la racine du dépôt git via git rev-parse --show-toplevel."""
    start_dir = target_path or os.getcwd()
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_dir,
            capture_output=True,
            text=True,
            check=True
        )
        git_root = Path(proc.stdout.strip()).resolve()
        return git_root
    except Exception as e:
        print(f"[!] Impossible de détecter la racine Git depuis '{start_dir}' : {e}", file=sys.stderr)
        return Path(start_dir).resolve()


def ensure_sanctuary_dir(repo_root: Path) -> Path:
    """Crée le dossier sanctuaire <repo_root>/stitch/ et son README.md d'avertissement."""
    stitch_dir = repo_root / "stitch"
    stitch_dir.mkdir(parents=True, exist_ok=True)

    readme_file = stitch_dir / "README.md"
    if not readme_file.exists():
        readme_file.write_text(README_SANCTUARY_WARNING, encoding="utf-8")
    return stitch_dir


def load_mcp_api_key(config_path: str = DEFAULT_MCP_CONFIG) -> str:
    """Extrait la clé X-Goog-Api-Key configurée pour Stitch MCP."""
    env_key = os.getenv("STITCH_API_KEY")
    if env_key:
        return env_key
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("mcpServers", {}).get("stitch", {}).get("headers", {}).get("X-Goog-Api-Key", "")
        except Exception:
            pass
    return ""


def load_cookie_header() -> str:
    """Charge le header Cookie Google session depuis les emplacements connus."""
    for p in DEFAULT_COOKIES_PATHS:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "cookieHeader" in data and data["cookieHeader"]:
                        return data["cookieHeader"]
            except Exception:
                pass
    return ""


def list_stitch_screens(project_id: str, config_path: str = DEFAULT_MCP_CONFIG, api_key: str = None) -> list:
    """
    Interroge Google Stitch MCP pour récupérer tous les écrans du projet.
    Essaye en premier l'endpoint direct JSON-RPC avec authentification API key,
    puis bascule sur mcp-cli si disponible.
    """
    if not api_key:
        api_key = load_mcp_api_key(config_path)

    # 1. Méthode prioritaire : Appel JSON-RPC direct vers https://stitch.googleapis.com/mcp
    if api_key:
        endpoint_url = "https://stitch.googleapis.com/mcp"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_screens",
                "arguments": {"projectId": project_id}
            }
        }
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    endpoint_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": api_key,
                        "User-Agent": "StitchSyncEngine/1.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    result = resp_data.get("result", {})
                    if result.get("isError"):
                        err_text = result.get("content", [{}])[0].get("text", "Erreur Stitch MCP")
                        print(f"    [!] Erreur Stitch MCP pour le projet '{project_id}' : {err_text}", file=sys.stderr)
                        return []
                    # Format structuredContent
                    screens = result.get("structuredContent", {}).get("screens", [])
                    if screens:
                        return screens
                    # Format text content
                    text_content = result.get("content", [{}])[0].get("text", "")
                    if text_content:
                        try:
                            parsed = json.loads(text_content)
                            return parsed.get("screens", [])
                        except Exception:
                            pass
                    if "screens" in result:
                        return result["screens"]
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_time = (attempt + 1) * 2
                    print(f"    [!] Rate limit Stitch MCP (HTTP 429). Pause {wait_time}s...", file=sys.stderr)
                    time.sleep(wait_time)
                    continue
                print(f"    [!] Erreur HTTP Stitch MCP ({e.code}) : {e.reason}", file=sys.stderr)
                break
            except Exception as e:
                print(f"    [!] Erreur connexion directe Stitch MCP : {e}", file=sys.stderr)
                break

    # 2. Méthode fallback : Appel mcp-cli (uniquement si mcp-cli disponible et pas de clé directe)
    cmd = ["mcp-cli", "--config", config_path, "call-tool", "stitch:list_screens", "--args", json.dumps({"projectId": project_id})]
    print(f"[*] Interrogation de l'API Stitch via mcp-cli pour le projet {project_id}...")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=25,
            stdin=subprocess.DEVNULL,
            shell=True
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            if data.get("isError"):
                err_text = data.get("content", [{}])[0].get("text", "")
                print(f"    [!] Erreur retournée par mcp-cli : {err_text}", file=sys.stderr)
                return []
            if "structuredContent" in data and "screens" in data["structuredContent"]:
                return data["structuredContent"]["screens"]
            raw_text = data.get("content", [{}])[0].get("text", "")
            if raw_text:
                try:
                    parsed = json.loads(raw_text)
                    return parsed.get("screens", [])
                except Exception:
                    pass
        else:
            print(f"[!] Erreur mcp-cli (code {proc.returncode}) : {proc.stderr.strip()}", file=sys.stderr)
    except Exception as e:
        print(f"[!] Erreur lors de l'appel mcp-cli list_screens : {e}", file=sys.stderr)

    return []


def download_html_direct(download_url: str, api_key: str = "", cookie_header: str = "") -> str:
    """
    Télécharge le HTML via urllib avec la clé X-Goog-Api-Key ou cookies de session.
    Note critique : Si X-Goog-Api-Key est présent, NE PAS envoyer Cookie car des cookies
    Google expirés provoquent une redirection indésirable vers accounts.google.com.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    if api_key:
        headers["X-Goog-Api-Key"] = api_key
    elif cookie_header:
        headers["Cookie"] = cookie_header

    for attempt in range(3):
        try:
            req = urllib.request.Request(download_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    raw_bytes = resp.read()
                    content = raw_bytes.decode("utf-8", errors="replace")
                    # Détection d'écran de connexion Google inattendu
                    if "<html" in content.lower() and "accounts.google.com" not in content[:500]:
                        return content
                    else:
                        print("    [!] Réponse interceptée par le portail d'authentification Google.", file=sys.stderr)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 2
                print(f"    [!] Rate limiting HTTP 429 sur le CDN Stitch. Attente de {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"    [!] Erreur HTTP direct {e.code} : {e.reason}", file=sys.stderr)
            break
        except Exception as e:
            print(f"    [!] Erreur téléchargement HTTP direct (tentative {attempt+1}/3) : {e}", file=sys.stderr)
            time.sleep(1)

    return ""


def find_matching_local_export(slug: str, title: str, downloads_dir: str = None) -> str:
    """
    Recherche un export local valide dans Downloads correspondant SPÉCIFIQUEMENT
    à cet écran (par extraction ZIP ou fichier HTML contenant le slug ou titre).
    Évite formellement d'écraser tous les écrans avec un seul fichier arbitraire.
    """
    if not downloads_dir:
        downloads_dir = os.path.expanduser(r"~\Downloads")

    # 1. Recherche dans les archives ZIP
    zips = glob.glob(os.path.join(downloads_dir, "*.zip"))
    for z in sorted(zips, key=os.path.getmtime, reverse=True):
        try:
            with zipfile.ZipFile(z, 'r') as zf:
                for name in zf.namelist():
                    norm = name.lower()
                    if norm.endswith(".html") or norm.endswith(".htm"):
                        if slug in norm or any(w in norm for w in slug.split('_') if len(w) > 4):
                            raw = zf.read(name)
                            return raw.decode("utf-8", errors="replace")
        except Exception:
            continue

    # 2. Recherche parmi les fichiers HTML nommés précisément
    for ext in ["*.html", "*.htm"]:
        for h in glob.glob(os.path.join(downloads_dir, ext)):
            base = os.path.basename(h).lower()
            if slug in base:
                try:
                    with open(h, "r", encoding="utf-8", errors="replace") as f:
                        return f.read()
                except Exception:
                    pass

    return ""


def fetch_screen_content(screen: dict, api_key: str, cookie_header: str, source_path: str = None) -> tuple:
    """
    Récupère le contenu d'un écran Stitch avec gestion des priorités et fallbacks ciblés.
    Retourne (content_str, origin_str).
    """
    title = screen.get("title") or "sans_titre"
    slug = slugify(title)
    download_url = screen.get("htmlCode", {}).get("downloadUrl", "")

    # 1. Téléchargement direct avec authentification API Key en priorité absolue
    if download_url and api_key:
        content = download_html_direct(download_url, api_key=api_key)
        if content:
            return content, "api_direct"

    # 2. Téléchargement direct avec cookies Google (si pas de clé API)
    if download_url and cookie_header:
        content = download_html_direct(download_url, cookie_header=cookie_header)
        if content:
            return content, "cookies_direct"

    # 3. Source manuelle passée en paramètre
    if source_path and os.path.exists(source_path):
        if source_path.endswith('.html') or source_path.endswith('.htm'):
            try:
                with open(source_path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(), "manual_source"
            except Exception:
                pass

    # 4. Export local ciblé dans Downloads
    matched_export = find_matching_local_export(slug, title)
    if matched_export:
        return matched_export, "downloads_matched"

    return "", "not_found"


def sync_screens(project_id: str, stitch_dir: Path, source_path: str = None, mcp_config: str = DEFAULT_MCP_CONFIG, dry_run: bool = False) -> tuple:
    """
    Synchronise ou prévisualise (--dry-run) les maquettes Stitch dans le dossier stitch/.
    Retourne (updated_screens, new_screens, identical_screens, errors).
    """
    api_key = load_mcp_api_key(mcp_config)
    cookie_header = load_cookie_header()

    print(f"[*] Interrogation du projet Stitch {project_id} (API Key: {'Oui' if api_key else 'Non'})...")
    screens = list_stitch_screens(project_id, config_path=mcp_config, api_key=api_key)

    html_screens = [
        s for s in screens
        if s.get("htmlCode", {}).get("downloadUrl")
        and s.get("htmlCode", {}).get("mimeType") == "text/html"
    ]

    print(f"[*] {len(screens)} éléments trouvés sur le projet {project_id} ({len(html_screens)} écrans HTML identifiés).")
    if not html_screens:
        return [], [], [], ["Aucun écran HTML trouvé dans le projet."]

    updated_screens = []
    new_screens = []
    identical_screens = []
    errors = []

    # Dictionnaire des fichiers locaux existants pour matcher par nom
    existing_files = {p.name: p for p in stitch_dir.glob("*.html")}
    used_filenames = set()

    for s in html_screens:
        title = s.get("title") or "sans_titre"
        slug = slugify(title)
        filename = f"{slug}.html"

        # Gérer les doublons de titres éventuels
        if filename in used_filenames:
            short_id = (s.get("name") or "").split("/")[-1][:8]
            filename = f"{slug}_{short_id}.html"
        used_filenames.add(filename)

        target_path = stitch_dir / filename
        print(f"[*] Analyse écran : « {title} » -> {filename}")

        html_content, origin = fetch_screen_content(s, api_key, cookie_header, source_path)
        if not html_content:
            print(f"    [!] Impossible de récupérer le contenu de « {title} ».", file=sys.stderr)
            errors.append(title)
            continue

        if target_path.exists():
            current_content = target_path.read_text(encoding="utf-8", errors="replace")
            if current_content == html_content:
                print(f"    [=] Identique au sanctuaire local ({len(html_content)} octets).")
                identical_screens.append({"title": title, "path": target_path, "size": len(html_content)})
            else:
                print(f"    [Δ] Modification détectée ({len(current_content)} -> {len(html_content)} octets) via {origin}.")
                updated_screens.append({"title": title, "path": target_path, "size": len(html_content), "old_size": len(current_content)})
                if not dry_run:
                    target_path.write_text(html_content, encoding="utf-8")
        else:
            print(f"    [+] Nouvel écran identifié ({len(html_content)} octets) via {origin}.")
            new_screens.append({"title": title, "path": target_path, "size": len(html_content)})
            if not dry_run:
                target_path.write_text(html_content, encoding="utf-8")

    return updated_screens, new_screens, identical_screens, errors


def get_stitch_status(repo_root: Path) -> tuple:
    """
    Analyse l'état Git des fichiers du dossier stitch/ (hors README.md).
    Retourne un tuple (staged_files, unstaged_files).
    Chaque élément est un dict: {'path': 'stitch/...', 'type': 'modifié'|'nouveau'|'supprimé'}
    """
    # 1. Stager automatiquement stitch/README.md si modifié ou non suivi pour sanctuariser l'UX
    readme_path = repo_root / "stitch" / "README.md"
    if readme_path.exists():
        proc_readme = subprocess.run(
            ["git", "status", "--porcelain=v1", "--", "stitch/README.md"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if proc_readme.stdout.strip():
            subprocess.run(["git", "add", "stitch/README.md"], cwd=repo_root, check=True)

    # 2. Statut complet de stitch/
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "-uall", "--", "stitch/"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True
    )

    staged = []
    unstaged = []

    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        status_code = line[:2]
        file_path_raw = line[3:].strip()
        if file_path_raw.startswith('"') and file_path_raw.endswith('"'):
            file_path_raw = file_path_raw[1:-1]

        norm_path = file_path_raw.replace("\\", "/")

        if norm_path.lower() == "stitch/readme.md" or norm_path.lower().endswith("/readme.md"):
            continue

        index_stat = status_code[0]
        work_stat = status_code[1]

        if status_code == "??":
            unstaged.append({"path": norm_path, "type": "nouveau"})
        else:
            if work_stat != " ":
                ctype = "modifié"
                if work_stat == "D":
                    ctype = "supprimé"
                elif work_stat == "A":
                    ctype = "nouveau"
                unstaged.append({"path": norm_path, "type": ctype})

            if index_stat in ("M", "A", "D", "R") and work_stat == " ":
                ctype = "modifié"
                if index_stat == "A":
                    ctype = "nouveau"
                elif index_stat == "D":
                    ctype = "supprimé"
                elif index_stat == "R":
                    ctype = "renommé"
                staged.append({"path": norm_path, "type": ctype})

    staged.sort(key=lambda x: x["path"])
    unstaged.sort(key=lambda x: x["path"])
    return staged, unstaged


def resolve_stitch_file(repo_root: Path, file_arg: str) -> Path:
    """Résout et valide de façon robuste le chemin d'un fichier du sanctuaire stitch/."""
    raw = file_arg.strip().replace("\\", "/")
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]

    p = Path(raw)
    if p.is_absolute() and p.exists():
        return p

    candidate1 = (repo_root / raw).resolve()
    if candidate1.exists():
        return candidate1

    candidate2 = (repo_root / "stitch" / Path(raw).name).resolve()
    if candidate2.exists():
        return candidate2

    proc = subprocess.run(
        ["git", "ls-files", "--", raw],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if proc.stdout.strip():
        return candidate1

    raise FileNotFoundError(
        f"Le fichier '{file_arg}' est introuvable dans le dossier sanctuaire {repo_root / 'stitch'}."
    )


def cmd_fetch(project_id: str, repo_root: Path, source_path: str = None, mcp_config: str = DEFAULT_MCP_CONFIG, dry_run: bool = False) -> None:
    """Télécharge les écrans Stitch et affiche la liste des écrans modifiés sans git add global."""
    print(f"[*] Racine du dépôt Git identifiée : {repo_root}")
    stitch_dir = ensure_sanctuary_dir(repo_root)
    print(f"[*] Dossier sanctuaire validé : {stitch_dir}")

    if dry_run:
        print("\n🔍 MODE DRY-RUN ACTIF : Aucune écriture disque ni modification Git ne sera appliquée.")

    updated, new, identical, errors = sync_screens(
        project_id=project_id,
        stitch_dir=stitch_dir,
        source_path=source_path,
        mcp_config=mcp_config,
        dry_run=dry_run
    )

    if dry_run:
        print("\n" + "="*70)
        print(f"📊 RAPPORT DE SIMULATION (DRY-RUN) — Projet {project_id}")
        print("="*70)
        print(f"  • {len(identical)} écran(s) déjà parfaitement synchronisé(s) et identiques")
        print(f"  • {len(updated)} écran(s) présentant des modifications distantes")
        print(f"  • {len(new)} nouvel/nouveaux écran(s) à importer")
        if errors:
            print(f"  • {len(errors)} erreur(s) d'accès / téléchargement")

        if updated:
            print("\nÉcrans à mettre à jour :")
            for item in updated:
                rel = item['path'].relative_to(repo_root).as_posix()
                print(f"  [Δ] {rel} ({item['old_size']} B -> {item['size']} B)")

        if new:
            print("\nNouveaux écrans à ajouter :")
            for item in new:
                rel = item['path'].relative_to(repo_root).as_posix()
                print(f"  [+] {rel} ({item['size']} B)")

        print("\n💡 Pour exécuter la synchronisation réelle, relancez sans '--dry-run' :")
        print(f"   python stitch_sync.py --fetch --project {project_id}")
        print("="*70)
        return

    if not updated and not new:
        if not errors:
            print(f"\n✅ Aucun changement détecté dans Stitch. Le dossier stitch/ est déjà parfaitement synchronisé ({len(identical)} écrans vérifiés).")
        else:
            print(f"\n⚠️ Synchronisation partielle : {len(errors)} écran(s) en erreur.")
        return

    staged, unstaged = get_stitch_status(repo_root)
    total = len(staged) + len(unstaged)

    print(f"\n📦 Synchronisation Stitch terminée : {len(unstaged)} écran(s) modifié(s) détecté(s) (total suivi : {total}).")
    for i, item in enumerate(unstaged, 1):
        print(f"  [{i}] {item['path']} ({item['type']})")

    if staged:
        print(f"  ℹ️ {len(staged)} écran(s) déjà stagé(s) / acquitté(s).")

    print("\n👉 Exécute 'python stitch_sync.py --next' pour examiner et intégrer le 1er écran.")


def cmd_next(repo_root: Path) -> None:
    """Affiche le diff du prochain écran non stagé ou déclenche le commit de clôture si tout est acquitté."""
    staged, unstaged = get_stitch_status(repo_root)
    total = len(staged) + len(unstaged)

    if not unstaged:
        if staged:
            print("\n🎉 Tous les écrans Stitch ont été consultés et acquittés !")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"chore(stitch): sync and integrate all screens {timestamp}"
            print(f"[*] Création automatique du commit Git de clôture : « {commit_msg} »...")
            try:
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_root, check=True)
                print(f"✅ Commit de clôture créé avec succès dans {repo_root}.")
            except subprocess.CalledProcessError as e:
                print(f"[!] Erreur lors de la création du commit Git : {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("\n✅ Aucun écran en attente de revue dans stitch/ (dépôt propre).")
        return

    target = unstaged[0]
    target_path = target["path"]
    target_type = target["type"]
    current_idx = len(staged) + 1

    print("\n" + "="*70)
    print(f"📋 ÉCRAN [{current_idx}/{total}] : {target_path} ({target_type})")
    print("="*70)

    full_path = repo_root / target_path

    if target_type == "nouveau":
        file_size = full_path.stat().st_size if full_path.exists() else 0
        print(f"--- NOUVEL ÉCRAN DÉTECTÉ ({file_size} octets) ---")
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            print(f"Aperçu des 60 premières lignes (sur {len(lines)} lignes au total) :\n")
            print("\n".join(lines[:60]))
            if len(lines) > 60:
                print(f"\n... [{len(lines) - 60} lignes supplémentaires dans {target_path}]")
        except Exception as e:
            print(f"[!] Erreur lors de la lecture du fichier : {e}", file=sys.stderr)
    else:
        try:
            diff_proc = subprocess.run(
                ["git", "diff", "--color=always", "--", target_path],
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            if diff_proc.returncode == 0 and diff_proc.stdout.strip():
                print(diff_proc.stdout)
            else:
                diff_cached = subprocess.run(
                    ["git", "diff", "--cached", "--color=always", "--", target_path],
                    cwd=repo_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                print(diff_cached.stdout or "(Aucune modification textuelle)")
        except Exception as e:
            print(f"[!] Erreur lors de l'exécution de git diff : {e}", file=sys.stderr)

    print("\n" + "="*70)
    print("💡 DIRECTIVE POUR L'AGENT / DÉVELOPPEUR :")
    print(f"1. Intègre ces ajouts/modifications dans les composants applicatifs (ex: frontend/src/).")
    print(f"2. Puis valide et passe à l'écran suivant en exécutant :")
    print(f"   python stitch_sync.py --ack {target_path}")
    print("="*70)


def cmd_ack(repo_root: Path, file_arg: str) -> None:
    """Acquitte un écran via git add, affiche la confirmation, puis enchaîne sur --next."""
    target_path = resolve_stitch_file(repo_root, file_arg)
    rel_path = target_path.relative_to(repo_root).as_posix()

    try:
        subprocess.run(["git", "add", rel_path], cwd=repo_root, check=True)
        print(f"\n✅ Écran {rel_path} acquitté et stagé dans Git.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Erreur lors de l'exécution de git add pour {rel_path} : {e}", file=sys.stderr)
        sys.exit(1)

    cmd_next(repo_root)


def cmd_status(repo_root: Path) -> None:
    """Affiche la jauge de progression des écrans acquittés (stagés) vs en attente (unstaged)."""
    staged, unstaged = get_stitch_status(repo_root)
    total = len(staged) + len(unstaged)

    print(f"\n[*] Racine Git : {repo_root}")
    if total == 0:
        print("✅ Aucun écran Stitch en cours de révision (aucun changement en attente dans stitch/).")
        return

    print(f"📊 Progression de la synchronisation Stitch : [{len(staged)}/{total}]")
    print(f"  • {len(staged)} écran(s) intégré(s) et acquitté(s) (stagé(s))")
    print(f"  • {len(unstaged)} écran(s) en attente d'intégration (unstaged)\n")

    if staged:
        print("Écrans acquittés (stagés) :")
        for item in staged:
            print(f"  [x] {item['path']} ({item['type']})")

    if unstaged:
        print("\nÉcrans en attente de revue :")
        for i, item in enumerate(unstaged):
            next_badge = " 👉 (prochain à traiter via --next)" if i == 0 else ""
            print(f"  [ ] {item['path']} ({item['type']}){next_badge}")
        print("\n👉 Exécute 'python stitch_sync.py --next' pour continuer la revue.")
    else:
        print("\n🎉 Tous les écrans sont acquittés ! Exécute 'python stitch_sync.py --next' pour commiter.")


def main():
    parser = argparse.ArgumentParser(
        description="Stitch Sync — Synchroniseur Google Stitch & Itérateur de Diff Pas-à-Pas (One-by-One Review)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--project",
        default=DEFAULT_PROJECT_ID,
        help=f"Identifiant du projet Google Stitch (défaut : {DEFAULT_PROJECT_ID})"
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Télécharge les écrans depuis Google Stitch dans le sanctuaire stitch/"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simule la synchronisation sans écrire sur le disque ni altérer Git"
    )
    parser.add_argument(
        "--next",
        action="store_true",
        help="Affiche le diff du prochain écran non stagé (ou commit final si tout est acquitté)"
    )
    parser.add_argument(
        "--ack",
        metavar="FICHIER",
        default=None,
        help="Acquitte un écran en l'ajoutant au staging Git (git add), puis enchaîne sur --next"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Affiche la jauge de progression des écrans traités vs restants"
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Chemin vers le dépôt git cible ou un sous-dossier (défaut : dossier courant)"
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Chemin optionnel vers un fichier HTML ou ZIP source pour injection manuelle"
    )
    parser.add_argument(
        "--mcp-config",
        default=DEFAULT_MCP_CONFIG,
        help=f"Chemin vers la configuration mcp_servers.json (défaut : {DEFAULT_MCP_CONFIG})"
    )

    args = parser.parse_args()
    repo_root = find_git_root(args.target)

    # 1. Mode Status
    if args.status:
        cmd_status(repo_root)
        return

    # 2. Mode Ack
    if args.ack:
        cmd_ack(repo_root, args.ack)
        return

    # 3. Mode Next
    if getattr(args, "next", False):
        cmd_next(repo_root)
        return

    # 4. Mode Fetch / Sync / Dry-run
    # Déclenché si --fetch, --dry-run, --source, ou si aucun argument d'itération n'est passé
    if args.fetch or args.dry_run or args.source or len(sys.argv) == 1:
        cmd_fetch(
            project_id=args.project,
            repo_root=repo_root,
            source_path=args.source,
            mcp_config=args.mcp_config,
            dry_run=args.dry_run
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
