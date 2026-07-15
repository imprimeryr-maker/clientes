import base64
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path

BACKUP_DIR = Path(__file__).parent / "backups"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = "imprimeryr-maker"
REPO = "clientes"
BRANCH = "main"

REPO_DIR = Path(__file__).parent.parent
DB_PATH = REPO_DIR / "data" / "ryr.db"


def log(msg):
    print(f"[backup] {msg}", flush=True)


def _github_api(method, path, data=None, expect_404=False):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/{path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "backup-bot",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404 and expect_404:
            return None
        body = e.read().decode()
        log(f"API error ({e.code}): {body[:500]}")
        return None


def export_cliente_backup(cliente_data: dict = None):
    log("=== INICIO BACKUP ===")

    if not GITHUB_TOKEN:
        log("GITHUB_TOKEN no configurado, se omite backup")
        return

    if not DB_PATH.exists():
        log(f"ERROR: DB no encontrada en {DB_PATH}")
        return
    log(f"DB encontrada ({DB_PATH.stat().st_size} bytes)")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"ryr_{timestamp}.db"
    filepath = BACKUP_DIR / filename

    try:
        shutil.copy2(str(DB_PATH), str(filepath))
        log(f"DB copiada a {filepath}")
    except Exception as e:
        log(f"ERROR copiando DB: {e}")
        return

    try:
        with open(filepath, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode()

        github_path = f"backend/backups/{filename}"

        sha = None
        existing = _github_api("GET", f"contents/{github_path}?ref={BRANCH}", expect_404=True)
        if existing and "sha" in existing:
            sha = existing["sha"]
            log(f"Archivo ya existe en GitHub, se actualizará (sha={sha[:8]}...)")

        payload = {
            "message": f"Backup DB: {filename}",
            "content": content_b64,
            "branch": BRANCH,
        }
        if sha:
            payload["sha"] = sha

        result = _github_api("PUT", f"contents/{github_path}", payload)
        if result:
            log(f"=== BACKUP SUBIDO A GITHUB ({filename}) ===")
        else:
            log(f"ERROR: no se pudo subir el backup")
    except Exception as e:
        log(f"ERROR en backup: {e}")
