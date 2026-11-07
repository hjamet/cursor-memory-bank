#!/usr/bin/env python3
"""
dream_inbox_cli.py — Utilitaire CLI pour interagir avec le dossier Google Drive Dream_Inbox.

Permet à /dream (ou à l'utilisateur) de lister, lire et mettre à la corbeille
les Google Docs déposés dans Dream_Inbox via le remote Rclone gdrive.
"""

from __future__ import annotations

import argparse
import datetime
import http.client
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

# Configuration standard des flux texte UTF-8
for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, io.UnsupportedOperation, OSError):
            pass

CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

try:
    "✓".encode(sys.stdout.encoding or "utf-8")
    CHECK_MARK = "✓"
    CROSS_MARK = "✗"
except (UnicodeEncodeError, AttributeError):
    CHECK_MARK = "[OK]"
    CROSS_MARK = "[Error]"


def get_aivc_dir() -> Path:
    """Chemin canonique ~/.aivc."""
    return Path.home() / ".aivc"


def _get_rclone_config_path() -> Path:
    """Résolution du chemin de rclone.conf."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            p = Path(appdata) / "rclone" / "rclone.conf"
            if p.exists():
                return p
    default_p = Path.home() / ".config" / "rclone" / "rclone.conf"
    if default_p.exists():
        return default_p
    try:
        out = subprocess.check_output(["rclone", "config", "file"], stderr=subprocess.DEVNULL, encoding="utf-8")
        for line in out.splitlines():
            line = line.strip()
            if line and not line.startswith("Configuration"):
                p = Path(line)
                if p.exists():
                    return p
    except Exception:
        pass
    return Path(os.environ.get("APPDATA", "")) / "rclone" / "rclone.conf"


def _get_rclone_drive_section() -> str:
    """Sélection de la section rclone avec scope en écriture prioritaire."""
    conf_path = _get_rclone_config_path()
    if conf_path.exists():
        import configparser
        cp = configparser.RawConfigParser()
        try:
            cp.read(conf_path, encoding="utf-8")
            if cp.has_section("gdrive_rw") and cp.has_option("gdrive_rw", "token"):
                return "gdrive_rw"
            for sec in cp.sections():
                if cp.has_option(sec, "token") and cp.has_option(sec, "type") and cp.get(sec, "type").strip() == "drive":
                    scope = cp.get(sec, "scope", fallback="").strip()
                    if scope and "readonly" not in scope.lower():
                        return sec
            if cp.has_section("gdrive") and cp.has_option("gdrive", "token"):
                return "gdrive"
            for sec in cp.sections():
                if cp.has_option(sec, "token") and cp.has_option(sec, "type") and cp.get(sec, "type").strip() == "drive":
                    return sec
        except Exception:
            pass
    return "gdrive"


def _get_rclone_drive_access_token() -> str:
    """Récupération du token OAuth Google Drive actif depuis rclone, avec rafraîchissement si expiré."""
    conf_path = _get_rclone_config_path()
    section = _get_rclone_drive_section()
    needs_refresh = True
    token_str = None

    if conf_path.exists():
        import configparser
        cp = configparser.RawConfigParser()
        try:
            cp.read(conf_path, encoding="utf-8")
            if cp.has_section(section) and cp.has_option(section, "token"):
                tok_data = json.loads(cp.get(section, "token"))
                token_str = tok_data.get("access_token")
                exp_str = tok_data.get("expiry")
                if token_str and exp_str:
                    exp_dt = datetime.datetime.fromisoformat(exp_str)
                    if exp_dt.tzinfo is None:
                        exp_dt = exp_dt.replace(tzinfo=datetime.timezone.utc)
                    now_dt = datetime.datetime.now(datetime.timezone.utc)
                    if (exp_dt - now_dt).total_seconds() > 120:
                        needs_refresh = False
        except Exception:
            needs_refresh = True

    if needs_refresh:
        try:
            res = subprocess.run(["rclone", "about", f"{section}:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
            if res.returncode == 0 and conf_path.exists():
                import configparser
                cp = configparser.RawConfigParser()
                cp.read(conf_path, encoding="utf-8")
                if cp.has_section(section) and cp.has_option(section, "token"):
                    tok_data = json.loads(cp.get(section, "token"))
                    token_str = tok_data.get("access_token")
        except Exception as e:
            print(f"{YELLOW}Warning: Échec rafraîchissement token via rclone ({e}){RESET}", file=sys.stderr)

    if token_str:
        return token_str
    raise RuntimeError(f"Impossible d'obtenir l'access_token Google Drive depuis rclone.conf (section: {section}).")


def _drive_api_get_json(path: str, access_token: str) -> dict:
    """Exécution d'un GET REST Drive v3."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Connection": "close",
    }
    conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)
    try:
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", errors="replace")
        if resp.status == 200:
            return json.loads(body)
        if resp.status == 401:
            raise PermissionError("HTTP 401 Unauthorized: access token expired")
        raise RuntimeError(f"Google Drive API GET failed on {path} (HTTP {resp.status}): {body}")
    finally:
        conn.close()


