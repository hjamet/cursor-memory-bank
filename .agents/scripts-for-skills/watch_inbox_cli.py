#!/usr/bin/env python3
"""
watch_inbox_cli.py — Surveillance événementielle Dream_Inbox sur Google Drive & Autonomie Bornée /one-shot.

Script CLI autonome synchronisé dans VoiceNotes/_agents/scripts-for-skills/
et piloté par le venv canonique ~/.aivc/venv/Scripts/python.exe.
"""

from __future__ import annotations

import argparse
import base64
import datetime
import http.client
import io
import json
import os
import re
import shutil
import signal
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
if hasattr(sys.stdin, "reconfigure"):
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, io.UnsupportedOperation, OSError):
        pass
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except (AttributeError, io.UnsupportedOperation, OSError):
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except (AttributeError, io.UnsupportedOperation, OSError):
        pass

# ---------------------------------------------------------------------------
# ANSI Formatting helpers
# ---------------------------------------------------------------------------
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
DIM = "\033[2m"
BOLD = "\033[1m"
MAGENTA = "\033[0;35m"
RESET = "\033[0m"

try:
    "✓".encode(sys.stdout.encoding or "utf-8")
    CHECK_MARK = "✓"
    CROSS_MARK = "✗"
except (UnicodeEncodeError, AttributeError):
    CHECK_MARK = "[OK]"
    CROSS_MARK = "[Error]"


# ---------------------------------------------------------------------------
# Gestion des Signaux & Arrêt Gracieux à Double Détente (Ctrl+C)
# ---------------------------------------------------------------------------
_SIGINT_COUNT: int = 0
_STOP_AFTER_AGENT: bool = False
_ACTIVE_AGY_PROC: subprocess.Popen | None = None


def _run_agy_command(agy_cmd: list[str], workspace: Path | str) -> int:
    """Execute agy command isolated from console Ctrl+C events under Windows.

    Uses CREATE_NEW_PROCESS_GROUP so the child process is not sent CTRL_C_EVENT
    when the user presses Ctrl+C in the console. Waits reactively via poll() loop
    so Python SIGINT handlers can run immediately.
    """
    global _ACTIVE_AGY_PROC
    if _STOP_AFTER_AGENT:
        return 0
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    proc = subprocess.Popen(
        agy_cmd,
        cwd=str(workspace),
        creationflags=creationflags,
        start_new_session=(os.name != "nt"),
    )
    _ACTIVE_AGY_PROC = proc
    try:
        while proc.poll() is None:
            time.sleep(0.2)
        return proc.returncode
    finally:
        _ACTIVE_AGY_PROC = None