def _get_dream_inbox_folder_ids(use_cache: bool = True) -> list[str]:
    """Récupère les folder IDs du dossier racine Dream_Inbox avec cache local et rclone lsjson."""
    cache_file = get_aivc_dir() / "dream_inbox_folders.json"
    if use_cache and cache_file.exists():
        try:
            cache_data = json.loads(cache_file.read_text(encoding="utf-8"))
            if isinstance(cache_data, dict) and "folder_ids" in cache_data:
                cached_ids = cache_data["folder_ids"]
                cached_time = cache_data.get("timestamp", 0)
                if time.time() - cached_time < 86400 and cached_ids:
                    return cached_ids
        except Exception:
            pass

    section = _get_rclone_drive_section()
    folder_ids = []
    # 1. Résolution via rclone lsjson (évite le rate-limit 403 sur client_id public)
    try:
        out = subprocess.check_output(
            ["rclone", "lsjson", f"{section}:", "--dirs-only", "--max-depth", "1"],
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
        )
        dirs = json.loads(out)
        for d in dirs:
            if d.get("Name") == "Dream_Inbox" and d.get("ID"):
                folder_ids.append(d["ID"])
    except Exception as e:
        print(f"{YELLOW}Warning: rclone lsjson a échoué ({e}), repli sur API REST...{RESET}", file=sys.stderr)

    # 2. Repli éventuel sur API REST directe si rclone n'a rien renvoyé
    if not folder_ids:
        access_token = _get_rclone_drive_access_token()
        params = {
            "q": "name = 'Dream_Inbox' and mimeType = 'application/vnd.google-apps.folder' and 'root' in parents and trashed = false",
            "fields": "files(id,name)",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        }
        path = f"/drive/v3/files?{urllib.parse.urlencode(params)}"
        data = _drive_api_get_json(path, access_token)
        files = data.get("files", [])
        folder_ids = [f["id"] for f in files if isinstance(f, dict) and f.get("id")]

    if not folder_ids:
        raise RuntimeError("Aucun dossier Google Drive nommé 'Dream_Inbox' trouvé à la racine.")

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({"folder_ids": folder_ids, "timestamp": time.time()}), encoding="utf-8")
    return folder_ids


def _load_dream_inbox_processed() -> dict:
    """Charge le registre local des documents traités."""
    local_path = get_aivc_dir() / "dream_inbox_processed.json"
    if local_path.exists():
        try:
            loaded = json.loads(local_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and "processed" in loaded:
                return loaded
        except Exception as e:
            print(f"{YELLOW}Warning: lecture dream_inbox_processed.json échouée: {e}{RESET}", file=sys.stderr)
    return {"processed": {}}


def _save_dream_inbox_processed(data: dict) -> None:
    """Sauvegarde le registre local des documents traités."""
    local_path = get_aivc_dir() / "dream_inbox_processed.json"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _record_dream_inbox_processed_doc(
    doc_id: str | None = None,
    doc_name: str | None = None,
    method: str = "manual_trash",
    local_path: str | None = None,
    extra_key: str | None = None,
) -> None:
    """Enregistre un document comme traité dans le registre persistant."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    reg = _load_dream_inbox_processed()
    primary_key = doc_id or doc_name or extra_key
    if not primary_key:
        return
    entry: dict[str, Any] = {
        "trashed_at": now_iso,
        "method": method,
        "name": doc_name or extra_key or primary_key,
    }
    if doc_id:
        entry["doc_id"] = doc_id
    if local_path:
        entry["local_path"] = local_path

    processed = reg.setdefault("processed", {})
    processed[primary_key] = entry
    if doc_id:
        processed[doc_id] = entry
    if doc_name:
        processed[doc_name] = entry
        stem = Path(doc_name).stem
        if stem:
            processed[stem] = entry
    if extra_key:
        processed[extra_key] = entry
    _save_dream_inbox_processed(reg)


def _list_all_dream_inbox_files(folder_ids: list[str] | None = None) -> list[dict]:
    """Scanne tous les dossiers Dream_Inbox et retourne la liste des fichiers dédupliqués."""
    if folder_ids is None:
        folder_ids = _get_dream_inbox_folder_ids()
    section = _get_rclone_drive_section()
    seen_ids = set()
    all_files = []
    for fid in folder_ids:
        try:
            out = subprocess.check_output(
                ["rclone", "lsjson", f"{section}:", "--drive-root-folder-id", fid],
                stderr=subprocess.DEVNULL,
                encoding="utf-8",
            )
            files = json.loads(out)
            for f in files:
                f_id = f.get("ID")
                if f_id and f_id in seen_ids:
                    continue
                if f_id:
                    seen_ids.add(f_id)
                f["FolderID"] = fid
                all_files.append(f)
        except Exception as e:
            print(f"{YELLOW}Warning: Échec scan dossier {fid}: {e}{RESET}", file=sys.stderr)
    return all_files


def _extract_dream_inbox_doc_text(folder_id: str, file_name: str, file_id: str = "", mime_type: str = "") -> str:
    """Télécharge et extrait le texte d'un document Dream_Inbox (REST ou rclone)."""
    if file_id:
        try:
            access_token = _get_rclone_drive_access_token()
            headers = {"Authorization": f"Bearer {access_token}", "Connection": "close"}
            # 1. Native Google Docs export as text/plain
            conn = http.client.HTTPSConnection("www.googleapis.com", timeout=20)
            conn.request("GET", f"/drive/v3/files/{file_id}/export?mimeType=text%2Fplain", headers=headers)
            resp = conn.getresponse()
            if resp.status == 200:
                text = resp.read().decode("utf-8", errors="replace")
                conn.close()
                return text
            resp.read()
            conn.close()

            # 2. Binary download via alt=media
            conn = http.client.HTTPSConnection("www.googleapis.com", timeout=20)
            conn.request("GET", f"/drive/v3/files/{file_id}?alt=media", headers=headers)
            resp = conn.getresponse()
            if resp.status == 200:
                raw_bytes = resp.read()
                conn.close()
                if zipfile.is_zipfile(io.BytesIO(raw_bytes)):
                    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                        xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    paras = []
                    for p in tree.iterfind(".//w:p", ns):
                        t_parts = [t.text for t in p.iterfind(".//w:t", ns) if t.text]
                        if t_parts:
                            paras.append("".join(t_parts))
                    return "\n".join(paras)
                else:
                    return raw_bytes.decode("utf-8", errors="replace")
            resp.read()
            conn.close()
        except Exception:
            pass

    # Fallback via rclone copy
    section = _get_rclone_drive_section()
    rclone_name = file_name
    if mime_type == "application/vnd.google-apps.document" and not rclone_name.endswith(".docx"):
        rclone_name = f"{rclone_name}.docx"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cmd = ["rclone", "copy", "--drive-root-folder-id", folder_id, f"{section}:{rclone_name}", str(tmp_path)]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target_file = tmp_path / rclone_name
        if not target_file.exists():
            candidates = list(tmp_path.iterdir())
            if candidates:
                target_file = candidates[0]
            else:
                raise FileNotFoundError(f"Fichier {file_name} introuvable après copie rclone depuis {folder_id}")

        if zipfile.is_zipfile(target_file):
            with zipfile.ZipFile(target_file) as z:
                xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paras = []
            for p in tree.iterfind(".//w:p", ns):
                t_parts = [t.text for t in p.iterfind(".//w:t", ns) if t.text]
                if t_parts:
                    paras.append("".join(t_parts))
            return "\n".join(paras)
        return target_file.read_text(encoding="utf-8", errors="replace")


def _save_dream_inbox_local_copy(doc_name: str, doc_id: str, doc_text: str) -> Path:
    """Archive le texte brut intégral localement dans C:\\Users\\Public\\aivc\\dream_inbox_archive\\."""
    archive_dir = Path(r"C:\Users\Public\aivc\dream_inbox_archive")
    archive_dir.mkdir(parents=True, exist_ok=True)
    clean_stem = doc_name
    for ch in '<>:"/\\|?*':
        clean_stem = clean_stem.replace(ch, "_")
    clean_stem = re.sub(r"\.(docx|txt|md)$", "", clean_stem, flags=re.IGNORECASE).strip()
    if not clean_stem:
        clean_stem = f"doc_{doc_id}"
    local_path = archive_dir / f"{clean_stem}.md"
    local_path.write_text(doc_text, encoding="utf-8")
    return local_path.resolve()


def _trash_drive_file_by_id(doc_id: str | None) -> bool:
    """Déplace le fichier Google Drive dans la corbeille via PATCH REST."""
    if not doc_id:
        return False
    try:
        token = _get_rclone_drive_access_token()
        conn = http.client.HTTPSConnection("www.googleapis.com", timeout=20)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Connection": "close",
        }
        conn.request("PATCH", f"/drive/v3/files/{doc_id}?supportsAllDrives=true", body=b'{"trashed": true}', headers=headers)
        resp = conn.getresponse()
        status = resp.status
        resp.read()
        conn.close()
        return status in (200, 204)
    except Exception as e:
        print(f"  {YELLOW}Avertissement API Drive: Requête PATCH corbeille échouée pour {doc_id} ({e}){RESET}", file=sys.stderr)
        return False