def _handle_sigint(signum: int, frame: Any) -> None:
    """Handle Ctrl+C (SIGINT) with double-action semantics:
    1st Ctrl+C: schedule graceful shutdown after current agent or cycle finishes.
    2nd Ctrl+C: force immediate shutdown by killing active agy process tree and exiting.
    """
    global _SIGINT_COUNT, _STOP_AFTER_AGENT, _ACTIVE_AGY_PROC
    _SIGINT_COUNT += 1
    _STOP_AFTER_AGENT = True

    if _SIGINT_COUNT == 1:
        if _ACTIVE_AGY_PROC is not None and _ACTIVE_AGY_PROC.poll() is None:
            print(
                f"\n{YELLOW}{BOLD}⚠️ [Ctrl+C (1/2)] Arrêt différé programmé : l'agent en cours poursuit son travail jusqu'au bout, puis watch-inbox s'arrêtera sans relancer de nouvel agent. (Pressez une 2e fois Ctrl+C pour forcer l'arrêt immédiat.){RESET}",
                flush=True,
            )
        else:
            print(
                f"\n{YELLOW}{BOLD}⚠️ [Ctrl+C (1/2)] Arrêt demandé (aucun agent en cours) : fermeture propre de watch-inbox.{RESET}",
                flush=True,
            )
    elif _SIGINT_COUNT >= 2:
        print(
            f"\n{RED}{BOLD}🛑 [Ctrl+C (2/2)] Arrêt immédiat forcé !{RESET}",
            flush=True,
        )
        if _ACTIVE_AGY_PROC is not None and _ACTIVE_AGY_PROC.poll() is None:
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(_ACTIVE_AGY_PROC.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    _ACTIVE_AGY_PROC.kill()
            except Exception:
                pass
        os._exit(130)


def _sleep_interruptible(seconds: float) -> bool:
    """Sleep in short steps (0.2s) so _STOP_AFTER_AGENT immediately terminates sleep."""
    steps = int(seconds / 0.2)
    for _ in range(steps):
        if _STOP_AFTER_AGENT:
            return True
        time.sleep(0.2)
    remainder = seconds - (steps * 0.2)
    if remainder > 0:
        if _STOP_AFTER_AGENT:
            return True
        time.sleep(remainder)
    return _STOP_AFTER_AGENT


def get_aivc_dir() -> Path:
    """Return ~/.aivc directory path."""
    return Path.home() / ".aivc"


# ---------------------------------------------------------------------------
# Registre Anti-Doublon & Cache Dossiers
# ---------------------------------------------------------------------------
_DREAM_INBOX_FOLDER_IDS_CACHE: list[str] | None = None
_DREAM_INBOX_FOLDERS_CACHE_FILE: Path | None = None


def _get_dream_inbox_folders_cache_file() -> Path:
    global _DREAM_INBOX_FOLDERS_CACHE_FILE
    if _DREAM_INBOX_FOLDERS_CACHE_FILE is not None:
        return _DREAM_INBOX_FOLDERS_CACHE_FILE
    _DREAM_INBOX_FOLDERS_CACHE_FILE = get_aivc_dir() / "dream_inbox_folders.json"
    return _DREAM_INBOX_FOLDERS_CACHE_FILE


def _load_dream_inbox_processed() -> dict:
    """Load processed documents registry locally and merge with Google Drive AIVC_Sync if available."""
    local_path = get_aivc_dir() / "dream_inbox_processed.json"
    data = {"processed": {}}
    if local_path.exists():
        try:
            loaded = json.loads(local_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and "processed" in loaded:
                data = loaded
        except Exception as e:
            print(f"{YELLOW}Warning: could not parse local dream_inbox_processed.json: {e}{RESET}", file=sys.stderr)

    # Attempt to sync/merge from Google Drive AIVC_Sync (scope drive.file compatible)
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            from aivc.sync.drive import NativeDriveSyncManager
            from aivc.config import get_storage_root
            mgr = NativeDriveSyncManager(get_storage_root())
            if getattr(mgr, "enabled", False):
                service = mgr._get_service()
                root_id = mgr._get_root_folder_id()
                q = f"name = 'dream_inbox_processed.json' and '{root_id}' in parents and trashed = false"
                res = service.files().list(q=q, spaces="drive", fields="files(id, name)").execute()
                files = res.get("files", [])
                if files:
                    content = service.files().get_media(fileId=files[0]["id"]).execute().decode("utf-8")
                    remote_data = json.loads(content)
                    if isinstance(remote_data, dict) and "processed" in remote_data:
                        for k, v in remote_data["processed"].items():
                            if k not in data["processed"]:
                                data["processed"][k] = v
        except Exception as e:
            print(f"{DIM}Note: optional Drive sync for dream_inbox_processed skipped ({e}){RESET}", file=sys.stderr)

    return data


def _save_dream_inbox_processed(data: dict) -> None:
    """Save processed documents registry locally and to Google Drive AIVC_Sync."""
    local_path = get_aivc_dir() / "dream_inbox_processed.json"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Attempt to sync to Google Drive AIVC_Sync (scope drive.file compatible)
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            from aivc.sync.drive import NativeDriveSyncManager
            from aivc.config import get_storage_root
            from googleapiclient.http import MediaInMemoryUpload
            mgr = NativeDriveSyncManager(get_storage_root())
            if getattr(mgr, "enabled", False):
                service = mgr._get_service()
                root_id = mgr._get_root_folder_id()
                q = f"name = 'dream_inbox_processed.json' and '{root_id}' in parents and trashed = false"
                res = service.files().list(q=q, spaces="drive", fields="files(id, name)").execute()
                files = res.get("files", [])
                body_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
                media = MediaInMemoryUpload(body_bytes, mimetype="application/json")
                if files:
                    service.files().update(fileId=files[0]["id"], media_body=media).execute()
                else:
                    meta = {"name": "dream_inbox_processed.json", "parents": [root_id]}
                    service.files().create(body=meta, media_body=media).execute()
        except Exception as e:
            print(f"{YELLOW}Warning: could not save dream_inbox_processed to Drive: {e}{RESET}", file=sys.stderr)


def _record_dream_inbox_processed_doc(
    doc_id: str | None = None,
    doc_name: str | None = None,
    method: str = "manual_trash",
    local_path: str | None = None,
    extra_key: str | None = None,
) -> None:
    """Record a document as processed in both local dream_inbox_processed.json and Drive AIVC_Sync."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    reg = _load_dream_inbox_processed()
    primary_key = doc_id or doc_name or extra_key
    if not primary_key:
        return
    entry = {
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
            processed[f"{stem}.docx"] = entry
            processed[f"{stem}.md"] = entry
    if extra_key:
        processed[extra_key] = entry
    _save_dream_inbox_processed(reg)


# ---------------------------------------------------------------------------
# Authentification & Accès REST Google Drive
# ---------------------------------------------------------------------------
def _get_rclone_config_path() -> Path:
    """Resolve path to rclone.conf."""
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
    except Exception as e:
        print(f"{YELLOW}Warning: could not resolve rclone config via CLI ({e}); using APPDATA default{RESET}", file=sys.stderr)
    return Path(os.environ.get("APPDATA", "")) / "rclone" / "rclone.conf"


def _find_best_rclone_drive_section(cp: Any) -> str | None:
    """Select the best rclone drive section with write scope preferred over readonly."""
    # 1. Priorité explicite à gdrive_rw si présent avec token
    if cp.has_section("gdrive_rw") and cp.has_option("gdrive_rw", "token"):
        return "gdrive_rw"

    # 2. Parcourir toutes les sections type = drive avec token et scope != drive.readonly
    for sec in cp.sections():
        if cp.has_option(sec, "token") and cp.has_option(sec, "type") and cp.get(sec, "type").strip() == "drive":
            scope = cp.get(sec, "scope", fallback="").strip()
            if scope and "readonly" not in scope.lower():
                return sec

    # 3. Dernier recours : gdrive ou toute section type=drive avec token
    if cp.has_section("gdrive") and cp.has_option("gdrive", "token"):
        return "gdrive"
    for sec in cp.sections():
        if cp.has_option(sec, "token") and cp.has_option(sec, "type") and cp.get(sec, "type").strip() == "drive":
            return sec
    return None


def _get_rclone_drive_section() -> str:
    """Return active rclone Google Drive section or 'gdrive' as default fallback."""
    conf_path = _get_rclone_config_path()
    if conf_path.exists():
        import configparser
        cp = configparser.RawConfigParser()
        try:
            cp.read(conf_path, encoding="utf-8")
            sec = _find_best_rclone_drive_section(cp)
            if sec:
                return sec
        except Exception:
            pass
    return "gdrive"



def _read_token_from_rclone_conf(conf_path: Path) -> tuple[str, str, str] | None:
    """Return (access_token, expiry_iso, section) from best drive section in rclone.conf."""
    import configparser
    cp = configparser.RawConfigParser()
    try:
        cp.read(conf_path, encoding="utf-8")
    except Exception:
        return None
    section = _find_best_rclone_drive_section(cp)
    if not section:
        return None
    raw_tok = cp.get(section, "token")
    try:
        tok_data = json.loads(raw_tok)
        return tok_data.get("access_token"), tok_data.get("expiry"), section
    except Exception:
        return None


def _get_rclone_drive_access_token() -> str:
    """Retrieve active Google Drive OAuth access_token from rclone, refreshing if needed."""
    conf_path = _get_rclone_config_path()
    token_info = _read_token_from_rclone_conf(conf_path) if conf_path.exists() else None

    section = token_info[2] if token_info and len(token_info) > 2 else _get_rclone_drive_section()

    needs_refresh = True
    if token_info and token_info[0] and token_info[1]:
        try:
            exp_str = token_info[1]
            exp_dt = datetime.datetime.fromisoformat(exp_str)
            now_dt = datetime.datetime.now(datetime.timezone.utc)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=datetime.timezone.utc)
            diff_sec = (exp_dt - now_dt).total_seconds()
            if diff_sec > 120:
                needs_refresh = False
        except Exception:
            needs_refresh = True

    if needs_refresh:
        try:
            res = subprocess.run(["rclone", "about", f"{section}:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
            if res.returncode != 0:
                print(f"{YELLOW}Warning: rclone about {section}: returned code {res.returncode}{RESET}", file=sys.stderr)
        except Exception as e:
            print(f"{YELLOW}Warning: Failed to refresh token via rclone about {section}: {e}{RESET}", file=sys.stderr)
        token_info = _read_token_from_rclone_conf(conf_path) if conf_path.exists() else None

    if token_info and token_info[0]:
        return token_info[0]
    raise RuntimeError(f"Failed to obtain Google Drive access token from rclone configuration (section: {section}).")


def _drive_api_get_json(
    path: str,
    access_token: str,
    conn: http.client.HTTPSConnection | None = None,
) -> tuple[dict, http.client.HTTPSConnection]:
    """Execute a Google Drive REST GET request with transient rate-limit backoff across a 60s window.

    Handles 403 rate limits, 429, and 5xx server errors with silent backoffs (5, 10, 20, 30)s.
    Re-establishes TCP/TLS connection immediately if dropped during keep-alive idle or sleep.
    Raises PermissionError immediately on 401.
    Raises RuntimeError Fail-Fast if all retries are exhausted or non-transient error occurs.
    """
    delays = (5, 10, 20, 30)
    max_attempts = len(delays) + 1

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Connection": "keep-alive",
    }

    if conn is None:
        conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)

    last_error_detail = ""

    for attempt in range(max_attempts):
        resp = None
        try:
            conn.request("GET", path, headers=headers)
            resp = conn.getresponse()
        except (http.client.RemoteDisconnected, http.client.BadStatusLine, ConnectionResetError, BrokenPipeError, TimeoutError, OSError) as net_err:
            conn.close()
            conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)
            if attempt == 0:
                # Reconnexion immédiate et silencieuse si la connexion keep-alive a été fermée pendant l'attente
                try:
                    conn.request("GET", path, headers=headers)
                    resp = conn.getresponse()
                except (http.client.RemoteDisconnected, http.client.BadStatusLine, ConnectionResetError, BrokenPipeError, TimeoutError, OSError) as net_err2:
                    net_err = net_err2

            if resp is None:
                if attempt < len(delays):
                    delay = delays[attempt]
                    time.sleep(delay)
                    continue
                last_error_detail = f"connection dropped ({net_err})"
                print(f"{YELLOW}Warning: Google Drive API connection dropped after {max_attempts} attempts ({net_err}){RESET}", file=sys.stderr)
                raise RuntimeError(f"Google Drive API GET failed on {path} after retries: {net_err}") from net_err

        body = resp.read().decode("utf-8", errors="replace")

        if resp.status == 200:
            return json.loads(body), conn

        if resp.status == 401:
            conn.close()
            raise PermissionError("HTTP 401 Unauthorized: access token expired")

        is_transient = (
            resp.status in (429, 500, 502, 503, 504)
            or (
                resp.status == 403
                and any(m in body for m in ("RATE_LIMIT_EXCEEDED", "rateLimitExceeded", "userRateLimitExceeded", "Quota exceeded", "quotaExceeded"))
            )
        )
        if is_transient:
            if attempt < len(delays):
                delay = delays[attempt]
                conn.close()
                conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)
                time.sleep(delay)
                continue
            last_error_detail = f"transient rate limit (HTTP {resp.status}): {body}"
            print(f"{YELLOW}Warning: Google Drive API transient error exhausted after {max_attempts} attempts (HTTP {resp.status}){RESET}", file=sys.stderr)

        conn.close()
        raise RuntimeError(f"Google Drive API GET failed on {path} (HTTP {resp.status}): {body}")

    conn.close()
    raise RuntimeError(f"Google Drive API GET failed on {path} after {max_attempts} attempts. {last_error_detail}")


def _drive_get_start_page_token(conn: http.client.HTTPSConnection, access_token: str) -> str:
    """Fetch initial startPageToken for Drive changes.list with transient retry."""
    data, _ = _drive_api_get_json("/drive/v3/changes/startPageToken?supportsAllDrives=true", access_token, conn=conn)
    return data["startPageToken"]


def _drive_poll_changes(conn: http.client.HTTPSConnection, access_token: str, page_token: str) -> tuple[str, list[dict]]:
    """Poll Drive changes.list from page_token and return (new_start_page_token, changes)."""
    all_changes = []
    current_token = page_token
    while True:
        params = {
            "pageToken": current_token,
            "includeRemoved": "false",
            "spaces": "drive",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
            "fields": "newStartPageToken,nextPageToken,changes(fileId,removed,file(id,name,parents,trashed,mimeType,modifiedTime))",
        }
        path = f"/drive/v3/changes?{urllib.parse.urlencode(params)}"
        data, conn = _drive_api_get_json(path, access_token, conn=conn)
        changes = data.get("changes", [])
        all_changes.extend(changes)
        if "nextPageToken" in data and data["nextPageToken"]:
            current_token = data["nextPageToken"]
        elif "newStartPageToken" in data and data["newStartPageToken"]:
            return data["newStartPageToken"], all_changes
        else:
            return current_token, all_changes


def _resolve_all_dream_inbox_folder_ids(use_cache: bool = True) -> list[str]:
    """Retrieve all Google Drive folder IDs named 'Dream_Inbox' at root via direct REST API."""
    global _DREAM_INBOX_FOLDER_IDS_CACHE
    if use_cache and _DREAM_INBOX_FOLDER_IDS_CACHE:
        return _DREAM_INBOX_FOLDER_IDS_CACHE

    cache_file = _get_dream_inbox_folders_cache_file()
    if use_cache and cache_file.exists():
        cache_data = json.loads(cache_file.read_text(encoding="utf-8"))
        if isinstance(cache_data, dict) and "folder_ids" in cache_data:
            cached_ids = cache_data["folder_ids"]
            cached_time = cache_data.get("timestamp", 0)
            if time.time() - cached_time < 3600 and cached_ids:
                _DREAM_INBOX_FOLDER_IDS_CACHE = cached_ids
                return cached_ids

    access_token = _get_rclone_drive_access_token()
    params = {
        "q": "name = 'Dream_Inbox' and mimeType = 'application/vnd.google-apps.folder' and 'root' in parents and trashed = false",
        "fields": "files(id,name)",
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }
    path = f"/drive/v3/files?{urllib.parse.urlencode(params)}"
    data, conn = _drive_api_get_json(path, access_token)
    conn.close()

    files = data.get("files", [])
    folder_ids = [f["id"] for f in files if isinstance(f, dict) and f.get("id")]

    if not folder_ids:
        raise RuntimeError("Aucun dossier Google Drive nommé 'Dream_Inbox' trouvé à la racine.")

    _DREAM_INBOX_FOLDER_IDS_CACHE = folder_ids
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({"folder_ids": folder_ids, "timestamp": time.time()}), encoding="utf-8")

    return folder_ids


_get_dream_inbox_folder_ids = _resolve_all_dream_inbox_folder_ids


def _list_all_dream_inbox_files(folder_ids: list[str] | None = None) -> list[dict]:
    """Scan all Dream_Inbox root folders and return deduplicated list of files with FolderID attached."""
    if folder_ids is None:
        folder_ids = _get_dream_inbox_folder_ids()

    seen_ids = set()
    all_files = []
    for fid in folder_ids:
        try:
            out = subprocess.check_output(
                ["rclone", "lsjson", f"{_get_rclone_drive_section()}:", "--drive-root-folder-id", fid],
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
            print(f"{YELLOW}Warning: Failed to list files in folder {fid}: {e}{RESET}", file=sys.stderr)
    return all_files


def _extract_dream_inbox_doc_text(folder_id: str, file_name: str, file_id: str = "", mime_type: str = "") -> str:
    """Download and extract full text from a document in Dream_Inbox.

    Attempts direct REST API export/download via Google Drive v3 if file_id is provided,
    avoiding rclone subprocess overhead and handling native Google Docs seamlessly.
    Falls back to rclone copy if REST fails or file_id is not provided.
    """
    if file_id:
        try:
            access_token = _get_rclone_drive_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Connection": "close",
            }

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
        except Exception as e:
            print(f"{DIM}Note: Direct REST fetch for {file_name} ({file_id}) failed ({e}); falling back to rclone...{RESET}", file=sys.stderr)

    # Fallback to rclone copy
    rclone_name = file_name
    if mime_type == "application/vnd.google-apps.document" and not rclone_name.endswith(".docx"):
        rclone_name = f"{rclone_name}.docx"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        cmd = ["rclone", "copy", "--drive-root-folder-id", folder_id, f"{_get_rclone_drive_section()}:{rclone_name}", str(tmp_path)]
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        target_file = tmp_path / rclone_name
        if not target_file.exists():
            candidates = list(tmp_path.iterdir())
            if candidates:
                target_file = candidates[0]
            else:
                raise FileNotFoundError(f"File {file_name} not found after rclone copy from folder {folder_id}")

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
        else:
            return target_file.read_text(encoding="utf-8", errors="replace")


def _trash_drive_file_by_id(doc_id: str | None) -> bool:
    """Trash a file in Google Drive by doc_id via direct REST PATCH.

    Returns True if successfully moved to Google Drive Trash (HTTP 200/204),
    or False with explicit diagnostic if scopes are insufficient or file is uneditable.
    """
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
        resp_body = resp.read().decode("utf-8", errors="replace")
        conn.close()
        if status in (200, 204):
            return True
        try:
            err_data = json.loads(resp_body)
            err_msg = err_data.get("error", {}).get("message", resp_body[:160])
        except Exception:
            err_msg = resp_body[:160]
        print(f"  {YELLOW}Note API Drive: Impossible de mettre le fichier {doc_id} à la corbeille distante (HTTP {status}: {err_msg}).{RESET}", file=sys.stderr)
    except Exception as e:
        print(f"  {YELLOW}Note API Drive: Échec de la requête REST PATCH pour {doc_id} ({e}).{RESET}", file=sys.stderr)

    return False


def _find_agy_executable() -> Path:
    """Resolve path to agy executable."""
    agy = shutil.which("agy")
    if agy:
        return Path(agy)
    candidates = [
        Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "agy" / "bin" / "agy.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Antigravity" / "bin" / "agy.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path("agy.exe")


def _save_dream_inbox_local_copy(doc_name: str, doc_id: str, doc_text: str) -> Path:
    """Save full text copy of detected Dream_Inbox document to local archive immediately."""
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


# ---------------------------------------------------------------------------
# Volet 2 — Autonomie Bornée /one-shot lorsque Dream_Inbox est vide
# ---------------------------------------------------------------------------
_LAST_NO_ELIGIBLE_REASON: str | None = None
_LAST_AUTONOMOUS_CHECK_TS: float = 0.0
_LAST_AIVC_TASKS_MTIME: float = 0.0


def _get_aivc_tasks_state_stamp() -> float:
    r"""Return maximum mtime of files in C:\Users\Public\aivc\advance_tldr and ~/.aivc/storage/commits."""
    max_mtime = 0.0
    tldr_dir = Path(r"C:\Users\Public\aivc\advance_tldr")
    if tldr_dir.exists():
        try:
            d_mtime = tldr_dir.stat().st_mtime
            if d_mtime > max_mtime:
                max_mtime = d_mtime
            with os.scandir(tldr_dir) as it:
                for entry in it:
                    if entry.is_file():
                        st = entry.stat()
                        if st.st_mtime > max_mtime:
                            max_mtime = st.st_mtime
        except OSError:
            pass

    for commits_dir in [Path.home() / ".aivc" / "storage" / "commits", Path.home() / ".aivc" / "commits"]:
        if commits_dir.exists():
            try:
                c_mtime = commits_dir.stat().st_mtime
                if c_mtime > max_mtime:
                    max_mtime = c_mtime
            except OSError:
                pass

    return max_mtime


def _reset_autonomous_throttle() -> None:
    """Reset autonomous throttle state when a new document is processed or a project is selected."""
    global _LAST_NO_ELIGIBLE_REASON, _LAST_AUTONOMOUS_CHECK_TS, _LAST_AIVC_TASKS_MTIME
    _LAST_NO_ELIGIBLE_REASON = None
    _LAST_AUTONOMOUS_CHECK_TS = 0.0
    _LAST_AIVC_TASKS_MTIME = 0.0


def _run_autonomous_one_shot_if_idle(
    workspace: str,
    agy_path: Path,
    model: str = "gemini-4-argon-high",
    dry_run: bool = False,
) -> bool:
    """Execute one autonomous /one-shot task on the highest-priority eligible project.

    Returns True if a project task was executed, False if no project was selected or error occurred.
    """
    global _LAST_NO_ELIGIBLE_REASON, _LAST_AUTONOMOUS_CHECK_TS, _LAST_AIVC_TASKS_MTIME

    now = time.time()
    current_mtime = _get_aivc_tasks_state_stamp()

    # Throttling intelligent : lorsqu'aucun projet n'était éligible (ex. no_todo_tasks_remaining ou all_projects_awaiting_validation),
    # ne pas relancer le sous-processus lourd next-autonomous à chaque tick de 15s si aucun fichier
    # de suivi n'a été modifié et qu'un délai de sécurité de 120s ne s'est pas écoulé.
    if _LAST_NO_ELIGIBLE_REASON in ("all_projects_awaiting_validation", "no_todo_tasks_remaining"):
        if (now - _LAST_AUTONOMOUS_CHECK_TS < 120.0) and (current_mtime <= _LAST_AIVC_TASKS_MTIME):
            return False

    script_path = Path(workspace) / "_agents" / "scripts-for-skills" / "project_memory_cli.py"
    if not script_path.exists():
        vn_path = Path.home() / "Documents" / "VoiceNotes" / "_agents" / "scripts-for-skills" / "project_memory_cli.py"
        if vn_path.exists():
            script_path = vn_path
        else:
            raise FileNotFoundError(f"[AUTONOMIE] Script project_memory_cli.py introuvable à {script_path}")

    res = subprocess.run(
        [sys.executable, str(script_path), "next-autonomous", "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    _LAST_AUTONOMOUS_CHECK_TS = time.time()
    _LAST_AIVC_TASKS_MTIME = _get_aivc_tasks_state_stamp()

    if res.returncode != 0:
        err_msg = res.stderr.strip() or res.stdout.strip()
        raise RuntimeError(f"project_memory_cli.py next-autonomous failed (code {res.returncode}): {err_msg}")

    data = json.loads(res.stdout)

    if not data.get("selected"):
        reason = data.get("reason", "unknown")
        if reason != _LAST_NO_ELIGIBLE_REASON:
            print(f"{DIM}[AUTONOMIE /one-shot] Aucun projet éligible (raison: {reason}).{RESET}")
            _LAST_NO_ELIGIBLE_REASON = reason
        return False

    _reset_autonomous_throttle()

    proj_title = data.get("title", "")
    proj_file = data.get("file", "")
    proj_abs = data.get("abs_path", "")
    tldr_path = data.get("tldr_path", "")
    eff_score = data.get("effective_score", 0.0)
    await_val_count = data.get("await_validation_count", 0)
    new_tasks_count = len(data.get("new_tasks") or [])

    print(f"{CYAN}{BOLD}[AUTONOMIE /one-shot] Dream_Inbox vide -> Projet sélectionné : {proj_title} (score effectif: {eff_score}, {new_tasks_count} tâche(s) todo en roadmap, {await_val_count} en await_validation){RESET}")

    auto_prompt = (
        f"Tu es lancé en mode autonome `/one-shot` par `watch-inbox` (1 projet = 1 tâche) sur le projet `{proj_title}`.\n"
        f"Note maîtresse : `{proj_abs}` (`{proj_file}`)\n"
        f"Fichier de suivi des tâches : `{tldr_path}`\n\n"
        f"Instructions strictes d'exécution (1 seule tâche `new` en `/one-shot`) :\n"
        f"1. Lis `{proj_abs}` et `{tldr_path}`.\n"
        f"2. Parmi les tâches au statut `new` (dans `## 📋 Roadmap du Projet` de `{tldr_path}`), identifie LA SEULE tâche existante la plus urgente qui soit immédiatement accessible et réalisable (en écartant toute tâche bloquée par une attente externe ; si seule la tâche récurrente Rasoir d'Ockham `[ockham-...]` est réalisable et présente dans `## 📋 Roadmap du Projet`, sélectionne-la).\n"
        f"3. Consulte l'historique complet de la tâche sélectionnée via `mcp-cli call aivc get_task_history '{{\"task_id\": \"<id>\"}}'` pour connaître toutes les itérations passées.\n"
        f"4. Traite UNIQUEMENT cette seule tâche de bout en bout selon les règles de `/one-shot` et `bonnes-pratiques-developpement.md` : travaille directement sur la branche principale (`main` / `master`), fais auditer et tester manuellement par `auditeur-alignement` (`Model: 'inherit'`), utilise obligatoirement `/draft` (`doc-version`) pour tout texte destiné à un humain ou refonte de note, et RESPECTE L'INTERDICTION ABSOLUE de commettre toute action impossible à annuler ou impliquant d'autres personnes (aucun envoi d'e-mail/message, aucune soumission de formulaire, aucun paiement, aucune publication externe). Respecte la Règle d'Or n°2 de sous-agents.md : INTERDICTION D'ENCHAÎNER PLUSIEURS VAGUES D'ÉCLAIREURS SÉQUENTIELLES (lance au maximum 1 seule vague d'éclaireurs flash en parallèle au tour 1 pour inspecter notes, liens entrants, git/worktrees et code en une seule fois, puis passe directement aux exécutants parallèles).\n"
        f"5. Enregistre le livrable prêt OBLIGATOIREMENT sur le MÊME `task_id` existant avec `task_status=\"await_validation\"` via `mcp-cli call aivc task_commit`. INTERDICTION ABSOLUE DE CRÉER DE NOUVELLES TÂCHES (`task_id=None` ou nouvel identifiant) SANS VALIDATION PRÉALABLE D'HENRI.\n"
        f"6. Clôture la session en exécutant `python \"{Path(workspace) / '_agents/scripts-for-skills/project_memory_cli.py'}\" feedback \"{proj_title}\" ok --agent`, puis arrête-toi immédiatement.\n"
    )

    if dry_run:
        print(f"{CYAN}{BOLD}[DRY-RUN] Commande agy.exe autonome préparée :{RESET}")
        print(f"  Executable:  {agy_path}")
        print(f"  Working Dir: {workspace}")
        print(f"  Model:       {model}")
        print(f"  Project:     {proj_title}")
        print(f"  Prompt size: {len(auto_prompt)} caractères")
        print(f"  TLDR Path:   {tldr_path}")
        print(f"  Command:     {agy_path} --model {model} -p <auto_prompt>")
        return False

    agy_cmd = [str(agy_path), "--model", model, "-p", auto_prompt]
    print(f"{CYAN}Exécution d'agy.exe en mode autonome /one-shot sur {proj_title}...{RESET}")
    ret_code = _run_agy_command(agy_cmd, workspace)
    if _STOP_AFTER_AGENT:
        print(f"\n{GREEN}{CHECK_MARK} Retour de l'agent reçu. Arrêt propre de watch-inbox suite au Ctrl+C.{RESET}", flush=True)
    if ret_code == 0:
        print(f"{GREEN}{CHECK_MARK} Session autonome /one-shot terminée avec succès sur {proj_title} (code 0).{RESET}")
    else:
        print(f"{RED}Session autonome /one-shot sur {proj_title} terminée avec le code {ret_code}.{RESET}")
    return True


_execute_autonomous_step = _run_autonomous_one_shot_if_idle


# ---------------------------------------------------------------------------
# Gestion des Processus WMI / PowerShell (status, stop, start)
# ---------------------------------------------------------------------------
def _run_powershell_script(script_text: str) -> str:
    """Execute a PowerShell snippet via Base64 EncodedCommand to avoid any escaping collisions."""
    encoded = base64.b64encode(script_text.encode("utf-16le")).decode("ascii")
    res = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        err = res.stderr.strip() or res.stdout.strip()
        raise RuntimeError(f"PowerShell execution failed (code {res.returncode}): {err}")
    return res.stdout.strip()


def _find_running_watch_processes() -> list[dict]:
    """Find all active Python processes running watch_inbox_cli.py watch or dream-inbox watch."""
    current_pid = os.getpid()
    ps_cmd = (
        f"$currentPid = {current_pid}; "
        "$procs = Get-CimInstance Win32_Process | Where-Object { "
        "$_.ProcessId -ne $currentPid -and "
        "$_.Name -like '*python*' -and "
        "($_.CommandLine -like '*watch_inbox_cli.py*' -or $_.CommandLine -like '*dream-inbox watch*') -and "
        "$_.CommandLine -notlike '* status*' -and "
        "$_.CommandLine -notlike '* stop*' -and "
        "$_.CommandLine -notlike '* list*' -and "
        "$_.CommandLine -notlike '* read*' -and "
        "$_.CommandLine -notlike '* trash*' -and "
        "$_.CommandLine -notlike '* --help*' "
        "} | Select-Object ProcessId, ParentProcessId, @{N='CreationDate';E={if ($_.CreationDate) { $_.CreationDate.ToString('yyyy-MM-dd HH:mm:ss') } else { '' }}}, CommandLine; "
        "if ($procs) { $procs | ConvertTo-Json -Compress } else { '[]' }"
    )
    stdout = _run_powershell_script(ps_cmd)
    if not stdout or stdout == "null":
        return []
    try:
        data = json.loads(stdout)
        procs: list[dict] = []
        if isinstance(data, dict):
            procs = [data]
        elif isinstance(data, list):
            procs = data
        if not procs:
            return []
        all_pids = {p.get("ProcessId") for p in procs if p.get("ProcessId")}
        return [p for p in procs if p.get("ParentProcessId") not in all_pids]
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse process list JSON: {stdout} ({e})")


def cmd_status(args: argparse.Namespace) -> None:
    """Display active watch-inbox processes (ProcessId, CreationDate, CommandLine)."""
    procs = _find_running_watch_processes()
    if not procs:
        print(f"{GREEN}{CHECK_MARK} Aucun processus watch-inbox en cours d'exécution.{RESET}")
        return
    print(f"{CYAN}{BOLD}Processus watch-inbox actifs ({len(procs)}) :{RESET}")
    for i, p in enumerate(procs, 1):
        pid = p.get("ProcessId")
        created = p.get("CreationDate", "inconnue")
        cmd = p.get("CommandLine", "")
        print(f"  {i}. PID: {BOLD}{pid}{RESET} | Démarré le: {created}")
        print(f"     Commande: {DIM}{cmd}{RESET}")


def cmd_stop(args: argparse.Namespace) -> None:
    """Stop all active watch_inbox_cli.py or dream-inbox watch processes."""
    procs = _find_running_watch_processes()
    if not procs:
        print(f"{GREEN}{CHECK_MARK} Aucun processus watch-inbox en cours d'exécution.{RESET}")
        return
    print(f"{CYAN}Arrêt de {len(procs)} processus watch-inbox actif(s)...{RESET}")
    for p in procs:
        pid = p.get("ProcessId")
        if not pid:
            continue
        try:
            res = subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  {GREEN}{CHECK_MARK} Processus {pid} arrêté avec succès.{RESET}")
            else:
                print(f"  {YELLOW}Avertissement : taskkill sur {pid} a retourné {res.returncode} ({res.stderr.strip()}).{RESET}", file=sys.stderr)
        except Exception as e:
            print(f"  {RED}Erreur lors de l'arrêt du processus {pid} : {e}{RESET}", file=sys.stderr)


def cmd_start(args: argparse.Namespace) -> None:
    """Start watch_inbox_cli.py in a detached WMI background process outside any Job Object."""
    procs = _find_running_watch_processes()
    if procs:
        print(f"{YELLOW}Arrêt préalable de {len(procs)} instance(s) existante(s)...{RESET}")
        cmd_stop(args)
        time.sleep(1)

    script_path = Path(__file__).resolve()
    venv_py = Path.home() / ".aivc" / "venv" / "Scripts" / "python.exe"
    python_exe = venv_py if venv_py.exists() else Path(sys.executable).resolve()
    log_dir = Path(r"C:\Users\Public\aivc")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "watch_inbox.log"

    flags: list[str] = []
    if getattr(args, "interval", None) and args.interval != 15:
        flags.extend(["--interval", str(args.interval)])
    if getattr(args, "no_autonomous", False):
        flags.append("--no-autonomous")
    if getattr(args, "model", None) and args.model != "gemini-4-argon-high":
        flags.extend(["--model", str(args.model)])
    if getattr(args, "workspace", None):
        flags.extend(["--workspace", str(args.workspace)])

    flags_str = " ".join(flags)
    watch_args = f"watch {flags_str}".strip()

    cmd_str = f'cmd.exe /s /c "\"{python_exe}\" -u \"{script_path}\" {watch_args} >> \"{log_file}\" 2>&1"'
    ps_launch = f"""
$cmd = @'
{cmd_str}
'@
$res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{{ CommandLine = $cmd }}
if ($res.ReturnValue -ne 0) {{ throw "WMI Process Creation failed with code $($res.ReturnValue)" }}
$res.ProcessId
""".strip()

    created_pid = _run_powershell_script(ps_launch)
    print(f"{GREEN}{CHECK_MARK} Processus watch-inbox démarré avec succès en arrière-plan détaché (PID lanceur WMI : {created_pid}).{RESET}")
    print(f"  {DIM}Logs en temps réel :{RESET} {log_file}")

    time.sleep(1.5)
    new_procs = _find_running_watch_processes()
    if new_procs:
        for p in new_procs:
            print(f"  {DIM}Processus Python actif :{RESET} PID {p.get('ProcessId')} (démarré à {p.get('CreationDate')})")
    else:
        print(f"  {YELLOW}Note : Le processus lanceur {created_pid} a été créé ; vérifiez les logs dans {log_file} si le processus Python s'est arrêté prématurément.{RESET}")


# ---------------------------------------------------------------------------
# Boucle Principale Watch & Commandes List, Read, Trash
# ---------------------------------------------------------------------------
def cmd_watch(args: argparse.Namespace) -> None:
    """Differential event-driven watcher for Google Drive Dream_Inbox via changes.list."""
    signal.signal(signal.SIGINT, _handle_sigint)
    interval = getattr(args, "interval", 15)
    once = getattr(args, "once", False)
    dry_run = getattr(args, "dry_run", False)
    no_autonomous = getattr(args, "no_autonomous", False)
    workspace = getattr(args, "workspace", None) or str(Path.home() / "Documents" / "VoiceNotes")
    model = getattr(args, "model", "gemini-4-argon-high") or "gemini-4-argon-high"

    watch_code_path = Path(__file__).resolve()
    watch_code_mtime = watch_code_path.stat().st_mtime

    print(f"{CYAN}{BOLD}=== AIVC Dream_Inbox Event Watcher ==={RESET}")
    print(f"  {DIM}Workspace:{RESET} {workspace}")
    print(f"  {DIM}Model:{RESET}     {model}")
    print(f"  {DIM}Interval:{RESET}  {interval}s (mode: {'once' if once else 'continuous'}{', dry-run' if dry_run else ''}{', sans autonomie' if no_autonomous else ', autonomie active'})")

    folder_ids = _get_dream_inbox_folder_ids()
    folder_ids_set = set(folder_ids)
    print(f"  {DIM}Dossiers Dream_Inbox détectés ({len(folder_ids)}) :{RESET} {', '.join(folder_ids)}")

    access_token = _get_rclone_drive_access_token()
    conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)
    try:
        page_token = _drive_get_start_page_token(conn, access_token)
        print(f"  {GREEN}{CHECK_MARK} Connexion API Google Drive établie. startPageToken initial: {page_token}{RESET}\n")
    except Exception as e:
        conn.close()
        raise RuntimeError(f"Échec d'initialisation startPageToken: {e}")

    agy_path = _find_agy_executable()

    def _process_doc(doc_name: str, doc_id: str, fid: str, is_demo: bool = False, mime_type: str = "") -> bool:
        _reset_autonomous_throttle()
        print(f"{YELLOW}{BOLD}>>> Nouveau document détecté : {doc_name} (ID: {doc_id}, Folder: {fid}){' [DRY-RUN DEMO SUR DERNIER DOC]' if is_demo else ''}{RESET}")
        try:
            doc_text = _extract_dream_inbox_doc_text(fid, doc_name, file_id=doc_id, mime_type=mime_type)
        except Exception as ex:
            print(f"{RED}Erreur lors de l'extraction du document {doc_name}: {ex}{RESET}")
            return False

        lines = doc_text.splitlines()
        preview = "\n".join(lines[:10]) + ("\n..." if len(lines) > 10 else "")
        print(f"{DIM}Extrait du document ({len(doc_text)} caractères, {len(lines)} lignes) :{RESET}")
        print(f"{DIM}--------------------------------------------------{RESET}")
        print(preview)
        print(f"{DIM}--------------------------------------------------{RESET}")

        local_archive_path = _save_dream_inbox_local_copy(doc_name, doc_id, doc_text)
        print(f"  {GREEN}{CHECK_MARK} Copie locale sauvegardée immédiatement : {local_archive_path} ({len(doc_text)} caractères){RESET}")

        prompt = (
            f"Tu es réveillé en mode événementiel par `watch-inbox` suite à l'arrivée du document Google Drive `{doc_name}` (ID: `{doc_id}`) dans `Dream_Inbox`.\n"
            f"Une copie locale intégrale du document a été sauvegardée sur le disque à l'emplacement suivant :\n"
            f"Fichier local : `{local_archive_path}`\n"
            f"Le fichier distant sur Google Drive a déjà été supprimé dès le début de la tâche pour éviter toute double exécution.\n\n"
            f"Instructions d'exécution immédiate (mode ciblé multi-projets, sans durée forcée de 45 min) :\n"
            f"1. Lis directement le fichier local `{local_archive_path}`. Identifie tous les projets ciblés par ce document, mets à jour sobrement les notes maîtresses Obsidian concernées (avec les citations exactes de la section 'Verbatim Exact d'Henri') et ajuste les scores de priorité via `project_memory_cli.py set-score` si demandé.\n"
            f"2. Lance en parallèle un sous-agent `superviseur-projet` (`Model: 'inherit'`) distinct sur chaque projet concerné.\n"
            f"3. RÈGLE STRICTE DE NON-RÉÉCRITURE : Ne réécris JAMAIS et ne reformule JAMAIS le propos d'Henri lorsque tu invoques un sous-agent `superviseur-projet`. Dans l'artefact de mission que tu passes à chaque `superviseur-projet`, donne-lui directement le lien/chemin vers le fichier téléchargé localement (`{local_archive_path}`) et demande-lui de lire directement ce fichier et de traiter uniquement les tâches qui concernent son projet dans ce fichier.\n"
            f"4. Traite chaque tâche sur la branche principale (`main` / `master`) avec garde-fou obligatoire `/draft` (`doc-version`), et RESPECTE L'INTERDICTION ABSOLUE de commettre toute action impossible à annuler ou impliquant d'autres personnes (aucun envoi d'e-mail/message, aucune soumission de formulaire, aucun paiement, aucune publication externe) sans validation directe d'Henri.\n"
            f"5. Enregistre chaque livrable, réponse ou clôture de tâche via `mcp-cli call aivc task_commit` sur la note maîtresse de chaque projet concerné afin que les Google Docs `Live_*` dans `AIVC_Sync/` soient mis à jour pour Gemini.\n"
        )

        agy_cmd = [str(agy_path), "--model", model, "-p", prompt]
        if dry_run or is_demo:
            print(f"{CYAN}{BOLD}[DRY-RUN] Commande agy.exe préparée :{RESET}")
            print(f"  Executable:  {agy_path}")
            print(f"  Working Dir: {workspace}")
            print(f"  Model:       {model}")
            print(f"  Prompt size: {len(prompt)} caractères")
            print(f"  Local Copy:  {local_archive_path}")
            print(f"  Command:     {agy_path} --model {model} -p <prompt>")
            return True

        _record_dream_inbox_processed_doc(
            doc_id=doc_id,
            doc_name=doc_name,
            method="watch_event_start",
            local_path=str(local_archive_path),
        )

        trashed_ok = _trash_drive_file_by_id(doc_id)
        if trashed_ok:
            print(f"  {GREEN}{CHECK_MARK} Fichier distant supprimé de Google Drive dès le début de la tâche (ID: {doc_id}).{RESET}")
        else:
            print(f"  {YELLOW}Mise à la corbeille distante non confirmée pour {doc_id} : document verrouillé dans dream_inbox_processed.json.{RESET}")

        print(f"{CYAN}Exécution d'agy.exe pour traiter le document...{RESET}")
        ret_code = _run_agy_command(agy_cmd, workspace)
        if _STOP_AFTER_AGENT:
            print(f"\n{GREEN}{CHECK_MARK} Retour de l'agent reçu. Arrêt propre de watch-inbox suite au Ctrl+C.{RESET}", flush=True)
        if ret_code == 0:
            print(f"{GREEN}{CHECK_MARK} Traitement agy réussi (returncode 0). Archive locale conservée dans {local_archive_path}.{RESET}")
            return True
        else:
            print(f"{RED}Erreur: agy.exe a échoué avec le code retour {ret_code}. Archive locale conservée dans {local_archive_path}.{RESET}")
            return False

    reg = _load_dream_inbox_processed()
    processed_map = reg.get("processed", {})
    all_existing_files = _list_all_dream_inbox_files(folder_ids)

    unprocessed = []
    for f in all_existing_files:
        f_name = f.get("Name", "")
        f_id = f.get("ID", "")
        f_stem = Path(f_name).stem if f_name else ""
        if f_id not in processed_map and f_name not in processed_map and f_stem not in processed_map:
            unprocessed.append(f)

    if unprocessed:
        print(f"{YELLOW}Scan initial : {len(unprocessed)} document(s) non traité(s) détecté(s).{RESET}")
        for f in unprocessed:
            _process_doc(f.get("Name"), f.get("ID"), f.get("FolderID", folder_ids[0]), mime_type=f.get("MimeType") or f.get("mimeType", ""))
            if _STOP_AFTER_AGENT:
                conn.close()
                return
    else:
        print(f"{GREEN}{CHECK_MARK} Scan initial : aucun document non traité en attente.{RESET}")
        if dry_run and once and all_existing_files and no_autonomous:
            sorted_files = sorted(all_existing_files, key=lambda x: x.get("ModTime", ""), reverse=True)
            demo_f = sorted_files[0]
            _process_doc(demo_f.get("Name"), demo_f.get("ID"), demo_f.get("FolderID", folder_ids[0]), is_demo=True, mime_type=demo_f.get("MimeType") or demo_f.get("mimeType", ""))
            if _STOP_AFTER_AGENT:
                conn.close()
                return

    if once:
        if _STOP_AFTER_AGENT:
            conn.close()
            return
        if not unprocessed and not no_autonomous:
            _run_autonomous_one_shot_if_idle(workspace, agy_path, model=model, dry_run=dry_run)
            if _STOP_AFTER_AGENT:
                conn.close()
                return
        print(f"\n{GREEN}{CHECK_MARK} Cycle unique terminé (--once).{RESET}")
        conn.close()
        return

    print(f"\n{CYAN}Démarrage de la boucle de surveillance (intervalle: {interval}s)... Pressez Ctrl+C pour programmer l'arrêt après l'agent en cours (2x Ctrl+C pour arrêt immédiat).{RESET}")
    err_count = 0
    check_autonomy_immediately = not unprocessed
    try:
        while True:
            if _STOP_AFTER_AGENT:
                return

            current_mtime = watch_code_path.stat().st_mtime
            if current_mtime != watch_code_mtime:
                print(f"\n{YELLOW}{BOLD}Modification du code source détectée ({watch_code_path.name}). Rechargement à chaud du processus...{RESET}")
                conn.close()
                venv_py = Path.home() / ".aivc" / "venv" / "Scripts" / "python.exe"
                py_bin = str(venv_py) if venv_py.exists() else sys.executable
                sys.exit(subprocess.call([py_bin, str(watch_code_path)] + sys.argv[1:]))

            try:
                if not check_autonomy_immediately:
                    if _sleep_interruptible(interval):
                        return
                check_autonomy_immediately = False

                if _STOP_AFTER_AGENT:
                    return

                try:
                    new_token, changes = _drive_poll_changes(conn, access_token, page_token)
                except (http.client.RemoteDisconnected, http.client.BadStatusLine, ConnectionResetError, BrokenPipeError, PermissionError):
                    conn.close()
                    access_token = _get_rclone_drive_access_token()
                    conn = http.client.HTTPSConnection("www.googleapis.com", timeout=30)
                    new_token, changes = _drive_poll_changes(conn, access_token, page_token)

                page_token = new_token
                err_count = 0

                inbox_docs_count = 0
                for ch in changes:
                    f_info = ch.get("file", {})
                    if not f_info or f_info.get("trashed"):
                        continue
                    f_name = f_info.get("name", "")
                    f_id = ch.get("fileId") or f_info.get("id")
                    f_mime = f_info.get("mimeType", "")
                    f_parents = f_info.get("parents", [])

                    is_inbox = any(p in folder_ids_set for p in f_parents)
                    if is_inbox:
                        reg = _load_dream_inbox_processed()
                        p_map = reg.get("processed", {})
                        f_stem = Path(f_name).stem if f_name else ""
                        if f_id not in p_map and f_name not in p_map and f_stem not in p_map:
                            target_fid = next((p for p in f_parents if p in folder_ids_set), folder_ids[0])
                            if _process_doc(f_name, f_id, target_fid, mime_type=f_mime):
                                inbox_docs_count += 1
                            if _STOP_AFTER_AGENT:
                                return

                if _STOP_AFTER_AGENT:
                    return

                if inbox_docs_count > 0:
                    check_autonomy_immediately = True
                    continue

                if not no_autonomous:
                    task_ran = _run_autonomous_one_shot_if_idle(workspace, agy_path, model=model, dry_run=dry_run)
                    if _STOP_AFTER_AGENT:
                        return
                    if task_ran:
                        check_autonomy_immediately = True
                        continue

            except KeyboardInterrupt:
                if _STOP_AFTER_AGENT:
                    return
                raise
            except Exception as e:
                err_count += 1
                backoff = min(interval * (2 ** err_count), 120)
                print(f"{RED}Erreur lors de l'interrogation Drive ({e}). Attente {backoff}s...{RESET}", file=sys.stderr)
                if _sleep_interruptible(backoff):
                    return
    finally:
        conn.close()


def _resolve_dream_inbox_target(target_str: str, folder_ids: list[str]) -> tuple[str | None, str | None, str | None]:
    files = _list_all_dream_inbox_files(folder_ids)
    for f in files:
        if f.get("Name") == target_str or f.get("ID") == target_str:
            return f.get("ID"), f.get("Name"), f.get("FolderID")
    if len(target_str) > 20 and "." not in target_str:
        return target_str, None, None
    return None, target_str, None


def cmd_list(args: argparse.Namespace) -> None:
    """List documents currently present in Dream_Inbox."""
    folder_ids = _get_dream_inbox_folder_ids()
    print(f"{CYAN}{BOLD}Google Drive Dream_Inbox Listing:{RESET}")
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
        f_fid = f.get("FolderID", "")[:8]
        f_mod = f.get("ModTime", "")[:19]
        status_tag = ""
        if f_id in processed_map or f_name in processed_map:
            status_tag = f" {YELLOW}[déjà traité]{RESET}"
        print(f"  {i}. {BOLD}{f_name}{RESET} (ID: {f_id}, Dossier: {f_fid}..., Date: {f_mod}){status_tag}")


def cmd_read(args: argparse.Namespace) -> None:
    """Read full text of a document from Dream_Inbox."""
    target = getattr(args, "target", "")
    if not target:
        raise ValueError("Document target name or ID required for read.")
    folder_ids = _get_dream_inbox_folder_ids()
    print(f"{DIM}Reading '{target}' from Dream_Inbox...{RESET}\n")

    doc_id, doc_name, doc_fid = _resolve_dream_inbox_target(target, folder_ids)
    target_name = doc_name or (f"{target}.docx" if len(target) > 20 and "." not in target else target)
    fid = doc_fid or (folder_ids[0] if folder_ids else "1ZLsrkwRBhH2Xz82eooQC3ahsePFjm28h")

    try:
        content = _extract_dream_inbox_doc_text(fid, target_name, file_id=doc_id)
        print(content)
    except Exception as e:
        downloaded = False
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_target = Path(tmp_dir) / target_name
            if doc_id:
                try:
                    from aivc.config import get_storage_root
                    from aivc.sync.drive import NativeDriveSyncManager
                    mgr = NativeDriveSyncManager(get_storage_root())
                    if getattr(mgr, "enabled", False):
                        service = mgr._get_service()
                        data = service.files().get_media(fileId=doc_id).execute()
                        local_target.write_bytes(data)
                        downloaded = True
                except Exception as err:
                    print(f"{YELLOW}Note: Native drive download failed for {doc_id}: {err}{RESET}", file=sys.stderr)
            if downloaded:
                if zipfile.is_zipfile(local_target):
                    with zipfile.ZipFile(local_target) as z:
                        xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    paras = []
                    for p in tree.iterfind(".//w:p", ns):
                        t_parts = [t.text for t in p.iterfind(".//w:t", ns) if t.text]
                        if t_parts:
                            paras.append("".join(t_parts))
                    print("\n".join(paras))
                else:
                    print(local_target.read_text(encoding="utf-8", errors="replace"))
            else:
                raise RuntimeError(f"Error reading file from Dream_Inbox: could not download '{target}': {e}") from e


def cmd_trash(args: argparse.Namespace) -> None:
    """Trash or mark a document as processed in Dream_Inbox."""
    target = getattr(args, "target", "")
    if not target:
        raise ValueError("Document target name or ID required for trash.")
    folder_ids = _get_dream_inbox_folder_ids()
    print(f"{DIM}Attempting to trash '{target}' from Dream_Inbox...{RESET}")

    doc_id, doc_name, doc_fid = _resolve_dream_inbox_target(target, folder_ids)
    fid = doc_fid or (folder_ids[0] if folder_ids else "1ZLsrkwRBhH2Xz82eooQC3ahsePFjm28h")

    if not doc_id and len(target) > 20:
        doc_id = target

    trashed = _trash_drive_file_by_id(doc_id)
    _record_dream_inbox_processed_doc(
        doc_id=doc_id,
        doc_name=doc_name,
        method="drive_api" if trashed else "local_registry",
        extra_key=target,
    )

    if trashed:
        print(f"{GREEN}{CHECK_MARK} File '{target}' successfully moved to Google Drive Trash and recorded in processed registry.{RESET}")
    else:
        print(f"{GREEN}{CHECK_MARK} Document '{target}' (ID: {doc_id or 'n/a'}) enregistré dans le registre persistant comme traité.")
        print(f"Il est désormais masqué de 'watch-inbox list' (utiliser 'watch-inbox list --all' pour l'afficher).{RESET}")
        print(f"{YELLOW}Note : Les tokens locaux actuels sont restreints en lecture seule (scope 'drive.readonly') ou par application ('drive.file').{RESET}")
        print(f"Pour purger ce document manuellement sur Google Drive si vous le souhaitez :")
        print(f"  {CYAN}https://drive.google.com/drive/folders/{fid}{RESET}")


# ---------------------------------------------------------------------------
# CLI Parser & Dispatcher
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="watch_inbox_cli.py",
        description="Surveillance événementielle Dream_Inbox sur Google Drive & Autonomie Bornée /one-shot",
    )
    subparsers = parser.add_subparsers(dest="command", help="Sous-commandes disponibles")

    # watch
    parser_watch = subparsers.add_parser("watch", help="Boucle événementielle de surveillance continue")
    parser_watch.add_argument("--interval", type=int, default=15, help="Intervalle de scrutation en secondes (défaut: 15)")
    parser_watch.add_argument("--once", action="store_true", help="Exécuter un seul cycle d'inspection et quitter")
    parser_watch.add_argument("--dry-run", action="store_true", help="Simuler les détections sans invoquer agy ni modifier Drive")
    parser_watch.add_argument("--workspace", type=str, default=str(Path.home() / "Documents" / "VoiceNotes"), help="Dossier de travail pour agy")
    parser_watch.add_argument("--model", type=str, default="gemini-4-argon-high", help="Modèle passé à agy.exe (défaut: gemini-4-argon-high)")
    parser_watch.add_argument("--no-autonomous", action="store_true", help="Désactiver l'autonomie /one-shot lorsque Dream_Inbox est vide")

    # list
    parser_list = subparsers.add_parser("list", help="Lister les documents dans Dream_Inbox")
    parser_list.add_argument("--all", action="store_true", help="Afficher tous les documents y compris ceux déjà traités")

    # read
    parser_read = subparsers.add_parser("read", help="Lire le texte intégral d'un document Dream_Inbox")
    parser_read.add_argument("target", type=str, help="Nom ou ID du document à lire")

    # trash
    parser_trash = subparsers.add_parser("trash", help="Mettre un document à la corbeille ou le marquer comme traité")
    parser_trash.add_argument("target", type=str, help="Nom ou ID du document à supprimer/masquer")

    # status
    subparsers.add_parser("status", help="Vérifier si des processus watch-inbox tournent en arrière-plan")

    # stop
    subparsers.add_parser("stop", help="Arrêter tous les processus watch-inbox actifs")

    # start
    parser_start = subparsers.add_parser("start", help="Démarrer watch-inbox en arrière-plan détaché (WMI)")
    parser_start.add_argument("--interval", type=int, default=15, help="Intervalle de scrutation en secondes (défaut: 15)")
    parser_start.add_argument("--workspace", type=str, default=str(Path.home() / "Documents" / "VoiceNotes"), help="Dossier de travail pour agy")
    parser_start.add_argument("--model", type=str, default="gemini-4-argon-high", help="Modèle passé à agy.exe (défaut: gemini-4-argon-high)")
    parser_start.add_argument("--no-autonomous", action="store_true", help="Désactiver l'autonomie /one-shot lorsque Dream_Inbox est vide")

    # Si appelé sans sous-commande ou directement avec des options (ex: python watch_inbox_cli.py --once),
    # insérer automatiquement 'watch' comme sous-commande par défaut.
    argv = sys.argv[1:]
    known_subcmds = {"watch", "list", "read", "trash", "status", "stop", "start", "-h", "--help"}
    if not argv:
        argv = ["watch"]
    elif argv[0] not in known_subcmds:
        argv = ["watch"] + argv

    args = parser.parse_args(argv)

    if args.command == "watch":
        cmd_watch(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "trash":
        cmd_trash(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "start":
        cmd_start(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