def _resolve_dream_inbox_target(target_str: str, folder_ids: list[str]) -> tuple[str | None, str | None, str | None, str]:
    """Résout le doc_id, doc_name, folder_id et mime_type à partir d'un nom ou d'un ID."""
    files = _list_all_dream_inbox_files(folder_ids)
    for f in files:
        if f.get("Name") == target_str or f.get("ID") == target_str:
            return f.get("ID"), f.get("Name"), f.get("FolderID"), f.get("MimeType") or f.get("mimeType", "")
    if len(target_str) > 20 and "." not in target_str:
        return target_str, None, None, ""
    return None, target_str, None, ""


def cmd_list(args: argparse.Namespace) -> None:
    """Liste les documents de Dream_Inbox."""
    folder_ids = _get_dream_inbox_folder_ids()
    files = _list_all_dream_inbox_files(folder_ids)
    registry = _load_dream_inbox_processed()
    processed_map = registry.get("processed", {})
    include_all = getattr(args, "all", False)

    filtered_files = []
    for f in files:
        f_name = f.get("Name", "")
        f_id = f.get("ID", "")
        if not include_all and (f_id in processed_map or f_name in processed_map):
            continue
        filtered_files.append(f)

    if not filtered_files:
        if files and not include_all:
            print(f"  {GREEN}{CHECK_MARK} Dream_Inbox ne contient aucun nouveau document non traité ({len(files)} document(s) masqué(s) car déjà traité(s), utilisez '--all' pour afficher).{RESET}")
        else:
            print(f"  {GREEN}{CHECK_MARK} Dream_Inbox est vide (0 fichier).{RESET}")
        return

    print(f"  {len(filtered_files)} fichier(s) trouvé(s) dans Dream_Inbox :")
    for i, f in enumerate(filtered_files, 1):
        f_name = f.get("Name")
        f_id = f.get("ID")
        f_fid = (f.get("FolderID") or "")[:8]
        f_mod = (f.get("ModTime") or "")[:19]
        status_tag = ""
        if f_id in processed_map or f_name in processed_map:
            status_tag = f" {YELLOW}[déjà traité]{RESET}"
        print(f"  {i}. {BOLD}{f_name}{RESET} (ID: {f_id}, Dossier: {f_fid}..., Date: {f_mod}){status_tag}")


def cmd_read(args: argparse.Namespace) -> None:
    """Lit le texte intégral d'un document Dream_Inbox."""
    target = getattr(args, "target", "")
    if not target:
        raise ValueError("Nom ou ID du document requis pour la lecture.")
    folder_ids = _get_dream_inbox_folder_ids()
    doc_id, doc_name, doc_fid, mime_type = _resolve_dream_inbox_target(target, folder_ids)
    target_name = doc_name or (f"{target}.docx" if len(target) > 20 and "." not in target else target)
    fid = doc_fid or (folder_ids[0] if folder_ids else "")
    if not fid:
        raise RuntimeError("Impossible de localiser le dossier parent du document.")

    content = _extract_dream_inbox_doc_text(fid, target_name, file_id=doc_id or "", mime_type=mime_type)
    print(content)


def cmd_trash(args: argparse.Namespace) -> None:
    """Archive localement et déplace un document vers la corbeille Google Drive."""
    target = getattr(args, "target", "")
    if not target:
        raise ValueError("Nom ou ID du document requis pour la mise à la corbeille.")
    folder_ids = _get_dream_inbox_folder_ids()
    doc_id, doc_name, doc_fid, mime_type = _resolve_dream_inbox_target(target, folder_ids)
    fid = doc_fid or (folder_ids[0] if folder_ids else "")

    if not doc_id and len(target) > 20:
        doc_id = target

    # Archivage local préalable obligatoire dans C:\Users\Public\aivc\dream_inbox_archive\
    local_archive_path = None
    if fid and (doc_name or doc_id):
        try:
            doc_text = _extract_dream_inbox_doc_text(fid, doc_name or target, file_id=doc_id or "", mime_type=mime_type)
            local_archive_path = _save_dream_inbox_local_copy(doc_name or target, doc_id or "unknown", doc_text)
            print(f"  {GREEN}{CHECK_MARK} Archive locale sauvegardée dans {local_archive_path}{RESET}")
        except Exception as e:
            print(f"  {YELLOW}Avertissement : Archivage local impossible avant mise à la corbeille ({e}){RESET}", file=sys.stderr)

    trashed = _trash_drive_file_by_id(doc_id)
    _record_dream_inbox_processed_doc(
        doc_id=doc_id,
        doc_name=doc_name,
        method="drive_api" if trashed else "local_registry",
        local_path=str(local_archive_path) if local_archive_path else None,
        extra_key=target,
    )

    if trashed:
        print(f"{GREEN}{CHECK_MARK} Document '{target}' mis à la corbeille sur Google Drive et consigné au registre.{RESET}")
    else:
        print(f"{GREEN}{CHECK_MARK} Document '{target}' consigné comme traité dans le registre persistant local.{RESET}")
        if fid:
            print(f"  Lien direct Google Drive : https://drive.google.com/drive/folders/{fid}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dream_inbox_cli.py",
        description="Utilitaire CLI Dream_Inbox sur Google Drive (list, read, trash)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sous-commandes disponibles")

    # list
    parser_list = subparsers.add_parser("list", help="Lister les documents dans Dream_Inbox")
    parser_list.add_argument("--all", action="store_true", help="Afficher tous les documents y compris ceux déjà traités")

    # read
    parser_read = subparsers.add_parser("read", help="Lire le texte intégral d'un document Dream_Inbox")
    parser_read.add_argument("target", type=str, help="Nom ou ID du document à lire")

    # trash
    parser_trash = subparsers.add_parser("trash", help="Archiver localement et mettre un document à la corbeille")
    parser_trash.add_argument("target", type=str, help="Nom ou ID du document à supprimer/masquer")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "trash":
        cmd_trash(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
